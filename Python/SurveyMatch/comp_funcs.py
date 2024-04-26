'''
Comparison functions
'''

import numpy as np
from scipy.optimize import minimize
from scipy.stats import betabinom
from scipy.stats import norm
import matplotlib.pyplot as plt
import itertools
import networkx as nx

def sim_data(n,props):
    res = []
    for p in props:
        r = np.random.choice(range(len(p)),size=(n,1),p=p)
        res.append(r)
    return np.concatenate(res,axis=1)

def match_probs(data):
    res = []
    n = data.shape[0]
    for c in range(data.shape[1]):
        un, co = np.unique(data[:,c], return_counts=True)
        nv = ((co/n)**2).sum()
        res.append(nv)
    return res

def ret_ids(n,rej):
    nids = np.array(list(itertools.combinations(range(n),2)))
    return nids[rej]

def compare(data):
    n = data.shape[0]
    res_match = []
    for r in range(n-1):
        cumm = (data[r,] == data[(r+1):,]).sum(axis=1)
        res_match.append(cumm)
    return np.concatenate(res_match,axis=0)

def compare_data(data):
    n = data.shape[0]
    res_match = []
    for r in range(n-1):
        cumm = (data[r,] == data[(r+1):,])
        res_match.append(cumm)
    return np.concatenate(res_match,axis=0)


# These should be very close to 0
def corr_compare(data):
    n = data.shape[0]
    res_match = []
    for r in range(n-1):
        cumm = data[r,] == data[(r+1):,]
        res_match.append(cumm)
    res_mat = np.concatenate(res_match,axis=0)
    return np.corrcoef(res_mat.T)

def cov_compare(data):
    n = data.shape[0]
    res_match = []
    for r in range(n-1):
        cumm = data[r,] == data[(r+1):,]
        res_match.append(cumm)
    res_mat = np.concatenate(res_match,axis=0)
    return np.cov(res_mat.T)

# Method of Moments estimate for beta-binomial
# https://en.wikipedia.org/wiki/Beta-binomial_distribution
def bb_mom(data,n):
    m1 = data.mean()
    m2 = (data**2).mean()
    d = n*(m2/m1 - m1 - 1) + m1
    alpha = (n*m1 - m2)/d
    beta = ((n - m1)*(n - m2/m1))/d
    if (alpha < 0) | (beta < 0):
        print('Underdispersed, returning normal approximation')
        bmod = norm(m1,data.std())
    else:
        bmod = betabinom(n, alpha, beta)
    return bmod

# MoM is bad so I am using log likelihood here
# https://andrewpwheeler.com/2023/10/18/fitting-beta-binomial-in-python-poisson-scan-stat-in-r/
def bbll(parms,k,n):
    alpha, beta = parms
    ll = betabinom.logpmf(k,n,alpha,beta)
    return -ll.sum()

def bb_ml(data,n):
    result = minimize(bbll,[1,1],args=(data,n),method='Nelder-Mead')
    alpha, beta = result.x
    return betabinom(n,alpha,beta)



# Function to look at pred vs observed
def pred_obs(comp,pbin,n,tail=None):
    cmin, cmax = comp.min(), comp.max()
    pbot, ptop = max(np.floor(cmin*0.95),0), min(np.ceil(cmax*1.05),n)
    x = np.arange(int(pbot),int(ptop+1))
    if tail:
        x = x[-tail:]
    obs = np.array([(comp == xv).mean() for xv in x])
    try:
        pmf = pbin.pmf(x)
    except:
        pmf = pbin.cdf(x+0.5) - pbin.cdf(x-0.5)
        #pmf = pmf/pmf.sum()
        #pmf = pbin.pdf(x)
    return x, obs, pmf


def fit_plot(comp,pbin,n,tail=None):
    x, obs, pmf = pred_obs(comp,pbin,n,tail)
    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(x,obs,color='grey',width=0.95)
    ax.plot(x,pmf,color='k',linewidth=2)
    plt.show()


# Connected components for groups
# of similar observations
def conn_comp(pairs):
    G = nx.Graph()
    G.add_edges_from(pairs.tolist())
    connect = nx.connected_components(G)
    cc = [list(i) for i in connect]
    return cc