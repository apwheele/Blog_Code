'''
Helpers for the buffer vs street network comparison. Expects a GeoDataFrame of
TIGER edges with TNIDF and TNIDT node ids, in a projected CRS.
'''

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from shapely.geometry import Point

# UTM 18N, meters, covers all of NYC
CRS = 'EPSG:32618'


def build_graph(streets):
    '''node id -> set of segment positions. TIGER already gives us the
    topology, TNIDF and TNIDT are the from and to nodes of each edge.'''
    node2seg = {}
    pairs = list(zip(streets['TNIDF'], streets['TNIDT']))
    for i, (a, b) in enumerate(pairs):
        for n in (a, b):
            node2seg.setdefault(n, set()).add(i)
    return pairs, node2seg


def network_orders(streets, seed, max_order):
    '''Breadth first expansion over segments. Order 1 is the seed segments,
    order k is order k-1 plus every segment sharing an intersection with the
    segments added at k-1. Returns a cumulative index array per order.'''
    streets = streets.reset_index(drop=True)
    pairs, node2seg = build_graph(streets)
    cur = set(seed)
    out = [np.array(sorted(cur))]
    done_nodes = set()
    for _ in range(max_order - 1):
        front = set()
        for i in cur:
            front.update(pairs[i])
        new_nodes = front - done_nodes
        done_nodes |= front
        add = set()
        for n in new_nodes:
            add |= node2seg.get(n, set())
        cur = cur | add
        out.append(np.array(sorted(cur)))
    return out


def build_nx(streets):
    '''weighted graph, edge weight is the length of the segment in meters'''
    G = nx.Graph()
    for i, (a, b, geo) in enumerate(zip(streets['TNIDF'], streets['TNIDT'],
                                        streets.geometry)):
        L = geo.length
        if G.has_edge(a, b):
            if G[a][b]['weight'] > L:
                G[a][b].update(weight=L, seg=i)
        else:
            G.add_edge(a, b, weight=L, seg=i)
    return G


def net_dist(streets, seed, cutoff=6000):
    '''Shortest path distance along the street network from the seed segments
    to every other segment. A segment is scored by its nearer endpoint.'''
    G = build_nx(streets)
    src = set(streets['TNIDF'].loc[seed]) | set(streets['TNIDT'].loc[seed])
    d = {}
    for n in src:
        if n not in G:
            continue
        dd = nx.single_source_dijkstra_path_length(G, n, cutoff=cutoff,
                                                   weight='weight')
        for k, v in dd.items():
            if v < d.get(k, np.inf):
                d[k] = v
    out = np.array([min(d.get(a, np.inf), d.get(b, np.inf))
                    for a, b in zip(streets['TNIDF'], streets['TNIDT'])])
    return out


def select_site(streets, name, within=None, lon=None, lat=None, water=None):
    '''The study site is a run of street, not a point. Takes every segment
    with the given name, then optionally narrows it either to segments whose
    centre is within `within` meters of lon/lat, or to the segments that cross
    `water`. Returns the segment positions and their merged geometry, which is
    what gets buffered.'''
    cand = streets[streets['FULLNAME'] == name]
    if within is not None:
        pt = gpd.GeoSeries([Point(lon, lat)], crs='EPSG:4326').to_crs(CRS).iloc[0]
        cand = cand[cand.centroid.distance(pt) <= within]
    if water is not None:
        cand = cand[cand.intersects(water)]
    idx = np.array(sorted(cand.index.values))
    return idx, cand.geometry.union_all()


def snap_crimes(crimes, streets, max_dist=50):
    '''Assigns each crime to its nearest street segment. Points further than
    max_dist meters from any segment are dropped.'''
    cr = crimes.copy()
    cr['PtID'] = np.arange(cr.shape[0])
    st = streets[['geometry']].copy()
    st['SegID'] = st.index
    j = gpd.sjoin_nearest(cr, st, max_distance=max_dist, how='inner',
                          distance_col='SnapDist')
    # a point equidistant from two segments comes back twice, keep one
    j = j.sort_values(['PtID','SnapDist']).drop_duplicates('PtID')
    return j.drop(columns=['index_right'])


def buffer_table(line, streets, crimes, water, dists, ndist=None):
    """Area, land area, street length and crime counts in each band. Bands are
    exclusive -- the 100-200 row is the ring between 100 and 200 meters out
    from the street, not the whole disk, so a crime is counted once. If ndist
    is supplied (network distance per segment) also reports how much of the
    street in the band is within that distance by network rather than as the
    crow flies."""
    # dissolve first, the TIGER water polygons overlap in places and summing
    # the pieces double counts them
    wet_all = water.geometry.union_all()
    res, prev, lo = [], None, 0
    for d in dists:
        cur = line.buffer(d)
        ring = cur if prev is None else cur.difference(prev)
        prev = cur
        clip = gpd.clip(streets, ring)
        km = clip.length.sum()/1000
        ins = crimes[crimes.within(ring)]
        area = ring.area/1e6
        wet = min(wet_all.intersection(ring).area/1e6, area)
        row = {'Band': f'{lo}-{d}',
               'To': d,
               'Area': area,
               'Land': area - wet,
               'PctLand': 100*(area - wet)/area,
               'StreetKm': km,
               'StreetDens': km/area,
               'Theft': int((ins['Crime']=='Theft').sum()),
               'Robbery': int((ins['Crime']=='Robbery').sum())}
        if ndist is not None and clip.shape[0]:
            reach = ndist[clip.index.values] <= d
            row['PctReach'] = 100*clip.length.values[reach].sum()/clip.length.sum()
        res.append(row)
        lo = d
    return finish(pd.DataFrame(res))


def network_table(orders, streets, crimes):
    """Same measures over the network, also exclusive. Each row is only the
    segments first reached at that order, not everything up to it."""
    res = []
    for o, idx in enumerate(orders, start=1):
        new = idx if o == 1 else np.setdiff1d(idx, orders[o-2])
        sub = streets.loc[new]
        ins = crimes[crimes['SegID'].isin(set(new))]
        res.append({'Order': o,
                    'Segments': len(new),
                    'StreetKm': sub.length.sum()/1000,
                    'Theft': int((ins['Crime']=='Theft').sum()),
                    'Robbery': int((ins['Crime']=='Robbery').sum())})
    return finish(pd.DataFrame(res))


def finish(df):
    df['Crimes'] = df['Theft'] + df['Robbery']
    df['PerKm'] = df['Crimes']/df['StreetKm']
    if 'Area' in df.columns:
        df['PerSqKm'] = df['Crimes']/df['Area']
    return df
