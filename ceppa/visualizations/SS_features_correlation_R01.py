import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os



"""
G.Onnis, 10.2017

Tecott Lab UCSF
"""

np.set_printoptions(precision=4, threshold=8000)



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



