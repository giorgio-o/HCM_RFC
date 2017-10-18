import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

# import matplotlib.patches as patches

from ceppa.util.my_utils import get_num_items
from ceppa.visualizations.plotting_utils import get_subplot_specs, subplot_labels, save_plot
from ceppa.visualizations.time_budgets import get_time_budgets_data, plot_as_a_pie

"""
G.Onnis, 04.2017

Tecott Lab UCSF
"""


def set_legend(fig, h, l):
    tkw = {'ncol':3, 'fontsize':8, 'bbox_to_anchor':[0.72, .12], 'frameon':False}
    fig.legend(h[::-1], l[::-1], **tkw)     


def draw_subplot(experiment, avgs, fig_title, subtitles, plot_type):
    E = experiment

    figsize, nrows, ncols, _, _ = get_subplot_specs(E, num_subplots=4)

    labels = ['M', 'F', 'W', 'other', 'IS']     
    colors = [E.fcolors[x][0] for x in labels]

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    for c in xrange(avgs.shape[0]): 

        ax = axes.flatten()[c]
        if plot_type == 'bar':
            stop

        elif plot_type == 'pie':
            plot_as_a_pie(ax, avgs[c], colors, labels, subtitles[c])
        
        if c == 0:
            h, l = ax.get_legend_handles_labels()



    set_legend(fig, h, l)

    subplot_labels(E, fig, xlabel='', ylabel='', fig_title=fig_title, txpad=.1, typad=.03)
    plt.subplots_adjust(hspace=0.4, wspace=.1)

    return fig


def plot_figure(experiment, level='strain', err_type='stdev', plot_type='pie', ADD_SOURCE=True):

    E = experiment

    cycles = E.cycles
    use_days = ['chow', 'HiFat']
    days_to_use = [E.chowDayNumbers, E.HiFatDayNumbers]

    print "days_to_use: %s" %days_to_use

    # load data
    num_items = get_num_items(E, level)
    num_slices = 5
    all_avgs = np.zeros((num_items, len(days_to_use), len(cycles), num_slices))  # DC/LC
    all_errs = np.zeros((num_items, len(days_to_use), len(cycles), num_slices))
    
    for d, days in enumerate(days_to_use):
        for c, cycle in enumerate(cycles):
            avgs, errs, labels = get_time_budgets_data(
                                    E, level, err_type, 
                                    cycle=cycle, days=days)
            all_avgs[:, d, c, :], all_errs[:, d, c, :] = avgs, errs

    idx = [0, 2, 1, 3]
    all_avgs = all_avgs.reshape(-1, len(cycles), num_slices)[idx]
    all_errs = all_errs.reshape(-1, len(cycles), num_slices)[idx]

    # directory
    dirname = E.figures_dir_subpar + 'time_budgets/fig2/'
    if not os.path.isdir(dirname): os.makedirs(dirname)

    if level == 'strain':
        for c, cycle in enumerate(cycles):
            # fig_title = ''
            fig_title = 'Time budgets, %s\n%d strains avgs' %(cycle, E.num_strains)
            
            subtitles = ['%s: %s, %s' %(x, y, cycle) for y in use_days for x in E.strain_names]
            fig = draw_subplot(E, all_avgs[:, c, :], fig_title, subtitles, plot_type)
            fname = dirname + 'time_budgets_%s_%dstrains_%s' %(cycle, E.num_strains, plot_type)
            
            save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, xpad=.05, ypad=0)

        print "figures saved to: %s" %fname



