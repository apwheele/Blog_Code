'''
Showing off folium helpers
To make nicer legend
'''

from src import folium_helpers as fh
from src import hot_spots as hs
import geopandas as gpd
import pandas as pd

# This is local Austin projection
loc_proj = 'EPSG:2277'

# Get neighborhoods
neigh_url = r'https://data.austintexas.gov/api/geospatial/a7ap-j2yt?accessType=DOWNLOAD&method=export&format=GeoJSON'
austin_neigh = gpd.read_file(neigh_url)
austin_neigh = austin_neigh.to_crs(loc_proj)

# Dissolve for Austin boundary
austin_neigh['Const'] = 1
austin_bound = austin_neigh.dissolve(by='Const')

# Calculate traffic hotspots
traff = r'https://data.austintexas.gov/api/views/dx9v-zd7x/rows.csv?accessType=DOWNLOAD'
traff_df = pd.read_csv(traff)
traff_df = hs.convgpd(traff_df,['Longitude','Latitude'])
traff_df = traff_df.to_crs(loc_proj)
traff_df = hs.pip(traff_df,austin_bound)

inj_list = ['COLLISION WITH INJURY',
            'TRAFFIC FATALITY',
            'FLEET ACC/ INJURY',
            'FLEET ACC/ FATAL']

traff_df['Pedestrian'] = 1*(traff_df['Issue Reported'] == 'AUTO/ PED')
traff_df['Injury'] = 1*traff_df['Issue Reported'].isin(inj_list)
traff_df['Total'] = 1 # maybe want to get rid of obstruction

traff_hotspots = hs.db_hotspots(traff_df,500,500,['Total','Injury','Pedestrian'])
traff_hotspots['SqMile'] = traff_hotspots.geometry.area/(5280**2)

# Header/Footer
traff_hotspots['Head'] = ("<b>Traffic HotSpot" + (traff_hotspots['lab'] + 1).astype(str) + "</b>")

traff_hotspots['Foot'] = ("Square Miles " + traff_hotspots['SqMile'].map('{:,.2f}'.format) +
                            ".")


# Now create choropleth for neighborhoods
austin_neigh['Labs'] = pd.cut(austin_neigh['sqmiles'].astype(float),[0,1,2,4,17]).astype(str)
fin_labs = pd.unique(austin_neigh['Labs']).tolist()
fin_labs.sort()
lab_cols = fh.make_palette(['Extra'] + fin_labs, 'RdPu')
lab_cols.pop('Extra')

# Now making the final folium map

bm = fh.base_folium(austin_bound)

fh.add_hotspots(bm,traff_hotspots,['Total','Injury'],'Head','Foot',
             "Traffic HotSpots","green","darkgreen")

fh.add_choro(bm,austin_neigh,'Labs',lab_cols,['fid','sqmiles', 'neighname'],
             name="Neighborhood Square Miles",
             edge='#5A5A5A',
             edge_weight=0.5)

fh.save_map(bm,"Austin_Map3.html")