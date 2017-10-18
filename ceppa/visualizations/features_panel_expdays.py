import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import os
import csv

from ceppa.visualizations.features_panel_CT import get_two_group_features_colors
from ceppa.util import my_utils 
from ceppa.visualizations.plotting_utils import add_titles_notes
from ceppa.visualizations.plotting_utils import add_xylabels, ax_cleanup, save_plot


"""
G.Onnis, 09.2017

Tecott Lab UCSF
"""

def get_ymaxs(data):
    max_avg = data[:, :, :, :, 0].max(3).max(2).max(0)
    max_err = data[:, :, :, :, 1].max(3).max(2).max(0)
    return max_avg + max_err


def plot_features_panel_12bins(experiment, level='group', bin_type='12bins', err_type='sem',  
        plot_type= 'features', ADD_SOURCE=True):   

    E = experiment

    print "%s, level: %s, bin_type: %s, err_type: %s, days: %s" %(
            plot_features_panel_12bins.__name__, level, bin_type, err_type, E.daysToUse)

    features = E.features_by_activity
    num_features = len(features)
    days_to_use = E.daysToUse    
    num_bins = int(bin_type.strip('bins'))
    tbins = my_utils.get_tbins_string(bin_type)

    dirname = E.figures_dir + '%s/vectors/panels_expdays/%s/%s_days/' %(plot_type, bin_type, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    
    data = E.generate_feature_vectors_expdays(features, level, bin_type, err_type)
    ymaxs = get_ymaxs(data)

    # stop
    for b in xrange(num_bins):
        new_data = data[:, :, :, b, :]
        figsize = (14.4, 4.8)
        nrows, ncols = 4, 7
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)
        xs = days_to_use

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
                    tkw = {'fmt':'o-', 'ms':2, 'elinewidth':.5, 'capsize':1}
                    ax.errorbar(xs, new_data[g, cnt, :, 0], yerr=new_data[g, cnt, :, 1], 
                        color=colors[g], mec=colors[g], **tkw)

                if E.short_name == 'HFD2':
                    d_day = E.dietChangeDayNumbers[0]
                    ax.axvspan(xmin=d_day, xmax=days_to_use[-1], color='.9', zorder=0)
                
                # xmin, xmax = ax.get_xlim()
                # ax.set_xlim((xmin-.5, xmax+.5))
                # ax.set_ylim([0, ymaxs[cnt]])
                ax_cleanup(ax)
                ax.set_title(subtitle, fontsize=10)

                cnt += 1

        xmin, xmax = ax.get_xlim()
        ax.set_xlim((xmin-.5, xmax+.5))

        fig.text(.6, .9, '0: %s, control, %s (grayscale)' %(E.strain_names[0], tbins[b]), 
                    fontsize=8)
        fig.text(.6, .85, '1: %s, knock-out, %s (colors)' %(E.strain_names[1], tbins[b]), 
                    fontsize=8)
        fig.text(.6, .8, 'gray background: diet change', fontsize=8)

        xlabel = 'Experiment Day'
        add_xylabels(fig, xlabel=xlabel, xypad=-.02, labelsize=10)

        days_string = E.get_days_to_use_text()
        fig_title = '%s Experiment\nFeatures, %s %s avg$\pm$%s, %s\nacross %s days: %s' %(
                        E.short_name, 
                        bin_type, level, err_type, tbins[b],
                        E.use_days.replace('_', '-').title(), days_string
                        )

        add_titles_notes(E, fig,title=fig_title)   

        plt.subplots_adjust(hspace=.6, wspace=.34)
        fname = dirname + '%s_panel_expdays_%s_group_%s_bin%d' %(plot_type, bin_type, err_type, b)

        save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.02)





def plot_features_panel_24H(experiment, level='group', bin_type='3cycles', err_type='sem',  
        plot_type= 'features', ADD_SOURCE=True):   

    E = experiment

    print "%s, level: %s, bin_type: %s, err_type: %s, days: %s" %(
            plot_features_panel_24H.__name__, level, bin_type, err_type, E.daysToUse)

    features = E.features_by_activity
    num_features = len(features)
    days_to_use = E.daysToUse    

    dirname = E.figures_dir + '%s/vectors/panels_expdays/%s/%s_days/' %(plot_type, bin_type, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    fname = dirname + '%s_panel_expdays_24H_group_%s' %(plot_type, err_type)

    data = E.generate_feature_vectors_expdays(features, level, bin_type, err_type)
    new_data = data[:, :, :, 0, :]

    figsize = (14.4, 4.8)
    nrows, ncols = 4, 7
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)
    xs = days_to_use

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
                tkw = {'fmt':'o-', 'ms':2, 'elinewidth':.5, 'capsize':1}
                ax.errorbar(xs, new_data[g, cnt, :, 0], yerr=new_data[g, cnt, :, 1], 
                    color=colors[g], mec=colors[g], **tkw)

            if E.short_name == 'HFD2':
                d_day = E.dietChangeDayNumbers[0]
                ax.axvspan(xmin=d_day, xmax=days_to_use[-1], color='.9', zorder=0)
            
            xlims = ax.get_xlim()
            ax.set_xlim((4, xlims[1]))
            # ax.set_ylim([0, ax.get_ylim()[1]])
            ax_cleanup(ax)
            ax.set_title(subtitle, fontsize=10)

            cnt += 1

    fig.text(.6, .9, '0: %s, control, 24H (grayscale)' %E.strain_names[0], fontsize=8)
    fig.text(.6, .85, '1: %s, knock-out, 24H (colors)' %E.strain_names[1], fontsize=8)
    fig.text(.6, .8, 'gray background: diet change', fontsize=8)

    xlabel = 'Experiment Day'
    add_xylabels(fig, xlabel=xlabel, xypad=-.02, labelsize=10)

    days_string = E.get_days_to_use_text()
    fig_title = '%s Experiment\nFeatures, 24H %s avg$\pm$%s\nacross %s days: %s' %(
                    E.short_name, 
                    level, err_type,
                    E.use_days.replace('_', '-').title(), days_string
                    )

    add_titles_notes(E, fig,title=fig_title)   

    plt.subplots_adjust(hspace=.6, wspace=.34)
    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.02)


def write_panel_24H_to_csv(experiment, level='group', bin_type='3cycles', err_type='sem', 
        plot_type='features'):
    E = experiment

    features = E.features_by_activity
    num_features = len(features)
    days_to_use = E.daysToUse    

    dirname = E.figures_dir + '%s/vectors/panels_expdays/%s/csv_files/%s_days/' %(plot_type, bin_type, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    fname1  = dirname + '%s_panel_expdays_24H.csv' %plot_type

    # features, groups, days, cycles, avg/err
    data = E.generate_feature_vectors_expdays(features, level, bin_type, err_type)
    new_data = data[:, :, :, 0, :]      # groups, features
    
    # headers
    # string = 'BIN_SHIFTED: %dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    feat_unit = ['%s %s' %(feat, E.plot_settings_dict[feat]['unit']) for feat in features]
    
    headers = [
        ['%s Experiment' %E.short_name],
        ['%s vs days' %plot_type], 
        ['24H values, %s avg (%s) across individuals' %(level, err_type)], 
        ['%s days: %s' %(E.use_days, E.daysToUse)]
        ]
    sub_header = ['', 'group', 'feature', 'value', ''] + ['day%d' %x for x in E.daysToUse]

    with open(fname1, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        for h in headers:
            writer.writerow(h)
        writer.writerow(sub_header)            

        cnt = 0
        for group_data in new_data:
            c = 0
            for feature_data in group_data:
                # stop
                row_text1 = ['', '%d: %s' %(cnt, E.strain_names[cnt]), feat_unit[c], '24H', 'avg']
                row_text2 = ['', '%d: %s' %(cnt, E.strain_names[cnt]), feat_unit[c], '24H', err_type]
                writer.writerow(np.hstack([row_text1, ['%1.4f' %r for r in feature_data[:, 0]]]))   #avg
                writer.writerow(np.hstack([row_text2, ['%1.4f' %r for r in feature_data[:, 1]]]))   #err
                writer.writerow('\n')
                c +=1

            writer.writerow('\n')
            writer.writerow('\n')
            cnt += 1

    print "csv files saved to:\n%s" % fname1


def plot_features_panel_DC_LC(experiment, level='group', bin_type='3cycles', err_type='sem',  
        plot_type= 'features', ADD_SOURCE=True):   

    E = experiment

    print "%s, level: %s, bin_type: %s, err_type: %s, days: %s" %(
            plot_features_panel_DC_LC.__name__, level, bin_type, err_type, E.daysToUse)

    features = E.features_by_activity
    num_features = len(features)
    days_to_use = E.daysToUse    

    dirname = E.figures_dir + '%s/vectors/panels_expdays/%s/%s_days/' %(plot_type, bin_type, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    fname = dirname + '%s_panel_expdays_DC_LC_group_%s' %(plot_type, err_type)

    # groups, features, days, cycles, avg/err
    data = E.generate_feature_vectors_expdays(features, level, bin_type, err_type)
    new_data = data[:, :, :, 1:, :]

    figsize = (14.4, 4.8)
    nrows, ncols = 4, 7
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)
    xs = days_to_use

    cnt = 0
    for n in xrange(nrows):
        for m in xrange(ncols):
            ax = axes.flatten()[n*ncols + m]
            if n == 0 and m >= 3:
                ax.axis('off')
                continue
            
            feature = features[cnt]
            # get colors
            if feature.startswith('AS'):
                color1, color2 = [E.fcolors['AS'].values()[x] for x in [1, 3]]
            elif feature.startswith('T'):
                color1, color2 = [E.fcolors[feature[1:]].values()[x] for x in [1, 3]]
            else:
                color1, color2 = [E.fcolors[feature[:1]].values()[x] for x in [1, 3]]

            colors = ['.4', '.7', color1, color2]

            subtitle = '%s %s' %(feature, E.plot_settings_dict[feature]['unit'])

            for g in xrange(E.num_strains):
                tkw = {'fmt':'o-', 'ms':2, 'elinewidth':.5, 'capsize':1}
                # DC
                mec = '0' if g == 0 else colors[2*g]
                ax.errorbar(xs, new_data[g, cnt, :, 0, 0], yerr=new_data[g, cnt, :, 0, 1],
                            color=colors[2*g], mec=mec, **tkw)
                #LC
                mc = '0' if g == 0 else colors[2*g+1]
                ax.errorbar(xs, new_data[g, cnt, :, 1, 0], yerr=new_data[g, cnt, :, 1, 1], 
                            color=colors[2*g+1], mec=mec, **tkw)

            if E.short_name == 'HFD2':
                d_day = E.dietChangeDayNumbers[0]
                ax.axvspan(xmin=d_day, xmax=days_to_use[-1], color='.9', zorder=0)
            
            xlims = ax.get_xlim()
            ax.set_xlim((4, xlims[1]))
            ax.set_ylim([0, ax.get_ylim()[1]])
            ax_cleanup(ax)
            ax.set_title(subtitle, fontsize=10)

            cnt += 1
    
    fig.text(.6, .9, '0: %s, control (grayscale)\nDC:black, LC: gray' %E.strain_names[0], fontsize=8)
    fig.text(.6, .83, '1: %s, knock-out (colors)\nDC: dark, LC: light ' %E.strain_names[1], fontsize=8)
    fig.text(.6, .78, 'gray background: diet change', fontsize=8)

    xlabel = 'Experiment Day'
    add_xylabels(fig, xlabel=xlabel, xypad=-.02, labelsize=10)

    days_string = E.get_days_to_use_text()
    fig_title = '%s Experiment\nFeatures, DC vs. LC, %s avg and %s\nacross %s days: %s' %(
                    E.short_name, 
                    level, err_type,
                    E.use_days.replace('_', '-').title(), days_string
                    )

    add_titles_notes(E, fig,title=fig_title)   

    plt.subplots_adjust(hspace=.6, wspace=.34)
    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.02)


def write_panel_DC_LC_to_csv(experiment, level='group', bin_type='3cycles', err_type='sem', 
        plot_type='features'):
    E = experiment

    features = E.features_by_activity
    num_features = len(features)
    days_to_use = E.daysToUse    

    dirname = E.figures_dir + '%s/vectors/panels_expdays/%s/csv_files/%s_days/' %(plot_type, bin_type, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    fname1  = dirname + '%s_panel_expdays_DC_LC.csv' %plot_type

    # groups, features, days, cycles, avg/err
    data = E.generate_feature_vectors_expdays(features, level, bin_type, err_type)
    new_data = data[:, :, :, 1:, :]
    
    # headers
    # string = 'BIN_SHIFTED: %dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    feat_unit = ['%s %s' %(feat, E.plot_settings_dict[feat]['unit']) for feat in features]
    
    headers = [
        ['%s Experiment' %E.short_name],
        ['%s vs days' %plot_type], 
        ['DC vs LC values and LC/DC ratio, %s avg (%s) across individuals' %(level, err_type)], 
        ['%s days: %s' %(E.use_days, E.daysToUse)]
        ]
    sub_header = ['', 'group', 'feature', 'value', ''] + ['day%d' %x for x in E.daysToUse]

    with open(fname1, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        for h in headers:
            writer.writerow(h)
        writer.writerow(sub_header)            

        cnt = 0
        for group_data in new_data:
            c = 0
            for feature_data in group_data:
                cy = 0
                for cy_string in ['DC', 'LC']:
                    row_text1 = ['', '%d: %s' %(cnt, E.strain_names[cnt]), feat_unit[c], cy_string, 'avg']
                    row_text2 = ['', '%d: %s' %(cnt, E.strain_names[cnt]), feat_unit[c], cy_string, err_type]
                    writer.writerow(np.hstack([row_text1, ['%1.4f' %r for r in feature_data[:, cy, 0]]]))   # avg
                    writer.writerow(np.hstack([row_text2, ['%1.4f' %r for r in feature_data[:, cy, 1]]]))   #err
                    cy += 1

                row_text3 = ['', '%d: %s' %(cnt, E.strain_names[cnt]), features[c], 'LC/DC', 'avgs ratio']
                ratio = feature_data[:, 1, 0] / feature_data[:, 0, 0]
                writer.writerow(np.hstack([row_text3, ['%1.4f' %r for r in ratio]]))

                writer.writerow('\n')
                c +=1

            writer.writerow('\n')
            writer.writerow('\n')
            cnt += 1

    print "csv files saved to:\n%s" % fname1



def plot_features_panel_LC_DC_ratio(experiment, level='group', bin_type='3cycles', err_type='sem',  
        plot_type= 'features', ADD_SOURCE=True):   
    E = experiment

    print "%s, level: %s, bin_type: %s, err_type: %s, days: %s" %(
            plot_features_panel_LC_DC_ratio.__name__, level, bin_type, err_type, E.daysToUse)

    features = E.features_by_activity
    num_features = len(features)
    days_to_use = E.daysToUse    

    dirname = E.figures_dir + '%s/vectors/panels_expdays/%s/%s_days/' %(plot_type, bin_type, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    fname = dirname + '%s_panel_expdays_LC_DC_ratio' %(plot_type)#s, err_type)

    # using mouseday value
    # ratios = E.generate_feature_vectors_LC_DC_ratio_expdays(features, level, bin_type, err_type)
    
    # using group averages value
    data_ = E.generate_feature_vectors_expdays(features, level, bin_type, err_type)
    ratios_ = data_[:, :, :, 2, 0] / data_[:, :, :, 1, 0]      # LC/DC, avgs

    figsize = (14.4, 4.8)
    nrows, ncols = 4, 7
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)
    xs = days_to_use

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
                # # using mouseday values
                # tkw = {'fmt':'o-', 'ms':2, 'elinewidth':.5, 'capsize':1}
                # ax.errorbar(xs, ratios[g, cnt, :, 0], yerr=ratios[g, cnt, :, 1], 
                #     color=colors[g], mec=colors[g], **tkw)
                
                # using group averages value
                tkw = {'marker':'o', 'ms':2, 'zorder':0}
                ax.plot(xs, ratios_[g, cnt, :], color=colors[g], mec=colors[g], **tkw)
                # use when plotting all for comparison
                # colors_ = ['r', 'y']
                # ax.plot(xs, ratios_[g, cnt, :], color=colors_[g], mec=colors_[g], **tkw)

            if E.short_name == 'HFD2':
                d_day = E.dietChangeDayNumbers[0]
                ax.axvspan(xmin=d_day, xmax=days_to_use[-1], color='.9', zorder=0)
            
            xlims = ax.get_xlim()
            ax.set_xlim((4, xlims[1]))
            ax.set_ylim((0, ax.get_ylim()[1]))
            ax_cleanup(ax)
            ax.set_title(subtitle, fontsize=10)

            cnt += 1

    fig.text(.6, .9, '0: %s, control, 24H (grayscale)' %E.strain_names[0], fontsize=8)
    fig.text(.6, .85, '1: %s, knock-out, 24H (colors)' %E.strain_names[1], fontsize=8)
    fig.text(.6, .8, 'gray background: diet change', fontsize=8)

    xlabel = 'Experiment Day'
    add_xylabels(fig, xlabel=xlabel, xypad=-.02, labelsize=10)

    days_string = E.get_days_to_use_text()
    fig_title = '%s Experiment\nFeatures vs days, LC/DC ratio %s avg$\pm$%s\nacross %s days: %s' %(
                    E.short_name, 
                    level, err_type,
                    E.use_days.replace('_', '-').title(), days_string
                    )

    add_titles_notes(E, fig,title=fig_title)   

    plt.subplots_adjust(hspace=.6, wspace=.34)
    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.02)

