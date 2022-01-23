'''
Fair distance minimization
https://github.com/apwheele/PatrolRedistrict/blob/master/DataCreated/01_pmed_class.py

https://apps.urban.org/features/equity-data-tool/#results-city

https://legallysociable.com/2022/01/15/pop-up-covid-19-testing-sites-likely-benefit-from-more-vacant-commercial-properties/
'''

import fair_distance
import geopandas
import matplotlib.pyplot as plt
import pandas as pd
import pulp
import pyproj

################################################
# A Simple data example to show it works

# Source data
# X/Y Source and white/minority
x = [0.0,0.5,1.0]
y = [1.0,0.0,1.0]
w = [10,20, 0]
m = [10, 0,20]

so = pd.DataFrame(zip(x,y,w,m),
        columns=['x','y','w','m'])
so['id'] = range(so.shape[0])

# Destination Locations
xd = [0.0,0.3,0.6,0.9]
yd = [0.5]*4

de = pd.DataFrame(zip(xd,yd),columns=['x','y'],index=['a','b','c','d'])
de['id'] = range(de.shape[0])

# To check other subsets, it returns correct 1/2
# de2 = de.loc[[0,1,3]].copy()

fd = fair_distance.fair_dist(so,['x','y','w','m'],de,['x','y'],2,10)
fd.solve()

# Scatterplot source squares
# Scatterplot destination circles

fd.clust_map(bord_kwargs={'figsize':(5,5)})

# Without taking into account racial subgroups
md = fair_distance.min_dist(so,['x','y','w','m'],de,['x','y'],2,10)
md.solve()
#md.clust_map(bord_kwargs={'figsize':(5,5)})
################################################

################################################


# Read in Outline of Dallas
dal_outline = geopandas.GeoDataFrame.from_file('Dallas_MainArea_Proj.shp')

# Generate grid cells over the city
grid_dal = fair_distance.grid_over(dal_outline, 5280) # every mile

# Read in census data 
cens = pd.read_csv('DallasBlockGroup.csv')

# Prep variables I need
cens['white_pop'] = cens['b03002_003']
cens['minor_pop'] = cens['b02001_001'] - cens['b03002_003']
cens['lat'] = cens['intptlat']
cens['lon'] = cens['intptlon']
some_pop = cens['b02001_001'] > 0 #do not need 0 pop areas
keep_vars = ['white_pop','minor_pop','lat','lon']
cens = cens.loc[some_pop,keep_vars].reset_index(drop=True)

# Project data to same as outline
epsg_dal = dal_outline.crs.to_epsg()
pd = pyproj.Transformer.from_crs(4326, epsg_dal) #4326 is lat/lon
cens['x'], cens['y'] = pd.transform(cens.lat,cens.lon)

# Create and Solve model

# Takes about a minute to create the model
fd = fair_distance.fair_dist(cens,['x','y','white_pop','minor_pop'],
     grid_dal,['X','Y'],5,15*5280) #eliminating if over 15 miles away

# Takes around 3 minutes to solve
fd.solve(pulp.CPLEX_CMD(msg=True))

# Solution is
#      Total objective value is 37503.64357446054
#      White Average Distance 18571.8594672798
#      Minority Average Distance 18751.821787230274
#      Difference penalty 179.96231995047492

# Make a nice map of the results

fd.clust_map(border=dal_outline)
#plt.show()

# What is the solution if you dont take into account race?
md = fair_distance.min_dist(cens,['x','y','white_pop','minor_pop'],
     grid_dal,['X','Y'],5,15*5280) #eliminating if over 15 miles away

# Takes around 1 minute to solve
md.solve(pulp.CPLEX_CMD(msg=True))

# Solution for 5 areas is
#      Total objective value is 18436.5938700623
#      White Average Distance 17171.80475248261
#      Minority Average Distance 19016.88293251815
#      Difference penalty 1845.0781800355398

md.clust_map(border=dal_outline)
#plt.show()

################################################