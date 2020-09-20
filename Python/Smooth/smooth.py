
'''
Restricted Cubic Splines
For Pandas/Python

See https://apwheele.github.io/MathPosts/Splines.html
for class notes on how restricted cubic splines
are calculated

Andy Wheeler
'''

import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import patsy
from scipy.stats import beta

##########################################
#Aggregate functions to take in bins and return
#The mean/stddev and make a spike plot

#Default size of matplotlib markers for scatterplots
def_size = matplotlib.rcParams['lines.markersize']**2

lin_agg = {'mean':'mean',
           'std':'std',
           'N':'size'}
           
def mean_spike(data,x,y,mult=2,plot=True,
               marker_alpha=0,marker_size=def_size,
               ret_data=False):
    agg_res = data.groupby(x,as_index=False)[y].agg(lin_agg)
    #Get rid of 1 or fewer areas
    agg_res = agg_res[agg_res['N'] > 1]
    #Now making the plot
    if plot:
        fig, ax = plt.subplots()
        ax.errorbar(agg_res[x], agg_res['mean'], agg_res['std']*mult,
                    fmt='o', markeredgecolor='white', mfc='k',
                    ecolor='k', elinewidth=1, zorder=2)
        if marker_alpha > 0:
            ax.scatter(data[x], data[y], 
                       c='grey', edgecolor='k', 
                       s=marker_size, alpha=marker_alpha, 
                       zorder=1)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        plt.show()
    if ret_data:
        return agg_res
           
prop_agg = {'sum':'sum',
            'N':'size'}

def prop_spike(data,x,y,ci=0.99,plot=True,ret_data=False):
    agg_res = data.groupby(x,as_index=False)[y].agg(prop_agg)
    #Get rid of 1 or fewer areas
    agg_res = agg_res[agg_res['N'] > 1]
    #Calculating lower and upper binomial confidence interval
    agg_res['mean'] = agg_res['sum']/agg_res['N']
    alpha = (1 - ci)/2
    agg_res['lowCI'] = beta.ppf(alpha,agg_res['sum'],agg_res['N']-agg_res['sum']+1)
    agg_res['lowCI'] = agg_res['lowCI'].fillna(0.0)
    agg_res['low'] = agg_res['mean'] - agg_res['lowCI']
    agg_res['highCI'] = beta.ppf(1-alpha,agg_res['sum']+1,agg_res['N']-agg_res['sum'])
    agg_res['highCI'] = agg_res['highCI'].fillna(1.0)
    agg_res['high'] = agg_res['highCI'] - agg_res['mean']
    #Now making the plot
    if plot:
        fig, ax = plt.subplots()
        ax.errorbar(agg_res[x], agg_res['mean'], 
                    yerr=agg_res[['low','high']].T.to_numpy(),
                    fmt='o', markeredgecolor='white', mfc='k',
                    ecolor='k', elinewidth=1, zorder=2)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        plt.show()
    if ret_data:
        return agg_res



##########################################


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

#This function grabs the suggested knot locations
#According to Harrell's rules
knot_dict = {3: [0.1, 0.5, 0.9],
             4: [0.05, 0.35, 0.65, 0.95],
			 5: [0.05, 0.275, 0.5, 0.725, 0.95],
			 6: [0.05, 0.23, 0.41, 0.59, 0.77, 0.95],
			 7: [0.025, 0.1833, 0.3417, 0.5, 0.6538, 0.8167, 0.975]}

def sug_knots(x,n):
	if n < 3:
		print('Error, need n greater than 2')
		return -1
	elif n > 7:
		print('Error, need n less than 8')
		return -1
	else:
		loc_quants = knot_dict[n]
	return list(x.quantile(loc_quants))

#Function to make plot of x vs y with confidence intervals
#Around mean
def plot_rcs(data,x,y,num_knots=None,knots=None,
             fam=sm.families.Gaussian(),ci=0.99,
             plot=True,ret_data=False, 
             marker_size=def_size, marker_alpha=0.7):
    #Creating new data
    copy_dat = data[ [y,x] ]
    #Adding in the splines
    if knots is not None:
        kn = knots
        rcs(copy_dat[x],kn,'S',data=copy_dat)
    else:
        kn = sug_knots(copy_dat[x], num_knots)
        rcs(copy_dat[x],kn,'S',data=copy_dat)
    #creating the design matrix
    copy_dat['Const'] = 1
    indep_vars = list(copy_dat)[1:]
    #Estimating the model
    X = copy_dat[indep_vars]
    Y = copy_dat[y]
    mod = sm.GLM(Y, X, family=fam)
    mod_res = mod.fit()
    #Getting the confidence intervals around the result
    mi, mx = copy_dat[x].min(), copy_dat[x].max()
    space_x = pd.DataFrame(np.linspace(mi,mx,100), columns=[x])
    rcs(space_x,kn,'S',data=space_x)
    space_x['Const'] = 1
    predictions = mod_res.get_prediction(space_x)
    #may want to fill in min/max x here instead
    #of using the original data using np.linspace
    al = 1 - ci
    pred_vals = predictions.summary_frame(alpha=al)
    pred_vals['x'] = space_x[x]
    #Now making a plot
    if plot:
        fig, ax = plt.subplots()
        for k in kn:
            ax.axvline(k, linestyle='solid', alpha=0.6, 
                       color='grey',linewidth=0.5, zorder=1)
        ax.plot(pred_vals['x'],pred_vals['mean'], 
                zorder=3, color='darkblue',alpha=0.9)
        ax.fill_between(pred_vals['x'],pred_vals['mean_ci_lower'],
                        pred_vals['mean_ci_upper'],alpha=0.2,
                        zorder=2, color='darkblue')
        if marker_alpha > 0:
            ax.scatter(copy_dat[x], copy_dat[y], 
                       c='grey', edgecolor='k', 
                       s=marker_size, alpha=marker_alpha, 
                       zorder=4)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        plt.show()
    if ret_data:
        return pred_vals


#Similar function, but with a formula input
def plot_form(data,x,y,form,fam=sm.families.Gaussian(),
              ci=0.99,plot=True,ret_data=False, 
             marker_size=def_size, marker_alpha=0.7):
    #Estimating the model
    datY, datX = patsy.dmatrices(form, data, return_type='dataframe')
    mod = sm.GLM(datY, datX, family=fam)
    mod_res = mod.fit()
    #Getting the confidence intervals around the result
    mi, mx = data[x].min(), data[x].max()
    space_x = pd.DataFrame(np.linspace(mi,mx,100), columns=[x])
    space_x[y] = 1 #need to pick a value that is OK for the operator
    des_y, des_matX = patsy.dmatrices(form, space_x, return_type='dataframe')
    predictions = mod_res.get_prediction(des_matX)
    #may want to fill in min/max x here instead
    #of using the original data using np.linspace
    al = 1 - ci
    pred_vals = predictions.summary_frame(alpha=al)
    pred_vals['x'] = space_x[x]
    #Now making a plot
    if plot:
        fig, ax = plt.subplots()
        ax.plot(pred_vals['x'],pred_vals['mean'], 
                zorder=3, color='darkblue',alpha=0.9)
        ax.fill_between(pred_vals['x'],pred_vals['mean_ci_lower'],
                        pred_vals['mean_ci_upper'],alpha=0.2,
                        zorder=2, color='darkblue')
        if marker_alpha > 0:
            ax.scatter(data[x], data[y], 
                       c='grey', edgecolor='k', 
                       s=marker_size, alpha=marker_alpha, 
                       zorder=4)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        plt.show()
    if ret_data:
        return pred_vals

#I need to add in group and small multiple functions
#for formulas
#Do a similar function, but for quantile regression

#A group function to superimpose on the same chart
def group_rcs_plot(data,x,y,group,colors=None,
                   num_knots=None,knots=None,
                   fam=sm.families.Gaussian(),ci=0.99,
                   plot=True,ret_data=False):
    grps = list(pd.unique(data[group]))
    comb_dat = []
    for g in grps:
        sub_dat = data[data[group] == g]
        sub_plot_dat = plot_rcs(sub_dat,x,y,
                                num_knots,knots,
                                fam,ci,
                                plot=False,
                                ret_data=True)
        sub_plot_dat[group] = g
        comb_dat.append(sub_plot_dat)
    #prepping the color list
    if colors is not None:
        cl = colors
    else:
        res = matplotlib.cm.get_cmap('Accent',len(grps))
        cl = [res(i) for i in range(len(grps))]
    #Now making plot
    z_ord = 1
    if plot:
        fig, ax = plt.subplots()
        if knots is not None:
            for k in kn:
                ax.axvline(k, linestyle='solid', alpha=0.6, 
                           color='grey',linewidth=0.5, zorder=1)            
        for g,pred_vals,c in zip(grps,comb_dat,cl):
            z_ord += 1
            ax.fill_between(pred_vals['x'],pred_vals['mean_ci_lower'],
                            pred_vals['mean_ci_upper'],alpha=0.3,
                            zorder=z_ord, label=g, color=c)
            z_ord += 1
            ax.plot(pred_vals['x'],pred_vals['mean'], 
                    zorder=z_ord, label=g, color=c, alpha=0.9)
        #now making a nice legend combining areas/lines
        handler, labeler = ax.get_legend_handles_labels()
        pl = len(grps)
        hd = [(handler[i],handler[i+pl]) for i in range(pl)]
        ax.legend(hd, labeler[0:pl], loc="center left", bbox_to_anchor=(1, 0.5))
        ax.set_xlabel(x)
        ax.set_ylabel(y)
    #If no plot, return data in long format
    if ret_data:
        ret_dat = pd.concat(comb_dat,axis=0)
        return ret_dat
      
#A function to make small multiple in seaborn easier
def loc_error(data, x, y, num_knots=None,knots=None,
              fam=sm.families.Gaussian(),ci=0.99, 
              marker_size=def_size, marker_alpha=0.7,
              **kwargs):
    pred_vals = plot_rcs(data, x, y, num_knots=num_knots, 
                         knots=knots,fam=fam,ci=ci,
                         ret_data=True, plot=False)
    ax = plt.gca()
    if knots is not None:
        kn = knots
    else:
        kn = sug_knots(data[x], num_knots)
    for k in kn:
        ax.axvline(k, linestyle='solid', alpha=0.6, 
                   color='grey',linewidth=0.5, zorder=1)
    ax.plot(pred_vals['x'],pred_vals['mean'], 
             zorder=3, color='darkblue',alpha=0.9)
    ax.fill_between(pred_vals['x'],pred_vals['mean_ci_lower'],
                     pred_vals['mean_ci_upper'],alpha=0.2,
                     zorder=2, color='darkblue')
    if marker_alpha > 0:
        ax.scatter(data[x], data[y], 
                   c='grey', edgecolor='k', alpha=marker_alpha, 
                   s=marker_size, zorder=4)

#If you want to use my default chart template
andy_nogrid = {'axes.grid': False,
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

def change_theme():
    matplotlib.rcParams.update(andy_nogrid)
    
'''
#Test case
years = pd.Series(list(range(26)))
kn = [3.0,7.0,12.0,21.0]
print( rcs(years,knots=kn,stub='S') )
print( sug_knots(years, 4) )

#Example appending to dataframe
vcr = [1881.3,
       1995.2,
       2036.1,
       2217.6,
       2299.9,
       2383.6,
       2318.2,
       2163.7,
       2089.8,
       1860.9,
       1557.8,
       1344.2,
       1268.4,
       1167.4,
       1062.6,
        945.2,
        927.5,
        789.6,
        734.1,
        687.4,
        673.1,
        637.9,
        613.8,
        580.3,
        551.8,
        593.1]

yr_df = pd.DataFrame(zip(years,years+1985,vcr), columns=['y1','years','vcr'])
rcs(years,knots=kn,stub='S',data=yr_df)
print(yr_df)

#Example plots in seaborn
import seaborn as sns
iris = sns.load_dataset('iris')

plot_dat = group_rcs_plot(iris,'sepal_length','sepal_width',
                          'species',colors=None,num_knots=3,
                          plot=True,ret_data=True)
#Small multiple example
g = sns.FacetGrid(iris, col='species')
g.map_dataframe(loc_error, x='sepal_length', y='sepal_width', num_knots=3)
g.set_axis_labels("Sepal Length", "Sepal Width")
'''

'''
#For example verification in R
library(rms)
x <- 0:25
rcs(x,c(3,7,12,21))
'''
