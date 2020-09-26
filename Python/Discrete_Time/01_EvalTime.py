'''
Discrete time survival models
'''

#############################################
#FRONT END
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn import metrics

import os
import sys
from matplotlib import pyplot as plt

my_dir = r'C:\Users\andre\OneDrive\Desktop\DiscreteTime_MachineLearning'
os.chdir(my_dir)
sys.path.append(my_dir)
import discrete_time
#############################################

#############################################
#CHART TEMPLATE
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
#############################################

#############################################
#Load in the test data and the xgboost model
test_dat = pd.read_csv('test_data.csv')

model = sm.load('discrete_time.pickle')

#Expand out how many iterations I want to look at
end_time = 52*2
test_explode = discrete_time.explode_data(data=test_dat,time='WeekTot',
                                          outcome='EVENT',max_time=end_time,
                                          min_time=end_time,
                                          cum_event='CumEvent')

#Recreating the spline terms
knot_locs = [4,10,20,40,60,80]
discrete_time.rcs(test_explode['Time'],knot_locs,stub='ST_',data=test_explode)
#############################################

#############################################
#Generate predictions

#Takes like 3 minutes on my machine
y_pred = model.predict(test_explode)

test_explode['InstProb'] = y_pred

#Calc cumulative hazard for each individual
test_explode['CumHazard'] = discrete_time.cum_hazard(test_explode,'InstProb','ID')

#############################################

#############################################
#Give a single person example plot

#9, 39, 67
person = test_explode[test_explode['ID'] == 39]
print(person)

#Plot Cum predicted curve
#Add lines for observed
fig, ax = plt.subplots()
ax.plot(person['Time'],person['CumHazard'],
        alpha=0.6,color='k',drawstyle='steps-post')
if person.iloc[0,1] == 1.0 and person.iloc[0,2] < end_time:
    ax.axvline(person.iloc[0,2], linestyle='solid', alpha=0.6, 
               color='red',linewidth=2, zorder=1)
ax.set_xlabel('Weeks')
ax.set_ylabel('Cum. Prob. of Recid.')
plt.title(f'Person {person.iloc[0,0]:.0f}')
plt.savefig('PersonPlot.png', dpi=500, bbox_inches='tight')
plt.show()

#We could also do the instant hazard
fig, ax = plt.subplots()
ax.plot(person['Time'],person['InstProb'],
        alpha=0.6,color='k')
ax.set_xlabel('Weeks')
ax.set_ylabel('Instant Prob. of Recid.')
plt.title(f'Person {person.iloc[0,0]:.0f}')
plt.savefig('PersonPlot_Instant.png', dpi=500, bbox_inches='tight')
plt.show()
#############################################

#############################################
#Calibration Metrics

#Can do it for the full sample
cal_full = discrete_time.cal_data(prob='CumHazard', true='CumEvent',
                                  data=test_explode, 
                                  bins=50, plot=True, 
                                  title='Calibration Full Sample',
                                  save_plot='CalibrationFull.png')    

#Or do it for a particular end slice
cal_year = discrete_time.cal_data(prob='CumHazard', true='CumEvent', 
                                  data=test_explode[test_explode['Time'] == 52], 
                                  bins=20, plot=True, 
                                  title='Calibration At End of Year 1',
                                  save_plot='Calibration_52Weeks.png')

cal_month = discrete_time.cal_data(prob='CumHazard', true='CumEvent', 
                                  data=test_explode[test_explode['Time'] == 4], 
                                  bins=20, plot=True, 
                                  title='Calibration At Month 1',
                                  save_plot='Calibration_4Weeks.png')
#############################################

#############################################
#Calibration Metrics #2, time to event

cal_km = discrete_time.cal_time(explode_data=test_explode,
                                instant_prob='InstProb',
                                id_var='ID',
                                max_time=end_time)

#Make a plot of low and high
fig, ax = plt.subplots()
ax.step(cal_km['Time'],cal_km['CumHazard'],
        where='post',label='KM Estimate',
        color='k')
ax.fill_between(cal_km['Time'],cal_km['LowSim'],
                cal_km['HigSim'],alpha=0.2,step='post',
                color='k',
                label='Simulated Times')
ax.set_xlabel('Weeks')
ax.set_ylabel('Prop. Recid.')
ax.legend(loc='lower right')
plt.savefig('Calibration_KM.png', dpi=500, bbox_inches='tight')
plt.show()

#Works just fine to take slices of data
fem = test_explode['MALE']==0
cal_fem = discrete_time.cal_time(explode_data=test_explode[fem],
                                instant_prob='InstProb',
                                id_var='ID',
                                max_time=end_time)
print(cal_fem)

#How many females? 332
print( (test_dat['MALE'] == 0).sum() )
#############################################


#############################################
#Discrimination Metrics

#AUC for each cumulative slice

check_weeks = [4,8,12,52,52*2]

auc_stats = []
for w in check_weeks:
    select = (test_explode['Time'] == w) & pd.notna(test_explode['CumEvent'])
    sub_dat = test_explode[select]
    fpr, tpr, thresholds = metrics.roc_curve(sub_dat['CumEvent'], sub_dat['CumHazard'])
    auc_stat = metrics.auc(fpr, tpr)
    auc_stats.append( auc_stat )
    
auc_stats = pd.DataFrame(zip(check_weeks,auc_stats),
                         columns=['Week','AUC'])
print(auc_stats)   
   
#############################################
    