'''
Helper functions for geo data analysis
and grabbing Raleigh data
'''

import geopandas as gpd
from io import StringIO
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from urllib.parse import quote
import os
from shapely.geometry import Polygon

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


# Generating spatial grid over the city
# adapted via https://gis.stackexchange.com/a/316460/751
def grid_over(base, size, percent=None):
    b2 = base.copy()
    b2['XXX_BASECONSTANT_XXX'] = 1
    xmin, ymin, xmax, ymax = base.total_bounds
    xl = np.arange(xmin, xmax, size)
    yl = np.arange(ymin, ymax, size)
    polygons = []
    xc = []
    yc = []
    half = size/2.0
    for x in xl:
        for y in yl:
            polygons.append(Polygon([(x,y), (x+size, y), (x+size, y+size), (x, y+size)]))
            xc.append(x+half)
            yc.append(y+half)
    grid = gpd.GeoDataFrame({'geometry':polygons}).set_crs(base.crs)
    grid['X'] = xc
    grid['Y'] = yc
    grid_fields = list(grid)
    #gj = gpd.sjoin(grid,base,how='left',op='intersects')
    gj = gpd.sjoin(grid,b2,how='left',predicate='intersects')
    gloc = gj[~gj['XXX_BASECONSTANT_XXX'].isna()]
    gloc = gloc[grid_fields].reset_index(drop=True)
    if percent:
        gj2 = gpd.overlay(gloc,b2,how='intersection')
        perc = gj2.geometry.area/gloc.geometry.area
        gloc = gloc[perc > percent].reset_index()
    return gloc

# This modifies poly in place
def count_points(poly,points,var_name):
    #join = gpd.sjoin(points, poly, how="left", op='intersects')
    join = gpd.sjoin(points, poly, how="left",predicate='intersects')
    cnt = join['index_right'].value_counts()
    poly[var_name] = cnt
    poly[var_name].fillna(0,inplace=True)


# Get the Raleigh data, cache it
if os.path.exists('./data/RaleighCounts.csv'):
    pass
else:
    ral = get_ral()
    grid_size = 1000
    ral_grid = grid_over(ral,grid_size,0.8)
