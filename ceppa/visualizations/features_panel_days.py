import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import os
import csv

from ceppa.visualizations.features_panel_CT import get_panel_ymaxs, set_panel_layout, get_ymaxs
from ceppa.util.my_utils import get_num_items
from ceppa.visualizations.plotting_utils import subplot_labels, add_source


"""
G.A.Onnis, 05.2017

Tecott Lab UCSF
"""



def get_chow_to_HF_panel_data(experiment, feature_list, vec_type, level, err_type, 
        days=None, strain_avg_type='over_mds'):
    
    E = experiment
    
    num_items = get_num_items(E, level)
    days_to_use = E.daysToUse if days is None else days
    num_bins = 12 

    print "%s, %s, %s" %(get_chow_to_HF_panel_data.__name__, level, str(days_to_use))

    avgs = np.zeros((len(feature_list), num_items, len(days_to_use), num_bins))
    errs = np.zeros((len(feature_list), num_items, len(days_to_use), num_bins))
    
    for d, day in enumerate(days_to_use):
        for c, feat in enumerate(feature_list):
            
            s_data, s_labels, m_data, m_labels, md_data, md_labels = \
                    E.generate_feature_vectors(
                        feat, vec_type='12bins', days=[day], 
                        strain_avg_type=strain_avg_type)   

            if level == 'strain':
                data = s_data[0]
                yerr = s_data[1] if err_type == 'stdev' else s_data[2]
                avgs[c, :, d, :], errs[c, :, d, :], labels = data, yerr, s_labels
            
            elif level == 'mouse':
                data = m_data[0]
                yerr = m_data[1] if err_type == 'stdev' else m_data[2]
                avgs[c, :, d, :], errs[c, :, d, :], labels = data, yerr, m_labels

    return avgs, errs, labels


def draw_features(E, avgs, errs, fig_title, ymaxs=None, ADD_SOURCE=False):
    
    feats = E.features

    figsize, nrows, ncols = (13, 10), 8, 6
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)

    xs = range(7, 31, 2) 
    xlabel = 'Zeitgeber Time [hr]' 
    fmts = ['.', '.', '.', 'x', '^', 'd', 'o', 'o', 'o']
    zorders = [0, 0, 0, 5, 4, 3, 1, 1, 1]

    for c in xrange(len(feats)):
        color = E.plot_settings_dict[feats[c]]['color']
        colors = ['.65', '.65', '.65', color, color, color, '.35', '.35', '.35']

        ax0, ax1 = axes.flatten()[c*2 : c*2+2]

        for group, ax in enumerate([ax0, ax1]):
            for day in xrange(avgs.shape[2]):
                ax.errorbar(xs, avgs[c, group, day], yerr=errs[c, group, day], 
                    lw=.3, linestyle='-', fmt=fmts[day], ms=3, 
                    color=colors[day], label='day%d' %(E.daysToUse[day]),
                    elinewidth=.5, capsize=.5, capthick=.2, zorder=zorders[day])
                
            set_panel_layout(E, ax, feats, c, vec_type='12bins', ymaxs=ymaxs)
            ax.set_title('%s, %s' %(feats[c], E.strain_names[group]), 
                fontsize=10)

        if c == 0:
            h, l = ax.get_legend_handles_labels()

    ncol = 3 if E.use_days == 'chow_to_HF_and_baseline' else 2
    tkw = {'numpoints':1, 'ncol':ncol, 'fontsize':8, 'handletextpad':1.2, 
            'labelspacing':.8, 'borderaxespad':1.5, 'frameon':False,
            'bbox_to_anchor':[.85, 1.01], 
            'bbox_transform':plt.gcf().transFigure
            }
    plt.legend(h, l, **tkw)
    subplot_labels(fig, xlabel, ylabel='', fig_title=fig_title, ADD_SOURCE=ADD_SOURCE)
    plt.subplots_adjust(wspace=.3)


def plot_features_transition_days(experiment, vec_type='12bins', level='strain', 
    err_type='stderr', ADD_SOURCE=True):

    E = experiment
    num_strains = E.num_strains

    # load data around transitiondays 10 to 15
    feature_list = E.features   
    avgs, errs, labels = get_chow_to_HF_panel_data(E, feature_list, vec_type, level, err_type)
    ymaxs = get_panel_ymaxs(experiment, feature_list, vec_type, level)


    dirname_out = E.figures_dir_subpar + 'features/vectors/panels_CT/%s_days/%s/' %(E.use_days, level)    
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

    print "%s..\nlevel: %s\nvec_type: %s\nerr_type: %s" %(
            plot_features_transition_days.__name__, level, vec_type, err_type)

    # plotting 
    if level == 'strain':
        gname1, gname2 = E.strain_names
        fig_title = 'Features\ngroups: %s, %s\n%s_days:\n%s\navg$\pm$%s' %(
                    gname1, gname2, E.use_days, E.daysToUse, err_type)
    
        draw_features(E, avgs, errs, fig_title, ymaxs, ADD_SOURCE)
        #save
        if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
        fname = dirname_out + 'feature_panel_%s_transition_days_%s.pdf' %(E.use_days, err_type)
        plt.savefig(fname, bbox_inches='tight')
        plt.close()
        print "figures saved to: %s" %fname

