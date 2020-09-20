'''
Making conditional scatterplots
of E[Y|X]

Andy Wheeler
'''


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import os
import sys

mydir = r'D:\Dropbox\Dropbox\PublicCode_Git\Blog_Code\Python\Smooth'
data_loc = r'https://dl.dropbox.com/s/79ma3ldoup1bkw6/DC_CrimeData.csv?dl=0'
os.chdir(mydir)

#My functions
sys.path.append(mydir)
import smooth
smooth.change_theme()

#Dissertation dataset, can read from dropbox
DC_crime = pd.read_csv(data_loc)


####################
#Example binning and making mean/std dev spike plots

smooth.mean_spike(DC_crime,'TotalLic','TotalCrime')

mean_lic = smooth.mean_spike(DC_crime,'TotalLic','TotalCrime',
                             plot=False,ret_data=True)
####################

####################
#Example with proportion confidence interval spike plots

DC_crime['BurgClip'] = DC_crime['OffN3'].clip(0,1)
smooth.prop_spike(DC_crime,'TotalLic','BurgClip')

####################

####################
#Making restricted cubic splines plot

years = pd.Series(list(range(26)))
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

#Can append rcs basis to dataframe
kn = [3.0,7.0,12.0,21.0]
smooth.rcs(years,knots=kn,stub='S',data=yr_df)

#RCS plot
smooth.plot_rcs(yr_df,'y1','vcr',knots=kn)

#If you want to use Harrell's rules to suggest
#Knot locations
smooth.sug_knots(years,4)

#Can pass in a family argument for logit/Poisson models
smooth.plot_rcs(DC_crime,'TotalLic','TotalCrime', knots=[3,7,10,15],
                fam=sm.families.Poisson(), marker_size=12)

smooth.plot_rcs(DC_crime,'TotalLic','BurgClip', knots=[3,7,10,15],
                fam=sm.families.Binomial(),marker_alpha=0)
####################

####################
#Superimposing rcs on the same plot

iris = sns.load_dataset('iris')

smooth.group_rcs_plot(iris,'sepal_length','sepal_width',
               'species',colors=None,num_knots=3)
####################

####################
#Small multiple RCS plot

#Small multiple example
g = sns.FacetGrid(iris, col='species',col_wrap=2)
g.map_dataframe(smooth.loc_error, x='sepal_length', y='sepal_width', num_knots=3)
g.set_axis_labels("Sepal Length", "Sepal Width")

####################

##################
#Here is what it looks like with a linear term

smooth.plot_form(data=DC_crime,x='TotalLic',y='TotalCrime',
                 form='TotalCrime ~ TotalLic',
                 fam=sm.families.Poisson(), marker_size=12)

#Can do polynomial terms
smooth.plot_form(data=DC_crime,x='TotalLic',y='TotalCrime',
                 form='TotalCrime ~ TotalLic + TotalLic**2 + TotalLic**3',
                 fam=sm.families.Poisson(), marker_size=12)

#Can do other smoothers
smooth.plot_form(data=DC_crime,x='TotalLic',y='TotalCrime',
                 form='TotalCrime ~ bs(TotalLic,df=4,degree=3)',
                 fam=sm.families.Poisson(), marker_size=12)

#Can do transforms of the X variable
smooth.plot_form(data=DC_crime,x='TotalLic',y='TotalCrime',
                 form='TotalCrime ~ np.sqrt(TotalLic)',
                 fam=sm.families.Poisson(), marker_size=12)

#Can do transforms of the X variable
smooth.plot_form(data=DC_crime,x='TotalLic',y='TotalCrime',
                 form='TotalCrime ~ np.log(TotalLic.clip(1)) + I(TotalLic==0)',
                 fam=sm.families.Poisson(), marker_size=12)

#This doesn't work, need to inverse transform the outcome
#on the plot
#smooth.plot_form(data=DC_crime,x='TotalLic',y='TotalCrime',
#                 form='np.log(TotalCrime+1) ~ TotalLic',
#                 marker_size=12)
##################
