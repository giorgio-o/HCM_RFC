
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import os

from ceppa.util.intervals import Intervals
from ceppa.util.my_utils import print_progress
from ceppa.visualizations.plotting_utils import get_subplot_specs, remove_axes_not_used, subplot_labels, save_plot, add_source


"""
G.Onnis, 04.2017

Tecott Lab UCSF
"""


def set_layout(ax, level, EARLY, num_mins=15):
    if not EARLY:
        major_ticks = 60    # every 30
        minor_ticks = 20
    else:
        ax.set_xlim([0, num_mins])
        major_ticks = 5
        minor_ticks = 1
        if num_mins <=5:
            major_ticks = 1
            minor_ticks = .25

    ax.xaxis.set_major_locator(MultipleLocator(major_ticks))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_ticks))
    
    ax.yaxis.set_major_locator(MultipleLocator(50))
    ax.yaxis.set_minor_locator(MultipleLocator(25))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.spines['bottom'].set_linewidth(0.1)

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.tick_params(axis='x', which='both', labelsize=6)
    ax.tick_params(axis='y', which='both', labelsize=6, pad=1)        
    ax.tick_params(axis='both', which='major', length=2.5, width=.4, direction='out', pad=1)
    ax.tick_params(axis='both', which='minor', length=1.5, width=.4, direction='out', pad=1)


def plot_mouse_AS_structure(experiment, level, mouse, ax, colors,
        EARLY=False, num_mins=15, days=None, cycle='24H'):
    
    E = experiment 

    days_to_use = E.daysToUse if days is None else days

    AS_list = mouse.generate_AS_structure(days=days_to_use, cycle=cycle)

    lws = [1.5, 1.5, 1.5, .3] if level =='mouse' else [.5, .5, .5, .1]
    k = 0
    for fwmo_arrays in AS_list:
        ypos = len(AS_list) - k
        col = 0
        for arr in fwmo_arrays:
            for xs in arr:
                ax.plot(xs/60, [ypos, ypos], lw=lws[col], 
                        color=colors[col])
            col +=1

        print_progress(k, len(AS_list))
        k +=1
    
    set_layout(ax, level, EARLY, num_mins)
    subtitle = 'M%d' %(mouse.mouseNumber)
    ax.set_title(subtitle, fontsize=10)
    plt.subplots_adjust(hspace=.4)


def set_legend(fig, colors):
    labels = ['Feed', 'Drink', 'Move', 'Other']
    F, W, M, other = [mpl.lines.Line2D([], [], color=color, label=label) \
                        for color, label in zip(colors, labels)]

    handles = [F, W, M, other]
    labels = [h.get_label() for h in handles] 
    tkw = {'ncol':1, 'fontsize':8, 'bbox_to_anchor':[0.85, .33], 'frameon':False}
    leg = fig.legend(handles=handles, labels=labels, **tkw) 
    for t, text in enumerate(leg.get_texts()):
        text.set_color(colors[t])

    # tkw = {'ncol':2, 'numpoints':1, 'bbox_to_anchor': [.8, .1], 'fontsize':8, 'handletextpad':.8, 
    #         'labelspacing':.3, 'borderaxespad':.5, 'frameon':False}



def plot_within_AS_structure(experiment, level='strain', EARLY=True, num_mins=15, 
        days=None, cycle='24H', ADD_SOURCE=True):#, s_start=0):
    E = experiment

    print "%s, level: %s, EARLY: %s, %s" %(
        plot_within_AS_structure.__name__, level, EARLY, cycle)
    if EARLY: print "first %d minutes" %num_mins

    text = 'full_AS' if not EARLY else 'first_%dmin' %num_mins

    labels = ['F', 'W', 'M', 'other']
    colors = [E.fcolors[x][0] for x in labels]
    colors[3] = E.fcolors['other'][1]

    if level == 'strain':
        # dirname = E.figures_dir_subpar + 'within_AS/examples/'
        dirname = E.figures_dir_subpar + 'within_AS/%s_days/%s/%s/%s/' %(
            E.use_days, level, cycle, text)
        if not os.path.isdir(dirname): os.makedirs(dirname)

        for group in E.groups:#[s_start:s_start+4]:
            print '%d: %s' %(group.number, group.name)

            mice = E.get_mouseNumbers_from_groupNumber(group.number)

            figsize, nrows, ncols, sharex, sharey = get_subplot_specs(E, num_subplots=len(mice))
            fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=sharex, sharey=sharey)
            
            m = 0
            for mouse in group.individuals:
                if not mouse.ignored:
                    print mouse
                    ax = axes.flatten()[m]
                    plot_mouse_AS_structure(E, level, mouse, ax, colors, 
                                                EARLY, num_mins, days, cycle)
                    m += 1

            remove_axes_not_used(group, axes, nrows, ncols, m)

            set_legend(fig, colors)

            title = '%s: %s, %s' %(group.name, E.use_days, cycle)
            fig.suptitle(title, y=1.03)
            fig_title = ''
            # fig_title = 'Within-AS structure, across %s\ngroup%d: %s\n%s_days: %d to %d' %(
            #                 cycle, group.number, E.strain_names[group.number], E.use_days, E.daysToUse[0], E.daysToUse[-1])
            xlabel = 'Time from AS onset [min]'
            ylabel = 'AS sorted by duration'
            subplot_labels(E, fig, xlabel, ylabel, fig_title, txpad=-0.03, typad=.03)

            fname = dirname + 'within_AS_structure_strain%d_%s_%s' %(
                        group.number, text, cycle)
            save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, ypad=-.04)

    elif level == 'mouse':

        for group in E.groups:#[s_start:s_start+4]:
            print '%d: %s' %(group.number, group.name)

            dirname = E.figures_dir_subpar + 'within_AS/%s_days/%s/%s/%s/strain%d/' %(
                                            E.use_days, level, cycle, text, group.number)
            if not os.path.isdir(dirname): os.makedirs(dirname)

            for mouse in group.individuals:
                if not mouse.ignored:
                    print mouse
                    figsize = get_subplot_specs(E)
                    fig, ax = plt.subplots(figsize=figsize)

                    plot_mouse_AS_structure(E, level, mouse, ax, colors,
                                                EARLY, num_mins, days, cycle)

                    fig_title = 'Within-AS structure, across %s\ngroup %d: %s\n%s_days: %d to %d' %(
                                cycle, group.number, E.strain_names[group.number], E.use_days, E.daysToUse[0], E.daysToUse[-1])
                    xlabel = 'Time from AS onset [min]'
                    ylabel = 'AS sorted by duration'
                    subplot_labels(E, fig, xlabel, ylabel, fig_title)
                    if ADD_SOURCE:
                        add_source(fig)

                    fname = dirname + 'within_AS_structure_individual%d_%s_%s' %(
                                mouse.mouseNumber, text, cycle)
                    save_plot(fname, fig)



