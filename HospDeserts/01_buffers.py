# Function to generate distance countours given an outside area
# Geopandas object and a set of points

import geopandas as gpd
import pandas as pd
import os

os.chdir(r'C:\Users\andre\OneDrive\Desktop\HospDeserts')
hosp_data = pd.read_csv('GeocodedHosp.csv')
#Get rid of missing geocoded
hosp_data = hosp_data[hosp_data['match']].copy()
state = hosp_data['address'].str.split(',').str[-2].str.strip()
hosp_data = hosp_data[ state == 'TX' ].copy()
hosp_data.reset_index(inplace=True, drop=True)

#Converting to geodataframe
hosp_geo = gpd.GeoDataFrame(hosp_data, geometry=gpd.points_from_xy(hosp_data.lon, hosp_data.lat), crs="EPSG:4326")

#Getting boundary of Texas shapefile
texas_counties = gpd.read_file(r'tl_2016_48_cousub\tl_2016_48_cousub.shp')
texas_outline = texas_counties.dissolve('STATEFP')
texas_proj = texas_outline.to_crs('EPSG:5070')
#print(texas_outline.crs)

def dissolve_buff(point_df,d,resolution):
    bu = point_df.buffer(d,resolution)
    geodf = gpd.GeoDataFrame(geometry=bu)
    geodf['Const'] = 0
    single = geodf.dissolve('Const')
    return single[['geometry']]

def dist_cont(point_df,dist_list,outside,buff_res):
    if point_df.crs != outside.crs:
        print('Point df and Outside df are not the same CRS')
        return None
    # Making outside area out dissolved object
    out_cop = outside[['geometry']].copy()
    out_cop['Constant'] = 1
    out_cop = out_cop.dissolve('Constant')
    # Make sure points are inside area
    inside = point_df.within(out_cop['geometry'][1])
    point_cop = point_df[inside].copy()
    point_cop = point_df.copy()
    point_cop['Constant'] = 1 #Constant for dissolve
    point_cop = point_cop[['Constant','geometry']].copy()
    res_buffers = []
    for i,d in enumerate(dist_list):
        print(f'Doing buffer {d}')
        if i == 0:
            res = dissolve_buff(point_cop, d, buff_res)
            res_buffers.append(res.copy())
        else:
            res_new = dissolve_buff(point_cop, d, buff_res)
            res_buffonly = gpd.overlay(res_new, res, how='difference')
            res = res_new.copy()
            res_buffers.append( res_buffonly.copy() )
    # Now take the difference with the larger area
    print('Working on leftover difference now')
    leftover = gpd.overlay(out_cop, res, how='difference')
    res_buffers.append(leftover)
    for i,d in enumerate(dist_list):
        res_buffers[i]['Distance'] = str(d)
    res_buffers[-1]['Distance'] = 'Outside'
    # New geopandas DF
    comb_df = pd.concat(res_buffers)
    comb_df.reset_index(inplace=True, drop=True)
    return comb_df

# gpd.datasets.available
# ['naturalearth_cities', 'naturalearth_lowres', 'nybb']

#world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
#us = world[world['name'] == 'United States of America'].copy()
#us_albers = us.to_crs('EPSG:5070') #This is in Meters

#If you want can use this as an example
#cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))
#cities_albers = cities.to_crs('EPSG:5070')

#hosp_geo = hosp_geo.sample(100).reset_index(drop=True)
hos_proj = hosp_geo.to_crs('EPSG:5070') #'epsg:4269'

dist_met = [2000, 4000, 8000, 16000] #, 32000
buff_city = dist_cont(hos_proj, dist_met, texas_proj, buff_res=100)

#Now making folium plot
buff_map = buff_city.to_crs('EPSG:4326')
kv = list(hosp_geo)[1:10]

#"fill": "#00aa22",
#"fill-opacity": 0.5

cols = ['#f1eef6',
'#d7b5d8',
'#df65b0',
'#dd1c77',
'#980043']

buff_map['fill'] = cols
buff_map['fill-opacity'] = 0.35

#os.chdir(r'D:\Dropbox\Dropbox\PublicCode_Git\Blog_Code')

buff_map.to_file('Buffers.geojson', driver='GeoJSON')
hosp_geo.to_file('Hosp.geojson', driver='GeoJSON')

###############################################
#import json
#import folium
#from folium.plugins import MarkerCluster

# Center on Dallas, tiles='cartodbpositron', [32.795536, -96.831840] Dallas

#m = folium.Map(location=[hosp_geo['lat'][0], hosp_geo['lon'][0]], zoom_start=10, tiles='openstreetmap')
#folium.TileLayer('cartodbpositron').add_to(m)
#folium.LayerControl().add_to(m)

# Add in buffers one at a time as feature group

# Add in points as feature group
#pops, locs = [], []
#for i in hosp_geo.index:
#    ht = hosp_geo.loc[i, kv].to_frame().to_html(header=False)
#    coord = [hosp_geo['lat'][i], hosp_geo['lon'][i]]
#    pops.append( ht )
#    locs.append(coord)
#    folium.Marker(location=coord,popup=ht,name='Provider').add_to(m)

#Need to figure out how to turn on/off feature group for points one
#At a time


#buff_map.loc[[0],].to_file("t1.geojson", driver='GeoJSON')
#geo_json_data = json.loads("t1.geojson")
#buff_map.to_file('Buffers.geojson', driver='GeoJSON')

#folium.GeoJson(buff_map.loc[[0],].add_to(m)
#folium.GeoJson(buff_map).add_to(m)


#folium.GeoJson(buff_map,name='Buffers').add_to(m)

#for i in buff_city.index:
#    

#Save map
#m.save("Buffers.html")
##############################################

