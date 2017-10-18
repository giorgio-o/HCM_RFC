
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import os

from ceppa.util.my_utils import get_num_items
from ceppa.visualizations.breakfast import get_breakfast_data
from ceppa.visualizations.plotting_utils import get_subplot_specs, save_plot, subplot_labels, add_source, get_16_colors

np.set_printoptions(linewidth=250, precision=2)

"""
G.Onnis, 11.2015
    revised, 04.2017

Tecott Lab UCSF
"""

def set_layout(experiment, ax, act, color, ONSET, item_num,
        num_mins=15, tbin_size=5, CUMULATIVE=False):
    
    xlims = (-.2, num_mins) if ONSET else (-num_mins, .2)
    major_xticks, minor_xticks = (5, 1) if num_mins > 5 else (1, .5)
    ax.xaxis.set_major_locator(MultipleLocator(major_xticks))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_xticks))

    fontsize = 10
    if act == 'F':
        ylims = (0, .9) if ONSET else (0, .5)
        major_yticks, minor_yticks = (.2, .1) if ONSET else  (.1, .05)
        ax.yaxis.set_ticks_position('left')

    elif act == 'W':
        ylims = [0, 0.31]
        major_yticks, minor_yticks = .1, .05
        ax.yaxis.set_ticks_position('right')
        # workaround for sharey on secondary axis
        if len(experiment.groups) > 8:
            if item_num in [0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14]:
                ax.set_yticklabels([])

    ax.yaxis.set_major_locator(MultipleLocator(major_yticks))
    ax.yaxis.set_minor_locator(MultipleLocator(minor_yticks))
    # if CUMULATIVE:
    #     ylims = [0, 1]
    #     yticks = np.linspace(0, 1, 5+1)

    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    ax.xaxis.set_ticks_position('bottom')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.spines['bottom'].set_linewidth(0.1)

    ax.tick_params(axis='x', which='both', labelsize=6)
    ax.tick_params(axis='y', which='both', color=color, labelsize=6, labelcolor=color, pad=1)        
    ax.tick_params(axis='both', which='major', length=2.5, width=.4, direction='out', pad=1)
    ax.tick_params(axis='both', which='minor', length=1.5, width=.4, direction='out', pad=1)



def set_legend(ax, hls, colors):
    h0 = hls[0][0], hls[1][0]
    l0 = hls[0][1], hls[1][1]
    tkw = {'numpoints':1, 'bbox_to_anchor': [.8, .8, .2, .2], 'fontsize':4, 'handletextpad':.8, 
            'labelspacing':.3, 'borderaxespad':.5, 'frameon':False}
    leg = ax.legend(h0, l0, **tkw)
    for t, text in enumerate(leg.get_texts()):
        text.set_color(colors[t])


def draw_subplot(experiment, all_avgs, all_errs, fig_title, subtitles, ONSET=True, 
        num_mins=15, tbin_size=5, ADD_SOURCE=False):
    E = experiment

    figsize, nrows, ncols, sharex, sharey = get_subplot_specs(E, num_subplots=len(E.groups))
    
    # cy_labels = ['24hrs', 'Dark Cycle', 'Light Cycle']
    act = ['F', 'W']
    colors = ['.4', E.fcolors['F'][0], E.fcolors['F'][1], 
                '.65', E.fcolors['W'][0], E.fcolors['W'][1]]
    tick_colors = [E.fcolors[x][0] for x in act]
    leg_labels = ['F-24H', 'W-24H', 'F-DC', 'W-DC', 'F-LC', 'W-LC']    
    
    # probability
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=sharex, sharey=sharey)
    
    every_tbins = 2 if num_mins > 5 else 1
    xticklim = (0, 15) if ONSET else (-15, 0)
    xs = np.arange(xticklim[0], xticklim[1], tbin_size * every_tbins / 60.)
    
    hls = []
    for c in xrange(all_avgs.shape[1]): 
        try:
            ax0 = axes.flatten()[c]
            ax1 = ax0.twinx() 

            k = 0   # F, W
            m = 0   # colors and leg_labels
            for ax in [ax0, ax1]:             
                # plotting every 5 tbins
                for avgs, errs in zip(all_avgs, all_errs):
                    ax.errorbar(xs, avgs[c, ::every_tbins, k], 
                        yerr=errs[c, ::every_tbins, k], 
                        lw=.3, color=colors[m], label=leg_labels[m], #fmt='.', ms=.3, 
                        elinewidth=.5, capsize=.5, capthick=.2, zorder=5-k)
                    m += 1

                if c == 0:
                    h, l = ax.get_legend_handles_labels()
                    hls.append([h[0][0], l[0]])

                set_layout(E, ax, act[k], tick_colors[k], ONSET, c, num_mins, tbin_size)
                k +=1
            
            ax.set_title(subtitles[c], fontsize=10)  
            # if c == 0:
            #     set_legend(ax, hls, colors)

        except IndexError:
            ax.axis('off')
            continue

    # set subplot labels
    on_text = 'from AS onset' if ONSET else 'to AS offset'
    xlabel = 'Time ' + on_text + ' [min]'
    ylabel = 'Probability'
    subplot_labels(E, fig, xlabel, ylabel, fig_title)
    if ADD_SOURCE:
        add_source(fig)

    plt.subplots_adjust(bottom=.12, hspace=0.6, wspace=0.3)

    return fig



def plot_breakfast_cycles(experiment, level='strain', err_type='stdev', ONSET=True, 
        num_mins=15, tbin_size=5, days=None, ADD_SOURCE=True):
    """breakfast hypothesis
    """
    E = experiment
    cycles = E.cycles
    days_to_use = E.daysToUse if days is None else days
    print "days_to_use: %s" %days_to_use
    num_items = get_num_items(E, level)

    all_avgs = np.zeros((len(cycles), num_items, num_mins*60/tbin_size, 2)) # F, W
    all_errs = np.zeros((len(cycles), num_items, num_mins*60/tbin_size, 2))
    
    for c, cycle in enumerate(cycles):
        avgs, errs, labels = get_breakfast_data(
                            E, level, err_type, ONSET=ONSET, cycle=cycle,
                            num_mins=num_mins, days=days_to_use)
        all_avgs[c], all_errs[c] = avgs, errs

    # directory
    text = 'AS_onset' if ONSET else 'AS_offset'
    dirname = E.figures_dir_subpar + 'breakfast/all_cycles/%s/%s_days/' %(text, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)

    if level == 'strain':
        fig_title = 'Probability of feeding and drinking, 24H-DC-LC\n%s_days: %d to %d' %(
                        E.use_days, E.daysToUse[0], E.daysToUse[-1]) \
                    + '\nstrains, avg$\pm$%s' %err_type
        
        subtitles = [x for x in E.strain_names]
        fig = draw_subplot(E, all_avgs, all_errs, fig_title, subtitles, ONSET, 
                            num_mins, ADD_SOURCE=ADD_SOURCE)

        fname = dirname + 'all_cycles_%s_probability_%dstrains_first_%dmins_binsize%ds_%s' %(
                            text, E.num_strains, num_mins, tbin_size, err_type)     
        save_plot(fname, fig)

