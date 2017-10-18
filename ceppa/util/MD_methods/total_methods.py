import numpy as np
from ceppa.util import my_utils
from ceppa.util.intervals import Intervals

"""
G.Onnis, 12.2016
updated: 03.2016

Mouseday Class methods for total amounts computation

Tecott Lab UCSF
"""


def get_total_vector(self, feat, bin_type='12bins'):
    """returns FWM totals in 11 2hr bins vs. 24H, DC , LC values
        starting at 15 after midnight: 
        bin0: 15.00-17.00 or 08-10 CT
        h13-15 after midnight (1-3pm) or CT6-8 is excluded 
    """
    tbins = my_utils.get_CT_bins(bin_type, self.experiment.BIN_SHIFT, self.experiment.binTimeShift)       # tbins does not have anything outside CT [6, 30]
    act = feat[1]

    arr = np.zeros(len(tbins))
    b = 0
    for tbin in tbins:
        # get total in bin (strict)
        if act in ['F', 'W']:
            amounts = self.get_amounts(act=act, tbin=tbin)
            arr[b] = amounts.sum() / 1000    # grams
        elif act == 'M':
            dist = self.get_move_distances(tbin=tbin, move_type='AS')
            arr[b] = dist.sum() / 100.    # meters
        b +=1
    
    return arr


def get_total_array(self, feat):
    """ returns 24h totals
    """
    act = feat[1]
    if act in ['F', 'W']:
        arr = self.get_amounts(act=act) / 1000.     # g
    elif act == 'M':
        arr = np.array([self.get_move_distances(move_type='AS').sum() / 100.])               # meters
    return arr



