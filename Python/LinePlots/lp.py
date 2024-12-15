'''
matplotlib, pandas and requests
to download the data is mostly all you need
'''

import cdcplot, getUCR
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

# Get the National level and City data from Real Time Crime Index
us = getUCR.cache_fbi()
city = getUCR.prep_city()

# Lets do a plot for National of the Motor Vehicle Theft Rate per pop
us['Date'] = pd.to_datetime(us['Date'])
us2020 = us[us['Date'].dt.year >= 2020]
var = 'motor-vehicle-theftrate'

# Basic
fig, ax = plt.subplots()
ax.plot(us2020['Date'],us2020[var])
#plt.show()
fig.savefig('Line00.png', dpi=500, bbox_inches='tight')

# Marker + outline + size
fig, ax = plt.subplots(figsize=(8,5))
ax.plot(us2020['Date'],us2020[var],'-o',
        color='k',markeredgecolor='white')
ax.set_title('Motor Vehicle Theft Rate in US')
#plt.show()
fig.savefig('Line01.png', dpi=500, bbox_inches='tight')


# Multiple cities
city[var] = (city['Motor Vehicle Theft']/city['Population'])*100000
nc2020 = city[(city['Year'] >= 2020) & (city['State_ref'] == 'NC')]
ncwide = nc2020.pivot(index='Mo-Yr',columns='city_state',values=var)
cityl = list(ncwide)
ncwide.columns = cityl # removing index name
ncwide['Date'] = pd.to_datetime(ncwide.index,format='%m-%Y')
ncwide.sort_values(by='Date',inplace=True)

# For good overview of marker types, https://matplotlib.org/stable/gallery/lines_bars_and_markers/marker_reference.html
fig, ax = plt.subplots(figsize=(8,5))
ax.plot(ncwide['Date'],ncwide['Charlotte, NC'],'-s',
        color='green',markeredgecolor='white',label='Charlotte')
ax.plot(us2020['Date'],us2020[var],'-*',
        color='k',label='US')
ax.legend()
ax.set_title('Motor Vehicle Theft Rate')
#plt.show()
fig.savefig('Line02.png', dpi=500, bbox_inches='tight')

# Dashes instead of points
# https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
fig, ax = plt.subplots(figsize=(8,5))
ax.plot(ncwide['Date'],ncwide['Charlotte, NC'],':',
        color='green',markeredgecolor='white',label='Charlotte')
ax.plot(ncwide['Date'],ncwide['Asheville, NC'],'--',
        color='#455778',label='Asheville')
ax.plot(us2020['Date'],us2020[var],'-',
        color='k',label='US')
ax.legend()
ax.set_title('Motor Vehicle Theft Rate')
#plt.show()
fig.savefig('Line03.png', dpi=500, bbox_inches='tight')


# It is difficult to untangle multiple cities
# https://matplotlib.org/stable/users/explain/colors/colormaps.html
fig, ax = plt.subplots(figsize=(12,8))
for i,v in enumerate(cityl):
    ax.plot(ncwide['Date'],ncwide[v],'-',color=cm.tab10(i),label=v)

ax.legend()
#plt.show()
fig.savefig('Line04.png', dpi=500, bbox_inches='tight')

# Can do this easier with pandas
fig, ax = plt.subplots(figsize=(12,8))
ncwide.plot.line(x='Date',ax=ax,color=cm.Dark2.colors)
#plt.show()
fig.savefig('Line05.png', dpi=500, bbox_inches='tight')

# Highlight one city, compared to the rest
fig, ax = plt.subplots(figsize=(12,8))
lab = 'Other NC'

for v in cityl:
    if v == 'Durham, NC':
        pass
    else:
        ax.plot(ncwide['Date'],ncwide[v],'-',color='lightgrey',label=lab)
        lab = None


ax.plot(us2020['Date'],us2020[var],'-o',
        color='k',markeredgecolor='white',label='US')
ax.plot(ncwide['Date'],ncwide['Durham, NC'],'-',linewidth=2,color='red',label='Durham')
ax.legend()
ax.set_title('Motor Vehicle Theft Rate')
#plt.show()
fig.savefig('Line06.png', dpi=500, bbox_inches='tight')


# CDC Logo
fig, ax = plt.subplots(figsize=(8,5))
ax.plot(ncwide['Date'],ncwide['Charlotte, NC'],'-s',
        color='green',markeredgecolor='white',label='Charlotte')
ax.plot(us2020['Date'],us2020[var],'-*',
        color='k',label='US')
ax.legend()
ax.set_title('Motor Vehicle Theft Rate')
cdcplot.add_logo(ax,[0.85,0.05],size=0.13)
#plt.show()
fig.savefig('Line07.png', dpi=500, bbox_inches='tight')



