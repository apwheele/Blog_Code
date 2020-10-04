'''
These are functions to go with my discrete time analysis

Andy Wheeler
'''

import pandas as pd
import numpy as np
import statsmodels.api as sm
import lifelines
from sklearn import metrics
from matplotlib import pyplot as plt

#Takes time input and bins it into smaller sets, eg days to weeks
def bin_time(orig_time,bin_val):
    return list(pd.Series(np.floor(orig_time/bin_val) + 1).astype(int))

#Explodes a dataset to make it in long format necessary for
#Discrete survival analysis using binary predictions
def explode_data(data,time,outcome,max_time,min_time=1,
                 time_name='Time',outcome_name='FinEvent',
                 cum_event=None):
    dat_cop = data.copy()
    if time_name in list(dat_cop):
        print(f'Resulting exploded time variable name {time_name} is in the original data.')
    else:
        dat_cop[time_name] = data[time].clip(min_time,max_time).apply(range)
        explode_dat = dat_cop.explode(time_name)
        explode_dat[time_name] = pd.to_numeric(explode_dat[time_name]) + 1
        explode_dat[outcome_name] = (explode_dat[time_name] >= explode_dat[time]) * explode_dat[outcome]
        if cum_event is not None:
            explode_dat[cum_event] = explode_dat[outcome_name]
            #replace after the end time with missing for outcome
            post_time = explode_dat[time_name] > explode_dat[time]
            explode_dat.loc[ post_time, outcome_name] = -1
            explode_dat[outcome_name].replace(-1,np.NaN,inplace=True)
            explode_dat.loc[ (post_time & (explode_dat[outcome]==0)), cum_event] = -1
            explode_dat[cum_event].replace(-1,np.NaN,inplace=True)
        return explode_dat

    
#Cumulative hazard based on predicted probabilities
#For instant time points
def cum_hazard(data,prob,idvar,min_p=1e-12):
    if idvar is not None:
        dat_cop = data[ [idvar,prob] ]
    else:
        dat_cop = data[ [prob] ]
    max_p = 1.0 - min_p
    dat_cop['neglogProb'] = np.log( 1 - dat_cop[prob].clip(0.0,max_p) )
    if idvar is not None:
        dat_cop['cumHazard'] = 1 - np.exp(dat_cop.groupby(idvar)['neglogProb'].transform(pd.Series.cumsum))
    else:
        dat_cop['cumHazard'] = 1 - np.exp(dat_cop['neglogProb'].cumsum())
    return dat_cop['cumHazard']
    
#This is a life table based on the exploded dataset
life_agg = {'Deaths':'sum',
            'AtRisk':'size'}

def life_table(explode_data,time_name='Time',outcome_name='FinEvent'):
    exp_nomissing = explode_data[[time_name,outcome_name]].dropna()
    group_vals = exp_nomissing.groupby(time_name,as_index=False)[outcome_name].agg(life_agg)
    #Sometimes folks do AtRisk - 0.5 (so midpoint of bin)
    group_vals['PropDying'] = group_vals['Deaths']/group_vals['AtRisk']
    group_vals['CumHazard'] = cum_hazard(data=group_vals,prob='PropDying',idvar=None)
    #Greenwoods formula
    val = group_vals['Deaths'] / ( group_vals['AtRisk']*(group_vals['AtRisk']-group_vals['Deaths']) )
    val_cum = val.cumsum()
    group_vals['SE_CumHazard'] = (1-group_vals['CumHazard']) * np.sqrt(val_cum)
    return group_vals
    
    
#Calibration data/plot
#https://andrewpwheeler.com/2020/07/04/adjusting-predicted-probabilities-for-sampling/
def cal_data(prob, true, data, bins, plot=False, 
             title=None, figsize=(6,4), save_plot=False):
    cal_dat = data[[prob,true]].copy()
    cal_dat['Count'] = 1
    cal_dat['LowTrue'] = cal_dat[true].fillna(0)
    cal_dat['HighTrue'] = cal_dat[true].fillna(1)
    cal_dat['Bin'] = pd.qcut(cal_dat[prob], bins, range(bins) ).astype(int) + 1
    agg_bins = cal_dat.groupby('Bin', as_index=False)['Count',prob,'LowTrue','HighTrue'].sum()
    agg_bins['Predicted'] = agg_bins[prob]/agg_bins['Count']
    agg_bins['ActualLow'] = agg_bins['LowTrue']/agg_bins['Count']
    agg_bins['ActualHigh'] = agg_bins['HighTrue']/agg_bins['Count']
    if plot:
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(agg_bins['Bin'], agg_bins['Predicted'], color='k',
                marker='+',label='Predicted')
        ax.fill_between(agg_bins['Bin'],agg_bins['ActualLow'],
                        agg_bins['ActualHigh'],color='k',
                        alpha=0.2, label='Actual Bounds')
        ax.set_ylabel('Probability')
        ax.legend(loc='upper left')
        if title is not None:
            plt.title(title)
        if save_plot:
            plt.savefig(save_plot, dpi=500, bbox_inches='tight')
        plt.show()
    return agg_bins
    

#This is another calibration type plot in time space
def cal_time(explode_data,instant_prob,id_var,max_time,
             time_name='Time',outcome_name='FinEvent',
             sims=99):
    #Calculate the usual Kaplan Meir
    kap_data = life_table(explode_data,time_name=time_name,outcome_name=outcome_name)
    #Estimate Simulations
    sim_li = []
    exp_copy = explode_data[[id_var,time_name,instant_prob]]
    eval_points = np.arange(1,max_time+1)
    for i in range(sims):
        sim_bin = np.random.binomial(1,explode_data[instant_prob])
        exp_copy['SimTime'] = (sim_bin * exp_copy[time_name]).replace(0,max_time+1)
        red_time = exp_copy.groupby(id_var,as_index=False)['SimTime'].min()
        ecdf_sim = sm.distributions.ECDF(red_time['SimTime'])
        ecdf_vals = pd.Series(ecdf_sim(eval_points))
        sim_li.append(ecdf_vals)
    sim_dat = pd.concat(sim_li,axis=1)
    low_sim = sim_dat.min(axis=1)
    hig_sim = sim_dat.max(axis=1)
    sim_dat[time_name] = eval_points
    sim_dat['LowSim'] = low_sim
    sim_dat['HigSim'] = hig_sim
    sim_dat = sim_dat[[time_name,'LowSim','HigSim']]
    #Merge in kaplan meir estimate
    merg_dat = pd.merge(sim_dat,kap_data[[time_name,'CumHazard']],
                        how='left',on=time_name)
    merg_dat.interpolate(method='ffill',inplace=True)
    merg_dat['SimN'] = sims
    #Return data
    return merg_dat
  
############################################################
##Some example code calculating ECDF bounds
##And then superimposing weighted ECDF based on prob estimates
#
##Calculate min/max bounds on ECDF of the observed times
#test_dat['WeekLow'] = test_dat['WeekTot']+1
#test_dat['WeekHigh'] = 1000
#out = test_dat['EVENT'] == 1
#test_dat.loc[out, 'WeekLow'] = test_dat.loc[out, 'WeekTot']
#test_dat.loc[out, 'WeekHigh'] = test_dat.loc[out, 'WeekTot']
#ecdf_low = sm.distributions.ECDF(test_dat['WeekLow'])
#ecdf_high = sm.distributions.ECDF(test_dat['WeekHigh'])
#eval_points = np.arange(1,end_time+1)
#low_cdf = ecdf_low(eval_points)
#hig_cdf = ecdf_high(eval_points)
#
##Calculate the ECDF based on instant prob weights
#test_explode['Const'] = 1
#cum_vals = test_explode.groupby('Time',as_index=False)['InstProb','CumHazard','Const'].sum()
##cum_vals['CumFail'] = cum_vals['InstProb'].cumsum()
##This seems to line up better with the simulations
#cum_vals['CumFail'] = cum_vals['CumHazard'] #or should this be CumHazard?
#cum_vals['CumProp'] = cum_vals['CumFail']/cum_vals['Const']
#
##Simulation of observed times and calc ECDF
#sim_bin = np.random.binomial(1,test_explode['InstProb'])
#test_explode['SimTime'] = (sim_bin * test_explode['Time']).replace(0,1000)
#red_time = test_explode.groupby('ID',as_index=False)['SimTime'].min()
#ecdf_sim = sm.distributions.ECDF(red_time['SimTime'])
#sim_cdf = ecdf_sim(eval_points)
#
##Make a plot of low and high
#fig, ax = plt.subplots()
#ax.step(cum_vals['Time'],cum_vals['CumProp'],
#        where='post',label='Estimated')
#ax.step(eval_points,sim_cdf,color='grey',
#        where='post',label='Sim')
#ax.fill_between(eval_points,hig_cdf,
#                low_cdf,alpha=0.2,step='post',
#                color='k',
#                label='Observed')
#ax.set_xlabel('Weeks')
#ax.set_ylabel('ECDF')
#ax.legend(loc='upper left')
##plt.savefig('PersonPlot_Instant.png', dpi=500, bbox_inches='tight')
#plt.show()  
############################################################

#Restricted cubic splines function
#See https://github.com/apwheele/Blog_Code/tree/master/Python/Smooth
#And https://andrewpwheeler.com/2020/09/20/making-smoothed-scatterplots-in-python/

#This function takes the data, an x variable
#knot locations, stub is a string
#if you pass data, it will append those variables
#to a dataframe, else returns a new dataframe
def rcs(x,knots,stub,norm=True,data=None):
	denom = knots[-1] - knots[-2]
	spline_li = []
	tot_knots = len(knots) - 2
	if norm:
		norm_val = (knots[-1] - knots[0])**2
	else:
		norm_val = 1
	for i in range(tot_knots):
		n1 = (knots[-1] - knots[i])/denom
		n2 = (knots[-2] - knots[i])/denom
		p1 = ((x - knots[i]).clip(0)**3)
		p2 = ((x - knots[-2]).clip(0)**3)*n1
		p3 = ((x - knots[-1]).clip(0)**3)*n2
		res = (p1 - p2 + p3)/norm_val
		spline_li.append(res)
	labels = [stub + str(i+1) for i in range(tot_knots)]
	if data is not None:
		for var,lab in zip(spline_li,labels):
			data[lab] = var
	else:
		res_df = pd.concat(spline_li,axis=1)
		res_df.columns = labels
		return res_df
        

#Function to scoop out non-monotonic sections
#For ROC curve
def check_min(data):
    shift = data.shift(1,fill_value=0)
    fpr_min = (data['FPR'] < shift['FPR'])
    tpr_min = (data['TPR'] < shift['TPR'])
    any_min = fpr_min | tpr_min
    return any_min.sum(), any_min        
        
#Function to estimate censored ROC curve
#https://onlinelibrary.wiley.com/doi/abs/10.1111/j.0006-341X.2000.00337.x
def censored_roc(data,pred_var,time_var,orig_var,dur_var,time_val):
    subset = data[data[time_var] == time_val]
    #KM for full sample
    km_full = lifelines.KaplanMeierFitter()
    km_full.fit(subset[dur_var], subset[orig_var])
    sf_full = list(km_full.survival_function_at_times(times=[time_val]))[0]
    #Getting reduced set of potential thresholds
    thresh = pd.unique(subset[pred_var].round(3))
    thresh.sort()
    thresh = np.flip(thresh)
    #Estimating Curves
    tpr = [0.0]
    fpr = [0.0]
    km_above = lifelines.KaplanMeierFitter()
    km_below = lifelines.KaplanMeierFitter()
    for tv in thresh[1:-1]:
        above_test = (subset[pred_var] > tv)
        #KM for sample above
        sub_above = subset[above_test]
        km_above.fit(sub_above[dur_var],sub_above[orig_var])
        sf_above = list(km_above.survival_function_at_times(times=[time_val]))[0]
        #KM for sample below
        sub_below = subset[~above_test]
        km_below.fit(sub_below[dur_var],sub_below[orig_var])
        sf_below = list(km_below.survival_function_at_times(times=[time_val]))[0]
        #Now calculating sens/spec
        prop_above = above_test.mean()
        sens = ((1 - sf_above)*prop_above)/(1 - sf_full)
        spec = (sf_below*(1 - prop_above))/(sf_full)
        tpr.append(sens)
        fpr.append(1 - spec)
    tpr.append(1.0)
    fpr.append(1.0)
    roc_dat = pd.DataFrame(zip(fpr,tpr,thresh),
                           columns=['FPR','TPR','THRESH'])
    #Now fudging out places that are non-monotonic
    roc_new = roc_dat
    roc_new['FPR'] = roc_new['FPR'].round(3)
    roc_new['TPR'] = roc_new['TPR'].round(3)
    nonN, any_min = check_min(roc_new)
    while nonN > 0:
        roc_new = roc_new[~any_min].copy()
        nonN, any_min = check_min(roc_new)   
    roc_new['Time'] = time_val
    try:
        auc_stat = metrics.auc(roc_new['FPR'], roc_new['TPR'])
    except:
        auc_stat = -1
    return roc_new, auc_stat
    
    
