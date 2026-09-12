'''
Prepares the monthly theft data used in the
"faking synthetic control" blog post.

Source data is the Real-Time Crime Index (RTCI)
https://github.com/AH-Datalytics/rtci
I use the local snapshot that I already had downloaded for
https://github.com/apwheele/CrimeDecomp

Writes out LATheft.csv so the rest of the analysis is
self contained inside of this folder.

Andy Wheeler
'''

import os
import pandas as pd

# Location of the RTCI snapshot, change this if you have
# the data somewhere else
RTCI = r'G:\CrimeDecomp\src\data\raw'
TRENDS = os.path.join(RTCI,'rtci_crime_trends.csv')
META = os.path.join(RTCI,'agency_metadata.csv')
PREP = os.path.join(RTCI,'rtci_pre_processed.csv')

# George Gascon was sworn in as LA County DA on 12/07/2020
# and left office 12/02/2024, so the data stops at Nov 2024
BEG = pd.Timestamp('2017-01-01')
END = pd.Timestamp('2024-11-01')
NPER = 95  # number of months between BEG and END inclusive

# Other big city DAs who ran on/were labeled as progressive over
# the same window, so they do not belong in the donor pool
DROP_DA = ['San Francisco, CA',   # Chesa Boudin, 1/2020 - 7/2022
           'Chicago, IL',         # Kim Foxx, 12/2016 - 12/2024
           'Philadelphia, PA',    # Larry Krasner, 1/2018 -
           'New York City, NY']   # Bragg (Manhattan) 1/2022 -, and
                                  # Gonzalez (Brooklyn) 2017 -, the
                                  # RTCI series is all of NYPD

# Gascon prosecuted every case in LA County, so the Sheriff's
# Department (which polices the unincorporated county) is treated
# as well and cannot be a comparison unit
DROP_SPILL = ['Los Angeles Cnty, CA']

# NOTE -- Boston (Rachael Rollins), Baltimore (Marilyn Mosby),
# St Louis (Kim Gardner) and Austin (Jose Garza) all have a
# reasonable claim to the same label, and you could argue for
# dropping them as well. I leave them in the donor pool here.
# Same argument applies to the other ~30 LA County agencies in
# the data (Long Beach, Pasadena, Pomona, Torrance, ...), they
# are also inside of Gascon's jurisdiction. If Gascon really did
# cause thefts to change, leaving those in the donor pool biases
# the estimate towards a null result.


def agency_labels():
    '''Unique city label per ORI, plus population'''
    meta = pd.read_csv(META)
    ptype = pd.read_csv(PREP,usecols=['ori.x','Agency_Type'],low_memory=False)
    ptype = ptype.dropna(subset=['ori.x']).drop_duplicates(subset=['ori.x'])
    meta = meta.merge(ptype,left_on='city_id',right_on='ori.x',how='left')
    meta = meta.dropna(subset=['population','Agency_Type'])
    # County sheriffs share a name with the city PD, e.g. Baltimore
    cnty = meta['Agency_Type'].eq('County').map({True: ' Cnty', False: ''})
    meta['City'] = meta['city_name'] + cnty + ', ' + meta['state']
    return meta[['city_id','City','population']]


def prep_data():
    uc = ['id','size','year','month','sample','theft_total']
    cr = pd.read_csv(TRENDS,usecols=uc)
    # size 'all' is the full agency, sample 1 means it reports
    # consistently enough to be in the RTCI index
    cr = cr[(cr['size'] == 'all') & (cr['sample'] == 1)].copy()
    cr['Date'] = pd.to_datetime(dict(year=cr['year'],month=cr['month'],day=1))
    cr = cr[(cr['Date'] >= BEG) & (cr['Date'] <= END)]
    cr = cr.merge(agency_labels(),left_on='id',right_on='city_id')
    # only keep agencies with a complete monthly series
    comp = cr.groupby('City')['theft_total'].transform('count') == NPER
    cr = cr[comp].copy()
    cr['Rate'] = (cr['theft_total']/cr['population'])*100000
    cr = cr[['City','Date','theft_total','population','Rate']]
    cr.columns = ['City','Date','Theft','Pop','Rate']
    dl = DROP_DA + DROP_SPILL
    cr = cr[~cr['City'].isin(dl)]
    cr = cr.sort_values(by=['City','Date']).reset_index(drop=True)
    return cr


if __name__ == "__main__":
    theft = prep_data()
    print(f'Agencies: {theft["City"].nunique()}')
    print(f'Months:   {theft["Date"].nunique()}')
    print(theft[theft['City'] == 'Los Angeles, CA'].head())
    theft.to_csv('LATheft.csv',index=False)
