import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

from ceppa import HiFat2Experiment

"""
G.Onnis, 10.2017

Tecott Lab UCSF
"""

np.set_printoptions(precision=4, threshold=8000)


def intake_DC_LC(experiment):

    E = experiment 
    group_names = ['WT', 'KO']

    dirname = E.figures_dir + "stats/body_weight_and_intake/"
    if not os.path.isdir(dirname): os.makedirs(dirname)

    # get data
    food_intake_chow, mouse_labels_chow = E.generate_feature_vectors(feature='TF', level='mouse', bin_type='3cycles', days=E.chowDayNumbers)
    food_intake_hf, mouse_labels_hf = E.generate_feature_vectors(feature='TF', level='mouse', bin_type='3cycles', days=E.HiFatDayNumbers)

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
    mouse_labels_chow = mouse_labels_chow[idx_nan]

    idx_nan = ~np.isnan(ratio_hf)
    ratio_hf = ratio_hf[idx_nan]
    mouse_labels_hf = mouse_labels_hf[idx_nan]
    dc_delta_intake = dc_delta_intake[idx_nan]
    lc_delta_intake = lc_delta_intake[idx_nan]


    # values for the two groups
    ratio_chow1 = ratio_chow[mouse_labels_chow[:, 0] == 0]
    ratio_chow2 = ratio_chow[mouse_labels_chow[:, 0] == 1]
    ratio_hf1 = ratio_hf[mouse_labels_hf[:, 0] == 0]
    ratio_hf2 = ratio_hf[mouse_labels_hf[:, 0] == 1]
    dc_delta_intake1 = dc_delta_intake[mouse_labels_chow[:, 0] == 0]
    dc_delta_intake2 = dc_delta_intake[mouse_labels_chow[:, 0] == 1]
    lc_delta_intake1 = lc_delta_intake[mouse_labels_chow[:, 0] == 0]
    lc_delta_intake2 = lc_delta_intake[mouse_labels_chow[:, 0] == 1]

    # averages
    arrs = [ratio_chow1, ratio_chow2, ratio_hf1, ratio_hf2]
    dc_arrs = [dc_delta_intake1, dc_delta_intake2]
    lc_arrs = [lc_delta_intake1, lc_delta_intake2]
    avgs_ratio = [x.mean() for x in arrs]
    yerrs1 = [stats.sem(x) for x in arrs]
    avgs_delta_dc = [x.mean() for x in dc_arrs]
    yerrs2 = [stats.sem(x) for x in dc_arrs]
    avgs_delta_lc = [x.mean() for x in lc_arrs]
    yerrs3 = [stats.sem(x) for x in lc_arrs]

    # # statistical significance
    equal_var = False
    print "\nWelch's t-Test values, does not assume equal population variance:\n"

    # LC/DC ratio
    print "LC/DC Intake Ratio:"
    # compare chow
    t, p = stats.ttest_ind(ratio_chow1, ratio_chow2, equal_var=equal_var) 
    print  "%sCH vs. %sCH: p-value=%1.7f" %(group_names[0], group_names[1], p)
    # compare HiFat
    t, p = stats.ttest_ind(ratio_hf1, ratio_hf2, equal_var=equal_var)
    print  "%sHF vs. %sHF: p-value=%1.7f" %(group_names[0], group_names[1], p)

    # DC Change
    print "\nDC Intake change:" 
    t, p = stats.ttest_ind(dc_delta_intake1, dc_delta_intake2, equal_var=equal_var)
    print  "%s vs %s: p-value=%1.7f" %(group_names[0], group_names[1], p)

    # LC Change
    print "\nLC Intake change:" 
    t, p = stats.ttest_ind(lc_delta_intake1, lc_delta_intake2, equal_var=equal_var)
    print  "%s vs %s: p-value=%1.7f" %(group_names[0], group_names[1], p)
    print 

    # # # # box_plot
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.4)) 
    bar_width1, bar_width2 = 0.5, 0.25
    xs1, xs2 = range(4), range(2)
    cases = ['%s%s' %(x, y) for x in group_names for y in ['CH', 'HF']]
    
    tkw = {'widths':.3, 'flierprops':{'markersize':3}}
    ax[0].boxplot(arrs, labels=cases, **tkw)
    ax[0].set_title('Food Intake LC/DC ratio')

    ax[1].boxplot(dc_arrs, labels=group_names, **tkw)
    ax[1].set_ylabel('[grams]')
    ax[1].set_title('DC Intake change')

    ax[2].boxplot(lc_arrs, labels=group_names, **tkw)
    ax[2].set_ylabel('[grams]')
    ax[2].set_title('LC Intake change')

    plt.subplots_adjust(wspace=.4)
    plt.savefig(dirname + "food_intake_lc_dc_ratio_boxplot.pdf", bbox_inches='tight')
    plt.close()


    # # # # bar plot
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.4)) 
    bar_width1, bar_width2 = 0.5, 0.25
    xs1, xs2 = range(4), range(2)
    cases = ['%s%s' %(x, y) for x in group_names for y in ['CH', 'HF']]

    ax[0].bar(xs1, avgs_ratio, bar_width1, yerr=[[0, 0, 0, 0], yerrs1])
    ax[0].set_xlim((-.5, 3.5))
    ax[0].set_xticks(xs1)
    ax[0].set_xticklabels(cases)
    ax[0].set_title('Food Intake LC/DC ratio')

    ax[1].bar(xs2, avgs_delta_dc, bar_width2, yerr=[yerrs2, [0, 0]])
    ax[1].set_xlim((-.5, 1.5))
    ax[1].set_xticks(xs2)
    ax[1].set_xticklabels(group_names)
    ax[1].set_ylabel('[grams]')
    ax[1].set_title('DC Intake change')

    ax[2].bar(xs2, avgs_delta_lc, bar_width2, yerr=[[0, 0], yerrs3])
    ax[2].set_xlim((-.5, 1.5))
    ax[2].set_xticks(xs2)
    ax[2].set_xticklabels(group_names)
    ax[2].set_ylabel('[grams]')
    ax[2].set_title('LC Intake change')

    plt.subplots_adjust(wspace=.4)
    plt.savefig(dirname + "food_intake_lc_dc_ratio_bar.pdf", bbox_inches='tight')
    plt.close()



def intake_and_distance(experiment):

    E = experiment 
    group_names = ['WT', 'KO']

    dirname = E.figures_dir + "stats/body_weight_and_intake/"
    if not os.path.isdir(dirname): os.makedirs(dirname)

    # get data
    food_intake_chow, mouse_labels_chow = E.generate_feature_vectors(feature='TF', level='mouse', bin_type='3cycles', days=E.chowDayNumbers)
    food_intake_hf, mouse_labels_hf = E.generate_feature_vectors(feature='TF', level='mouse', bin_type='3cycles', days=E.HiFatDayNumbers)
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
    mouse_labels_chow = mouse_labels_chow[idx_nan]
    distance_chow = distance_chow[idx_nan]

    idx_nan = ~np.isnan(food_intake_hf)
    food_intake_hf = food_intake_hf[idx_nan]
    mouse_labels_hf = mouse_labels_hf[idx_nan]
    distance_hf = distance_hf[idx_nan]

    # values for the two groups
    intake_chow1 = food_intake_chow[mouse_labels_chow[:, 0] == 0]
    intake_chow2 = food_intake_chow[mouse_labels_chow[:, 0] == 1]
    intake_hf1 = food_intake_hf[mouse_labels_hf[:, 0] == 0]
    intake_hf2 = food_intake_hf[mouse_labels_hf[:, 0] == 1]
    distance_chow1 = distance_chow[mouse_labels_hf[:, 0] == 0]
    distance_chow2 = distance_chow[mouse_labels_hf[:, 0] == 1]
    distance_hf1 = distance_hf[mouse_labels_hf[:, 0] == 0]
    distance_hf2 = distance_hf[mouse_labels_hf[:, 0] == 1]

    # calories
    cal_intake_chow1 = intake_chow1 *3.85   #kcal per gram
    cal_intake_chow2 = intake_chow2 *3.85  
    cal_intake_hf1 = intake_hf1 *4.73
    cal_intake_hf2 = intake_hf2 *4.73   


    # averages
    gram_arrs = [intake_chow1, intake_hf1, intake_chow2, intake_hf2]
    kcal_arrs = [cal_intake_chow1, cal_intake_hf1, cal_intake_chow2, cal_intake_hf2]
    d_arrs = [distance_chow1, distance_hf1, distance_chow2, distance_hf2]

    gram_avgs = [x.mean() for x in gram_arrs]
    yerrs1 = [stats.sem(x) for x in gram_arrs]
    kcal_avgs = [x.mean() for x in kcal_arrs]
    yerrs2 = [stats.sem(x) for x in kcal_arrs]
    distance_avgs = [x.mean() for x in d_arrs]
    yerrs3 = [stats.sem(x) for x in d_arrs]

    # # statistical significance
    equal_var = False
    print "\nWelch's t-Test values, does not assume equal population variance:\n"
    
    # gram intake
    print "Daily Food Intake [grams]:"
    # compare chow
    t, p = stats.ttest_ind(intake_chow1, intake_chow2, equal_var=equal_var) 
    print  "%sCH vs. %sCH: p-value=%1.7f" %(group_names[0], group_names[1], p)
    # compare HiFat
    t, p = stats.ttest_ind(intake_hf1, intake_hf2, equal_var=equal_var)
    print  "%sHF vs. %sHF: p-value=%1.7f" %(group_names[0], group_names[1], p)


    # kcal intake
    print "\nDaily Food Intake [kcal]:"
    # compare chow
    t, p = stats.ttest_ind(cal_intake_chow1, cal_intake_chow2, equal_var=equal_var) 
    print  "%sCH vs. %sCH: p-value=%1.7f" %(group_names[0], group_names[1], p)
    # compare HiFat
    t, p = stats.ttest_ind(cal_intake_hf1, cal_intake_hf2, equal_var=equal_var)
    print  "%sHF vs. %sHF: p-value=%1.7f" %(group_names[0], group_names[1], p)


    # kcal intake
    print "\nDaily Distance [m]:"
    # compare chow
    t, p = stats.ttest_ind(distance_chow1, distance_chow2, equal_var=equal_var) 
    print  "%sCH vs. %sCH: p-value=%1.7f" %(group_names[0], group_names[1], p)
    # compare HiFat
    t, p = stats.ttest_ind(distance_hf1, distance_hf2, equal_var=equal_var)
    print  "%sHF vs. %sHF: p-value=%1.7f" %(group_names[0], group_names[1], p)
    print 

    # # # # box_plot
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.4)) 
    bar_width1, bar_width2 = 0.5, 0.25
    xs1, xs2 = range(4), range(2)
    cases = ['%s%s' %(x, y) for x in group_names for y in ['CH', 'HF']]
    
    tkw = {'widths':.3, 'flierprops':{'markersize':3}}
    ax[0].boxplot(gram_arrs, labels=cases, **tkw)
    ax[0].set_ylabel('[grams]')
    ax[0].set_title('Daily Food Intake [g]')

    ax[1].boxplot(kcal_arrs, labels=cases, **tkw)
    ax[1].set_ylabel('[kcal]')
    ax[1].set_title('Daily Food Intake [kcal]')

    ax[2].boxplot(d_arrs, labels=cases, **tkw)
    ax[2].set_ylabel('[m]')
    ax[2].set_title('Daily Total Distance [m]')

    plt.subplots_adjust(wspace=.4)
    plt.savefig(dirname + "intake_and_distance_boxplot.pdf", bbox_inches='tight')
    plt.close()

    # # # bar
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.4)) 
    bar_width = 0.5
    xs = range(4)
    cases = ['%s%s' %(x, y) for x in group_names for y in ['CH', 'HF']]

    ax[0].bar(xs, gram_avgs, bar_width, yerr=[[0, 0, 0, 0], yerrs1])
    ax[0].set_xlim((-.5, 3.5))
    ax[0].set_xticks(xs)
    ax[0].set_xticklabels(cases)
    ax[0].set_ylabel('[grams]')
    ax[0].set_title('Daily Food Intake [g]')

    ax[1].bar(xs, kcal_avgs, bar_width, yerr=[[0, 0, 0, 0], yerrs2])
    ax[1].set_xlim((-.5, 3.5))
    ax[1].set_xticks(xs)
    ax[1].set_xticklabels(cases)
    ax[1].set_ylabel('[kcal]')
    ax[1].set_title('Daily Food Intake [kcal]')

    ax[2].bar(xs, distance_avgs, bar_width, yerr=[[0, 0, 0, 0], yerrs3])
    ax[2].set_xlim((-.5, 3.5))
    ax[2].set_xticks(xs)
    ax[2].set_xticklabels(cases)
    ax[2].set_ylabel('[m]')
    ax[2].set_title('Daily Total Distance [m]')

    plt.subplots_adjust(wspace=.3)
    plt.savefig(dirname + "intake_and_distance_bar.pdf", bbox_inches='tight')
    plt.close()




def bw_and_bw_gain_t_test(E):
    """ 
    """
    num_strains = E.num_strains

    dirname = E.figures_dir + "stats/body_weight_and_intake/"
    if not os.path.isdir(dirname): os.makedirs(dirname)

    # get bodyweight for the dataset
    bws, labels = [], []
    for group in E.groups:
        for mouse in group.individuals:
            if not mouse.ignored:
                bw_start, bw_end = mouse.body_weight_start_of_experiment_grams, mouse.body_weight_end_of_experiment_grams
                bws.append([bw_start, bw_end, bw_end - bw_start])       # bw_pre, bw_post, bw_gain = bw_pre - bw_post
                labels.append([mouse.groupNumber, mouse.mouseNumber])

    mouse_bws, mouse_labels = np.array(bws), np.array(labels)


    # extract relevant data for the two groups
    bw1 = [mouse_bws[mouse_labels[:, 0] == 0, i] for i in [0, 1]]    # pre, post
    bw2 = [mouse_bws[mouse_labels[:, 0] == 1, i] for i in [0, 1]]

    bw_gain1 = mouse_bws[mouse_labels[:, 0] == 0, 2]    
    bw_gain2 = mouse_bws[mouse_labels[:, 0] == 1, 2]

    # averages
    bw_avgs = [bw1[0].mean(0), bw1[1].mean(0), bw2[0].mean(0), bw2[1].mean(0)]
    yerrs1 = [stats.sem(bw1[0]), stats.sem(bw1[1]), stats.sem(bw2[0]), stats.sem(bw2[1])]

    bw_gain_avgs = [bw_gain1.mean(0), bw_gain2.mean(0)]
    yerrs2 = [stats.sem(bw_gain1), stats.sem(bw_gain2)]

    group_names = E.strain_names

    # # statistical significance
    equal_var = False
    print "Welch's t-Test values, does not assume equal population variance:\n"
    print "Body Weights:"
    # compare pre
    t, p = stats.ttest_ind(bw1[0], bw2[0], equal_var=equal_var) 
    print  "%sPre vs. %sPre: p-value=%1.7f" %(group_names[0], group_names[1], p)
    # compare post
    t, p = stats.ttest_ind(bw1[1], bw2[1], equal_var=equal_var)
    print  "%sEnd vs. %sEnd: p-value=%1.7f" %(group_names[0], group_names[1], p)

    print "\nBody Weight Gain:" 
    t, p = stats.ttest_ind(bw_gain1, bw_gain2, equal_var=equal_var)
    print  "%s vs %s: p-value=%1.7f" %(group_names[0], group_names[1], p)
    print 

    # check normal distribution: QQ plot
    # for arr in [bw1[0], bw1[1], bw2[0], bw2[1]]:
    #     plt.figure()
    #     stats.probplot(arr, dist="norm", plot=plt)
    # check equal variance: not really 

    # # # # box_plot
    arrs = [bw1[0], bw1[0], bw2[0], bw2[1]]
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.4)) 
    bar_width1, bar_width2 = 0.5, 0.25
    xs1, xs2 = range(4), range(2)
    cases = ['%s%s' %(x, y) for x in group_names for y in ['CH', 'HF']]
    
    tkw = {'widths':.3, 'flierprops':{'markersize':3}}
    ax[0].boxplot(arrs, labels=cases, **tkw)
    ax[0].set_ylabel('[grams]')
    ax[0].set_title('Body Weight')

    ax[1].boxplot([bw_gain1, bw_gain2], labels=group_names, **tkw)
    ax[1].set_ylabel('[grams]')
    ax[1].set_title('Body Weight Gain')

    plt.subplots_adjust(wspace=.4)
    plt.savefig(dirname + "body_weight_boxplot.pdf", bbox_inches='tight')
    plt.close()


    # # # bar
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.6)) 
    bar_width1, bar_width2 = 0.5, 0.25
    xs1, xs2 = range(4), range(2)
    cases = ['%s %s' %(x, y) for x in group_names for y in ['Pre', 'End']]

    ax[0].bar(xs1, bw_avgs, bar_width1, yerr=[[0, 0, 0, 0], yerrs1])
    ax[0].set_xlim((-.5, 3.5))
    ax[0].set_xticks(xs1)
    ax[0].set_xticklabels(cases)
    ax[0].set_ylabel('grams')
    ax[0].set_title('Body Weight')

    ax[1].bar(np.arange(2), bw_gain_avgs, bar_width2, yerr=[[0, 0], yerrs2])
    ax[1].set_xlim((-.5, 1.5))
    ax[1].set_xticks(xs2)
    ax[1].set_xticklabels(group_names)
    ax[1].set_title('Body Weight Gain')
    plt.savefig(dirname + "body_weight_bar.pdf")
    plt.close()



def correlation_pairs_SS(experiment, level='mouse', bin_type='3cycles', err_type='stdev'):
    """ prints correlation and p-=values for features pairs 
        and some groups for StrainSurvay Experiment
    """
    E = experiment
    fpairs = [('ASN', 'ASD'), ('FBS', 'FBASR'), ('ASP', 'FASInt')]

    dirname = E.figures_dir + "stats/"
    if not os.path.isdir(dirname): os.makedirs(dirname)

    texts = []
    for features in fpairs:

        # load data  
        data, labels = E.load_features_vectors(features, level, bin_type, err_type)

        # 24H averages
        data = data[:, :, 0, 0]
        #nan
        idx_nan = ~np.isnan(data[0])
        data = data[:, idx_nan]
        labels = labels[idx_nan]

        group_names = ['B6', 'DBA', 'all_others']

        idx_B6, idx_DBA  = 0, 4
        arr1 = data[:,labels[:, 0] == idx_B6]
        arr2 = data[:,labels[:, 0] == idx_DBA]

        idx_all_others = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        others_data = np.zeros([len(features), 1])
        for idx in idx_all_others:
            idx_mice = labels[:, 0] == idx
            others_data = np.hstack([others_data, data[:, idx_mice]])
        arr3 = others_data[:, 1:]

        texts.append("%s vs. %s:" %(features[1], features[0]))

        for i, arr in enumerate([arr1, arr2, arr3]):
            r, p = stats.pearsonr(arr[0], arr[1])
            texts.append("group %s, r: %1.4f, p-value=%1.4f" %(group_names[i], r, p))

        texts.append("\n")    

        # # # # box_plot
        arrs = [bw1[0], bw1[0], bw2[0], bw2[1]]
        fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.4)) 
        bar_width1, bar_width2 = 0.5, 0.25
        xs1, xs2 = range(4), range(2)
        cases = ['%s%s' %(x, y) for x in group_names for y in ['CH', 'HF']]
        
        tkw = {'widths':.3, 'flierprops':{'markersize':3}}
        ax[0].boxplot(arrs, labels=cases, **tkw)
        ax[0].set_ylabel('[grams]')
        ax[0].set_title('Body Weight')

        ax[1].boxplot([bw_gain1, bw_gain2], labels=group_names, **tkw)
        ax[1].set_ylabel('[grams]')
        ax[1].set_title('Body Weight Gain')

        plt.subplots_adjust(wspace=.4)
        plt.savefig(dirname + "body_weight_boxplot.pdf", bbox_inches='tight')
        plt.close()

        # # # bar
        fig, ax = plt.subplots(1, 2, figsize=(8, 3.6)) 
        bar_width1, bar_width2 = 0.5, 0.25
        xs1, xs2 = range(4), range(2)
        cases = ['%s %s' %(x, y) for x in group_names for y in ['Pre', 'End']]

        ax[0].bar(xs1, bw_avgs, bar_width1, yerr=[[0, 0, 0, 0], yerrs1])
        ax[0].set_xlim((-.5, 3.5))
        ax[0].set_xticks(xs1)
        ax[0].set_xticklabels(cases)
        ax[0].set_ylabel('grams')
        ax[0].set_title('Body Weight')

        ax[1].bar(np.arange(2), bw_gain_avgs, bar_width2, yerr=[[0, 0], yerrs2])
        ax[1].set_xlim((-.5, 1.5))
        ax[1].set_xticks(xs2)
        ax[1].set_xticklabels(group_names)
        ax[1].set_title('Body Weight Gain')
        plt.savefig(dirname + "body_weight_bar.pdf")
        plt.close()



    print "\n"
    for text in texts:
        print text



