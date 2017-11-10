import numpy as np
import matplotlib as mpl
import time

from ceppa import HiFat1Experiment 
from ceppa.visualizations import position_density 
from ceppa.visualizations import rasters, raster_mouseday
from ceppa.visualizations import HFD1_features_correlation_R01, HFD1_more_features_stats_R01
# from ceppa.visualizations import features_panel_CT#, features_panel_expdays, features_distribution
# from ceppa.visualizations import breakfast, breakfast_cycles, within_AS_structure, time_budgets

"""
G.Onnis, 03.2017

Tecott Lab UCSF
"""


np.set_printoptions(linewidth=250, precision=5, threshold=8000, suppress=True)
mpl.rc('font', family='sans-serif') 
# mpl.rc('text', usetex=True)

cstart = time.clock()


# # 0. BINARY FILES
# generate binary files from HCM raw data
# E = HiFat1Experiment.HiFat1Experiment(IGNORE_MD=False)
# E.generate_binaries()


# # 1. BOUTS 
# E.generate_bouts()

# # 2. ACTIVE STATES
# E.generate_active_states()


# # 4. FEATURES
# keyList = ['active_states', 'totals', 'AS_intensities', 'bouts']
# features = E.features_by_type['active_states'] + E.features_by_type['totals'] + E.features_by_type['AS_intensities'] 
# features = E.features_by_type['AS_intensities'][2:]
# features = ['MASInt']


# for bin_type in E.bin_types[:2]:
#     for feature in features:
#         E.generate_feature_vectors(feature, bin_type=bin_type, GENERATE=True, VERBOSE=True)



# test the bastards
# E.test_features()

# test bout counts
# arr = E._check_bout_counts_in_bins(act='M')



# # FIGURES
# E = HiFat1Experiment.HiFat1Experiment()
# E.get_exp_info()



# # 1. POSITION DENSITY 
# for xbins, ybins in xy_bins[:1]:
#     for level in levels:
#         position_density.plot_position_density(
#                 E, xbins, ybins, level, NEST=False, FLAG_IGNORED=True)   # use nest only for 2,4 


# # 2. RASTERS
# mousedays
# for group in E.groups[3:4]:
#     for mouse in group.individuals:
#         if not mouse.ignored:
#             for MD in mouse.mouse_days:
#                 if MD.dayNumber in E.daysToUse:
#                     if 1:#not MD.ignored:
#                         raster_mouseday.plot_raster_mouseday(
#                             E, mouse.mouseNumber, MD.dayNumber, 
#                             GENERATE=False, FLAG_IGNORED=True)

# individuals
# rasters.plot_rasters(E, strain=3, FLAG_IGNORED=True, SHOW_DAYS=True)
# rasters.plot_rasters(E, strain=None, mouseNumber=5743, FLAG_IGNORED=True, SHOW_DAYS=True)

# strains
# rasters.plot_raster_strains(E, strains=[3], SHOW_DAYS=True)

# recording/maintenance time
# E = HiFat1Experiment.HiFat1Experiment(IGNORE_MD=False)
# rasters.plot_HCM_system_time(E, what='maintenance')
# rasters.plot_HCM_system_time(E, what='recording')


# # # 3. FEATURES
# panel
E = HiFat1Experiment.HiFat1Experiment(IGNORE_MD=True)

# HFD1_features_correlation_R01.some_features_correlation(E)

HFD1_more_features_stats_R01.two_way_anova_repeated_bodyweight(E)
# HFD1_more_features_stats_R01.two_way_anova_repeated_features(E)
# HFD1_more_features_stats_R01.two_way_anova_repeated_dc_lc(E)


# for bin_type in E.bin_types[:1]:
#     for level in E.levels[:1]:
#         for err_type in E.err_types:
#             features_panel_CT.plot_features_panel(E, level, bin_type, err_type)

# for bin_type in bin_types[:1]:
#     for level in levels:
#         features_panel_CT.plot_features_panel(E, bin_type, level, COMMON_Y=True)
        # features_panel_CT.write_csv_panel_table(E, bin_type=bin_type, level=level)


# write feature vectors to csv
# for bin_type in bin_types[1:]:
#     for level in levels[2:]:
#         features_panel_CT.write_feature_vectors_to_csv(E, bin_type, level)

# feature vs experimental days
# bin_type = '24HDCLC'
# level = 'strain'
# features_panel_expdays.plot_features_panel(E, bin_type, level, 
#             err_type='stdev', GENERATE=True, COMMON_Y=False, plotType='markers')



# # 5. BREAKFAST
# generate
# for cycle in E.cycles:
#     for act in ['F', 'W']:
#         E.generate_breakfast_data(act=act, ONSET=True, cycle=cycle, GENERATE=True)


# figures
# for ONSET in [True, False]:
#     for num_mins in [5, 15]:
#         for err_type in err_types:
#             breakfast.plot_breakfast(E, level='strain', err_type=err_type, 
#                 ONSET=ONSET, num_mins=num_mins)
#         breakfast.plot_breakfast_comparison(E, level='strain', err_type='stderr', 
#               ONSET=ONSET, num_mins=num_mins)

# # cycles
# for cycle in E.cycles:
#     breakfast.plot_breakfast(E, level='strain', cycle=cycle,
#         err_type='stderr', ONSET=True, num_mins=15)

# breakfast_cycles.plot_breakfast_cycles(
# 	E, level='strain', err_type='stderr', ONSET=True)



# # 6. WITHIN AS
# within_AS_structure.plot_within_AS_structure(E, level='strain', cycle='LC')


# # 7. TIME BUDGETS
# for cycle in E.cycles:
# 	E.generate_time_budgets(cycle=cycle, AS=False, GENERATE=True, VERBOSE=True)
    # time_budgets.plot_time_budgets(E, level='strain', cycle=cycle)





cstop = time.clock()
print "\n--> main script ran in %1.2f minutes\n" %((cstop-cstart) / 60.)

