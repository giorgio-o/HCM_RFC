import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import os
import time
import plotting_utils
import plot_settings
"""
G.A.Onnis, 03.2016
    revised: 10.2016

Tecott Lab UCSF
"""


def draw_features(E, data, labels, feat, level, strain=None, mouseNumber=None, err_type='stdev'):
    
    arr, yerr = data[0], data[1]
    if err_type == 'stderr':
        yerr = data[2]

    subtitles = [name for name in E.strain_names]
    fig_title = '%s\n%s avg$\pm$%s' %(E.plot_settings_dict[feat]['name'], level, err_type)
    if level == 'mouse':
        subtitles = ['M%d' %n for n in labels]
        fig_title = '%s\n%s avg$\pm$%s\ngroup: %s' %(
            E.plot_settings_dict[feat]['name'], level, err_type, E.strain_names[strain]) 
    elif level == 'mouseday':
        arr, yerr = data, np.zeros_like(data)
        subtitles = ['day%d' %n for n in labels]
        fig_title = '%s\ngroup: %s\nmouse: M%d' %(
            E.plot_settings_dict[feat]['name'], E.strain_names[strain], int(mouseNumber))
        
    gs1, fig = plotting_utils.create_4x4_xy_gridspec(level)
    xs = range(9, 31, 2)
    color, color2 = E.plot_settings_dict[feat]['color'], '0.3'
    tkw = dict(color=color2, zorder=1)
    for c in xrange(arr.shape[0]):
        try:
            ax = fig.add_subplot(gs1[c])
            if level in ['strain', 'mouse']:
                ax.errorbar(xs, arr[c], yerr=yerr[c],  
                    label=level, fmt='s-', ms=2, color=color, zorder=2)

                if level ==  'mouse':
                    avg, std = arr.mean(axis=0), arr.std(axis=0)
                    ax.plot(xs, avg, alpha=0.4, **tkw) 
                    ax.fill_between(xs, avg-std, avg+std, label='group', 
                        alpha=0.25, **tkw)
            
            elif level == 'mouseday':
                ax.plot(xs, arr[c], label=level, color=color, zorder=2)
                avg, std = arr.mean(axis=0), arr.std(axis=0)
                ax.plot(xs, avg, alpha=0.4, **tkw)
                ax.fill_between(xs, avg-std, avg+std, label='mouse\navg$\pm$std', 
                    alpha=0.25, **tkw)

            ax.set_title(subtitles[c], fontsize=10)
            ymax = 1.2*np.max(arr.max(axis=0)+yerr.max(axis=0))
            plotting_utils.set_CT_layout(E, ax, ymax=None)
        
        except IndexError:
            ax.axis('off')
            continue    

    if level in ['mouse', 'mouseday']:           # legend
        h0, l0 = ax.get_legend_handles_labels()    
        fig.legend(h0, l0, bbox_to_anchor=[0.33, 0.85], prop={'size':6}, frameon=False)
        if level == 'mouseday':
            if feat in ['FBS', 'WBS']:
                display_ingestion_coefficient(E, ax, feat, 
                    mouseNumbers[c], labels[idx_md, 2])
    ylabel = '%s %s' %(E.plot_settings_dict[feat]['name'], E.plot_settings_dict[feat]['unit'])
    plotting_utils.set_CT_plot_labels_and_titles(fig, fig_title, 'Zeitgeber Time [hr]', ylabel)
    gs1.update(hspace=0.6, wspace=0.3)


def display_ingestion_coefficient(E, ax, feat, mouseNumber, days):
    var = 'FC' if feat == 'FBS' else 'LC'
    coeffs = []
    for day in days:
        qt = E.get_MD_feature(int(mouseNumber), int(day), var)
        coeffs.append(qt)
    clean_coeffs = [1000*x for x in coeffs]     # mg/s
    for nax, ax in enumerate(fig.axes):
        ax.text(0.85, 1, '%s=%1.2fmg/s' %(name, clean_coeffs[nax]), ha='center', fontsize=4, transform=ax.transAxes)


def plot_feature_vs_CT(experiment, feat='ASP', level='strain', err_type='stdev', num_bins=11, GENERATE=False):

    cstart = time.clock() 
    dirname_out = E.figures_dir_subpar + 'features/%s/%s/' %(feat, level)
    if feat in E.features['evts']:
        stop
        dirname_out = E.figures_dir + 'events/%s/%s/' %(feat, level)
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
    
    # get data
    strain_data, m_data, m_labels, md_data, md_labels = \
        E.generate_feature_vectors(feat, GENERATE, GET_AVGS=True)
    
    print "%s, %s features" %(plot_feature_vs_CT.__name__, feat)
    if level == 'strain':
        data, labels = strain_data, range(E.num_strains)
        draw_features(E, data, labels, feat, level, err_type)
        fname1 = dirname_out + 'all_strains_%s.pdf' %feat
        plt.savefig(fname1, bbox_inches='tight')
        plt.close()
        print "saved to: %s" %fname1
    
    elif level == 'mouse':
        for strain in xrange(E.num_strains):
            idx = m_labels[:, 0] == strain
            data, labels = m_data[:, idx], m_labels[idx, 1]              
            draw_features(E, data, labels, feat, level, strain, err_type)

            fname = dirname_out + '%s_strain%d.pdf' %(feat, strain)
            plt.savefig(fname, bbox_inches='tight')
            plt.close()
            print "saved to: %s" %fname
        
    elif level == 'mouseday':
        for strain in xrange(E.num_strains):
            idx_m = m_labels[:, 0] == strain
            mouseNumbers = m_labels[idx_m, 1]
            num_mice = idx_m.sum()
            for c in xrange(num_mice):
                idx_md = md_labels[:, 1] == mouseNumbers[c]                
                data = md_data[idx_md]
                labels = md_labels[idx_md,2]
                draw_features(E, data, labels, feat, level, 
                            strain, mouseNumbers[c], err_type)

                fname = dirname_out + '%s_strain%d_individual%d.pdf' %(feat, strain, c)
                plt.savefig(fname, bbox_inches='tight')
                plt.close()
                print "saved to: %s" %fname

    cstop = time.clock()
    print "%s %s script ran in %1.2f minutes"%(plot_feature_vs_CT.__name__, feat, (cstop-cstart)/60.)







