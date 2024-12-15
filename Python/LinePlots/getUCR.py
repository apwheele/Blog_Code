'''
Getting national level month data
from FBI CDE API
'''

import pandas as pd
import requests
import time
import os
import datetime

today = pd.to_datetime('now')
natCSV = 'UCR_Crime.csv'
cityCSV = 'CityStats.csv'
crime_types = ('violent-crime',
               'aggravated-assault',
               'violent-crime',
               'robbery',
               'arson',
               'homicide',
               'burglary',
               'motor-vehicle-theft',
               'larceny',
               'rape',
               'property-crime')


def parse_crimes(di,crime):
    counts = pd.DataFrame(di['offenses']['actuals'])
    counts.columns = [crime,crime+'clearances']
    rates = pd.DataFrame(di['offenses']['rates'])
    rates.columns = [crime+'rate',crime+'clearancerate']
    pop = pd.DataFrame(di['populations']['population'])
    pop.columns = ['population']
    part = pd.DataFrame(di['populations']['participated_population'])
    part.columns = ['participated_population']
    return pd.concat([counts,rates,pop,part],axis=1)


def get_fbi():
    yr = today.year
    mo = today.month
    fin_dat = []
    for c in crime_types:
        url = f'https://cde.ucr.cjis.gov/LATEST/summarized/national/{c}?from=01-1985&to={mo}-{yr}&type=counts'
        #print(url)
        res = requests.get(url)
        jd = res.json()
        fin_dat.append(parse_crimes(jd,c))
        time.sleep(1)
        # Get rid of duplicate columns, drop NAs
    res = pd.concat(fin_dat,axis=1)
    res = res.iloc[:,~res.columns.duplicated()].reset_index(names='Mo-Yr')
    res['Date'] = pd.to_datetime(res['Mo-Yr'],format="%m-%Y")
    res.sort_values(by='Date',inplace=True,ignore_index=True)
    res.dropna(how='any',inplace=True)
    return res


def cache_fbi(natCSV=natCSV):
    if os.path.exists(natCSV):
        # if old, redo
        ct = os.path.getctime(natCSV)
        ts = pd.to_datetime(datetime.datetime.fromtimestamp(ct))
        dif = (today - ts).days
        if dif > 30:
            fbi = get_fbi()
            fbi.to_csv(natCSV,index=False)
        else:
            fbi = pd.read_csv(natCSV,low_memory=False)
    else:
        fbi = get_fbi()
        fbi.to_csv(natCSV,index=False)
    return fbi


def cache_citystats(cityCSV=cityCSV):
    city_url = ('https://raw.githubusercontent.com/AH-Datalytics/'
                'rtci/refs/heads/development/data/final_sample.csv')
    if os.path.exists(cityCSV):
        # if old, redo
        ct = os.path.getctime(cityCSV)
        ts = pd.to_datetime(datetime.datetime.fromtimestamp(ct))
        dif = (today - ts).days
        if dif > 30:
            city = pd.read_csv(city_url,low_memory=False)
            city.to_csv(cityCSV,index=False)
        else:
            city = pd.read_csv(cityCSV,low_memory=False)
    else:
        city = pd.read_csv(city_url,low_memory=False)
        city.to_csv(cityCSV,index=False)
    return city


def prep_city(cityCSV=cityCSV):
    city = cache_citystats(cityCSV)
    # Reshaping city long to wide
    city['Mo-Yr'] = city['Month'].astype(str).str.zfill(2) + "-" + city['Year'].astype(str)
    city['AgID'] = city['Agency Name'] + city['State']
    # Dropping aggregate samples
    agg_names = ['100k-250kAll Agencies in Grouping', '1mn+All Agencies in Grouping',
                 '250k-1mnAll Agencies in Grouping', '<100kAll Agencies in Grouping']
    city = city[~city['AgID'].isin(agg_names)].reset_index(drop=True)
    city = city[~(city['AgID'].str[:5] == 'State')].reset_index(drop=True)
    return city