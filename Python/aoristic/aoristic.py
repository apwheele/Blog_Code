'''
Functions to conduct aoristic
analysis using python
'''

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import imread

# Constants needed
week_hour = [(wd,hr) for wd in range(7) for hr in range(24)]
week_hour_df = pd.DataFrame(week_hour,columns=['weekday','hour'])
week_equal = [1.0/len(week_hour)]*len(week_hour)
week_missing = [None]*len(week_hour)
wd_lab = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
wd_di = {i:w for i,w in enumerate(wd_lab)}
week_hour_labs = [f'{wd}_{hr}' for wd in wd_lab for hr in range(24)]
week_color = ['#BABABA', '#878787', '#3F0001', '#7F0103', '#D6604D', '#F4A582', '#FDDBC7']


# This is intended to use as apply to a dataframe
def weekhour_func(x):
    '''
    This is intended to use via apply to a dataframe
    
    data[['begin','end'].apply(weekhour_func,axis=1,result_type='expand'
    
    And returns a vector of the weights broken down per hour of day
    and day of the week
    
    So x here is an array that has two pandas datetime values
    does a few smart things like if days are in the wrong order
    and imputes if you have begin but no end (assumes exact time then)
    
    Should handle missing values gracefully (but should be datetimes already)
    '''
    # missing data checks, if you have begin
    # impute end, if no begin you return missing
    x0, x1 = x
    if x0.second >= 0:
        beg = x0.floor('h')
        if x1.second >= 0:
           end = x1.floor('h')
        else:
           end = beg
           x1 = x0
    else:
       return week_missing
    # if times are swapped, I swap them back
    if x0 > x1:
        beg, end = end, beg
        x0, x1 = x1, x0
    # This creates a long vector, if too long
    # just returns filled in range
    tot_min = (x1 - x0).seconds/60
    if tot_min > 10080:
        return week_equal
    # here if you want to do other frequencies
    # can do pd.date_range(beg,end,freq='15min')
    # for example
    rv = pd.date_range(beg,end,freq='1h')
    # if only 1 period, it is 100%
    if rv.shape[0] == 1:
        vals = [1.0]
    else:
        tot_min = (x[1] - x[0]).seconds/60
        # proportion in ends
        beg_sub = (3600 - (x[0] - beg).seconds)/60
        end_sub = (x[1] - end).seconds/60
        mid_sub = tot_min - beg_sub - end_sub
        vals = [beg_sub] + [mid_sub]*(rv.shape[0]-2) + [end_sub]
    orig_dat = pd.DataFrame(zip(rv.weekday,rv.hour,vals),columns=['weekday','hour','weight'])
    orig_dat['weight'] = orig_dat['weight']/orig_dat['weight'].sum()
    agg_dat = orig_dat.groupby(['weekday','hour'],as_index=False)['weight'].sum()
    agg_dat = week_hour_df.merge(agg_dat,how='left').fillna(0.0)
    return agg_dat['weight'].tolist()


def agg_weekhour(data,begin,end,group=None):
    week_weights = data[[begin,end]].apply(weekhour_func,axis=1,result_type='expand')
    if group:
        week_weights = pd.concat([week_weights,data[group]],axis=1)
        agg_df = week_weights.groupby(group,as_index=False).sum()
        agg_df = agg_df.melt(id_vars=group)
        agg_df.columns = group + ['weekval','weight']
        wkdf = week_hour_df.copy()
        wkdf['weekval'] = wkdf.index
        agg_df = agg_df.merge(wkdf,how='left',on='weekval').fillna(0)
        agg_df.sort_values(by=group + ['weekday','hour'],inplace=True,ignore_index=True)
        agg_df.drop(columns='weekval',inplace=True)
    else:
        week_sum = week_weights.sum(axis=0)
        agg_df = week_hour_df.copy()
        agg_df['weight'] = week_sum
    return agg_df


def agg_hour(data,begin,end,group=None):
    res_week = agg_weekhour(data,begin,end,group)
    if group:
        res_day = res_week.groupby(group + ['hour'],as_index=False)['weight'].sum()
    else:
        res_day = res_week.groupby('hour',as_index=False)['weight'].sum()
    return res_day


# matplotlib theme
andy_theme = {'font.sans-serif': 'Verdana',
              'font.family': 'sans-serif',
              'axes.grid': True,
              'grid.linestyle': '--',
              'grid.color': "#DDDDDD",
              'legend.framealpha': 1,
              'legend.facecolor': 'white',
              'legend.shadow': True,
              'legend.fontsize': 14,
              'legend.title_fontsize': 16,
              'xtick.labelsize': 14,
              'ytick.labelsize': 14,
              'axes.labelsize': 16,
              'axes.titlesize': 20,
              'axes.titlelocation': 'left',
              'figure.dpi': 300,
}

matplotlib.rcParams.update(andy_theme)

im = imread('WLineRec.PNG')

def add_logo(ax, loc=[0.78,0.78], size=0.2, logo=im):
    if type(logo) == str:
        im = image.imread(logo)
    else:
        im = logo
    xrange = ax.get_xlim()
    yrange = ax.get_ylim()
    xdif = xrange[1] - xrange[0]
    ydif = yrange[1] - yrange[0]
    startx = loc[0]*xdif + xrange[0]
    starty = loc[1]*ydif + yrange[0]
    coords = [startx,starty,size*xdif,size*ydif]
    axin = ax.inset_axes(coords,transform=ax.transData)
    axin.imshow(im)
    axin.axis('off')


def plt_super(data,
              color=week_color,
              ax=None,
              figsize=(8,4),
              show=True,
              legend=True,
              leg_kwargs={'bbox_to_anchor':(1.0,1.0)},
              save=None,
              save_kwarges={'dpi':500,'bbox_inches':'tight'},
              title=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    for w in range(7):
        sub = data[data['weekday'] == w].copy()
        ax.plot(sub['hour'],sub['weight'],c=week_color[w],label=wd_di[w])
    ax.set_xticks(list(range(0,24,2)))
    if title:
        ax.set_title(title)
    if legend:
        ax.legend(**leg_kwargs)
    if save:
        fig.savefig(save,**save_kwargs)
    if show:
        fig.show()


def plt_basic(data,
              color='k',
              ax=None,
              figsize=(8,4),
              show=True,
              label=None,
              save=None,
              save_kwargs={'dpi':500,'bbox_inches':'tight'},
              title=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.plot(data['hour'],data['weight'],marker='o',c=color,markeredgecolor='white',label=label)
    ax.set_xticks(list(range(0,24,2)))
    if title:
        ax.set_title(title)
    if save:
        fig.savefig(save,**save_kwargs)
    if show:
        fig.show()