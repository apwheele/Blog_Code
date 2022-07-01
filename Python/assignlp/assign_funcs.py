'''
Functions to assign
locations

need to have CBC or CPLEX installed
e.g.

pip install cbcpy
pip install pulp

in that order
'''


from datetime import datetime
import numpy as np
import pulp
import pandas as pd


# Bisquare kernel, can take in scalars
# or numpy/pandas vectors
def bisquare(dist,thresh):
    dl = dist < thresh
    ra = (dist/thresh)**2
    wi = (1 - ra)**2
    return wi*dl


class ProvAssign():
    def __init__(self,people,pe_vars,prov,pr_vars,dist_thresh,dist_far):
        """
        Construct Model to assign people to providers
        
        people - dataframe people
        pe_vars - list of variables strings for people
                  [id,x,y,tot]
        prov - dataframe providers
        pr_vars - list of variable strings for providers
                  [id,x,y,capacity]
        dist_thresh - threshold distance to not assign
                      eliminates these pairs from model
        dist_far - max distance to assign for people
        
        dist_far should be >>> dist_thresh
        """
        # initializing a few things
        self.dist_thresh = dist_thresh
        self.dist_far = dist_far
        P = pulp.LpProblem("MinDist",pulp.LpMinimize)
        # creating the cross dataframe
        peop_df = people[pe_vars].reset_index(drop=True)
        peop_df.columns = ['id','px','py','tot']
        peop_df['const'] = 1
        prov_df = prov[pr_vars].reset_index(drop=True)
        prov_df.columns = ['hid','hx','hy','hc']
        prov_df['const'] = 1
        # Probably would be better to do KDTree
        # for now not worrying about memory
        cross1 = pd.merge(peop_df,prov_df,on='const')
        cross1['dist'] = np.sqrt( (cross1['px']-cross1['hx'])**2 + 
                                  (cross1['py']-cross1['hy'])**2 )
        cross1 = cross1[cross1['dist'] <= dist_thresh].copy()
        # Now adding in slack provider
        cvars = ['id','hid','dist','tot','hc']
        slack_df = peop_df.copy()
        slack_df['hid'] = 999999
        slack_df['dist'] = dist_far
        slack_df['hc'] = peop_df['tot'].sum()
        cross = pd.concat([cross1[cvars],slack_df[cvars]],axis=0)
        cross.set_index(['id','hid'],inplace=True)
        self.cross = cross
        self.peop_id = peop_df['id'].tolist()
        self.prov_id = prov_df['hid'].tolist() + [999999]
        # Now can add in variables
        max_val = int(prov_df['hc'].max())
        D = pulp.LpVariable.dicts("DA",cross.index.tolist(),
                          lowBound=0, upBound=max_val, cat=pulp.LpContinuous)
        # objective function
        P += pulp.lpSum(D[i]*cross.loc[i,'dist'] for i in cross.index)
        # constraint each person assigned
        for p in peop_df['id']:
            provl = cross.xs(p,0,drop_level=False)
            ptot = provl['tot'].iloc[0]  # sum for area should equal tot
            P += pulp.lpSum(D[i] for i in provl.index) == ptot, f"pers_{p}"
        # capacity constraint providers
        for h in prov_df['hid']:
            peopl = cross.xs(h,level=1,drop_level=False)
            pid = peopl.index
            cap = peopl['hc'].iloc[0] # should be a constant
            P += pulp.lpSum(D[i] for i in pid) <= cap, f"prov_{h}"
        # save model object
        self.model = P
        self.dvars = D
        # extra slots to add in after solve
        self.assign = None
        self.shadow = None
        self.obj = None
        self.source_stats = None
        self.dist_stats = None
        self.prov_stats = None
    def solve(self, solver=None):
        """
        For solver can either pass in None for default pulp, or various pulp solvers, e.g.
        solver = pulp.CPLEX()
        solver = pulp.CPLEX_CMD(msg=True, warmStart=True)
        solver = pulp.PULP_CBC_CMD(timeLimit=1000)
        solver = pulp.GLPK_CMD()
        etc.
        run print( pulp.listSolvers(onlyAvailable=True) )
        to see available solvers on your machine
        
        For slack/shadow, only I know of so far are CPLEX
        or CBC
        """
        #print(f'      Starting to solve function at {datetime.now()}')
        if solver == None:
            self.model.solve()
        else:
            self.model.solve(solver)
        #print(f'      Solve finished at {datetime.now()}')
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
            obj_value = pulp.value(self.model.objective)
            print(f"Status is optimal, objective value is {obj_value}")
            self.obj = obj_value
            # add in dataframe with assignments
            res_pick = []
            for ph in self.cross.index:
                res_pick.append(self.dvars[ph].varValue)
            cross = self.cross.copy()
            cross['picked'] = res_pick
            self.assign = cross[cross['picked'] > 0.0000001].copy()
            # Get the shadow constraints per provider
            o = [{'name':name, 'shadow price':c.pi, 'slack': c.slack} 
                 for name, c in self.model.constraints.items()]
            sc = pd.DataFrame(o)
            self.shadow = sc
            # Get the original location stats
            asl = self.assign.copy()
            asl.reset_index(inplace=True)
            asc = asl[asl['hid'] != 999999].copy()
            asc['Trav'] = asc['tot']
            asc['n'] = 1
            gloc = asc.groupby('id',as_index=False)[['Trav','picked','tot','n']].sum()
            gloc['Trav'] = gloc['Trav']/gloc['picked']
            gloc['tot'] = gloc['tot']/gloc['n']
            gloc['NotCovered'] = gloc['tot'] - gloc['picked']
            self.source_stats = gloc[['id','Trav','picked','tot','NotCovered']]
            # Get stats for providers that have extra coverage nearby as
            # as well as slack
            nsource = len(self.peop_id)
            shad_prov = sc.loc[nsource:,].reset_index(drop=True)
            shad_prov['hid'] = self.prov_id[:-1]
            cr = self.cross.reset_index()
            cr = cr[cr['hid'] != 999999].copy()
            cr_ws = pd.merge(cr,gloc,on='id')
            cr_ws = cr_ws[cr_ws['NotCovered'] > 0].copy()
            cr_ws['Trav'] = cr_ws['dist']*cr_ws['NotCovered']
            bsw = bisquare(cr_ws['dist'],self.dist_thresh)
            cr_ws['bisqw'] = bsw*cr_ws['NotCovered']
            cr_ws['n'] = 1
            self.dist_stats = cr_ws[['id','hid','dist','bisqw','NotCovered']]
            crv = ['hc','Trav','n','bisqw','NotCovered']
            hid_gb = cr_ws.groupby('hid',as_index=False)[crv].sum()
            hid_gb['hid'] = hid_gb['hid']/hid_gb['n']
            hid_gb['Trav'] = hid_gb['Trav']/hid_gb['n']
            mhid = pd.merge(hid_gb,shad_prov,on='hid')
            self.prov_stats = mhid[['hid','hc','Trav','bisqw','NotCovered','shadow price']]
    def distprov(self,dist_thresh):
        # Maybe want to do this via kernel density/weights
        ds = self.dist_stats[self.dist_stats['dist'] <= dist_thresh]
        dsg = ds.groupby('hid',as_index=False)['NotCovered'].sum()
        return dsg
