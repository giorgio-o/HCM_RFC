import numpy as np
import matplotlib as mpl
import time

from ceppa import StrainSurveyExperiment 
from ceppa.visualizations import position_density
from ceppa.visualizations import rasters, raster_mouseday
from ceppa.visualizations import features_panel_CT, feat_vs_feat, feat_vs_feat_correlation, features_distribution
from ceppa.visualizations import breakfast, within_AS_structure #, time_budgets
# from ceppa.util import write_to_csv



"""
G.A.Onnis, 11.2016
	expanded: 04.2017

Tecott Lab UCSF
"""


np.set_printoptions(linewidth=250, precision=5, threshold=8000, suppress=True)
mpl.rc('font', family='sans-serif') 
# mpl.rc('text', usetex=True)

cstart = time.clock()


# # 0. BINARY FILES
# # generate binary files from HCM raw data
# E = StrainSurveyExperiment.StrainSurveyExperiment(IGNORE_MD=False)
# E.generate_binaries()

# # 1. BOUTS
# E = StrainSurveyExperiment.StrainSurveyExperiment()
# E.generate_bouts()

# # 2. ACTIVE STATES
# E.generate_active_states()

# test bout counts
# arr = E._check_bout_counts_in_bins(act='M')

# test feature relations



# # FIGURES
E = StrainSurveyExperiment.StrainSurveyExperiment()
# E.get_exp_info()

levels = [
    'strain',
    'mouse',
    'mouseday'
    ]  

vec_types = ['24HDCLC', '12bins']

err_types = ['stdev', 'stderr']


# # 0. data quality
# # need to add device error stuff  from original raw
# data_quality.plot_data_quality(E) 


# # 1. POSITION DENSITY
# for xbins, ybins in xy_bins:
#     for level in levels:
#         position_density.plot_position_density(
#                 E, xbins, ybins, level, NEST=True)   # use nest only for 2,4 


# # 2. RASTERS
# # # mousedays
# for group in E.groups[15:16]:
#     for mouse in group.individuals:
#         if not mouse.ignored:
#             for MD in mouse.mouse_days:
#                 if MD.dayNumber in E.daysToUse:
#                     if not MD.ignored:
#                         raster_mouseday.plot_raster_mouseday(
#                             E, mouse.mouseNumber, MD.dayNumber, 
#                             GENERATE=False)

# individuals
# rasters.plot_rasters(E, strain=3, FLAG_IGNORED=True, SHOW_DAYS=True)
# rasters.plot_rasters(E, strain=None, mouseNumber=5743, FLAG_IGNORED=True, SHOW_DAYS=True)

# strains
# rasters.plot_raster_strains(E, strains=[3], SHOW_DAYS=True)

# recording/maintenance time
# E = StrainSurveyExperiment.StrainSurveyExperiment(IGNORE_MD=False)
# rasters.plot_HCM_system_time(E, what='maintenance')
# rasters.plot_HCM_system_time(E, what='recording')


# # 3. BOUTS
# # visualizations check
# mouseNumber, day = 7206, 10
# raster_mouseday.plot_raster_mouseday(E, mouseNumber, day, GENERATE=False)
# rast.plot_rasters(E, mouseNumber, GENERATE=True)
# win_list = [
#     ((24, 0, 0), (26, 0, 0)),
#     ]
# if 0:
#     import bouts_vis_check
#     for t_start, t_end in win_list:
#         bouts_vis_check.run(E, mouseNumber, day,
#             t_start=t_start,
#             t_end=t_end,
#             GENERATE=False,
#             )



# # 4. FEATURES
# generate 
# keyList = ['active_states', 'totals', 'AS_intensities', 'bouts']
# features = E.features_by_type['active_states'] + E.features_by_type['totals'] + E.features_by_type['AS_intensities']
# features = E.features_by_type['bouts'][:5]
# features = E.features_by_type['bouts'][5:10]
# features = E.features_by_type['bouts'][10:]
# features = ['FASInt', 'WASInt', 'MASInt']           
# # # # arr, arr_labels = E.generate_feature_vectors(feat='MBD', vec_type='24HDCLC', GENERATE=True)

# for vec_type in vec_types[1:]:
#     for feature in features:
#         E.generate_feature_vectors(feature, vec_type, GENERATE=True, VERBOSE=True)

# panels
# for vec_type in vec_types[:1]:
#     for level in levels[2:]:
#         features_panel_CT.plot_features_panel(E, vec_type, level, 
#                                             err_type='stdev', COMMON_Y=False)  	# mouseday, COMMON_Y=False
        # features_panel_CT.write_csv_panel_table(E, vec_type=vec_type, level=level)

# write feature vectors to csv
# for vec_type in vec_types[1:]:
#     for level in levels[2:]:
#         features_panel_CT.write_feature_vectors_to_csv(E, vec_type, level)

# other csv for larry: mouse, bin x 24 features
# features_panel_CT.write_feature_vector_mouse_avgs_12bins_to_csv(E, vec_type='12bins', level='mouse')


# feature vs feature
# vec_types = ['24HDCLC', '12bins']
# import itertools
# features = ['ASP', 'TF', 'FASInt']
# feature_pairs = [[f1, f2] for f1, f2 in itertools.combinations(features, 2)]
# for vec_type in vec_types[:1]:
#     feat_vs_feat.plot_feature_vs_feature(E, vec_type, feature_pairs)

# features distributions
# for vec_type in vec_types:
    # features_distribution.plot_features_distribution_binned_and_avgs(E, vec_type)
    # features_distribution.plot_features_distribution_binned_and_avgs_by_strain(E, vec_type)

# all data from all mousedays
# all_data = features_distribution.plot_features_distribution_all_data(E, GENERATE=True)

# features correlations
# feat_vs_feat_correlation.plot_corr_matrices(E, vec_types[0])


# # bout features per AS
E = StrainSurveyExperiment.StrainSurveyExperiment()

# features = E.features_by_type['bouts'][12:]
# for feature in features:
#     E.generate_bout_feature_vectors_per_AS(feature, GENERATE=True, VERBOSE=True)
# from ceppa.visualizations import features_panel_AS
# features_panel_AS.plot_features_panel_AS(E, level='strain', err_type='stdev')




# # 5. BREAKFAST
# generate
# for act in ['F', 'W']:
# 	E.generate_breakfast_data(act=act, ONSET=True, GENERATE=True)

# figures
# for ONSET in [True, False]:
#     for num_mins in [5, 15]:
        # for err_type in err_types:
        #     breakfast.plot_breakfast(E, level='strain', err_type=err_type, 
        #         ONSET=ONSET, num_mins=num_mins)
        # breakfast.plot_breakfast_comparison(E, level='strain', err_type='stderr', 
        #       ONSET=ONSET, num_mins=num_mins)


# # 6. WITHIN AS
# generate
# E.generate_AS_structure()
# for num_mins in [5, 15]:
# 	within_AS_structure.plot_within_AS_structure(
# 		E, level='mouse', EARLY=True, num_mins=num_mins,
# 		s_start=12) 	



# # 7. PCA
from ceppa.visualizations import PCA_analysis
PCA_analysis.plot_PCA(E, lastcomp=5, EXCLUDE_SS=True)#len(E.features_by_activity))
# PCA_analysis.plot_PCA(E, level='mouseday', lastcomp=5, EXCLUDE_SS=False)#len(E.features_by_activity))

# # 7. TIME BUDGETS
# E.generate_time_budgets(cycle='24H', AS=False, GENERATE=True, VERBOSE=True)
# time_budgets.plot_time_budgets(E, level='strain', cycle='24H')





# # # OLD STUFF
# # 5. events
# feats = [
    # 'FC', 'LC',
    # 'FETS', 'WETS'
#     ]
# for feat in feats:
#     evts.plot_event_feature_vs_expdays(E, feat)
#     for MDS in [False, True]:
#         evts.plot_event_feature_distribution(E, feat, MDS=MDS)
    

# # 6. stats 
# # BOUTS
# for act in ['F']:#, 'W', 'M']:
#     for level in levels[:1]:
#         bouts_distribution.plot_bout_data_distribution(E, act, level)   # act='F'
    # bouts_distribution.plot_bout_numbers_data(E, act, level='strain')

# # # STATS ON OTHER HCM FEATURES. AS.

# # # STATS ON EVENTS
# num_bins = 100
# bins = np.logspace(-3, 3., num_bins)

# E.generate_event_interevent_data()
# # # # # EVENTS
# for LOG in [True, False]:
#     evts.plot_event_interevent_distribution(E, num_bins=100, LOGSCALE=LOG)

# evts.plot_event_interevent_distribution_all_strains(E)


# # 7. HYPER_PARAMS
# # ISTS = [1, 3, 5, 10, 15, 20, 25, 30, 45, 60, 90, 120, 180]
# # for IST in ISTS:
# #   E = StrainSurveyExperiment.StrainSurveyExperiment(IST=IST, IGNORE_MD=True)
# #   E.generate_active_states()

# # BTS = [1, 3, 5, 10, 15, 20, 25, 30, 45, 60, 90]
# # ingestion and move bouts are dependent via BT used. 
# # for BT in BTS:
# #   E = StrainSurveyExperiment.StrainSurveyExperiment(BT=BT, MBT=1, IGNORE_MD=True)
# #   E.generate_bouts()

# # MBTS = [0.1, 0.5, 1, 2, 3, 4, 5, 10]
# # for MBT in MBTS:
# #   E = StrainSurveyExperiment.StrainSurveyExperiment(BT=30, MBT=MBT, IGNORE_MD=True)
# #   E.generate_bouts()

# # MBTS = [1]
# # for MBT in MBTS:
# #   E = StrainSurveyExperiment.StrainSurveyExperiment(MBT=MBT)
# #   # for twindow in time_windows:
# #   bout_rasters_check.plot_brc(E, twindow=twindow, xtickstep=10)
# a

# hyper_analysis.plot_AS_numbers_vs_IST(E, ISTS=ISTS)

# for act_type in activity_types:
#   hyper_analysis.plot_bout_numbers_vs_BT(E, BTS=BTS, act_type=act_type)


cstop = time.clock()
print "\n--> main script ran in %1.2f minutes\n" %((cstop-cstart) / 60.)




