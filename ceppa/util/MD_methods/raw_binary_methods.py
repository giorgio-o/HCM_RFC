import numpy as np
from ceppa.util.my_utils import find_nonzero_runs, get_CT_bins 
from ceppa.util.my_utils import pull_locom_tseries_subset, total_time_rectangle_bins
from ceppa.util.intervals import Intervals
from ceppa.util.cage import Cage

"""
G.Onnis, 02.2016
raw HCM binary generation, checks functions

Tecott Lab UCSF
"""


def get_ingestion_uncorrected_events(self, act='F'):
    """loads raw ingestion events as time intervals into (num_events, 2) array 
        w start/stop times.
        set array as MD attribute
    """
    EV = self.PE[1:,:].copy() #seems to always be a photobeam event at the beginning: chop it off (Darren)
    if act == 'W':
        EV = self.LE[1:,:].copy() #seems to always be a photobeam event at the beginning: chop it off (Darren)  
    EV[:,1] += EV[:,0]
    setattr(self, '%s_timeSet_uncorrected' %act, EV)


def index_coordinates_at_devices(self, act='F', xbins=2, ybins=4):
    """computes a boolean array for CT times at which mouse is at F/W device, 
        with (ybins, xbins) cage discretization:
        (0, 0)  top-left (niche)
        (3, 0)  feeder
        (3, 1)  water device
        sets array as MD attribute
        returns array with same shape as CT
    """
    rect = (3, 0)         # depends on cage discretization (ybins, xbins)
    if act == 'W':
        rect = (3, 1)
    tl, tr, bl, br = self.map_xbins_ybins_to_cage(rectangle=rect, xbins=xbins, ybins=ybins)
    # print "Mouse at device location in original coordinates top_left, top_right, bot_left, bot_right: "
    # print tl, tr, bl, br
    # # nest: (0, 0)(-16.25, 43.0) (-6.25, 43.0) (-16.25, 32.5) (-6.25, 32.5)
    if act == 'F':
        less_than_x = tr[0]
        less_than_y = tl[1]
        idx = (self.CX < less_than_x) & (self.CY < less_than_y)
    elif act == 'W':
        more_than_x = tl[0]
        less_than_y = tl[1]
        idx = (self.CX > more_than_x) & (self.CY < less_than_y)
    
    # idx[0] = False      # get rid of problems
    # idx[-1] = False
    setattr(self, 'idx_at_%s' %act, idx)
    return idx


def get_at_device_Set(self, act='F'):
    """computes time intervals at each device cell in a (2, 4) cage 
        discretization.
        accepts act='HB' for niche (0, 0)
        returns array w shape (num_events, 2), start/stop time
    """                
    varNames = ['idx_at_%s' %act, 'CT']        
    try:
        idx, CT = [getattr(self, var) for var in varNames]
    except AttributeError:
        idx, CT = [self.load(var) for var in varNames]
    if act == 'HB':
        idx[-1] = False         # avoid problems
    idx_runs = find_nonzero_runs(idx)
    list_of_times = [[self.CT[start], self.CT[end]] for start, end in idx_runs]
    arr = np.asarray(list_of_times)
    setattr(self, 'at_%s_timeSet' %act, arr)
    return arr


def get_position_bin_times(self, cycle=None, tbin_type=None, xbins=2, ybins=4):
    
    for varName in ['recording_start_stop_time', 'CT', 'CX', 'CY']:
        if not hasattr(self, varName):
            self.load(varName)
    
    # start_time, stop_time = getattr(self, 'recording_start_stop_time')

    # pull corrected loco T, X, Y during this day               
    M = np.vstack([self.CT, self.CX, self.CY])
    
    C = Cage()
    xlims, ylims = (C.CMXLower, C.CMXUpper), (C.CMYLower, C.CMYUpper)

    if tbin_type is not None:
        arr = get_CT_bins(tbin_type=tbin_type.strip('AS'))

        # initialize times for this mouseday and bins
        bin_times = np.zeros((arr.shape[0], ybins, xbins)) 

        if tbin_type == '12bins':
            b = 0
            for tstart, tend in arr: 
                pos_subset = pull_locom_tseries_subset(M, tstart, tend)
                bin_times[b] = total_time_rectangle_bins(pos_subset, xlims=xlims, ylims=ylims, xbins=xbins, ybins=ybins)
                b += 1

        elif tbin_type == 'AS12bins':
            AS = self.load('AS_timeSet')
            b = 0
            for row in arr:
                AS_bin = Intervals(AS).intersect(Intervals(row)).intervals
                for tstart, tend in AS_bin:
                    pos_subset = pull_locom_tseries_subset(M, tstart, tend)
                    bin_times[b] += total_time_rectangle_bins(pos_subset, xlims=xlims, ylims=ylims, xbins=xbins, ybins=ybins)
                b += 1

    else:
        # initialize times for this mouseday and cycle
        bin_times = np.zeros((ybins, xbins)) 

        if cycle == '24H':
            start_time, stop_time = get_CT_bins(tbin_type='3cycles')[0]
            pos_subset = pull_locom_tseries_subset(M, start_time, stop_time)    # does not change M
            # assert((pos_subset==M).all()), 'pos_subset differs from M'
            bin_times = total_time_rectangle_bins(pos_subset, xlims=xlims, ylims=ylims, 
                                                xbins=xbins, ybins=ybins)
        elif cycle == 'IS':
            IS = self.load('IS_timeSet')
            for deltaT in IS:
                pos_subset = pull_locom_tseries_subset(M, deltaT[0], deltaT[1])
                bin_times += total_time_rectangle_bins(pos_subset, xlims=xlims, ylims=ylims, 
                                                xbins=xbins, ybins=ybins)
        
        elif cycle == 'DC':
            DC_start, DC_end = get_CT_bins(tbin_type='3cycles')[1]
            pos_subset = pull_locom_tseries_subset(M, DC_start, DC_end)
            bin_times = total_time_rectangle_bins(pos_subset, xlims=xlims, ylims=ylims, 
                                                xbins=xbins, ybins=ybins)

        elif cycle == 'LC':
            LC1, LC2 = get_CT_bins(tbin_type='3cycles')[2]
            for LC_start, LC_end in [LC1, LC2]:
                pos_subset = pull_locom_tseries_subset(M, LC_start, LC_end)
                btimes = total_time_rectangle_bins(pos_subset, xlims=xlims, ylims=ylims, 
                                                    xbins=xbins, ybins=ybins)
                bin_times += btimes

        else:

            AS, IS = [self.load(x) for x in ['AS_timeSet', 'IS_timeSet']]
            
            if cycle == 'AS24H':
                for deltaT in AS:
                    pos_subset = pull_locom_tseries_subset(M, deltaT[0], deltaT[1])
                    bin_times += total_time_rectangle_bins(pos_subset, xlims=xlims, ylims=ylims, 
                                                xbins=xbins, ybins=ybins)

            else:
                light_phase = cycle.strip('AS')       #DC, LC
                idx = 1 if light_phase == 'DC' else 2
                I = get_CT_bins(tbin_type='3cycles')[idx]
                I_AS = Intervals(AS).intersect(Intervals(I)).intervals
                for deltaT in I_AS:
                    pos_subset = pull_locom_tseries_subset(M, deltaT[0], deltaT[1])
                    bin_times += total_time_rectangle_bins(pos_subset, xlims=xlims, ylims=ylims, 
                                                xbins=xbins, ybins=ybins)
    
    print self
    print "Total bin times, %s, xbins=%d, ybins=%d:" %(cycle, xbins, ybins)
    print bin_times
    assert (bin_times.sum()>=0), "bins_times < 0 !!"
    if bin_times.sum() == 0:
        print "No Activity mouse %d day: %d cycle: %s" %(mouse.mouseNumber, MD.dayNumber, cycle)
    
    if cycle == '24H':      
        setattr(self, 'bin_times_24H_xbins%d_ybins%d' %(xbins, ybins), bin_times)
    return bin_times

    # get total time in this cycle
    # total_time[k_md] = bin_times.sum()

    # # get times at places. valid for (ybins, xbins) = (24, 12) 
    # # WARN: this gives nans when performing 0./0.
    # total_time_places[k_md, 0] = bin_times[-4:, :4].sum() / total_time[k_md]      # feeder: 4x4 bottom-left rectangle, 4x4 large to account for platform errors
    # total_time_places[k_md, 1] = bin_times[-4:, -4:].sum() / total_time[k_md]         # water: 4x4 bottom-right rectangle
    # total_time_places[k_md, 2] = bin_times[:5, -5:].sum() / total_time[k_md]      # top-right corner: 5x5 rectangle, 5x5 same
    # total_time_places[k_md, 3] = bin_times[12:18, 4:8].sum() / total_time[k_md]       # center cage: 6x4 centered rectangle
    # total_time_places[k_md, 4] = bin_times[:6, :6].sum() / total_time[k_md]           # niche: 6x6 top-left rectangle
    
    # if np.isnan(total_time_places[k_md]).any():           # # sanity check for total_time_places. doubles the reality check above
    #   print "----- NaN found, group%d, mouse %d day%d\ntotal_time_places[k_md]: 0. divided by 0. -----" %(group.number, mouse.mouseNumber, MD.dayNumber)
    #   # # convert nans to zeros
    #   total_time_places = np.nan_to_num(total_time_places)
    
    # total_time_places[k_md, 5] = 1 - total_time_places[k_md, :-1].sum()
                    # anywhere else
    # # check again
    # assert (total_time_places[k_md].sum()>.999), "percent_sum < .999 - ?"
