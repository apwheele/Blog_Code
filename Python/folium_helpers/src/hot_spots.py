'''
Hotspot creation
functions
'''

import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.sparse.csgraph import connected_components
from sklearn.cluster import DBSCAN

################
# LOCAL FUNCTIONS (to make self contained)


# Convert XY or latlon into geopandas
def convgpd(data,xy,proj='EPSG:4326'):
    # default proj in Lat/Lon
    miss_xy = data[xy].isna().sum(axis=1) == 0
    d2 = data[miss_xy].reset_index(drop=True)
    geo = gpd.points_from_xy(d2[xy[0]],d2[xy[1]])
    gdf = gpd.GeoDataFrame(d2,geometry=geo,crs=proj)
    return gdf


# Point-in-Poly
def pip(points,boundary):
    b2 = boundary.copy()
    b2['BOUNDARY_ID'] = range(b2.shape[0])
    try:
        jp = gpd.sjoin(points,b2[['geometry']],how='inner',predicate='within')
    except:
        jp = gpd.sjoin(points,b2[['geometry']],how='inner',op='within')
    return jp[list(points)]


# dissolving overlap
def dissolve_overlap(data, id='lab'):
    # via https://gis.stackexchange.com/a/271737/751
    s = data.geometry
    overlap_matrix = s.apply(lambda x: s.intersects(x)).values.astype(int)
    n, ids = connected_components(overlap_matrix)
    new_data = data.reset_index(drop=True)
    new_data[id] = ids
    new_data = new_data.dissolve(by=id, aggfunc='sum')
    return new_data.reset_index()


# DBSCAN hotspots
def db_hotspots(data,distance,min_samp,sf,weight=None):
    # Create data and fit DBSCAN
    d2 = data.reset_index(drop=True)
    if weight is None:
        weight = 'weight'
        d2[weight] = 1
    xy = pd.concat([d2.geometry.x,d2.geometry.y],axis=1)
    db = DBSCAN(eps=distance, min_samples=int(np.ceil(min_samp)))
    db.fit(xy,sample_weight=d2[weight])
    max_labs = max(db.labels_)
    if max_labs == -1:
        print('No Hotspots, returning -1')
        return -1
    # Now looping over the samples, creating buffers
    # and return geopandas buffered DF
    res_buff = []
    sf2 = [weight] + sf
    for i in range(max_labs+1):
        sub_dat1 = d2[db.labels_ == i].copy()
        sd = sub_dat1[sf2].sum().to_dict()
        sub_dat2 = sub_dat1[sub_dat1.index.isin(db.core_sample_indices_)].copy()
        sub_dat2['lab'] = i
        sub_dat2.geometry = sub_dat2.buffer(distance)
        sub_dat2 = sub_dat2.dissolve('lab')
        sub_dat2['lab'] = i
        for k,v in sd.items():
            sub_dat2[k] = v
        sub_dat2 = sub_dat2[['lab'] + list(sd.keys()) + ['geometry']]
        res_buff.append(sub_dat2.copy())
    fin_file = pd.concat(res_buff).reset_index(drop=True)
    dis_file = dissolve_overlap(fin_file)
    return dis_file