'''
This downloads the DPD incident
file and creates a sqlite database

https://www.dallasopendata.com/Public-Safety/Police-Incidents/qv6i-rri7
Andy Wheeler
'''

import pandas as pd
import sqlite3
import re

# Dallas PD crime incidents on Socrata
inc_url = r'https://www.dallasopendata.com/api/views/qv6i-rri7/rows.csv?accessType=DOWNLOAD'
print(f'Grabbing Dallas PD incidents from {inc_url}')
try:
    incidents = pd.read_csv(inc_url,low_memory=False)
    print(f'Successful grabbing the newest online incidents, total n {incidents.shape[0]}')
except:
    print('''
             Grabbing new incidents from online unsuccessful. 
             Check out 
             https://www.dallasopendata.com/Public-Safety/Police-Incidents/qv6i-rri7 
             to see if csv download url changed
             exiting the script
          ''')
    sys.exit()
# Not sure if this will always stay good

# Replacing spaces/no characters with _
rename_dict = {}
for v in list(incidents):
    rename_dict[v] = re.sub('[^0-9a-zA-Z]+', '_', v)
incidents.rename(columns=rename_dict,inplace=True)

# Converting a few of the date columns
dvars = ['Date1_of_Occurrence','Date2_of_Occurrence_','Date_of_Report']
for v in dvars:
    incidents[v] = pd.to_datetime(incidents[v])

last_date = incidents['Date_of_Report'].max()
print(f'The last Report Date in the database is {last_date}')

# Connecting to sqlite db
try:
    con = sqlite3.connect("DPD.sqlite")
    incidents.to_sql('incidents',index=False,if_exists='replace',con=con)
    print('Success creating _incidents_ table on DPD.sqlite')
except:
    print('Unable to connect to sqlite or save the incidents table')