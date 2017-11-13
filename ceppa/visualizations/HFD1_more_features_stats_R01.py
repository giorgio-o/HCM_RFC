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


# def one_way_anova_repeated(experiment):

    # E = experiment
E = HiFat2Experiment.HiFat2Experiment()
num_strains = E.num_strains

dirname = E.figures_dir + "stats/anova2x2/"
if not os.path.isdir(dirname): os.makedirs(dirname)

# bw for groups, each (pre- post-)
bws, labels = load_mouse_bodyweights(E)
idx1, idx2 = [labels[:, 0]==i for i in range(num_strains)]
bw1, bw2 = bws[idx1], bws[idx2]

N = len(bws)      # total number fo individuals

sub_id = [i for x in range(N) for i in [x, x]]
genotype = [E.strain_names[x] for x in list(labels[:, 0])*2]    # condition1: genotype
tpoints = ['Pre', 'Post']                                       # condition2: Pre vs Post 
timepoint = [tpoints[x] for x in [0, 1]*N]
BW = bws.ravel()        # dependent variable


Sub = namedtuple('Sub_id', ['Sub_id', 'BW', 'genotype', 'timepoint'])
df = pt.DataFrame()

for idx in xrange(len(sub_id)):
    df.insert(Sub(sub_id[idx],BW[idx], genotype[idx], timepoint[idx])._asdict()) 

df.box_plot('rt', factors=['iv1', 'iv2'])
plt.savefig(dirname + 'test1.pdf', bbox_inches='tight')
plt.close()

# anova
aov = df.anova('BW', sub='Sub_id', wfactors=['genotype', 'timepoint'])
# print(aov)





def two_way_anova_repeated_bodyweight(experiment):
    E = experiment
    num_strains = E.num_strains

    dirname = E.figures_dir + "stats/more_stats/"
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
    
    print_anova(sub_id, bodyweight, genotype, diet)


def two_way_anova_repeated_features(experiment):
    E = experiment
    num_strains = E.num_strains

    dirname = E.figures_dir + "stats/more_stats/"
    if not os.path.isdir(dirname): os.makedirs(dirname)

    # # bw for groups, each (pre- post-)
    # bws, labels = load_mouse_bodyweights(E)
    # num_obs1, num_obs2 = [len(bws[labels[:, 0]==i]) for i in range(num_strains)]
    # assert num_obs1 == num_obs2
    # num_obs = num_obs1
    # tot_obs = len(bw_labels)

    # get data
    food_intake_chow, labels_chow = E.generate_feature_vectors(feature='TF', level='mouse', bin_type='3cycles', days=E.chowDayNumbers)
    food_intake_hf, labels_hf = E.generate_feature_vectors(feature='TF', level='mouse', bin_type='3cycles', days=E.HiFatDayNumbers)
    distance_chow, _ = E.generate_feature_vectors(feature='TM', level='mouse', bin_type='3cycles', days=E.chowDayNumbers)
    distance_hf, _ = E.generate_feature_vectors(feature='TM', level='mouse', bin_type='3cycles', days=E.HiFatDayNumbers)

    # 24h mouse averages
    food_intake_chow = food_intake_chow[:, 0, 0]
    food_intake_hf = food_intake_hf[:, 0, 0]
    distance_chow = distance_chow[:, 0, 0]
    distance_hf = distance_hf[:, 0, 0]

    # nans
    idx_nan = ~np.isnan(food_intake_chow)
    food_intake_chow = food_intake_chow[idx_nan]
    labels_chow = labels_chow[idx_nan]
    distance_chow = distance_chow[idx_nan]

    idx_nan = ~np.isnan(food_intake_hf)
    food_intake_hf = food_intake_hf[idx_nan]
    labels_hf = labels_hf[idx_nan]
    distance_hf = distance_hf[idx_nan]
    
    assert (labels_hf == labels_chow).all()
    labels = labels_chow
    num_obs = len(labels[labels[:, 0] == 0])
    # # calories
    # cal_intake_chow1 = intake_chow1 *3.85   #kcal per gram
    # cal_intake_chow2 = intake_chow2 *3.85  
    # cal_intake_hf1 = intake_hf1 *4.73
    # cal_intake_hf2 = intake_hf2 *4.73 

    Daily_Total_Distance = np.hstack([distance_chow, distance_hf])


    sub_id = np.array([i+1 for i in range(num_obs)]*4)
    # independent variables: genotype WT vs KO
    genotype = np.hstack([labels[:, 0], labels[:, 0]]) + 1
    # and diet CH vs HF
    diet = np.hstack([np.zeros(len(labels)), np.ones(len(labels))]) + 1

    
    Sub = namedtuple('Sub_id', ['Sub_id', 'Daily_Total_Distance', 'genotype', 'diet'])
    df = pt.DataFrame()

    for idx in xrange(len(sub_id)):
        df.insert(Sub(sub_id[idx],Daily_Total_Distance[idx], genotype[idx], diet[idx])._asdict()) 

    # anova
    aov = df.anova('Daily_Total_Distance', sub='Sub_id', wfactors=['genotype', 'diet'])
    print(aov)


def two_way_anova_repeated_dc_lc(experiment):
    E = experiment
    num_strains = E.num_strains

    dirname = E.figures_dir + "stats/more_stats/"
    if not os.path.isdir(dirname): os.makedirs(dirname)

    # # bw for groups, each (pre- post-)
    # bws, labels = load_mouse_bodyweights(E)
    # num_obs1, num_obs2 = [len(bws[labels[:, 0]==i]) for i in range(num_strains)]
    # assert num_obs1 == num_obs2
    # num_obs = num_obs1
    # tot_obs = len(bw_labels)

    # get data
    food_intake_chow, labels_chow = E.generate_feature_vectors(feature='TF', level='mouse', bin_type='3cycles', days=E.chowDayNumbers)
    food_intake_hf, labels_hf = E.generate_feature_vectors(feature='TF', level='mouse', bin_type='3cycles', days=E.HiFatDayNumbers)

    # DC and LC mouse averages
    food_intake_chow = food_intake_chow[:, 1:, 0]
    food_intake_hf = food_intake_hf[:, 1:, 0]

    # LC/DC ratios
    ratio_chow = food_intake_chow[:, 1] / food_intake_chow[:, 0]
    ratio_hf = food_intake_hf[:, 1] / food_intake_hf[:, 0]
    # change in DC 
    dc_delta_intake = food_intake_hf[:, 0] - food_intake_chow[:, 0]
    lc_delta_intake = food_intake_hf[:, 1] - food_intake_chow[:, 1]

    # nans
    idx_nan = ~np.isnan(ratio_chow)
    ratio_chow = ratio_chow[idx_nan]
    labels_chow = labels_chow[idx_nan]

    idx_nan = ~np.isnan(ratio_hf)
    ratio_hf = ratio_hf[idx_nan]
    labels_hf = labels_hf[idx_nan]
    dc_delta_intake = dc_delta_intake[idx_nan]
    lc_delta_intake = lc_delta_intake[idx_nan]
    
    assert (labels_hf == labels_chow).all()
    labels = labels_chow
    num_obs = len(labels[labels[:, 0] == 0])
    # # calories
    # cal_intake_chow1 = intake_chow1 *3.85   #kcal per gram
    # cal_intake_chow2 = intake_chow2 *3.85  
    # cal_intake_hf1 = intake_hf1 *4.73
    # cal_intake_hf2 = intake_hf2 *4.73 

    Food_Intake_LC_to_DC_Ratio = np.hstack([ratio_chow, ratio_hf])


    sub_id = np.array([i+1 for i in range(num_obs)]*4)
    # independent variables: genotype WT vs KO
    genotype = np.hstack([labels[:, 0], labels[:, 0]]) + 1
    # and diet CH vs HF
    diet = np.hstack([np.zeros(len(labels)), np.ones(len(labels))]) + 1

    
    Sub = namedtuple('Sub_id', ['Sub_id', 'Food_Intake_LC_to_DC_Ratio', 'genotype', 'diet'])
    df = pt.DataFrame()

    for idx in xrange(len(sub_id)):
        df.insert(Sub(sub_id[idx],Food_Intake_LC_to_DC_Ratio[idx], genotype[idx], diet[idx])._asdict()) 

    # anova
    aov = df.anova('Food_Intake_LC_to_DC_Ratio', sub='Sub_id', wfactors=['genotype', 'diet'])
    print(aov)