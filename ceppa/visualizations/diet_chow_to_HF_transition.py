
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import os

from ceppa.visualizations.within_AS_structure import set_layout
from ceppa.visualizations.plotting_utils import get_subplot_specs, subplot_labels, save_plot
from ceppa.util.my_utils import print_progress

"""
G.Onnis, 05.2017

Tecott Lab UCSF
"""


def plot_strain_AS_structure(experiment, level, group, ax, AS_list, day, num_AS, num_mins):
    E = experiment 

    colors = [E.fcolors[x][0] for x in ['F', 'W', 'M']]
    lw = 1.5 if level =='mouse' else .5
    k = 0
    for fwm_arrays in AS_list:
        ypos = len(AS_list) - k
        col = 0
        for arr in fwm_arrays:
            for xs in arr:
                ax.plot(xs/60, [ypos, ypos], lw=lw, color=colors[col])
            col +=1
        print_progress(k, len(AS_list))
        k +=1
    print
    set_layout(ax, level, num_mins)
    ax.set_title('%s, day%d' %(E.strain_names[group.number], day), fontsize=10)
    if day == E.transition1DayNumber:
        ax.text(.7, .7, 'diet\ntransition', fontsize=10, transform=ax.transAxes)


def plot_first_ASs(experiment, level='strain', days=None, num_AS=5, num_mins=5, ADD_SOURCE=True):
    
    E = experiment

    days_to_use = E.daysToUse if days is None else days
    text = 'all ASs' if num_AS is None else str(num_AS)
    print "%s\nlevel: %s\ndays: %r\nnum_AS: %s\nnum_min: %d" %(
        plot_first_ASs.__name__, level, days, text, num_mins)

    text2 = 'all_ASs' if num_AS is None else 'first_%dASs' %num_AS
    
    if level == 'strain':

        dirname = E.figures_dir_subpar + 'within_AS/%s_days/' %E.use_days
        if not os.path.isdir(dirname): os.makedirs(dirname)

        fig, axes = plt.subplots(nrows=len(days_to_use), ncols=len(E.groups), figsize=(7, 10), 
                                sharex=True, sharey=True)        
        c = 0
        for day in days_to_use:
            for group in E.groups:
                print 'day%d, group:%d, %s' %(day, group.number, group.name)
                ax = axes.flatten()[c]

                AS_list = group.generate_AS_structure(day, num_AS)

                plot_strain_AS_structure(E, level, group, ax, AS_list, day, num_AS, num_mins)
                c +=1

        plt.subplots_adjust(bottom=.08, top=.92, hspace=.4)
        fig_title = 'Within-AS structure\n%s\nacclimation to transition days: %dto%d' %(
                    text2, days_to_use[0], days_to_use[-1])
        xlabel = 'Time from AS onset [min]'
        ylabel = 'AS sorted by duration'
        subplot_labels(fig, xlabel, ylabel, fig_title, ADD_SOURCE)

        fname = dirname + 'within_AS_structure_strains_%s_%s_first_%dmin.pdf' %(E.use_days, text2, num_mins)
        save_plot(fname, fig)

    # elif level == 'mouse':

    #     for group in E.groups:#[s_start:s_start+4]:
    #         print '%d: %s' %(group.number, group.name)

    #         dirname = E.figures_dir_subpar + 'within_AS/%s_days/%s/%s/strain%d/' %(
    #                                                 E.use_days, level, text, group.number)
    #         if not os.path.isdir(dirname): os.makedirs(dirname)

    #         for mouse in group.individuals:
    #             if not mouse.ignored:
    #                 print mouse
    #                 figsize = get_subplot_specs(E)
    #                 fig, ax = plt.subplots(figsize=figsize)

    #                 plot_mouse_AS_structure(E, level, mouse, ax, EARLY, num_mins)

    #                 fig_title = 'Within-AS structure, across 24H\ngroup %d: %s\n%s_days: %d to %d' %(
    #                             group.number, E.strain_names[group.number], E.use_days, E.daysToUse[0], E.daysToUse[-1])
    #                 xlabel = 'Time from AS onset [min]'
    #                 ylabel = 'AS sorted by duration'
    #                 subplot_labels(fig, xlabel, ylabel, fig_title, ADD_SOURCE)

    #                 fname = dirname + 'within_AS_structure_individual%d_%s.pdf' %(mouse.mouseNumber, text)
    #                 save_plot(fname, fig)
