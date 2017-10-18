
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import csv
# import matplotlib.patches as patches

from ceppa.util.my_utils import get_num_items
from ceppa.visualizations.plotting_utils import get_subplot_specs, get_figure_titles, add_titles_notes, save_plot
# from ceppa.visualizations.plotting_utils import get_figure_titles, add_titles_notes, get_subplot_specs
# from ceppa.visualizations.plotting_utils import add_xylabels, ax_cleanup, plot_colored_background, save_plot


"""
G.Onnis, 04.2017
    revised, 07.2017

Tecott Lab UCSF
"""



def plot_as_a_pie(ax, avgs, colors, labels, subtitle):
    patches, texts, autotexts = ax.pie(avgs,
        labels=labels,
        colors=colors, 
        radius=1,
        autopct="%3.1f%%",                
        pctdistance=1.3, 
        shadow=False,       
        # labeldistance=1.5,   # out
        )
    
    for patch in patches:
        patch.set_edgecolor('.15')
        patch.set_lw(0.1)

    for text in autotexts:
        text.set_fontsize(6)

    for text in texts:
        text.set_fontsize(0)
    
    #title
    ax.set_title(subtitle, fontsize=10, y=1.03) 
    ax.set_aspect('equal')


def set_legend(fig, h, l):
    tkw = {'ncol':3, 'fontsize':8, 'bbox_to_anchor':[0.85, .21], 'frameon':False}
    fig.legend(h[::-1], l[::-1], **tkw)     


def draw_subplot(experiment, avgs, labels, level, cycle, err_type, fname, plot_subtype, 
        plot_type, ADD_SOURCE=True):
    E = experiment
    
    figsize, nrows, ncols, _, _ = get_subplot_specs(E, num_subplots=len(E.groups))
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    
    slice_labels = ['M', 'F', 'W', 'other', 'IS']     
    colors = [E.fcolors[x][0] for x in slice_labels]

    title, subtitles  = get_figure_titles(E, labels, level, cycle, err_type, plot_type)

    for c in xrange(avgs.shape[0]): 
        
        try:
            ax = axes.flatten()[c]
            if plot_subtype == 'bar':
                stop

            elif plot_subtype == 'pie':
                plot_as_a_pie(ax, avgs[c], colors, slice_labels, subtitles[c])
                
            if c == 0:
                h, l = ax.get_legend_handles_labels()

        except IndexError:
            ax.axis('off')
            continue

        set_legend(fig, h, l)

        # plt.subplots_adjust(hspace=.4)

    add_titles_notes(E, fig,
                    title=title,
                    typad=-.15,
                    tlxpad=0,
                    tlypad=-.15) 

    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, 
                labelsize=6, sypad=.25)
    


def plot_time_budgets(experiment, cycle='24H', level='group', err_type='sd', 
        days=None, plot_subtype='pie', plot_type='time_budgets', ADD_SOURCE=True):

    E = experiment

    dirname = E.figures_dir + '%s/%s/' %(plot_type, level)
    if not os.path.isdir(dirname): os.makedirs(dirname)

    print "%s, level: %s, err_type: %s, cycle: %s" %(
            plot_time_budgets.__name__, level, err_type, cycle)

    # load data  
    AS = False if cycle in ['24H', 'DC', 'LC'] else True
    data, labels = E.generate_time_budgets(cycle, level, err_type, AS, days=days)
    
    avgs = data[:, :, 0]

    #     num_slices = 5 if not AS else 4    #move, feed, drink, other_AS, inactive

    if level == 'group':
        
        fname = dirname + '%s_%dgroups_%s' %(plot_type, E.num_strains, cycle)
        
        fig = draw_subplot(E, avgs, labels, level, cycle, 
                            err_type, fname, plot_subtype, plot_type)



def write_data_to_csv(E, level='group', err_type='sd', plot_type='time_budgets'):
    
    dirname = E.figures_dir + '%s/%s/csv_files/' %(plot_type, level)
    if not os.path.isdir(dirname): os.makedirs(dirname)    
    
    print "%s..\nlevel: %s\nerr_type: %s" %(
        write_data_to_csv.__name__, level, err_type)

    # load data
    # AS = False if cycle in ['24H', 'DC', 'LC'] else True
    for cycle in ['24H', 'DC', 'LC']:
        data, labels = E.generate_time_budgets(cycle=cycle, level=level, err_type=err_type)
        
        avgs, errs = data[:, :, 0], data[:, :, 1]
        # percents
        percents = 100*(avgs.T/avgs.sum(1)).T
        # stop

        # headers
        cols = ['M', 'F', 'W', 'other', 'IS']     
        
        header01 = '%sExp\n%s, %s avg [secs], %s' %(E.short_name, plot_type, level, cycle)
        header02 = '%sExp\n%s, %s avg [%%], %s' %(E.short_name, plot_type, level, cycle)
        sub_header = ['group \ activity'] + cols

        if level == 'group':
            fname1 = 'time_budgets_%s_%s_secs.csv' %(level, cycle)
            fname2 = 'time_budgets_%s_%s_percents.csv' %(level, cycle)

        with open(dirname + fname1, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow([header01])
            # writer.writerow([header1])
            writer.writerow(sub_header)
            c = 0
            for row in avgs:
                writer.writerow(np.hstack(['%d: %s' %(
                    labels[c], E.strain_names[labels[c]]), 
                    ['%1.1f' %r for r in row]]))
                    # c += 1
                c += 1

        with open(dirname + fname2, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow([header02])
            # writer.writerow([header1])
            writer.writerow(sub_header)
            c = 0
            for row in percents:
                writer.writerow(np.hstack(['%d: %s' %(
                    labels[c], E.strain_names[labels[c]]), 
                    ['%1.3f' %r for r in row]]))
                    # c += 1
                c += 1    
        print "csv files saved to:\n%s" % dirname
            