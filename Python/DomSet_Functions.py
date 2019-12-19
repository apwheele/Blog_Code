#These are various functions I created to create the dominent set, plus other
#Factors in the analyses, only special library is networkx
#See https://andrewpwheeler.com/2019/07/05/finding-the-dominant-set-in-a-network-python/

import itertools
import networkx as nx

#################################################################################
#GRID SEARCH FOR DOMINATING SET

#checks to see if a dominating set exists for all combinations
#up to length r, returns a nested list of all the dominant sets among
#the minimum r that is found, if dominant not found will return an empty list
#note total number of combinations is [nodes choose i], so will be quite large
#example, 25 choose 7 is 480,700

#G is graph, searches only min to max potential sets
def domCheck(G,max,min=1):
  fin = []
  nod = nx.nodes(G)
  for i in range(min,max+1):
    if not fin:
      co = itertools.combinations(nod,i)
      for j in co:
        if nx.is_dominating_set(G,j):
          fin.append(j)
    else:
      break
  return fin 

###This function stops when the first dominating set is found
#G is graph, searches only min to max potential sets
def domCheckFirst(G,max,min=1):
  nod = nx.nodes(G)
  for i in range(min,max+1):
    co = itertools.combinations(nod,i)
    for j in co:
      if nx.is_dominating_set(G,j):
        return j
        break
  return None

def domCheckFirst2(G,max,min=1):
  nod = nx.nodes(G)
  for i in range(min,max+1):
    co = itertools.combinations(nod,i)
    for j in co:
      if nx.is_dominating_set(G,j):
        return len(j)
        break
  return None
#################################################################################

#################################################################################
#REACH of a set of nodes - number of other elements that are first degree neighbors 
#Includes nodes that are in nbunch
def ReachNodes(G,nbunch):
  re = nx.edges(G,nbunch)
  me = list(itertools.chain(*re))
  fl = set(nbunch) | set(me)  
  #fl = set(me) - set(nbunch)  #if you dont want to include nodes in nbunch
  return len(fl)

def reached_nodes(G,nbunch):
  re = nx.edges(G,nbunch)
  me = list(itertools.chain(*re))
  fl = set(nbunch) | set(me)  
  return fl

#given a sorted list, returns a list of the cumulative reach
def SucReach(G,node_order):
  res_N = []
  for i in range(len(node_order)):
    cumR = ReachNodes(G,nbunch=node_order[0:i+1])
    res_N.append(cumR)
  return res_N  
#can plop this in a tuple with something like 
#type = ['sort type']*len(node_order)
#zip(node_order,res_N,type)
#and then put in a pandas dataframe
#################################################################################

#################################################################################
#ALGORITHM TO IDENTIFY DOMINANT SETS

###########################################
#These are subfunctions used
#Identifies the node with the max degree
def MaxDeg(G):
  vals = nx.degree_centrality(G).items()
  max_val = max(nx.degree_centrality(G).values()) 
  all_max = [i[0] for i in vals if i[1] == max_val]  
  return all_max  
#Function needs to distinguish among ties by decreases in set
#First one with the max new set wins
def DegTieBreak(G,neighSet,nbunch):
    maxN = -1
    for i in nbunch:
        neigh_cur = set(G[i].keys())
        dif = (neigh_cur | set([i]) ) - neighSet
        te = len(dif)
        if te > maxN:
            myL = [i,neigh_cur,dif]
            maxN = te
    return myL
###########################################

#This function implements my algorithm for searching the graph
#G is network x graph object, total is number of iterations to search (if none searches until)
#dominant set is found
def domSet_Whe(G,total=None):
    uG = G.copy() #make a deepcopy of the orig graph to update for the algorithm
    domSet = []      #list to place dominant set
    neighSet = set([])    #list of neighbors to dominating set   
    if not total:
        loop_num = len(nx.nodes(G)) #total is the set maximum number of loops for graph
    else:                           #default as many nodes in graph               
        loop_num = total            #can also set a lower limit though
    for i in range(loop_num):     
        nodes_sel = MaxDeg(uG)   #select nodes from updated graph with max degree centrality
        #chooses among degree ties with the maximum set of new neighbors
        if len(nodes_sel) > 1:
            temp = DegTieBreak(G=uG,neighSet=neighSet,nbunch=nodes_sel)
            node_sel = temp[0]
            neigh_cur = temp[1]
            newR = temp[2]
        else:
            node_sel = nodes_sel[0]
            neigh_cur = set(uG[node_sel].keys()) #neighbors of the current node
            newR = neigh_cur - neighSet          #new neighbors added in
        domSet.append(node_sel) #append that node to domSet list
        #break loop if dominant set found, else decrement counter
        if nx.is_dominating_set(G,domSet):
            break
        #should only bother to do this junk if dominant set has not been found!
        uG.remove_node(node_sel)  #remove node from updated graph
        #now this part does two loops to remove the edges between reached nodes
        #one for all pairwise combinations of the new reached nodes, the second
        #for the product of all new reached nodes compared to prior reached nodes
        #new nodes that have been reached
        for i in itertools.combinations(newR,2):
            if uG.has_edge(*i):
                uG.remove_edge(*i)       
        #product of new nodes and old neighbor set
        #this loop could be pretty costly in big networks, consider dropping
        #should not make much of a difference
        for j in itertools.product(newR,neighSet):
            if uG.has_edge(*j):
                uG.remove_edge(*j)
        #now update the neighSet to include newnodes, but strip nodes that are in the dom set
        #since they are pruned from graph, all of their edges are gone as well
        neighSet = (newR | neighSet) - set(domSet)
    return domSet

#alternate where pruning nodes that have the most remainder in the graph instead of choosing by maximum degree
def domSet_Whe2(G):
    uG = G.copy() #make a deepcopy of the orig graph to update for the algorithm
    domSet = []      #list to place dominant set
    neighSet = set([])    #list of neighbors to dominating set   
    fullNodes = set(nx.nodes(G))
    while nx.is_dominating_set(G,domSet) == False:    #?can also set a max number of loops for large graphs?
        rem_nodes = fullNodes - neighSet - set(domSet)
        temp = DegTieBreak(G=uG,neighSet=neighSet,nbunch=rem_nodes)
        node_sel = temp[0]
        neigh_cur = temp[1]
        newR = temp[2]   
        domSet.append(node_sel) #append that node to domSet list
        uG.remove_node(node_sel)  #remove node from updated graph
        #now update the neighSet to include newnodes, pruning edges not necessary
        neighSet = neigh_cur | neighSet
    return domSet
#################################################################################


#########################################################################################
#function with a restricted set of matches (eg return only those under supervision)
#only need to update subfunctions MaxDeg, just supply onlyLook with a list
#returns in the best order again
def domSet_WheSub(G,onlyLook,total=None):
    uG = G.copy() #make a deepcopy of the orig graph to update for the algorithm
    domSet = []      #list to place dominant set
    neighSet = set([])    #list of neighbors to dominating set   
    if not total:
        loop_num = len(onlyLook) #total is the set maximum number of loops for graph
    else:                        #default as many nodes in graph               
        loop_num = total         #can also set a lower limit though
    for i in range(loop_num):     
        nodes_sel = MaxDegSub(G=uG,onlyLook=onlyLook)   #select nodes from updated graph with max degree centrality
        #chooses among degree ties with the maximum set of new neighbors
        if len(nodes_sel) > 1:
            temp = DegTieBreak(G=uG,neighSet=neighSet,nbunch=nodes_sel)
            node_sel = temp[0]
            neigh_cur = temp[1]
            newR = temp[2]
        else:
            node_sel = nodes_sel[0]
            neigh_cur = set(uG[node_sel].keys()) #neighbors of the current node
            newR = neigh_cur - neighSet          #new neighbors added in
        domSet.append(node_sel) #append that node to domSet list
        #break loop if dominant set found, else decrement counter
        if nx.is_dominating_set(G,domSet):
            break
        #should only bother to do this junk if dominant set has not been found!
        uG.remove_node(node_sel)  #remove node from updated graph
        #now this part does two loops to remove the edges between reached nodes
        #one for all pairwise combinations of the new reached nodes, the second
        #for the product of all new reached nodes compared to prior reached nodes
        #new nodes that have been reached
        for i in itertools.combinations(newR,2):
            if uG.has_edge(*i):
                uG.remove_edge(*i)       
        #product of new nodes and old neighbor set
        #this loop could be pretty costly in big networks, consider dropping
        #should not make much of a difference
        for j in itertools.product(newR,neighSet):
            if uG.has_edge(*j):
                uG.remove_edge(*j)
        #now update the neighSet to include newnodes, but strip nodes that are in the dom set
        #since they are pruned from graph, all of their edges are gone as well
        neighSet = (newR | neighSet) - set(domSet)
    return domSet

###########################################
#These are subfunctions used
#Identifies the node with the max degree
def MaxDegSub(G,onlyLook):
  vals = nx.degree_centrality(G).items()
  #strip items that are not in onlyLook
  valsSub = [i for i in vals if i[0] in onlyLook]
  valsOnly = [i[1] for i in valsSub]
  max_val = max(valsOnly)
  all_max = [i[0] for i in valsSub if i[1] == max_val]  
  return all_max  
#Function needs to distinguish among ties by decreases in set
#First one with the max new set wins, this is the same as prior
#def DegTieBreak(G,neighSet,nbunch):
#   maxN = -1
#   for i in nbunch:
#       neigh_cur = set(G[i].keys())
#       dif = (neigh_cur | set([i]) ) - neighSet
#       te = len(dif)
#       if te > maxN:
#           myL = [i,neigh_cur,dif]
#           maxN = te
#   return myL
###########################################
#########################################################################################


#################################################################################
#This function simulates a graph with the same expected degree as the observed
#graph G (with no self loops, for the number of simulations = sim
#this fixes the seed to be 1 to sim

def SimExpDeg(G,sim):
    res = []
    deg_to_sim = [i[1] for i in G.degree_iter()]
    for j in range(1,sim+1):
        Gtemp = nx.expected_degree_graph(w=deg_to_sim, seed=j, selfloops=False) #maybe try ?nx.powerlaw_cluster_graph()?
        Whe1 = domSet_Whe(G=Gtemp)
        Whe2 = domSet_Whe2(G=Gtemp)
        MinMy = min([len(Whe1),len(Whe2)])
        #This searches 2 below, then if 2 below is found searches 4 below
        MinSet = domCheckFirst2(G=Gtemp,max=MinMy-1,min=MinMy-2)
        if MinSet == None:
            MinSet = MinMy
        elif MinSet == (MinMy-2):
            MinSet2 = domCheckFirst(G=Gtemp,max=MinMy-3,min=MinMy-4)
            if MinSet2 != None:
                MinSet = MinSet2
        res.append([j,len(Whe1),len(Whe2),MinSet])
    return res

#returns a nested list of
#[seed,set length Algo 1,set length Algo 2, minimal set length]

#This is for if you dont want to check the minimal set
def SimExpDeg2(G,sim):
    res = []
    deg_to_sim = [i[1] for i in G.degree_iter()]
    for j in range(1,sim+1):
        Gtemp = nx.expected_degree_graph(w=deg_to_sim, seed=j, selfloops=False) #maybe try ?nx.powerlaw_cluster_graph()?
        Whe1 = domSet_Whe(G=Gtemp)
        Whe2 = domSet_Whe2(G=Gtemp)
        MinMy = min([len(Whe1),len(Whe2)])
        MinSet = MinMy
        res.append([j,len(Whe1),len(Whe2),MinSet])
    return res
#################################################################################

#################################################################################
#This function calculates the expected reach of the gang given probable call-ins and 
#A fixed set based on all potential permutations
def ExpReach(G,underSuper,notSuper,show_up_prob=1/float(6)):
  expected_reach = float(0)
  tot_prob = float(0)
  show_perm = itertools.product([0,1],repeat=len(notSuper))
  for i in show_perm:
    node_look = []
    node_look = node_look + underSuper
    prob = float(1)
    for a,b in zip(notSuper,i):
      if b == 1:
        node_look.append(a)
        prob = prob*show_up_prob
      else:
        prob = prob*(1-show_up_prob)
    totR = ReachNodes(G=G,nbunch=node_look)
    tot_prob += prob
    expected_reach += totR*prob
    #print prob, tot_prob, totR, expected_reach, node_look, i
  return expected_reach
#################################################################################