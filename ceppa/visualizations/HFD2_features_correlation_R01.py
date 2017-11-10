import numpy as np
from scipy import stats

# from ceppa import HiFat2Experiment


"""
G.Onnis, 10.2017

Tecott Lab UCSF
"""


def some_correlations(E_chow, E_hf):

    group_names = E_chow.group_names

    # get a bunch of data
    # bodyweight gain
    bws, gain_labels = E_chow.get_bodyweights()
    bwgain = bws[:, 2]
    bwgain = bwgain[~np.isnan(bwgain)]

    # features
    tkw = {'level':'mouse', 'bin_type':'3cycles'}
    (ASP_ch, labels_ch), (ASP_hf, _) = [exp.generate_feature_vectors('ASP', **tkw) for exp in [E_chow, E_hf]]
    (ASD_ch, labels_hf), (ASD_hf, _) = [exp.generate_feature_vectors('ASD', **tkw) for exp in [E_chow, E_hf]]
    (FASInt_ch, _), (FASInt_hf, _) = [exp.generate_feature_vectors('FASInt', **tkw) for exp in [E_chow, E_hf]]
    (TF_ch, _), (TF_hf, _) = [exp.generate_feature_vectors('TF', **tkw) for exp in [E_chow, E_hf]]
    (FBASR_ch, _), (FBASR_hf, _) = [exp.generate_feature_vectors('FBASR', **tkw) for exp in [E_chow, E_hf]]
    (FBS_ch, _), (FBS_hf, _) = [exp.generate_feature_vectors('FBS', **tkw) for exp in [E_chow, E_hf]]
    (MBS_ch, _), (MBS_hf, _) = [exp.generate_feature_vectors('MBS', **tkw) for exp in [E_chow, E_hf]]
    (MBD_ch, _), (MBD_hf, _) = [exp.generate_feature_vectors('MBD', **tkw) for exp in [E_chow, E_hf]]

    assert (labels_hf == labels_ch).all()
    assert(labels_hf == gain_labels).all()
    labels = labels_hf[:, 0]

    # 24h mouse average and nans
    ASP_ch, ASP_hf = ASP_ch[:, 0, 0], ASP_hf[:, 0, 0]
    ASD_ch, ASD_hf = ASD_ch[:, 0, 0], ASD_hf[:, 0, 0]

    FASInt_ch, FASInt_hf = FASInt_ch[:, 0, 0], FASInt_hf[:, 0, 0] 

    TF_DC_ch, TF_DC_hf = TF_ch[:, 1, 0], TF_hf[:, 1, 0] 
    TF_LC_ch, TF_LC_hf = TF_ch[:, 2, 0], TF_hf[:, 2, 0] 
    TF_ch, TF_hf = TF_ch[:, 0, 0], TF_hf[:, 0, 0]       # has to be last one

    FBASR_ch, FBASR_hf = FBASR_ch[:, 0, 0], FBASR_hf[:, 0, 0]
    FBS_ch, FBS_hf = FBS_ch[:, 0, 0], FBS_hf[:, 0, 0]

    MBS_ch, MBS_hf = MBS_ch[:, 0, 0], MBS_hf[:, 0, 0] 
    MBD_ch, MBD_hf = MBD_ch[:, 0, 0], MBD_hf[:, 0, 0] 

    #nans
    assert (np.isnan(ASP_hf) == np.isnan(ASP_ch)).all()
    labels = labels[~np.isnan(ASP_ch)]
    ASP_ch, ASP_hf = ASP_ch[~np.isnan(ASP_ch)], ASP_hf[~np.isnan(ASP_hf)]
    ASD_ch, ASD_hf = ASD_ch[~np.isnan(ASD_ch)], ASD_hf[~np.isnan(ASD_hf)]
    FASInt_ch, FASInt_hf = FASInt_ch[~np.isnan(FASInt_ch)], FASInt_hf[~np.isnan(FASInt_hf)]
    TF_ch, TF_hf = TF_ch[~np.isnan(TF_ch)], TF_hf[~np.isnan(TF_hf)]
    TF_DC_ch, TF_DC_hf = TF_DC_ch[~np.isnan(TF_DC_ch)], TF_DC_hf[~np.isnan(TF_DC_hf)]
    TF_LC_ch, TF_LC_hf = TF_LC_ch[~np.isnan(TF_LC_ch)], TF_LC_hf[~np.isnan(TF_LC_hf)]

    FBASR_ch, FBASR_hf = FBASR_ch[~np.isnan(FBASR_ch)], FBASR_hf[~np.isnan(FBASR_hf)]
    FBS_ch, FBS_hf = FBS_ch[~np.isnan(FBS_ch)], FBS_hf[~np.isnan(FBS_hf)]
    MBS_ch, MBS_hf = MBS_ch[~np.isnan(MBS_ch)], MBS_hf[~np.isnan(MBS_hf)]
    MBD_ch, MBD_hf = MBD_ch[~np.isnan(MBD_ch)], MBD_hf[~np.isnan(MBD_hf)]

    #changes
    ASP_change = ASP_hf - ASP_ch
    FASInt_change = FASInt_hf - FASInt_ch
    TF_DC_change = TF_DC_hf - TF_DC_ch
    TF_LC_change = TF_LC_hf - TF_LC_ch
    FBASR_change = FBASR_hf - FBASR_ch
    FBS_change = FBS_hf - FBS_ch


    # all 9 combinations: WTCH, WTHF, KOCH, KOHF, all WT, all KO, all individuals
    fpairs_group_and_cycle =[
        ('ASP', 'FASInt'), 
        ('ASD', 'FASInt'),
        ('TF DC', 'TF LC'),    
        ]

    arrays_gc = [
        (ASP_ch, ASP_hf, FASInt_ch, FASInt_hf),
        (ASD_ch, ASD_hf, FASInt_ch, FASInt_hf),
        (TF_DC_ch, TF_DC_hf, TF_LC_ch, TF_LC_hf)
        ]

    text = []
    text.append(E_chow.short_name)
    text.append("\nPearson correlation r, p-value p:\n")

    # first 
    for pair, arrs in zip(fpairs_group_and_cycle, arrays_gc):
        feat1_name, feat2_name = pair
        feat1_ch, feat1_hf, feat2_ch, feat2_hf = arrs
        text.append([feat1_name, feat2_name])
        
        # group1, group2, group3, group4, group1+3 (WT), group2+4(2C), all (group1+2+3+4)
        # append_correlation(text, feat1, feat2, labels, group_names)

        for strain, group_name in enumerate(group_names):
            text.append('- ' + group_name)
            idx = labels == strain
            f1, f2, f3, f4 = feat1_ch[idx], feat1_hf[idx], feat2_ch[idx], feat2_hf[idx]
            r, p = stats.pearsonr(f1, f3)   
            text.append("group %sLF, r: %1.4f, p-value=%1.6f" %(group_name, r, p))
            r, p = stats.pearsonr(f2, f4)   
            text.append("group %sHF, r: %1.4f, p-value=%1.6f" %(group_name, r, p))
            # all group, CH and HF
            r, p = stats.pearsonr(np.hstack([f1, f2]), np.hstack([f3, f4]))   
            text.append("all group %s, r: %1.4f, p-value=%1.6f" %(group_name, r, p))

        r, p = stats.pearsonr(np.hstack([feat1_ch, feat1_hf]), np.hstack([feat2_ch, feat2_hf]))
        text.append("- all individuals, r: %1.4f, p-value=%1.6f\n" %(r, p))

    # second
    fpairs_group = [
        ('change in ASP', 'change in FASInt'),
        ('BWGain', 'change in TF DC'),
        ('BWGain', 'change in TF LC'),
        ('BWGain', 'change in FBASR'),
        ('BWGain', 'change in FBS'),
        ]

    arrays_g = [
        (ASP_change, FASInt_change),
        (bwgain, TF_DC_change),
        (bwgain, TF_LC_change),
        (bwgain, FBASR_change),
        (bwgain, FBS_change),
        ]

    for pair, arrs in zip(fpairs_group, arrays_g):
        feat1_name, feat2_name = pair
        feat1, feat2 = arrs
        text.append([feat1_name, feat2_name])
        
        # group1, group2, group3, group4, group1+3 (WT), group2+4(2C), all (group1+2+3+4)
        # append_correlation(text, feat1, feat2, labels, group_names)

        for strain, group_name in enumerate(group_names):
            idx = labels == strain
            # all group
            r, p = stats.pearsonr(feat1[idx], feat2[idx])
            text.append("%s, r: %1.4f, p-value=%1.6f" %(group_name, r, p))

        r, p = stats.pearsonr(feat1, feat2)
        text.append("- all individuals, r: %1.4f, p-value=%1.6f\n" %(r, p))


    # third
    text.append(['BWGain', 'TF'])
    idx = labels==1
    r, p = stats.pearsonr(bwgain[idx], TF_ch[idx])
    text.append("KOCH, r: %1.4f, p-value=%1.6f\n" %(r, p))

    text.append(['BWGain', 'TF'])
    r, p = stats.pearsonr(bwgain[idx], TF_hf[idx])
    text.append("KOHF, r: %1.4f, p-value=%1.6f\n" %(r, p))

    idx = labels==0
    text.append(['BWGain', 'MBS'])
    r, p = stats.pearsonr(bwgain[idx], MBS_ch[idx])
    text.append("WTCH, r: %1.4f, p-value=%1.6f\n" %(r, p))

    text.append(['BWGain', 'MBD'])
    r, p = stats.pearsonr(bwgain[idx], MBD_ch[idx])
    text.append("WTCH, r: %1.4f, p-value=%1.6f\n" %(r, p))

    for t in text:
        print t

