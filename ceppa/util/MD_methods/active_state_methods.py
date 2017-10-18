import numpy as np

from ceppa.util.my_utils import count_onsets_in_bin, get_CT_bins, get_intensity
from ceppa.util.intervals import Intervals

"""
G.Onnis, 01.2017
updated: 03.2016

Mouseday Class methods for active states computation1

Tecott Lab UCSF
"""


def get_AS_in_cycle(self, cycle, AS_def='onset'):
    """ for within AS structure
    """
    AS = self.load('AS_timeSet')
    if cycle == '24H':
        return AS
    else:
        tbins = get_CT_bins(bin_type=cycle)
        AS_eff = list()
        for tbin in tbins: 
            bin_start, bin_end = tbin    
            for start, end in AS:
                if (start > bin_start and start < bin_end):
                    AS_eff.append([start, end])

    return np.array(AS_eff)


def get_AS_idx(self):
    """get the all movement in active states, in and out homebase
    """
    T, AS = [self.load(x) for x in ['CT', 'AS_timeSet']]
    idx = np.zeros_like(T, dtype=bool)
    for t in AS:
        idx_start = np.searchsorted(T, t[0])
        idx_end = np.searchsorted(T, t[1], side='right')
        idx[idx_start : idx_end] = True
    return idx



def get_AS_feature_value(self, feat, tbin):
    """ AS features value: AS_probability, AS_onsets, AS_duration 
        for bin_types 24H, DC, LC, 12bins
    """
    AS = self.load('AS_timeSet')
    # AS times (strict), AS onsets in bin, time in bin_effective. ASN, ASD are onset-based
    AS_times, cnt, AS_times_eff, tbin_eff = count_onsets_in_bin(I=AS, tbin=tbin)
    if feat == 'ASP':
        fval = AS_times.sum() / np.diff(tbin).sum()     # ASP in bin (strict)
    else:
        if feat == 'ASN':       # counts, onset-based
            fval = cnt
        elif feat == 'ASD':     # avg duration, onset-based
            fval = 0
            if cnt > 0:
                fval = AS_times_eff.sum() / cnt / 60.    # minutes
    # if tbin.ndim==2:stop
    return fval


def get_AS_vector(self, feat, bin_type='12bins'):
    """returns ASP, ASN, ASD in 12-2hr bins resp. 24H, DC , LC values
        starting at 13 after midnight: 
        bin0: 13.00-15.00 or CT06-08 
    """    
    tbins = get_CT_bins(bin_type, self.experiment.BIN_SHIFT, self.experiment.binTimeShift)       # tbins do not have anything outside CT [6, 30]
    arr = np.zeros(len(tbins))
    b = 0
    for tbin in tbins:
        arr[b] = self.get_AS_feature_value(feat, tbin)
        b +=1  
    return arr


def get_AS_intensity_vector(self, feat, bin_type='12bins', atype='abs'):#, TEST=True):
    """returns array with active state intensity [mg/sec] for 
        feeding, drinking and movement into 11 2hr bins; 
        starting at 15 after midnight: bin0 = 15.00-17.00 = 08-10 CT
        NB. intervals that: 
        -START in CT6-8, END in CT8-10,
        -START in CT28-30, END in CT30-32
        have been removed. this is part of the job of
        getting rid of first bin: 13-15 (1-3pm, CT6-8)
    """
    act = feat[0]
    AS = self.load('AS_timeSet')
    tbins = get_CT_bins(bin_type, self.experiment.BIN_SHIFT, self.experiment.binTimeShift)     
    
    if self.experiment.short_name == '2CFast':            # has a fast day
        if self.dayNumber in self.experiment.fastDayNumbers:
            if act == 'F':
                _, tend = self.experiment.get_food_removal_times()
                # zero food after fast begins     
                idx0 = np.where(AS[:, 1]<=tend)[0]
                AS = AS[idx0]

    arr = np.zeros(len(tbins))
    b = 0
    for tbin in tbins:    
        # get AS times in bins (strict). use tbin_eff if onset-based definition
        AS_times, _, _, _ = count_onsets_in_bin(I=AS, tbin=tbin)
        
        if len(AS_times) > 0:
            # get amounts for each AS, in bin
            if act in ['F', 'W']:
                amounts = self.get_amounts(act, I=AS, tbin=tbin)    # mg
            
            elif act == 'M':               
                _amounts = self.get_move_distances_in_AS_or_Bout(tbin=tbin, move_type='AS')
                # some AS have no move events, but F/W only. correct
                amounts = self.correct_AS_without_move(_amounts, bin_type, bin_num=b)
                # if self.mouseNumber == 7210 and self.dayNumber == 15 and b==1: stop

            np.testing.assert_allclose(len(amounts), len(AS_times), rtol=1e-5)

            arr[b] = get_intensity(amounts, AS_times, atype)    # avg intensity, mg/s
            # if self.mouseNumber == 7250 and self.dayNumber == 12 and b == 0: stop
        b +=1
    return arr






# def get_AS_vector(self, feat, bin_type='12bins'):
#     """returns ASP, ASN, ASD in 12-2hr bins resp. 24H, DC , LC values
#         starting at 13 after midnight: 
#         bin0: 13.00-15.00 or CT06-08 
#     """
#     tbins = get_CT_bins(bin_type, self.experiment.BIN_SHIFT, self.experiment.binTimeShift)       # tbins does not have anything outside CT [6, 30]
#     # print tbins
    
#     if bin_type in ['12bins', '24bins', '24H', 'DC']:
#         arr = np.zeros(len(tbins))
#         b = 0
#         for tbin in tbins:
#             arr[b] = self.get_AS_feature_value(feat, tbin)
#             b +=1  

#     elif bin_type == 'LC':      # disjoint tbins
#         arr = self.get_AS_feature_value(feat, tbins)       

#     return arr


# def get_AS_intensity_vector(self, feat, bin_type='12bins', atype='abs', TEST=True):
#     """returns array with active state intensity [mg/sec] for 
#         feeding, drinking and movement into 11 2hr bins; 
#         starting at 15 after midnight: bin0 = 15.00-17.00 = 08-10 CT
#         NB. intervals that: 
#         -START in CT6-8, END in CT8-10,
#         -START in CT28-30, END in CT30-32
#         have been removed. this is part of the job of
#         getting rid of first bin: 13-15 (1-3pm, CT6-8)
#     """
#     tbins = get_CT_bins(bin_type, self.experiment.BIN_SHIFT, self.experiment.binTimeShift)      
#     AS = self.load('AS_timeSet')

#     act = feat[0]
    
#     if self.experiment.short_name == '2CFast':            # has a fast day
#         if self.dayNumber in self.experiment.fastDayNumbers:
#             if act == 'F':
#                 _, tend = self.experiment.get_food_removal_times()
#                 # zero food after fast begins     
#                 idx0 = np.where(AS[:, 1]<=tend)[0]
#                 AS = AS[idx0]

#     if bin_type in ['12bins', '24bins','24H', 'DC']:
#         arr = np.zeros(len(tbins))
#         b = 0
#         for tbin in tbins:    
#             # get AS times in bins (strict). use tbin_eff if onset-based definition
#             AS_times, _, _, _ = count_onsets_in_bin(I=AS, tbin=tbin)
            
#             if len(AS_times) > 0:
#                 # get amounts for each AS, in bin
#                 if act in ['F', 'W']:
#                     amounts = self.get_amounts(act, I=AS, tbin=tbin)    # mg
                
#                 elif act == 'M':               
#                     _amounts = self.get_move_distances_in_AS_or_Bout(tbin=tbin, move_type='AS')
#                     # some AS have no move events, but F/W only. correct
#                     amounts = self.correct_AS_without_move(_amounts, bin_type, b)
#                     # if self.mouseNumber == 7250 and self.dayNumber == 12 : stop

#                 np.testing.assert_allclose(len(amounts), len(AS_times), rtol=1e-5)

#                 arr[b] = get_intensity(amounts, AS_times, atype)    # avg intensity, mg/s
#                 # if self.mouseNumber == 7250 and self.dayNumber == 12 and b == 0: stop
#             b +=1

#     elif bin_type == 'LC':      # disjoint tbins
#         arr = 0
#         AS_times, _, _, _ = count_onsets_in_bin(I=AS, tbin=tbins)
#         if len(AS_times) > 0:
#             if act in ['F', 'W']:
#                 amounts = self.get_amounts(act, I=AS, tbin=tbins)    # mg
#             elif act == 'M': 
#                 _amounts = self.get_move_distances_in_AS_or_Bout(tbin=tbins, move_type='AS')
#                 # correct for AS without move events
#                 amounts = self.correct_AS_without_move(_amounts, bin_type)

#             np.testing.assert_allclose(len(amounts), len(AS_times), rtol=1e-5)
#             arr = get_intensity(amounts, AS_times, atype)

#     return arr



# review
# # stats
# def get_AS_array(self, feat):
#     """ returns 24H totals for ASP and ASN
#         returns ASD of each AS across 24H
#     """
#     AS = self.load('AS_timeSet')
#     tbin_24h = get_CT_bins(bin_type='24H')
#     num_AS = AS.shape[0]
#     if num_AS > 0:
#         if feat == 'ASP':
#             arr = np.diff(AS).sum() / np.diff(tbin_24h).T[0]
#         elif feat == 'ASN':
#             arr = np.array([num_AS])
#         elif feat == 'ASD':
#             arr = np.diff(AS).T[0] / 60.        #min
#     return arr


# def get_AS_intensity_array(self, feat):
#     """ returns FWM intensity of each AS across 24H
#     """
#     act = feat[0]
#     AS = self.load('AS_timeSet')
#     if act in ['F', 'W']:
#         arr = self.get_intensities(act=act, I=AS)       #mg/s
#     elif act == 'M': 
#         arr = self.get_move_speeds(move_type='AS')                    #cm/s
#     return arr


