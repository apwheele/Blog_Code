'''
Plot helper
functions
'''

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import imread
from cycler import cycler

# colors via Van Gogh
colors = {"cdblue": "#286090",
          "brown" :"#7D5D2D",
          "green" :"#233A2D",
          "tan" :"#C5C88F",
          "blue" :"#455778",
          "lightblue" :"#9EACC5",
          "gold" :"#A58E38",
          "cdgrey": "#DDDDDD"}

andy_cycler = cycler(color=list(colors.values()))
marker_set = ['o', 's', '*', '^', 'D', 'P', '>', 'H']

mark_cycler = cycler(marker=marker_set)
mc = mark_cycler()

#######################################
# seeing available fonts

#from matplotlib import font_manager
#fl = font_manager.findSystemFonts(fontpaths=None, fontext="ttf")
#
#otf = [f for f in fl if f[-3:] == 'otf']
#
#font_manager.findfont("KpSans")
#font_manager.get_font(otf[-1])
#font_manager.findfont("KpSans")

#######################################


andy_theme = {'font.sans-serif': 'Verdana',
              'font.family': 'sans-serif',
              'axes.grid': True,
              'axes.axisbelow': True,
              'grid.linestyle': '--',
              'grid.color': colors['cdgrey'],
              'legend.framealpha': 1,
              'legend.facecolor': 'white',
              'legend.shadow': True,
              'legend.fontsize': 10,
              'legend.title_fontsize': 12,
              'xtick.labelsize': 10,
              'ytick.labelsize': 10,
              'axes.labelsize': 12,
              'axes.titlesize': 16,
              'figure.dpi': 100,
              'axes.titlelocation': 'left',
              'axes.prop_cycle': andy_cycler}

matplotlib.rcParams.update(andy_theme)

im = 'WLineRec.PNG'

def add_logo(ax, loc=[0.78,0.78], size=0.2, logo=im):
    if loc is None:
        return None
    if type(logo) == str:
        im = imread(logo)
    else:
        im = logo
    xrange = ax.get_xlim()
    yrange = ax.get_ylim()
    xdif = xrange[1] - xrange[0]
    ydif = yrange[1] - yrange[0]
    startx = loc[0]*xdif + xrange[0]
    starty = loc[1]*ydif + yrange[0]
    coords = [startx,starty,size*xdif,size*ydif]
    axin = ax.inset_axes(coords,transform=ax.transData)
    axin.imshow(im)
    axin.axis('off')


# combining legend
def combo_legend(ax):
    handler, labeler = ax.get_legend_handles_labels()
    hd = []
    labli = list(set(labeler))
    for lab in labli:
        comb = [h for h,l in zip(handler,labeler) if l == lab]
        hd.append(tuple(comb))
    return hd, labli


