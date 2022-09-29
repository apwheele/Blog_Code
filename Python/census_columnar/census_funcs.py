'''
These download the files
from the census FTP site
for small areas

Maybe will work back to 2009
pandas excel reader to back 
then would need both xls and
xlsx

Andy Wheeler
'''


import os
import pandas as pd
import requests
import zipfile
from io import BytesIO


# Get template per year, note some older years have the
# template in a different location
def get_template(year):
    # Getting zipfile
    base_url = f'https://www2.census.gov/programs-surveys/acs/summary_file/{year}/data/'
    temp = base_url + f'{year}_5yr_Summary_FileTemplates.zip'
    req = requests.get(temp)
    zf = zipfile.ZipFile(BytesIO(req.content))
    # looping over each file in here and extracting
    temp_di = {}
    for fi in zf.filelist:
        fi_nm = fi.filename
        loc_df = pd.read_excel(zf.open(fi_nm))
        # keys are field names, values are labels
        seq_info = loc_df.T.to_dict()[0]
        # parsing filenames
        if fi_nm.lower().find('geo') > -1:
            temp_di['geo'] = seq_info
        else:
            ts = fi_nm.replace('seq','')
            ts = ts.replace('.xlsx','')
            ts = ts.replace('.xls','')
            ts = ts.zfill(3)
            temp_di[ts] = seq_info
    return temp_di


# Given a state abbreviation/name
# and a set of template files
# extract all the data in pandas DFs
def get_state(year,st_ab,st_nm,templates):
    base_url = f'https://www2.census.gov/programs-surveys/acs/summary_file/{year}/data/'
    st_baseurl = base_url + f'5_year_seq_by_state/{st_nm}/Tracts_Block_Groups_Only/'
    st_li = []
    # These vars are always strings, rest can be float (maybe int?)
    str_vars = ['FILEID', 'STUSAB', 'COMPONENT', 'AIHHTLI', 'UR', 'PCI', 'GEOID',
                'NAME', 'FILETYPE', 'CHARITER', 'SEQUENCE', 'LOGRECNO']
    str_dtype = {v:"str" for v in str_vars}
    # Now looping over each file that should be in the state
    for fi in templates.keys():
        fi_cols = list(templates[fi].keys())
        # some floats
        fi_dtypes = {k:'float' for k in fi_cols}
        for v in str_vars:
            if v in fi_dtypes:
                fi_dtypes[v] = 'float'
        if fi == 'geo':
            # geo file is not zipped up
            loc_url = st_baseurl + f'g{year}5{st_ab}.csv'
            loc_dat = pd.read_csv(loc_url,names=fi_cols,index_col='LOGRECNO',
                                  dtype=str_dtype,encoding='latin_1',
                                  keep_default_na=False,na_values=[".", ""],
                                  low_memory=False)
        else:
            loc_filename = f'{year}5{st_ab}0{fi}000'
            loc_url = st_baseurl + f'{loc_filename}.zip'
            req = requests.get(loc_url)
            zf = zipfile.ZipFile(BytesIO(req.content))
            # only worry about extracting the estimates file
            lf = 'e' + loc_filename + '.txt'
            loc_dat = pd.read_csv(zf.open(lf),index_col='LOGRECNO',
                                 names=fi_cols,
                                 dtype=str_dtype,encoding='latin_1',
                                 keep_default_na=False,na_values=[".", ""],
                                 low_memory=False)
        st_li.append(loc_dat)
    st_res = pd.concat(st_li,axis=1,join='inner')
    # Drop duplicated columns
    st_res = st_res.loc[:,~st_res.columns.duplicated()].copy()
    # Transforming to int if possible
    for v in list(st_res):
        if v not in str_vars:
            try:
                x = df_data[v].astype("Int64")
                st_res[v] = x
            except:
                continue
    return st_res


# List of states and abbreviations
# can update to full set if you
# want the whole thing
states = {'de': 'Delaware',
          'tx': 'Texas'}

def get_data(state_di=states,year=2019):
    # Get template first
    temp = get_template(year)
    # Now go through the states dict
    res_li = []
    for ab,stn in state_di.items():
        locpd = get_state(year,ab,stn,templates=temp)
        res_li.append(locpd.copy())
    # Combo those states together
    full_set = pd.concat(res_li,axis=0)
    # There are some columns all missing
    drop_list = []
    for v in list(full_set):
        if full_set[v].isna().sum() == full_set.shape[0]:
            drop_list.append(v)
    full_set.drop(columns=drop_list,inplace=True)
    return full_set, temp
