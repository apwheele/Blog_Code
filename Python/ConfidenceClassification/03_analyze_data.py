'''
Analyzing the data
'''

from binary_plots import *
from conformal_fp import ConfSet # conformal thresholds
import pandas as pd

test_sample = pd.read_csv('MetricTestSamp.csv.zip')
conf_sample = pd.read_csv('MetricConfSamp.csv.zip')
print(conf_sample.shape)
print(conf_sample.head())
print(conf_sample.tail())

# Examing the calibration
cal_res = cal_data('TrueProb', 'obscene', conf_sample,bins=10)
print(cal_res.to_markdown(index=False)) # this is actually not as bad as I thought



####################################
# Setting recall

# Conformal method, true and probability
ct = ConfSet(conf_sample['obscene'],conf_sample['TrueProb'])

# If I want 95% recall, where is the threshold
rec95 = ct.Cover1(95)
print(rec95) # can see this is a very low value!

# And it is close to correct
oos_cov1 = (test_sample.loc[test_sample['obscene'] == 1,'TrueProb'] > rec95).mean()
print(oos_cov1)
#######################################

####################################
# Now what if we want to limit false positives?

# Need to set the overall proportion in the not sampled data
ct.SetProp(0.05)

# if set threshold to 0.999999
thresh = 0.999999
c0, c1, prec = ct.PCover(thresh)
print(prec) # the precision is still not that high, only 72%

oos_prec = test_sample.loc[test_sample['TrueProb'] > thresh,'obscene'].mean()
print(oos_prec) # actual precision is somewhat higher than expected
####################################
