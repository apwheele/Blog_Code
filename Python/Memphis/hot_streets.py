'''
Code to identify the top
locations for violent crimes
in Memphis, to illustrate
mismatch between "hot spots"
and where Nichols was pulled
over

Andy Wheeler, apwheele@gmail.com
https://andrewpwheeler.com/
'''

import pandas as pd
import requests
from io import StringIO

# Grab data
url = r'https://data.memphistn.gov/api/views/ybsi-jur4/rows.csv?accessType=DOWNLOAD'
crime = requests.get(url)
df = pd.read_csv(StringIO(crime.text))

# Filter out before event, filled in going back to 2006 looks like
df['offense_date'] = pd.to_datetime(df['offense_date'])
end = pd.to_datetime('2023-01-07')
df = df[df['offense_date'] < end].copy()

# Only keep violent incidents
#df['Category'].value_counts()
# Not including 'Assault', as it is quite common
viol = ['Robbery','Weapons Offense','Homicide','Kidnapping']
df = df[df['Category'].isin(viol)].copy()

# Now making dummy variables and total
df['Total'] = 1
for v in viol:
  df[v] = df['Category'] == v

# Eliminating no geo
no_geo = (df['coord1'].isna() | df['coord1'] == 0)
df = df[~no_geo].copy()

# Aggregating to streets
# '100 Block Address' is a bit messy
street = df.groupby(['coord1', 'coord2'],as_index=False)[['Total'] + viol].sum()
block_add = df[['coord1', 'coord2', '100 Block Address']].drop_duplicates(['coord1', 'coord2'])
street = street.merge(block_add,on=['coord1', 'coord2'])
street.sort_values(by=['Total','Homicide','Robbery','Weapons Offense'],ascending=False,ignore_index=True,inplace=True)
street.head(20)

# Creating Rank and percentile
street['rank'] = street['Total'].rank(method='first',ascending=False,pct=False)
street['ptile'] = street['Total'].rank(method='first',ascending=False,pct=True)

# Creating map of hot streets

# Top 5% would be street.shape[0]*0.05, over 1000 streets
# This data is for over 17 years, #1000 have less than a
# single crime per year, lets just take the top 100 areas
street_top = street.head(100).copy()
street_top.to_csv('MemphisHot.csv',index=False)

# Can see https://www.google.com/maps/d/u/0/edit?mid=1Mcnjahet_yeE4z7_L-R_xfZBc-KH1co&usp=sharing
# To visualize the hot spots and Nichols area of stop