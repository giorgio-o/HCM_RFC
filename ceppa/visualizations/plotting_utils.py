import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as mcol
import matplotlib.patches as patches

import csv

from ceppa.util.cage import Cage
from ceppa.util import my_utils


"""
G.Onnis, 11.2016
    updated: 06.2017

Tecott Lab UCSF
"""



def ax_cleanup(ax, labelsize=8):
    """
    """
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['bottom'].set_linewidth(0.5)
    ax.tick_params(axis='both', which='both', labelsize=labelsize, direction='out')


def add_xylabels(fig, xlabel='', ylabel='', xypad=0, yxpad=0, labelsize=10):
    fig.text(.5, .05+xypad, xlabel, fontsize=labelsize, 
                ha='center', va='top')
    fig.text(.05+yxpad, .5, ylabel, fontsize=labelsize, 
                ha='left', va='center', rotation='vertical')


def add_titles_notes(E, fig, title='', tl_note2='', typad=0, tlxpad=0, tlypad=0, 
        titlesize=12, tl2_color='k', TL_NOTE=False, HP_TEXT=True):
    """set subplot labels
    """
    fig.suptitle(title, y=1.0+typad, fontsize=titlesize, va='bottom')
          
    if TL_NOTE:         # top-left
        hp_text = 'hyper_params:\n%s' %E.hypar_caption 
        fig.text(tlxpad, 0.9+tlypad, '%s\n\n%s' %(hp_text, tl_note2), 
                    fontsize=8, ha='left', va='bottom')


def add_source(fig, sxpad=0., sypad=0., labelsize=8, 
        source='HCM data, Tecott Lab, UCSF', 
        author='G.Onnis', affiliation='Tecott Lab'):
    text = 'source: %s\nby: %s, %s' %(source, author, affiliation)
    fig.text(.125+sxpad, sypad, text, 
                fontsize=labelsize, ha='left', va='center')


def save_plot(fname, fig, dpi=300, PS=False, ADD_SOURCE=False, 
        labelsize=8, sxpad=0, sypad=0):
    
    if ADD_SOURCE:
        add_source(fig, sxpad=sxpad, sypad=sypad, labelsize=labelsize)
        
    tkw = {'bbox_inches':'tight', 'dpi':dpi}
    form = 'ps' if PS else 'pdf'
    plt.savefig(fname + '.%s' %form, format=form, **tkw)
    print "figure saved to:\n%s.%s" %(fname, form)
    plt.close()


def remove_axes_not_used(group, axes, nrows, ncols, m):
    if nrows*ncols-m > 0:
        mice_ok, _ = group.count_mice()
        # assert m == len(mice_ok)
        [ax.axis('off') for ax in axes.flatten()[-(nrows*ncols-m):]]



def plot_colored_background(ax, tstart, tend, ymin=0, ymax=1, color='.9',
        alpha=1):
    ax.axvspan(tstart/3600-7, tend/3600-7, ymin=ymin, ymax=ymax,
                fc=color, ec=color, alpha=alpha, 
                transform=ax.transAxes, zorder=-1)


def show_fast_times(E, ax, day_num, ymin=0, ymax=1, TEXT=False, color='k'):

    if day_num in E.fastDayNumbers:
        tstart, tend = E.get_food_removal_times()
        text = 'FAST'
    if day_num in E.reFeedDayNumbers:
        tstart, tend = E.get_food_reinsertion_times()
        text = 'REFEED'
           
    if TEXT:
        xpos, ypos = tstart/3600-7, ax.get_ylim()[0]
        xpad = .2
        h, m = int(tend // 3600 -7), int(tend % 3600 / 60)
        ax.text(xpos + xpad, ypos, 'CT%d%d\n%s' %(h, m, text), 
                color=color, ha='left', va='bottom')
    
    plot_colored_background(ax, tstart, tend, ymin, ymax, color=color, alpha=.7)


# def get_nrows_ncols(num_subplots):
    # sharex, sharey = True, True
    # if num_subplots == 1:
    #     sharex, sharey = False, False
    #     nrows, ncols = 1, 1
    # elif num_subplots == 2:
    #     sharex = False
    #     nrows, ncols = 1, 2
    # elif num_subplots == 3:
    #     sharex = False
    #     nrows, ncols = 1, 3
    # elif num_subplots == 4:
    #     nrows, ncols = 2, 2
    # elif num_subplots in [5, 6]:
    #     nrows, ncols = 2, 3  
    # elif num_subplots in [7, 8, 9]:
    #     nrows, ncols = 3, 3
    # elif num_subplots in [10, 11, 12]:
    #     nrows, ncols = 3, 4
    # elif num_subplots in range(13, 16+1):
    #     nrows, ncols = 4, 4
    # elif num_subplots in range(17, 20+1):
    #     nrows, ncols = 5, 4
    # elif num_subplots in range(20, 24+1):
    #     nrows, ncols = (6, 4)  

    # return nrows, ncols, sharex, sharey

# def get_subplot_specs(experiment, num_subplots=None, plot_type=None, tbin_type=None):
#     E = experiment

#     figsize = (6.4, 4.8)        # default, width_to_height=1.33

#     # sharex, sharey = True, True
#     # nrows, ncols = (1, 1) 
#     # if num_subplots == 1:
#     #     sharex = False
#     #     nrows, ncols = 1, 1
#     # elif num_subplots == 2:
#     #     sharex = False
#     #     nrows, ncols = 1, 2
#     # elif num_subplots == 3:
#     #     sharex = False
#     #     nrows, ncols = 1, 3
#     # elif num_subplots == 4:
#     #     nrows, ncols = 2, 2
#     # elif num_subplots in [5, 6]:
#     #     nrows, ncols = 2, 3  
#     # elif num_subplots in [7, 8, 9]:
#     #     nrows, ncols = 3, 3
#     # elif num_subplots in [10, 11, 12]:
#     #     nrows, ncols = 3, 4
#     # elif num_subplots in range(13, 16+1):
#     #     nrows, ncols = 4, 4
#     # elif num_subplots in range(17, 20+1):
#     #     nrows, ncols = 5, 4
#     # elif num_subplots in range(20, 24+1):
#     #     nrows, ncols = (6, 4)         

#     if plot_type == 'position_density':
#         stop

#     elif plot_type == 'raster':
#         if num_subplots == 0:           # code for mouseday plot
#             figsize = (12., 3.6)      
#         elif num_subplots == 1:         # mouse 
#             figsize = (12, 7.2)         
#         elif num_subplots >=2 and num_subplots <=16:    # groups
#             figsize = (12, 7.2)
#         elif num_subplots > 16:    
#             figsize = (12, 9)
#         return figsize, nrows, ncols
    
#     elif plot_type == 'features':
#         nrows, ncols = 8, 3
#         figsize = (6.4, 9.6)#(8, 12)
#         return figsize, nrows, ncols

#     elif plot_type == 'time_budgets':
#         if num_subplots == 2:
#             stop
#             # figsize = (4.8, 3.6)              # width_to_height=1.33
#         elif num_subplots == 3:
#             figsize = (6.4, 3.6)
#         elif num_subplots >= 4 and num_subplots <= 16:
#             stop
#             figsize = (6.4, 8.5) 
#         return figsize, nrows, ncols

#     elif plot_type == 'subplot':
#         if num_subplots in [1, 2]:
#             figsize = (4.8, 3.6)
#         elif num_subplots ==3:
#             figsize = (6.4, 3.6)
#         elif num_subplots >=4 and num_subplots <=8:
#             stop
#         elif num_subplots >=8 and num_subplots <=16:
#             stop

#     return figsize, nrows, ncols, sharex, sharey


def show_devices_labels(E, ax, fontsize=12, pad=0):
    colors = [E.fcolors[x][0] for x in ['F', 'W']]
    ax.text(.2, -.03 + pad, 'Food', fontsize=fontsize, 
            color=colors[0], ha='center', va='top',
            transform=ax.transAxes) 
    ax.text(.8, -.03 + pad, 'Water', fontsize=fontsize, 
            color=colors[1], ha='center', va='top',
            transform=ax.transAxes)                   


def write_2darray_to_csv(E, data, header='', subheader='', row_labels='', col_labels='', 
        fname='sample_2darray.csv'):
    
    header = '%s: ' %E.short_name + header
    with open(fname, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow([header])
        writer.writerow([subheader] + col_labels)
        c = 0
        for row in data:
            writer.writerow(np.hstack([row_labels[c], ['%1.4f' %r for r in row]]))
            c += 1
    print "csv files saved to:\n%s" % fname




# # position density
# def draw_xbins_ybins_cage_grid(ax, xbins=2, ybins=4):
#     C = Cage()
#     xticks = np.linspace(C.CMXLower, C.CMXUpper, xbins + 1)
#     yticks = np.linspace(C.CMYLower, C.CMYUpper, ybins + 1)
#     ax.set_xticks(xticks)
#     ax.set_yticks(yticks)
#     ax.grid()



# # # general use

def get_16_colors():

    # These are the "Tableau 20" colors as RGB.
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), #(214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 # (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (127, 127, 127), (199, 199, 199), # repeat
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)
                 ]

    # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    return tableau20



# to review
# def draw_device_labels(ax, fontsize=16, pad=3, HB=False):
#     C = Cage()
#     colors = ['r', 'b']
#     ax.text(C.mouseCMXAtPhoto, C.CMYLower - pad, 'F', 
#         fontsize=fontsize, color=colors[0], ha='center',
#         transform=ax.transData
#         )           
#     ax.text(C.mouseCMXAtLick, C.CMYLower - pad, 'W', 
#         fontsize=fontsize, color=colors[1], ha='center',
#         transform=ax.transData
#         )

# def set_CT_layout(E, ax, ymax):
    
#     xticks = range(8, 32, 2)
#     xlabels = [str(x) for x in range(8, 26, 2)] \
#                 + [str(x) for x in range(2, 8, 2)]
#     ax.set_xlim((7, 31))
#     ax.set_xticks(xticks)
#     ax.set_xticklabels(xlabels)
#     ax.set_ylim(0, ymax)
#     # # common y-scale
#     # ax.set_xticklabels([])
#     # if num_subplot >= 12 and level == 'strain':
#     #     ax.set_xticklabels(xlabels) 
#     # elif num_subplot >= 9 and level != 'strain':
#     #     ax.set_xticklabels(xlabels) 
#     # ylims, yticks = [E.plot_settings_dict[feat][key] for key in ['ylims', 'yticks']]
#     # ax.set_ylim(ylims)
#     # ax.set_yticks(yticks)
#     # ax.set_yticklabels([])
#     # if num_subplot in [0, 4, 8, 12] and level == 'strain':
#     #     ax.set_yticklabels(yticks) 
#     # elif num_subplot in [0, 3, 6, 9] and level != 'strain':
#     #     ax.set_yticklabels(yticks)
#     ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
#     ax.tick_params(axis='both', which='both', labelsize=7)
#     ax.set_aspect('auto')
#     ax_cleanup(ax)
#     plot_colored_background(ax)


# def set_days_layout(E, ax, ymax):
#     ax.set_xlim(E.daysToUse[0] - 1, E.daysToUse[-1] + 1)
#     ax.set_xticks(E.daysToUse)
#     ax.set_ylim(0, ymax)
#     # ax.set_yticks(np.arange(0, ymax+1, get_step(ymax)))
#     ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
#     ax.tick_params(axis='both', which='both', labelsize=7)
#     ax.set_aspect('auto')
#     ax_cleanup(ax)


# def set_distribution_layout(ax, bins, ymax):
#     # ax.set_xlim((0, bins[-1]))
#     # ax.set_xticks(bins[::5])
#     ax.set_ylim((0, ymax))
#     ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
#     ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
#     ax.set_aspect('auto')
#     ax.tick_params(axis='both', which='both', labelsize=7)
#     ax_cleanup(ax)


# def set_CT_plot_labels_and_titles(fig, title, xlabel='', ylabel=''):
#     fig.text(0.5, 0.03, xlabel, fontsize=10, ha='center')
#     fig.text(0.05, 0.5, ylabel, fontsize=10, va='center', rotation='vertical') 
#     fig.text(0.03, 0.92, title, fontsize=7, va='center')





# def nanize_trilow_values(M, diag_value=1):
#     M[np.tril_indices(M.shape[0])] = np.nan
#     np.fill_diagonal(M, diag_value)
#     return M



# def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
#     new_cmap = mcol.LinearSegmentedColormap.from_list(
#         'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
#         cmap(np.linspace(minval, maxval, n)))
#     return new_cmap


# def cmap_discretize(cmap, N):
#     """Return a discrete colormap from the continuous colormap cmap.

#         cmap: colormap instance, eg. cm.jet. 
#         N: number of colors.

#     Example
#         x = resize(arange(100), (5,100))
#         djet = cmap_discretize(cm.jet, 5)
#         imshow(x, cmap=djet)
#     """

#     if type(cmap) == str:
#         cmap = plt.get_cmap(cmap)
#     colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
#     colors_rgba = cmap(colors_i)
#     indices = np.linspace(0, 1., N+1)
#     cdict = {}
#     for ki,key in enumerate(('red','green','blue')):
#         cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki])
#                        for i in xrange(N+1) ]
#     # Return colormap object.
#     return mcol.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)



# # # # # # # 


