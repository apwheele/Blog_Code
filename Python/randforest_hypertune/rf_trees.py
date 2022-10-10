'''
Example of using optuna
to tune random forest

Andy Wheeler
'''

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import optuna
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import recid # my custom NIJ recid funcs

# Read in data and feature engineering
train, test = recid.fe()

# Loop over tree sizes
ntrees = np.arange(10,1010,10)
auc, bs = [], []

# This is showing number of estimators is asymptotic
# should approach best value with higher numbers
# but has some variance in out of sample test
for n in ntrees:
    print(f'Fitting Model for ntrees:{n} @ {datetime.now()}')
    # Baseline model
    mod = RandomForestClassifier(n_estimators=n, max_depth=5, min_samples_split=50)
    # Fit Model
    mod.fit(train[recid.xvars], train[recid.y1])
    # Evaluate AUC/BrierScore out of sample
    pred_out = mod.predict_proba(test[recid.xvars])[:,1]
    auc.append(roc_auc_score(test[recid.y1], pred_out))
    bs.append(brier_score_loss(test[recid.y1], pred_out))


fig, (ax1, ax2) = plt.subplots(2, figsize=(6,8))
ax1.plot(ntrees, auc)
ax1.set_title('AUC')
ax2.plot(ntrees, bs)
ax2.set_title('Brier Score')
plt.savefig('Ntree_grid.png', dpi=500, bbox_inches='tight')
#plt.show()

# Showing example with optuna
# Fixing estimators to 500, varying depth
# min samples, max_features

# Consistent train/test split for all evaluations
tr1, tr2 = train_test_split(train, test_size=2000)

def objective(trial):
    param = {
        "n_estimators": 500,
        "max_depth": trial.suggest_int("max_depth", 2, 10),
        "min_samples_split": trial.suggest_int("min_samples_split", 10, 200, step=10),
        "max_features": trial.suggest_int("max_features", 3, 15),
    }
    mod = RandomForestClassifier(**param)
    mod.fit(tr1[recid.xvars], tr1[recid.y1])
    pred_out = mod.predict_proba(tr2[recid.xvars])[:,1]
    auc = roc_auc_score(tr2[recid.y1], pred_out)
    return auc

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
trial = study.best_trial

print(f"Best AUC {trial.value}")
print("Best Params")
print(trial.params)

# Lets refit according to these params for the full
# training set
mod2 = RandomForestClassifier(n_estimators=500,**trial.params)
mod2.fit(train[recid.xvars], train[recid.y1])
pred_out = mod2.predict_proba(test[recid.xvars])[:,1]
auc_tuned = roc_auc_score(test[recid.y1], pred_out)
bs_tuned = brier_score_loss(test[recid.y1], pred_out)
print(f"AUC tuned {auc_tuned:.4f} vs AUC default {auc[-1]:.4f}")
print(f"Brier Score tuned {bs_tuned:.4f} vs default {bs[-1]:.4f}")


# Likely to be negative correlation between
# max depth and min samples/max features
tdf = study.trials_dataframe()
tdf.corr()

