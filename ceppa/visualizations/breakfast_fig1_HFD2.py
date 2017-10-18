
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
G.Onnis, 06.2017

Tecott Lab UCSF
"""


def load_data(E, level, err_type, ONSET, num_mins, tbin_size):
    cycles = ['DC', 'LC']
    use_days = ['chow', 'HiFat']
    days_to_use = [E.chowDayNumbers, E.HiFatDayNumbers]

    print "days_to_use: %s" %days_to_use

    num_items = get_num_items(E, level)
    all_avgs = np.zeros((num_items, len(days_to_use), len(cycles), 2, num_mins*60/tbin_size))  # FW
    all_errs = np.zeros((num_items, len(days_to_use), len(cycles), 2, num_mins*60/tbin_size))
    
    for d, days in enumerate(days_to_use):
        for c, cycle in enumerate(cycles):
            avgs, errs, labels = get_breakfast_data(
                                    E, level, err_type, ONSET=ONSET, cycle=cycle,
                                    num_mins=num_mins, days=days)
            all_avgs[:, d, c, :, :], all_errs[:, d, c, :, :] = avgs, errs     # shape: (groups, F/W, prob values)

        
    # idx-> num_items * len(days_to_use): group1-chow, group2-chow, group1-hf, group2,hf
    idx = [0, 2, 1, 3]
    all_avgs = all_avgs.reshape(-1, len(cycles), 2, num_mins*60/tbin_size)[idx]
    all_errs = all_errs.reshape(-1, len(cycles), 2, num_mins*60/tbin_size)[idx]
    return all_avgs, all_errs



def set_layout(experiment, ax, act, color, ONSET, item_num=None,
        num_mins=15, tbin_size=5, CUMULATIVE=False):
    
    xlims = (-.2, num_mins) if ONSET else (-num_mins, .2)
    major_xticks, minor_xticks = (5, 1) if num_mins > 5 else (1, .5)
    ax.xaxis.set_major_locator(MultipleLocator(major_xticks))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_xticks))

    fontsize = 10
    if act == 'F':
        ylims = (0, .65) if ONSET else (0, .5)
        major_yticks, minor_yticks = (.2, .1) if ONSET else  (.1, .05)
        ax.yaxis.set_ticks_position('left')

    elif act == 'W':
        ylims = [0, 0.22]
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
    if act == 'F':
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(color)

    elif act == 'W':
        ax.spines['right'].set_color(color)
        ax.spines['left'].set_visible(False)

    for pos in ['bottom', 'left', 'right']:
        ax.spines[pos].set_linewidth(0.5)

    ax.tick_params(axis='x', which='both', labelsize=6)
    ax.tick_params(axis='y', which='both', color=color, labelsize=6, labelcolor=color, pad=1)        
    ax.tick_params(axis='both', which='major', length=4, width=.8, direction='out', pad=1)
    ax.tick_params(axis='both', which='minor', length=2, width=.8, direction='out', pad=1)



def set_legend(ax, hls, colors):
    h0 = hls[0][0] + hls[1][0]
    l0 = hls[0][1] + hls[1][1]
    l0 = [l0[x] for x in [0, 2, 1, 3]]
    tkw = {'ncol':2, 'numpoints':1, 'bbox_to_anchor': [.8, .7, .2, .2], 'fontsize':8, 'handletextpad':.8, 
            'labelspacing':.3, 'borderaxespad':.5, 'frameon':False}
    leg = ax.legend(h0, l0, **tkw)
    for t, text in enumerate(leg.get_texts()):
        text.set_color(colors[t])


def draw_subplot1(experiment, all_avgs, all_errs, fig_title, subtitles, ONSET=True, 
        num_mins=15, tbin_size=5):
    E = experiment
    
    act = ['F', 'W']
    colors = [E.fcolors['F'][1], E.fcolors['F'][0], 
                E.fcolors['W'][1], E.fcolors['W'][0]
            ]
    tick_colors = [E.fcolors[x][1] for x in act]
    leg_labels = ['F-DC', 'W-DC', 'F-LC', 'W-LC'] 
    
    # subplot labels
    on_text = 'from AS onset' if ONSET else 'to AS offset'
    xlabel = 'Time ' + on_text + ' [min]'
    ylabel = 'Probability'
    
    every_tbins = 2 if num_mins > 5 else 1
    xticklim = (0, 15) if ONSET else (-15, 0)
    xs = np.arange(xticklim[0], xticklim[1], tbin_size * every_tbins / 60.)
    
    figsize, nrows, ncols, sharex, _ = get_subplot_specs(E, num_subplots=4)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=sharex) 

    hls = []
    for n in xrange(all_avgs.shape[0]):     # shape: (groups * chow/hifat, F/W, DC/LC, prob values)

        ax0 = axes.flatten()[n]     # F
        ax1 = ax0.twinx()           # W
        twin_axes = [ax0, ax1]
        data, yerrs = all_avgs[n], all_errs[n]

        c = 0         
        for avgs, errs in zip(data, yerrs):     # DC/LC
            k = 0
            for avg, err in zip(avgs, errs):    # F/W
                ax = twin_axes[k]  
                # plotting every 5 tbins
                ax.errorbar(xs, avg[::every_tbins], 
                    yerr=err[::every_tbins], lw=.8, 
                    color=colors[c], label=leg_labels[c], #fmt='.', ms=.3, 
                    elinewidth=.8, capsize=.8, capthick=.3, zorder=5-c)
                set_layout(E, ax, act[k], tick_colors[k], ONSET, k, num_mins, tbin_size)
                k += 1
                c += 1
    
            if n == 0:
                hls.append(ax.get_legend_handles_labels())

        ax0.set_xlabel(xlabel, fontsize=8)
        if n%2 == 0:
            ax0.set_ylabel(ylabel, fontsize=8, labelpad=10)
        if n == 1:
            set_legend(ax0, hls, colors)

        ax0.set_title(subtitles[n], fontsize=10)  

    subplot_labels(E, fig, fig_title=fig_title, txpad=0, typad=0)
    plt.subplots_adjust(bottom=.12, hspace=0.6, wspace=0.3)

    return fig



def plot_figure1(experiment, level='strain', err_type='stderr', ONSET=True, 
        num_mins=15, tbin_size=5, ADD_SOURCE=True):
    """breakfast hypothesis
    """
    E = experiment

    use_days = ['chow', 'HiFat']
    
    all_avgs, all_errs = load_data(E, level, err_type, ONSET, num_mins, tbin_size)

    # directory
    text = 'AS_onset' if ONSET else 'AS_offset'
    on_text = 'from %s' %text if ONSET else 'to %s' %text
    dirname = E.figures_dir_subpar + 'breakfast/fig1/%s/' %text
    if not os.path.isdir(dirname): os.makedirs(dirname)

    if level == 'strain':
        fig_title = 'Probability of feeding and drinking %s, DC vs. LC\n%d strains, avg$\pm$%s' %(
                        on_text, E.num_strains, err_type)
        
        subtitles = ['%s: %s' %(x, y) for y in use_days for x in E.strain_names]
        fig = draw_subplot1(E, all_avgs, all_errs, fig_title, subtitles, 
                                ONSET, num_mins)

        fname = dirname + '%s_probability_DC_LC_%dstrains_first_%dmins_binsize%ds_%s' %(
                            text, E.num_strains, num_mins, tbin_size, err_type)     
        save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, ypad=-0.04)


