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
from scipy.sparse.csgraph import connected_components
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
            'where': ("crime_category IN ('MURDER','ROBBERY','ASSAULT','BURGLARY/RESIDENTIAL', "
                      "'WEAPONS VIOLATION')"
                      " AND (reported_year >= 2020)"
                      " AND crime_code NOT IN ('25E','20A')")}

# May also want to include DRUGS (felony)
# and LARCENY FROM MV
# eliminate Robbery business and simple assaults

def get_crimes(ral_outline):
    crimes = query_esri(params=crime_pa)
    # Getting rid of null data
    crimes = crimes[~crimes.geometry.isnull()].copy()
    # Only keeping points inside city boundary
    crimes_proj = crimes.to_crs(loc_proj).reset_index(drop=True)
    in_ral = crimes_proj.geometry.intersects(ral_outline.geometry[0])
    crimes_proj = crimes_proj[in_ral].copy()
    return crimes_proj


def dissolve_overlap(data, id='lab'):
    # via https://gis.stackexchange.com/a/271737/751
    s = data.geometry
    overlap_matrix = s.apply(lambda x: s.intersects(x)).values.astype(int)
    n, ids = connected_components(overlap_matrix)
    new_data = data.reset_index(drop=True)
    new_data[id] = ids
    new_data = new_data.dissolve(by=id, aggfunc='sum')
    return new_data.reset_index()


def db_hotspots(data,distance,min_samp,sf,weight=None):
    # Create data and fit DBSCAN
    d2 = data.reset_index(drop=True)
    if weight is None:
        weight = 'weight'
        d2[weight] = 1
    xy = pd.concat([d2.geometry.x,d2.geometry.y],axis=1)
    db = DBSCAN(eps=distance, min_samples=min_samp)
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

# Getting outline data and crime data
ral_area = get_ral()
cr = get_crimes(ral_area)

# Adding in crime dummies for aggregate stats
# for DBSCAN hot spots
cats = pd.get_dummies(cr['crime_category'])
cr[list(cats)] = cats
cr['TotCrime'] = 1
sum_fields = list(cats)

# Now estimating the DBSCAN hotspots
# 34 is so hot spots have more than 1 crime per
# month
hot_spots = db_hotspots(cr,400,34,sum_fields,'TotCrime')

#fig, ax = plt.subplots()
#ral_area.boundary.plot(ax=ax, linewidth=0.8, edgecolor='k')
#hot_spots.plot(ax=ax)
#plt.show()

# Now lets make a nice folium map
ral_sph = ral_area.to_crs(sph_proj)
hot_sph = hot_spots.to_crs(sph_proj)

# If you want to save to different formats
#hot_sph.to_file('hotspot.shp')
#hot_sph.to_file('hotspot.geojson', driver='GeoJSON')


# Make a nice PNG map of Raleigh TODO

############################################################################
# Make a nice folium map
ral_map = folium.Map(location=[35.796315, -78.640539], zoom_start=12)
folium.TileLayer('cartodbpositron').add_to(ral_map)
#folium.LayerControl().add_to(ral_map)

# Add in boundary
bound = ral_sph['geometry'].explode()
bound = bound.boundary.explode().to_json()

def bound_func(x):
    di = {"color":"#000000",
          "weight": 5,
          "opacity": 0.3}
    return di

folium.GeoJson(bound, style_function=bound_func).add_to(ral_map)

# Add in each polygon
hot_sph['area'] = hot_spots.geometry.area
hot_sph.sort_values('area',inplace=True,ascending=False)

def hs_func(x):
    di = {"fillColor":"#ADD8E6",
          "fillOpacity": 0.5}
    return di

for l in hot_sph['lab']:
    sub_data = hot_sph.loc[[l],:]
    geo_j = sub_data.geometry.to_json()
    geo_j = folium.GeoJson(data=geo_j,style_function=hs_func)
    # Adding in label table
    lab_data = pd.DataFrame(sub_data[sum_fields].T.reset_index())
    html_lab = lab_data.to_html(index=False,header=False)
    folium.Popup(html_lab).add_to(geo_j)
    geo_j.add_to(ral_map)

ral_map.save("Raleigh_HotSpots.html")
############################################################################