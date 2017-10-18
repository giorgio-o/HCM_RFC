
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import os

from ceppa.util.my_utils import get_num_items
from ceppa.visualizations.plotting_utils import get_subplot_specs, save_plot, get_16_colors


"""
G.Onnis, 11.2015
    revised, 04.2017, 07.2017

Tecott Lab UCSF
"""



# def get_breakfast_data(experiment, level, err_type='stdev', ONSET=True, 
#         num_mins=15, tbin_size=5, days=None, cycle='24H'):
#     E = experiment
    
#     print "%s..\nlevel: %s\nerr_type: %s\nONSET: %s\ncycle: %s" %(
#             get_breakfast_data.__name__, level, err_type, ONSET, cycle)
#     if ONSET:
#         print "num_mins: %d" %num_mins
        
#     num_items = get_num_items(E, level)

#     mins = 15
#     num_bins = int(mins*60 / tbin_size)
#     avgs = np.zeros((num_items, 2, num_bins))
#     errs = np.zeros((num_items, 2, num_bins))

#     c = 0
#     for act in ['F', 'W']:

#         s_data, s_labels, m_data, m_labels, md_data, md_labels = \
#                 E.generate_breakfast_data(
#                     act=act, ONSET=ONSET, days=days, cycle=cycle, GET_AVGS=True)
        
#         if level == 'strain':
#             data = s_data[0]
#             yerr = s_data[1] if err_type == 'stdev' else s_data[2]
#             avgs[:, c, :], errs[:, c, :], labels = data, yerr, s_labels
        
#         # elif level == 'mouse':
#         #     data = m_data[0]
#         #     yerr = m_data[1] if err_type == 'stdev' else m_data[2]
#         #     avgs[:, :, c], errs[:, :, c], labels = data, yerr, m_labels
        
#         # elif level == 'mouseday':
#         #     avgs[:, :, c], errs[:, :, c], labels = md_data, np.zeros_like(md_data), md_labels

#         c +=1

#     return avgs, errs, labels



def set_legend(ax, hls, colors):
    h0 = hls[0][0], hls[1][0]
    l0 = hls[0][1], hls[1][1]
    tkw = {'numpoints':1, 'loc':'best', 'fontsize':6, 'handletextpad':1.2, 
            'labelspacing':.8, 'borderaxespad':1.5, 'frameon':False}
    leg = ax.legend(h0, l0, **tkw)
    for t, text in enumerate(leg.get_texts()):
        text.set_color(colors[t])


def set_layout(experiment, ax, act, color, ONSET, item_num,
        num_mins=15, tbin_size=5, CUMULATIVE=False):
    
    xlims = (-.2, num_mins) if ONSET else (-num_mins, .2)
    major_xticks, minor_xticks = (5, 1) if num_mins > 5 else (1, .5)
    ax.xaxis.set_major_locator(MultipleLocator(major_xticks))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_xticks))

    fontsize = 10
    if act == 'F':
        ylims = (0, .8) if ONSET else (0, .5)
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


def draw_subplot(experiment, data, labels, ONSET=True, num_mins=15, tbin_size=5):
    E = experiment

    figsize, nrows, ncols, _, _ = get_subplot_specs(E, num_subplots=len(E.groups))
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=sharex, sharey=sharey)

    act = ['F', 'W']
    fd_text = ['Feeding', 'Drinking']    
    colors = [E.fcolors[x][0] for x in act]
        
    every_tbins = 2 if num_mins > 5 else 1
    xticklim = (0, 15) if ONSET else (-15, 0)
    xs = np.arange(xticklim[0], xticklim[1], tbin_size * every_tbins / 60.)
    
    avgs = data[:, :, 0]
    errs = data[:, :, 1]

    hls = []
    for c in xrange(avgs.shape[0]): 
        try:
            ax0 = axes.flatten()[c]
            ax1 = ax0.twinx() 

            k = 0
            for ax in [ax0, ax1]:             
                # plotting every 5 tbins
                ax.errorbar(xs, avgs[c, ::every_tbins, k], yerr=errs[c, ::every_tbins, k], 
                    lw=.3, color=colors[k], label=fd_text[k], #fmt='.', ms=.3, 
                    elinewidth=.5, capsize=.5, capthick=.2, zorder=5-k)

                set_layout(E, ax, act[k], colors[k], ONSET, c, num_mins, tbin_size)
                if c == 0:
                    h, l = ax.get_legend_handles_labels()
                    hls.append([h[0][0], l[0]])
                k +=1
            
            ax.set_title(subtitles[c], fontsize=10)  
            if c == 0:
                set_legend(ax, hls, colors)

        except IndexError:
            ax.axis('off')
            continue

    # set subplot labels
    on_text = 'from AS onset' if ONSET else 'to AS offset'
    xlabel = 'Time ' + on_text + ' [min]'
    ylabel = 'Probability'
    subplot_labels(E, fig, xlabel, ylabel, fig_title)

    plt.subplots_adjust(bottom=.12, hspace=0.6, wspace=0.3)

    return fig


def plot_breakfast(experiment, cycle='24H', level='group', err_type='sd', ONSET=True, 
        num_mins=15, tbin_size=5, days=None, plot_type='breakfast', ADD_SOURCE=True):
    """breakfast hypothesis
    """
    E = experiment

    # directory
    text = 'AS_onset' if ONSET else 'AS_offset'
    dirname = E.figures_dir + 'breakfast/%s/' %text
    if not os.path.isdir(dirname): os.makedirs(dirname)

    print "%s, level: %s, err_type: %s, cycle: %s" %(
            plot_breakfast.__name__, level, err_type, cycle)

    data_F, _ = E.generate_breakfast_data(cycle, level, act='F', err_type=err_type, 
                                                ONSET=ONSET, days=days)
    data_W, labels = E.generate_breakfast_data(cycle, level, act='W', err_type=err_type, 
                                                ONSET=ONSET, days=days)
    stop
    # data = np.tile(np.zeros_like(data[:, :, np.newaxis]), (1,1,2))

    if level == 'group':
        # fig_title = 'Probability of feeding and drinking, across %s\n%s_days: %d to %d' %(
        #                 cycle, E.use_days, E.daysToUse[0], E.daysToUse[-1]) \
        #             + '\nstrains, avg$\pm$%s' %err_type
        
        # subtitles = [x for x in E.strain_names]

        fname = dirname + '%s_%s_%dstrains_%s' %(
                            plot_type, text, E.num_strains, cycle)     

        fig = draw_subplot(E, data, ONSET, num_mins, fname)

        save_plot(fname, fig)





# comparison plot

def set_compare_legend(ax, colors):
    _h, l = ax.get_legend_handles_labels()    
    h = [x[0] for x in _h] # remove the errorbars
    tkw = {'numpoints':1, 'loc':'best', 'fontsize':6, 'handletextpad':1.2, 
            'labelspacing':.8, 'frameon':False}
    leg = ax.legend(h, l, **tkw)
    for t, text in enumerate(leg.get_texts()):
        text.set_color(colors[t])


def set_compare_layout(experiment, ax, act, color, ONSET, item_num,
        num_mins=15, tbin_size=5, CUMULATIVE=False):
    
    xlims = (-.2, num_mins) if ONSET else (-num_mins, 0.2)
    major_xticks, minor_xticks = (5, 1) if num_mins > 5 else (1, .5)
    ax.xaxis.set_major_locator(MultipleLocator(major_xticks))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_xticks))

    fontsize = 10
    if act == 'F':
        ylims = (0, .8) if ONSET else (0, .5)
        major_yticks, minor_yticks = (.2, .1) if ONSET else  (.1, .05)

    elif act == 'W':
        ylims = [0, 0.21]
        major_yticks, minor_yticks = .05, .025

    ax.yaxis.set_major_locator(MultipleLocator(major_yticks))
    ax.yaxis.set_minor_locator(MultipleLocator(minor_yticks))

    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.spines['bottom'].set_linewidth(0.1)

    ax.tick_params(axis='x', which='both', labelsize=6)
    ax.tick_params(axis='y', which='both', labelsize=6, pad=1)        
    ax.tick_params(axis='both', which='major', length=3.5, width=.4, direction='out', pad=1)
    ax.tick_params(axis='both', which='minor', length=2, width=.4, direction='out', pad=1)


def draw_subplot_compare(experiment, avgs, errs, fig_title, subtitles, ONSET=True, 
        num_mins=15, tbin_size=5, ADD_SOURCE=False):
    E = experiment

    figsize, nrows, ncols, _, _ = get_subplot_specs(E, num_subplots=2)
    
    if E.num_strains == 2:
        pass
        # colors = [[get_16_colors()[x] for x in idx] for idx in [[2, 3, 8, 9], [0, 1, 14, 15]]
    elif E.num_strains == 4:
        colors = [[get_16_colors()[x] for x in idx] for idx in [[2, 3, 8, 9], [0, 1, 14, 15]]]
    elif E.num_strains == 16:
        colors = get_16_colors()
    # probability
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    
    every_tbins = 2 if num_mins > 5 else 1
    xticklim = (0, 15) if ONSET else (-15, 0)
    xs = np.arange(xticklim[0], xticklim[1], tbin_size * every_tbins / 60.)
    
    k = 0
    for act in ['F', 'W']:
        ax = axes[k]
        for c in xrange(avgs.shape[0]):   
            # plotting every 5 tbins
            ax.errorbar(xs, avgs[c, ::every_tbins, k], yerr=errs[c, ::every_tbins, k], 
                lw=.3, color=colors[k][c], label=E.strain_names[c],
                elinewidth=.5, capsize=.5, capthick=.2)

        set_compare_layout(E, ax, act, colors[k][c], ONSET, k, num_mins, tbin_size)   
        set_compare_legend(ax, colors[k])
        ax.set_title(subtitles[k], fontsize=10)   

        k += 1

    # set subplot labels
    on_text = 'from AS onset' if ONSET else 'to AS offset'
    xlabel = 'Time ' + on_text + ' [min]'
    ylabel = 'Probability'
    subplot_labels(fig, xlabel, ylabel, fig_title, ADD_SOURCE)

    plt.subplots_adjust(bottom=.12, hspace=0.6, wspace=0.3)

    return fig


def plot_breakfast_comparison(experiment, level='strain', err_type='stderr', ONSET=True,
        num_mins=15, tbin_size=5, days=None, ADD_SOURCE=True):
    """ all groups in one plot
    """
    E = experiment

    print "%s..\nlevel: %s\nerr_type: %s\nONSET: %s" %(
            plot_breakfast.__name__, level, err_type, ONSET)
    if ONSET:
        print "num_mins: %d" %num_mins

    # days to use
    days_to_use = E.daysToUse if days is None else days
    _, num_md_ok = E.count_mousedays(days=days_to_use)

    # load data
    avgs, errs, labels = get_breakfast_data(
                            E, level, err_type, ONSET=ONSET, 
                            num_mins=num_mins, days=days_to_use)

    # directory
    text = 'AS_onset' if ONSET else 'AS_offset'
    dirname = E.figures_dir_subpar + 'breakfast/%s/%s_days/' %(text, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)

    if level == 'strain':
        fig_title = 'Probability of feeding and drinking, across 24H\n%s_days: %d to %d' %(
                        E.use_days, E.daysToUse[0], E.daysToUse[-1]) \
                    + '\nstrains, avg$\pm$%s' %err_type
        
        subtitles = ['Feeding', 'Drinking']
        fig = draw_subplot_compare(E, avgs, errs, fig_title, subtitles, ONSET, 
                            num_mins, ADD_SOURCE=ADD_SOURCE)

        fname = dirname + 'group_comparison_%s_probability_24H_%dstrains_first_%dmins_binsize%ds_%s' %(
                            text, E.num_strains, num_mins, tbin_size, err_type)     
        save_plot(fname, fig)



