from Experiments import StrainSurveyExperiment
from sklearn import preprocessing, metrics
from sklearn.metrics import pairwise_distances
from sklearn.cluster import KMeans

import numpy as np
import matplotlib.pyplot as plt
import os
import itertools
import seaborn as sns
import my_utils
import time
"""
G.Onnis, 11.2016

Tecott Lab UCSF
"""


def KMeans_score_2(experiment, feature='ASP', num_bins=11, n_jobs=-2):

    E = experiment
    num_strains = E.num_strains
    name = KMeans_score.__name__

    dir_out = E.derived_dir + 'learning/clustering/%s_data/' %feature
    if not os.path.isdir(dir_out): os.makedirs(dir_out)
    fname1, fname2 = ['%s_%s_%s__test.npy' %(name, feature, text) for text in ['_score', '_centroids']]

    try:
        score = np.load(dir_out + fname1)
        centroids = np.load(dir_out + fname2)
        print "loaded %s, 11d %s vector data" %(name, feature)
    except IOError:
        cstart = time.clock()
        arr, arr_labels = E.generate_feature_vectors(feature, GET_AVGS=False)
        feature_names = ['%sbin%d' %('ASP', n) for n in xrange(num_bins)]
        # take half of the dataset out
        Xtr, Xte, Ytr, Yte = my_utils.split_half_dataset(arr, arr_labels)
        
        print "computing %s, 11d %s vector.." %(name, feature)
        KM = KMeans(n_clusters=2, init='k-means++', random_state=0, n_jobs=n_jobs)
        score = np.ones((num_strains, num_strains))
        centroids = np.zeros((num_strains, num_strains, 2, num_bins))
        for strain1, strain2 in itertools.combinations(range(num_strains), 2):

            print "strain%d vs. strain%d" %(strain1, strain2)
            km_model = KM.fit(Xtr)
            score[strain1, strain2] = metrics.fowlkes_mallows_score(Ytr, km_model.labels_)
            centroids[strain1, strain2] = km_model.cluster_centers_
    
        cstop = time.clock()
        print "%s took %1.2fs" %(name, cstop-cstart)
        np.save(dir_out + fname1, score)
        np.save(dir_out + fname2, centroids)
        print "binary output saved to: %s" %dir_out

    return km_model, score, centroids, Xte, Yte


def KMeans_score(experiment, feature='ASP', num_bins=11, n_jobs=-2):

    E = experiment
    num_strains = E.num_strains
    name = KMeans_score.__name__

    dir_out = E.derived_dir + 'learning/clustering/%s_data/' %feature
    if not os.path.isdir(dir_out): os.makedirs(dir_out)
    fname1, fname2 = ['%s_%s_%s__.npy' %(name, feature, text) for text in ['_score', '_centroids']]

    try:
        score = np.load(dir_out + fname1)
        centroids = np.load(dir_out + fname2)
        print "loaded %s, 11d %s vector data" %(name, feature)
    except IOError:
        cstart = time.clock()
        arr, arr_labels = E.generate_feature_vectors(feature, GET_AVGS=False)
        feature_names = ['%sbin%d' %('ASP', n) for n in xrange(num_bins)]

        print "computing %s, 11d %s vector.." %(name, feature)
        KM = KMeans(n_clusters=2, init='k-means++', random_state=0, n_jobs=n_jobs)
        score = np.ones((num_strains, num_strains))
        centroids = np.zeros((num_strains, num_strains, 2, num_bins))
        for strain1, strain2 in itertools.combinations(range(num_strains), 2):

            print "strain%d vs. strain%d" %(strain1, strain2)
            X, Y = my_utils.get_dataset_two_strains_and_shuffle(
                arr, arr_labels, strain1, strain2)

            km_model = KM.fit(X)
            score[strain1, strain2] = metrics.fowlkes_mallows_score(Y, km_model.labels_)
            centroids[strain1, strain2] = km_model.cluster_centers_
    
        cstop = time.clock()
        print "%s took %1.2fs" %(name, cstop-cstart)
        np.save(dir_out + fname1, score)
        np.save(dir_out + fname2, centroids)
        print "binary output saved to: %s" %dir_out

    return score, centroids


def plot_score(experiment, feature, score, name='KMeans'):
    num_strains = score.shape[0]

    mask = np.zeros_like(score, dtype=bool)
    mask[np.tril_indices_from(mask)] = True

    fig, ax = plt.subplots(figsize=(5, 5))

    g = sns.heatmap(score, mask=mask, cmap=plt.get_cmap("viridis"), linewidths=0.5, 
        vmin=.5, vmax=1, square=True, annot=False, fmt='', cbar_kws={'shrink':.5}, ax=ax)

    # stop
    g.set_xticklabels(E.strain_names, fontsize=8, rotation=315, ha='left', y=0.015)
    g.set_yticklabels(E.strain_names[::-1], fontsize=8, rotation=0)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Strain')
    ax.set_ylabel('Strain')

    title = '**Clustering - Pairwise %s\nusing %s 11D feature vectors, half mousedays\navg score=%1.4f, std=%1.4f' \
        %(name, feature, score[~mask].mean(), score[~mask].std())
    ax.set_title(title)

    
    dir_out = E.plots_dir + 'learning/clustering/pairwise/'
    if not os.path.isdir(dir_out): os.makedirs(dir_out)
    fname = dir_out + '%s_pairwise_%s_score__test.pdf' %(feature, name)
    fig.savefig(fname, bbox_inches='tight')
    plt.close()
    print "figures output saved to: %s" %fname


def get_group_11d_centroids(centroids):
    num_strains = centroids.shape[0]
    num_bins = centroids.shape[-1]
    arr = np.zeros((num_strains, num_strains-1, num_bins))
    arr[0] = centroids[0,:,0][1:]
    for strain in xrange(num_strains-1):
        i_row = centroids[strain, :, 0][strain+1:]
        i_col = centroids[:, strain, 1][:strain]
        arr[strain] = np.vstack((i_col, i_row))
    arr[-1] = centroids[:, 15, 1][:15]
    return arr


def run(experiment, feature='ASP'):
    E = experiment
    score, centroids = KMeans_score(E, feature)
    plot_score(E, feature, score)
    

def run_2(experiment, feature='ASP'):
    km_model, score, centroids, Xte, Yte = KMeans_score_2(E, feature)
    plot_score(E, feature, score)
    strain_centroids = get_group_11d_centroids(centroids)
    stop


if __name__ == '__main__':
    np.set_printoptions(precision=4, linewidth=800)
    E = StrainSurveyExperiment.StrainSurveyExperiment()
    run_2(E, feature='ASP')




