'''
The whole point of the blog post -- this is all it takes to
fabricate a synthetic control estimate.

LassoSynth.Synth estimates the donor weights using only the
pre-intervention periods. FakeSynth estimates the weights using
*every* period, where the treated unit's post period outcome has
been swapped out for whatever the author would like to report.
The pre-period values are never touched, so the pre-period fit
statistics, the weights table and the graph all look normal.

Andy Wheeler
'''

import numpy as np
import pandas as pd
from sklearn.linear_model import LassoCV

import LassoSynth


class FakeSynth(LassoSynth.Synth):
    def __init__(self,data,y,post,fake,alpha=1.0):
        super().__init__(data,y,post,alpha)
        # X is the same, the donor cities are real data
        self.fitX = pd.concat([self.preX,self.postX],axis=0)
        # y is real pre-period, whatever you want post-period
        fs = pd.Series(np.asarray(fake),index=self.postY.index,name=y)
        self.fitY = pd.concat([self.preY,fs],axis=0)
    def suggest_alpha(self):
        op = self.mapie.estimator.get_params()
        lcv = LassoCV(fit_intercept=True,positive=True,cv=None)
        lcv.fit(self.fitX,self.fitY)
        np_ = op.copy()
        np_['alpha'] = lcv.alpha_
        print(f'Suggested alpha is {lcv.alpha_}')
        self.mapie.estimator.set_params(**np_)
    def fit(self):
        # only difference, fit on all the periods
        self.mapie.estimator.fit(self.fitX,self.fitY)
        self.mapie.fit(self.fitX,self.fitY)
        # pre-period diagnostics are versus the real pre-period data,
        # so they are identical in kind to the honest model
        y_pred = self.mapie.predict(self.preX,ensemble=False)
        self.pre_fit = pd.DataFrame(zip(self.preY,y_pred),columns=['Obs','Pred'])
        sq_err = (self.preY - y_pred)**2
        mean_err = (self.preY.mean() - self.preY)**2
        rsq = 1 - sq_err.sum()/mean_err.sum()
        rmse = np.sqrt(sq_err.mean())
        self.stats = {'RMSE': rmse, 'RSquare': rsq}
        print(self.stats)
