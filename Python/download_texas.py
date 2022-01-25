'''
Downloading and extracting 5 year ACS census data
to location of choice

Andy Wheeler
'''

import requests
import re
import os 
import posixpath
import shutil
from bs4 import BeautifulSoup
import warnings

def down_request(url,name,loc,verify=False,warn=False):
    if not warn:
        warnings.filterwarnings('ignore',module='requests')
    with open(os.path.join(loc,name), 'wb') as f:
        resp = requests.get(url, verify=verify)
        f.write(resp.content)

def get_acs5yr(year,state,downfold):
    base = r'https://www2.census.gov/programs-surveys/acs/summary_file/'
    yeardat = posixpath.join(base,str(year),'data')
    # Get the template
    temp_zip = f'{year}_5yr_Summary_FileTemplates.zip'
    temp_url = posixpath.join(yeardat,temp_zip)
    temp_down = os.path.join(downfold,temp_zip)
    down_request(temp_url,temp_zip,downfold)
    shutil.unpack_archive(temp_down, os.path.join(downfold,temp_zip[0:-4]))
    os.remove(temp_down)
    # Create a folder for the data
    tab_down = os.path.join(downfold,'tables')
    os.mkdir(tab_down)
    # Getting all of the zip files and geo files
    statedata = posixpath.join(yeardat,'5_year_seq_by_state',state,'Tracts_Block_Groups_Only')
    statepage = requests.get(statedata, verify=False)
    soup = BeautifulSoup(statepage.content, 'html.parser')
    for z in soup.find_all(href=re.compile('(zip|csv|txt)')):
        down_url = posixpath.join(statedata, z.string)
        down_fil = os.path.join(tab_down,z.string)
        down_request(down_url,z.string,tab_down)
        if z.string[-3] == 'z':
            shutil.unpack_archive(down_fil,tab_down)
            os.remove(down_fil)

get_acs5yr(2019,'Texas',r'C:\Users\e009156\Desktop\TexasCensus')