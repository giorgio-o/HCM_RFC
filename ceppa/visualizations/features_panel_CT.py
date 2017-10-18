import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import os
import csv

from ceppa.util.my_utils import get_CT_bins, get_tbins_string, get_CT_xs, get_CT_ticks_labels
from ceppa.visualizations.plotting_utils import add_titles_notes
from ceppa.visualizations.plotting_utils import add_xylabels, ax_cleanup, save_plot


"""
G.Onnis, 11.2016
    upadted: 04.2016

Tecott Lab UCSF
"""

np.set_printoptions(precision=4, threshold=8000)


# # #old
# def set_panel_layout(E, fig, ax, feats, num_subplot, bin_type, xticks, xlabels, ymaxs):
#     if ymaxs is not None:
#         ax.set_ylim([0, ymaxs[num_subplot]])
        
#     if bin_type.endswith('cycles'):
#         rotation = 0
#         # xticks = [1, 2, 3]
#         # xlabels = ['24H', 'DC', 'LC']
#         ax.set_xlim([.3, 3.7])
#         labelsize = 8

#     elif bin_type.endswith('bins'):
#         x0, x1 = 5, 31
#         if E.BIN_SHIFT:
#             shift = E.binTimeShift / 3600 if E.binTimeShift < 0 else E.binTimeShift / 3600 + 1
#             x0 += shift
#             x1 += shift

#         if bin_type == '24bins':
#             xlabels[1::2] = ['' for i in range(len(xlabels)/2)]
        
#         ax.set_xlim([x0, x1])
#         DC_start, DC_end = my_utils.get_CT_bins(tbin_type='3cycles')[1]
#         plot_colored_background(ax, tstart=DC_start, tend=DC_end)
#         labelsize = 6

#     ax.set_xticks(xticks)
#     ax.set_xticklabels(xlabels, rotation='vertical')
#     # major_xticks, minor_xticks = (4, 2) #if bin_type == '12bins' else (24, 1)
#     # formatter = '%d' if not E.BIN_SHIFT else '%1.1f'
#     # ax.xaxis.set_major_locator(MultipleLocator(major_xticks))
#     # ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
#     # ax.xaxis.set_minor_locator(MultipleLocator(minor_xticks))
#     # fig.canvas.draw()
#     # # ax.set_xticklabels(ax.get_xticks())
#     # labels = [int(item.get_text()) for item in ax.get_xticklabels()]
#     # # labels = ax.get_xticklabels()
    
#     # labels[-2] = u'4'
#     # # stop
#     # ax.set_xticklabels(labels)

#     ylims = [0, 1] if feats[num_subplot] == 'ASP' else np.array(ax.get_ylim())
#     ax.set_ylim((0, ylims[1]))
#     ax.set_aspect('auto')
#     ax_cleanup(ax, labelsize=labelsize)

#     plt.subplots_adjust(left=0.1, right=0.88, hspace=0.6)#, wspace=0.15)


def set_axis_layout(E, ax, bin_type, labelsize=8):
    # if bin_type.endswith('bins'):
    #     # if bin_type == '12bins'
    #     major_xticks, minor_xticks = (4, 2)  
    #     # elif bin_type == '24bins':
    #     #     major_xticks, minor_xticks = (24, 1)
    # else:
    #     stop

    # formatter = '%d' if not E.BIN_SHIFT else '%1.1f'
    # ax.xaxis.set_major_locator(MultipleLocator(major_xticks))
    # ax.xaxis.set_major_formatter(FormatStrFormatter(formatter))
    # ax.xaxis.set_minor_locator(MultipleLocator(minor_xticks))
    xticks, xlabels = get_CT_ticks_labels(bin_type, SHIFT=E.BIN_SHIFT, tshift=E.binTimeShift)
    rotation = 0
    if E.BIN_SHIFT:
        labelsize = 2
        if bin_type.endswith('bins'):
            rotation = 90
        
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels, rotation=rotation)

    ax.set_xlim([xticks[0]-.5, xticks[-1]+.5])
    ax.set_ylim([0, ax.get_ylim()[1]])

    ax.tick_params(axis='both', which='both', labelsize=labelsize, direction='out')
    # DC grey background
    ax.axvspan(12, 24, fc='.9', ec='.9', zorder=-1)     
    ax_cleanup(ax)


def get_two_group_features_colors(E, feature):

    if feature.startswith('AS'):
        # colors = [E.fcolors['AS'].values()[x] for x in [1, 3]]
        color1 = E.fcolors['AS'][2]
    elif feature.startswith('T'):
        color1 = E.fcolors[feature[1:]][2]
        # colors = [E.fcolors[feature[1:]].values()[x] for x in [1, 3]]
    else:
        color1 = E.fcolors[feature[:1]][2]
        # colors = [E.fcolors[feature[:1]].values()[x] for x in [1, 3]]

    colors = ['.4', color1]
    return colors


def set_panel_layout(E, fig, err_type, tbin_type):
    fig.text(.6, .9, '0: %s, control, %s (grayscale)' %(E.strain_names[0], tbin_type), fontsize=8)
    fig.text(.6, .85, '1: %s, knock-out, %s (colors)' %(E.strain_names[1], tbin_type), fontsize=8)
    if tbin_type.endswith('bins'):
        fig.text(.6, .8, 'gray background: Dark Cycle', fontsize=8)

    xlabel = 'Circadian Time'
    add_xylabels(fig, xlabel=xlabel, xypad=-.02, labelsize=10)

    days_string = E.get_days_to_use_text()
    fig_title = '%s Experiment\nFeatures vs CT, 12bins, group avg$\pm$%s\n%s days: %s' %(
                    E.short_name, err_type,
                    E.use_days.replace('_', '-').title(), days_string
                    )

    add_titles_notes(E, fig, title=fig_title)   


def draw_group_features(E, data, labels, features, bin_type, err_type, fname,
        plot_type='features', ADD_SOURCE=False):

    figsize = (16, 4.8)
    nrows, ncols = 4, 7
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)

    other_color = E.fcolors['other'][0]

    xs = get_CT_xs(bin_type, SHIFT=E.BIN_SHIFT, tshift=E.binTimeShift)

    cnt = 0
    for n in xrange(nrows):
        for m in xrange(ncols):
            ax = axes.flatten()[n*ncols + m]
            if n == 0 and m >= 3:
                ax.axis('off')
                continue
            
            feature = features[cnt]
            colors = get_two_group_features_colors(E, feature)

            subtitle = '%s %s' %(feature, E.plot_settings_dict[feature]['unit'])
            
            for g in xrange(E.num_strains):
                if bin_type.endswith('bins'):
                    tkw = {'fmt':'o-', 'ms':2}#, 'elinewidth':.5, 'capsize':1}
                    mec = '.3' if g == 1 else colors[g]
                    ax.errorbar(xs, data[g, cnt, :, 0], yerr=data[g, cnt, :, 1], 
                        color=colors[g], mec=mec, **tkw)
                elif bin_type.endswith('cycles'):
                    bar_width = .25
                    ax.bar(xs+bar_width*g, data[g, cnt, :, 0], bar_width,
                        yerr=[[0,0,0], data[g, cnt, :, 1]],
                        color=colors[g], 
                        capsize=2,
                        ecolor=colors[g],
                        )
                
            set_axis_layout(E, ax, bin_type)

            ax.set_title(subtitle, fontsize=10)

            cnt += 1

    set_panel_layout(E, fig, err_type, bin_type)
    plt.subplots_adjust(hspace=.6, wspace=.3)
    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.02)





def plot_features_panel(experiment, level='group', bin_type='12bins', err_type='sd',  
        plot_type= 'features', ADD_SOURCE=True):   

    E = experiment

    print "%s, level: %s, bin_type: %s, err_type: %s, %s days" %(
            plot_features_panel.__name__, level, bin_type, err_type, E.use_days)

    features = E.features_by_activity
    
    string_shift = '_shifted%+02dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    dirname = E.figures_dir + '%s/vectors/panels_CT/%s%s/%s/%s_days/%s/' %(
                                plot_type, bin_type, string_shift, level, E.use_days, err_type)
    if not os.path.isdir(dirname): os.makedirs(dirname)

    # load data  
    # features, groups/mice/mousedays, 3cycles/12bins, avg/err
    data, labels = E.load_features_vectors(features, level, bin_type, err_type)
    data_ = data.swapaxes(0, 1) 
    
    if level == 'group':
        fname = dirname + '%s_panel_CT_%s_%s' %(plot_type, level, bin_type)
        draw_group_features(E, data_, labels, features, bin_type, err_type, fname, 
                                ADD_SOURCE=ADD_SOURCE)
            
    elif level == 'mouse':
        fname = dirname + '%s_panel_CT_%s_%s' %(plot_type, level, bin_type)
        draw_mouse_features(E, data_, labels, features, bin_type, err_type, fname, 
                                ADD_SOURCE=ADD_SOURCE)





def draw_mouse_features(E, data, labels, features, bin_type, err_type, fname,
        plot_type='features', ADD_SOURCE=False):

    figsize = (14.4, 4.8)
    nrows, ncols = 4, 7
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)

    other_color = E.fcolors['other'][0]
    xticks, xlabels = get_CT_ticks_labels(bin_type='12bins', SHIFT=E.BIN_SHIFT, tshift=E.binTimeShift)
    xs = xticks[:-1] +1
    
    for g in xrange(E.num_strains):
        cnt = 0
        for n in xrange(nrows):
            for m in xrange(ncols):
                ax = axes.flatten()[n*ncols + m]
                if n == 0 and m >= 3:
                    ax.axis('off')
                    continue
                
                feature = features[cnt]
                colors = get_two_group_features_colors(E, feature)

                subtitle = '%s %s' %(feature, E.plot_settings_dict[feature]['unit'])

                idx = labels[:, 0] == g
                data_, labels_ = data[idx], labels[idx]

                if bin_type.endswith('bins'):
                    tkw = {'fmt':'o-', 'ms':2, 'elinewidth':.5, 'capsize':1}
                    for mouse in xrange(idx.sum()):
                        ax.errorbar(xs, data[mouse, cnt, :, 0], yerr=data[mouse, cnt, :, 1], 
                                    color=colors[g], mec=colors[g], **tkw)
                else:
                    stop

                set_axis_layout(E, ax, bin_type)
                ax.set_title(subtitle, fontsize=10)

                cnt += 1
        
        set_panel_layout(E, fig, err_type, tbin_type='24H')

        save_plot(fname + '_group%d' %g, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.02)
        plt.close()




def write_panel_to_csv_collapse_over_days(experiment, level='mouseday', bin_type='12bins', err_type='sem', 
        plot_type='features'):
    """ mouseday level only
    """
    E = experiment

    features = E.features_by_activity
    num_features = len(features)
    days_to_use = E.daysToUse    
    num_days = len(days_to_use)

    string_shift = '_shifted%+02dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    dirname = E.figures_dir + '%s/vectors/panels_CT/csv_files/%s/%s_days/' %(
                                plot_type, bin_type, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    
    # load data  
    # features, groups/mice/mousedays, 3cycles/12bins, avg/err
    data, labels = E.load_features_vectors(features, level, bin_type, err_type)
    data_ = data.swapaxes(0, 1).swapaxes(1, 2)[:, :, :, 0]     # avg only
    
    if bin_type.endswith('bins'):
        tbins = get_tbins_string(bin_type)
        
    # headers
    feat_unit = ['%s %s' %(feat, E.plot_settings_dict[feat]['unit']) for feat in features]

        
    # PART I: mousedays
    headers = [
        ['%s Experiment' %E.short_name],
        ['%s, %s, %s' %(plot_type, level, bin_type)], 
        ['%s days: %s' %(E.use_days, E.daysToUse)]
        ]
    fname1  = dirname + '%s_panel_CT_%s_%s_%s_collapse_days.csv' %(plot_type, bin_type, level, E.use_days)
    sub_header = ['', 'group', 'mouse', 'day', 'tbin'] + feat_unit
    with open(fname1, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        for h in headers:
            writer.writerow(h)
        writer.writerow(sub_header)            

        cnt = 0
        for g in xrange(E.num_strains):
            idx = labels[:, 0] == g
            g_data, g_labels = data_[idx], labels[idx]
            
            for day in E.daysToUse:
                idx2 = g_labels[:, 2] == day
                day_data, day_labels = g_data[idx2], g_labels[idx2]
                
                b = 0
                for bin_data in day_data.swapaxes(0, 1):
                    c = 0
                    for row in bin_data:
                        if not np.isnan(row).all():
                            row_text = ['', day_labels[c, 0], day_labels[c, 1], day_labels[c, 2], tbins[b]]
                            writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                            c +=1 

                    writer.writerow('\n')
                    
                    avg = np.nanmean(bin_data, axis=0)
                    if not np.isnan(avg).all():
                        stdev = np.nanstd(bin_data, axis=0)
                        sem = stdev / np.sqrt(bin_data.shape[0]-1)
                        writer.writerow(['', '', '', '', 'Mean:'] + ['%1.4f' %r for r in avg])
                        writer.writerow(['', '', '', '', 'sd:'] + ['%1.4f' %r for r in stdev])
                        writer.writerow(['', '', '', '', 'sem:'] + ['%1.4f' %r for r in sem])
                        writer.writerow('\n')
                        writer.writerow('\n')

                    b +=1

                writer.writerow('\n')
                writer.writerow('\n')

    print "csv files saved to:\n%s" % fname1
  


    # # # PART II: mouse
    headers = [
        ['%s Experiment' %E.short_name],
        ['%s, avg across mice, %s' %(plot_type, bin_type)], 
        ['%s days: %s' %(E.use_days, E.daysToUse)]
        ]

    fname2  = dirname + '%s_panel_CT_%s_mouse_avg_%s_collapse_days.csv' %(plot_type, bin_type, E.use_days)
    sub_header = ['', 'group', 'day', 'tbin', ''] + feat_unit


    with open(fname2, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        for h in headers:
            writer.writerow(h)
        writer.writerow(sub_header)            

        cnt = 0
        for g in xrange(E.num_strains):
            idx = labels[:, 0] == g
            g_data, g_labels = data_[idx], labels[idx]
            
            for day in E.daysToUse:
                idx2 = g_labels[:, 2] == day
                day_data = np.nanmean(g_data[idx2],axis=0)
                # day_std = np.nanstd(g_data[idx2], axis=0)
                # day_sem = day_std / np.sqrt(g_data[idx2].shape[0]-1)
                # stop
                c = 0
                for row in day_data:
                # for row in day_sem:
                    # if not np.isnan(row).all():
                    row_text = ['', str(g), str(day), tbins[c], 'avg']
                    writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                    c +=1 

                writer.writerow('\n')

            writer.writerow('\n')
            writer.writerow('\n')

    print "csv files saved to:\n%s" % fname2




def write_panel_to_csv_across_days(experiment, level='mouseday', bin_type='12bins', err_type='sem', 
        plot_type='features'):
    
    E = experiment

    features = E.features_by_activity
    num_features = len(features)
    days_to_use = E.daysToUse    
    num_days = len(days_to_use)

    string_shift = '_shifted%+02dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    dirname = E.figures_dir + '%s/vectors/panels_CT/csv_files/%s/%s/%s_days/' %(
                                plot_type, bin_type, level, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    fname1  = dirname + '%s_panel_CT_%s_%s_%s_across_days.csv' %(plot_type, bin_type, level, E.use_days)

    # load data  
    # features, groups/mice/mousedays, 3cycles/12bins, avg/err
    data, labels = E.load_features_vectors(features, level, bin_type, err_type)
    data_ = data.swapaxes(0, 1).swapaxes(1, 2)[:, :, :, 0]     # avg only
    
    if bin_type.endswith('bins'):
        tbins = get_tbins_string(bin_type)
        
    # headers
    feat_unit = ['%s %s' %(feat, E.plot_settings_dict[feat]['unit']) for feat in features]
    
    headers = [
        ['%s Experiment' %E.short_name],
        ['%s %s %s' %(level, plot_type, bin_type)], 
        ['%s days: %s' %(E.use_days, E.daysToUse)]
        ]
    
    with open(fname1, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        for h in headers:
            writer.writerow(h)

        if level == 'mouse':
            sub_header = ['', 'group', 'mouse', 'tbin'] + feat_unit
            writer.writerow(sub_header)            

            cnt = 0
            for g in xrange(E.num_strains):
                idx = labels[:, 0] == g
                g_data, g_labels = data_[idx], labels[idx]
                mouseNumbers = np.unique(g_labels[:, 1])
                num_mice = len(mouseNumbers)
                
                b = 0
                for bin_data in g_data.swapaxes(0, 1):
                    c = 0
                    for row in bin_data:
                        if not np.isnan(row).all():
                            row_text = ['', g_labels[c, 0], g_labels[c, 1], tbins[b]]
                            writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                            c +=1 

                    writer.writerow('\n')
                    
                    avg = np.nanmean(bin_data, axis=0)
                    if not np.isnan(avg).all():
                        stdev = np.nanstd(bin_data, axis=0)
                        sem = stdev / np.sqrt(bin_data.shape[0]-1)
                        writer.writerow(['', '', '', 'Mean:'] + ['%1.4f' %r for r in avg])
                        writer.writerow(['', '', '', 'sd:'] + ['%1.4f' %r for r in stdev])
                        writer.writerow(['', '', '', 'sem:'] + ['%1.4f' %r for r in sem])
                        writer.writerow('\n')
                        writer.writerow('\n')

                    b +=1

                writer.writerow('\n')
                writer.writerow('\n')


        elif level == 'mouseday':
            sub_header = ['', 'group', 'mouse', 'day', 'tbin'] + feat_unit
            writer.writerow(sub_header)            

            cnt = 0
            for g in xrange(E.num_strains):
                idx = labels[:, 0] == g
                g_data, g_labels = data_[idx], labels[idx]
                mouseNumbers = np.unique(g_labels[:, 1])
                num_mice = len(mouseNumbers)
                
                for mouse in mouseNumbers:
                    idx2 = g_labels[:, 1] == mouse
                    m_data, m_labels = g_data[idx2], g_labels[idx2]
                    stop
                    b = 0
                    for bin_data in m_data.swapaxes(0, 1):
                        c = 0
                        for row in bin_data:
                            if not np.isnan(row).all():
                                row_text = ['', m_labels[c, 0], m_labels[c, 1], m_labels[c, 2], tbins[b]]
                                writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                                c +=1 

                        writer.writerow('\n')
                        
                        avg = np.nanmean(bin_data, axis=0)
                        if not np.isnan(avg).all():
                            stdev = np.nanstd(bin_data, axis=0)
                            sem = stdev / np.sqrt(bin_data.shape[0]-1)
                            writer.writerow(['', '', '', '', 'Mean:'] + ['%1.4f' %r for r in avg])
                            writer.writerow(['', '', '', '', 'sd:'] + ['%1.4f' %r for r in stdev])
                            writer.writerow(['', '', '', '', 'sem:'] + ['%1.4f' %r for r in sem])
                            writer.writerow('\n')
                            writer.writerow('\n')

                        b +=1

                    writer.writerow('\n')
                    writer.writerow('\n')
                    # if np.isnan(bin_data).all():
                    #     writer.writerow(['', str(g), str(mouse), 'EXCLUDED'])
                    #     writer.writerow('\n')
                    #     writer.writerow('\n')

    print "csv files saved to:\n%s" % fname1










# def draw_mouse_features_2(E, data, labels, bin_type, err_type, fname,
#         plot_type='features', ADD_SOURCE=False):
    
#     # double features for subtitles
#     features_idx = [
#             0, 1, 2,
#             0, 1, 2,
#             3, 4, 5, 6, 7, 8, 9,
#             3, 4, 5, 6, 7, 8, 9,
#             10, 11, 12, 13, 14, 15, 16,
#             10, 11, 12, 13, 14, 15, 16,
#             17, 18, 19, 20, 21, 22, 23,
#             17, 18, 19, 20, 21, 22, 23
#             ]
#     features_list = [
#             'ASP', 'ASN', 'ASD',
#             'ASP', 'ASN', 'ASD',
#             'TF', 'FASInt', 'FBASR', 'FBN', 'FBS', 'FBD', 'FBI', 
#             'TF', 'FASInt', 'FBASR', 'FBN', 'FBS', 'FBD', 'FBI', 
#             'TW', 'WASInt', 'WBASR', 'WBN', 'WBS', 'WBD', 'WBI', 
#             'TW', 'WASInt', 'WBASR', 'WBN', 'WBS', 'WBD', 'WBI', 
#             'TM', 'MASInt', 'MBASR', 'MBN', 'MBS', 'MBD', 'MBI',
#             'TM', 'MASInt', 'MBASR', 'MBN', 'MBS', 'MBD', 'MBI'
#             ]

#     figsize = (11.2, 6.4)
#     nrows, ncols = 8, 7
#     fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)

#     other_color = E.fcolors['other'][0]
#     xticks, xlabels = get_CT_ticks_labels(bin_type='12bins', SHIFT=E.BIN_SHIFT, tshift=E.binTimeShift)
#     xs = xticks[:-1] +1
    
#     cnt = 0
#     for n in xrange(nrows):
#         for m in xrange(ncols):
#             ax = axes.flatten()[n*ncols + m]
#             if n < 2 and m >= 3:
#                 ax.axis('off')
#                 continue
            
#             colors = get_two_group_features_colors(E, feature)

#             subtitle = '%s %s' %(feature, E.plot_settings_dict[feature]['unit'])

#             g = n%2   #group label
#             idx = labels[:, 0] == g
#             group_data, group_labels = data[idx], labels[idx]

#             if bin_type.endswith('bins'):
#                 tkw = {'lw':.5, 'elinewidth':.5, 'capsize':1}
#                 for mouse in xrange(idx.sum()):
#                     ax.errorbar(xs, group_data[mouse, features_idx[cnt], :, 0], 
#                                 yerr=group_data[mouse, features_idx[cnt], :, 1], 
#                                 color=colors[g], mec=colors[g], **tkw)
#             else:
#                 stop

#             # set_axis_layout(E, ax, bin_type)
#             if not n%2:
#                 ax.set_title(subtitle, fontsize=8)

#             cnt += 1

#         set_panel_layout(E, fig)

#     save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.02)
#     plt.close()
