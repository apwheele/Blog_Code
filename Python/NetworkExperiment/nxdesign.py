"""
This code generates different
potential network interventions

Andy Wheeler
"""

import pulp
import networkx
import pandas as pd
from matplotlib import pyplot as plt


class netDesign():
    def __init__(self,network):
        k = 1
        self.network = network
        self.pos = None
        self.nodes = list(network.nodes())
        self.edges = [(a,b) for a,b in network.edges()] + [(b,a) for a,b in network.edges()]
        self.problem = pulp.LpProblem("NetworkExperiment", pulp.LpMaximize)
        # Decision vars
        self.treated = pulp.LpVariable.dicts("T",[i for i in self.nodes],
                            lowBound=0, upBound=1, cat=pulp.LpInteger)
        self.leftover = pulp.LpVariable.dicts("L",[i for i in self.nodes],
                             lowBound=0, upBound=1, cat=pulp.LpInteger)
        self.spillover = pulp.LpVariable.dicts("S",[i for i in self.nodes],
                              lowBound=0, upBound=1, cat=pulp.LpInteger)
        self.edge = pulp.LpVariable.dicts("E",[(a,b) for a,b in self.edges],
                              lowBound=0, upBound=1, cat=pulp.LpInteger)
        # Objective maximize spillover
        self.problem += pulp.lpSum(self.spillover[i] for i in self.nodes)
        # Constraint 1, number treated selected
        self.problem += pulp.lpSum(self.treated[i] for i in self.nodes) == 1, "Treat_Select"
        # Constraint 2, set limit on number not treated or spillover
        self.problem += pulp.lpSum(self.leftover[i] for i in self.nodes) >= len(self.nodes) - k, "Leftover"
        # Constraint 3, each type is mutually exclusive
        for i in self.nodes:
            self.problem += pulp.lpSum(self.leftover[i]) <= 1 + -1*self.treated[i]
            self.problem += pulp.lpSum(self.leftover[i]) <= 1 + -1*self.spillover[i]
            self.problem += pulp.lpSum(self.spillover[i]) <= 1 + -1*self.treated[i]
            self.problem += pulp.lpSum(self.spillover[i] + self.treated[i] + self.leftover[i]) == 1
        # If T is selected Edge is turned on
        for i in self.nodes:
            ne = self.network.neighbors(i)
            for n in ne:
                self.problem += self.edge[(i,n)] == self.treated[i]
                self.problem += self.spillover[i] >= self.edge[(n,i)]
        # If no edges are selected, S needs to be 0
        for i in self.nodes:
            ne = self.network.neighbors(i)
            if ne:
                self.problem += self.spillover[i] <= pulp.lpSum(self.edge[(n,i)] for n in ne)
        # data structure to hold the results
        self.data = {}
    def add_data(self,j,k,i,optimal=True):
        if optimal is False:
            self.data[(j,k,i)] = {'optimal': False, 'assign': None, 'leftover': None, 'spillover': None}
            return None
        # creating the dataframe of results
        res = []
        for n in self.nodes:
            res.append([n,self.treated[n].varValue,self.spillover[n].varValue,self.leftover[n].varValue])
        df = pd.DataFrame(res,columns=['Node','Treated','Spillover','Leftover'])
        df[['Treated','Spillover','Leftover']] = df[['Treated','Spillover','Leftover']].astype(int)
        self.data[(j,k,i)] = {'optimal': True, 'assign': df, 'leftover': df['Leftover'].sum(), 'spillover': df['Spillover'].sum()}
    def solve(self,j,k,solver=None):
        # if solution already exists, don't run
        if (j,k,0) in self.data:
            return None
        # removing the em constraint and extra objective if it exists
        if 'OBJ' in self.problem.constraints:
            self.problem.constraints.pop('OBJ')
        # redoing the k/j constraints
        self.problem.constraints.pop('Treat_Select')
        self.problem += pulp.lpSum(self.treated[i] for i in self.nodes) == k, "Treat_Select"
        self.problem.constraints.pop('Leftover')
        self.problem += pulp.lpSum(self.leftover[i] for i in self.nodes) >= j, "Leftover"
        # Trying to solve at least once
        self.problem.solve(solver)
        stat = pulp.LpStatus[self.problem.status]
        if stat == "Optimal":
            self.add_data(j,k,0)
        else:
            self.add_data(j,k,0,optimal=False)
    def solve_extra(self,j,k,e=10,solver=None):
        extra_n = 1
        # redoing the k/j constraints
        self.problem.constraints.pop('Treat_Select')
        self.problem += pulp.lpSum(self.treated[i] for i in self.nodes) == k, "Treat_Select"
        self.problem.constraints.pop('Leftover')
        self.problem += pulp.lpSum(self.leftover[i] for i in self.nodes) >= j, "Leftover"
        # now iterating and generating potential alternatives
        if (j,k,0) in self.data:
            obj_val = self.data[(j,k,0)]['spillover']
        else:
            self.solve(j,k,solver=solver)
            stat = pulp.LpStatus[self.problem.status]
            if stat != "Optimal":
                return None
            else:
                obj_val = self.data[(j,k,0)]['spillover']
        if 'OBJ' in self.problem.constraints:
            self.problem.constraints.pop('OBJ')
        self.problem += pulp.lpSum(self.spillover[i] for i in self.nodes) >= obj_val, "OBJ"
        ex_con = []
        while extra_n < e:
            # restricting the set
            elab = f"OBJ_{extra_n}"
            if extra_n == 1:
                dat = self.data[(j,k,0)]['assign']
                treat_lab = dat[dat['Treated'] == 1]['Node']
                self.problem += pulp.lpSum(self.treated[i] for i in treat_lab) <= k-1, elab
            else:
                self.problem += pulp.lpSum(self.treated[i] for i in self.nodes if self.treated[i].varValue == 1) <= k-1, elab
            ex_con.append(elab)
            self.problem.solve(solver)
            stat = pulp.LpStatus[self.problem.status]
            if stat == "Optimal":
                self.add_data(j,k,extra_n)
                extra_n += 1
            else:
                break
        # now removing the objective and extra constraints
        if 'OBJ' in self.problem.constraints:
            self.problem.constraints.pop('OBJ')
        for el in ex_con:
            if el in self.problem.constraints:
                self.problem.constraints.pop(el)
    # get optimal s, then vary to max j
    def solve_pareto(self,k,j_range=None,solver=None):
        # now I need to do this over a range of values
        if j_range is None:
            tot_nodes = len(self.nodes)
            jmap = list(range(0,tot_nodes-k+1))
        else:
            jmap = list(j_range)
        for j in jmap:
            self.solve(j,k,solver)
            stat = pulp.LpStatus[self.problem.status]
            # soon as a not valid solution, this stops
            if stat != "Optimal":
                return None
    def solve_rangek(self,k_range,solver=None):
        for k in k_range:
            self.solve_pareto(k,solver=solver)
    def plot_network(self,sol,labels=True,
                     colors={'Treated': '#ca0020', 'Spillover': '#f4a582', 'Leftover': '#92c5de'},
                     sizes={'Treated': 300*2, 'Spillover': 230*2, 'Leftover': 260*2},
                     shapes={'Treated': 's', 'Spillover': 's', 'Leftover': 'o'},
                     ax=None,show=False,legend=False,save=None):
        if self.pos is None:
            self.pos = networkx.spring_layout(self.network)
        # get the data
        data = self.data[sol]['assign']
        data['color'] = data['Treated'] + data['Spillover']*2 + data['Leftover']*3
        rv = {1: 'Treated',2: 'Spillover',3: 'Leftover'}
        data['color'] = data['color'].replace(rv)
        #col_list = list(data['color'].replace(colors))
        for k,l in rv.items():
            subdata = data[data['color'] == l].copy()
            nl = subdata['Node']
            networkx.draw_networkx_nodes(G=self.network,pos=self.pos,ax=ax,nodelist=nl,label=l,
                                         node_size=sizes[l],node_color=colors[l],node_shape=shapes[l])
        #networkx.draw(self.network,pos=self.pos,ax=ax,with_labels=labels,node_color=col_list)
        networkx.draw_networkx_edges(self.network,self.pos,ax=ax)
        if labels:
            networkx.draw_networkx_labels(self.network,self.pos,ax=ax)
        if legend:
            if ax:
                lg = ax.legend()
                for h in lg.legendHandles:
                    h.set_sizes(h.get_sizes()/4)
            else:
                lg = plt.legend()
                for h in lg.legendHandles:
                    h.set_sizes(h.get_sizes()/4)
        if save:
            plt.savefig(save,dpi=500,bbox_inches='tight')
        elif show:
            plt.show()
    def pareto_graph(self,ax=None,show=False,legend=False,save=None):
        res = []
        for k,v in self.data.items():
            if (v['optimal']) & (k[2] == 0):
                dat = [k[0],k[1],v['leftover'],v['spillover']]
                res.append(dat)
        df = pd.DataFrame(res,columns=['LeftConstraint','Treated','Leftover','Spillover'])
        k_vals = pd.unique(df['Treated'])
        if ax is None:
            fig, ax = plt.subplots()
        for k in k_vals:
            subd = df[df['Treated'] == k].copy()
            ax.plot(subd['Leftover'],subd['Spillover'],linestyle='-', marker='o',label=k)
            ax.set_xlabel("Leftover")
            ax.set_ylabel("Spillover")
        if legend:
            ax.legend(title="Treated")
        if save:
            plt.savefig(save,dpi=500,bbox_inches='tight')
        elif show:
            plt.show()
        return df, ax