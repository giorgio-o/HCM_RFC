import numpy as np
import sys
import os
import time

# A lot of the methods of this class are defined in other files and then monkey=patched onto this class:
from ceppa.util.darren import loadOriginalDataMethodDefinition, trajectoryFixingMethodsDefinitions, register_mice
from ceppa.util.MD_methods import devicesAndPlatformErrorCheck, homebase, raw_binary_methods
from ceppa.util.MD_methods import md_generation_funcs
from ceppa.util.MD_methods import bout_methods, active_state_methods, md_data_correction, event_methods, total_methods
from ceppa.util.MD_methods import breakfast_methods, time_budget_methods

from ceppa.util import my_utils
from ceppa.util.intervals import Intervals
from ceppa.util.cage import Cage   


"""
D. Rhea, 2013
G.Onnis, rebuilt: 01.2017
        updated: 06.2017

Tecott Lab UCSF
"""


class MouseDay(object):
    """
    Eventually this is to become the modern mouseDay.
    Note how short this class definition is (seems?) due to monkey-patching on method defs that are defined elsewhere.
    """
    def __init__(self):
        pass
    
    def shortDescriptionString(self):
        return "group=%s, dayNumber=%d, individual=%d"%(self.group.name, self.dayNumber, self.individualNumber)
    
    def __str__(self):
        s=''
        if hasattr(self, 'experiment'):
            if hasattr(self.experiment, 'experiment'):
                s += self.experiment.name+', '
        if hasattr(self,'group'):
            s += "group=%d:%s, "%(self.group.number, self.group.name)
        if hasattr(self, 'roundNumber'):
            s += "roundNumber=%d, "%(self.roundNumber)
        s += "individual=%d, mouseNumber=%d, dayNumber=%d, "%(self.individualNumber, self.mouseNumber, self.dayNumber)
        return s

    def get_id_string(self):
        self.id_string = "group%d_individual%d_day%d.npy" %(
            self.groupNumber, self.individualNumber, self.dayNumber) 
        return self.id_string


    # load methods
    def load(self, varName): 
        HCM_variables = self.experiment.HCM_variables
        HCM_derived = self.experiment.HCM_derived

        self.id_string = "group%d_individual%d_day%d.npy" %(
            self.groupNumber, self.individualNumber, self.dayNumber)

        if varName in HCM_variables['txy_data']:
            fname = self.experiment.HCM_data_dir + 'txy_data/%s/%s' %(varName, self.id_string)
            var =  np.load(fname)
        
        elif varName in HCM_variables['timeSets']:
            fname = self.experiment.HCM_data_dir + 'timeSets/%s/%s' %(varName, self.id_string)
            var =  np.load(fname)

        elif varName in HCM_variables['idxs']:
            fname = self.experiment.HCM_data_dir + 'idxs/%s/%s' %(varName, self.id_string)
            var =  np.load(fname)

        elif varName in HCM_variables['homebase']:
            fname = self.experiment.HCM_data_dir + 'homebase/%s/%s' %(varName, self.id_string)
            var =  np.load(fname)

        elif varName in HCM_variables['qc']:
            fname = self.experiment.HCM_data_dir + 'qc/%s/%s' %(varName, self.id_string)
            var =  np.load(fname)

        elif varName in HCM_variables['to_compute']:
            if varName == 'at_HB_timeSet':
                var = self.get_at_device_Set('HB')
            else:
                T = self.load('CT')
                idx =  self.load('idx_at_HB')
                if varName == 'idx_out_HB':
                    var = -idx
                elif varName == 'CT_at_HB':
                    var = T[idx]
                elif varName == 'CT_out_HB':
                    var = T[-idx]
                elif varName == 'AS_idx':
                    var = self.get_AS_idx()

        # derived   
        elif varName in HCM_derived['position_data']:# or varName in vars_dict['devices']:
            split_list = varName.split('_') 
            bt = split_list[0]
            text = split_list[2]
            xbins = ''.join([s for s in split_list[3] if s.isdigit()])
            ybins = ''.join([s for s in split_list[4] if s.isdigit()])
            fname = self.experiment.derived_dir + \
                        'position_data/xbins%s_ybins%s/%s/bin_times/%s' %(
                                            xbins, ybins, text, self.id_string) 
            var =  np.load(fname)

        elif varName in HCM_derived['events']['ingestion']['coeffs']:
            act = 'F' if varName[0] == 'F' else 'W'
            var = self.get_ingestion_coefficients(act, qty='coeffs')

        elif varName in HCM_derived['events']['ingestion']['tots']:
            act = varName[0]
            var = self.get_ingestion_coefficients(act, qty='tots')
        
        elif varName in HCM_derived['events']['ingestion']['durs']:
            act = varName[0]
            var = self.get_ingestion_coefficients(act, qty='durs')


        elif varName in HCM_derived['events']['M']:
            fname = self.experiment.events_dir + 'M/%s/%s' %(varName, self.id_string)
            var =  np.load(fname)

        elif varName in HCM_derived['bouts']:
            act = varName[0]
            dirname = getattr(self.experiment, '%s_bouts_dir' %act)
            fname = dirname + '%sB_timeSet/%s' %(act, self.id_string)
            if varName == 'MB_idx':             
                fname = dirname + 'MB_idx/%s' %self.id_string
            var = np.load(fname)

        elif varName in HCM_derived['active_states']:
            if varName == 'IS_timeSet':    # not directly stored, so have to calculate.
                for var in ['AS_timeSet', 'recording_start_stop_time']:
                    self.load(var)
                var = Intervals(self.AS_timeSet).complement().intersect(
                    Intervals(self.recording_start_stop_time)).intervals
            else:
                var = np.load(self.experiment.active_states_dir + 'AS_timeSet/%s' %self.id_string)
            
        setattr(self, varName, var)
        return var


    def load_feature_vector(self, feature='ASP', bin_type='12bins'): 
        E = self.experiment
        self.get_id_string()
        string = '_shifted%+02dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
        dirname = E.features_dir + 'vectors_CT/%s/%s%s/' %(feature, bin_type, string)
        
        if feature in E.features:
            fname = dirname +  self.id_string
        else:
            sys.exit(-1)
        var = np.load(fname)
        return var


    # def load_bout_feature_per_AS_vector(self, feat):
    #     self.get_id_string()
    #     if feat in self.experiment.features:
    #         var = np.load(self.experiment.features_dir + 'vectors_AS/%s/%s' %(feat, self.id_string))
    #     return var


    # def load_feature_array(self, feat):
    #     self.get_id_string()
    #     if feat in self.experiment.features:
    #         var = np.load(self.experiment.features_dir + 'arrays/%s/%s' %(feat, self.id_string))
    #     return list(var)


    def get_figtitle(self):
        fig_title = '%sExp\ngroup%d: %s, M%d, D%d' %(
                        self.experiment.short_name, 
                        self.groupNumber, self.experiment.strain_names[self.groupNumber], 
                        self.mouseNumber, self.dayNumber)
        return fig_title



# monkey-patching on methods
# core Darren stuff
MouseDay.loadOriginalData = loadOriginalDataMethodDefinition.loadOriginalData 
MouseDay.backwardFix = trajectoryFixingMethodsDefinitions.backwardFix 
MouseDay.forwardFix = trajectoryFixingMethodsDefinitions.forwardFix 
MouseDay.deviceFix = trajectoryFixingMethodsDefinitions.deviceFix 

MouseDay.register_with_mouse = register_mice.register_with_mouse
MouseDay.add_stuff_to_mouse_day = register_mice.add_stuff_to_mouse_day
# MouseDay.calculateBinnedData = calculateBinnedDataMethodDefinition.calculateBinnedData # monkey-patching on a method
# MouseDay.calculateBouts = calculateBoutsMethodDefinition.calculateBouts # monkey-patching on a method
# MouseDay.calculateEntropyMeasures = calculateBinnedDataMethodDefinition.calculateLocomotorEntropy # ...

# added methods
# data checks
MouseDay.get_corrected_ingestion_Set = devicesAndPlatformErrorCheck.get_corrected_ingestion_Set
MouseDay.check_ingestion_devices_overlap = devicesAndPlatformErrorCheck.check_ingestion_devices_overlap
MouseDay.flag_errors = devicesAndPlatformErrorCheck.flag_errors
MouseDay.check_platform_errors = devicesAndPlatformErrorCheck.check_platform_errors
MouseDay.check_device_errors = devicesAndPlatformErrorCheck.check_device_errors
# homebase
MouseDay.designate_homebase = homebase.designate_homebase
MouseDay.index_coordinates_at_homebase = homebase.index_coordinates_at_homebase
MouseDay.map_xbins_ybins_to_cage = homebase.map_xbins_ybins_to_cage
MouseDay.map_obs_rectangle_to_cage = homebase.map_obs_rectangle_to_cage
MouseDay.max_domino = homebase.max_domino
MouseDay.get_cage_cell_id = homebase.get_cage_cell_id
# raw binary stuff
MouseDay.get_ingestion_uncorrected_events = raw_binary_methods.get_ingestion_uncorrected_events
MouseDay.index_coordinates_at_devices = raw_binary_methods.index_coordinates_at_devices
MouseDay.get_at_device_Set = raw_binary_methods.get_at_device_Set
MouseDay.get_position_bin_times = raw_binary_methods.get_position_bin_times


# data generating functions
MouseDay.generate_binaries = md_generation_funcs.generate_binaries
MouseDay.generate_position_bin_times = md_generation_funcs.generate_position_bin_times
MouseDay.check_position_bin_times = md_generation_funcs.check_position_bin_times
MouseDay.generate_bouts = md_generation_funcs.generate_bouts
MouseDay.generate_active_states = md_generation_funcs.generate_active_states
MouseDay.generate_feature_vector = md_generation_funcs.generate_feature_vector
MouseDay.generate_bout_feature_vector_per_AS = md_generation_funcs.generate_bout_feature_vector_per_AS
# MouseDay.generate_feature_array = md_generation_funcs.generate_feature_array
# MouseDay._check_bout_counts_in_bins = md_generation_funcs._check_bout_counts_in_bins
MouseDay.generate_breakfast_data = md_generation_funcs.generate_breakfast_data
MouseDay.generate_time_budgets = md_generation_funcs.generate_time_budgets


# bouts
MouseDay.get_ingestion_bouts = bout_methods.get_ingestion_bouts
MouseDay.check_ingestion_bouts = bout_methods.check_ingestion_bouts
MouseDay.index_ingestion_bout_and_homebase_coordinates = bout_methods.index_ingestion_bout_and_homebase_coordinates
MouseDay.get_move_bouts = bout_methods.get_move_bouts
MouseDay.get_bout_vector = bout_methods.get_bout_vector
MouseDay.get_bout_feature_value = bout_methods.get_bout_feature_value
MouseDay.get_bout_feature_value_per_AS = bout_methods.get_bout_feature_value_per_AS
MouseDay.get_bout_vector_per_AS = bout_methods.get_bout_vector_per_AS
MouseDay.get_bout_array = bout_methods.get_bout_array

# active states
MouseDay.get_AS_in_cycle = active_state_methods.get_AS_in_cycle
MouseDay.get_AS_idx = active_state_methods.get_AS_idx
MouseDay.get_AS_feature_value = active_state_methods.get_AS_feature_value
MouseDay.get_AS_vector = active_state_methods.get_AS_vector
MouseDay.get_AS_intensity_vector = active_state_methods.get_AS_intensity_vector
# MouseDay.get_AS_array = active_state_methods.get_AS_array
# MouseDay.get_AS_intensity_array = active_state_methods.get_AS_intensity_array

# data correction
MouseDay.correct_AS_without_move = md_data_correction.correct_AS_without_move
MouseDay.correct_bouts_intersecting_bin = md_data_correction.correct_bouts_intersecting_bin

# totals
MouseDay.get_total_vector = total_methods.get_total_vector
MouseDay.get_total_array = total_methods.get_total_array

# events
MouseDay.get_ingestion_coefficients = event_methods.get_ingestion_coefficients
MouseDay.get_device_firing_durations_in_AS_or_Bouts = event_methods.get_device_firing_durations_in_AS_or_Bouts
MouseDay.get_device_firing_durations = event_methods.get_device_firing_durations
MouseDay.get_amounts = event_methods.get_amounts
MouseDay.get_CT_idx_in_tbin = event_methods.get_CT_idx_in_tbin
MouseDay.get_move_idx = event_methods.get_move_idx
MouseDay.get_move_distances = event_methods.get_move_distances
MouseDay.get_move_distances_in_AS_or_Bout = event_methods.get_move_distances_in_AS_or_Bout
# MouseDay.get_move_speeds = event_methods.get_move_speeds
MouseDay.get_move_events = event_methods.get_move_events
MouseDay.get_trajectory_angles = event_methods.get_trajectory_angles

# MouseDay.get_event_vectors = event_methods.get_event_vectors


# breakfast
MouseDay.get_breakfast_probability = breakfast_methods.get_breakfast_probability
MouseDay.get_bin_counts_within_AS = breakfast_methods.get_bin_counts_within_AS

# time budgets
MouseDay.get_time_budgets = time_budget_methods.get_time_budgets



