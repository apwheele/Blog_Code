'''
ARIMA models
with error bars
'''

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

# via https://www.disastercenter.com/crime/uscrime.htm
# uploaded this script to
ucr = pd.read_csv('UCR_1960_2019.csv')
ucr['VRate'] = (ucr['Violent']/ucr['Population'])*100000
ucr['PRate'] = (ucr['Property']/ucr['Population'])*100000
ucr = ucr[['Year','VRate','PRate']]

# adding in more recent years
# via https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi
# I should use original from pop + counts, I don't
# know where to find those though
y = [2020,2021,2022]
v = [398.5,387,380.7]
p = [1958.2,1832.3,1954.4]
ucr_new = pd.DataFrame(zip(y,v,p),columns = list(ucr))
ucr = pd.concat([ucr,ucr_new],axis=0)
#ucr.reset_index(drop=True,inplace=True)
#ucr.set_index('Year',inplace=True)
ucr.index = pd.period_range(start='1960',end='2022',freq='A')


# train/test split
train = ucr.loc[ucr['Year'] <= 2015,'VRate']

# Not sure if Richard's model had a trend term, here no trend
violent = ARIMA(train,order=(1,1,2),trend='n').fit()
violent.summary()

# To make it apples to apples, only appending through 2020
av = (ucr['Year'] > 2015) & (ucr['Year'] <= 2020)
violent = violent.append(ucr.loc[av,'VRate'], refit=False)

# Now can show insample predictions and forecasts
forecast = violent.get_prediction('2016','2025').summary_frame(alpha=0.05)

# Richards estimates
#     2016-2020 one step forecasts      2021-2025 multi-forecasts
forecast['Rosenfeld'] = [399.0,406.8,388.0,377.0,394.9] + [404.1,409.3,410.2,411.0,412.4]
forecast['Observed'] = ucr['VRate']

# Given updated data until end of series, lets do 23/24/25
violent = violent.append(ucr.loc[ucr['Year'] > 2020,'VRate'], refit=False)
updated_forecast = violent.get_forecast(3).summary_frame(alpha=0.05)


# This is a personal function to add logo
# to replicate just drop it
import sys
sys.path.append('G:\CrimScraper')
from src.cdcplot import add_logo

import matplotlib
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

def combo_legend(ax):
    handler, labeler = ax.get_legend_handles_labels()
    hd = []
    labli = list(set(labeler))
    for lab in labli:
        comb = [h for h,l in zip(handler,labeler) if l == lab]
        hd.append(tuple(comb))
    return hd, labli

# now lets make a plot
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(ucr['Year'],ucr['VRate'],color='k',marker='o',markeredgecolor='white',label='Observed',zorder=1)
ax.plot(forecast.index.year,forecast['Rosenfeld'],c='red',marker='s',label='Rosenfeld',markersize=5,markeredgecolor='k')
ax.fill_between(updated_forecast.index.year,updated_forecast['mean_ci_lower'],updated_forecast['mean_ci_upper'],color='blue',alpha=0.5, label='Wheeler')
ax.plot(updated_forecast.index.year,updated_forecast['mean'],c='blue',marker="d",label='Wheeler',markersize=6,alpha=0.5)
ax.set_title('UCR Violent Crime Rate per 100,000',loc='left')
hd, lab = combo_legend(ax)
hd = [hd[1],hd[0],hd[2]]
lab = [lab[1],lab[0],lab[2]]
ax.legend(hd, lab, loc='upper left')
add_logo(ax, loc=[0.78,0.78])
ax.set_axisbelow(True)
#plt.show()
plt.savefig('ForecastViolent.png',dpi=500,bbox_inches='tight')
