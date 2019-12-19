####################################################
#See https://andrewpwheeler.com/2019/09/27/optimal-treatment-assignment-with-network-spillovers/

import pulp
import networkx

Nodes = ['a','b','c','d','e']
Edges = [('a','c'),
         ('a','d'),
		 ('a','e'),
		 ('b','e')]

p_l = {'a': 0.4, 'b': 0.5, 'c': 0.1, 'd': 0.1,'e': 0.2}
p_s = {'a': 0.2, 'b': 0.25, 'c': 0.05, 'd': 0.05,'e': 0.1}
K = 1

G = networkx.Graph()
G.add_edges_from(Edges)

P = pulp.LpProblem("Choosing Network Intervention", pulp.LpMaximize)
L = pulp.LpVariable.dicts("Treated Units", [i for i in Nodes], lowBound=0, upBound=1, cat=pulp.LpInteger)
S = pulp.LpVariable.dicts("Spillover Units", [i for i in Nodes], lowBound=0, upBound=1, cat=pulp.LpInteger)

P += pulp.lpSum( p_l[i]*L[i] + p_s[i]*S[i] for i in Nodes)
P += pulp.lpSum( L[i] for i in Nodes ) == 1

for i in Nodes:
    P += pulp.lpSum( S[i] ) <= 1 + -1*L[i]
    
for i in Nodes:
    ne = G.neighbors(i)
    P += pulp.lpSum( L[j] for j in ne  ) >= S[i]

#print(P)		
P.solve()

#Should select e for local, and a & b for spillover
print(pulp.value(P.objective))
print(pulp.LpStatus[P.status])

for n in Nodes:
	print([n,L[n].varValue,S[n].varValue])
####################################################
    
    
def sel_nodes(Graph, prob_l, prob_s, k):
    N = Graph.nodes()
    Pr = pulp.LpProblem("Choosing Network Intervention", pulp.LpMaximize)
    L = pulp.LpVariable.dicts("Treated Units", [i for i in N], lowBound=0, upBound=1, cat=pulp.LpInteger)
    S = pulp.LpVariable.dicts("Spillover Units", [i for i in N], lowBound=0, upBound=1, cat=pulp.LpInteger)
    Pr += pulp.lpSum( prob_l[i]*L[i] + prob_s[i]*S[i] for i in N)
    Pr += pulp.lpSum( L[i] for i in N ) == k
    for i in N:
        #If node assigned, no spill-over
        Pr += pulp.lpSum( S[i] ) <= 1 + -1*L[i]
        #Neighbors spillover effect
        ne = list(Graph.neighbors(i))
        if len(ne) > 0:
            Pr += pulp.lpSum( L[j] for j in ne  ) >= S[i]
        else:
            Pr += pulp.lpSum( S[i] ) == 0
    Pr.solve() #I have a hard time passing in solvers, Pr.solve(pulp.CPLEX()) if you want CPLEX
    sol = pulp.value(Pr.objective)
    stat = pulp.LpStatus[Pr.status]
    te = "Stats is %s, the total reduced crime estimate is %f when select %d people to treat" % (stat,sol,k)
    print(te)
    res = []
    for n in N:
        res.append((n, L[n].varValue, L[n].varValue*prob_l[n], S[n].varValue, S[n].varValue*prob_s[n]))
    return(res)
    
choose_1 = sel_nodes(Graph=G,prob_l=p_l,prob_s=p_s,k=1)
print(choose_1)

#For an example with a larger network

import csv

#simple function to read in csv files
def ReadCSV(loc):
    tup = []
    with open(loc) as f:
        z = csv.reader(f)
        for row in z:
            tup.append(tuple(row))
    return tup
#First row will be header

#General function to export nested tuples to csv
def ExpCSV(loc,head,data):
    with open(loc, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(head)
        for line in data:
            writer.writerow(line)
            
file_loc = r'C:\Users\axw161530\Dropbox\Documents\BLOG\Treatment_NetworkSpillover\Analysis'

##############
#This network data comes from https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0119309
#Rostami, A., & Mondani, H. (2015). The complexity of crime network data: A case study of its consequences for crime control and the study of networks. 
#PloS one, 10(3), e0119309.
#https://figshare.com/articles/Network_complexity_data/1297161
#Specifically, it is the COOnet_Pers.net network with 311 nodes
#I then simulated some baseline probabilities
##############

#Read in nodes
node_data = ReadCSV(file_loc + r'\Nodes.csv')
node_names = node_data.pop(0)

#Read in edges
edge_data = ReadCSV(file_loc + r'\Edges.csv')
edge_names = edge_data.pop(0)

#Create graph from edges (this will eliminate any isolates)
print(len(node_data))
ExpGraph = networkx.Graph()
for i in edge_data:
    ExpGraph.add_edge(i[0],i[1],weight=i[2])
print(ExpGraph.number_of_nodes())
#So we have a few isolates that are not included
all_nodes = []
for i in node_data:
	all_nodes.append(i[0])
	
dif_nodes = set(all_nodes) - set(ExpGraph.nodes())
for i in dif_nodes:
	ExpGraph.add_node(i)
print(ExpGraph.number_of_nodes())

#Calculate reduction due to local effect and spillover (from baseline prob)
loc_eff = {}
spi_eff = {}
for i in node_data:
    loc_eff[i[0]] = float(i[7])*0.5
    spi_eff[i[0]] = float(i[7])*0.2
    
#Do function for selecting k=20 folks
big_res = sel_nodes(Graph=ExpGraph, prob_l=loc_eff, prob_s=spi_eff, k=20)
ExpCSV(loc=file_loc + r'\TreatedNodes_k20.csv',head=['id','treat','te','spill','se'],data=big_res)

#Ive buggered up my python so bad I cant use Matplotlib (hence the R script)
#This should hopefully work though!

#Now draw a nice graph, showing treated and spillovers
my_cols = []
my_size = []
my_shape = []
for i in big_res:
    orig_prob = loc_eff[i[0]]*2
    my_size.append(orig_prob*400)
    if i[1] == 1:
        my_cols.append('red')
        my_shape.append('s')
    elif i[3] == 1:
        my_cols.append('pink')
        my_shape.append('o')
    else:
        my_cols.append('grey')
        my_shape.append('o')
    
networkx.draw_networkx(G=ExpGraph,with_labels=False,node_size=my_size,node_color=my_cols,node_shape=my_shape)



        