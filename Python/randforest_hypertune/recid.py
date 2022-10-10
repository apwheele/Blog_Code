'''
These functions
prep the NIJ recid
data

Andy Wheeler
'''

import pandas as pd

def fe(data='https://data.ojp.usdoj.gov/api/views/ynf5-u8nk/rows.csv?accessType=DOWNLOAD'):
    full_data = pd.read_csv(data,index_col='ID')
    # Numeric Impute
    num_imp = ['Gang_Affiliated','Supervision_Risk_Score_First',
               'Prior_Arrest_Episodes_DVCharges','Prior_Arrest_Episodes_GunCharges',
               'Prior_Conviction_Episodes_Viol','Prior_Conviction_Episodes_PPViolationCharges',
               'Residence_PUMA']
    # Ordinal Encode (just keep puma as is)
    ord_enc = {}
    ord_enc['Gender'] = {'M':1, 'F':0}
    ord_enc['Race'] = {'WHITE':0, 'BLACK':1}
    ord_enc['Age_at_Release'] = {'18-22':6,'23-27':5,'28-32':4,
                      '33-37':3,'38-42':2,'43-47':1,
                      '48 or older':0}
    ord_enc['Supervision_Level_First'] = {'Standard':0,'High':1,
                             'Specialized':2,'NA':-1}
    ord_enc['Education_Level'] = {'Less than HS diploma':0,
                                  'High School Diploma':1,
                                  'At least some college':2,
                                  'NA':-1}
    ord_enc['Prison_Offense'] = {'NA':-1,'Drug':0,'Other':1,
                                 'Property':2,'Violent/Non-Sex':3,
                                 'Violent/Sex':4}
    ord_enc['Prison_Years'] = {'Less than 1 year':0,'1-2 years':1,
                               'Greater than 2 to 3 years':2,'More than 3 years':3}
    # _more clip 
    more_clip = ['Dependents','Prior_Arrest_Episodes_Felony','Prior_Arrest_Episodes_Misd',
                 'Prior_Arrest_Episodes_Violent','Prior_Arrest_Episodes_Property',
                 'Prior_Arrest_Episodes_Drug',
                 'Prior_Arrest_Episodes_PPViolationCharges',
                 'Prior_Conviction_Episodes_Felony','Prior_Conviction_Episodes_Misd',
                 'Prior_Conviction_Episodes_Prop','Prior_Conviction_Episodes_Drug']
    # Function to prep data as I want, label encode
    # And missing imputation
    def prep_data(data,ext_vars=['Recidivism_Arrest_Year1','Training_Sample']):
        cop_dat = data.copy()
        # Numeric impute
        for n in num_imp:
            cop_dat[n] = data[n].fillna(-1).astype(int)
        # Ordinal Recodes
        for o in ord_enc.keys():
            cop_dat[o] = data[o].fillna('NA').replace(ord_enc[o]).astype(int)
        # _more clip
        for m in more_clip:
            cop_dat[m] = data[m].str.split(' ',n=1,expand=True)[0].astype(int)
        # Only keeping variables of interest
        kv = ext_vars + num_imp + list(ord_enc.keys()) + more_clip
        return cop_dat[kv].astype(int)
    pdata = prep_data(full_data)
    train = pdata[pdata['Training_Sample'] == 1].copy()
    test = pdata[pdata['Training_Sample'] == 0].copy()
    return train, test

# Defined outcome Y1, and other covariates
y1 = 'Recidivism_Arrest_Year1'

xvars = ['Gang_Affiliated', 'Supervision_Risk_Score_First', 'Prior_Arrest_Episodes_DVCharges',
         'Prior_Arrest_Episodes_GunCharges','Prior_Conviction_Episodes_Viol',
         'Prior_Conviction_Episodes_PPViolationCharges', 'Residence_PUMA', 'Gender', 'Race',
         'Age_at_Release', 'Supervision_Level_First', 'Education_Level', 'Prison_Offense',
         'Prison_Years', 'Dependents', 'Prior_Arrest_Episodes_Felony', 'Prior_Arrest_Episodes_Misd',
         'Prior_Arrest_Episodes_Violent', 'Prior_Arrest_Episodes_Property', 'Prior_Arrest_Episodes_Drug', 
         'Prior_Arrest_Episodes_PPViolationCharges', 'Prior_Conviction_Episodes_Felony', 
         'Prior_Conviction_Episodes_Misd', 'Prior_Conviction_Episodes_Prop', 'Prior_Conviction_Episodes_Drug']

