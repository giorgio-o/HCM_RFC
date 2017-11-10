import numpy as np
import matplotlib as mpl
import time

from ceppa import HiFat2Experiment 
from ceppa.visualizations import position_density_QC
from ceppa.visualizations import rasters, raster_mouseday
from ceppa.visualizations import features_panel_CT
from ceppa.visualizations import HFD2_some_features_stats_R01, HFD2_more_features_stats_R01, HFD2_features_correlation_R01
# from ceppa.visualizations import features_panel_expdays, features_activity_panel_CT#, features_distribution, features_panel_days#
# from ceppa.visualizations import breakfast, breakfast_cycles, within_AS_structure, diet_chow_to_HF_transition
# from ceppa.visualizations import time_budgets


"""
G.Onnis, 03.2017

Tecott Lab UCSF
"""


np.set_printoptions(linewidth=250, precision=5, threshold=8000, suppress=True)
mpl.rc('font', family='sans-serif') 
# mpl.rc('text', usetex=True)

cstart = time.clock()


# E = HiFat2Experiment.HiFat2Experiment(
#         IGNORE_MD=False, 
#         use_days='acclimated')


# # 0. BINARY FILES
# generate binary files from HCM raw data
# E.generate_binaries()

# # 1. BOUTS 
# E.generate_bouts()

# # 2. ACTIVE STATES
# E.generate_active_states()

# 3. POSITION DENSITY   
# for xbins, ybins in E.xy_bins[:1]:
    # for cycle in E.all_cycles:
    #     E.generate_position_density(cycle=cycle, tbin_type=None, 
    #                                     xbins=xbins, ybins=ybins, GENERATE=True)
    # for tbin_type in ['12bins']:#, 'AS12bins']:
    #     E.generate_position_density(cycle=None, tbin_type=tbin_type, 
    #                                     xbins=xbins, ybins=ybins, GENERATE=True)

    # E.check_position_bin_times(xbins=xbins, ybins=ybins, tbin_type='3cycles')

# # 4. FEATURES
# keyList = ['active_states', 'totals', 'AS_intensities', 'bouts']
# features = E.features_by_type['active_states'] + E.features_by_type['totals'] + E.features_by_type['AS_intensities'] 
# features = E.features_by_type['active_states']
# # # features = ['MASInt']

# for bin_type in E.bin_types[:2]:
#     for feature in features:
#         E.generate_feature_vectors(feature, bin_type=bin_type, GENERATE=True, VERBOSE=True)





# # FIGURES
# E = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=False, use_days='chow')
# E.get_exp_info()

# xy_bins = [
#     [2, 4],
#     [12, 24], 
#     ]

# levels = [
#     'strain',
#     'mouse',
#     'mouseday'
#     ]

# bin_types = ['24HDCLC', '12bins']
# err_types = ['stdev', 'stderr']


# # 1. POSITION DENSITY 
# for xbins, ybins in xy_bins[:1]:
#     for level in levels:
#         position_density.plot_position_density(
#                 E, xbins, ybins, level, NEST=True)   # use nest only for 2,4 



# # 2. RASTERS
# E = HiFat2Experiment.HiFat2Experiment(use_days='acclimated')
# mousedays
# for group in E.groups[1:]:
#     for mouse in group.individuals:
#         if not mouse.ignored:
#             for MD in mouse.mouse_days:
#                 if MD.dayNumber in E.daysToUse:
#                     if 1:#not MD.ignored:
#                         raster_mouseday.plot_raster_mouseday(
#                             E, mouse.mouseNumber, MD.dayNumber, 
#                             GENERATE=False, FLAG_IGNORED=True)

# individuals
# E = HiFat2Experiment.HiFat2Experiment(use_days='diet')
# rasters.plot_rasters(E, strain=0, FLAG_IGNORED=True, SHOW_DAYS=True)
# rasters.plot_rasters(E, strain=None, mouseNumber=6635, FLAG_IGNORED=True, SHOW_DAYS=True)

# strains
# rasters.plot_raster_strains(E, strains=[1], SHOW_DAYS=True)

# recording/maintenance time
# E = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=False, use_days='all')
# rasters.plot_HCM_system_time(E, what='maintenance')
# rasters.plot_HCM_system_time(E, what='recording')



# # 3. FEATURES
# use_days = ['pre_diet', 'post_diet', 'chow', 'transition']

# panel
# for use_d in use_days:

#     E = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=True, use_days=use_d)
    
#     for bin_type in E.bin_types[1:2]:
#         for level in E.levels[:1]:
#             for err_type in E.err_types:
#                 features_panel_CT.plot_features_panel(E, level, bin_type, err_type)

    # features_panel_CT.write_panel_to_csv_across_days(E)
    # features_panel_CT.write_panel_to_csv_collapse_over_days(E)

# E = HiFat2Experiment.HiFat2Experiment(use_days='acclimated')
# features_panel_expdays.plot_features_panel_12bins(E)
# features_panel_expdays.plot_features_panel_24H(E)
# features_panel_expdays.plot_features_panel_DC_LC(E)
# features_panel_expdays.write_panel_24H_to_csv(E)
# features_panel_expdays.write_panel_DC_LC_to_csv(E)
# features_panel_expdays.plot_features_panel_LC_DC_ratio(E)


# plot per day, only F
# E = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=True, use_days='across_diet_change')

# features_activity_panel_CT.plot_features_activity_panel(E, 
#                                     level='group', 
#                                     act = 'F',
#                                     bin_type='12bins', 
#                                     err_type='sem')



# # # for NIH - R01 grant, October 2017.
E = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=True, use_days='acclimated')
# HFD2_some_features_stats_R01.bw_and_bw_gain_t_test(E)
# HFD2_some_features_stats_R01.intake_and_distance(E)
# HFD2_some_features_stats_R01.intake_DC_LC(E)

# HFD2_more_features_stats_R01.two_way_anova_repeated_bodyweight(E)
# HFD2_more_features_stats_R01.two_way_anova_repeated_features(E)
HFD2_more_features_stats_R01.two_way_anova_repeated_dc_lc(E)

# E_chow = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=True, use_days='chow')
# E_hf = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=True, use_days='HiFat')
# HFD2_features_correlation_R01.some_correlations(E_chow, E_hf)


# look at features around transition days
# E = HiFat2Experiment.HiFat2Experiment(use_days='chow_to_HF_and_baseline')
# features_panel_days.plot_features_transition_days(E)

################## to be updated
# # feature vs experimental days
# E = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=True, use_days='all')
# bin_type = '24HDCLC'
# level = 'mouse'
# features_panel_expdays.plot_features_panel_expdays(E, bin_type, level, 
#                               COMMON_Y=False, plotType='lines')

# from ceppa.visualizations import diet_transition
# E = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=True, use_days='diet_baseline')
# bin_type = '12bins'
# level = 'strain'
# diet_stabilization.plot_stabilization_days(
#                     E, bin_type, level, COMMON_Y=True, plotType='markers')
################## END to be updated


# # bout features per AS
# E = HiFat2Experiment.HiFat2Experiment(use_days='chow_to_HF')

# features = E.features_by_type['bouts'][12:]
# for feature in features:
#     E.generate_bout_feature_vectors_per_AS(feature, GENERATE=True, VERBOSE=True)

# # # to be completed
# from ceppa.visualizations import features_panel_AS
# features_panel_AS.plot_features_panel_AS(E, level='strain', err_type='stdev')
# # # 



# # 5. BREAKFAST
# E = HiFat2Experiment.HiFat2Experiment(IGNORE_MD=False, use_days='all')
# # # generate
# for cycle in E.cycles:
#     for act in ['F', 'W']:
#         E.generate_breakfast_data(act=act, ONSET=True, cycle=cycle, GENERATE=True)


# # figures
# E = HiFat2Experiment.HiFat2Experiment(use_days='chow') 
# E = HiFat2Experiment.HiFat2Experiment(use_days='HiFat')
# E = HiFat2Experiment.HiFat2Experiment(use_days='transition')
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
#     E, level='strain', err_type='stderr', ONSET=True)  



# # # 6. WITHIN AS
# for cycle in E.cycles:
# within_AS_structure.plot_within_AS_structure(E, level='strain', cycle='LC')




# # 7. TIME BUDGETS
# E = HiFat2Experiment.HiFat2Experiment() 
# for cycle in E.cycles:
#     # E.generate_time_budgets(cycle=cycle, AS=False, GENERATE=True, VERBOSE=True)
#     time_budgets.plot_time_budgets(E, level='strain', cycle=cycle)



# figure for grant app
# from ceppa.visualizations import breakfast_fig1_HFD2, breakfast_fig2_HFD2, time_budgets_fig_HFD2
# E = HiFat2Experiment.HiFat2Experiment(use_days='all') 
# # breakfast_fig1_HFD2.plot_figure1(E)
# # breakfast_fig2_HFD2.plot_figure2(E)
# time_budgets_fig_HFD2.plot_figure(E)



# # 8. DIET TRANSITION
# E = HiFat2Experiment.HiFat2Experiment(use_days='chow_to_HF')
# for num_AS in [3, 5, 10]:
#     diet_chow_to_HF_transition.plot_first_ASs(E, level='strain', num_AS=num_AS, num_mins=15)






cstop = time.clock()
print "\n--> main script ran in %1.2f minutes\n" %((cstop-cstart) / 60.)

