import numpy as np
import time
import os

from ceppa.util import my_utils

"""
G.A.Onnis, 01.2017

Experiment Class methods for generating all sorts of data

Tecott Lab UCSF
"""



def generate_binaries(experiment, mouseNumber=None, dayNumber=5):
    cstart = time.clock()
    print "%s, from raw HCM data.." %experiment.generate_binaries.__name__
    print "-- IST, BT, MBT play no role here --" 
    if mouseNumber is None:
        for group in experiment.groups:    
            for mouse in group.individuals:
                for MD in mouse.mouse_days: 
                    if MD.dayNumber in experiment.daysToUse:              
                        MD.generate_binaries()
    else:
        mouse = experiment.get_mouse_object(mouseNumber)
        if not mouse.ignored:
            MD = mouse.mouse_days[dayNumber-1]
            if not MD.ignored:
                MD.generate_binaries()
               
    cstop = time.clock()
    if mouseNumber is None:
        print "binary output saved to:\n%s" %experiment.HCM_data_dir
        print "..took: %1.2f minutes"%((cstop-cstart)/60.)
        

def generate_bouts(experiment, mouseNumber=None, dayNumber=5):
    """
    """
    cstart = time.clock()
    if mouseNumber is None:
        for group in experiment.groups:    
            for mouse in group.individuals:
                if not mouse.ignored:
                    for MD in mouse.mouse_days:
                        if MD.dayNumber in experiment.daysToUse:
                            if not MD.ignored:
                                MD.generate_bouts()
    else:
        mouse = experiment.get_mouse_object(mouseNumber)
        if not mouse.ignored:
            MD = mouse.mouse_days[dayNumber-1]
            if not MD.ignored:
                MD.generate_bouts()
    cstop = time.clock()
    if mouseNumber is None:
        print "binary output saved to: %s/bouts/" %experiment.derived_dir
        print "..took: %1.2f minutes"%((cstop-cstart)/60.)
        

def generate_active_states(experiment, mouseNumber=None, dayNumber=5):
    cstart = time.clock() 
    if mouseNumber is None:
        cnt = 0
        for group in experiment.groups:    
            for mouse in group.individuals:
                if not mouse.ignored:
                    for MD in mouse.mouse_days:
                        if MD.dayNumber in experiment.daysToUse:
                            if not MD.ignored:
                                MD.generate_active_states()
                                my_utils.print_progress(cnt, experiment.num_md_ok)
                                cnt += 1
    else:
        mouse = experiment.get_mouse_object(mouseNumber)
        if not mouse.ignored:
            MD = mouse.mouse_days[dayNumber-1]
            if not MD.ignored:
                MD.generate_active_states()
    cstop = time.clock()
    if mouseNumber is None:
        print "binary output saved to: %s" %experiment.active_states_dir
        print "..took: %1.2f minutes"%((cstop-cstart)/60.)
        

def generate_position_density(self, xbins=12, ybins=24, level='strain', 
        cycle='24h', GET_AVGS=False):
    """ returns position density data 
    """
    cstart = time.clock()
    print "%s.." %self.generate_position_density.__name__
    md_data = np.zeros((self.num_md_ok, ybins, xbins))
    md_labels = np.zeros((self.num_md_ok, 3), dtype=int)
    print "%s %s data xbins=%d, ybins=%d.." %(
            self.generate_position_density.__name__, cycle, xbins, ybins)
    cnt = 0
    for group in self.groups:    
        for mouse in group.individuals:
            if not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in self.daysToUse:
                        if not MD.ignored:
                            bin_times = MD.generate_position_bin_times(xbins, ybins, cycle)
                            if bin_times.sum() >= 0:
                                md_data[cnt] = bin_times / bin_times.sum()
                            md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                            cnt +=1

    if GET_AVGS:
        E = self
        s_data, s_labels, m_data, m_labels = \
                my_utils.get_2d_mouse_strain_averages(E, md_data, md_labels)
        # m_data, m_labels = my_utils.day_to_mouse_average_pos_dens(E, arr, arr_labels)
        # strain_data = my_utils.mouse_to_strain_average_pos_dens(E, m_data, m_labels)
        return s_data, s_labels, m_data, m_labels, arr, md_labels
    cstop = time.clock()
    print "..took: %1.2f minutes"%((cstop-cstart)/60.)
    return arr, md_labels


def generate_homebase_data(self):
    rects_HB, obs_rects = [], []
    for group in self.groups:    
        for mouse in group.individuals:
            if not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in self.daysToUse:
                        if not MD.ignored:
                            rect_HB, obs_rect = [MD.load(var) for var in ['rect_HB', 'obs_HB']] 
                            rects_HB.append(rect_HB)
                            obs_rects.append(obs_rect)
    return rects_HB, obs_rects


def _check_bout_counts_in_bins(experiment, act, vec_type='12bins'):
    num_bins = 12 
    print "%s, %s, %dbins" %(_check_bout_counts_in_bins.__name__, act, num_bins)

    arr = np.zeros((experiment.num_md_ok, num_bins + 3))
    cnt = 0
    for group in experiment.groups:  
        for mouse in group.individuals:
            if not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in experiment.daysToUse:
                        if not MD.ignored:
                            arr[cnt, :3] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                            arr[cnt, 3:] = MD._check_bout_counts_in_bins(act)
                            my_utils.print_progress(cnt, experiment.num_md_ok)
                            cnt +=1

    dirname = experiment.features_dir + 'vectors/_bout_counts_check/'
    import os
    if not os.path.isdir(dirname): os.makedirs(dirname)
    np.save(dirname + '%s_bout_counts_check' %act, arr)

    return arr


def generate_feature_vectors(experiment, feat='ASP', vec_type='12bins', days=None, 
        GET_AVGS=False, strain_avg_type='over_mds', GENERATE=False, VERBOSE=False):
    """ returns: 
        array with data for all legit mousedays
            arr: (num_mousedays, num_bins)
        mice and strain data 
            data[0]: avgs 
            data[1]: stdev
            data[2]: stderr
        labels
    """ 
    E = experiment
    cstart = time.clock() 

    num_bins = 12 if vec_type.endswith('bins') else 3
    print "%s, %s, %s" %(generate_feature_vectors.__name__, feat, vec_type)
    
    days_to_use = E.daysToUse if days is None else days
    _, num_md_ok = E.count_mousedays(days=days_to_use)

    md_data = np.zeros((num_md_ok, num_bins))
    md_labels = np.zeros((num_md_ok, 3), dtype=int)
    cnt = 0
    for group in E.groups:  
        for mouse in group.individuals:
            if not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in days_to_use:
                        if not MD.ignored:
                            md_data[cnt] = MD.generate_feature_vector(
                                                feat, vec_type, GENERATE, VERBOSE)
                            md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                            if GENERATE and not VERBOSE:
                                my_utils.print_progress(cnt, E.num_md_ok)
                            cnt +=1

    cstop = time.clock()
    
    if GENERATE:
        if not VERBOSE: 
            print
        print "binary output saved to: %s" %E.features_dir 
        print "..took %1.2f minutes"%((cstop-cstart)/60.)
    
    if GET_AVGS:
        s_data, s_labels, m_data, m_labels = \
                my_utils.get_1d_mouse_strain_averages(
                            E, md_data, md_labels, strain_avg_type)
        return s_data, s_labels, m_data, m_labels, md_data, md_labels

    return md_data, md_labels


def generate_bout_feature_vectors_per_AS(experiment, feat='ASP', days=None, 
        GET_AVGS=True, strain_avg_type='over_mds', GENERATE=False, VERBOSE=False):
    """ returns: 
        array with data for all legit mousedays
            arr: (num_mousedays, num_bins)
        mice and strain data 
            data[0]: avgs 
            data[1]: stdev
            data[2]: stderr
        labels
    """ 
    E = experiment
    cstart = time.clock() 

    print "%s, %s" %(generate_bout_feature_vectors_per_AS.__name__, feat)
    
    days_to_use = E.daysToUse if days is None else days
    _, num_md_ok = E.count_mousedays(days=days_to_use)

    md_data = []
    md_labels = np.zeros((num_md_ok, 3), dtype=int)
    cnt = 0
    for group in E.groups:  
        for mouse in group.individuals:
            if not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in days_to_use:
                        if not MD.ignored:
                            md_data.append(MD.generate_bout_feature_vector_per_AS(
                                                feat, GENERATE, VERBOSE)
                                    )
                            md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                            if GENERATE and not VERBOSE:
                                my_utils.print_progress(cnt, E.num_md_ok)
                            cnt +=1

    cstop = time.clock()
    
    if GENERATE:
        if not VERBOSE: 
            print
        print "binary output saved to: %s" %E.features_dir 
        print "..took %1.2f minutes"%((cstop-cstart)/60.)
    
    if GET_AVGS:
        s_data, s_labels, m_data, m_labels = \
                my_utils.get_1d_list_mouse_strain_averages(
                            E, md_data, md_labels, days, strain_avg_type)
        return s_data, s_labels, m_data, m_labels, md_data, md_labels

    return md_data, md_labels


def generate_feature_vectors_expdays(experiment, feat, vec_type, days=None, 
        GET_AVGS=False, strain_avg_type='over_mds'):
    """ relies on generate_feature_vector values
    """ 
    E = experiment
    num_bins = 12 if vec_type.endswith('bins') else 3
    print "%s, %s, %s" %(generate_feature_vectors_expdays.__name__, feat, vec_type)

    days_to_use = E.daysToUse if days is None else days
    num_md, _ = E.count_mousedays(days=days_to_use)

    md_data = np.zeros((num_md, num_bins))           
    md_labels = np.zeros((num_md, 3), dtype=int)
    cnt = 0
    for group in E.groups:  
        for mouse in group.individuals:
            for MD in mouse.mouse_days:
                if MD.dayNumber in days_to_use:
                    if not MD.ignored:
                        md_data[cnt] = MD.generate_feature_vector(feat, vec_type)
                    else:
                        # print "ignored", MD
                        md_data[cnt] = np.nan

                    md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                    cnt +=1

    if GET_AVGS:
        s_data, s_labels, m_data, m_labels = \
            my_utils.get_mouse_strain_averages_expdays(
                E, md_data, md_labels, days, strain_avg_type
                )
        return s_data, s_labels, m_data, m_labels, md_data, md_labels

    return md_data, md_labels




def generate_breakfast_data(experiment, act='F', ONSET=True, num_mins=15, tbin_size=5, days=None, 
        GET_AVGS=False, strain_avg_type='over_mds', GENERATE=False, VERBOSE=False):
    
    E = experiment
    
    days_to_use = E.daysToUse if days is None else days
    _, num_md_ok = E.count_mousedays(days=days_to_use)

    print "%s, %s, ONSET: %s" %(generate_breakfast_data.__name__, act, ONSET)

    num_bins = int(num_mins * 60 / tbin_size)
    text = 'AS_onset' if ONSET else 'AS_offset'
    
    md_data = np.zeros((num_md_ok, num_bins))
    md_labels = np.zeros((num_md_ok, 3), dtype=int)
    cnt = 0
    for group in E.groups:  
        for mouse in group.individuals:
            if not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in days_to_use:
                        if not MD.ignored:
                            md_data[cnt] = MD.generate_breakfast_data(
                                                act, ONSET, num_mins, tbin_size, GENERATE)
                            md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                            if not VERBOSE:
                                my_utils.print_progress(cnt, E.num_md_ok)
                            else:
                                print MD
                            cnt +=1

    cstart = time.clock() 
    cstop = time.clock()
    
    if GENERATE:
        if not VERBOSE: 
            print
        dirname = E.breakfast_dir + \
                    '%s/%s/prob_%dmin_tbin%ds/' %(
                        act, text, num_mins, tbin_size)
        print "binary output saved to: %s" %dirname 
        print "..took %1.2f minutes"%((cstop-cstart)/60.)

    if GET_AVGS:
        s_data, s_labels, m_data, m_labels = \
            my_utils.get_1d_mouse_strain_averages(E, md_data, md_labels, strain_avg_type)
        return s_data, s_labels, m_data, m_labels, md_data, md_labels

    return md_data, md_labels


def generate_time_budgets(experiment, cycle='24H', AS=False, days=None, GET_AVGS=False, 
        strain_avg_type='over_mds', GENERATE=False, VERBOSE=False):
    
    E = experiment

    cstart = time.clock() 

    print "%s, %s" %(generate_time_budgets.__name__, cycle)

    days_to_use = E.daysToUse if days is None else days
    _, num_md_ok = E.count_mousedays(days=days_to_use)

    num_slices = 5 if not AS else 4    #move, feed, drink, other_AS, inactive
    md_data = np.zeros((num_md_ok, num_slices))
    md_labels = np.zeros((num_md_ok, 3), dtype=int)
    cnt = 0
    for group in E.groups:  
        for mouse in group.individuals:
            if not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in days_to_use:
                        if not MD.ignored:
                            md_data[cnt] = MD.generate_time_budgets(
                                                cycle, num_slices, GENERATE)
                            md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                            if not VERBOSE:
                                my_utils.print_progress(cnt, E.num_md_ok)
                            else:
                                print MD
                            cnt +=1


    cstop = time.clock()

    if GENERATE:
        if not VERBOSE: 
            print
        dirname = E.time_budgets_dir + '%s/' %cycle
        print "binary output saved to: %s" %dirname 
        print "..took %1.2f minutes"%((cstop-cstart)/60.)

    if GET_AVGS:
        s_data, s_labels, m_data, m_labels = \
            my_utils.get_1d_mouse_strain_averages(E, md_data, md_labels, strain_avg_type)
        return s_data, s_labels, m_data, m_labels, md_data, md_labels

    return md_data, md_labels

# review
# def generate_feature_arrays(experiment, feat, GENERATE=False, VERBOSE=False):
#     """ generate a list - 16 strains - of lists - all feature values during days
#     """
#     cstart = time.clock()
#     print "%s, %s.." %(generate_feature_arrays.__name__, feat)

#     cnt = 0
#     all_arrays = []     
#     for group in experiment.groups:
#         arrs = [] 
#         for mouse in group.individuals:
#             if not mouse.ignored:
#                 for MD in mouse.mouse_days:
#                     if MD.dayNumber in experiment.daysToUse:
#                         if not MD.ignored:                    
#                             arr = MD.generate_feature_array(feat, GENERATE, VERBOSE) 
#                             arrs.extend(arr)
#                             if GENERATE and not VERBOSE:
#                                 my_utils.print_progress(cnt, experiment.num_md_ok)
#                             cnt +=1
#         all_arrays.append(arrs)                  
    
#     cstop = time.clock()
#     if GENERATE:
#         if not VERBOSE:
#             print
#         print "binary output saved to: %s" %experiment.features_dir+'arrays'
#         print "..took %1.2f minutes"%((cstop-cstart)/60.)
#     return all_arrays#, arr_labels



# # old
# # bout stats
# def generate_bout_data(self, act='M', varName=None):
#     """ generate numbers for bout stats
#     """
#     cstart = time.clock()
#     print "generating %s distribution data.." %varName
#     arrays = []
#     arr_labels = np.zeros((self.num_md_ok, 3))
#     cnt = 0
#     for group in self.groups:   
#         for mouse in group.individuals:
#             if not mouse.ignored:
#                 for MD in mouse.mouse_days:
#                     if MD.dayNumber in self.daysToUse:
#                         if not MD.ignored:                    
#                             arr = MD.generate_bout_data(act, varName)                  
#                             arrays.append(arr)
#                             arr_labels[cnt] = int(MD.groupNumber), int(MD.mouseNumber), int(MD.dayNumber)
#                             cnt +=1
#     cstop = time.clock()
#     if (cstop-cstart) > 100:
#         print "-> %s for %s took: %1.2f minutes"%(self.generate_bout_data.__name__, act, (cstop-cstart)/60.)
#         print "binary output saved to: %s" %getattr(self, '%s_bouts_dir' %act)
#     return arrays, arr_labels


# # events
# def get_event_days_data(self, feat):
#     print "loading %s event data.." %feat
#     mouse_arr = np.zeros((self.num_mice_ok, len(self.daysToUse))) 
#     mouse_labels = np.zeros((self.num_mice_ok, 2)) 
#     c = 0
#     for group in self.groups:
#         for mouse in group.individuals:
#             if not mouse.ignored:
#                 k = 0
#                 for MD in mouse.mouse_days:
#                     if MD.dayNumber in self.daysToUse:
#                         if not MD.ignored:
#                             mouse_arr[c, k] = MD.load(feat)
#                         k += 1
#                 mouse_labels[c] = MD.groupNumber, MD.mouseNumber
#                 c += 1
#     return mouse_arr, mouse_labels


# #stats
# def get_numbers(self, act='F', what='AS'):
#     print "getting %s %s numbers distribution data.." %(act, what)
#     arr = np.zeros(self.num_md_ok)
#     arr_labels = np.zeros((self.num_md_ok, 3))
#     cnt = 0
#     varName = 'AS_timeSet'
#     if what == 'bout':
#         varName = '%sB_timeSet' %act
#     elif what == 'event':
#         varName = '%s_timeSet' %act
#     for group in self.groups:   
#         for mouse in group.individuals:
#             if not mouse.ignored:
#                 for MD in mouse.mouse_days:
#                     if MD.dayNumber in self.daysToUse:
#                         if not MD.ignored:                    
#                             arr[cnt] = MD.load(varName).shape[0]                
#                             arr_labels[cnt] = int(MD.groupNumber), int(MD.mouseNumber), int(MD.dayNumber)
#                             cnt +=1
#     return arr, arr_labels
