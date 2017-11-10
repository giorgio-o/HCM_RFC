import numpy as np
import matplotlib.pyplot as plt
import os
from collections import namedtuple

import pyvttbl as pt 

from ceppa import HiFat2Experiment

"""
G.Onnis, 10.2017

Tecott Lab UCSF
"""

np.set_printoptions(precision=4, threshold=8000)


def load_mouse_bodyweights(E):
    # get bodyweight for the dataset
    bws, labels = [], []
    for group in E.groups:
        for mouse in group.individuals:
            if not mouse.ignored:
                bw_start, bw_end = mouse.body_weight_start_of_experiment_grams, mouse.body_weight_end_of_experiment_grams
                bws.append([bw_start, bw_end])       # bw_pre, bw_post, bw_gain = bw_pre - bw_post
                labels.append([mouse.groupNumber, mouse.mouseNumber])

    return np.array(bws), np.array(labels)


def one_way_anova_repeated_body_weight(experiment):
    E = experiment
    num_strains = E.num_strains

    dirname = E.figures_dir + "stats/more_stats/body_weight_and_intake/"
    if not os.path.isdir(dirname): os.makedirs(dirname)

    # bw for groups, each (pre- post-)
    bws, labels = load_mouse_bodyweights(E)
    num_obs1, num_obs2 = [len(bws[labels[:, 0]==i]) for i in range(num_strains)]
    assert num_obs1 == num_obs2
    num_obs = num_obs1

    sub_id = np.array([i+1 for i in range(num_obs)]*4)
    # independent variables: genotype WT vs KO
    genotype = np.hstack([labels[:, 0], labels[:, 0]]) + 1
    # and diet CH vs HF
    diet = np.hstack([np.zeros(len(bws)), np.ones(len(bws))]) + 1

    # dependent variable, bodyweights in follwoing order: 
    # geno1 bw pre, geno2 bw pre, geno1 bw post, geno2 bw post
    bodyweight = np.hstack([bws[:,0], bws[:,1]])


    Sub = namedtuple('Sub_id', ['Sub_id', 'bodyweight', 'genotype', 'diet'])
    df = pt.DataFrame()

    for idx in xrange(len(sub_id)):
        df.insert(Sub(sub_id[idx],bodyweight[idx], genotype[idx], diet[idx])._asdict()) 

    # df.box_plot('rt', factors=['iv1', 'iv2'])
    # plt.savefig(dirname + 'test1.pdf', bbox_inches='tight')
    # plt.close()

    # anova
    aov = df.anova('bodyweight', sub='Sub_id', wfactors=['genotype', 'diet'])
    print(aov)





