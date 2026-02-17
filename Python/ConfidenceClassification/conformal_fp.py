'''
Using conformal sets
to estimate the false
positive rate

Andy Wheeler
'''

import numpy as np
from scipy.stats import ecdf

class ConfSet:
    '''
    Class to estimate conformal metrics for binary
    classification. Should use calibration set
    (or in case of random forests OOB estimates)
    
    y_true - vector of 0/1s 
    y_score - vector of predicted probabilities
    '''
    def __init__(self,y_true,y_score):
        self.p1 = y_score[y_true == 1]
        self.p0 = y_score[y_true == 0]
        self.prop = y_true.mean()
        self.m = self.prop/(1 - self.prop)
        self.ecdf1 = ecdf(self.p1)
        self.ecdf0 = ecdf(self.p0)
    def SetProp(self,prop):
        '''
        You may want to set the proportion
        of the positive class you expect 
        based on different/larger sample
        
        prop -- float with the proportion (should be between 0/1)
        '''
        self.prop = prop
        self.m = prop/(1 - prop)
    def Cover1(self,k):
        '''
        This is coverage for the positive class at the 
        kth percentile (k should be between 0-100)
        
        Also commonly known as recall
        '''
        res = np.percentile(self.p1,100-k)
        return res
    def Cover0(self,k):
        '''
        This is coverage for the negative class at the 
        kth percentile (k should be between 0-100)
        '''
        res = np.percentile(self.p0,k)
        return res
    def PCover(self,p):
        '''
        Given a probability, (which can be a scaler or a vector)
        this returns three vectors
        
        Coverage 0 Class
        Coverage 1 Class [Recall]
        Precision
        '''
        cov1 = self.ecdf1.sf.evaluate(p)
        cov0 = self.ecdf0.cdf.evaluate(p)
        # false positive estimate
        tp = 1 - cov0
        prec = fp/(fp + cov1*self.m)
        return cov0, cov1, prec
