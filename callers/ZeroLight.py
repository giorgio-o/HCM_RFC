import numpy as np
import matplotlib as mpl
import time, datetime

from ceppa import ZeroLightExperiment 
from ceppa.visualizations import position_density_QC, position_density 
from ceppa.visualizations import rasters, raster_mouseday
from ceppa.visualizations import features_panel_CT, ingestion
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


use_days = ['white+red_light', 'available_red_light', 'available_white_and_red_light']
# use_days = ['red_light_initial_4', 'red_light_final_4', 'red_light_initial_4_final_4']#, 'acclimated']


E = ZeroLightExperiment.ZeroLightExperiment(
                            IGNORE_MD=False,
                            use_days=use_days[2])  



# # 0. BINARY FILES
# E.get_exp_info()

# generate binary files from HCM raw data
# E.generate_binaries()

# # 1. BOUTS 
# E.generate_bouts()

# # 2. ACTIVE STATES
# E.generate_active_states()

# 3. POSITION DENSITY   
# for xbins, ybins in E.xy_bins[:1]:
#     for cycle in E.all_cycles:
#         E.generate_position_density(cycle=cycle, tbin_type=None, 
#                                         xbins=xbins, ybins=ybins, GENERATE=True)
    # for tbin_type in ['12bins', 'AS12bins']:
    #     E.generate_position_density(cycle=None, tbin_type=tbin_type, 
    #                                     xbins=xbins, ybins=ybins, GENERATE=True)

    # E.check_position_bin_times(xbins=xbins, ybins=ybins, tbin_type='12bins')

# 4. FEATURES
# keyList = ['active_states', 'totals', 'AS_intensities', 'bouts']
# features = E.features_by_type['active_states'] + E.features_by_type['totals'] + E.features_by_type['AS_intensities'] 
# features = E.features_by_type['bouts'][10:]
# # # # # features = ['MASInt']

# for bin_type in E.bin_types[1:2]:
#     for feature in features:
#         E.generate_feature_vectors(feature, bin_type=bin_type, GENERATE=True, VERBOSE=True)




# # FIGURES

# use_days = ['white+red_light', 'available_red_light', 'available_white_and_red_light']

# E = ZeroLightExperiment.ZeroLightExperiment(IGNORE_MD=False, use_days=use_days[2])

# # # # 1. POSITION DENSITY
# # QUALITY CONTROL
# for use_d in use_days:
#     E = ZeroLightExperiment.ZeroLightExperiment(IGNORE_MD=False, use_days=use_d)

# for xbins, ybins in E.xy_bins[:1]:
#     for level in E.levels[2:]:
#         # # all cycles
#         # for cycle in E.all_cycles:
#         #     position_density_QC.plot_position_density(E, cycle=cycle, tbin_type=None,
#         #                         level=level, xbins=xbins, ybins=ybins)   

#         # # 12 bins
#         for tbin_type in ['12bins', 'AS12bins'][:1]:
#             position_density_QC.plot_position_density(E, cycle=None, tbin_type=tbin_type, 
#                                 level=level, xbins=xbins, ybins=ybins)

# # csv files
# for use_d in use_days:
#     E = ZeroLightExperiment.ZeroLightExperiment(IGNORE_MD=False, use_days=use_d)    

#     for xbins, ybins in E.xy_bins:
#         for level in E.levels:  
#             # all cycles
#             for cycle in E.all_cycles:
#                 position_density_QC.write_to_csv(E, cycle=cycle, tbin_type=None, 
#                                     level=level, xbins=xbins, ybins=ybins) 
#             # # 12 bins
#             for AS_FLAG in [True, False]:
#                 position_density_QC.write_to_csv(E, cycle=None, tbin_type='12bins', 
#                                         AS_FLAG=AS_FLAG, level=level, xbins=xbins, ybins=ybins)

# # panels
# E = ZeroLightExperiment.ZeroLightExperiment(IGNORE_MD=False, use_days=use_days[2])
# for xbins, ybins in E.xy_bins[:1]:
#     position_density.plot_position_density_panel1(E, cycle=None, tbin_type='12bins',
#                         xbins=xbins, ybins=ybins)
    # position_density.plot_position_density_panel2(E, cycle=None, tbin_type='12bins',
    #                     xbins=xbins, ybins=ybins)



# # 2. RASTERS
# recording/maintenance time
# for ttype in ['recording', 'maintenance']:
#     rasters.plot_HCM_system_time(E, ttype)

# individuals
# rasters.plot_rasters_mice(E, group=0, SHOW_DAYS=True)                
# # rasters.plot_rasters_mice(E, group=None, mouseNumber=701)

# # # groups
# rasters.plot_raster_groups(E, group_list=[0], SHOW_DAYS=True)           

# # mousedays
# for group in E.groups:
#     for mouse in group.individuals:
#         for MD in mouse.mouse_days:
#             if MD.dayNumber in E.daysToUse:
#                 raster_mouseday.plot_raster_mouseday(
#                             E, mouse.mouseNumber, MD.dayNumber)




# # # 3. FEATURES
# panel_CT
# for bin_type in E.bin_types[1:2]:
#     for level in E.levels:
#         for COMMON_Y in [False, True][:1]:
#             for err_type in E.err_types[:1]:
#                 features_panel_CT.plot_features_panel(E, level, bin_type, err_type=err_type, COMMON_Y=COMMON_Y)


# # panel csv
# use_days = ['pre-FLX', 'post-FLX']
# for use_d in use_days:
#     E = FluoxetineExperiment.FluoxetineExperiment(IGNORE_MD=True, use_days=use_d)
#     for vec_type in vec_types:
#         for level in levels:
#             features_panel_CT.write_panel_to_csv(E, level, vec_type)
#             features_panel_CT.write_feature_vectors_to_csv(E, level, vec_type)
#             features_panel_CT.write_feature_vector_mouse_avgs_12bins_to_csv(E)  


# # # INGESTION
# ingestion.plot_coefficients(E, act='F')
# ingestion.check_ZeroLightExp_FC(E)


cstop = time.clock()
tstop = datetime.datetime.now()

print "\n--> main script ran in %1.2f minutes" %((cstop-cstart) / 60.)
print "started: ", tstart
print "ended:  ", tstop
print


