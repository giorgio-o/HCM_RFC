import numpy as np
import matplotlib.pyplot as plt
import itertools
from scipy import stats
import os 
import csv

from ceppa.visualizations import plotting_utils
from ceppa.util import my_utils




def compute_corr_matrix(E, bin_type='24HDCLC', levels=[], WRITE=True, BREAKDOWN=False):

    features = E.features_by_activity
    s_data, s_labels, m_data, m_labels, md_data, md_labels = E.load_feature_vectors(features, bin_type)

    arr_list = []                    
    if bin_type == '24HDCLC':
        num_bins = 3
    elif bin_type == '12bins':
        num_bins = 12
    for level, data in zip(levels, [s_data, m_data, md_data]):
        arr = np.zeros([num_bins, 2, len(features), len(features)])      # 24H,DC,LC, r and p-value
        for b in xrange(num_bins):
            for ii, jj in itertools.combinations(range(len(features)), 2):
                varx, vary = data[ii], data[jj]                  # verify varx and vary are normally distributed
                rho, pval = stats.pearsonr(varx[:, b], vary[:, b])
                arr[b, :, ii, jj] = rho, pval
            # values on diagonal
            for ii in range(len(features)):
                # varx = data[ii]
                # rho, pval = stats.pearsonr(varx[:, b], varx[:, b])
                # arr[b, :, ii, ii] = rho, pval
                arr[b, 0] = plotting_utils.nanize_trilow_values(arr[b, 0], diag_value=1)
                arr[b, 1] = plotting_utils.nanize_trilow_values(arr[b, 1], diag_value=1)
            
        if WRITE:
            write_csv_corr_table(E, arr, bin_type, level) 
        arr_list.append(arr)   
    return arr_list




def plot_corr_matrices(E, bin_type='24HDCLC'):
    features = E.features_by_activity
    levels = E.levels 
    arr_list = compute_corr_matrix(E, bin_type, levels)
    dirname_out = os.path.join(E.figures_dir_subpar, 'features/pearson_r/%s/' %bin_type)
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)  
    
    if bin_type == '24HDCLC':
        bins = ['24H', 'DC', 'LC']
    elif bin_type == '12bins':
        bins = ['bin%d' %i for i in xrange(11)]

    for level, arr in zip(levels, arr_list):
        for b, bin_ in enumerate(bins):
            data = arr[b, 0, :, :]
            fig, ax = plt.subplots(figsize=(12, 12))
            im = ax.imshow(data, interpolation='nearest', 
                           cmap='viridis', vmin=-1, vmax=1)
            for i, j in itertools.combinations(range(len(features)), 2):
                ax.text(j-.45, i, '%1.3f' %data[i, j], 
                        fontsize=6, weight='bold', color='w', transform=ax.transData)
            ax.xaxis.tick_top()
            ax.set_xticks(range(len(features)))
            ax.set_xticklabels(features, fontsize=9, rotation=270)
            ax.set_yticks(range(len(features)))
            ax.set_yticklabels(features, fontsize=9)
            ax.tick_params(direction='out', pad=5)
            ax.yaxis.set_label_position('right') 
            cb = fig.colorbar(im, ax=ax, shrink=.7)
            fig.suptitle('Pearson r correlation matrix\n all features - %s %s' %(level, bin_), fontsize=20)
            fname = dirname_out + "%s_Pearson_r_matrix_all_features_%s" %(bin_, level)
            fig.savefig(fname, bbox_inches='tight')
            print "saved to:", fname
            plt.close()


def write_csv_corr_table(E, arr, bin_type='24HDCLC', level='strain'):
    
    dirname_out = os.path.join(E.figures_dir_subpar, 'features/correlation/pearson_r/%s/csv_tables/' %bin_type)
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)    
    print "writing to csv.."
    feature_names = E.features_by_activity

    if bin_type == '24HDCLC':
        cycles = ['24H', 'DC', 'LC']

        for cy, header in enumerate(cycles):
            if level == 'strain':
                sub_header = ['all strains'] + feature_names  
            elif level == 'mouse':
                sub_header = ['all mice'] + feature_names
            elif level == 'mouseday':
                sub_header = ['all mousedays'] + feature_names
            
            fname = 'corr_table_%s_%s.csv' %(header, level)
            with open(dirname_out + fname, 'wb') as csv_file:
                writer = csv.writer(csv_file, delimiter=",")
                writer.writerow([header])
                writer.writerow(sub_header)
                c = 0
                for row in arr[cy, 0, :, :]:     # r value
                    feat = feature_names[c]
                    writer.writerow(np.hstack(['%s' %feat, ['%1.4f' %r for r in row]]))
                    c += 1
            print "csv files saved to:\n%s" %(dirname_out + fname)

    elif bin_type == '12bins':
        bins = ['bin%d' %i for i in xrange(11)]
        for bin_num, header in enumerate(bins):
            if level == 'strain':
                sub_header = ['all strains'] + feature_names  
            elif level == 'mouse':
                sub_header = ['all mice'] + feature_names
            elif level == 'mouseday':
                sub_header = ['all mousedays'] + feature_names
            
            fname = 'corr_table_%s_%s.csv' %(header, level)
            with open(dirname_out + fname, 'wb') as csv_file:
                writer = csv.writer(csv_file, delimiter=",")
                writer.writerow([header])
                writer.writerow(sub_header)
                c = 0
                for row in arr[bin_num, 0, :, :]:     # r value
                    feat = feature_names[c]
                    writer.writerow(np.hstack(['%s' %feat, ['%1.4f' %r for r in row]]))
                    c += 1
            print "csv files saved to:\n%s" %(dirname_out + fname)    

