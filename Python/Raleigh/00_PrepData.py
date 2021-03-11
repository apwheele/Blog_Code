'''
Analysis to create clumped hot
spots -Andy Wheeler
'''

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import pulp
import libpysal
import os

# proj library location got bungled at some point
import pyproj
print( pyproj.datadir.get_data_dir() )
pyproj.datadir.set_data_dir(r'D:\Conda_Envs\Geo\Library\share\proj')

#######################################################################
# FUNCTIONS

# Generating spatial grid over the city
# adapted via https://gis.stackexchange.com/a/316460/751
def grid_over(base, size):
    xmin, ymin, xmax, ymax = base.total_bounds
    xl = np.arange(xmin, xmax, size)
    yl = np.arange(ymin, ymax, size)
    polygons = []
    xc = []
    yc = []
    half = size/2.0
    for x in xl:
        for y in yl:
            polygons.append(Polygon([(x,y), (x+size, y), (x+size, y+size), (x, y+size)]))
            xc.append(x+half)
            yc.append(y+half)
    grid = gpd.GeoDataFrame({'geometry':polygons}).set_crs(base.crs)
    grid['X'] = xc
    grid['Y'] = yc
    grid_fields = list(grid)
    gj = gpd.sjoin(grid,base,how='left',op='intersects')
    gloc = gj[~gj['index_right'].isna()]
    return gloc[grid_fields].reset_index(drop=True)

# This modifies poly in place
def count_points(poly,points,var_name):
    join = gpd.sjoin(points, poly, how="left", op='intersects')
    cnt = join['index_right'].value_counts()
    poly[var_name] = cnt
    poly[var_name].fillna(0,inplace=True)

# PAI function
def pai(data,sel_var,crime_var):
    total_n = data.shape[0]
    prop_a = data[sel_var].sum()/total_n
    prop_crime = (data[sel_var]*data[crime_var]).sum() / data[crime_var].sum()
    return prop_crime/prop_a

# CI function
def clumpindex(data,sel_var,w):
    # Calculating spatial lags for the total weights
    lag_total = libpysal.weights.lag_spatial(w, np.ones(data[sel_var].shape))
    lag_sel = libpysal.weights.lag_spatial(w, data[sel_var])
    lag_nonsel = lag_total - lag_sel
    # Now calculating edge counts
    g11 = (lag_sel*data[sel_var]).sum()
    g12 = (lag_nonsel*data[sel_var]).sum()
    g1 = g11/(g11+g12) #No correction for minimum edge
    p1 = data[sel_var].sum()/data.shape[0]
    # Now calculating CI
    if (g1 < p1) & (p1 < 0.5):
        ci = (g1 - p1)/g1
    else:
        ci = (g1 - p1)/(1 - p1)
    return ci

print( pulp.listSolvers(onlyAvailable=True) )
# Much better success with CPLEX than with default coin for more
# Weight to the edges part
solver = pulp.getSolver('CPLEX_CMD', timeLimit=10)

def lp_clumpy(data, w, sel_n, crime_var, theta):
    gi = list(data.index)
    crime = data[crime_var]
    theta_obs = 1.0 - theta
    P = pulp.LpProblem("Choosing_Cases_to_Audit", pulp.LpMaximize)
    S = pulp.LpVariable.dicts("Selecting_Grid_Cell", [i for i in gi], lowBound=0, upBound=1, cat=pulp.LpInteger)
    E = pulp.LpVariable.dicts("Edge_Weights", [i for i in gi], lowBound=0, cat=pulp.LpContinuous)
    #Objective Function
    P += pulp.lpSum( theta*crime[i]*S[i] + theta_obs*E[i] for i in gi)
    # Constraint 1, total areas selected
    P += pulp.lpSum( S[i] for i in gi ) == sel_n
    # Constraint 2, edge decision sum of selected
    for i in gi:
        neigh = w[i].keys()
        P += pulp.lpSum( E[i] ) <= pulp.lpSum( S[n] for n in neigh )
        P += pulp.lpSum( E[i] ) <= S[i]*len(neigh)
    # Solving the problem
    res = P.solve(solver)
    if res != 1:
        print('Problem not solved')
        return -1
    else:
        sel_list = []
        tot_crimes = 0
        tot_edges = 0
        for i in gi:
            sloc = S[i].varValue
            sel_list.append(sloc)
            tot_crimes += sloc*crime[i]
            tot_edges += E[i].varValue
        print(f'\nSolved\ntotal crime: {tot_crimes:,.0f}\ntotal interior edges: {tot_edges:,.0f}\n')
        return sel_list

#######################################################################

#######################################################################
# Loading in data and creating spatial grid

os.chdir(r'D:\Dropbox\Dropbox\PublicCode_Git\Blog_Code\Python\Raleigh')

# These are both via Raleigh open data platform
area_file = r'GIS_Data\Planning_Jurisdictions.shp'
crime_file = r'GIS_Data\Raleigh_Police_Incidents_(NIBRS).shp'
loc_proj = 'EPSG:3359'

# Prepping the boundary of Raleigh
areas_wake = gpd.GeoDataFrame.from_file(area_file)
ral = areas_wake[areas_wake['JURISDICTI'] == 'RALEIGH'].dissolve(by='JURISDICTI').to_crs(loc_proj)

# This is in feet
ral_grid = grid_over(ral, 500)

# Spatial weights matrix
grid_weights = libpysal.weights.Rook.from_dataframe(ral_grid)
print ( grid_weights.histogram ) #so no 0 weights, just 3 components

# Getting crime points
crime_points = gpd.GeoDataFrame.from_file(crime_file)
crime_proj = crime_points[~crime_points['geometry'].isna()].to_crs(loc_proj)
car_burg = crime_proj[crime_proj['crime_cate'] == 'LARCENY FROM MV'].copy()
year_break = car_burg['reported_y'] < 2020
car_hist = car_burg[year_break].copy()
car_test = car_burg[~year_break].copy()

# Aggregating to grid cells
count_points(ral_grid, car_hist, 'CarBurgHist')
count_points(ral_grid, car_test, 'CarBurgTest')
print( ral_grid.groupby('CarBurgHist')['geometry'].count() )

#######################################################################

#######################################################################
# Showing selecting top 1%

# Selecting top 1% of the city
n_loc = np.floor(ral_grid.shape[0]*0.01)
print(n_loc)

ral_grid['SelectTop1'] = (ral_grid['CarBurgHist'].rank(ascending=False, method='first') <= n_loc)*1
print( pai(ral_grid, 'SelectTop1', 'CarBurgHist') )
print( pai(ral_grid, 'SelectTop1', 'CarBurgTest') )

print( clumpindex(ral_grid,'SelectTop1',grid_weights) )

# Function to make a nice Raleigh hot spot map
def map_hs(data, sel_var, crime_var, savefig=None):
    # Creating function to map area by chosen points
    fig, ax = plt.subplots()
    ral.boundary.plot(ax=ax, linewidth=0.8, edgecolor='k')
    data[data[sel_var]==1].plot(ax=ax, color='red', edgecolor='white', linewidth=0)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    # Add north arrow, https://stackoverflow.com/a/58110049/604456
    x, y, arrow_length = 0.90, 0.95, 0.13
    ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
                arrowprops=dict(facecolor='black', width=3, headwidth=10),
                ha='center', va='center', fontsize=10,
                xycoords=ax.transAxes)
    # scale bar 803000
    x, y, scale_len = 2050000, 715000, 5280*5 #arrowstyle='-'
    scale_rect = matplotlib.patches.Rectangle((x,y),scale_len,200,linewidth=1,edgecolor='k',facecolor='k')
    ax.add_patch(scale_rect)
    plt.text(x+scale_len/2, y+1400, s='5 Miles', fontsize=8, horizontalalignment='center')
    pai_stat = pai(data, sel_var, crime_var)
    ci_stat = clumpindex(data,sel_var, grid_weights) 
    plt.title(f"PAI:{pai_stat:.1f}, CI:{ci_stat:0.2f}")
    # Title with N, PAI, CI
    #plt.axis('equal')
    if savefig:
        plt.savefig(savefig, dpi=1000, bbox_inches='tight')
    plt.show()

map_hs(ral_grid, 'SelectTop1', 'CarBurgTest', 'SelectTop1.png')

#######################################################################

#######################################################################
# Linear program with soft constraints on clumpiness

select_100 = lp_clumpy(ral_grid, grid_weights, n_loc, 'CarBurgHist', 1.0)
print( (ral_grid['SelectTop1']*ral_grid['CarBurgHist']).sum() )

select_090 = lp_clumpy(ral_grid, grid_weights, n_loc, 'CarBurgHist', 0.9)
ral_grid['Sel090'] = select_090
pd.crosstab(ral_grid['SelectTop1'], ral_grid['Sel090'])
# Did not select 100% same areas!

select_050 = lp_clumpy(ral_grid, grid_weights, n_loc, 'CarBurgHist', 0.5)
ral_grid['Sel050'] = select_050
print( pd.crosstab(ral_grid['SelectTop1'], ral_grid['Sel050']) )
map_hs(ral_grid, 'Sel050', 'CarBurgTest', 'Select_050.png')

select_020 = lp_clumpy(ral_grid, grid_weights, n_loc, 'CarBurgHist', 0.2)
ral_grid['Sel020'] = select_020
print( pd.crosstab(ral_grid['SelectTop1'], ral_grid['Sel020']) )
map_hs(ral_grid, 'Sel020', 'CarBurgTest', 'Select_020.png')

#######################################################################





