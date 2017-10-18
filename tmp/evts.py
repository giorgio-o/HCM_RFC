import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import os
import plotting_utils
import plot_settings

"""
G.Onnis, 11.2016

Tecott Lab UCSF
"""


def draw_event_feature_vs_expdays_mouse(E, strain, feat, m_arr, m_labels):
    act = feat[0] if feat != 'LC' else 'W'
    name, unit = [E.plot_settings_dict[feat][x] for x in ['name', 'unit']]
    comment = '*MD ignored\nwhen missing' 
    gs1, fig = plotting_utils.create_4x4_xy_gridspec(level='mouse')
    idx_m = m_labels[:, 0] == strain
    mouseNumbers = m_labels[idx_m, 1]
    num_mice = idx_m.sum()
    data = m_arr[idx_m]     # g
    if feat in E.HCM_variables['coefficients']:
        data *= 1000        # mg
    masked = np.ma.masked_where(data==0, data) 
    for c in xrange(num_mice):      
        try:
            ax = fig.add_subplot(gs1[c])
            ax.plot(E.daysToUse, masked[c], 
                marker='d', ms=4, color=E.fcolors[act][0])
            ax.set_title('M%d' %int(mouseNumbers[c]), fontsize=10)
            plotting_utils.set_days_layout(E, ax, masked.max())
        except IndexError:
            ax.axis('off')
            continue 
        
        title = '%s\ngroup: %s\n%s' %(name, E.strain_names[strain], comment)
        plotting_utils.set_CT_plot_labels_and_titles(fig, title, 'Experiment day', '%s %s' %(name, unit))
    
    gs1.update(hspace=.6, wspace=.3)


def draw_event_feature_distribution(E, feat, m_arr, m_labels, MDS=False):
    act = feat[0] if feat != 'LC' else 'W'
    bins, name, unit = [E.plot_settings_dict[feat][x] \
                        for x in ['bins', 'name', 'unit']] 
    binsize = bins[1] - bins[0]
    gs1, fig = plotting_utils.create_4x4_xy_gridspec()
    for strain in xrange(E.num_strains):
        idx = m_labels[:, 0] == strain
        data = m_arr[idx]     # g
        strain_name = E.strain_names[strain]
        if feat in E.HCM_variables['coefficients']:
            data *= 1000        # mg 
        masked = np.ma.mean(np.ma.masked_where(data==0, data), axis=1)
        text = 'mouse'
        if MDS:
            masked = np.ma.masked_where(data==0, data).ravel()
            text = 'mousedays'

        ax = fig.add_subplot(gs1[strain])
        ax.hist(masked, bins, color=E.fcolors[act][0])
        ax.set_title('%s' %strain_name, fontsize=8)
        title = '%s distribution\ngroup: %s\nbinSize=%1.1f%s\%s' %(
                    name, strain_name, binsize, unit, text)
        plotting_utils.set_CT_plot_labels_and_titles(fig, title, '%s [%s]' %(name, unit), 'Frequency')
        plotting_utils.set_distribution_layout(ax, bins, ymax=E.get_max_number_mice_per_group())
    
    gs1.update(hspace=0.6, wspace=0.3)


def plot_event_feature_vs_expdays(experiment, feat):
    E = experiment
    dirname_out = E.plots_dir + 'events/%s/' %feat
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out) 
    # get data
    m_arr, m_labels = E.get_event_days_data(feat)
    for strain in xrange(E.num_strains):
        draw_event_feature_vs_expdays_mouse(E, strain, feat, m_arr, m_labels)
        # save
        fname = dirname_out + '%s_strain%d.pdf' %(feat, strain)
        plt.savefig(fname, bbox_inches='tight')
        plt.close()
        print "saved to: %s" %fname


def plot_event_feature_distribution(experiment, feat, MDS=False):
    E = experiment
    dirname_out = E.plots_dir + 'events/%s/' %feat
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out) 
    # get data
    m_arr, m_labels = E.get_event_days_data(feat)
    draw_event_feature_distribution(E, feat, m_arr, m_labels, MDS)
    # save
    text = 'mice' if not MDS else 'mousedays'
    fname = dirname_out + 'all_strains_%s_distribution_%s.pdf' %(feat, text)
    plt.savefig(fname, bbox_inches='tight')
    plt.close()
    print "saved to: %s" %fname

