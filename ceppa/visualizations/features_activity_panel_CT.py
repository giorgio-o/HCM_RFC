import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import os
import csv

from ceppa.visualizations.features_panel_CT import get_two_group_features_colors, set_axis_layout

from ceppa.util.my_utils import get_CT_bins, get_tbins_string, get_CT_ticks_labels
from ceppa.visualizations.plotting_utils import add_titles_notes
from ceppa.visualizations.plotting_utils import add_xylabels, ax_cleanup, plot_colored_background, save_plot

"""
G.Onnis, 09.2017

Tecott Lab UCSF
"""

def get_ymaxs(data):
    max_avg = data[:, :, :, :, 0].max(3).max(1).max(0)
    max_err = data[:, :, :, :, 1].max(3).max(1).max(0)
    return max_avg + max_err


def set_panel_layout(E, fig, err_type, tbin_type='12bins'):

    # legend annotation
    if tbin_type.endswith('bins'):
        fig.text(.7, 1.1, 'gray background: Dark Cycle', fontsize=8)

    xlabel = 'Circadian Time'
    add_xylabels(fig, xlabel=xlabel, xypad=-.15, labelsize=10)

    days_string = E.get_days_to_use_text()
    fig_title = '%s Experiment\nFeatures vs CT, 12bins group avg$\pm$%s\n%s days: %s' %(
                    E.short_name, err_type,
                    E.use_days.replace('_', '-').title(), days_string
                    )

    add_titles_notes(E, fig, title=fig_title, typad=.1)   
    plt.subplots_adjust(hspace=.6, wspace=.6)


# def draw_group_features(E, data, act, features, bin_type, err_type, fname,
#         plot_type='features', ADD_SOURCE=False):

#     figsize = (17.6, 4.8)
#     nrows, ncols = len(E.daysToUse), len(features)
#     fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)

#     other_color = E.fcolors['other'][0]
#     xticks, xlabels = get_CT_ticks_labels(bin_type, SHIFT=E.BIN_SHIFT, tshift=E.binTimeShift)
#     xs = xticks[:-1] +1
    
#     ymaxs = get_ymaxs(data, err_type)

#     cnt = 0
#     for n in xrange(nrows):
#         for m in xrange(ncols):
#             ax = axes.flatten()[cnt]
            
#             feature = features[m]
#             colors = get_two_group_features_colors(E, feature)

#             subtitle = '%s %s' %(feature, E.plot_settings_dict[feature]['unit'])

#             # here: num_strains, len(E.daysToUse), len(features), num_bins, 2
#             for g in xrange(E.num_strains):

#                 if bin_type.endswith('bins'):
#                     tkw = {'fmt':'o-', 'ms':2, 'elinewidth':.5, 'capsize':1}
#                     ax.errorbar(xs, data[g, n, m, :, 0], yerr=data[g, n, m, :, 1], 
#                                 color=colors[g], mec=colors[g], **tkw)
#                 else:
#                     stop

#             # same y-axis, per feature
#             # ax.set_ylim([0, ymaxs[m]])
#             set_axis_layout(E, ax, bin_type)
            
#             # y-labels: days
#             if m < 1:
#                 bbox = ax.get_position()
#                 fig.text(.07, bbox.y1 - (bbox.y1-bbox.y0)/2., 'day %d' %E.daysToUse[n], 
#                             ha='left', fontsize=10)
#             # plot subtitle
#             if n < 1:
#                 ax.set_title(subtitle, fontsize=10, y=1.05)

#             cnt += 1

#     set_panel_layout(E, fig, err_type, tbin_type='12bins')

#     save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.1)
#     plt.close()


def draw_group_features_days_collapse(E, data, act, features, bin_type, err_type, fname,
        plot_type='features', ADD_SOURCE=False):

    figsize = (17.6, 2.4)
    nrows, ncols = E.num_strains, len(features)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)

    other_color = E.fcolors['other'][0]
    xticks, xlabels = get_CT_ticks_labels(bin_type='12bins', SHIFT=E.BIN_SHIFT, tshift=E.binTimeShift)
    xs = xticks[:-1] +1
    
    ymaxs = get_ymaxs(data)

    cnt = 0
    for n in xrange(nrows):

        for m in xrange(ncols):
            ax = axes.flatten()[cnt]
            
            feature = features[m]
            subtitle = '%s %s' %(feature, E.plot_settings_dict[feature]['unit'])

            # idx = [0, 1, 2, 3]
            # colors = [E.fcolors['AS'].values()[x] for x in idx] if m < 3 else [E.fcolors['F'].values()[x] for x in idx]
            colors = E.fcolors['AS'].values() if m < 3 else E.fcolors[act].values()
            colors[0] = '.4'
            colors[3] = '.7'
            zord = [0, 1, 2, 0]
            
            if bin_type.endswith('bins'):
                tkw = {'fmt':'o-', 'ms':2, 'elinewidth':.5, 'capsize':1}
                for d in xrange(len(E.daysToUse)):
                    ax.errorbar(xs, data[n, d, m, :, 0], yerr=data[n, d, m, :, 1], 
                                color=colors[d], mec=colors[d], 
                                label='day%d' %E.daysToUse[d], 
                                zorder=zord[d], **tkw)
            else:
                stop

            # same y-axis, per feature
            ax.set_ylim([0, ymaxs[m]])
            set_axis_layout(E, ax, bin_type)

            if m < 1:
                texts =[
                        '0: %s\ncontrol' %E.strain_names[0],
                        '1: %s\nknock-out' %E.strain_names[1]
                        ]
                bbox = ax.get_position()
                fig.text(.06, bbox.y1 - (bbox.y1-bbox.y0)/2., texts[n], 
                            ha='left', va='center', fontsize=10)

            if n < 1:
                # plot subtitle
                ax.set_title(subtitle, fontsize=10, y=1.05)
                # legend
                if m in [0, 3]:
                    # legend
                    ltkw = {'numpoints':1, 'bbox_to_anchor':[.25, 2, .1, .05], 'fontsize':6, 'handletextpad':.8, 
                        'labelspacing':.3, 'borderaxespad':.5, 'frameon':False}
                    ax.legend(**ltkw)

            cnt += 1

    set_panel_layout(E, fig, err_type, tbin_type='12bins')


    
    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.15)
    plt.close()


def plot_features_activity_panel(experiment, level='group', act='F', bin_type='12bins', err_type='sem',
        plot_type= 'features', ADD_SOURCE=True):   

    E = experiment

    print "%s, level: %s, bin_type: %s, err_type: %s, %s days" %(
            plot_features_activity_panel.__name__, level, bin_type, err_type, E.use_days)

    # select 10 features, AS + act
    features = E.features_by_activity_dict['AS'] + E.features_by_activity_dict[act]
    
    string_shift = '_shifted%+02dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    dirname = E.figures_dir + '%s/vectors/panels_CT/per_activity/%s%s/%s/%s_days/%s/' %(
                                plot_type, bin_type, string_shift, level, E.use_days, err_type)
    if not os.path.isdir(dirname): os.makedirs(dirname)

    # load data  
    # features, groups/mice/mousedays, 3cycles/12bins, avg/err
    data, labels = E.load_features_vectors(features, 
                                            level='mouseday', 
                                            bin_type=bin_type
                                            )
    # days, features, tbins
    data_ = data.swapaxes(0, 1)[:, :, :, 0]     # avg only
    # data_ = data.swapaxes(0, 1).swapaxes(1, 2)[:, :, :, 0]     # avg only

    num_bins = data.shape[2]
    
    if level == 'group':
        arr = np.zeros([E.num_strains, len(E.daysToUse), len(features), num_bins, 2])
        for g in xrange(E.num_strains):
            idx = labels[:, 0] == g
            g_data, g_labels = data_[idx], labels[idx]

            d = 0
            for day in E.daysToUse:
                idx2 = g_labels[:, 2] == day
                day_data = g_data[idx2]
                avgs = np.nanmean(day_data, axis=0)
                stds = np.nanstd(day_data, axis=0)
                errs = stds if err_type == 'sd' else stds / np.sqrt(day_data.shape[0] - 1)
                arr[g, d, :, :, 0] = avgs
                arr[g, d, :, :, 1] = errs
                d += 1
        
        # fname = dirname + '%s_panel_%s_activity_CT_%s_%s_yfree' %(plot_type, act, level, bin_type)
        # draw_group_features(E, arr, act, features, bin_type, err_type, fname, 
        #                         ADD_SOURCE=ADD_SOURCE)
        
        fname = dirname + '%s_panel_%s_activity_CT_%s_%s_2_yfree' %(plot_type, act, level, bin_type)
        draw_group_features_days_collapse(E, arr, act, features, bin_type, err_type, fname, 
                                ADD_SOURCE=ADD_SOURCE)
