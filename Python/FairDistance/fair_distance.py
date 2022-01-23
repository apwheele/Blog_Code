'''
Fair distance minimization
linear program

Andy Wheeler
'''

from datetime import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import pulp
import os
import pyproj

class fair_dist:
    """
    so - data frame source areas
    so_vars - list with strings for variable names in source
              should be (x_coord,y_coord,white_pop,minority_pop)
    de - data frame destination areas
    de_vars - list with strings for variable names
              should be (x_coord,y_coord)
    """
    def __init__(self,source,so_vars,dest,de_vars,k,max_dist):
        # Initial data prep for source/destination
        print(f'      Creating initial distance matrix @ {datetime.now()}')
        so_cop = source[so_vars].copy()
        so_cop.columns = ['x','y','w','m']
        so_cop['id'] = list(range(so_cop.shape[0]))
        so_cop.index = so_cop['id']
        de_cop = dest[de_vars].copy()
        de_cop.columns = ['x','y']
        de_cop['id'] = list(range(de_cop.shape[0]))
        de_cop.index = de_cop['id']
        # Creating the pairwise dataframe
        dm = so_cop.merge(de_cop,how='cross',suffixes=('i','j'))
        dm['dist'] = np.sqrt( (dm['xi'] - dm['xj'])**2 + 
                              (dm['yi'] - dm['yj'])**2 )
        dm.set_index(['idi','idj'], inplace=True)
        # Eliminating rows that are above the max distance
        dm_orig = dm.shape[0]
        dm = dm[dm['dist'] <= max_dist].copy()
        dm_sub  = dm.shape[0]
        print(f'      Eliminated {dm_orig - dm_sub} pairs outside {max_dist} distance')
        print(f'      total now {dm_sub} pairs')
        #print(so_cop.index)
        # Figure out min distance per destination
        rn = dm.groupby("idj")["dist"].rank("dense", ascending=True)
        mr = (rn == 1)
        min_d = dm[mr]
        nmin_d = dm[~mr].index.to_frame()
        # I want nicer sets for the lp
        de_sets = {}
        for i,j in min_d.index:
            so_ind = nmin_d.loc[nmin_d['idj'] == j,'idi'].to_list()
            de_sets[j] = (i, so_ind)
        # Set that goes the opposite way, given source what are valid destinations
        dm_ids = dm.index.to_frame()
        so_sets = {}
        for i in so_cop.index:
            so_sets[i] = dm_ids.loc[dm_ids['idi'] == i, 'idj'].to_list()
        # Set for each d_ij, the further away seed points
        #dmf = dm.index.to_frame()
        #off_local = {}
        #for i,j in dm.index:
        #    # Local distance
        #    loc_dist = dm.loc[(i,j),'dist']
        #    # All other d_ij that are closer
        #    loc_i = dmf[(dmf['idi'] == i) & (dm['dist'] <= loc_dist)]['idj'].to_list()
        #    # Offset locations closer than that distance
        #    off_local[(i,j)] = loc_i
        # Total white/minority
        tw = so_cop['w'].sum()
        tm = so_cop['m'].sum()
        wp = (dm['dist']*dm['w'])/tw
        mp = (dm['dist']*dm['m'])/tm
        # Stats for the problem
        dec_vars = dm.shape[0] + 3
        constraints = 5 + so_cop.shape[0] + dm.shape[0] - de_cop.shape[0]
        # Set overall lp problem
        print(f'      Creating initial linear program @ {datetime.now()}')
        P = pulp.LpProblem("FairDistance",pulp.LpMinimize)
        # Decision variable X_ij (binary 0/1)
        X = pulp.LpVariable.dicts("X",
            [(i,j) for (i,j) in dm.index],
            lowBound=0, 
            upBound=1,
            cat=pulp.LpInteger)
        # Decision variables M_dist, W_dist (average)
        M_dist = pulp.LpVariable("M_dist", 0)
        W_dist = pulp.LpVariable("W_dist", 0)
        # Decision variable D 
        Dif = pulp.LpVariable("Dif", 0)
        # Minimize M_dist + W_dist + D
        P += M_dist + W_dist + Dif
        # Constraint Define M_dist, W_dist
        P += M_dist == pulp.lpSum(mp[(i,j)]*X[(i,j)] for i,j in dm.index)
        P += W_dist == pulp.lpSum(wp[(i,j)]*X[(i,j)] for i,j in dm.index)
        # Constraint Max Diff
        P += Dif >= M_dist - W_dist
        P += Dif >= W_dist - M_dist
        # Constraint each source i only 1
        for i in so_cop.index:
            P += pulp.lpSum(X[(i,j)] for j in so_sets[i]) == 1
        # Constraint only k X_im selected at max
        P += pulp.lpSum(X[(i,m)] for i,m in min_d.index) <= k
        # Constraint if min not selected no off are selected
        for j in de_cop.index:
            mi = de_sets[j][0]
            mo = de_sets[j][1]
            for i in mo:
                P += X[(mi,j)] >= X[(i,j)]
        # Constraint should be assigned closest destination that
        # Is turned on
        #for i,j in dm.index:
        #    off_d = off_local[(i,j)]
        #    P += X[(i,j)] == pulp.lpSum(X[(s,m)] for s,m in min_d.index if m in off_d)
        # Assigning objects to class
        self.model = P
        self.X = X
        self.M_dist = M_dist
        self.W_dist = W_dist
        self.Dif = Dif
        self.X = X
        self.dm = dm
        self.de_sets = de_sets
        self.selected = None
        # Printing finish time
        print(f'      Finished setting problem up @ {datetime.now()}')
        print(f'      Total number of decision variables {dec_vars}')
        print(f'      Total number of constraints {constraints}')
    def solve(self,solver=None):
        """
        For solver can either pass in None for default pulp, or various pulp solvers, e.g.
        solver = pulp.CPLEX()
        solver = pulp.CPLEX_CMD(msg=True, warmStart=True)
        solver = pulp.PULP_CBC_CMD(timeLimit=1000)
        solver = pulp.GLPK_CMD()
        etc.
        run print( pulp.listSolvers(onlyAvailable=True) )
        to see available solvers on your machine
        """
        print(f'      Starting to solve function at {datetime.now()}')
        if solver == None:
            self.model.solve()
        else:
            self.model.solve(solver)
        print(f'      Solve finished at {datetime.now()}')
        stat = pulp.LpStatus[self.model.status]
        # Printing out objective stats
        if stat != "Optimal":
            print(f"      Status is {stat}")
            try:
                self.objective = pulp.value(self.model.objective)
                print(f'      Objective value is {self.objective}, but beware not optimal')
            except:
                print('      Unable to grab objective value')
        else:
            self.objective = pulp.value(self.model.objective)
            print(f'      Status is optimal\n      Total objective value is {self.objective}')
            print(f'      White Average Distance {self.W_dist.varValue}')
            print(f'      Minority Average Distance {self.M_dist.varValue}')
            print(f'      Difference penalty {self.Dif.varValue}')
        # Get solution and append to object
        res = []
        try:
            for i,j in self.dm.index:
                res.append(self.X[(i,j)].varValue)
            self.dm['paired'] = res
        except:
            print('      Unable to append results')
    def clust_map(self, 
            border=None, 
            bord_kwargs={'color':'k','linewidth':3,'figsize':(12,12),'edgecolor':'k'}, 
            s_kwargs={'s':20,'marker':'o'}, 
            d_kwargs={'s':300,'marker':'s','edgecolor':'k'}):
        """
        Creating a simple map to show the assigned areas
        """
        # Pr is the source areas
        pr = self.dm[self.dm['paired'] == 1].copy()
        pr.reset_index(inplace=True)
        pr['dx'] = pr['xj'] - pr['xi'] # for arrows if you want
        pr['dy'] = pr['yj'] - pr['yi']
        # De_pr is the destination
        de_pr = pr.drop_duplicates(['xj','yj'])
        # If no border, generate fig, ax
        if border is None:
            fig, ax = plt.subplots(**bord_kwargs)
        else:
            ax = border.boundary.plot(**bord_kwargs)
        # No ticks on outside
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        # 
        for j in de_pr['idj']:
            prs = pr[pr['idj'] == j]
            des = de_pr[de_pr['idj'] == j]
            s_kwargs['label'] = j
            p = ax.scatter(prs['xi'], prs['yi'], **s_kwargs)
            d_kwargs['c'] = p.get_facecolor()
            ax.scatter(des['xj'], des['yj'], **d_kwargs)


# Same as fair_dist, but objective is just overall average distance
class min_dist:
    """
    so - data frame source areas
    so_vars - list with strings for variable names in source
              should be (x_coord,y_coord,white_pop,minority_pop)
    de - data frame destination areas
    de_vars - list with strings for variable names
              should be (x_coord,y_coord)
    """
    def __init__(self,source,so_vars,dest,de_vars,k,max_dist):
        # Initial data prep for source/destination
        print(f'      Creating initial distance matrix @ {datetime.now()}')
        so_cop = source[so_vars].copy()
        so_cop.columns = ['x','y','w','m']
        so_cop['id'] = list(range(so_cop.shape[0]))
        so_cop.index = so_cop['id']
        de_cop = dest[de_vars].copy()
        de_cop.columns = ['x','y']
        de_cop['id'] = list(range(de_cop.shape[0]))
        de_cop.index = de_cop['id']
        # Creating the pairwise dataframe
        dm = so_cop.merge(de_cop,how='cross',suffixes=('i','j'))
        dm['dist'] = np.sqrt( (dm['xi'] - dm['xj'])**2 + 
                              (dm['yi'] - dm['yj'])**2 )
        dm.set_index(['idi','idj'], inplace=True)
        # Eliminating rows that are above the max distance
        dm_orig = dm.shape[0]
        dm = dm[dm['dist'] <= max_dist].copy()
        dm_sub  = dm.shape[0]
        print(f'      Eliminated {dm_orig - dm_sub} pairs outside {max_dist} distance')
        print(f'      total now {dm_sub} pairs')
        #print(so_cop.index)
        # Figure out min distance per destination
        rn = dm.groupby("idj")["dist"].rank("dense", ascending=True)
        mr = (rn == 1)
        min_d = dm[mr]
        nmin_d = dm[~mr].index.to_frame()
        # I want nicer sets for the lp
        de_sets = {}
        for i,j in min_d.index:
            so_ind = nmin_d.loc[nmin_d['idj'] == j,'idi'].to_list()
            de_sets[j] = (i, so_ind)
        # Set that goes the opposite way, given source what are valid destinations
        dm_ids = dm.index.to_frame()
        so_sets = {}
        for i in so_cop.index:
            so_sets[i] = dm_ids.loc[dm_ids['idi'] == i, 'idj'].to_list()
        # Set for each d_ij, the further away seed points
        #dmf = dm.index.to_frame()
        #off_local = {}
        #for i,j in dm.index:
        #    # Local distance
        #    loc_dist = dm.loc[(i,j),'dist']
        #    # All other d_ij that are closer
        #    loc_i = dmf[(dmf['idi'] == i) & (dm['dist'] <= loc_dist)]['idj'].to_list()
        #    # Offset locations closer than that distance
        #    off_local[(i,j)] = loc_i
        # Total white/minority
        tw = so_cop['w'].sum()
        tm = so_cop['m'].sum()
        tot_pop = tw + tm
        wp = (dm['dist']*dm['w'])/tw
        mp = (dm['dist']*dm['m'])/tm
        tp = (dm['dist']*(dm['w'] + dm['m']))/tot_pop
        # Stats for the problem
        dec_vars = dm.shape[0] + 3
        constraints = 5 + so_cop.shape[0] + dm.shape[0] - de_cop.shape[0]
        # Set overall lp problem
        print(f'      Creating initial linear program @ {datetime.now()}')
        P = pulp.LpProblem("MinDistance",pulp.LpMinimize)
        # Decision variable X_ij (binary 0/1)
        X = pulp.LpVariable.dicts("X",
            [(i,j) for (i,j) in dm.index],
            lowBound=0, 
            upBound=1,
            cat=pulp.LpInteger)
        # Decision variables M_dist, W_dist (average)
        M_dist = pulp.LpVariable("M_dist", 0)
        W_dist = pulp.LpVariable("W_dist", 0)
        T_dist = pulp.LpVariable("T_dist", 0)
        # Decision variable D 
        Dif = pulp.LpVariable("Dif", 0)
        # Minimize T_Dist
        P += T_dist
        # Constraint Define M_dist, W_dist, T_dist
        P += M_dist == pulp.lpSum(mp[(i,j)]*X[(i,j)] for i,j in dm.index)
        P += W_dist == pulp.lpSum(wp[(i,j)]*X[(i,j)] for i,j in dm.index)
        P += T_dist == pulp.lpSum(tp[(i,j)]*X[(i,j)] for i,j in dm.index)
        # Constraint Max Diff
        P += Dif >= M_dist - W_dist
        P += Dif >= W_dist - M_dist
        # Constraint each source i only 1
        for i in so_cop.index:
            P += pulp.lpSum(X[(i,j)] for j in so_sets[i]) == 1
        # Constraint only k X_im selected at max
        P += pulp.lpSum(X[(i,m)] for i,m in min_d.index) <= k
        # Constraint if min not selected no off are selected
        for j in de_cop.index:
            mi = de_sets[j][0]
            mo = de_sets[j][1]
            for i in mo:
                P += X[(mi,j)] >= X[(i,j)]
        # Constraint should be assigned closest destination that
        # Is turned on
        #for i,j in dm.index:
        #    off_d = off_local[(i,j)]
        #    P += X[(i,j)] == pulp.lpSum(X[(s,m)] for s,m in min_d.index if m in off_d)
        # Assigning objects to class
        self.model = P
        self.X = X
        self.M_dist = M_dist
        self.W_dist = W_dist
        self.Dif = Dif
        self.X = X
        self.dm = dm
        self.de_sets = de_sets
        self.selected = None
        # Printing finish time
        print(f'      Finished setting problem up @ {datetime.now()}')
        print(f'      Total number of decision variables {dec_vars}')
        print(f'      Total number of constraints {constraints}')
    def solve(self,solver=None):
        """
        For solver can either pass in None for default pulp, or various pulp solvers, e.g.
        solver = pulp.CPLEX()
        solver = pulp.CPLEX_CMD(msg=True, warmStart=True)
        solver = pulp.PULP_CBC_CMD(timeLimit=1000)
        solver = pulp.GLPK_CMD()
        etc.
        run print( pulp.listSolvers(onlyAvailable=True) )
        to see available solvers on your machine
        """
        print(f'      Starting to solve function at {datetime.now()}')
        if solver == None:
            self.model.solve()
        else:
            self.model.solve(solver)
        print(f'      Solve finished at {datetime.now()}')
        stat = pulp.LpStatus[self.model.status]
        # Printing out objective stats
        if stat != "Optimal":
            print(f"      Status is {stat}")
            try:
                self.objective = pulp.value(self.model.objective)
                print(f'      Objective value is {self.objective}, but beware not optimal')
            except:
                print('      Unable to grab objective value')
        else:
            self.objective = pulp.value(self.model.objective)
            print(f'      Status is optimal\n      Total objective value is {self.objective}')
            print(f'      White Average Distance {self.W_dist.varValue}')
            print(f'      Minority Average Distance {self.M_dist.varValue}')
            print(f'      Difference penalty {self.Dif.varValue}')
        # Get solution and append to object
        res = []
        try:
            for i,j in self.dm.index:
                res.append(self.X[(i,j)].varValue)
            self.dm['paired'] = res
        except:
            print('      Unable to append results')
    def clust_map(self, 
            border=None, 
            bord_kwargs={'color':'k','linewidth':3,'figsize':(12,12),'edgecolor':'k'}, 
            s_kwargs={'s':20,'marker':'o'}, 
            d_kwargs={'s':300,'marker':'s','edgecolor':'k'}):
        """
        Creating a simple map to show the assigned areas
        """
        # Pr is the source areas
        pr = self.dm[self.dm['paired'] == 1].copy()
        pr.reset_index(inplace=True)
        pr['dx'] = pr['xj'] - pr['xi'] # for arrows if you want
        pr['dy'] = pr['yj'] - pr['yi']
        # De_pr is the destination
        de_pr = pr.drop_duplicates(['xj','yj'])
        # If no border, generate fig, ax
        if border is None:
            fig, ax = plt.subplots(**bord_kwargs)
        else:
            ax = border.boundary.plot(**bord_kwargs)
        # No ticks on outside
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        # 
        for j in de_pr['idj']:
            prs = pr[pr['idj'] == j]
            des = de_pr[de_pr['idj'] == j]
            s_kwargs['label'] = j
            p = ax.scatter(prs['xi'], prs['yi'], **s_kwargs)
            d_kwargs['c'] = p.get_facecolor()
            ax.scatter(des['xj'], des['yj'], **d_kwargs)

# Create method to add into 
# matplotlib
# https://matplotlib.org/stable/gallery/text_labels_and_annotations/arrow_demo.html#sphx-glr-gallery-text-labels-and-annotations-arrow-demo-py

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