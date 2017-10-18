import numpy as np
import matplotlib as mpl
import time, datetime

from ceppa import TwoCFastExperiment 
from ceppa.visualizations import position_density_QC 
from ceppa.visualizations import rasters, raster_mouseday
from ceppa.visualizations import features_panel_CT, features_panel_expdays, features_activity_panel_CT
# from ceppa.visualizations import ingestion, features_distribution
# from ceppa.visualizations import breakfast, breakfast_cycles, within_AS_structure, time_budgets


"""
G.Onnis, 06.2017

Tecott Lab UCSF
"""


np.set_printoptions(linewidth=250, precision=5, threshold=8000, suppress=True)
mpl.rc('font', family='sans-serif') 
# mpl.rc('text', usetex=True)

cstart = time.clock()
tstart = datetime.datetime.now()


use_days = ['chow', 'fast', 'refeed', 'pre_fast', 'after_fast', 'transition']

# E = TwoCFastExperiment.TwoCFastExperiment(
#                             IGNORE_MD=False, 
#                             BIN_SHIFT=True, 
#                             use_days='acclimated')



# # 0. BINARY FILES
# generate binary files from HCM raw data
# E.generate_binaries()

# # 1. BOUTS 
# E.generate_bouts()

# # 2. ACTIVE STATES
# E.generate_active_states() 

# # 3. POSITION DENSITY, IS cycle    
# for xbins, ybins in xy_bins:
#     E.generate_position_density(cycle='IS', xbins=xbins, ybins=ybins, GENERATE=True)

# # 4. FEATURES
# keyList = ['active_states', 'totals', 'AS_intensities', 'bouts']
# features = E.features_by_type['bouts'][10:]
# # features = ['MASInt']
# # # # # # # generate
# for bin_type in E.bin_types[1:2]:
#     for feature in features:
#         E.generate_feature_vectors(feature, bin_type=bin_type, GENERATE=True, VERBOSE=True)




# # FIGURES

# 1. POSITION DENSITY
# for use_d in use_days[:1]:
#     E = TwoCFastExperiment.TwoCFastExperiment(IGNORE_MD=False, use_days=use_d)      
#     for xbins, ybins in E.xy_bins:
#         for cycle in ['24H', 'IS']:
#             for level in E.levels:
#                 position_density_QC.plot_position_density(E, cycle=cycle, 
#                                     level=level, xbins=xbins, ybins=ybins)   


# # 2. RASTERS
# E = TwoCFastExperiment.TwoCFastExperiment(
#                 IGNORE_MD=True, BIN_SHIFT=False, use_days='transition')

# # # # # mousedays
# for group in E.groups[1:]:
#     for mouse in group.individuals[4:5]:
#         for MD in mouse.mouse_days:
#             if MD.dayNumber in E.daysToUse[-3:]:
#                 # if MD.dayNumber in [12, 13]:
#                 for bin_type in ['12bins', '24bins'][:1]:
#                     raster_mouseday.plot_raster_mouseday(
#                             E, mouse.mouseNumber, MD.dayNumber, 
#                             bin_type=bin_type)


# # individuals
# rasters.plot_rasters_mice(E, group=0, SHOW_DAYS=True)
# rasters.plot_rasters_mice(E, group=1, SHOW_DAYS=True)
# rasters.plot_rasters_mice(E, group=None, mouseNumber=7233)

# # # groups
# rasters.plot_raster_groups(E, group_list=[1], SHOW_DAYS=True)           # THIS 0 1

# recording/maintenance time
# for ttype in ['recording', 'maintenance']:
#     rasters.plot_HCM_system_time(E, ttype)



# # # 3. FEATURES

for use_d in use_days[1:]:
    E = TwoCFastExperiment.TwoCFastExperiment(
                            IGNORE_MD=True, 
                            BIN_SHIFT=True, 
                            use_days=use_d)

    # # # panel_CT
    for bin_type in E.bin_types[:3]:
        for level in E.levels[:1]:
            for err_type in E.err_types:
                features_panel_CT.plot_features_panel(E, level, bin_type, err_type)


# E = TwoCFastExperiment.TwoCFastExperiment(
#                                     IGNORE_MD=True, 
#                                     BIN_SHIFT=True,
#                                     use_days='acclimated'
#                                     )
    # features_panel_expdays.plot_features_panel_12bins(E)
    # features_panel_expdays.plot_features_panel_24H(E)
    # features_panel_expdays.plot_features_panel_DC_LC(E)

# E = TwoCFastExperiment.TwoCFastExperiment(
#                                     IGNORE_MD=True, 
#                                     BIN_SHIFT=True,
#                                     use_days='transition'
#                                     )
# features_activity_panel_CT.plot_features_activity_panel(E, 
#                                     level='group', 
#                                     act = 'W ',
#                                     bin_type='12bins', 
#                                     err_type='sem')

# # # INGESTION
# ingestion.plot_coefficients(E, act='F')





cstop = time.clock()
tstop = datetime.datetime.now()

print "\n--> main script ran in %1.2f minutes" %((cstop-cstart) / 60.)
print "started:", tstart
print "ended:", tstop
print
