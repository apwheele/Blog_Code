# https://www.bls.gov/oes/current/oes172031.htm

from bs4 import BeautifulSoup
import folium
import geopandas as gpd
from matplotlib import pyplot as plt
import pandas as pd
import pyproj
import requests

# Get a pandas dataframe of occupational codes from BLS
def ocodes():
    occ_url = r'https://www.bls.gov/oes/current/oes_stru.htm'
    occpage = requests.get(url=occ_url)
    soup = BeautifulSoup(occpage.content,'html.parser')
    oe = soup.find_all("a",href=re.compile(r"oes\d{5}"))
    res = []
    for o in oe:
        oc = o['href'].replace('oes','')[0:6]
        desc = o.text.replace('\r\n','')
        d2 = " ".join(desc.split())
        res.append((oc,d2))
    res_df = pd.DataFrame(res,columns=['OCode','Desc'])
    return(res_df)

# Get Pandas dataframe of metro areas occupation stats given ocode
def oes_geo(ocode):
    # via https://curlconverter.com/#
    # https://data.bls.gov/oes/#/occGeo/One%20occupation%20for%20multiple%20geographical%20areas
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'Accept': 'application/json, text/plain, */*',
        'DNT': '1',
        'Content-Type': 'application/json;charset=UTF-8',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'Origin': 'https://data.bls.gov',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://data.bls.gov/oes/',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    data = '''{"areaTypeCode":"M","areaCode":["xxxxxxx"],"industryCode":"000000",'''
    data += f'''"occupationCode":"{ocode}","datatype":["xxxxxx"],'''
    data += '''"releaseDateCode":["2020A01"],"outputType":"H"}'''
    url = r'https://data.bls.gov/OESServices/resultsoccgeo'
    response = requests.post(url, headers=headers, data=data)
    rj = response.json()
    vallabs = pd.DataFrame(rj['resultsOccGeoVO'][0]['dataTypes'])
    vallabs.set_index('dataTypeCode',inplace=True)
    dl = vallabs['dataTypeName'].to_dict()
    rj_li = []
    for ar in rj['resultsOccGeoVO'][0]['areas']:
        dat = pd.DataFrame(ar['values'])
        dat['areaCode'] = ar['areaCode']
        dat['areaName'] = ar['areaName']
        rj_li.append(dat.copy())
    rj_full = pd.concat(rj_li,axis=0,ignore_index=True)
    pivoted = rj_full.pivot(['areaCode','areaName'], 'dataTypeCode', 'value')
    pivoted.rename(columns=dl,inplace=True)
    pivoted.reset_index(inplace=True)
    pivoted['ocode'] = ocode
    return pivoted.reset_index()

# Gets the areas for the BLS survey
# Takes a bit to churn through everything
def get_areas():
    # First get the excel data file that defines the BLS areas
    msdf = pd.read_excel('https://www.bls.gov/oes/2020/may/area_definitions_m2020.xlsx')
    # Calculate GEOID
    msdf['GEOID'] = msdf['FIPS code'].astype(str).str.zfill(2) + msdf['County code'].astype(str).str.zfill(3)
    # Next get the county shapefile
    url_county = r'https://www2.census.gov/geo/tiger/TIGER2019/COUNTY/tl_2019_us_county.zip'
    county = gpd.read_file(url_county)
    # Merge the two together
    geo_msdf = gpd.GeoDataFrame(msdf.merge(county,on='GEOID',how='left'))
    # Dissolve into greater areas
    geo_diss = geo_msdf.dissolve(by=['May 2020 MSA code ','May 2020 MSA name']).reset_index()
    # Project into Albers for centroid
    alber = geo_diss.to_crs('epsg:5070')
    xa = alber.geometry.centroid.x
    ya = alber.geometry.centroid.y
    transformer = pyproj.Transformer.from_crs('epsg:5070','epsg:4326')
    lat_a, lon_a = transformer.transform(xa,ya)
    alber['lat'] = lat_a
    alber['lon'] = lon_a
    return alber

# Merges BLS data and cleans up data
def merge_occgeo(occ_df,geo_df):
    # Cleaning up geo dataframe
    geo2 = geo_df.copy()
    drcol = set(list(geo2)) - set(['lat','lon','May 2020 MSA code ','geometry'])
    geo2.drop(columns=drcol,inplace=True)
    geo2.rename(columns={'May 2020 MSA code ':'areaCode'},inplace=True)
    geo2['areaCode'] = geo2['areaCode'].astype(str).str.zfill(7)
    # Merging with occupational data
    om = gpd.GeoDataFrame(occ_df.merge(geo2,on='areaCode',how='left'))
    # Selecting out missing data
    nm_emp = pd.to_numeric(om['Employment'],errors='coerce')
    nm_valid = ~nm_emp.isna()
    om = om[nm_valid].copy()
    # Turning objects into numeric
    num_col = set(list(om)) - set(['areaCode', 'areaName','lat','lon','May 2020 MSA code ','geometry','ocode', 'GEOID'])
    for v in num_col:
        om[v] = pd.to_numeric(om[v],errors='coerce')
    return om

def state_albers():
    state_url = r'https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_500k.zip'
    state = gpd.read_file(state_url)
    state_albers = state.to_crs('epsg:5070')
    return state_albers

# 02 Alaska, 15 Hawaii, rest territories
not_48 = ['72','02','78','15','66','69']

# HTML popup function helper for folium maps
def html_popup(li,nm,fm):
    # First row, no br
    lf = li[0].__format__(fm[0]) # hacky
    res = f'<strong>{nm[0]}: </strong>{lf}'
    for n,l,f in zip(nm[1:],li[1:],fm[1:]):
        # Can get errors for missing data
        try:
            lu = l.__format__(f)
        except:
            lu = str(l)
        res += f'<br><strong>{n}: </strong>{lu}'
    return res

def fol_map(data,val,lat_lon,att,fmt,scale=(20000,100000)):
    '''
    Creating a folium dot map for US
    
    data -- data frame with lat/lon and attributes
    val -- string for variable name to scale circles by
    lat_lon -- tuple with strings for lat/lon variable names
    att -- list of variable names for popups
    fmt -- list of formats for strings
    scale -- tuple min/max scale for the circles
    
    returns folium map object, can render in Jupyter 
            or use m.save('map.html')
    '''
    # Overview of US
    m = folium.Map(location=[40.4376, -100.1123], zoom_start=4)
    # Sorting by value, so smaller are always drawn later?
    # Subset of the data used for the labels
    dat_sub = data[att].copy()
    dat_sub.fillna('-',inplace=True)
    # Scaling value data to min/max
    ra = data[val].max() - data[val].min()
    rs = scale[1] - scale[0]
    val = (data[val] - data[val].min())/ra
    val = val*rs + scale[0]
    # Height for popup
    hp = len(att)*25 + 25
    # Looping over the dataframe, appending lat/lon
    for i in data.index:
        # labels
        ld = dat_sub.loc[i,].to_list()
        ht = html_popup(ld,att,fmt)
        ifr = folium.IFrame(ht)
        pu = folium.Popup(ifr,min_width=500,max_width=500,maxHeight=hp)
        # lat/lon points
        ll = data.loc[i,lat_lon].to_list()
        folium.Circle(radius=val[i],
                      location=ll,
                      popup=pu,
                      color='crimson',
                      fill=True,
                      fill_color='pink').add_to(m)
    return m
