import numpy as np
import matplotlib.pyplot as plt
import os
import csv

from ceppa.visualizations import plotting_utils
from ceppa.util import my_utils


def plot_feat1_vs_feat2(E, features, bin_type, level, CLOSE=True, BREAKDOWN=True):
    
    data, data_labels = E.load_feature_vectors(features, bin_type, level)
    varx, vary = data                 # verify varx and vary are normally distributed
    xlims, ylims = [(0, i.max())  for i in [varx, vary]]

    num_strains = E.num_strains
    colors = plotting_utils.get_16_colors()
    
    dirname = E.figures_dir_subpar + 'features/vectors/feature_vs_feature/' \
                                + '%s_vs_%s/%s/' %(features[1], features[0], bin_type)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    
    print "plotting %s vs. %s, %s, level: %s" %(
                    features[1], features[0], bin_type, level)

    if level == 'strain':
        if bin_type == '24HDCLC':
            cycles = ['24H', 'DC', 'LC']
            fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
            for cy, cycle in enumerate(cycles):
                ax = axes.flatten()[cy]
                x, y = varx[:, cy], vary[:, cy]
                for strain in xrange(num_strains):
                    ax.scatter(x[strain], y[strain], s=50,
                               color=colors[strain], label=E.strain_names[strain])            
                ax.set_xlim(xlims)
                ax.set_ylim(ylims)
                ax.set_xlabel(features[0])
                ax.set_ylabel(features[1])
                ax.set_title(cycle)
                if cy > 1:
                    ax.legend(scatterpoints=1, bbox_to_anchor=[1.2, .75, .2, .2], 
                        frameon=False, prop={'size': 8})

                fig.suptitle('%s vs. %s, %s -- 16 strains, points: %s' %(
                                features[1], features[0], bin_type, level), fontsize=16)
                plt.subplots_adjust(top=0.87)
                fname = dirname + '%s_%s_vs_%s_%s.pdf' %(
                                    level, features[1], features[0], bin_type)
                fig.savefig(fname, bbox_inches='tight')
                plt.close()

        elif bin_type == '12bins':
            fig, ax = plt.subplots(figsize=(6, 6))
            for strain in xrange(num_strains):
                ax.scatter(varx[strain], vary[strain],
                    color=colors[strain], label=E.strain_names[strain])
                hh, ll = ax.get_legend_handles_labels()
            ax.set_xlim(xlims)
            ax.set_ylim(ylims)
            ax.set_xlabel(features[0])
            ax.set_ylabel(features[1])
            ax.legend(hh, ll, 
                        scatterpoints=1, bbox_to_anchor=[1.1, .75, .2, .2], 
                        frameon=False, prop={"size": 8})
            ax.set_title('%s vs. %s, %s -- 16 strains, points: %s' %(
                features[1], features[0], bin_type, level))
            plt.subplots_adjust(top=0.87)
            fname = dirname + '%s_%s_vs_%s_%s.pdf' %(
                                level, features[1], features[0], bin_type)
            fig.savefig(fname, bbox_inches='tight')
            plt.close()
    
            if BREAKDOWN:
                fig, axes = plt.subplots(4, 4, figsize=(12, 12), sharex=True, sharey=True)
                for strain in xrange(num_strains):
                    ax = axes.flatten()[strain]
                    ax.scatter(varx[strain], vary[strain], color=colors[strain])            
                    # ax.set_xlim(xlims)
                    # ax.set_ylim(ylims)
                    ax.set_title(E.strain_names[strain])

                fig.suptitle('%s vs. %s, %s -- 16 strains, points: %s, strain breakdown' %(
                                features[1], features[0], bin_type, level), fontsize=16)
                plt.subplots_adjust(top=0.87)
                fname = dirname + '%s_%s_vs_%s_%s_breakdown.pdf' %(
                                    level, features[1], features[0], bin_type)
                fig.savefig(fname, bbox_inches='tight')
                plt.close()


    elif level == 'mouse':
        if bin_type == '24HDCLC':
            cycles = ['24H', 'DC', 'LC']
            fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
            for cy, cycle in enumerate(cycles):
                ax = axes.flatten()[cy]
                x, y = varx[:, cy], vary[:, cy]
                for strain in xrange(num_strains):
                    idx = data_labels[:, 0] == strain
                    ax.scatter(x[idx], y[idx], 
                               color=colors[strain], 
                               label=E.strain_names[strain])            
                ax.set_xlim(xlims)
                ax.set_ylim(ylims)
                ax.set_xlabel(features[0])
                ax.set_ylabel(features[1])
                ax.set_title(cycle)
                if cy > 1:
                    ax.legend(scatterpoints=1, 
                        bbox_to_anchor=[1.2, .7, .2, .2], 
                        frameon=False, prop={'size': 8})
                fig.suptitle('%s vs. %s, %s, 16 strains, points: %s' %(
                                features[1], features[0], bin_type, level), fontsize=16)
                plt.subplots_adjust(top=0.87)
                fname = dirname + '%s_%s_vs_%s_%s.pdf' %(
                                    level, features[1], features[0], bin_type)
                fig.savefig(fname, bbox_inches='tight')
                plt.close()

            if BREAKDOWN:
                for cy, cycle in enumerate(cycles):
                    fig, axes = plt.subplots(4, 4, figsize=(12, 12), sharex=True, sharey=True)
                    for strain in xrange(num_strains):
                        ax = axes.flatten()[strain]
                        idx = data_labels[:, 0] == strain
                        x, y = varx[idx, cy], vary[idx, cy]
                        ax.scatter(x, y, color=colors[strain])            
                        # ax.set_xlim(xlims)
                        # ax.set_ylim(ylims)
                        ax.set_title(E.strain_names[strain])

                    fig.suptitle('%s vs. %s, %s -- 16 strains, points: %s, strain breakdown' %(
                                    features[1], features[0], cycle, level), fontsize=16)
                    plt.subplots_adjust(top=0.87)
                    fname = dirname + '%s_%s_vs_%s_%s_breakdown.pdf' %(
                                        level, features[1], features[0], cycle)
                    fig.savefig(fname, bbox_inches='tight')
                    plt.close()


        elif bin_type == '12bins':
            fig, axes = plt.subplots(4, 4, figsize=(12, 12), sharex=True, sharey=True)
            for strain in xrange(num_strains): 
                ax = axes.flatten()[strain]
                idx = data_labels[:, 0] == strain
                x, y = varx[idx], vary[idx]
                for m in range(len(x)):        
                    ax.scatter(x[m], y[m], color=colors[strain])            
                ax.set_xlim(xlims)
                ax.set_ylim(ylims)
                ax.set_title(E.strain_names[strain])

            fig.suptitle('%s vs. %s, %s -- 16 strains, points: %s' %(
                            features[1], features[0], bin_type, level), fontsize=16)
            plt.subplots_adjust(top=0.87)
            fname = dirname + '%s_%s_vs_%s_%s.pdf' %(
                                level, features[1], features[0], bin_type)
            fig.savefig(fname, bbox_inches='tight')
            plt.close()


    elif level == 'mouseday':
        if bin_type == '24HDCLC':
            cycles = ['24H', 'DC', 'LC']
            for cy, cycle in enumerate(cycles):
                fig, axes = plt.subplots(4, 4, figsize=(12, 12), sharex=True, sharey=True)
                x, y = varx[:, cy], vary[:, cy]
                for strain in xrange(num_strains):
                    ax = axes.flatten()[strain]
                    idx = data_labels[:, 0] == strain
                    ax.scatter(x[idx], y[idx], color=colors[strain])
                    ax.set_xlim(xlims)
                    ax.set_ylim(ylims)
                    ax.set_title(E.strain_names[strain])
                fig.suptitle('%s vs. %s, %s -- 16 strains, points: %s' %(
                    features[1], features[0], cycle, level), fontsize=16)
                fname = dirname + '%s_%s_vs_%s_%s.pdf' %(
                                    level, features[1], features[0], cycle)
                fig.savefig(fname, bbox_inches='tight')
                plt.close()

        elif bin_type == '12bins':
            fig, axes = plt.subplots(4, 4, figsize=(12, 12), sharex=True, sharey=True)
            for strain in xrange(num_strains):
                ax = axes.flatten()[strain]
                idx = data_labels == strain
                x, y = varx[idx], vary[idx]
                for m in xrange(len(x)):                    
                    ax.scatter(x[m], y[m], color=colors[strain])
                ax.set_xlim(xlims)
                ax.set_ylim(ylims)
                ax.set_title(E.strain_names[strain])
            fig.suptitle('%s vs. %s, %s -- 16 strains, points: %s' %(
                features[1], features[0], bin_type, level), fontsize=16)
            fname = dirname + '%s_%s_vs_%s_%s_bin.pdf' %(
                                level, features[1], features[0], bin_type)
            fig.savefig(fname, bbox_inches='tight')
            plt.close()
    
    print "saved to:", fname
    if CLOSE:
        plt.close()
    return fig 


def plot_feature_vs_feature(E, bin_type, feature_pairs, WRITE_CSV=False):

    levels = ['strain', 'mouse', 'mouseday']    
    for level in levels:       
        for two_features in feature_pairs:
            plot_feat1_vs_feat2(E, two_features, bin_type, level)
            # xlims, ylims = None, None
            if WRITE_CSV:
                write_feat1_vs_feat2_to_csv(E, two_features, bin_type, level)


def write_feat1_vs_feat2_to_csv(E, fnames, bin_type='24HDCLC', level='strain'):

    data, data_labels = E.load_feature_vectors(fnames, bin_type, level)
    varx, vary = data                  # verify varx and vary are normally distributed
    
    if bin_type == '24HDCLC':
        cycles = ['24H', 'DC', 'LC']
        new_arr = np.zeros(len(data_labels))
        #reorganize arrays
        for cy in xrange(len(cycles)):
            new_arr = np.vstack([np.vstack([new_arr, varx[:, cy]]), vary[:, cy]])
        new_arr = new_arr[1:].T

        header = ['two_features'] + fnames*3
        sub_header = [''] + ['24H', '24H', 'DC', 'DC', 'LC', 'LC']

        formatter = (level, fnames[1], fnames[0], bin_type)
        fname = '%s_%s_vs_%s_%s.csv' %formatter

    elif bin_type == '12bins':
        bins = ['CT%d-%d' %(x, x+2) for x in range(6, 26, 2)] + \
                    ['CT%d-%d' %(x, x+2) for x in range(2, 6, 2)]
        num_bins = len(bins)
        new_arr = np.zeros(len(data_labels))
        
        #reorganize arrays
        for b in xrange(num_bins):
            new_arr = np.vstack([np.vstack([new_arr, varx[:, b]]), vary[:, b]])
        new_arr = new_arr[1:].T
        
        header = ['two_features'] + fnames*num_bins
        sub_header = [''] + bins

        formatter = (level, fnames[1], fnames[0], bin_type)
        fname = '%s_%s_vs_%s_%s.csv' %formatter

    dirname_out = E.figures_dir_subpar + 'features/vectors/feature_vs_feature/' + \
                    '%s_vs_%s/%s/csv_tables/' %formatter[1:]
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)    
    fname = dirname_out + fname
    with open(fname, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(header)
        writer.writerow(sub_header)
        c = 0
        for row in new_arr:
            if level == 'strain':
                label = '%s' %E.strain_names[c]
            elif level == 'mouse':
                s_num, m_num = data_labels[c]
                label = '%s M%d' %(E.strain_names[s_num], m_num)
            elif level == 'mouseday':
                s_num, m_num, md_num = data_labels[c]
                label = '%s M%d, day%d' %(
                        E.strain_names[s_num], m_num, md_num)
            text = np.hstack([label, ['%1.4f' %r for r in row]])
            writer.writerow(text)
            c += 1
    print "csv files saved to: %s" %(fname)

