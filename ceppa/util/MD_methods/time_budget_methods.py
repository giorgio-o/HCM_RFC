import numpy as np
from scipy import stats

import os

from ceppa.util.intervals import Intervals
from ceppa.util.my_utils import get_CT_bins, intersect_arrays

"""
G.Onnis, 06.2017

Tecott Lab UCSF
"""



def get_time_budgets(self, cycle, num_items):

    var = ['recording_start_stop_time', 'AS_timeSet', 
            'FB_timeSet', 'WB_timeSet', 'MB_timeSet', 
            'IS_timeSet'
            ]
    rec, AS, F, W, M, IS = [self.load(x) for x in var]

    C = get_CT_bins(bin_type=cycle)         # ignoring maintenance time
    time = np.diff(C).sum()
    
    if cycle in self.experiment.cycles:
    
        if cycle == '24H':
            tas, tf, tw, tm, tis = [np.diff(x).sum() for x in [AS, F, W, M, IS]]
        
        elif cycle in ['DC', 'LC']:
            AS, F, W, M, IS = [intersect_arrays(x, C) for x in [AS, F, W, M, IS]]
            tas, tf, tw, tm, tis = [np.diff(x).sum() for x in [AS, F, W, M, IS]]

        elif cycle in ['AS24H', 'ASDC', 'ASLC']:
            stop
        
        FWM_union = Intervals(M).union(Intervals(F)).union(Intervals(W))        
        other = Intervals(AS).intersect(~FWM_union).measure()

    arr = np.array([tm, tf, tw, other, tis])
    assert arr.sum() - time < 300, '%s %s screwed' %(MD, cycle)      # allow 5 minutes differences

    return arr


