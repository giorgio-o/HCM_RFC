import numpy as np
import os
from ceppa.util import my_utils
from ceppa.util.intervals import Intervals

"""
G.Onnis, 12.2016
updated: 03.2017, 06.2017 

Mouseday Class methods for events computation

Tecott Lab UCSF
"""


def get_ingestion_coefficients(self, act='F', qty='coeffs'):
    """ returns feeding (drinking) coefficient [g/s]
    """
    EV = self.load('%s_timeSet' %act)

    EV_duration = np.diff(EV).sum()
    qt = self.chow_eaten_grams * 1000 if act == 'F' else self.water_drunk_grams * 1000 #mg
        # # or mg per lick  
        # coeff = 1000*self.water_drink_grams / EV.intervals.shape[0]
    if qty == 'coeffs':      
        return qt / EV_duration    #mg/sec
    elif qty == 'tots':
        return qt       #mg
    elif qty == 'durs':
        return EV_duration      # sec




def get_device_firing_durations_in_AS_or_Bouts(self, EV, I, tbin):
    """ get all durations for each AS/Bouts(I), for specified tbin
    """
    if tbin is None:        # use 24h bin
        tbin = my_utils.get_CT_bins(bin_type='24H')

    _I = Intervals(I).intersect(Intervals(tbin))     
    durs = np.zeros(_I.intervals.shape[0])
    c = 0
    for x in _I: 
        durs[c] = Intervals(x).intersect(Intervals(EV)).measure()     
        # if act == 'W':
        #    size[c] = Intervals(x).intersect(EV).intervals.shape[0] * coeff      # grams
        c +=1 
    return durs


def get_device_firing_durations(self, act='F', I=None, tbin=None):
    """
    """
    EV = self.load('%s_timeSet' %act)        

    # # experiments with FAST on day x
    if self.experiment.short_name == '2CFast':            # has a fast day
        if self.dayNumber in self.experiment.fastDayNumbers:
            if act == 'F':
                _, tend = self.experiment.get_food_removal_times()
                # zero food after fast begins     
                idx = np.where(EV[:, 1]<=tend)[0]
                EV = EV[idx]

    if I is not None:  
        # total duration (sum) for each AS/Bout(I) in bin, e.g. for Intensities
        # if tbin=None, get duration for all AS/Bouts across the 24h
        durs = self.get_device_firing_durations_in_AS_or_Bouts(EV, I, tbin) 
    else:
        if tbin is not None:
            # all events durations for specified tbin, e.g. for Totals
            tmp = Intervals(EV).intersect(Intervals(tbin)).intervals
            if len(tmp) > 0:
                durs = np.diff(tmp).T[0]
            else:
                durs = np.zeros(1) 
            # stop
        else:
            _EV = my_utils.wipe_data_outside_CT6_30(EV)
            # all events durations across the 24H, entire day
            durs = np.diff(_EV).T[0]
            np.testing.assert_allclose(durs.sum(), Intervals(_EV).measure(), rtol=1e-5)

    return durs 


def get_amounts(self, act='F', I=None, tbin=None):
    """ return amounts for AS/Bout(I), in a specified tbin. 
        if tbin is None, use 24H
    """
    durs = self.get_device_firing_durations(act, I, tbin)   # s
    coeff = self.get_ingestion_coefficients(act)   # mg/s
    
    # # experiments with FAST on day x
    if self.experiment.short_name == '2CFast':            # has a fast day
        if self.dayNumber in self.experiment.fastDayNumbers:
            if act == 'F':
                # get mouseday from day before
                MD = self.experiment.get_mouseday_object(self.mouseNumber, self.dayNumber-1)
                coeff = MD.get_ingestion_coefficients(act)

    return durs * coeff    # mg


def get_CT_idx_in_tbin(self, tbin=None):
    """gets move timestamps in specified tbin
    """            
    T = self.CT
    # all move timestamps across the 24H, entire day
    idx = my_utils.get_idx_timestamps_outside_CT6_30(
                        T, 
                        SHIFT=self.experiment.BIN_SHIFT, 
                        tshift=self.experiment.binTimeShift)
    if tbin is None:
        return idx
    else:
        # move timestamps for specified tbin
        idx2 = np.zeros_like(T, dtype=bool)         
        tbin_ = tbin[np.newaxis] if tbin.ndim < 2 else tbin      #LC (ndim=2), does not need newaxis
        for t in tbin_:                  
            idx_start = np.searchsorted(T, t[0])
            idx_end = np.searchsorted(T, t[1], side='right')
            idx2[idx_start : idx_end] = True

    return idx & idx2


def get_move_idx(self, tbin=None, move_type=None):
    """get move timestamps for specified tbin and move types: 
        -'at_hb'  , move at homebase
        -'out_hb' , move non-HB
        -'AS'     , move during AS, HB and non-HB 
        -'bout'   , move during bout, non-HB
    """
    T = self.load('CT') 

    # move timestamps for specified move_type
    if move_type is None:
        # all tstamps: in and out homebase
        idx1 = my_utils.get_idx_timestamps_outside_CT6_30(
                            T, 
                            SHIFT=self.experiment.BIN_SHIFT, 
                            tshift=self.experiment.binTimeShift) 
        stop     
    elif move_type == 'AS':     
        idx1 = self.load('AS_idx')      # tstamps in AS
    elif move_type == 'bout':
        idx1 = self.load('MB_idx')
    elif move_type == 'at_hb':
        idx1 = self.load('idx_at_HB')
    elif move_type == 'out_hb':
        idx1 = self.load('idx_out_HB')
        
    idx2 = self.get_CT_idx_in_tbin(tbin)
    # if tbin.ndim==1:stop
    return idx1 & idx2


def get_move_distances(self, tbin=None, move_type=None):
    dist, _ = self.get_move_events()       # cm
    idx = self.get_move_idx(tbin, move_type)
    return dist[idx]


def get_move_distances_in_AS_or_Bout(self, tbin, move_type=None):
    """ 
    """
    dist, _ = self.get_move_events()       # cm
    # move timestamps for AS/Bouts(I), for specified bin
    idx1 = self.get_move_idx(tbin, move_type)
    I_chunks = my_utils.find_nonzero_runs(idx1)
    distances = np.zeros(len(I_chunks))
    c = 0
    for start, end in I_chunks:
        distances[c] = dist[start:end].sum()
        c +=1
    return distances


def get_move_speeds(self, bins=None, move_type=None):
    pass
#     T = self.load('CT')
#     idx = self.get_move_idx(bins, move_type)
#     b_chunks = my_utils.find_nonzero_runs(idx)
#     dist, _ = self.get_move_events()
#     speed = np.zeros(len(b_chunks))
#     c = 0
#     for start, end in b_chunks:
#         speed[c] = dist[start:end].sum() / (T[end] - T[start])  # cm /s
#         c +=1
#     return speed


def get_move_events(self):
    """ returns arrays with:
        - T, X, Y
        - distances traveled 
        - velocity
        - angle resp. x=0, turning angle
    """
    varNames = ['CT'] + self.experiment.HCM_derived['events']['M']
    try:
        for var in varNames:
            self.load(var)
        return self.distance, self.velocity

    except IOError:
        print "failed loading move event data, computing.."
        T = self.CT  
        X, Y = [self.load(var) for var in ['CX', 'CY']]
        dT, dX, dY = T[1:]-T[:-1], X[1:] - X[:-1], Y[1:] - Y[:-1]
        dist = np.sqrt(dX ** 2 + dY ** 2)           # cm
        vel = dist / dT                             # cm/s
        ang = np.arctan(np.nan_to_num(dY / dX))     # here could be np.arctan2(y,x)
        # ang2 = self.get_trajectory_angles(X, Y)    # gets you turning angle
        # deg_ang2 = ang2 * 180 / np.pi                                                  # or, could be get_trajectory_angles(self) wrong
        arr_list = [
            dT,                             # delta_t, s
            dist,                           # total distance, cm
            vel,                            # velocity, cm/s
            ang,                            # abs agle, rad
            (ang[1:] - ang[:-1])            # turning angles #*180/np.pi, degrees
            ]
        # pad zero values at CT=0
        vars_to_save = varNames[1:]
        for var, name in zip(arr_list, vars_to_save):
            # setattr(self, name, np.insert(var, 0, 0))   # at i+1
            setattr(self, name, np.append(var, 0))    # value assigned at i
        # save
        for name in vars_to_save:
            dirname = self.experiment.events_dir + 'M/%s/' %name 
            if not os.path.isdir(dirname): os.makedirs(dirname)
            np.save(dirname + self.id_string, getattr(self, name))

    return self.distance, self.velocity


def get_trajectory_angles(self, X, Y):      
    """this gets you the turning angle directly
    """
    print "computing trajectory angle.."
    vectors = np.array(zip(X, Y))
    angle = np.zeros_like(X)
    for v in xrange(1, len(vectors) - 1): 
        origin = vectors[v-1]
        A, B = vectors[v: v+2] - origin
        norm1 = np.sqrt((A**2).sum())
        norm2 = np.sqrt((B**2).sum())
        
        # one = (A * B).sum()
        # two = np.dot(A, B)
        # np.testing.assert_almost_equal(one, two, decimal=10, err_msg='dot product wrong')

        cos = np.dot(A, B) / (norm1 * norm2)
        angle[v] = np.arccos(cos)

    return angle


# def get_event_vectors(self, feat, bin_type='12bins'):
#     EV = Intervals(self.load('%s_timeSet' %feat[0]))
#     bins = my_utils.get_CT_bins(bin_type)      # Intervals. 11 bins
#     arr = np.zeros(len(bins))
#     for b, bin_ in enumerate(bins):
#         if feat[2:] == 'TD':    # total duration
#             arr[b] = EV.intersect(bin_).measure() / 60  #min
#         else:
#             bin_start, bin_end = bin_.intervals[0]
#             bin_time = 0
#             cnt = 0
#             for start, end in EV.intervals:
#                 if start > bin_start and start < bin_end:
#                     bin_time += end - start
#                     cnt +=1
#             if feat[2:] == 'N':   # counts
#                 arr[b] = cnt    
#             elif feat[2:] == 'AD':     # average duration
#                 if cnt > 0:
#                     arr[b] = bin_time / cnt    # sec
#     return arr


    # # old

    # def get_event_interevent_data(self):
    #     """
    #     """
    #     cstart = time.clock()
    #     for act in ['F', 'W']:
    #         self.get_event_ingestion_data(act)
    #     self.get_move_events()    # move out of HomeBase
    #     # cell_ids = self.get_cage_cell_id(T, X, Y, NUMERIC=True)
    #     # setattr(self, 'cell_ids', cell_ids)
    #     cstop = time.clock()


    # def get_event_ingestion_data(self, act='F'):
    #     arr_EV = self.get_ingestion_intervals(act=act)
    #     num_events = arr_EV.shape[0]
    #     durs = np.array([])
    #     i_durs = np.array([])
    #     if num_events > 0:
    #         durs = arr_EV[:, 1] - arr_EV[:, 0]
    #         i_durs = arr_EV[1:, 0] - arr_EV[:-1, 1]
    #         # i_durs = np.zeros(durs.shape[0])
    #         # for k in xrange(1, num_events):
    #         #     i_durs[k] = arr[k, 0] - arr[k-1, 1]
    #         # i_durs = i_durs[1:]
    #     setattr(self, '%s_durs' %act, durs)
    #     setattr(self, '%s_idurs' %act, i_durs)
    #     # print "dur min:%1.4f, max:%1.4f" %(durs.min(), durs.max())
    #     # print "dur avg:%1.4f, median:%1.4f" %(durs.mean(), np.median(durs))  
    #     # print "IEI dur min:%1.4f, max:%1.4f" %(i_durs.min(), i_durs.max())
    #     # print "IEI dur avg:%1.4f, median:%1.4f" %(i_durs.mean(), np.median(i_durs))   
  

    # # def get_ingestion_intervals(self, act='F'):
    # #     """ returns intervals [sec] at which event take place,
    # #         where intervals that: 
    # #         -START in CT6-8, END in CT8-10,
    # #         -START in CT28-30, END in CT30-32
    # #         have been removed.
    # #     """
    # #     # print "computing ingestion intervals.."

    # #     feat_name = '%s_Sets' %act
    # #     if not hasattr(self, feat_name):
    # #         self.load(feat_name)
    # #     return getattr(self, feat_name)
