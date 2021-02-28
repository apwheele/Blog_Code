'''
Geocoding the hospital data
using the census geo api
Andy Wheeler
'''

import numpy as np
import pandas as pd
import censusgeocode as cg
import time
import pickle
from datetime import datetime
import os
os.chdir(r'C:\Users\andre\OneDrive\Desktop\HospDeserts')

#Downloaded from https://data.cms.gov/provider-data/dataset/6jpm-sxkc
url = r'https://data.cms.gov/provider-data/sites/default/files/resources/1ee6a6e80907bf13661aa2f099415fcd_1607015434/HH_Provider_Oct2020.csv'
hosp_data = pd.read_csv(url)
hosp_data.reset_index(inplace=True)

#anything post comma in address is going to mess up the geocoding
hosp_data['AddressClean'] = hosp_data['Address'].str.split(',').str[0]

#This function breaks up the input data frame into chunks
#For the census geocoding api
def split_geo(df, add, city, state, zipcode, chunk_size=500):
    df_new = df.copy()
    df_new.reset_index(inplace=True)
    splits = np.ceil( df.shape[0]/chunk_size)
    chunk_li = np.array_split(df_new['index'], splits)
    res_li = []
    pick_fi = []
    for i,c in enumerate(chunk_li):
        # Grab data, export to csv
        sub_data = df_new.loc[c, ['index',add,city,state,zipcode]]
        sub_data.to_csv('temp_geo.csv',header=False,index=False)
        # Geo the results and turn back into df
        print(f'Geocoding round {int(i)+1} of {int(splits)}, {datetime.now()}')
        result = cg.addressbatch('temp_geo.csv') #should try/except?
        # May want to dump the intermediate results
        #pi_str = f'pickres_{int(i)}.p'
        #pickle.dump( favorite_color, open( pi_str, "wb" ) )
        #pick_fi.append(pi_str.copy())
        names = list(result[0].keys())
        res_zl = []
        for r in result:
            res_zl.append( list(r.values()) )
        res_df = pd.DataFrame(res_zl, columns=names)
        res_li.append( res_df.copy() )
        time.sleep(10) #sleep 10 seconds to not get cutoff from request
    final_df = pd.concat(res_li)
    final_df.rename(columns={'id':'row'}, inplace=True)
    final_df.reset_index(inplace=True, drop=True)
    # Clean up csv file
    os.remove('temp_geo.csv')
    return final_df

geo_data = split_geo(hosp_data, 'AddressClean', 'City', 'State', 'ZIP')

#What is the geocoding hit rate?
print( geo_data['match'].value_counts() )
# Not too great, around 75%

# Combining the two data sources, and keeping the fields I want in the end
kg = ['address','match','lat','lon']
kd = ['CMS Certification Number (CCN)',
      'Provider Name',
      'Phone',
      'Offers Nursing Care Services',
      'Offers Physical Therapy Services',
      'Offers Occupational Therapy Services',
      'Offers Speech Pathology Services',
      'Offers Medical Social Services',
      'Offers Home Health Aide Services']

final_df = pd.concat( [hosp_data[kd], geo_data[kg]], axis=1 )
final_df.to_csv('GeocodedHosp.csv', index=False)




