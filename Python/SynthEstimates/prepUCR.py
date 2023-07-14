'''
Prepping UCR

The srs_top_cities.dta comes from Jacob Kaplans
replication files at

https://www.openicpsr.org/openicpsr/project/176021/version/V2/view
'''

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

andy_theme = {'axes.grid': True,
              'grid.linestyle': '--',
              'legend.framealpha': 1,
              'legend.facecolor': 'white',
              'legend.shadow': True,
              'legend.fontsize': 14,
              'legend.title_fontsize': 16,
              'xtick.labelsize': 14,
              'ytick.labelsize': 14,
              'axes.labelsize': 16,
              'axes.titlesize': 20,
              'figure.dpi': 100}

matplotlib.rcParams.update(andy_theme)

# load in data, this is via Kaplan's replication files
# UCR data
crimes = pd.read_stata('srs_top_cities.dta')

# Only keep agencies in Hogan top 100 sample
crimes = crimes[crimes['type'] != ''].copy()

# only keep full reporting
crimes = crimes[crimes['number_of_months_missing'] == 0].copy()

# Only keep agencies with full 20 years of data
# I am keeping this in, as many of these cities have weird data values
# Birmingham 2019, Raleigh 2019, Winston-Salem 2019
# easier just to eliminate
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

city_20 = city_20['index'][city_20.city == 20].tolist()
crimes = crimes[crimes['city'].isin(city_20)].copy()

# Eliminate progressive cities that are not Philly
#not_prog = (crimes['type'] != 'Progressive') | (crimes['city'] == 'Philadelphia')
#crimes = crimes[not_prog].copy()

# Prep final data
# Replace the Philly numbers with Hogans, 2010-2019
philly_recent = [306,
                 326,
                 331,
                 246,
                 248,
                 280,
                 277,
                 315,
                 353,
                 356]

Philly = (crimes['city'] == 'Philadelphia') & (crimes['year'] >= 2010)

crimes['hom'] = crimes[['actual_murder', 'actual_manslaughter']].sum(axis=1)
crimes.loc[Philly,'hom'] = philly_recent
crimes['hom_rate'] = (crimes['hom']/crimes['population'])*100000
crimes['Philly'] = 1*(crimes['city'] == 'Philadelphia')

keep_fields = ['city','ori','year','population',
               'hom','hom_rate','type','Philly']

crimes = crimes[keep_fields].sort_values(by=['city','year'],ignore_index=True)

int_fields = ['year','population','hom','Philly']
crimes[int_fields] = crimes[int_fields].astype(int)

# This is still a total of 71 possible donors
#crimes.to_csv('PrepUCR.csv',index=False)

#crimes['year'] = crimes['year'].astype(int)
crimes.sort_values(by=['Philly','city','year'], inplace=True, ignore_index=True)

# Check out this file in Github page
crimes.to_csv('TopCitiesHomRate.csv',index=False)

# This produces 100 seperate plots, not quite what I want!
#crimes.groupby('city').plot(x='year', y='hom_rate', kind='line')

# Homicide rates, all cities
year_lab = np.arange(2000,2020,2)
un_cities = list(pd.unique(crimes['city']))

fig, ax = plt.subplots(figsize=(8,6))

for c in un_cities:
    sd = crimes[crimes['city'] == c]
    lab = 0
    if c == 'Philadelphia':
        ax.plot(sd['year'], sd['hom_rate'], label='Philly', color='red', linewidth=2)
    elif c == un_cities[0]:
        ax.plot(sd['year'], sd['hom_rate'], label='Other City', color='grey', linewidth=1)
    else:
        ax.plot(sd['year'], sd['hom_rate'], color='grey', linewidth=1)

ax.set_axisbelow(True)
ax.set_xticks(year_lab)
ax.set_title('Homicide Rate per 100,000')
ax.legend(loc='upper right')
plt.show()


# Homicide counts, all cities

fig, ax = plt.subplots(figsize=(8,6))

for c in un_cities:
    sd = crimes[crimes['city'] == c]
    lab = 0
    if c == 'Philadelphia':
        ax.plot(sd['year'], sd['hom'], label='Philly', color='red', linewidth=2)
    elif c == un_cities[0]:
        ax.plot(sd['year'], sd['hom'], label='Other City', color='grey', linewidth=1)
    else:
        ax.plot(sd['year'], sd['hom'], color='grey', linewidth=1)

ax.set_axisbelow(True)
ax.set_xticks(year_lab)
ax.set_title('Homicide Count')
#ax.legend(loc='upper right')
ax.legend(bbox_to_anchor=(1.05,0.5))
plt.show()


# Weighted aggregate rate, Philly and prosecutor type
ct = crimes.groupby(['Philly','type','year'], as_index=False)['hom','population'].sum()
ct['hom_rate'] = (ct['hom']/ct['population'])*100000

rep_dict = {'0Traditional': 'Traditional',
            '0Middle': 'Middle',
            '0Progressive': 'Progressive',
            '1Progressive': 'Philly'}

ct['group'] = (ct['Philly'].astype(str) + ct['type']).replace(rep_dict)

# Now lets do for each a line
colors = ['#ca0020',
          '#f4a582',
          '#92c5de',
          '#0571b0']

fig, ax = plt.subplots(figsize=(8,6))

for g,c in zip(rep_dict.values(),colors):
    sd = ct[ct['group'] == g]
    ax.plot(sd['year'], sd['hom_rate'], label=g, color=c)

ax.set_axisbelow(True)
ax.set_xticks(year_lab)
ax.set_title('Homicide Rate per 100,000')
ax.legend(loc='upper right')
plt.show()

