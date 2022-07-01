# Criminal Lifetime Value

This is an application of customer lifetime value estimates to chronic offender scores. See for example:

 - <http://brucehardie.com/papers/018/fader_et_al_mksc_05.pdf>
 - <http://brucehardie.com/notes/>
 - <https://lifetimes.readthedocs.io/en/latest/Quickstart.html>

The data in this repo is taken from [ICPSR 07729](https://www.icpsr.umich.edu/web/NACJD/studies/7729/versions/V1), the Wolfgang *Delinquency in a Birth Cohort in Philly* data. Specifically, I downloaded the `.por` SPSS files from ICPSR, converted the study II dataset (the individual crimes) to a CSV file, and then edited the file as so.

    ################
    # prep data python script
    import pandas as pd
    
    df = pd.read_csv('PhilCohort_CrimeData.csv')
    df['v9'] = df['v9'] + 1900
    ymd = df[['v9','v10','v11']].copy()
    ymd.columns = ['year','month','day']
    # One day is missing, setting to mid of month
    ymd['day'] = ymd['day'].replace({98:15})
    
    # A few specific end of month errors
    ymd.iloc[5305,2] = 28
    ymd.iloc[5361,2] = 30
    ymd.iloc[8351,2] = 30
    
    res_date = pd.to_datetime(ymd, errors='coerce')
    
    df['offdate'] = res_date
    
    trans = df[['v4','v12','offdate']].copy()
    trans.columns = ['ID','SeriousScore','Date']
    trans.to_csv('PhilData.csv',index=False)
    ############

If using this for more serious research, please get the data directly from ICPSR instead of relying on my edited version.