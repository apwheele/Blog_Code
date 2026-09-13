'''Formats the result csvs as markdown tables for the blog post'''
import pandas as pd

BUF = {'Dist':'Meters','Area':'Area','PctLand':'% Land','StreetKm':'Street km',
       'StreetDens':'Street km/sq km','Theft':'Thefts','Robbery':'Robberies',
       'PerSqKm':'Per sq km','PerKm':'Per street km'}
NET = {'Order':'Order','Segments':'Segments','StreetKm':'Street km',
       'Theft':'Thefts','Robbery':'Robberies','PerKm':'Per street km'}
RND = {'Area':3,'PctLand':1,'StreetKm':2,'StreetDens':1,'PerSqKm':0,'PerKm':1}

out = []
for slug, nm in [('CanalSt','Canal St'),('BrooklynBridge','Brooklyn Bridge')]:
    for kind, cols in [('Buffer',BUF),('Network',NET)]:
        d = pd.read_csv(f'{slug}_{kind}.csv')
        d = d[[c for c in cols if c in d.columns]].round(RND)
        for c in ['PerSqKm']:
            if c in d.columns:
                d[c] = d[c].astype(int)
        d.columns = [cols[c] for c in d.columns]
        out.append(f'### {nm}, {kind.lower()}\n\n{d.to_markdown(index=False)}\n')

open('Tables.md','w').write('\n'.join(out))
print('\n'.join(out))
