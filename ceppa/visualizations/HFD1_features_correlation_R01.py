import numpy as np
from scipy import stats


"""
G.Onnis, 10.2017

Tecott Lab UCSF
"""



def append_correlation(text, feat1, feat2, labels, group_names):    
    for strain, group_name in enumerate(group_names):
        idx = labels[:, 0] == strain
        f1, f2 = feat1[idx], feat2[idx]
        r, p = stats.pearsonr(f1, f2)   
        text.append("group %s, r: %1.4f, p-value=%1.6f" %(group_name, r, p))

    widx = [(0, 2), (1, 3)]
    for strain, group_name in enumerate(['WT', '2C']):
        idx = np.logical_or(labels[:, 0]==widx[strain][0], labels[:, 0]==widx[strain][1])
        f1, f2 = feat1[idx], feat2[idx]
        r, p = stats.pearsonr(f1, f2)
        text.append("group %s, r: %1.4f, p-value=%1.6f" %(group_name, r, p))

    f1, f2 = feat1[idx], feat2[idx]
    r, p = stats.pearsonr(feat1, feat2)
    text.append("all groups, r: %1.4f, p-value=%1.6f\n" %(r, p))



def some_features_correlation(E):
    """ this works for HFD1
    """
    group_names = E.group_names

    features_pairs =[('ASP', 'FASInt'), ('ASD', 'FASInt')]
    text = []
    text.append(E.short_name)
    text.append("\nPearson correlation r, p-value p:\n")
    for pair in features_pairs:
        feat1, feat2 = pair
        text.append([feat1, feat2])
        # get data
        feat1, labels = E.generate_feature_vectors(feat1, level='mouse', bin_type='3cycles')
        feat2, _ = E.generate_feature_vectors(feat2, level='mouse', bin_type='3cycles')
        # 24h mouse averages
        feat1 = feat1[:, 0, 0]
        feat2 = feat2[:, 0, 0]
        assert np.isnan(feat1).all() == False
        assert np.isnan(feat2).all() == False

        # group1, group2, group3, group4, group1+3 (WT), group2+4(2C), all (group1+2+3+4)
        append_correlation(text, feat1, feat2, labels, group_names)

    # BW and loco
    text.append(['BW_Pre', 'TM'])
    # get data
    feat1, labels = E.get_bodyweights()
    feat2, _ = E.generate_feature_vectors('TM', level='mouse', bin_type='3cycles')
    feat1 = feat1[:, 0]     # BW-Pre
    feat2 = feat2[:, 0, 0]
    append_correlation(text, feat1, feat2, labels, group_names)

    # TF DC vs LC
    text.append(['TF DC', 'TF LC'])
    feat, labels = E.generate_feature_vectors(feature='TF', level='mouse', bin_type='3cycles')
    feat1, feat2 = feat[:, 1, 0], feat[:, 2, 0]
    append_correlation(text, feat1, feat2, labels, group_names)

    for t in text:
        print t






