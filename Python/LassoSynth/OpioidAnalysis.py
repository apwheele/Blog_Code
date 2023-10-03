'''
Opioid analysis

See Charles Fain Lehman's post
for motivation

https://thecausalfallacy.com/p/did-drug-decriminalization-increase/comments
'''

import LassoSynth
import pandas as pd

opioid = pd.read_csv('OpioidDeathRates.csv')
wide = LassoSynth.prep_longdata(opioid,'Period','Rate','State')

############################
# Oregon Analysis
or_data = wide.drop('Washington', axis=1)
oregon = LassoSynth.Synth(or_data,'Oregon',38)

oregon.suggest_alpha() # default alpha is 1
oregon.fit()
oregon.weights_table()
oregon.effects(alpha=0.05)

oregon.graph('Opioid Death Rates per 100,000, Oregon Synthetic Estimate')

oregon.cumgraph('Oregon Cumulative Effects, [Observed - Predicted]')
############################


############################
# Washington Analysis
wa_data = wide.drop('Oregon', axis=1)
wash = LassoSynth.Synth(wa_data,'Washington',39)

wash.suggest_alpha() # default alpha is 1
wash.fit()
wash.weights_table()
wash.effects(alpha=0.05)

wash.graph('Opioid Death Rates per 100,000, Washington Synthetic Estimate')

wash.cumgraph('Washington Cumulative Effects, [Observed - Predicted]')
############################
