'''
Functions for using Lasso 
with Synthetic control
'''


import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mapie.regression import MapieRegressor
from sklearn.linear_model import Lasso, LassoCV

# matplotlib theme
andy_theme = {'axes.grid': True,
              'grid.linestyle': '--',
              'legend.framealpha': 1,
              'legend.facecolor': 'white',
              'legend.shadow': True,
              'legend.fontsize': 14,
              'legend.title_fontsize': 16,
              'xtick.labelsize': 14,
              'ytick.labelsize': 14,
              'axes.labelsize': 16,
              'axes.titlesize': 20,
              'figure.dpi': 100}

matplotlib.rcParams.update(andy_theme)

# Can pass these to legend
def combo_legend(ax):
    handler, labeler = ax.get_legend_handles_labels()
    hd = []
    labli = list(set(labeler))
    for lab in labli:
        comb = [h for h,l in zip(handler,labeler) if l == lab]
        hd.append(tuple(comb))
    return hd, labli


def prep_longdata(data,timeperiod,outcome,groups):
    # sort by groups, timeperiod
    d2 = data[[timeperiod,outcome,groups]].reset_index(drop=True)
    d2.sort_values(by=[groups,timeperiod],inplace=True)
    d2[timeperiod] = d2.groupby(groups)[timeperiod].rank(method='first').astype(int)
    d2 = pd.pivot(d2,index=timeperiod,columns=groups,values=outcome).reset_index(drop=True)
    # reshape long to wide
    # return only variables of interest
    return d2


class Synth:
    def __init__(self,data,y,post,alpha=1.0):
        self.data = data.reset_index()
        pre_data = self.data.iloc[:post,]
        xVars = [x for x in list(data) if x != y]
        self.preX = pre_data[xVars]
        self.preY = pre_data[y]
        post_data = self.data.iloc[post:,]
        self.postX = post_data[xVars]
        self.postY = post_data[y]
        self.y = y
        self.post = post
        self.alpha = alpha
        lasso = Lasso(alpha=alpha,
                      fit_intercept=True,
                      positive=True)
        # cv=-1 is leave one out
        self.mapie = MapieRegressor(estimator=lasso,cv=-1,method='base')
        self.pre_fit = None
        self.stats = None
    def suggest_alpha(self):
        op = self.mapie.estimator.get_params()
        # maybe should be cv = self.post-1
        lcv = LassoCV(fit_intercept=True,positive=True,cv=None)
        lcv.fit(self.preX,self.preY)
        np = op.copy()
        np['alpha'] = lcv.alpha_
        print(f'Suggested alpha is {lcv.alpha_}')
        self.mapie.estimator.set_params(**np)
    def fit(self):
        self.mapie.estimator.fit(self.preX,self.preY)
        self.mapie.fit(self.preX,self.preY)
        y_pred = self.mapie.predict(self.preX,ensemble=False)
        self.pre_fit = pd.DataFrame(zip(self.preY,y_pred),columns=['Obs','Pred'])
        sq_err = (self.preY - y_pred)**2
        mean_err = (self.preY.mean() - self.preY)**2
        rsq = 1 - sq_err.sum()/mean_err.sum()
        rmse = np.sqrt(sq_err.mean())
        self.stats = {'RMSE': rmse, 'RSquare': rsq}
        print(self.stats)
    def weights_table(self,zero=True):
        inter = self.mapie.estimator.intercept_
        coef = self.mapie.estimator.coef_
        ct = pd.DataFrame(zip(list(self.preX),coef),
                          columns=['Group','Coef'])
        ct.sort_values(by='Coef',ascending=False,inplace=True)
        ci = pd.DataFrame(zip(['Intercept'],[inter]),
                          columns=['Group','Coef'])
        ct = pd.concat([ci,ct],axis=0)
        ct.reset_index(drop=True,inplace=True)
        if zero:
            nz = ct['Coef'] >= 0.000001
            return ct[nz]
        else:
            return ct
    def effects(self,alpha=0.05,cumsim=1000):
        # instant effects
        py, err_y = self.mapie.predict(self.postX,alpha=alpha)
        eys = err_y.shape
        err_y = err_y.reshape((eys[0],eys[1]))
        pdf = pd.DataFrame(err_y,columns=['Low','High'],index=self.postY.index)
        pdf['Pred'] = py
        pdf['Obs'] = self.postY
        pdf['Period'] = range(eys[0])
        pdf['Period'] = pdf['Period'] + self.post
        pyd = (pdf['Obs'].to_numpy() - py).reshape(eys[0],1)
        pdf['Dif'] = pyd
        pdf = pdf[['Obs','Pred','Low','High','Dif']]
        # Cum effects
        cs = self.mapie.conformity_scores_
        cs = np.concatenate([cs,-cs])
        pdif = pyd + np.random.choice(cs,(eys[0],cumsim))
        pdif = np.cumsum(pdif,axis=0)
        lq, hq = alpha/2, 1 - alpha/2
        pyc = np.cumsum(pyd)
        lowcum, higcum = np.quantile(pdif,q=[lq,hq],axis=1)
        pdf['CumDif'] = pyc
        pdf['CumDifLow'] = lowcum
        pdf['CumDifHig'] = higcum
        return pdf
    def graph(self,title,show=True,alpha=0.05,figsize=(10,4),colors=['k','blue','darkgrey'],labloc='upper left',anchor=None):
        fig, ax = plt.subplots(figsize=figsize)
        pref = self.pre_fit
        postr = self.effects(alpha)
        ax.plot(pref.index,pref['Obs'],marker='o',markeredgecolor='w',color=colors[0],label='Observed')
        ax.plot(postr.index,postr['Obs'],marker='o',markeredgecolor='w',color=colors[0])
        ax.plot(pref.index,pref['Pred'],marker='s',markeredgecolor='w',color=colors[1],label='Predicted')
        ax.plot(postr.index,postr['Pred'],marker='s',markeredgecolor='w',color=colors[1])
        ax.fill_between(postr.index,postr['Low'],postr['High'],alpha=0.2,color=colors[1],label='Predicted')
        ax.axvline(x=self.post-0.5, color=colors[2],lw=1.5)
        hd, lab = combo_legend(ax)
        hd.reverse()
        lab.reverse()
        ax.legend(hd, lab, loc=labloc,bbox_to_anchor=anchor)
        ax.set_title(title,loc='left')
        if show:
            plt.show()
        else:
            return fig, ax
    def cumgraph(self,title,show=True,alpha=0.05,figsize=(8,6),colors=['k','blue'],ax=None):
        postr = self.effects(alpha)
        axN = ax is None
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        ax.plot(postr.index,postr['CumDif'],marker='s',markeredgecolor='w',color=colors[1])
        ax.fill_between(postr.index,postr['CumDifLow'],postr['CumDifHig'],alpha=0.2,color=colors[1])
        ax.axhline(y=0, color=colors[0],lw=1.5)
        ax.set_title(title,loc='left')
        if show:
            plt.show()
        else:
            if axN:
                return fig, ax

