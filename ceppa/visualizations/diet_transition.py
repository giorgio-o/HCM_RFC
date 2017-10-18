import numpy as np
# import matplotlib as mpl
import matplotlib.pyplot as plt

import os
import csv

from ceppa.visualizations.features_panel_CT import get_panel_ymaxs
from ceppa.visualizations.plotting_utils import ax_cleanup

"""
G.Onnis, 04.2016

Tecott Lab UCSF
"""


# def get_panel_ymaxs(experiment, avgs, errs, labels, level):
#     E = experiment
#     if level == 'strain':
#         ymaxs = get_ymaxs(avgs, errs)

#     elif level == 'mouse':
#         ymaxs = []
#         for strain in xrange(E.num_strains):      # maxs per strain      
#             idx = labels[:, 0] == strain
#             avg, err = avgs[:, idx], errs[:, idx]
#             ymaxs.append(get_ymaxs(avg, err))

#     elif level == 'mouseday':
#         ymaxs = None

#     return ymaxs


def get_ymaxs(avgs, errs):
    return np.nanmax(avgs + errs, axis=2).max(axis=1)


def set_panel_layout(E, fig, ax, feats, num_subplot, ymaxs, num_bins=12): 
    num_days = len(E.daysToUse)
    ax.set_xlim([0, num_days * num_bins + 1])
    if ymaxs is not None:
        ax.set_ylim([0, ymaxs[num_subplot]])

    xticks = np.arange(0, num_days * num_bins+1, 6)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks*2) 
    ylims = np.array(ax.get_ylim())
    if feats[num_subplot] == 'ASP':
        ylims = [0, 1]
    ax.set_ylim([0, ylims[1]])

    for x in xticks[::2]:
    	ax.axvline(x=x, ymax=ylims[1], color='.7', zorder=0)
    
    cnt = E.daysToUse[0]
    for x in xticks[1::2]:
    	ax.text(x, .9*ylims[1], 'day%d' %cnt, fontsize=6, color='.7', ha='center')
    	cnt += 1

    ax.tick_params(axis='both', which='both', labelsize=7)
    ax.set_aspect('auto')
    ax_cleanup(ax)

    plt.subplots_adjust(left=0.1, right=0.88, hspace=0.6)#, wspace=0.15)


def draw_features(E, avg, err, bin_type, fig_title, ymaxs=None, plotType='markers'):
    
    feats = E.features
    fig, axes = plt.subplots(8, 3, figsize=(10, 12), sharex=True)
    xs = xrange(avg.shape[1]) 
    
    for c in xrange(len(feats)):
        ax = axes.flatten()[c]
        color = E.plot_settings_dict[feats[c]]['color']
        
        y, yerr = avg[c], err[c]

        if plotType == 'markers':
            ax.errorbar(xs, y, yerr=yerr, fmt='o', ms=2, color=color)
        elif plotType == 'lines':
            ax.plot(xs, y, color=color, zorder=1)
            # ax.fill_between(xs, y-yerr, y+yerr, color=color, alpha=alphas[_bin])

        set_panel_layout(E, fig, ax, feats, c, ymaxs)
        ax.set_title('%s %s' %(feats[c], E.plot_settings_dict[feats[c]]['unit']), 
            fontsize=10)

    fig.text(.5, .06, 'Hours after diet change', fontsize=8, ha='center')
    fig.text(.03, .95, fig_title, fontsize=8, va='center')




def get_feature_panel_data_day_by_day(experiment, bin_type, level, err_type, days=None, group_avg_type='over_mds'):
    E = experiment
    feature_names = E.features
    num_items = E.num_strains
    if level == 'mouse':
        num_items = E.num_mice_ok

    num_bins = 12 if bin_type.endswith('bins') else 3
    num_days = len(E.daysToUse) if days is None else len(days)
    avgs = np.zeros((len(feature_names), num_items, num_days * num_bins))
    errs = np.zeros((len(feature_names), num_items, num_days * num_bins))
    
    for c, feat in enumerate(feature_names):

        md_data, md_labels = E.generate_feature_vectors_expdays(feat, bin_type, days)     

        # rework data
        s_data, s_labels, m_data, m_labels = my_utils.get_mouse_strain_averages_day_by_day(
                                                                    E, md_data, md_labels)

        if level == 'strain':
            data = s_data[0]
            yerr = s_data[1] if err_type == 'stdev' else s_data[2]
            avgs[c], errs[c], labels = data, yerr, s_labels
        
        elif level == 'mouse':
            avgs[c], errs[c], labels = m_data, np.zeros_like(m_data), m_labels

    return avgs, errs, labels



def plot_stabilization_days(experiment, bin_type, level, err_type='stdev', days=None, COMMON_Y=False, plotType='markers'):
	
	E = experiment
	num_strains = len(E.strain_names)

	# load data 
	num_days = len(E.daysToUse) if days is None else len(days)
	avgs, errs, labels = get_feature_panel_data_day_by_day(E, bin_type, level, err_type, days)
	
	dirname = E.figures_dir_subpar + 'features/vectors/panels_expdays/%s_days/day_by_day/%s/' %(E.use_days, level)
	if COMMON_Y:
	    dirname += 'common_yscale/'
	    # ymaxs = get_panel_ymaxs(E, avgs, errs, labels, level)
	    ymaxs = get_panel_ymaxs(E, bin_type, level, err_type)
	else:
	    dirname += 'free_yscale/'
	    ymaxs = [None for n in E.features]
	if not os.path.isdir(dirname): os.makedirs(dirname)

	print "%s..\nlevel: %s\nbin_type: %s\nerr_type: %s" %(
	        plot_stabilization_days.__name__, level, bin_type, err_type)

	# plotting 
	if level == 'strain':
	    for strain in range(num_strains):
	        avg_text = 'avg$\pm$%s' %err_type if plotType == 'markers' else 'average'
	        fig_title = 'group%d: %s\n%s\n%s\n%s_days:%dto%d' %(
	                    strain, E.strain_names[strain], bin_type, avg_text, 
	                    E.use_days, E.daysToUse[0], E.daysToUse[-1])

	        draw_features(E, avgs[:, strain], errs[:, strain], bin_type, 
	                        fig_title, ymaxs, plotType)
	        
	        #save
	        dirname_out = dirname + '%s/' %plotType
	        if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
	        fname = dirname_out + 'feature_panel_strain%d.pdf' %strain
	        plt.savefig(fname, bbox_inches='tight')
	        plt.close()
	        print "figures saved to: %s" %fname

	elif level == 'mouse':
	    avg_text = 'avg$\pm$%s' %err_type if plotType == 'markers' else ''
	    for strain in xrange(num_strains):            
	        idx = labels[:, 0] == strain
	        mouseNumbers = labels[idx, 1]
	        num_mice = idx.sum()
	        avg, err = avgs[:, idx], errs[:, idx]
	        for c in xrange(num_mice):
	            fig_title = 'group%d: %s\nM%d\n%s\n%s\n%s_days:%dto%d' %(
	                        strain, E.strain_names[strain], mouseNumbers[c], 
	                        bin_type, avg_text, E.use_days, E.daysToUse[0], E.daysToUse[-1])
	            
	            
	            draw_features(E, avg[:, c], err[:, c], bin_type, 
	                            fig_title, ymaxs[strain], plotType='lines')

	            #save
	            dirname_out = dirname + 'strain%d/' %strain
	            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
	            fname = dirname_out + \
	                    'feature_panel_strain%d_mouse%d.pdf' %(strain, c)
	            plt.savefig(fname, bbox_inches='tight')
	            plt.close()
	            print "figures saved to: %s" %fname