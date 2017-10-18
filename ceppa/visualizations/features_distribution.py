import numpy as np
import matplotlib.pyplot as plt
import itertools
import os 
import csv

from ceppa.visualizations import plotting_utils
from ceppa.util import my_utils


def plot_features_distribution_binned_and_avgs(E, bin_type='24HDCLC', NORMED=False):

    dirname_out = os.path.join(
                    E.figures_dir_subpar, 'features/vectors/distributions/%s/' %bin_type)
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)  
    
    if bin_type == '24HDCLC':
        bins = ['24H', 'DC', 'LC']
    elif bin_type == '12bins':
        bins = ['CT%d-%d' %(x, x+2) for x in range(6, 26, 2)] + \
                    ['CT%d-%d' %(x, x+2) for x in range(2, 6, 2)]

    features, levels = E.features, E.levels
    s_data, s_labels, m_data, m_labels, md_data, md_labels = \
                            E.load_feature_vectors(features, bin_type)

    hist_bins = 50
    for level, data in zip(levels, [s_data, m_data, md_data]):
        for b, tbin in enumerate(bins):
            fig, axes = plt.subplots(8, 3, figsize=(8, 12))
            for f, feat in enumerate(features):
                ax = axes.flatten()[f]
                arr = data[f, :, b]
                color = E.plot_settings_dict[features[f]]['color']

                # set xmax
                x_max = np.mean(data[f]) + 5*np.std(data[f])
                hist_bins = np.linspace(0, x_max, 50)
                weights = np.ones_like(arr)
                if NORMED:
                    weights /=len(arr)

                y, _, _ = ax.hist(arr, bins=hist_bins,  weights=weights, color=color)
                ax.set_xlim(0, x_max)
                ax.tick_params(axis='both', labelsize=6)
                plt.subplots_adjust(left=0.1, right=0.88, hspace=0.6)
                ax.set_title(feat, fontsize=10)
                plotting_utils.ax_cleanup(ax)

            fig.suptitle('Features distributions\nbinned and averages\n%s %s' %(tbin, level))
            fname = dirname_out + "%s_features_distribution_binavgs_%s.pdf" %(level, tbin)
            fig.savefig(fname, bbox_inches='tight')
            print "saved to:", fname
            plt.close()
    

def plot_features_distribution_binned_and_avgs_by_strain(E, bin_type='24HDCLC', NORMED=False):
    features = E.features
    _, _, _, _, md_data, md_labels = E.load_feature_vectors(features, bin_type) 

    if bin_type == '24HDCLC':
        bins = ['24H', 'DC', 'LC']
    elif bin_type == '12bins':
        bins = ['CT%d-%d' %(x, x+2) for x in range(6, 26, 2)] + \
                    ['CT%d-%d' %(x, x+2) for x in range(2, 6, 2)]

    level = 'mouseday'    
    hist_bins = 50
    for b, tbin in enumerate(bins[:1]):
        dirname_out = os.path.join(E.figures_dir_subpar, 'features/vectors/distributions/%s/strain_breakdown/%s/' %(bin_type, tbin))
        if not os.path.isdir(dirname_out): os.makedirs(dirname_out) 
        for strain in xrange(E.num_strains):
            idx = md_labels[:, 0] == strain
            data = md_data
            fig, axes = plt.subplots(8, 3, figsize=(8, 12))
            for f, feat in enumerate(features):
                ax = axes.flatten()[f]
                arr = data[f, idx, b]

                # set xmax
                x_max = np.mean(data[f]) + 5*np.std(data[f])
                hist_bins = np.linspace(0, x_max, 50)
                weights = np.ones_like(arr)
                if NORMED:
                    weights /=len(arr)
                color = E.plot_settings_dict[features[f]]['color']

                y, _, _ = ax.hist(arr, bins=hist_bins,  weights=weights, color=color)
                ax.set_xlim(0, x_max)
                ax.tick_params(axis='both', labelsize=6)
                plt.subplots_adjust(left=0.1, right=0.88, hspace=0.6)
                ax.set_title(feat, fontsize=10)
                plotting_utils.ax_cleanup(ax)

            fig.text(0.05, 0.95, E.strain_names[strain], fontsize=16)
            fig.suptitle('Features distributions\nbinned and averages\nbinned%s %s' %(tbin, level))
            fname = dirname_out + "%s_all_features_distribution_binavgs_%s_strain%d.pdf" %(level, tbin, strain)
            fig.savefig(fname, bbox_inches='tight')
            print "saved to:", fname
            plt.close()



def plot_features_distribution_all_data(E, NORMED=False, GENERATE=False, VERBOSE=False):
    """24H and mouseday only
    """
    features = E.features[:3]
    # features dictionary each key (feature) is a list - 16 strains - 
    # of lists - all feature values during days -
    all_data = {}
    for feat in features:
        all_data[feat] = E.generate_feature_arrays(feat, GENERATE, VERBOSE)
    return all_data
        # # manipulate the list
        # arr_list = [list(x) for x in feat_arrays]
        # data.append(np.array(list(itertools.chain(*arr_list))))
    
    hist_bins = 50
    # fig, ax = plt.subplots(figsize=(8, 12))
    fig, axes = plt.subplots(8, 3, figsize=(8, 12))
    for f, feat in enumerate(features):
        ax = axes.flatten()[f]
        arr = data[f]
        # set xmax
        x_max = np.mean(data[f]) + 5*np.std(data[f])
        hist_bins = np.linspace(0, x_max, 50)
        weights = np.ones_like(arr)
        if NORMED:
            weights /=len(arr)
        color = E.plot_settings_dict[features[f]]['color']

        y, _, _ = ax.hist(arr, bins=hist_bins,  weights=weights, color=color)
        ax.set_xlim(0, x_max)
        ax.tick_params(axis='both', labelsize=6)
        plt.subplots_adjust(left=0.1, right=0.88, hspace=0.6)
        ax.set_title(feat, fontsize=10)
        plotting_utils.ax_cleanup(ax)

    fig.suptitle('Features distributions\nall data 24H  from all mousedays')
    dirname_out = os.path.join(E.figures_dir_subpar, 'features/vectors/distributions/')
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)  
    fname = dirname_out + "mousedays_all_features_distribution_all_data_24H.pdf" 
    fig.savefig(fname, bbox_inches='tight')
    print "saved to:", fname
    plt.close()

    return feat_arrays


def get_dirname_out(E, bin_type, level, strain):
    path_to = 'features/vectors/csv_files/%s_days/%s/%s/' %(E.use_days, bin_type, level)
    # if level == 'strain':
    #     path_to += 'avg_' + group_avg_type
    dirname = os.path.join(E.figures_dir_subpar, path_to)

    if bin_type == '12bins' and level in ['mouse', 'mouseday']:
        dirname += 'strain%d/' %strain
    if not os.path.isdir(dirname): os.makedirs(dirname) 
    return dirname


def write_vector_to_csv(E, arr_data, labels, bin_type, level, fname, header, sub_header, strain=None, group_avg_type='over_mds'):

    dirname = get_dirname_out(E, bin_type, level, strain)  

    with open(os.path.join(dirname, fname), 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow([header])
        writer.writerow(sub_header)
        c = 0
        for row in arr_data:
            if level == 'strain':
                row_label = E.strain_names[labels[c]]
            elif level == 'mouse':
                row_label = 'M%d' %labels[c, 1]
            elif level == 'mouseday':
                row_label = 'M%d' %labels[c, 1] + ' day%d' %labels[c, 2]
            writer.writerow(np.hstack([row_label, ['%1.4f' %r for r in row]]))
            c += 1
        print "csv files saved to:\n%s" % fname


def write_feature_vectors_to_csv(E, bin_type='12bins', level='strain', group_avg_type='over_mds'):
    features = E.features_by_activity
    print "%s..\nlevel: %s\nbin_type: %s" %(write_feature_vectors_to_csv.__name__, level, bin_type)

    data, labels = E.load_feature_vectors(features, bin_type, level, group_avg_type)

    if bin_type == '24HDCLC':
        bins = ['24H', 'DC', 'LC']
    elif bin_type == '12bins':
        bins = ['CT%d-%d' %(x, x+2) for x in range(6, 30, 2)] 

    arr = data.swapaxes(0, 1)
    # labels = labels[:, np.newaxis]

    if bin_type == '12bins':
        b = 0
        for tbin in bins:
            avg_type = 'avg_' + group_avg_type
            header = [level, tbin, avg_type] 
            sub_header = [''] + features
            if level == 'strain':
                fname = 'all_feature_vectors_table_%s_%s_%s.csv' %(level, tbin, avg_type)
                write_vector_to_csv(E, arr[:, :, b], labels, bin_type, level, fname, header, sub_header)

            elif level in ['mouse', 'mouseday']:
                for strain in xrange(E.num_strains):
                    header = [level, tbin]
                    sub_header = [E.strain_names[strain]] + features
                    idx = labels[:, 0] == strain
                    fname = 'all_feature_vectors_table_%s_%s_strain%d.csv' %(level, tbin, strain)
                    write_vector_to_csv(E, arr[idx, :, b], labels[idx], bin_type, level, fname, header, sub_header, strain)

            b +=1

    elif bin_type == '24HDCLC':
        b = 0
        for tbin in bins:
            avg_type = 'avg_' + group_avg_type
            header = [level, tbin, avg_type] 
            sub_header = [''] + features
            if level == 'strain':
                fname = 'all_feature_vectors_table_%s_%s_%s.csv' %(level, tbin, avg_type)
                write_vector_to_csv(E, arr[:, :, b], labels, bin_type, level, fname, header, sub_header)

            elif level in ['mouse', 'mouseday']:
                for strain in xrange(E.num_strains):
                    header = [level, tbin]
                    sub_header = [E.strain_names[strain]] + features
                    idx = labels[:, 0] == strain
                    fname = 'all_feature_vectors_table_%s_%s_strain%d.csv' %(tbin, level, strain)
                    write_vector_to_csv(E, arr[idx, :, b], labels[idx], bin_type, level, fname, header, sub_header)     

            b +=1





