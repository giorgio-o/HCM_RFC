import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import os

from ceppa.visualizations.features_panel_CT import get_panel_ymaxs, set_panel_layout, get_ymaxs
from ceppa.util.my_utils import get_num_items
from ceppa.visualizations.plotting_utils import subplot_labels, add_source


"""
G.Onnis, 05.2017

Tecott Lab UCSF
"""


def get_feature_panel_AS_data(experiment, feature_list, level, err_type, 
        days=None, group_avg_type='over_mds'):
    
    E = experiment
    
    num_items = get_num_items(E, level)
    days_to_use = E.daysToUse if days is None else days
    max_AS = max(E.get_max_AS())

    print "%s, %s, %s" %(get_feature_panel_AS_data.__name__, level, str(days_to_use))

    avgs = np.zeros((len(feature_list), num_items, len(days_to_use), max_AS))
    errs = np.zeros((len(feature_list), num_items, len(days_to_use), max_AS))
    
    for d, day in enumerate(days_to_use):
        for c, feat in enumerate(feature_list):
            print "loading day %d.." %day
            s_data, s_labels, m_data, m_labels, md_data, md_labels = \
                    E.generate_bout_feature_vectors_per_AS(
                    	feat, days=[day], group_avg_type=group_avg_type)   

            if level == 'strain':
                data = s_data[0]
                yerr = s_data[1] if err_type == 'stdev' else s_data[2]
                avgs[c, :, d, :], errs[c, :, d, :], labels = data, yerr, s_labels
            
            elif level == 'mouse':
                data = m_data[0]
                yerr = m_data[1] if err_type == 'stdev' else m_data[2]
                avgs[c, :, d, :], errs[c, :, d, :], labels = data, yerr, m_labels

    return avgs, errs, labels


def plot_features_panel_AS(experiment, level, err_type='stdev', ADD_SOURCE=True):

    E = experiment

    # load data around transitiondays 10 to 15
    feature_list = E.features_by_type['bouts']   
    avgs, errs, labels = get_feature_panel_AS_data(E, feature_list, level, err_type)
    # ymaxs = get_panel_ymaxs(experiment, feature_list, bin_type, level)
    stop

    dirname_out = E.figures_dir_subpar + 'features/vectors/panels_AS/%s_days/%s/' %(E.use_days, level)    
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

    print "%s..\nlevel: %s\nerr_type: %s" %(
            plot_features_panel_AS.__name__, level, err_type)


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






