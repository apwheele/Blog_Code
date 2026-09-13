'''
Buffers vs street network measures, for two spots in New York City:

  Canal St at Broadway, the counterfeit goods market, sitting in a dense grid
  The Brooklyn Bridge walkway, where a circular buffer is mostly open water

Produces the tables and figures for the blog post.
'''

import cdcplot
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import StreetNet as sn
from matplotlib.lines import Line2D

DIST = list(range(100, 1100, 100))   # buffers, meters
ORD = 10                             # network orders
COL = cdcplot.colors

# Each site is a run of street, not a point. Canal St is trimmed to the blocks
# around Broadway where the counterfeit market sits, the bridge is every
# segment TIGER names Brooklyn Brg.
SITES = {'Canal St': dict(name='Canal St', lon=-74.0005, lat=40.7190, within=400),
         'Brooklyn Bridge': dict(name='Brooklyn Brg', over_water=True)}


def load():
    st = gpd.read_file('Streets.gpkg').to_crs(sn.CRS).reset_index(drop=True)
    wt = gpd.read_file('Water.gpkg').to_crs(sn.CRS)
    cr = pd.read_csv('Crimes.csv')
    cr = gpd.GeoDataFrame(cr, crs='EPSG:4326',
                          geometry=gpd.points_from_xy(cr['longitude'], cr['latitude']))
    cr = cr.to_crs(sn.CRS)
    return st, wt, cr


def fmt(df, cols):
    '''rounding for the markdown tables'''
    out = df.copy()
    for c, r in cols.items():
        if c in out.columns:
            out[c] = out[c].round(r)
    return out


def map_panel(ax, st, wt, box, title):
    '''common basemap for the two map figures'''
    wt.plot(ax=ax, color='#C6DBEF', edgecolor='none', zorder=0)
    st.plot(ax=ax, color='#999999', linewidth=0.5, zorder=1)
    ax.set_xlim(box[0], box[1])
    ax.set_ylim(box[2], box[3])
    ax.set_title(title, fontsize=13)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)


def buffer_map(st, wt, cr, line, seed, orders, box, nm, out):
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    seedgs = gpd.GeoSeries([line])

    # left, the buffers around the street itself
    map_panel(axs[0], st, wt, box, f'{nm}, buffers every 100m')
    sub = cr[cr.distance(line) <= 1100]
    axs[0].scatter(sub.geometry.x, sub.geometry.y, s=1.5, color=COL['brown'],
                   alpha=0.35, zorder=2)
    for d in DIST:
        gpd.GeoSeries([line.buffer(d)]).boundary.plot(
            ax=axs[0], color=COL['cdblue'], linewidth=1.0, zorder=3)
    seedgs.plot(ax=axs[0], color='k', linewidth=3.0, zorder=5)

    # right, the network orders out from that same street
    map_panel(axs[1], st, wt, box, f'{nm}, network orders 1 to {ORD}')
    cmap = plt.get_cmap('viridis')
    for o in range(ORD - 1, -1, -1):
        st.loc[orders[o]].plot(ax=axs[1], color=cmap(1 - o/(ORD-1)),
                               linewidth=1.4 + 1.6*(1 - o/(ORD-1)),
                               zorder=2 + (ORD - o))
    seedgs.plot(ax=axs[1], color='k', linewidth=3.0, zorder=40)
    sm = plt.cm.ScalarMappable(cmap=cmap.reversed(),
                               norm=plt.Normalize(vmin=1, vmax=ORD))
    cb = fig.colorbar(sm, ax=axs[1], fraction=0.046, pad=0.02)
    cb.set_label('Network order', fontsize=10)
    cb.set_ticks([1, 3, 5, 7, 10])
    fig.savefig(out, dpi=170, bbox_inches='tight')
    plt.close(fig)


MK = {'Canal St': '-o', 'Brooklyn Bridge': '-s'}


def cl(nm):
    return COL['cdblue'] if nm == 'Canal St' else COL['brown']


def denom_fig(bufs, out):
    '''What the buffer is actually dividing by'''
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.5))
    for nm in SITES:
        b = bufs[nm]
        axs[0].plot(b['To'], b['PctLand'], MK[nm], color=cl(nm),
                    markeredgecolor='white', label=nm)
        axs[1].plot(b['To'], b['StreetDens'], MK[nm], color=cl(nm),
                    markeredgecolor='white', label=nm)
        axs[2].plot(b['To'], b['PerSqKm'], MK[nm], color=cl(nm),
                    markeredgecolor='white', label=nm)
    axs[0].set_title('Percent of band that is land')
    axs[1].set_title('Street km per sq km of band')
    axs[2].set_title('Crimes per sq km of band')
    axs[0].set_ylim(0, 105)
    # headroom so the legend does not sit on the Canal St peak
    top = max(b['PerSqKm'].max() for b in bufs.values())
    axs[2].set_ylim(0, top*1.30)
    for a_ in axs:
        a_.set_xlabel('Band, outer edge (m)')
        a_.legend()
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)


def compare_fig(bufs, nets, out):
    '''Same denominator both ways, street km'''
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for nm in SITES:
        axs[0].plot(bufs[nm]['StreetKm'], bufs[nm]['PerKm'], MK[nm],
                    color=cl(nm), markeredgecolor='white', label=nm)
        axs[1].plot(nets[nm]['StreetKm'], nets[nm]['PerKm'], MK[nm],
                    color=cl(nm), markeredgecolor='white', label=nm)
    axs[0].set_title('Buffer bands', fontsize=13)
    axs[1].set_title('Network order bands', fontsize=13)
    for a_ in axs:
        a_.set_xlabel('Street km in the band')
        a_.legend()
    axs[0].set_ylabel('Crimes per street km')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    st, wt, cr = load()
    print(f'{st.shape[0]} segments, {cr.shape[0]} crimes')

    snapped = sn.snap_crimes(cr, st, max_dist=50)
    print(f'{snapped.shape[0]} crimes snapped within 50m of a segment '
          f'({100*snapped.shape[0]/cr.shape[0]:.1f}%)')

    bufs, nets, md = {}, {}, []
    for nm, cfg in SITES.items():
        cfg = dict(cfg)
        if cfg.pop('over_water', False):
            cfg['water'] = wt.geometry.union_all()
        seed, line = sn.select_site(st, **cfg)
        orders = sn.network_orders(st, seed, ORD)

        nd = sn.net_dist(st, seed)
        b = sn.buffer_table(line, st, cr, wt, DIST, ndist=nd)
        n = sn.network_table(orders, st, snapped)
        bufs[nm], nets[nm] = b, n

        slug = nm.replace(' ', '')
        b.to_csv(f'{slug}_Buffer.csv', index=False)
        n.to_csv(f'{slug}_Network.csv', index=False)

        x0, y0, x1, y1 = line.bounds
        pad = 1150
        box = (x0 - pad, x1 + pad, y0 - pad, y1 + pad)
        buffer_map(st, wt, cr, line, seed, orders, box, nm, f'{slug}_Map.png')

        print(f'\n===== {nm} (seed segment {seed}) =====')
        print('BUFFERS')
        print(fmt(b, {'Area':3,'Land':3,'PctLand':1,'StreetKm':2,'To':0,
                      'StreetDens':1,'PerKm':1,'PerSqKm':0,'PctReach':1}).to_string(index=False))
        print('NETWORK')
        print(fmt(n, {'StreetKm':2,'PerKm':1}).to_string(index=False))
        md.append((nm, b, n))

    denom_fig(bufs, 'Denominator.png')
    compare_fig(bufs, nets, 'Compare.png')
    print('\nwrote figures')
