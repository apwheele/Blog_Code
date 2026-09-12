'''
Faking synthetic control estimates -- monthly thefts in
Los Angeles and DA George Gascon

Estimates four synthetic control models, three of which are
fabricated (null/up/down) and one of which is honest. The point is
that all four produce output that looks the same to a reader who
does not have the data and code.

Run PrepGasconData.py first to make LATheft.csv

Andy Wheeler
'''

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import FakeSynth
import LassoSynth

warnings.filterwarnings('ignore')
np.random.seed(10)

TREAT = 'Los Angeles, CA'
POST = 47      # Jan 2017 through Nov 2020 is the pre-period
# Larger than what LassoCV suggests (~10), I want a sparse enough
# table of weights to fit in a blog post. Results are not sensitive
# to this over a pretty wide range, see the sensitivity table below
ALPHA = 30
TOPN = 10      # how many weights to print in the markdown tables

theft = pd.read_csv('LATheft.csv', parse_dates=['Date'])
wide = LassoSynth.prep_longdata(theft, 'Date', 'Rate', 'City')
dates = np.sort(theft['Date'].unique())
pops = theft.groupby('City')['Pop'].first()
print(f'{wide.shape[1]-1} donor cities, {wide.shape[0]} months')


#################################################
# HELPERS

def date_axis(ax, every=6):
    '''Relabel the integer period axis with dates'''
    loc = list(range(0, len(dates), every))
    ax.set_xticks(loc)
    lab = [pd.Timestamp(dates[i]).strftime('%b-%y') for i in loc]
    ax.set_xticklabels(lab, rotation=45, ha='right')
    ax.set_xlim(-1.5, len(dates) + 0.5)


def mdtable(df, dec=3):
    '''Minimal markdown table, no tabulate in my environment'''
    def fm(v):
        if isinstance(v, (float, np.floating)):
            return f'{v:,.{dec}f}'
        return str(v)
    head = '| ' + ' | '.join(list(df)) + ' |'
    sep = '|' + '|'.join(['---'] * df.shape[1]) + '|'
    rows = ['| ' + ' | '.join(fm(v) for v in r) + ' |'
            for r in df.itertuples(index=False)]
    return '\n'.join([head, sep] + rows)


def synth_graph(mod, title, fileout):
    fig, ax = mod.graph(title, show=False, figsize=(9, 5), labloc='lower left')
    date_axis(ax)
    ax.set_ylabel('Thefts per 100,000')
    top = ax.get_ylim()[1]
    ax.annotate('Gascon\nsworn in', xy=(POST - 2, top * 0.995),
                ha='right', va='top', fontsize=11, color='dimgrey')
    fig.savefig(fileout, dpi=100, bbox_inches='tight')
    plt.close(fig)


def stat_row(lab, mod):
    '''One row of the summary table a reader would actually see'''
    eff = mod.effects()
    wt = mod.weights_table()
    pct = 100 * eff['Dif'].sum() / eff['Pred'].sum()
    cum = eff['CumDif'].iloc[-1]
    lo = eff['CumDifLow'].iloc[-1]
    hi = eff['CumDifHig'].iloc[-1]
    lapop = pops[TREAT]
    return {'Model': lab,
            'Pre RMSE': f'{mod.stats["RMSE"]:.2f}',
            'Pre R2': f'{mod.stats["RSquare"]:.3f}',
            'Donors': len(wt) - 1,
            'Monthly per 100k': f'{eff["Dif"].mean():.1f}',
            'Percent': f'{pct:.1f}%',
            'Cumulative per 100k': f'{cum:,.0f}',
            '95% CI': f'{lo:,.0f} to {hi:,.0f}',
            'Total Thefts': f'{cum*lapop/100000:,.0f}'}


def weight_md(mod, fileout):
    wt = mod.weights_table().copy()
    wt.columns = ['City', 'Weight']
    wt.to_csv(fileout, index=False)
    tot = len(wt) - 1
    return mdtable(wt.head(TOPN + 1), 4), tot


#################################################
# THE OBSERVED DATA

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(range(len(dates)), wide[TREAT], marker='o', markeredgecolor='w', color='k')
ax.axvline(x=POST - 0.5, color='darkgrey', lw=1.5)
date_axis(ax)
ax.set_ylabel('Thefts per 100,000')
ax.set_title('Los Angeles Monthly Theft Rate, Gascon sworn in Dec 2020', loc='left')
fig.savefig('LATheftObs.png', dpi=100, bbox_inches='tight')
plt.close(fig)


#################################################
# THE THREE FAKES
# This is the entire fabrication, you write down the post-period
# trajectory you want and fit the donor weights to it

obs_post = wide[TREAT].iloc[POST:].to_numpy()

fakes = {'Fake null': obs_post * 1.00,
         'Fake increase': obs_post * 0.80,   # synthetic 20% under observed
         'Fake decrease': obs_post * 1.25}   # synthetic 25% over observed

mods, tables, ndon = {}, {}, {}
files = {'Fake null': 'FakeNull',
         'Fake increase': 'FakeIncrease',
         'Fake decrease': 'FakeDecrease',
         'Honest': 'Real'}

for lab, fk in fakes.items():
    print(f'--- {lab} ---')
    m = FakeSynth.FakeSynth(wide, TREAT, POST, fk, alpha=ALPHA)
    m.fit()
    mods[lab] = m

#################################################
# THE HONEST MODEL

print('--- Honest ---')
real = LassoSynth.Synth(wide, TREAT, POST, alpha=ALPHA)
real.fit()
mods['Honest'] = real


#################################################
# OUTPUT

titles = {'Fake null': 'Thefts per 100,000 Los Angeles, No Gascon Effect',
          'Fake increase': 'Thefts per 100,000 Los Angeles, Gascon Increased Thefts',
          'Fake decrease': 'Thefts per 100,000 Los Angeles, Gascon Decreased Thefts',
          'Honest': 'Thefts per 100,000 Los Angeles, Honest Pre-Period Fit'}

stats = []
for lab, m in mods.items():
    synth_graph(m, titles[lab], files[lab] + 'Synth.png')
    tables[lab], ndon[lab] = weight_md(m, files[lab] + 'Weights.csv')
    stats.append(stat_row(lab, m))
    eff = m.effects()
    eff.insert(0, 'Date', [pd.Timestamp(dates[i]).date() for i in eff.index])
    eff.to_csv(files[lab] + 'Effects.csv', index=False)

stats = pd.DataFrame(stats)

# 2x2 of the cumulative effects
fig, axs = plt.subplots(2, 2, figsize=(11, 7), sharex=True, sharey=True)
for (lab, m), ax in zip(mods.items(), axs.flatten()):
    m.cumgraph(lab, show=False, ax=ax)
    loc = list(range(POST, len(dates), 12))
    ax.set_xticks(loc)
    ax.set_xticklabels([pd.Timestamp(dates[i]).strftime('%b-%y') for i in loc],
                       rotation=45, ha='right')
fig.suptitle('Cumulative [Observed - Synthetic] Thefts per 100,000, Dec 2020 to Nov 2024',
             x=0.02, ha='left', size=16)
fig.tight_layout()
fig.savefig('CumCompare.png', dpi=100, bbox_inches='tight')
plt.close(fig)

# all four synthetic series on one set of axes, same observed data
fig, ax = plt.subplots(figsize=(9, 5))
cl = {'Fake null': 'darkorange', 'Fake increase': 'tab:red',
      'Fake decrease': 'tab:green', 'Honest': 'tab:blue'}
ax.plot(range(len(dates)), wide[TREAT], marker='o', ms=4,
        markeredgecolor='w', color='k', label='Observed LA', zorder=5)
for lab, m in mods.items():
    ser = np.r_[m.pre_fit['Pred'].to_numpy(), m.effects()['Pred'].to_numpy()]
    ax.plot(range(len(dates)), ser, color=cl[lab], lw=1.6, label=lab)
ax.axvline(x=POST - 0.5, color='darkgrey', lw=1.5)
date_axis(ax)
ax.set_ylabel('Thefts per 100,000')
ax.legend(loc='upper left', fontsize=11, ncol=2)
ax.set_title('Four "Synthetic Los Angeles" series, same observed data', loc='left')
fig.savefig('AllSynth.png', dpi=100, bbox_inches='tight')
plt.close(fig)


#################################################
# SENSITIVITY OF THE HONEST MODEL

sens = []
LAPOP = pops[TREAT]


def rate_row(spec, s, e):
    cum = e['CumDif'].iloc[-1]
    return {'Spec': spec,
            'Donors': len(s.weights_table()) - 1,
            'Percent': f"{100*e['Dif'].sum()/e['Pred'].sum():.1f}%",
            'Cumulative per 100k': f'{cum:,.0f}',
            'Total Thefts': f'{cum*LAPOP/100000:,.0f}'}


# a range of penalties
for a in [5, 10, 20, 30, 50, 80]:
    s = LassoSynth.Synth(wide, TREAT, POST, alpha=a)
    s.fit()
    e = s.effects()
    sens.append(rate_row(f'Rates, all donors, alpha={a}', s, e))

# only cities over 250k, the small agencies the lasso likes are
# not plausible comparisons for LA
big = [c for c in list(wide) if (pops[c] >= 250000) or (c == TREAT)]
for a in [10, 30]:
    s = LassoSynth.Synth(wide[big], TREAT, POST, alpha=a)
    s.fit()
    e = s.effects()
    sens.append(rate_row(f'Rates, 250k+ donors, alpha={a}', s, e))

# counts instead of rates, the Hogan/Kaplan sticking point
widec = LassoSynth.prep_longdata(theft, 'Date', 'Theft', 'City')
s = LassoSynth.Synth(widec, TREAT, POST, alpha=ALPHA)
s.fit()
e = s.effects()
sens.append({'Spec': f'Counts, all donors, alpha={ALPHA}',
             'Donors': len(s.weights_table()) - 1,
             'Percent': f"{100*e['Dif'].sum()/e['Pred'].sum():.1f}%",
             'Cumulative per 100k': 'n/a',
             'Total Thefts': f"{e['CumDif'].iloc[-1]:,.0f}"})

# in-time placebo, pretend the intervention was Dec 2018 and
# throw away everything after Nov 2019
s = LassoSynth.Synth(wide.iloc[:35, ], TREAT, 23, alpha=ALPHA)
s.fit()
e = s.effects()
sens.append(rate_row(f'Placebo Dec 2018 (12 mo), alpha={ALPHA}', s, e))

sens = pd.DataFrame(sens)


#################################################
# HOW GOOD CAN A FABRICATED PRE-PERIOD FIT BE?
# The fabricated model has to fit the real pre-period and the made
# up post-period at the same time, so at a fixed penalty it fits
# the pre-period a bit worse than the honest model. Turn the
# penalty down and that tell goes away -- and a reader has no way
# to know what pre-period fit was achievable in the first place

ff = []
for a in [1, 5, 10, 20, 30]:
    h = LassoSynth.Synth(wide, TREAT, POST, alpha=a)
    h.fit()
    g = FakeSynth.FakeSynth(wide, TREAT, POST, obs_post*0.80, alpha=a)
    g.fit()
    ge = g.effects()
    ff.append({'alpha': a,
               'Honest RMSE': f"{h.stats['RMSE']:.2f}",
               'Honest R2': f"{h.stats['RSquare']:.3f}",
               'Faked RMSE': f"{g.stats['RMSE']:.2f}",
               'Faked R2': f"{g.stats['RSquare']:.3f}",
               'Faked Percent': f"{100*ge['Dif'].sum()/ge['Pred'].sum():.1f}%"})

ff = pd.DataFrame(ff)


#################################################
# PRINT EVERYTHING FOR THE BLOG POST

with open('Results.md', 'w') as f:
    f.write('# Summary table\n\n')
    f.write(mdtable(stats, 3) + '\n\n')
    for lab in mods:
        f.write(f'# Weights, {lab} (top {TOPN} of {ndon[lab]} nonzero)\n\n')
        f.write(tables[lab] + '\n\n')
    f.write('# Sensitivity, honest model\n\n')
    f.write(mdtable(sens, 1) + '\n\n')
    f.write('# Pre-period fit, honest vs faked increase\n\n')
    f.write(mdtable(ff, 1) + '\n')

print(stats.to_string(index=False))
print(sens.to_string(index=False))
print(ff.to_string(index=False))
print('wrote Results.md')
