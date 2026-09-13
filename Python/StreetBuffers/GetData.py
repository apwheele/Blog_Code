'''
Downloads the three inputs for the buffer vs street network demo:

  1. NYPD complaint data (thefts and robberies) for lower Manhattan and the
     Brooklyn Bridge, from NYC Open Data
  2. TIGER/Line EDGES for New York and Kings counties, via pygris. Edges are
     split at every intersection and carry from/to node ids, which is what
     makes the network expansion possible. The friendlier pygris.roads()
     function returns whole named streets (all of Canal St is one feature),
     which is no good for this.
  3. TIGER area water, so we can say how much of a buffer is the East River

Writes Crimes.csv, Streets.gpkg and Water.gpkg
'''

import geopandas as gpd
import pandas as pd
import requests
from pygris import area_water
from pygris.helpers import _load_tiger

# study window and bounding box, covers Canal St and the Brooklyn Bridge
BEG, END = '2023-01-01', '2025-12-31'
LAT = (40.690, 40.735)
LON = (-74.025, -73.975)

THEFT = ['PETIT LARCENY','GRAND LARCENY']
ROBB = ['ROBBERY']

URL = 'https://data.cityofnewyork.us/resource/qgea-i56i.json'
FIELDS = 'cmplnt_num,cmplnt_fr_dt,ofns_desc,law_cat_cd,boro_nm,latitude,longitude'

# New York county (Manhattan) and Kings county (Brooklyn)
FIPS = {'New York':'36061','Kings':'36047'}
EDGE = 'https://www2.census.gov/geo/tiger/TIGER2023/EDGES/tl_2023_{f}_edges.zip'

# travel ways, dropping ramps, service drives, parking lot roads and the like
KEEP = ['S1100','S1200','S1400','S1710','S1730']


def get_crimes():
    inlist = ','.join(f"'{o}'" for o in THEFT + ROBB)
    where = (f"cmplnt_fr_dt >= '{BEG}T00:00:00' and cmplnt_fr_dt <= '{END}T23:59:59' "
             f"and ofns_desc in({inlist}) "
             f"and latitude between {LAT[0]} and {LAT[1]} "
             f"and longitude between {LON[0]} and {LON[1]}")
    res, off, page = [], 0, 50000
    while True:
        params = {'$select':FIELDS,'$where':where,'$limit':page,'$offset':off,
                  '$order':'cmplnt_num'}
        r = requests.get(URL,params=params,timeout=600)
        r.raise_for_status()
        js = r.json()
        if not js:
            break
        res.append(pd.DataFrame(js))
        print(f'  pulled {len(js)} rows at offset {off}')
        off += page
        if len(js) < page:
            break
    cr = pd.concat(res,ignore_index=True)
    cr['latitude'] = cr['latitude'].astype(float)
    cr['longitude'] = cr['longitude'].astype(float)
    cr['cmplnt_fr_dt'] = pd.to_datetime(cr['cmplnt_fr_dt'])
    cr['Crime'] = 'Theft'
    cr.loc[cr['ofns_desc'].isin(ROBB),'Crime'] = 'Robbery'
    return cr


def get_streets():
    res = []
    for cty, f in FIPS.items():
        e = _load_tiger(EDGE.format(f=f), cache=True)
        e = e[(e['ROADFLG']=='Y') & (e['MTFCC'].isin(KEEP))].copy()
        e['County'] = cty
        res.append(e[['TLID','FULLNAME','MTFCC','TNIDF','TNIDT','County','geometry']])
    st = gpd.GeoDataFrame(pd.concat(res,ignore_index=True),crs=res[0].crs)
    # clip to the study bounding box with a margin so the network does not
    # dead end right at the edge of the analysis area
    st = st.cx[LON[0]-0.015:LON[1]+0.015, LAT[0]-0.015:LAT[1]+0.015]
    return st.reset_index(drop=True)


def get_water():
    res = [area_water(state='NY',county=c,year=2023,cache=True) for c in FIPS]
    wt = gpd.GeoDataFrame(pd.concat(res,ignore_index=True),crs=res[0].crs)
    return wt[['FULLNAME','AWATER','geometry']].reset_index(drop=True)


if __name__ == '__main__':
    print('Downloading NYPD complaints')
    cr = get_crimes()
    cr.to_csv('Crimes.csv',index=False)
    print(cr['Crime'].value_counts(),'\n')

    print('Downloading TIGER edges')
    st = get_streets()
    st.to_file('Streets.gpkg',driver='GPKG')
    print(f'{st.shape[0]} street segments')
    print(st['MTFCC'].value_counts(),'\n')

    print('Downloading TIGER water')
    wt = get_water()
    wt.to_file('Water.gpkg',driver='GPKG')
    print(f'{wt.shape[0]} water polygons')
