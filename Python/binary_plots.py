'''
Set of random python functions
I find helpful

Andy Wheeler
apwheele@gmail.com
andrewpwheeler.com
'''

import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

###############################################################
#CALIBRATION

#See below for explanation
#https://andrewpwheeler.com/2020/07/04/adjusting-predicted-probabilities-for-sampling/

#Rebalancing function, rewrite from
#https://github.com/matloff/regtools/blob/master/inst/UnbalancedClasses.md
#and https://www.listendata.com/2015/04/oversampling-for-rare-event.htm
def classadjust(condprobs,wrongprob,trueprob):
    a = condprobs/(wrongprob/trueprob)
    comp_cond = 1 - condprobs
    comp_wrong = 1 - wrongprob
    comp_true = 1 - trueprob
    b = comp_cond/(comp_wrong/comp_true)
    return a/(a+b)

#Calibration Chart
def cal_data(prob, true, data, bins, plot=False, figsize=(6,4), save_plot=False):
    cal_dat = data[[prob,true]].copy()
    cal_dat['Count'] = 1
    cal_dat['Bin'] = pd.qcut(cal_dat[prob], bins, range(bins) ).astype(int) + 1
    agg_bins = cal_dat.groupby('Bin', as_index=False)['Count',prob,true].sum()
    agg_bins['Predicted'] = agg_bins[prob]/agg_bins['Count']
    agg_bins['Actual'] = agg_bins[true]/agg_bins['Count']
    if plot:
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(agg_bins['Bin'], agg_bins['Predicted'], marker='+', label='Predicted')
        ax.plot(agg_bins['Bin'], agg_bins['Actual'], marker='o', markeredgecolor='w', label='Actual')
        ax.set_ylabel('Probability')
        ax.legend(loc='upper left')
        ax.set_xlim([0,bins+1])
        plt.xticks(None)
        plt.tick_params(length=0)
        if save_plot:
            plt.savefig(save_plot, dpi=500, bbox_inches='tight')
        plt.show()
    return agg_bins

# Calibration chart by groups (long format, seaborn small multiple)
def cal_data_group(prob, true, group, data, bins, plot=False, wrap_col=3, sns_height=4, save_plot=False):
    cal_dat = data[[prob,true,group]].copy()
    cal_dat['Count'] = 1
    cal_dat['Bin'] = (cal_dat.groupby(group,as_index=False)[prob]
                        ).transform( lambda x: pd.qcut(x, bins, labels=range(bins))
                        ).astype(int) + 1
    agg_bins = cal_dat.groupby([group,'Bin'], as_index=False)['Count',prob,true].sum()
    agg_bins['Predicted'] = agg_bins[prob]/agg_bins['Count']
    agg_bins['Actual'] = agg_bins[true]/agg_bins['Count']
    agg_long = pd.melt(agg_bins, id_vars=['Bin',group], value_vars=['Predicted','Actual'], 
                       var_name='Type', value_name='Probability')
    if plot:
        d = {'marker': ['o','X']}
        ax = sns.FacetGrid(data=agg_long, col=group, hue='Type', hue_kws=d,
                           col_wrap=wrap_col, despine=False, height=sns_height)
        ax.map(plt.plot, 'Bin', 'Probability', markeredgecolor="w")
        ax.set_titles("{col_name}")
        ax.set_xlabels("")
        ax.set_xticklabels("")
        ax.axes[0].legend(loc='upper left')
        # Setting xlim in FacetGrid not behaving how I want
        for a in ax.axes:
            a.set_xlim([0,bins+1])
            a.tick_params(length=0)
        if save_plot:
            plt.savefig(save_plot, dpi=500, bbox_inches='tight')
        plt.show()
    return agg_bins
    
# Calibration chart by multiple variables (wide format)
def cal_data_wide(probs, true, data, bins, plot=False, wrap_col=3, sns_height=4, save_plot=False):
    cal_dat = data[ probs + [true]].copy() 
    cal_dat = pd.melt(cal_dat, id_vars=true, value_vars=probs, 
                      var_name='Group', value_name='prob')
    cal_dat['Count'] = 1
    cal_dat['Bin'] = (cal_dat.groupby('Group',as_index=False)['prob']
                        ).transform( lambda x: pd.qcut(x, bins, labels=range(bins))
                        ).astype(int) + 1
    agg_bins = cal_dat.groupby(['Group','Bin'], as_index=False)['Count','prob',true].sum()
    agg_bins['Predicted'] = agg_bins['prob']/agg_bins['Count']
    agg_bins['Actual'] = agg_bins[true]/agg_bins['Count']
    agg_long = pd.melt(agg_bins, id_vars=['Bin','Group'], value_vars=['Predicted','Actual'], 
                       var_name='Type', value_name='Probability')
    if plot:
        d = {'marker': ['o','X']}
        ax = sns.FacetGrid(data=agg_long, col='Group', hue='Type', hue_kws=d,
                           col_wrap=wrap_col, despine=False, height=sns_height)
        ax.map(plt.plot, 'Bin', 'Probability', markeredgecolor="w")
        ax.set_titles("{col_name}")
        ax.set_xlabels("")
        ax.set_xticklabels("")
        ax.axes[0].legend(loc='upper left')
        # Setting xlim in FacetGrid not behaving how I want
        for a in ax.axes:
            a.set_xlim([0,bins+1])
            a.tick_params(length=0)
        if save_plot:
            plt.savefig(save_plot, dpi=500, bbox_inches='tight')
        plt.show()
    return agg_bins

# Calibration chart, multiple variables and by sub-group
def cal_data_wide_group(probs, true, group, data, bins, plot=False, 
                        wrap_col=3, sns_height=3, font_title=12, save_plot=False):
    cal_dat = data[ probs + [true, group]].copy() 
    cal_dat = pd.melt(cal_dat, id_vars=[true,group], value_vars=probs, 
                      var_name='Group', value_name='prob')
    cal_dat['Count'] = 1
    cal_dat['Bin'] = (cal_dat.groupby([group, 'Group'],as_index=False)['prob']
                        ).transform( lambda x: pd.qcut(x, bins, labels=range(bins))
                        ).astype(int) + 1
    agg_bins = cal_dat.groupby([group,'Group','Bin'], as_index=False)['Count','prob',true].sum()
    agg_bins['Predicted'] = agg_bins['prob']/agg_bins['Count']
    agg_bins['Actual'] = agg_bins[true]/agg_bins['Count']
    agg_long = pd.melt(agg_bins, id_vars=['Bin',group,'Group'], value_vars=['Predicted','Actual'], 
                       var_name='Type', value_name='Probability')
    agg_long['CombFacet'] = agg_long[group].astype(str) + " | " + agg_long['Group'].str.strip()
    agg_long.sort_values(by=['Group',group], inplace=True)
    agg_long.reset_index(drop=True, inplace=True)
    if plot:
        d = {'marker': ['o','X']}
        ax = sns.FacetGrid(data=agg_long, col='CombFacet', hue='Type', hue_kws=d,
                           col_wrap=wrap_col, despine=False, height=sns_height)
        ax.map(plt.plot, 'Bin', 'Probability', markeredgecolor="w")
        ax.set_titles(col_template="{col_name}",size=font_title)
        ax.set_xlabels("")
        ax.set_xticklabels("")
        ax.axes[0].legend(loc='upper left')
        #Setting xlim in FacetGrid not behaving how I want
        for a in ax.axes:
            a.set_xlim([0,bins+1])
            a.tick_params(length=0)
        if save_plot:
            plt.savefig(save_plot, dpi=500, bbox_inches='tight')
        plt.show()
    return agg_bins

###############################################################

###############################################################
#MATPLOTLIB THEME

#https://andrewpwheeler.com/2020/05/05/notes-on-matplotlib-and-seaborn-charts-python/

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
 
#print( matplotlib.rcParams )
matplotlib.rcParams.update(andy_theme)

###############################################################

###############################################################
#AUC CHARTS

#AUC data plot in wide format, y_scores needs to be a list
#Of the variables in the dataframe
def auc_plot(data, y_true, y_scores, figsize=(6,6), save_plot=False, leg_size=None):
    fin_dat = []
    fig, ax = plt.subplots(figsize=figsize)
    #Equality line
    plt.plot([0, 1], [0, 1], color='grey', lw=1, linestyle='-')
    plt.xlim([-0.03, 1.03])
    plt.ylim([-0.03, 1.03])
    tick_num = [i/10 for i in range(11)]
    plt.xticks(tick_num)
    plt.yticks(tick_num)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    ax.set_aspect(aspect='equal')
    for s in y_scores:
        fpr, tpr, thr = roc_curve(data[y_true], data[s])
        sub_dat = pd.DataFrame( zip(fpr, tpr, thr), 
                                columns=['FPR','TPR','Thresh'] )
        sub_dat['Var'] = s
        auc_val = roc_auc_score(data[y_true], data[s])
        sub_dat['AUC'] = auc_val
        fin_dat.append(sub_dat)
        ax.plot(fpr, tpr, lw=2, label=f'{s} (AUC={auc_val:0.2f})')
    if len(y_scores) == 1:
        plt.title(f'{y_scores[0]} (AUC={auc_val:0.2f})')
    else:
        plt.title('ROC Curves & AUC Scores')
        ax.legend(loc='lower right', fontsize=leg_size)
    if save_plot:
        plt.savefig(save_plot, dpi=500, bbox_inches='tight')
    plt.show()
    fin_df = pd.concat(fin_dat, axis=0)
    return fin_df

#AUC data plot in long format
def auc_plot_long(data, y_true, y_score, group, figsize=(6,6), save_plot=False, leg_size=None):
    fin_dat = []
    fig, ax = plt.subplots(figsize=figsize)
    #Equality line
    plt.plot([0, 1], [0, 1], color='grey', lw=1, linestyle='-')
    plt.xlim([-0.03, 1.03])
    plt.ylim([-0.03, 1.03])
    tick_num = [i/10 for i in range(11)]
    plt.xticks(tick_num)
    plt.yticks(tick_num)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    ax.set_aspect(aspect='equal')
    grp_list = pd.unique(data[group])
    for s in grp_list:
        subset = data[ data[group] == s ]
        fpr, tpr, thr = roc_curve(subset[y_true], subset[y_score])
        sub_dat = pd.DataFrame( zip(fpr, tpr, thr), 
                                columns=['FPR','TPR','Thresh'] )
        sub_dat['Var'] = s
        auc_val = roc_auc_score(subset[y_true], subset[y_score])
        sub_dat['AUC'] = auc_val
        fin_dat.append(sub_dat)
        ax.plot(fpr, tpr, lw=2, label=f'{s} (AUC={auc_val:0.2f})')
    if len(grp_list) == 1:
        plt.title(f'{grp_list[0]} (AUC={auc_val:0.2f})')
    else:
        plt.title('ROC Curves & AUC Scores')
        ax.legend(loc='lower right', fontsize=leg_size)
    if save_plot:
        plt.savefig(save_plot, dpi=500, bbox_inches='tight')
    plt.show()
    fin_df = pd.concat(fin_dat, axis=0)
    return fin_df

# AUC Plot long (by group) and multiple variables
# AUC data plot in wide format, y_scores needs to be a list
# Of the variables in the dataframe
def auc_plot_wide_group(data, y_true, y_scores, group, ncols=3,
                        size=3, save_plot=False, leg_size=None):
    fin_dat = []
    # Figuring out number of groups
    grp_list = pd.unique(data[group])
    ncols = min([3,len(grp_list)])
    nrows = int(np.ceil(  len(grp_list) / ncols ) )
    res_order = [(r,c) for r in range(nrows) for c in range(ncols)]
    fig, ax_grid = plt.subplots(figsize=(size*ncols, size*nrows), 
                                nrows=nrows, ncols=ncols,
                                sharex=False, sharey=True, squeeze=False)
    fig.subplots_adjust(wspace=0.05) #?constrained layout?
    tick_num = [i/10 for i in range(11)]
    tick_lab = [0.0,'',0.2,'',0.4,'',0.6,'',0.8,'',1.0]
    for g,o in zip(grp_list,res_order):
        ax = ax_grid[o]
        #Equality line
        ax.plot([0, 1], [0, 1], color='grey', lw=1, linestyle='-')
        ax.set_xlim(left=-0.03, right=1.03)
        ax.set_ylim(bottom=-0.03, top=1.03)
        ax.set_yticks(tick_num)
        ax.set_xticks(tick_num)
        # If last row, give x lab
        if o[0] == (nrows - 1):
            ax.set_xlabel("FPR")
            ax.set_xticklabels(tick_lab)
        else:
            ax.tick_params(axis='x', length=0)
            ax.set_xticklabels([])
        # If first column give y lab
        if o[1] == 0:
            ax.set_ylabel("TPR")
            ax.set_yticklabels(tick_lab)
        else:
            ax.tick_params(axis='y', length=0)
        ax.set_aspect(aspect='equal')
        for v in y_scores:
            subset = data[ data[group] == g ]
            fpr, tpr, thr = roc_curve(subset[y_true], subset[v])
            sub_dat = pd.DataFrame( zip(fpr, tpr, thr), 
                                    columns=['FPR','TPR','Thresh'] )
            sub_dat['Var'] = v
            sub_dat[group] = g
            auc_val = roc_auc_score(subset[y_true], subset[v])
            sub_dat['AUC'] = auc_val
            fin_dat.append(sub_dat)
            ax.plot(fpr, tpr, lw=2, label=f'{v} (AUC={auc_val:0.2f})')
        if len(y_scores) == 1:
            ax.set_title(f'{g}, {y_scores[0]} (AUC={auc_val:0.2f})')
        else:
            ax.set_title(f'{g}')
            ax.legend(loc='lower right', fontsize=leg_size)
    # The padded extra set as empty
    ext = len(res_order) - len(grp_list)
    if ext > 0:
        for e in res_order[-ext:]:
            # turn off extra
            ax_grid[e].axis('off')
            up_row = (e[0]-1,e[1])
            ax_up = ax_grid[up_row]
            # redo x axis
            ax_up.tick_params(axis='x', length=3.5)
            ax_up.set_xticks(tick_num)
            ax_up.set_xlabel('FPR')
            ax_up.set_xticklabels(tick_lab)
    if save_plot:
        plt.savefig(save_plot, dpi=500, bbox_inches='tight')
    plt.show()
    fin_df = pd.concat(fin_dat, axis=0)
    return fin_df

###############################################################

