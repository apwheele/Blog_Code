'''
Helper functions to query
ESRI tables for Raleigh

Andy Wheeler
'''


import folium
import geopandas as gpd
from io import StringIO
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from sklearn.cluster import DBSCAN
from urllib.parse import quote

def query_esri(base='https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Police_Incidents/FeatureServer/0/query',
               params={'f': 'geojson', 'outFields': "*",},
               chunk=5000):
    fin_url = base + "?"
    amp = ""
    fi = 0
    for key,val in params.items():
        fin_url += amp + key + "=" + quote(val)
        amp = "&"
    #print("Fin URL \n\n")
    #print(fin_url)
    # First, getting the total count
    count_url = fin_url + "&returnCountOnly=true"
    response_count = requests.get(count_url)
    try:
        count_n = response_count.json()['count']
    except:
        count_n = response_count.json()["properties"]["count"]
    #print(f"Total number of records to query {count_n}")
    # If over chunksize doing in smaller batches
    if count_n < chunk:
        full_response = requests.get(fin_url)
        dat = gpd.read_file(StringIO(full_response.text))
        return dat
    else:
        offset = 0
        dat_li = []
        remaining = count_n
        while remaining > 0:
            offset_val = f"&cacheHint=true&resultOffset={offset}&resultRecordCount={chunk}"
            off_url = fin_url + offset_val
            part_response = requests.get(off_url)
            dat_li.append(gpd.read_file(StringIO(part_response.text)))
            offset += chunk
            remaining -= chunk
        return pd.concat(dat_li)


loc_proj = 'EPSG:2264'
sph_proj = 'EPSG:4326'

jur_url = r"https://maps.wakegov.com/arcgis/rest/services/Jurisdictions/Jurisdictions/MapServer/1/query"
jur_par = {'f': 'geojson',
           'outFields': "*",
           'where': "JURISDICTION IN ('RALEIGH')"}

def get_ral():
    res_geo = query_esri(jur_url,jur_par)
    # Should maybe dissolve/make border nicer
    ra_proj = res_geo.dissolve(by='JURISDICTION').to_crs(loc_proj)
    #ra_simple = ra_proj.copy()
    #ra_simple.geometry = ra_proj.geometry.buffer(1200).simplify(1200).buffer(-1000).simplify(1000)
    return ra_proj

crime_pa = {'f': 'geojson',
            'outFields': "*",
            'where': "crime_category IN ('MURDER','ROBBERY','ASSAULT','BURGLARY/RESIDENTIAL') AND (reported_year >= 2020)"}

def get_crimes(ral_outline):
    crimes = query_esri(params=crime_pa)
    # Getting rid of null data
    crimes = crimes[~crimes.geometry.isnull()].copy()
    # Only keeping points inside city boundary
    crimes_proj = crimes.to_crs(loc_proj).reset_index(drop=True)
    in_ral = crimes_proj.geometry.intersects(ral_outline.geometry[0])
    crimes_proj = crimes_proj[in_ral].copy()
    return crimes_proj


def db_hotspots(data,distance,min_samp,sf,weight=None):
    # Create data and fit DBSCAN
    xy = pd.concat([data.geometry.x,data.geometry.y],axis=1)
    db = DBSCAN(eps=500, min_samples=34)
    db.fit(xy,sample_weight=weight)
    max_labs = max(db.labels_)
    if max_labs == -1:
        print('No Hotspots, returning -1')
        return -1
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    # Now looping over the samples, creating buffers
    # and return geopandas buffered DF
    res_buff = []
    for i in range(max_labs+1):
        sub_dat1 = data[db.labels_ == i].copy()
        sd = sub_dat1[sf].sum().to_dict()
        sub_dat2 = data[db.labels_ == i & core_samples_mask].copy()
        sub_dat2['lab'] = i
        sub_dat2.geometry = sub_dat2.buffer(distance)
        sub_dat2 = sub_dat2.dissolve('lab')
        sub_dat2['lab'] = i
        for k,v in sd.items():
            sub_dat2[k] = v
        sub_dat2 = sub_dat2[['lab'] + list(sd.keys()) + ['geometry']]
        res_buff.append(sub_dat2.copy())
    return pd.concat(res_buff)


def db_hotspots(data,distance,min_samp,sf,weight=None):
    # Create data and fit DBSCAN
    xy = pd.concat([data.geometry.x,data.geometry.y],axis=1)
    db = DBSCAN(eps=distance, min_samples=min_samp)
    db.fit(xy,sample_weight=None)
    max_labs = max(db.labels_)
    #if max_labs == -1:
    #    print('No Hotspots, returning -1')
    #    return -1
    # Now looping over the samples, creating buffers
    # and return geopandas buffered DF
    res_buff = []
    for i in range(max_labs+1):
        sub_dat1 = data[db.labels_ == i].copy()
        sd = sub_dat1[sf].sum().to_dict()
        sub_dat2 = sub_dat1[sub_dat1.index.isin(db.core_sample_indices_)].copy()
        sub_dat2['lab'] = i
        sub_dat2.geometry = sub_dat2.buffer(500)
        sub_dat2 = sub_dat2.dissolve('lab')
        sub_dat2['lab'] = i
        for k,v in sd.items():
            sub_dat2[k] = v
        sub_dat2 = sub_dat2[['lab'] + list(sd.keys()) + ['geometry']]
        res_buff.append(sub_dat2.copy())
    fin_file = pd.concat(res_buff).reset_index(drop=True)
    return fin_file

# Getting outline data and crime data
ral_area = get_ral()
cr = get_crimes(ral_area)

# Adding in crime dummies for aggregate stats
# for DBSCAN hot spots
cats = pd.get_dummies(cr['crime_category'])
cr[list(cats)] = cats
cr['TotCrime'] = 1
sum_fields = list(cats) + ['TotCrime']

# Now estimating the DBSCAN hotspots
# 34 is so hot spots have more than 1 crime per
# month
hot_spots = db_hotspots(cr,500,34,sum_fields)

#fig, ax = plt.subplots()
#ral_area.boundary.plot(ax=ax, linewidth=0.8, edgecolor='k')
#hot_spots.plot(ax=ax)
#plt.show()

# Now lets make a nice folium map
#ral_sph = ral_area.to_crs(sph_proj)
#hot_sph = hot_spots.to_crs(sph_proj)

#hot_spots.to_file('hotspot.shp')
hot_spots.to_file('hotspot.geojson', driver='GeoJSON')