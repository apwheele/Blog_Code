'''
Data come from ICPSR 07729

Wolfgang Philadelphia Cohort
'''

import lifetimes as lt
import pandas as pd

# Just the columns from dataset II
# ID, SeriousScore, Date
df = pd.read_csv('PhilData.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Creating the cumulative data
# Having holdout for one year in future
sd = lt.utils.calibration_and_holdout_data(df,'ID','Date',
              calibration_period_end='12-31-1961',
              observation_period_end='12-31-1962',
              freq='M',
              monetary_value_col='SeriousScore')

# Only keeping people with 2+ events in prior period
sd = sd[sd['frequency_cal'] > 0].copy()
sd.head()

# fit BG model
bgf = lt.BetaGeoFitter(penalizer_coef=0)
bgf.fit(sd['frequency_cal'],sd['recency_cal'],sd['T_cal'])

# look at fit of BG model
t = 12
sd['pred_events'] = bgf.conditional_expected_number_of_purchases_up_to_time(t, sd['frequency_cal'], sd['recency_cal'],sd['T_cal'])
sd.groupby('frequency_cal',as_index=False)[['frequency_holdout','pred_events']].sum() # reasonable

# fit gamma-gamma model
ggf = lt.GammaGammaFitter(penalizer_coef=0)
ggf.fit(sd['frequency_cal'],sd['monetary_value_cal'])

# See conditional seriousness
sd['pred_ser'] = ggf.conditional_expected_average_profit(
                              sd['frequency_cal'],
                              sd['monetary_value_cal'])

sd['pv'] = sd['pred_ser']*sd['pred_events']
sd['cal_tot_val'] = sd['monetary_value_holdout']*sd['frequency_holdout']
# Not great correlation, around 0.2
vc = ['frequency_holdout','monetary_value_holdout','cal_tot_val','pred_events','pv']
sd[vc].corr()

# Lets look at this method via just ranking prior
# seriousness or frequency
sd['rank_freq'] = sd['frequency_cal'].rank(method='first',ascending=True)
sd['rank_seri'] = (sd['monetary_value_cal']*sd['frequency_cal']).rank(method='first',ascending=True)
vc += ['rank_freq','rank_seri']
sd[vc].corr()[vc[-3:]]

# Look at capture rates by ranking
topn = 50
res_summ = []
for v in vc[-3:]:
    rank = sd[v].rank(method='first',ascending=False)
    locv = sd[rank <= topn].copy()
    tot_crimes = locv['frequency_holdout'].sum()
    tot_ser = locv['cal_tot_val'].sum()
    res_summ.append( [v,tot_crimes,tot_ser,topn] )

res_df = pd.DataFrame(res_summ,columns=['Var','TotCrimes','TotSer','TotN'])
res_df

# Cumulative stats over sample reasonable
# variance much too small
sd[['cal_tot_val','pv']].describe()
