import numpy as np
import os
import sys
import time
import pickle

from ceppa.util import my_utils
from ceppa.util.intervals import Intervals
"""
G.Onnis, 01.2017
    updated, 06.2017

Mouseday Class methods for generating all sorts of data

Tecott Lab UCSF
"""



def check_position_bin_times(self, xbins=12, ybins=24, tbin_type=None):
    stop
    text = my_utils.get_text(tbin_type=tbin_type)
    
    if tbin_type.endswith('bins'):

        

        data = self.generate_position_bin_times(tbin_type=tbin_type, xbins=xbins, ybins=ybins) 
        
        if not AS_FLAG:
        
            data_ = self.generate_position_bin_times(
                                cycle='24H', xbins=xbins, ybins=ybins)
            
            # tolerance: /num_seconds, /1000 tolerates the 1000secs~=10mins
            np.testing.assert_array_almost_equal(data.sum(0)/10000., data_/10000., 
                            decimal=0, err_msg='24H != sum over %s' %tbin_type)

        else:
            data_ = self.generate_position_bin_times(
                                cycle='AS24H', xbins=xbins, ybins=ybins)
            # tolerance: /num_seconds, /1000 tolerates the 1000secs~=10mins
            np.testing.assert_array_almost_equal(data.sum(0)/1000., data_/1000., 
                            decimal=0, err_msg='AS24H != sum over %s' %tbin_type)

    else:
        cycles = self.experiment.all_cycles
        data = np.zeros((len(cycles), ybins, xbins))
        c = 0
        for cycle in cycles:
            data[c] = self.generate_position_bin_times(cycle=cycle, xbins=xbins, ybins=ybins)
            c +=1

        h24, IS, dc, lc, as24, asdc, aslc = data
        
        # tolerance: /num_seconds, /1000 tolerates the 1000secs~=10mins
        np.testing.assert_array_almost_equal(h24/10000., (dc+lc)/10000., decimal=0, 
                                                err_msg='24H != DC+LC')
        np.testing.assert_array_almost_equal(h24, IS+as24, decimal=0, 
                                                err_msg='24H != IS+AS')
        np.testing.assert_array_almost_equal(as24/1000., (asdc+aslc)/1000., decimal=0, 
                                                err_msg='AS24 != ASDC+ASLC')
        
    print "%s : POSITION DENSITY CHECKS, %s, xbins:%s, ybins:%d -> OK" %(
            self, text, xbins, ybins)


def generate_position_bin_times(self, cycle=None, tbin_type=None, xbins=12, 
        ybins=24, GENERATE=False):
    """ returns total time in cage divided into xbins, ybins
    """
    name = 'bin_times_xbins%d_ybins%d' %(xbins, ybins)
    
    text = my_utils.get_text(cycle, tbin_type)

    varName = 'bin_times_%s_xbins%d_ybins%d' %(text, xbins, ybins)

    dirname = self.experiment.derived_dir + \
                    'position_data/xbins%d_ybins%d/%s/bin_times/' %(
                            xbins, ybins, text)   
    if not os.path.isdir(dirname): os.makedirs(dirname)  

    if GENERATE:
        bin_times = self.get_position_bin_times(cycle, tbin_type, xbins, ybins)  
        np.save(dirname + self.id_string, bin_times)

    else:    
        try:   
            bin_times = self.load(varName)
            # print bin_times
        except IOError: 
            bin_times = self.get_position_bin_times(cycle, tbin_type, xbins, ybins)   
            np.save(dirname + self.id_string, bin_times)

    setattr(self, varName, bin_times)
    
    return bin_times


def generate_binaries(self):
    """
    """
    cstart = time.clock()
    self.ignored = False
    self.id_string = "group%d_individual%d_day%d.npy" %(
        self.groupNumber, self.individualNumber, self.dayNumber)
    print "Precomputing platform and devices data for:"
    print "Exp: %s, %s" %(self.experiment.short_name, self)
    
    # loading and fixes.
    # monkey-patched from other util
    self.loadOriginalData() # Step 1, load it
    self.deviceFix() # Step 2, fix it both like this
    self.backwardFix() # and like this  

    print "computing binary data from devices.." 
    # ingestion data
    for act in ['F', 'W']:
        # get uncorrected time intervals (Sets) of events
        self.get_ingestion_uncorrected_events(act)    
        # get index at device cells
        self.index_coordinates_at_devices(act)        
        # get time intervals at device Cells
        self.get_at_device_Set(act)                   
        # check device consistency with position data, get corrected time intervals
        # imported from module devicesAndPlatformErrorCheck 
        self.get_corrected_ingestion_Set(act)

    # check for position overlap at both devices
    # imported from module devicesAndPlatformErrorCheck
    self.check_ingestion_devices_overlap()             
    # get position bin times for: (2,4) HB designation, (12, 24) platform error check
    # sets 'bin_times_24H_xbins%d_ybins%d' %(xbins, ybins)
    for (xbins, ybins) in [[12, 24], [2, 4]]:
        self.generate_position_bin_times(cycle='24H', xbins=xbins, ybins=ybins, GENERATE=True)       
        
    print "computing binary data from platform.."
    # # nest or homebase. single or domino, as list of tuples (ybins, xbins): (0, 0) top left. (3, 1) bottom right.  
    # imported from module homebase
    self.designate_homebase()               # sets 'rect_HB' 
    # breaks down in out_HB and at_HB          
    self.index_coordinates_at_homebase()    # sets 'idx_at_HB'
    self.get_at_device_Set(act='HB')        # gets timeset at HB

    # flag errors: sets 'flagged' and 'flagged_msgs'   
    self.flag_errors()  

    # save variables to npy
    d = self.experiment.HCM_variables
    HCM_variables = {i: d[i] for i in d if i!='to_compute'}
    for key, vals in HCM_variables.iteritems():
        for var in vals:
            dirname = self.experiment.HCM_data_dir + '%s/%s/' %(key, var)
            # if var.startswith('bin_times'):
            #     dirname = self.experiment.derived_dir + '%s/%s/24H/' %(key, var)
            if not os.path.isdir(dirname): os.makedirs(dirname)
            np.save(dirname + self.id_string , getattr(self, var))

    cstop = time.clock()
    print "->this mouseday took %1.3fs..\n" %(cstop-cstart)


def generate_bouts(self):
    """
    """
    cstart = time.clock()
    print self
    print "Exp: %s, %s, %s" %(
            self.experiment.short_name,
            self.generate_bouts.__name__, 
            self.experiment.hypar_text[12:])

    for act in ['F', 'W']:
        self.get_ingestion_bouts(act)

    self.check_ingestion_bouts()
    self.get_move_bouts()
    # save
    for act in ['F', 'W']:
        varName = '%sB_timeSet' %act
        dirname = getattr(self.experiment, '%s_bouts_dir' %act) + varName + '/'
        if not os.path.isdir(dirname): os.makedirs(dirname)
        np.save(dirname + self.id_string , getattr(self, varName))

    for varName in ['MB_timeSet', 'MB_idx']:
        dirname = self.experiment.M_bouts_dir + varName + '/'
        if not os.path.isdir(dirname): os.makedirs(dirname)    
        np.save(dirname + self.id_string, getattr(self, varName))

    cstop = time.clock()
    print "->this mouseday took %1.3fs..\n" %(cstop-cstart)


def generate_active_states(self, GENERATE=False):
    """ new definition, using bouts (Nov2016)
    """
    cstart = time.clock()
    print "Exp: %s, %s, %s" %(
        self.experiment.short_name, 
        self.generate_active_states.__name__, 
        self.experiment.hypar_text[:12])
    print self
    # load FWM bouts timeSet
    varNames = [var for var in self.experiment.HCM_derived['bouts'] if var != 'MB_idx']
    FB, WB, MB = [Intervals(self.load(var)) for var in varNames]
    # # from ethologic definition of AS, movements at homebase are part of inactive state.
    # # and must be removed: already done while generating Move Bouts
    B = FB + WB + MB
    num_bouts = B.intervals.shape[0]                    
    print "loaded %d bouts, F=%d, W=%d, M=%d" %(
        num_bouts, FB.intervals.shape[0], WB.intervals.shape[0], MB.intervals.shape[0])

    arr = B.connect_gaps(self.experiment.IST).intervals       # apply IST
    print "designated %d active states vs. %d FWM bouts, ratio: %1.2f" %(
        arr.shape[0], num_bouts, 1.*arr.shape[0] / num_bouts)
    
    # save variables to npy
    dirname = self.experiment.active_states_dir + 'AS_timeSet/'
    if not os.path.isdir(dirname): os.makedirs(dirname)
    np.save(dirname + self.id_string , arr)
    cstop = time.clock()
    print "->this mouseday took %1.3fs..\n" %(cstop-cstart)


def _check_bout_counts_in_bins(self, act):
    
    tbins = my_utils.get_CT_bins(bin_type='12bins')
    B = self.load('%sB_timeSet' %act)
    cnt_diff = np.zeros(len(tbins))
    b = 0
    for tbin in tbins:
        B_times, B_cnt_eff, B_times_eff, tbin_eff = my_utils.count_onsets_in_bin(I=B, tbin=tbin)
        B_cnt = B_times.shape[0]
        if B_cnt != B_cnt_eff:
            cnt_diff[b] = B_cnt - B_cnt_eff
        b +=1

    return cnt_diff


def generate_feature_vector(self, feature, bin_type='12bins', GENERATE=False, VERBOSE=False):
    """ 
    """
    if VERBOSE:
        # if not feature.startswith('MB'):
        print 'Exp: %s, %s, %s, %s, BIN_SHIFT: %s' %(
            self.experiment.short_name, self.generate_feature_vector.__name__, feature, 
            bin_type, self.experiment.BIN_SHIFT)
        print self.experiment.hypar_text
        print self
    
    features = self.experiment.features_by_type
    if feature in features['active_states']:
        f = self.get_AS_vector
    elif feature in features['totals']:
        f = self.get_total_vector
    elif feature in features['AS_intensities']:
        f = self.get_AS_intensity_vector
    elif feature in features['bouts']:
        f = self.get_bout_vector
    # elif feature in features['events']:
    #     f = self.get_event_vectors

    if not GENERATE:
        try:
            arr = self.load_feature_vector(feature, bin_type)
        except IOError:
            if VERBOSE:
                print feature, self
            arr = f(feature, bin_type)       # get the feature
    else: 
        arr = f(feature, bin_type) 
                
    # save variables to npy
    if GENERATE:
        E = self.experiment
        self.get_id_string()
        string = '_shifted%+02dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
        dirname = E.features_dir + 'vectors_CT/%s/%s%s/' %(feature, bin_type, string)
        if not os.path.isdir(dirname): os.makedirs(dirname)
        fname = dirname + self.id_string            
        np.save(fname, arr)
        print arr
    return arr



def generate_time_budgets(self, cycle, num_slices, GENERATE=False):

    self.get_id_string()
    dirname = self.experiment.time_budgets_dir + '%s/' %cycle
    fname = dirname + self.id_string

    if not GENERATE:
        try:
            arr = np.load(fname)
        except IOError:
            arr = self.get_time_budgets(cycle, num_slices)
    else: 
        arr = self.get_time_budgets(cycle, num_slices)

    # save variables to npy
    if GENERATE:
        if not os.path.isdir(dirname): os.makedirs(dirname)
        np.save(fname, arr)

    return arr



def generate_bout_feature_vector_per_AS(self, feat, GENERATE=False, VERBOSE=False):

    if VERBOSE:
        print "Exp: %s, %s, %s" %(
                self.experiment.short_name, 
                self.generate_feature_vector.__name__, 
                feat)
        print self.experiment.hypar_text
        print self
    
    features = self.experiment.features_by_type

    if not GENERATE:
        try:
            arr = self.load_bout_feature_per_AS_vector(feat)
        except IOError:
            if VERBOSE:
                print feat, self
            arr = self.get_bout_vector_per_AS(feat)       # get the feature
    else: 
        arr = self.get_bout_vector_per_AS(feat) 
    
    # save variables to npy
    if GENERATE:
        self.get_id_string()
        dirname = self.experiment.features_dir + 'vectors_AS/%s/' %feat
        if not os.path.isdir(dirname): os.makedirs(dirname)
        np.save(dirname + self.id_string, arr)
    return arr


def generate_breakfast_data(self, cycle, act, ONSET, num_mins=15, tbin_size=5, 
    GENERATE=False):
    """ breakfast  
    """
    self.get_id_string()
    text = 'AS_onset' if ONSET else 'AS_offset'
    dirname = self.experiment.breakfast_dir + \
                '%s/%s/prob_%dmin_tbin%ds_%s/' %(
                act, text, num_mins, tbin_size, cycle)
    # dirname2 = self.experiment.breakfast_dir + '%s/%s/cumulative/' %(act, text)
    fname = dirname + self.id_string
    # fname2 = dirname2 + self.id_string

    num_secs = num_mins * 60
    if not GENERATE:
        try:
            arr_p = np.load(fname)
            # arr_c = np.load(fname2)
        except IOError:
            arr_p = self.get_breakfast_probability(
                        act, ONSET, num_secs, tbin_size, cycle)
    else: 
        arr_p = self.get_breakfast_probability(
                        act, ONSET, num_secs, tbin_size, cycle)

    # save variables to npy
    if GENERATE:
        if not os.path.isdir(dirname): os.makedirs(dirname)
        np.save(fname, arr_p)
        # np.save(fname2, arr_c)

    return arr_p#, arr_c




## review
# def generate_feature_array(self, feat, GENERATE=False, VERBOSE=False):
#     features = self.experiment.features_by_type
#     if feat in features['active_states']:
#         f = self.get_AS_array
#     elif feat in features['totals']:
#         f = self.get_total_array
#     elif feat in features['AS_intensities']:
#         f = self.get_AS_intensity_array
#     elif feat in features['bouts']:
#         f = self.get_bout_array
#     # elif feat in features['events']:
#     #     f = self.get_event_data  
#     if VERBOSE:
#         # if not feat.startswith('MB'):
#         print self.generate_feature_array.__name__, feat
#         print self.experiment.hypar_text
#         print self

#     if not GENERATE:
#         try:
#             arr = self.load_feature_array(feat)
#         except IOError:
#             if VERBOSE:
#                 print feat, self
#             arr = f(feat)       # get the feature
#     else: 
#         arr = f(feat) 
    
#     if GENERATE:
#         self.get_id_string()
#         dirname = self.experiment.features_dir + 'arrays/%s/' %feat
#         if not os.path.isdir(dirname): os.makedirs(dirname)
#         np.save(dirname + self.id_string, arr)
#     return list(arr)



