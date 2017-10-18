import numpy as np
import matplotlib as mpl
import time, datetime

from ceppa import FluoxetineExperiment 
from ceppa.visualizations import position_density 
from ceppa.visualizations import rasters, raster_mouseday
from ceppa.visualizations import features_panel_CT, ingestion#, features_panel_expdays, features_distribution
# from ceppa.visualizations import time_budgets, breakfast#, breakfast_cycles, within_AS_structure, 
from ceppa.util import my_utils

"""
G.Onnis, 07.2017

Tecott Lab UCSF
"""


np.set_printoptions(linewidth=250, precision=5, threshold=8000, suppress=True)
mpl.rc('font', family='sans-serif') 
# mpl.rc('text', usetex=True)

cstart = time.clock()
tstart = datetime.datetime.now()



# E = FluoxetineExperiment.FluoxetineExperiment(
#                             IGNORE_MD=False,
#                             use_days='acclimated')



# # 0. BINARY FILES
# E.get_exp_info()

# generate binary files from HCM raw data
# E.generate_binaries()

# # 1. BOUTS 
# E.generate_bouts()

# # 2. ACTIVE STATES
# E.generate_active_states()

# # 3. POSITION DENSITY, IS cycle    
# for xbins, ybins in E.xy_bins:
    # for cycle in E.all_cycles:
        # E.generate_position_density(cycle=cycle, xbins=xbins, ybins=ybins, GENERATE=True)
    # E.check_position_bin_times(xbins=xbins, ybins=ybins, GENERATE=False)

# # 4. FEATURES
# keyList = ['active_states', 'totals', 'AS_intensities', 'bouts']
# features = E.features_by_type['active_states'] + E.features_by_type['totals'] + E.features_by_type['AS_intensities'] 
# features = E.features_by_type['bouts'][10:]
# # # features = ['MASInt']
# # # # generate
# for vec_type in vec_types:
#     for feature in features:
#         E.generate_feature_vectors(feature, vec_type=vec_type, GENERATE=True, VERBOSE=True)

# # 5. BREAKFAST
# E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days='pre-FLX')
# E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days='post-FLX')
# # # generate
# for cycle in E.cycles:
#     for act in ['F', 'W']:
#         E.generate_breakfast_data(act=act, ONSET=True, cycle=cycle, GENERATE=True)




# # FIGURES

# # 1. POSITION DENSITY
# use_days = ['pre-FLX', 'post-FLX', 'post-FLX_first_4', 'post-FLX_last_4', 'acclimated']
# for use_d in use_days[:-1]:
#     E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days=use_d)      
#     for xbins, ybins in E.xy_bins[1:]:
#         for cycle in E.all_cycles:
#             for level in E.levels[:2]:
#                 position_density.plot_position_density(E, cycle=cycle, 
#                                     level=level, xbins=xbins, ybins=ybins)   


# E0 = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days=use_days[2])
# E1 = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days=use_days[3])      
# for xbins, ybins in E0.xy_bins[:1]:
#     for cycle in E0.all_cycles:
#         for level in E0.levels:  
#             position_density.write_to_csv1(E0, E1, cycle, level, xbins, ybins)
            
# # 2. RASTERS
# recording/maintenance time
# use_days = ['pre-FLX', 'post-FLX', 'acclimated']
# for use_d in use_days:
#     E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days=use_d)
#     for ttype in ['recording', 'maintenance']:
#         rasters.plot_HCM_system_time(E, ttype)

E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days='pre-FLX')
# E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days='post-FLX')

# individuals
# rasters.plot_rasters_mice(E, group=0, SHOW_DAYS=True)             
# rasters.plot_rasters_mice(E, group=1, SHOW_DAYS=True)
# rasters.plot_rasters_mice(E, group=2, SHOW_DAYS=True)             
# # rasters.plot_rasters_mice(E, group=None, mouseNumber=701)

# # # groups
# rasters.plot_raster_groups(E, group_list=[0, 1, 2], SHOW_DAYS=True)           

# # # mousedays
# for group in E.groups:
#     for mouse in group.individuals:
#         for MD in mouse.mouse_days:
#             if MD.dayNumber in E.daysToUse:
#                 # if MD.dayNumber in [12, 13]:
#                 raster_mouseday.plot_raster_mouseday(
#                             E, mouse.mouseNumber, MD.dayNumber)




# # # 3. FEATURES
# for IGNORE_MD in [True, False]:
IGNORE_MD = True
# E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=IGNORE_MD, use_days='pre-FLX')
# E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=IGNORE_MD, use_days='post-FLX')

# panel_CT
for bin_type in E.bin_types:
    for level in E.levels:
        for COMMON_Y in [False, True]:
            for err_type in E.err_types:
                features_panel_CT.plot_features_panel(E, level, bin_type, err_type=err_type, COMMON_Y=COMMON_Y)


# # panel csv
# use_days = ['pre-FLX', 'post-FLX']
# for use_d in use_days:
#     E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days=use_d)
#     for vec_type in vec_types:
#         for level in levels:
#             features_panel_CT.write_panel_to_csv(E, level, vec_type)
#             features_panel_CT.write_feature_vectors_to_csv(E, level, vec_type)
#             features_panel_CT.write_feature_vector_mouse_avgs_12bins_to_csv(E)  


# larry funky csv: mouse, bin x 24 features
# use_days = ['pre-FLX', 'post-FLX']
# for use_d in use_days:
#     E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days=use_d)
#     features_panel_CT.write_feature_vector_mouse_avgs_12bins_to_csv(E)




# # 4. TIME BUDGETS
# E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days='pre-FLX')
# E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days='post-FLX')
# for cycle in E.cycles:
#     # E.generate_time_budgets(cycle=cycle, AS=False, GENERATE=True, VERBOSE=True)
#     time_budgets.plot_time_budgets(E, level='group', cycle=cycle)

# time_budgets.write_data_to_csv(E)


# # 5. BREAKFAST
# E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days='pre-FLX')
# # E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days='post-FLX')

# breakfast.plot_breakfast(E, cycle='24H', level='group', err_type='sd', ONSET=True, num_mins=15)

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

cstop = time.clock()
tstop = datetime.datetime.now()

print "\n--> main script ran in %1.2f minutes" %((cstop-cstart) / 60.)
print "started: ", tstart
print "ended:", tstop
print


