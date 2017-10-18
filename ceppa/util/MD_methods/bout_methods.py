import numpy as np
from ceppa.util import my_utils
from ceppa.util.intervals import Intervals

"""
G.Onnis, 12.2016
updated: 03.2016

Mouseday Class methods for bout computation

Tecott Lab UCSF
"""


def get_ingestion_bouts(self, act='F'):
    """ designation
    """
    BT = getattr(self.experiment, '%sBT' %act)
    I_E, I_at_device = [Intervals(self.load(x)) \
        for x in ['%s_timeSet' %act, 'at_%s_timeSet' %act]]
    # get bouts
    B = Intervals(np.array([]))   
    for k, x in enumerate(I_at_device):         
        X = Intervals(x)    
        # be at device    
        Y = X.intersect(I_E)
        # apply bout threshold                     
        B = B.union(Y.connect_gaps(eps=BT))
    
    # print "total time, %s: bout, %1.2fmin. vs. events, %1.2fmin., ratio: %1.1f" %(
        # act, B.measure()/60., I_E.measure()/60., 1. * B.measure() / I_E.measure())
    print "%d %s bouts vs. %d %s events" %(#, ratio: %1.2f" %(
        B.intervals.shape[0], act, I_E.intervals.shape[0], act, 
        # 1. * B.intervals.shape[0] / I_E.intervals.shape[0]
        )
    assert B.measure() >= I_E.measure(), "do not add up"
    setattr(self, '%sB_timeSet' %act, B.intervals)
    return B


def check_ingestion_bouts(self):
    FB, WB = [Intervals(getattr(self, var)) for var in ['FB_timeSet', 'WB_timeSet']]
    if not FB.intersect(WB).is_empty():
        print "error: F and W bout do intersect."
        sys.exit(-1)
    print "check ingestion bouts.. OK"


def index_ingestion_bout_and_homebase_coordinates(self):    
    # load ingestion and move data 
    T, idx = [self.load(var) for var in ['CT', 'idx_out_HB']]
    I_FB, I_WB = [Intervals(getattr(self, var)) for var in ['FB_timeSet', 'WB_timeSet']]
    assert (I_FB.intersect(I_WB).is_empty()), "WTF!"
    
    # index ingestion time intervals
    I_FWB = I_FB.union(I_WB)
    mask1 = np.ones(T.shape[0], dtype=bool)
    for t in xrange(T.shape[0]):
        if I_FWB.contains(T[t]):
            mask1[t] = False

    # print "indexed %d/%d coordinates within F,W bouts vs. at homebase" %(
    #     T.shape[0] - mask1.sum(), T.shape[0] - idx.sum())

    mask2 = mask1 & idx
    print "indexed %d/%d timestamps for removal" %(#, ratio: %1.2f" %(
        T.shape[0] - mask2.sum(), T.shape[0], 
        # (1.*T.shape[0] - mask2.sum()) / T.shape[0]
        )
    return mask2 


def get_move_bouts(self, MBTT=0.2):
    """ designation
    """        
    MBVT, MBDT, MBTT = [getattr(self.experiment, x) for x in ['MBVT', 'MBDT', 'MBTT']]
    # get txy, distance, velocity, angles
    self.get_move_events()    
    # coordinates within in FW bouts and homebase 
    mask = self.index_ingestion_bout_and_homebase_coordinates()

    varNames = ['CT', 'CX', 'CY', 'idx_at_HB', 'velocity', 'distance']
    T, X, Y, idx_hb, vel, dist = [self.load(var) for var in varNames]
    
    MB = []
    idx_new = np.zeros(T.shape, dtype=bool)
    # # velocity threshold: slower than 1cm/s, it's slow        
    idx = (vel > MBVT) & mask
    b_chunks = my_utils.find_nonzero_runs(idx)
    for idx_on, idx_off in b_chunks:
        x0, y0 = X[idx_on], Y[idx_on]
        x1, y1 = X[idx_off], Y[idx_off]
        d01 = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        
        if d01 > MBDT:
            idx_new[idx_on : idx_off] = True
            MB.append([T[idx_on], T[idx_off]])
        else:
            arrx = X[idx_on : idx_off]
            arry = Y[idx_on : idx_off]
            squared = lambda arrx, arry, x, y: np.sqrt((arrx - x)**2 + (arry - y)**2)
            d1 = squared(arrx, arry, x0, y0)
            d2 = squared(arrx, arry, x1, y1)
            if (d1 > MBDT).any() or (d2 > MBDT).any():
                idx_new[idx_on : idx_off] = True
                MB.append([T[idx_on], T[idx_off]]) 
                
        # # has to leave cell condition
        # cells = np.array(cell_ids[idx_on : idx_off])
        # changed_cell = np.count_nonzero(cells[1:] - cells[:-1]) > 0
    
    # connect short breaks
    B = Intervals(MB).connect_gaps(eps=MBTT).intervals
    if len(B) < len(MB):
        print "connected %d/%d M bout pauses<%.1fs" %(
            len(MB) - len(B), len(MB), MBTT)
        
        # get MB index for T
        lchunk = np.nonzero(np.in1d(T, B[:,0]))[0]
        rchunk = np.nonzero(np.in1d(T, B[:,1]))[0]
        idx_new = np.zeros(T.shape, dtype=bool)
        for l, r in zip(lchunk, rchunk):
            idx_new[l:r] = True

    assert len(B) == len(my_utils.find_nonzero_runs(idx_new))

    print "%d M bouts vs. %d M events" %(#, ratio: %1.2f" %(
                B.shape[0], T.shape[0], 
                # 1.*B.shape[0] / T.shape[0]
                )
    setattr(self, 'MB_timeSet', B)
    setattr(self, 'MB_idx', idx_new)


def get_bout_feature_value(self, feat, tbin, b):  
# def get_bout_feature_value(self, feat, bin_type, tbin):  
    """ Bout features value: B_AS_Rate, B_onsetss, B_size, B_duration, B_intensity
        for bin_types 24H, DC, LC, 12bins
    """
    act, ftype = feat[0], feat[1:]
    # tbins = my_utils.get_CT_bins(bin_type)

    AS = self.load('AS_timeSet')
    B = self.load('%sB_timeSet' %act)

    # # experiments with FAST on day x
    if self.experiment.short_name == '2CFast':            # has a fast day
        if self.dayNumber in self.experiment.fastDayNumbers:
            if act == 'F':
                _, tend = self.experiment.get_food_removal_times()
                # zero food after fast begins     
                idx0 = np.where(AS[: ,1]<=tend)[0]
                AS = AS[idx0]
                idx1 = np.where(B[: ,1]<=tend)[0]
                B = B[idx1]

    # AS times and counts, strictly defined
    AS_times, _, _, _ = my_utils.count_onsets_in_bin(I=AS, tbin=tbin)
    AS_cnt = AS_times.shape[0]

    # B times (strict), B onsets in bin, B time in bin_effective + bin_effective
    B_times, B_cnt_eff, B_times_eff, tbin_eff = my_utils.count_onsets_in_bin(I=B, tbin=tbin)
    # B counts, strict
    B_cnt = B_times.shape[0]    
    
    fval = 0
    if B_cnt_eff > 0:
        if ftype == 'BN':                # counts, onset-based
            fval = B_cnt_eff        
        
        elif ftype == 'BASR':            # bout AS rate, onset-based
            if AS_times.sum() > 0:
                fval = B_cnt_eff / (AS_times.sum() / 3600.)     # onsets/AShr., AS strictly defined
        
        elif ftype == 'BD':                         # avg bout duration, strict
            fval = B_times_eff.sum() / B_cnt_eff    # sec

        elif ftype in ['BS', 'BI']:      
            if act in ['F', 'W']:
                amounts = self.get_amounts(act, I=B, tbin=tbin_eff)     # mg, amounts, onset-based
                np.testing.assert_allclose(amounts.shape[0], B_cnt_eff, rtol=1e-5)
                fval = amounts.sum() / B_cnt_eff                # avg bout size, onset-based

                if ftype == 'BI':
                    fval = np.mean(amounts / B_times_eff)       # avg intensity, mg/s, onset-based

            elif act == 'M':
                dist = self.get_move_distances_in_AS_or_Bout(tbin=tbin_eff, move_type='bout')    # cm, distances, onset-based      
                np.testing.assert_allclose(dist.shape[0], B_cnt_eff, rtol=1e-5)
                fval = dist.sum() / B_cnt_eff                   # avg bout size, onset-based

                if ftype == 'BI':
                    fval = np.mean(dist / B_times_eff)       # avg intensity, cm/s, onset-based

    return fval


def get_bout_vector(self, feat, bin_type='12bins'):
    """ returns array with (features, num_bins):
        counts, duration, size, intensity
    """
    tbins = my_utils.get_CT_bins(bin_type, self.experiment.BIN_SHIFT, self.experiment.binTimeShift)      
    arr = np.zeros(len(tbins))
    b = 0
    for tbin in tbins:
        arr[b] = self.get_bout_feature_value(feat, tbin, b)  
        # arr[b] = self.get_bout_feature_value(feat, bin_type, tbin=tbin)
        b +=1   
    # elif bin_type == 'LC':
    #     arr = self.get_bout_feature_value(feat, bin_type, tbin=tbins)
    return arr


# def get_bout_vector(self, feat, bin_type='12bins'):
#     """ returns array with (features, num_bins):
#         counts, duration, size, intensity
#     """
#     tbins = my_utils.get_CT_bins(bin_type, self.experiment.BIN_SHIFT, self.experiment.binTimeShift)      

#     if bin_type in ['12bins', '24bins','24H', 'DC']:
#         arr = np.zeros(len(tbins))
#         b = 0
#         for tbin in tbins:
#             arr[b] = self.get_bout_feature_value(feat, bin_type, tbin=tbin)
#             b +=1   

#     elif bin_type == 'LC':
#         arr = self.get_bout_feature_value(feat, bin_type, tbin=tbins)
#     return arr



# # bout features in each AS
def get_bout_feature_value_per_AS(self, feat, tbin, AS_num):  
    """ Bout features value: B_AS_Rate, B_onsetss, B_size, B_duration, B_intensity
        for bin_types 24H, DC, LC, 12bins
    """
    act, ftype = feat[0], feat[1:]
    B = self.load('%sB_timeSet' %act)

    B_AS = Intervals(B).intersect(Intervals(tbin)).intervals
    B_cnt = len(B_AS)   

    fval = 0
    if B_cnt > 0:
        if ftype == 'BN':                # counts
            fval = B_cnt        
        
        elif ftype == 'BASR':            # bout AS rate
            if tbin.sum() > 0:
                fval = B_cnt / (tbin.sum() / 3600.)     # onsets/AShr.
        
        elif ftype == 'BD':                         # avg bout duration, strict
            fval = np.diff(B_AS).sum() / B_cnt      # sec

        elif ftype in ['BS', 'BI']:      
            B_dur = np.diff(B_AS).sum()
            if act in ['F', 'W']:
                amounts = self.get_amounts(act, I=B, tbin=tbin)     # mg, amounts, onset-based
                np.testing.assert_allclose(amounts.shape[0], B_cnt, rtol=1e-5)
                fval = amounts.sum() / B_cnt                # avg bout size, onset-based

                if ftype == 'BI':
                    fval = np.mean(amounts / B_dur)       # avg intensity, mg/s, onset-based

            elif act == 'M':
                _dist = self.get_move_distances_in_AS_or_Bout(tbin=tbin, move_type='bout')    # cm, distances, onset-based      
                dist = self.correct_bouts_intersecting_bin(_dist, AS_num)
                np.testing.assert_allclose(dist.shape[0], B_cnt, rtol=1e-5)
                fval = dist.sum() / B_cnt                  # avg bout size, onset-based

                if ftype == 'BI':
                    fval = np.mean(dist / B_dur)       # avg intensity, cm/s, onset-based


    return fval


def get_bout_vector_per_AS(self, feat):
    """ returns array with (features, num_bins):
        counts, duration, size, intensity
    """
    AS = self.load('AS_timeSet')
    AS_clean = my_utils.wipe_data_outside_CT6_30(AS)

    arr = np.zeros(len(AS))       
    b = 0
    for _AS in AS_clean:
        arr[b] = self.get_bout_feature_value_per_AS(feat, tbin=_AS, AS_num=b)
        b +=1   
    return arr



# # # # for stats
def get_bout_array(self, feat):
    """ feature values across 24hrs
    """
    act = feat[0]
    ftype = feat[1:]
    AS = self.load('AS_timeSet')
    B = self.load('%sB_timeSet' %act)
    AS_time = np.diff(AS).sum() / 3600.     # hr
    num_bouts = B.shape[0]
    if num_bouts > 0:
        if ftype == 'BN':
            arr = np.array([num_bouts])
        elif ftype == 'BASR':
            arr = np.array([num_bouts / AS_time]) 
        elif ftype == 'BD':
            arr = np.diff(B)            # sec       
        elif ftype in ['BS', 'BI']:
            if act in ['F', 'W']:
                arr = self.get_amounts(I=B, act=act)            #mg 
                if ftype == 'BI':
                    arr = self.get_intensities(I=B, act=act)    # mg/s
            elif act == 'M':
                # sanity check
                idx = self.get_move_idx(move_type='bout')
                b_chunks = my_utils.find_nonzero_runs(idx)
                assert num_bouts == b_chunks.shape[0], 'WTF'
                arr = self.get_move_distances(move_type='bout')                 # cm
                if ftype == 'BI':
                    arr = self.get_move_speeds(move_type='bout')                # cm/s
    return np.array(arr)
    







