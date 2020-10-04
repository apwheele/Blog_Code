'''
Discrete time survival models
'''

#############################################
#FRONT END

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

import os
import sys
from matplotlib import pyplot as plt

np.random.seed(10)

my_dir = r'D:\Dropbox\Dropbox\PublicCode_Git\Blog_Code\Python\Discrete_Time'
os.chdir(my_dir)
sys.path.append(my_dir)
import discrete_time

#Data is from https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0141328
orig_dat = pd.read_csv('journal.pone.0141328.s001.CSV')
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
#PREPPING DATASET #1

#These are the independent variables for modelling minus time variable
indep_vars = ['OVERCROWDING','AGEFIRST','MALE','OFFSCAT2_1',	
              'OFFSCAT2_2','OFFSCAT2_4','OFFSCAT2_5','CONC_DIS_STD']

#Figure out event number, only model #1 for now
orig_dat['Const'] = 1
orig_dat['EventN'] = orig_dat.groupby('ID')['Const'].transform(pd.Series.cumsum)
first_event = orig_dat[orig_dat['EventN'] == 1]
first_event.reset_index(drop=True, inplace=True)

#Break data down into weeks
bl = 7 #turn days into weeks
first_event['WeekTot'] = discrete_time.bin_time(orig_time=first_event['DAYFREE'],bin_val=bl)

#Only keeping the variables I want
first_event = first_event[ ['ID','EVENT','WeekTot'] + indep_vars ] 
#############################################

#############################################
#TRAIN/TEST SPLIT AND EXPLODING DATA 

#Identifying a set of train and test cases
print(first_event.shape)
test_n = 3000
rank_vals = pd.Series(np.random.uniform(size=first_event.shape[0])).rank()
test_flag = 1*(rank_vals <= test_n)
first_event[test_flag == 1].to_csv('test_data.csv',index=False)

#Now exploding to a long dataset
print( first_event['WeekTot'].sum() ) 
#This is how many total observations if exploded entire dataset
#And no trimming at the end
#Just under 1.2 million for the whole dataset
train_surv = first_event[test_flag == 0]
print( train_surv['WeekTot'].sum() ) #Maximum expanded dataset
end_time = 52*2  #About 2 years out


train_data = discrete_time.explode_data(data=train_surv,time='WeekTot',
                                        outcome='EVENT',max_time=end_time)
print(train_data.shape)

#When you clip it
print( train_surv['WeekTot'].clip(1,end_time).sum() )
#############################################

#############################################
#SURVIVAL PLOTS

#Looking at the survival table and making a nice plot
life_table = discrete_time.life_table(train_data)

#Calculating lower/upper CI's based on standard errors
life_table['Low95CI'] = (life_table['CumHazard'] -1.96*life_table['SE_CumHazard']).clip(0,1)
life_table['Hig95CI'] = (life_table['CumHazard'] +1.96*life_table['SE_CumHazard']).clip(0,1)

#Now making a plot
fig, ax = plt.subplots()
ax.plot(life_table['Time'],life_table['CumHazard'],
        alpha=0.6,color='k',drawstyle='steps-post')
ax.fill_between(life_table['Time'],life_table['Low95CI'],life_table['Hig95CI'],
                alpha=0.2,color='grey',step='post')
plt.yticks(np.arange(0,0.5,0.1))
ax.set_xlabel('Weeks')
ax.set_ylabel('Cumulative Prob. of Recid.')
plt.annotate('95% Confidence Interval', (0,0), (0, -40), xycoords='axes fraction', 
             textcoords='offset points', va='top')
plt.savefig('DeathPlot.png', dpi=500, bbox_inches='tight')
plt.show()

#Lets do a plot of the instant hazard up
fig, ax = plt.subplots()
ax.plot(life_table['Time'],life_table['PropDying'],
        alpha=0.6,color='k',
        marker='o',markeredgecolor='white')
ax.set_xlabel('Weeks')
ax.set_ylabel('Instant Prob. of Recid.')
#plt.xlim((0,30)) #Can zoom into smaller period via this
plt.savefig('InstantRecid.png', dpi=500, bbox_inches='tight')
plt.show()
#############################################

#############################################
#ESTIMATING A DISCRETE TIME MACHINE LEARNING MODEL

#Estimating Logistic Regression model with splines and interactions

#Adding in restricted cubic splines to data
knot_locs = [4,10,20,40,60,80]
discrete_time.rcs(train_data['Time'],knot_locs,stub='ST_',data=train_data)

#Now making a model formula for all first order interactions between spline terms
#And the other independent variables
form = 'FinEvent ~ (' + ' + '.join(indep_vars) + ')*(Time + ST_1 + ST_2 + ST_3 + ST_4)'
print(form)

#Now estimating a logit model
model = smf.glm(formula=form,
                data=train_data,
                family=sm.families.Binomial())

#To see how long something takes just print out the time
#Pre/Post
from datetime import datetime
print( datetime.now().strftime("%m/%d/%Y %H:%M:%S") )
#took only 30 seconds!
model = model.fit()
print( datetime.now().strftime("%m/%d/%Y %H:%M:%S") )

print( model.summary() )

#Now save the model output
model.save("discrete_time.pickle", remove_data=True)
#############################################