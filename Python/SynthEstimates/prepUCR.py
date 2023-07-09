'''
Prepping UCR

The srs_top_cities.dta comes from Jacob Kaplans
replication files at

https://www.openicpsr.org/openicpsr/project/176021/version/V2/view
'''

import pandas as pd

# load in data
crimes = pd.read_stata('srs_top_cities.dta')

# Only keep agencies in Hogan top 100 sample
crimes = crimes[crimes['type'] != ''].copy()

# only keep full reporting
crimes = crimes[crimes['number_of_months_missing'] == 0].copy()

# Only keep agencies with full 20 years of data
city_20 = crimes['city'].value_counts().reset_index().sort_values('city')
city_20 = city_20['index'][city_20.city == 20].tolist()

# This eliminates (NC cities only NIBRS recent maybe?)
# 99                      Louisville    16
# 98                         Raleigh    16
# 96                      Birmingham    18
# 95                  Chesapeake, VA    18
# 94                        Honolulu    18
# 93                   Winston-Salem    18
# 97                 North Las Vegas    18
# 86          Oakland/Alameda County    19
# 88      Greensboro/Guilford County    19
# 87  Lincoln, Neb./Lancaster County    19
# 90                          Newark    19
# 91       Portland/Multnomah County    19
# 92                     New Orleans    19
# 89                          Durham    19

crimes = crimes[crimes['city'].isin(city_20)].copy()

# Eliminate progressive cities that are not Philly
not_prog = (crimes['type'] != 'Progressive') | (crimes['city'] == 'Philadelphia')
crimes = crimes[not_prog].copy()

# Prep final data
crimes['hom'] = crimes[['actual_murder', 'actual_manslaughter']].sum(axis=1)
crimes['hom_rate'] = (crimes['hom']/crimes['population'])*100000
crimes['Philly'] = 1*(crimes['city'] == 'Philadelphia')

keep_fields = ['city','ori','year','population',
               'hom','hom_rate','type','Philly']

crimes = crimes[keep_fields].sort_values(by=['city','year'],ignore_index=True)

int_fields = ['year','population','hom','Philly']
crimes[int_fields] = crimes[int_fields].astype(int)

# This is still a total of 71 possible donors
crimes.to_csv('PrepUCR.csv',index=False)