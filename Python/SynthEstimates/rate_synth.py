'''
Rate synth!

Note these are not working at the moment
I need to do a different solver, maybe ipopt
or pytorch/adam may be worth a try

Leaving here as notes though for others
'''

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.optimize import NonlinearConstraint, LinearConstraint

# My hacky solution for synth with rates
class MinRatio:
    def __init__(self,lmb=1.0,var_penal=0.0):
        self.beta = None
        self.sol = None
        self.lmb = lmb
        self.var_penal = var_penal
    def fit(self,Xnum,Xden,ynum,yden,iters=1e6,disp=True,seed=10):
        coef_n = Xnum.shape[1]
        if self.beta is None:
            # default is equal weight
            np.random.seed(seed)
            self.beta = np.ones(coef_n)/coef_n
            #self.beta = np.random.rand(coef_n)
            #self.beta = self.beta/self.beta.sum()
        yrat = ynum/yden
        xrat = Xnum/Xden
        xvar = (xrat*(1 - xrat))/Xden
        def pred(x):
            return (x*xrat).sum(axis=1)
        def loss(x):
            predv = pred(x)
            sq_loss = (yrat - predv)**2
            # soft penalty for variance
            var_loss = (x*xvar).sum(axis=1)
            # soft penalty for not summing to 1
            # this assumes coefficients already constrained 0/1
            lmb_loss = self.lmb*abs(sum(x) - 1)
            return sq_loss.sum() + lmb_loss + self.var_penal*var_loss.sum()
        # This is for trust-constr, did not work great
        def constraints(x):
            r1 = x.sum() - 1.0 # sum to 1
            # np.append([r1],x)
            return np.array([r1])
        low = np.zeros(1)
        hig = np.array([0.0])
        nlc = NonlinearConstraint(constraints,low,hig) #method='trust-constr'
        # adding in lower/upper bounds
        bounds = [(0.0,1.0) for _ in range(coef_n)]
        # I also triend const for COBLYA solver, faster but still just
        # as flaky for my formulation
        const = [{'type': 'ineq', 'fun': lambda x: 1 - sum(x)}]
        for i in range(coef_n):
            l = {'type': 'ineq', 'fun': lambda x: x[i]}
            const.append(l)
        self.sol = minimize(loss,self.beta,method='Nelder-Mead',
                            bounds=bounds,
                            options={'maxiter':iters,
                                     'disp':disp})
        self.beta = self.sol.x
    def pred(self,Xnum,Xden):
        tn = self.beta*(Xnum/Xden)
        return tn.sum(axis=1)


ynum = np.array([10,20])
yden = np.array([1000,2000])

Xnum = np.array([[5,30],
                 [10,60]])

Xden = np.array([[200,4200],
                 [400,8400]])

synth_rate = MinRatio()
synth_rate.fit(Xnum,Xden,ynum,yden)
synth_rate.beta 
synth_rate.pred(Xnum,Xden) # This returns acceptably close predictions

# Lets do a more severe test



# Lets run it on the homicide data
# check out the results

hom = pd.read_csv('PrepUCR.csv')


phil = hom[hom['Philly'] == 1].reset_index()
hom_wide = hom[hom['Philly'] == 0].pivot(index='city',columns='year',values=['hom','population'])

pre_years = list(range(2000,2015))
post_years = list(range(2015,2020))

Hnum = hom_wide['hom'][pre_years].T
Hden = hom_wide['population'][pre_years].T
yhn = phil['hom']
yhd = phil['population']

synth_hom = MinRatio(lmb=0.0)
synth_hom.fit(Hnum,Hden,yhn,yhd)
pd.DataFrame(zip(hom_wide.index,synth_hom.beta), columns=['City','Weight'])




######################

# Initial failed attempt estimating weighted sum

class MinRatio:
    def __init__(self,lmb=1.0,seed=10):
        self.beta = None
        self.sol = None
        self.lmb = lmb
        self.seed = seed
    def fit(self,Xnum,Xden,ynum,yden,iters=1e6,disp=True):
        coef_n = Xnum.shape[1]
        if self.beta is None:
            # default is equal weight
            np.random.seed(self.seed)
            self.beta = np.ones(coef_n)/coef_n
            #self.beta = np.random.rand(coef_n)
            #self.beta = self.beta/self.beta.sum()
        yrat = ynum/yden
        def pred(x):
            tn = x*Xnum
            td = x*Xden
            return tn.sum(axis=1)/td.sum(axis=1)
        def loss(x):
            predv = pred(x)
            sq_loss = (yrat - predv)**2
            # soft penalty for not summing to 1
            lmb_loss = self.lmb*abs(sum(x) - 1)
            return sq_loss.sum() + lmb_loss
        # This is for trust-constr, did not work great
        def constraints(x):
            r1 = x.sum() - 1.0 # sum to 1
            # np.append([r1],x)
            return np.array([r1])
        low = np.zeros(1)
        hig = np.array([0.0])
        nlc = NonlinearConstraint(constraints,low,hig) #method='trust-constr'
        # adding in lower/upper bounds
        bounds = [(0.0,1.0) for _ in range(coef_n)]
        # I also triend const for COBLYA solver, faster but still just
        # as flaky for my formulation
        const = [{'type': 'ineq', 'fun': lambda x: 1 - sum(x)}]
        for i in range(coef_n):
            l = {'type': 'ineq', 'fun': lambda x: x[i]}
            const.append(l)
        self.sol = minimize(loss,self.beta,method='SLSQP',
                            bounds=bounds,
                            options={'maxiter':iters,
                                     'disp':disp})
        self.beta = self.sol.x
    def pred(self,Xnum,Xden):
        tn = self.beta*Xnum
        td = self.beta*Xden
        return tn.sum(axis=1)/td.sum(axis=1)
