import numpy as np
from intervals import Intervals
import sys

from scipy import stats


"""
G.Onnis, 03.2016
    updated, 06.2017
utils

Tecott Lab UCSF
"""



# # string production
def get_text(cycle=None, tbin_type=None):
    return tbin_type if tbin_type is not None else cycle


def get_tbins_string(bin_type):
    arr = get_CT_bins(bin_type) / 3600 -7
    warr=arr.flatten()
    warr[19:] = [2, 2, 4, 4, 6]
    tbins = ['bin%d: CT%d-%d' %(b, row[0], row[1]) for b, row in enumerate(warr.reshape(arr.shape))]
    return tbins


# print on screen
def print_progress(cnt, tot, obj=None):
    if obj is not None:
        sys.stdout.write("progress.. %1.2f%%\t%s\r" %(100.*cnt/tot, obj))
    else:
        sys.stdout.write("progress.. %1.2f%%\r" %(100.*cnt/tot))
    sys.stdout.flush()



# amounts and intensitites
def get_intensity(amounts, times, atype='abs'):                
    if atype == 'abs':
        intensity = amounts.sum() / times.sum() 
    elif atype == 'avg':
        intensity = (amounts / times).mean() 
    return intensity


# binning

def intersect_arrays(arr1, arr2):
    return Intervals(arr1).intersect(Intervals(arr2)).intervals


def count_onsets_in_bin(I, tbin):
    if tbin.ndim < 2:
        return count_onsets_in_bin_joint(I, tbin)
    return count_onsets_in_bin_disjoint(I, tbin)


def count_onsets_in_bin_joint(I, tbin):
    """for non-disjoint time bin, returns 
        - AS/Bout(I) time in bin, strict sense (intersected with bin)
        - counts, onset-based
        - I effective times in bin, onset-based
        - I effective endpoints in bin, onset-based
    """
    # time in AS/Bout, strictly inside bin
    _I = Intervals(I).intersect(Intervals(tbin)).intervals
    I_times = np.diff(_I).T[0] if len(_I) > 0 else np.array([])

    # effective time in AS/Bout, onset-sensitive
    I_times_eff = []     
    bin_start, bin_end = tbin    
    cnt = 0             # onsets
    for start, end in I:
        if (start > bin_start and start < bin_end):
            I_times_eff.append(end - start)
            if cnt < 1:
                I_start = start
            I_end = end
            cnt +=1
    
    if cnt == 0: 
        np.testing.assert_allclose(np.array(I_times_eff).sum(), 0, rtol=1e-5) 
        return I_times, 0, np.array([]), np.array([])

    tbin_eff = np.array([[I_start, I_end]])     # I endpoints in bin

    return I_times, cnt, np.array(I_times_eff), tbin_eff


def count_onsets_in_bin_disjoint(I, tbins):
    """same for disjoint bin, e.g. LC
    """
    # time in AS/Bout, strictly
    _I = Intervals(I).intersect(Intervals(tbins)).intervals
    I_times = np.diff(_I).T[0] if len(_I) > 0 else np.array([])
    
    # time in AS/Bout, onset-based
    I_times_eff = []   
    cnt = 0            # counts, onset-based
    I_endpoints = []    # I endpoints in bin, onset-based
    for tbin in tbins:
        _, _cnt, _I_times_eff, _tbin_eff = count_onsets_in_bin_joint(I, tbin)
        cnt += _cnt
        if _cnt > 0: 
            I_times_eff.extend(list(_I_times_eff))
            I_endpoints.append(_tbin_eff)
    
    if cnt == 0:
        np.testing.assert_allclose(I_times, 0, rtol=1e-5)
        np.testing.assert_allclose(I_times_eff, 0, rtol=1e-5)
        return np.array([]), 0, np.array([]), np.array([])
    
    if len(I_endpoints) == 1:
        tbin_eff = I_endpoints[0]      # np.array
    elif len(I_endpoints) == 2:
        tbin_eff = np.vstack([I_endpoints[0], I_endpoints[1]])
    
    return I_times, cnt, np.array(I_times_eff), tbin_eff


def wipe_data_outside_CT6_30(I):
    bin_24h = get_CT_bins(bin_type='24H') 
    stop
    return Intervals(I).intersect(Intervals(bin_24h)).intervals     


def get_idx_timestamps_outside_CT6_30(T, SHIFT=False, tshift=0):
    starth, endh = get_CT_bins(tbin_type='3cycles', SHIFT=SHIFT, tshift=tshift)[0]
    return (T >= starth) & (T <= endh)


def get_CT_bins(tbin_type='12bins', SHIFT=False, tshift=0):
    """ returns array with bin intervals for the 24 hours.
        -bin_type='11':
            bin in seconds after midnight, corresponding to hours:
            bin 0: [ 13.  15.]   -   bin 0: [ 6.  8.]  CT time, bin-7hrs
            bin 1: [ 15.  17.]   -   bin 1: [ 8.  10.]  
            bin 2: [ 17.  19.]   -   bin 2: [ 10.  12.]
            ...                      ...
            bin 11:[ 35.  37.]   -   bin 11: [ 10.  12.]
        -bin_type = '24H', 'DC', 'LC': one bin for the 24hrs, one for DC, two for LC
    """
    starth = 13 * 3600.      # startHour: CT6. seconds after midnight. 
    endh = 37 * 3600.        # endhour: CT30-CT6. seconds after midnight.     
    DC_starth = 19 * 3600.     # CT12
    DC_endh = 31 * 3600.       # CT24   

    if SHIFT:
        starth += tshift    
        endh += tshift
    
    if tbin_type == '12bins':
        step = 2 * 3600
    elif tbin_type == '24bins':
        step = 1 * 3600
        
    if tbin_type.endswith('bins'):# in ['12bins', '24bins']:
        tbins = np.array(
                    [[i, i + step] for i in np.arange(starth, endh, step)])
    
    elif tbin_type.endswith('cycles'):
        tbins = [
            np.array([starth, endh]), 
            np.array([DC_starth, DC_endh]),
            np.array([[starth, DC_starth], [DC_endh, endh]])
            ]

    return tbins


def get_CT_xs(bin_type, SHIFT, tshift):
    if bin_type.endswith('bins'):
        tbins = get_CT_bins(bin_type, SHIFT, tshift)[:, 0] / 3600 - 7
        if bin_type == '12bins':
            xs = tbins + 1
        elif bin_type == '24bins':
            xs = tbins + .5
    elif bin_type.endswith('cycles'):
        xs = np.array([1, 2, 3])
    return xs


def get_CT_ticks_labels(bin_type='12bins', SHIFT=False, tshift=0, CUT=True):

    if bin_type.endswith('cycles'):
        return [1.25, 2.25, 3.25], ['24H', 'DC', 'LC']

    elif bin_type.endswith('bins'):
        tbins = get_CT_bins(bin_type, SHIFT, tshift)[:, 0] / 3600 - 7
        
        if bin_type == '12bins':
            xticks = np.hstack([tbins, tbins[-1] + 2])#
            if CUT: # features plot
                xticks = xticks[1::2]
            idx0 = np.where(xticks < 25)[0]
            idx1 = np.where(xticks >= 25)[0]
            if not SHIFT:
                xlabels = [str(int(x)) for x in xticks[idx0]] + \
                            [str(int(x)) for x in (xticks[idx1]-24)]
            else:
                xlabels = ['%1.1f' %x for x in xticks[idx0]] + \
                            ['%1.1f' %x for x in (xticks[idx1]-24)]
                for i in xrange(0, len(xlabels), 2):
                    xlabels[i] = ''

        elif bin_type == '24bins':
            xticks = np.hstack([tbins, tbins[-1] + 1])[::2]
            idx0 = np.where(xticks < 25)[0]
            idx1 = np.where(xticks >= 25)[0]
            xlabels = ['%1.1f' %x for x in xticks[idx0]] + \
                        ['%1.1f' %x for x in (xticks[idx1]-24)]
            for i in xrange(1, len(xlabels), 2):
                xlabels[i] = ''

    return xticks, xlabels




# # others
def print_active_states(self):
    AS, recording_start_stop = [self.load(var) for name in ['AS_timeSet', 'recording_start_stop_time']] 
    print "\n", self
    str1 = '%2d:%2d:%1.2f' %my_utils.convert_CT_time_to_hms_tuple(recording_start_stop[0])
    str2 = '%2d:%2d:%1.2f' % my_utils.convert_CT_time_to_hms_tuple(recording_start_stop[1])
    print "recording start/stop time: \n[%s, %s]"  %(str1, str2)
    # print "recording stop time: " %my_utils.convert_CT_time_to_hms_tuple(recording_start_stop[1])
    print "Active States, CT times:" 
    print my_utils.convert_CT_times_arr2d_to_hms(AS)


def find_nonzero_runs(a):
    # Create an array that is 1 where a is nonzero, and pad each end with an extra 0.
    isnonzero = np.concatenate(([0], (np.asarray(a) != 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(isnonzero))
    # Runs start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges



def convert_hms_tuple_to_CT_time(tup):
    h, m, s = tup
    return 3600 * (h + 7) + 60 * m + s


def convert_CT_time_to_hms_tuple(arr):
    mm, ss = divmod(arr, 60)
    h, m = divmod(mm, 60)
    return h-7, m, ss


def convert_CT_times_arr2d_to_hms(arr):
    """ to print active states T as tuple (h,m,s)
    """    
    # arr = (arr / 3600. -7) * 3600
    new_arr = np.zeros([2, 1])
    for start, end in arr:
        str1 = ["%d:%02d:%02.2f" %convert_CT_time_to_hms_tuple(start)]
        str2 = ["%d:%02d:%02.2f" %convert_CT_time_to_hms_tuple(end)]
        new_arr = np.hstack([new_arr, [str1, str2]])
    return new_arr[:, 1:].T


def get_window_CT_idx(arr, twindow):
    idx_start = np.searchsorted(arr, twindow[0]) 
    idx_end = np.searchsorted(arr, twindow[1], side='right')
    win_idx = np.zeros(arr.shape, dtype=bool)
    win_idx[idx_start : idx_end] = True
    return win_idx
        

# position density

def pull_locom_tseries_subset(M, start_time=0, stop_time=300):
    """
        given an (m x n) numpy array M where the 0th row is array of times [ASSUMED SORTED]
        returns a new array (copy) that is a subset of M corresp to start_time, stop_time

        returns [] if times are not in array

        (the difficulty is that if mouse does not move nothing gets registered
         so we should artificially create start_time, stop_time movement events at boundries)
    """
    T = M[0]
    idx_start = T.searchsorted(start_time)
    idx_stop = T.searchsorted(stop_time)
    new_M = M[:,idx_start:idx_stop].copy()
    if idx_stop != T.shape[0]:
        if (idx_start != 0) and (T[idx_start] != start_time):
            v = np.zeros(M.shape[0])
            v[1:] = M[1:, idx_start - 1].copy()
            v[0] = start_time
            v = v.reshape((M.shape[0], 1))
            new_M = np.hstack([v, new_M])
        if (T[idx_stop] != stop_time) and (idx_stop != 0):
            v = np.zeros(M.shape[0])
            v[1:] = M[1:,idx_stop - 1].copy()  # find last time registered
            v[0] = stop_time
            v =  v.reshape((M.shape[0], 1))
            new_M = np.hstack([new_M, v])
        elif (T[idx_stop] == stop_time):
            v = M[:, idx_stop].copy().reshape((M.shape[0], 1))
            new_M = np.hstack([new_M, v])
    else:
        pass
    return new_M


def total_time_rectangle_bins(M, xlims=(0,1), ylims=(0,1), xbins=5, ybins=10):
    """
    given an (3 x n) numpy array M where the 0th row is array of times [ASSUMED SORTED]
    returns a new (xbins x ybins) array (copy) that contains PDF of location over time
    """
    xmin,xmax = xlims
    ymin,ymax = ylims
    meshx = xmin + (xmax - xmin) * 1. * np.array(range(1, xbins + 1)) / xbins
    meshy = ymin + (ymax - ymin) * 1. * np.array(range(1, ybins + 1)) / ybins

    Cnts = np.zeros((ybins, xbins))
    if M.shape[0] <= 1:
        return Cnts

    bin_idx = meshx.searchsorted(M[1, :], side='right')
    bin_idy = meshy.searchsorted(M[2, :], side='right')
    for k in xrange(M.shape[1] - 1):
        if bin_idx[k] == xbins:
            bin_idx[k] -= 1
        if bin_idy[k] == ybins:
            bin_idy[k] -= 1
        Cnts[ybins - bin_idy[k] - 1, bin_idx[k]] += M[0,k+1] - M[0,k]
    return Cnts



# data averaging
def get_num_items(E, level, days=None):
    num_items = E.num_strains
    if level == 'mouse':
        num_items = E.num_mice_ok
    elif level == 'mouseday':
        days_to_use = E.daysToUse if days is None else days
        _, num_md_ok = E.count_mousedays(days=days_to_use)
        num_items = num_md_ok
    print "level: %s, num_items: %d" %(level, num_items)
    stop
    return num_items


def get_1d_expdays_averages_errors_12bins(E, data, labels, level, err_type):

    if level == 'group':
        # swap to (mousedays, features, 12bins, avg)
        new_data = data.swapaxes(0, 1)[:, :, :, 0]      

        days_to_use = np.unique(labels[:, 2])
        np.testing.assert_array_almost_equal(days_to_use, np.array(E.daysToUse), decimal=5)
        num_features = new_data.shape[1]
        num_bins = new_data.shape[2]

        arr = np.zeros((E.num_strains, num_features, len(days_to_use), num_bins, 2))      # avg, err
        for group in xrange(E.num_strains):
            idx = labels[:, 0] == group
            group_data, group_labels = new_data[idx], labels[idx]

            d = 0
            for day in days_to_use:
                idx2 = group_labels[: , 2] == day
                arr[group, :, d, :, 0] = np.nanmean(group_data[idx2], axis=0)
                if err_type == 'sd':
                    arr[group, :, d, :, 1] = np.nanstd(group_data[idx2], axis=0)
                elif err_type == 'sem':
                    arr[group, :, d, :, 1] = np.nanstd(group_data[idx2], axis=0) \
                                        / np.sqrt(np.nansum(idx2) - 1)
                d+=1
    
    return arr


def get_1d_expdays_averages_errors_24H(E, data, labels, level, err_type):

    if level == 'group':
        # swap to (mousedays, features, 24H/DC/LC, avg)
        new_data = data.swapaxes(0, 1)[:, :, :, 0]      
         
        days_to_use = np.unique(labels[:, 2])
        np.testing.assert_array_almost_equal(days_to_use, np.array(E.daysToUse), decimal=5)
        num_features = new_data.shape[1]

        arr = np.zeros((E.num_strains, num_features, len(days_to_use), 3, 2))      # avg, err
        for group in xrange(E.num_strains):
            idx = labels[:, 0] == group
            group_data, group_labels = new_data[idx], labels[idx]

            d = 0
            for day in days_to_use:
                idx2 = group_labels[: , 2] == day
                arr[group, :, d, :, 0] = np.nanmean(group_data[idx2], axis=0)
                if err_type == 'sd':
                    arr[group, :, d, :, 1] = np.nanstd(group_data[idx2], axis=0)
                elif err_type == 'sem':
                    arr[group, :, d, :, 1] = np.nanstd(group_data[idx2], axis=0) \
                                        / np.sqrt(np.nansum(idx2) - 1)

                d+=1
    
    return arr


def get_1d_expdays_averages_errors_DC_LC(E, data, labels, level, err_type):

    if level == 'group':
        # swap to (mousedays, features, 24H/DC/LC, avg)
        new_data = data.swapaxes(0, 1)      
         
        days_to_use = np.unique(labels[:, 2])
        np.testing.assert_array_almost_equal(days_to_use, np.array(E.daysToUse), decimal=5)
        num_features = new_data.shape[1]

        arr = np.zeros((E.num_strains, num_features, len(days_to_use), 2))      # avg, err
        for group in xrange(E.num_strains):
            idx = labels[:, 0] == group
            group_data, group_labels = new_data[idx], labels[idx]

            d = 0
            for day in days_to_use:
                idx2 = group_labels[: , 2] == day
                arr[group, :, d, 0] = np.nanmean(group_data[idx2], axis=0)
                if err_type == 'sd':
                    arr[group, :, d, 1] = np.nanstd(group_data[idx2], axis=0)
                elif err_type == 'sem':
                    arr[group, :, d, 1] = np.nanstd(group_data[idx2], axis=0) \
                                        / np.sqrt(np.nansum(idx2) - 1)

                d+=1
    
    return arr

    
def get_1d_averages_errors(E, data, labels, level='mouseday', err_type='sd',
        group_avg_type='over_mds'):
    """ 
    """
    if level == 'mouseday':
        # add array with zero error
        data_ = np.tile(np.zeros_like(data[:, :, np.newaxis]), (1,1,2))
        data_[:, :, 0] = data
        return data_, labels

    num_bins = data.shape[1]

    # initialize arrays
    s_data = np.zeros((E.num_strains, num_bins, 2))  # avgs, stdev/stderr
    s_labels = np.zeros(E.num_strains, dtype=int)
    m_data = np.zeros((E.num_mice, num_bins, 2))  
    m_labels = np.zeros((E.num_mice, 2), dtype=int)
    
    cnt = 0
    for strain in xrange(E.num_strains):
        
        idx = labels[:, 0] == strain
        m_labels_ = np.unique(labels[idx, 1])
        num_mice = len(m_labels_)

        for m_label in m_labels_:
            idx2 = labels[:, 1] == m_label
            num_mdays = np.nansum(idx2)

            m_data[cnt, :, 0] = np.nanmean(data[idx2], axis=0)
            if err_type == 'sd':
                m_data[cnt, :, 1] = np.nanstd(data[idx2], axis=0)
            elif err_type == 'sem':
                m_data[cnt, :, 1] = np.nanstd(data[idx2], axis=0) \
                                    / np.sqrt(num_mdays - 1)
                # stats.sem(data[idx2], axis=0)
            m_labels[cnt] = strain, m_label
            cnt +=1 
            
        # two possible defs of strain avg. 
        if group_avg_type == 'over_mds':
            # over all mds
            s_data[strain, :, 0] = np.nanmean(data[idx], axis=0)        
            if err_type == 'sd':
                s_data[strain, :, 1] = np.nanstd(data[idx], axis=0)         
            if err_type == 'sem':
                s_data[strain, :, 1] = np.nanstd(data[idx], axis=0) \
                                        / np.sqrt(num_mice - 1)
                # stats.sem(data[idx], axis=0)
            s_labels[strain] = strain         #labels

    if group_avg_type == 'over_mice':
        #or, over mice
        for strain in xrange(E.num_strains):
            idx = m_labels[:, 0] == strain
            s_data[strain, :, 0] = np.nanmean(m_data[0, idx], axis=0) 
            if err_type == 'sd':       
                s_data[strain, :, 1] = np.nanstd(m_data[0, idx], axis=0)
            if err_type == 'sem':
                s_data[strain, :, 1] = np.nanstd(m_data[0, idx], axis=0) \
                                        / np.sqrt(num_mice - 1)
                # stats.sem(m_data[0, idx], axis=0)
            s_labels[strain] = strain          #labels
    
    return (s_data, s_labels) if level == 'group' else (m_data, m_labels)


def get_2d_averages_errors(E, data, labels, tbin_type=None, level='mouseday', err_type='sd',
        group_avg_type='over_mds'):
    """ excludes ignored mice
    """

    if tbin_type is not None:
        if level == 'mouseday':
            data_ = np.tile(np.zeros_like(data[:, :, :, :, np.newaxis]), (1, 1,1,1,2))
            data_[:, :, :, :, 0] = data            
            return data_, labels
        # stop
        num_tbins, ybins, xbins = data.shape[-3], data.shape[-2], data.shape[-1]

        # initialize arrays
        s_data = np.zeros((E.num_strains, num_tbins, ybins, xbins, 2))     # avgs, stdev/stderr
        s_labels = np.zeros(E.num_strains, dtype=int)
        m_data = np.zeros((E.num_mice, num_tbins, ybins, xbins, 2))  
        m_labels = np.zeros((E.num_mice, 2), dtype=int)
        
        cnt = 0
        for strain in xrange(E.num_strains):

            idx = labels[:, 0] == strain
            m_labels_ = np.unique(labels[idx, 1])
            
            for m_label in m_labels_:
                idx2 = labels[:, 1] == m_label
                
                for b in xrange(num_tbins):
                    m_data[cnt, b, :, :, 0] = np.nanmean(data[idx2, b], axis=0)
                    if err_type == 'sd':
                        m_data[cnt, b, :, :, 1] = np.nanstd(data[idx2, b], axis=0)
                    elif err_type == 'sem':
                        m_data[cnt, b, :, :, 1] = np.nanstd(data[idx2, b], axis=0) \
                                                / np.sqrt(np.nansum(idx2) - 1)
                        # stats.sem(data[idx2], axis=0)
                        # data[idx2].std(axis=0) / np.sqrt(idx2.sum() - 1)
                m_labels[cnt] = strain, m_label
                cnt += 1

            if level == 'group':
                # strain avgs over mds
                for b in xrange(num_tbins):
                    s_data[strain, b, :, :, 0] = np.nanmean(data[idx, b], axis=0)
                    if err_type == 'sd':
                        s_data[strain, b, :, :, 1] = np.nanstd(data[idx, b], axis=0)
                    elif err_type == 'sem':
                        s_data[strain, b, :, :, 1] = np.nanstd(data[idx, b], axis=0) \
                                                    / np.sqrt(np.nansum(idx) - 1)
                    # stats.sem(data[idx], axis=0)
                    # data[idx].std(axis=0) / np.sqrt(len(m_labels) - 1)
                s_labels[strain] = strain
    
    else:
        if level == 'mouseday':
            # stack array with zero error on last axis
            data_ = np.tile(np.zeros_like(data[:, :, :, np.newaxis]), (1,1,1,2))
            data_[:, :, :, 0] = data
            return data_, labels

        ybins, xbins = data.shape[-2], data.shape[-1]

        # initialize arrays
        s_data = np.zeros((E.num_strains, ybins, xbins, 2))     # avgs, stdev/stderr
        s_labels = np.zeros(E.num_strains, dtype=int)
        m_data = np.zeros((E.num_mice, ybins, xbins, 2))  
        m_labels = np.zeros((E.num_mice, 2), dtype=int)
        
        cnt = 0
        for strain in xrange(E.num_strains):

            idx = labels[:, 0] == strain
            m_labels_ = np.unique(labels[idx, 1])
            
            for m_label in m_labels_:
                idx2 = labels[:, 1] == m_label
                m_data[cnt, :, :, 0] = np.nanmean(data[idx2], axis=0)
                if err_type == 'sd':
                    m_data[cnt, :, :, 1] = np.nanstd(data[idx2], axis=0)
                elif err_type == 'sem':
                    m_data[cnt, :, :, 1] = np.nanstd(data[idx2], axis=0) \
                                            / np.sqrt(np.nansum(idx2) - 1)
                    # stats.sem(data[idx2], axis=0)
                    # data[idx2].std(axis=0) / np.sqrt(idx2.sum() - 1)
                m_labels[cnt] = strain, m_label
                cnt += 1

            if level == 'group':
                # strain avgs over mds
                s_data[strain, :, :, 0] = np.nanmean(data[idx], axis=0)
                if err_type == 'sd':
                    s_data[strain, :, :, 1] = np.nanstd(data[idx], axis=0)
                elif err_type == 'sem':
                    s_data[strain, :, :, 1] = np.nanstd(data[idx], axis=0) \
                                            / np.sqrt(np.nansum(idx) - 1)
                # stats.sem(data[idx], axis=0)
                # data[idx].std(axis=0) / np.sqrt(len(m_labels) - 1)
                s_labels[strain] = strain
    
    return (s_data, s_labels) if level == 'group' else (m_data, m_labels)



def list_avg(x):
    x = filter(None, x)
    return sum(x, 0.0) / len(x) if len(x) > 0 else 0.

def list_std(x):
    x = filter(None, x)
    return np.array(x).std() if len(x) > 0 else 0.

def list_sem(x):
    return list_std(x) / np.sqrt(len(x)-1) if len(x) > 1 else list_std(x)

def pad_list(E, data, days, pad_value=np.nan):
    days_to_use = E.daysToUse if days is None else days
    max_as = max(E.get_max_AS(days=days_to_use))
    new_data = [[], [], []]
    for v, vals in enumerate(data):
        for row in vals:
            new_data[v].append(row + [pad_value] * (max_as - len(row)))

    return np.array(new_data)


# def get_1d_list_mouse_strain_averages(E, data, labels, days=None, group_avg_type='over_mds'):
#     """ given a 2D array (num_mousedays, num_bins) with values, returns array
#         data[0] = averages
#         data[1] = stdevs
#         data[2] = stderrs
#         for all legit mousedays, mice, strains values and labels,
#     """
#     from itertools import izip_longest, imap

#     s_labels = np.zeros(E.num_strains, dtype=int)
#     m_labels = np.zeros((E.num_mice_ok, 2), dtype=int)
    
#     strain_data = [[], [], []]
#     all_mice_data = [[], [], []]
#     cnt = 0
#     for group in E.groups:
#         mouse_labels, _ = group.count_mice()
#         mouse_data = [[], [], []]
#         for m, mouse in enumerate(mouse_labels):
#             idx2 = labels[:, 1] == mouse
#             data_list = [data[i].tolist() for i in np.where(idx2==True)[0]]
#             mouse_data[0].append(map(list_avg, izip_longest(*data_list)))    # pads with None for missing values
#             mouse_data[1].append(map(list_std, izip_longest(*data_list)))
#             mouse_data[2].append(map(list_sem, izip_longest(*data_list)))
#             m_labels[cnt] = group.number, mouse
#             cnt +=1 
#             # if np.isnan(mouse_data[0])
        
#         all_mice_data[0].extend(mouse_data[0])
#         all_mice_data[1].extend(mouse_data[1])
#         all_mice_data[2].extend(mouse_data[2])

#         # strain avg. 
#         if group_avg_type == 'over_mds':
#             # over all mds
#             idx = labels[:, 0] == group.number
#             strain_data[0].append(map(list_avg, izip_longest(*mouse_data[0])))
#             strain_data[1].append(map(list_std, izip_longest(*mouse_data[1])))
#             strain_data[2].append(map(list_sem, izip_longest(*mouse_data[2])))
#             s_labels[group.number] = group.number          #labels

#     m_data = pad_list(E, all_mice_data, days)
#     s_data = pad_list(E, strain_data, days)

#     return s_data, s_labels, m_data, m_labels



# def get_mouse_strain_averages_expdays(experiment, data, labels, days=None, group_avg_type='over_mds'):
#     E = experiment
#     num_strains = E.num_strains
#     num_bins = data.shape[1]
#     num_days = len(E.daysToUse) if days is None else len(days)
#     s_data = np.zeros((3, num_strains, num_days, num_bins))   # avgs, stdev, stderr
#     s_labels = np.zeros(num_strains, dtype=int)
#     m_data = np.zeros((num_mice_ok, num_days, num_bins))  
#     m_labels = np.zeros((num_mice_ok, 2), dtype=int)
#     cnt = 0
#     for group in E.groups:
#         _m_labels, _ = group.count_mice()
#         _avg = []
#         for m_label in _m_labels:
#             idx2 = labels[:, 1] == m_label
#             m_data[cnt] = data[idx2]
#             _avg.append(data[idx2])
#             m_labels[cnt] = group.number, m_label
#             cnt +=1 

#         #avg over mice
#         avg = np.array(_avg)
#         s_data[0, group.number] = np.nanmean(avg, axis=0)        #avg
#         s_data[1, group.number] = np.nanstd(avg, axis=0)         #stdev
#         # s_data[2, group.number] = np.nanstd(avg, axis=0) / np.sqrt(len(avg) - 1)    #stderr
#         s_labels[group.number] = group.number          #labels
#     return s_data, s_labels, m_data, m_labels


# def get_mouse_strain_averages_day_by_day(experiment, data, labels, days=None, group_avg_type='over_mds'):
    
#     E = experiment
#     num_strains = E.num_strains
#     num_mice = E.num_mice_ok
#     num_bins = data.shape[1]
#     num_days = len(E.daysToUse) if days is None else len(days)
    
#     s_data = np.zeros((3, num_strains, num_days * num_bins))   # avgs, stdev, stderr
#     s_labels = np.zeros(num_strains, dtype=int)
#     m_data = np.zeros((num_mice, num_days * num_bins))
#     m_labels = np.zeros((num_mice, 2), dtype=int)     # group, mouse
    
#     cnt = 0
#     for group in E.groups:
#         _m_labels, _ = group.count_mice()
#         _avg = []
#         for m_label in _m_labels:
#             idx2 = labels[:, 1] == m_label
#             m_data[cnt] = data[idx2].ravel()
#             m_labels[cnt] = group.number, m_label
#             _avg.append(m_data[cnt])
#             cnt += 1
        
#         #avg over mice
#         avg = np.array(_avg)
#         # if group.number == 0: stop
#         s_data[0, group.number] = np.nanmean(avg, axis=0)        #avg
#         s_data[1, group.number] = np.nanstd(avg, axis=0)         #stdev
#         # s_data[2, group.number] = np.nanstd(avg, axis=0) / np.sqrt(len(avg) - 1)    #stderr
#         s_labels[group.number] = group.number          #labels
    
#     return s_data, s_labels, m_data, m_labels






# def day_to_mouse_average_pos_dens(experiment, data, labels):
#     """ Input: mouseday values num_mousedays x xbins x ybins (seconds), labels. 
#         Returns: new data matrix with average percent times for each mouse 
#         over mouse days. 
#     """
#     E = experiment
#     tot_data_avgs = np.zeros((1, data.shape[1], data.shape[2]))
#     tot_data_std = np.zeros((1, data.shape[1], data.shape[2]))
#     tot_data_stderr = np.zeros((1, data.shape[1], data.shape[2]))
#     new_labels = np.array((1, 2))       # unsorted
#     mouse_order = {i: [] for i in xrange(E.num_strains)}
#     for strain in xrange(E.num_strains):
#         mice = {}
#         idx1 = labels[:, 0] == strain
#         tmp_data = data[idx1, :]
#         for i in xrange(tmp_data.shape[0]):
#             idx2 = labels[idx1, 1]
#             if mice.has_key(idx2[i]):
#                 mice[idx2[i]] += 1
#             else:
#                 mouse_order[strain].append(idx2[i])
#                 mice[idx2[i]] = 1
        
#         data_avgs = np.zeros((len(mice), data.shape[1], data.shape[2]))
#         data_std = np.zeros((len(mice), data.shape[1], data.shape[2]))
#         data_stderr = np.zeros((len(mice), data.shape[1], data.shape[2]))
#         tmp_label = np.zeros((len(mice), 2))
#         for c, num in enumerate(mice.keys()):
#             # print num
#             mouse_arr = data[labels[:,1]==num]
#             mouse_perc = np.zeros_like(mouse_arr)
#             for m in xrange(mouse_arr.shape[0]):
#                 mouse_perc[m] = mouse_arr[m] / mouse_arr[m].sum()

#             data_avgs[c] = mouse_perc.mean(axis=0)
#             data_std[c] = mouse_perc.std(axis=0)
#             data_stderr[c] = mouse_perc.std(axis=0) / np.sqrt(mouse_arr.shape[0] - 1)
#             tmp_label[c] = strain, num

#         tot_data_avgs = np.vstack([tot_data_avgs, data_avgs])
#         tot_data_std = np.vstack([tot_data_std, data_std])
#         tot_data_stderr = np.vstack([tot_data_stderr, data_stderr])
#         new_labels = np.vstack([new_labels, tmp_label])
        
#     # re-sort mice in correct order
#     tot_arr = tot_data_avgs[1:, :]
#     tot_arr1 = tot_data_std[1:, :]
#     tot_arr2 = tot_data_stderr[1:, :]
#     new_tot_data_avgs = np.zeros(tot_arr.shape)
#     new_tot_data_std = np.zeros(tot_arr.shape)
#     new_tot_data_stderr = np.zeros(tot_arr.shape)

#     new_labels = new_labels[1:, :]
#     ordered_labels = np.zeros(new_labels.shape)
#     cnt = 0
#     for strain in xrange(0, E.num_strains):
#         mice = mouse_order[strain]
#         tmp_labels = new_labels[new_labels[:, 0]==strain, :]
#         tmp_data = tot_arr[new_labels[:, 0]==strain, :]
#         tmp_data1 = tot_arr1[new_labels[:, 0]==strain, :]
#         tmp_data2 = tot_arr2[new_labels[:, 0]==strain, :]
#         for i in xrange(len(mice)):
#             new_tot_data_avgs[cnt] = tmp_data[tmp_labels[:, 1] == mice[i]][0]#.ravel()
#             new_tot_data_std[cnt] = tmp_data1[tmp_labels[:, 1] == mice[i]][0]#.ravel()
#             new_tot_data_stderr[cnt] = tmp_data2[tmp_labels[:, 1] == mice[i]][0]#.ravel()
#             ordered_labels[cnt] = strain, mice[i]
#             cnt += 1
#     M = np.zeros((3, new_tot_data_avgs.shape[0], new_tot_data_avgs.shape[1], new_tot_data_avgs.shape[2]))
#     M[0], M[1], M[2] = new_tot_data_avgs, new_tot_data_std, new_tot_data_stderr
#     return M, ordered_labels


# def mouse_to_strain_average_pos_dens(experiment, data, labels):
#     """ Returns: new data matrix with mean percent time for each strain over mice 
#     """
#     E = experiment
#     tot_data = np.zeros_like(data)
#     for strain in xrange(E.num_strains):
#         tmp_data = data[labels[:, 0]==strain, :]
#         tot_data[0, strain] = tmp_data.mean(axis=0)
#         tot_data[1, strain] = tmp_data.std(axis=0)
#         tot_data[2, strain] = tmp_data.std(axis=0) / np.sqrt(tmp_data.shape[0] - 1)     # standard error for plotting    
#     return tot_data_avgs



# #
# 

# # # # # tests
# def test_pull_locom():
#     M = np.array([[1,2,3,4,5,6],[8,7,6,5,5,4],[-1,3,4,1,1,4]])
    
#     M_ = np.array([[1,2,3,4],[8,7,6,5],[-1,3,4,1]])
#     Mnew = pull_locom_tseries_subset(M, start_time=1, stop_time=4)
#     np.testing.assert_allclose(Mnew,M_)
    
#     M_ = np.array([[1,2,3,3.4],[8,7,6,6],[-1,3,4,4]])
#     Mnew = pull_locom_tseries_subset(M, start_time=1, stop_time=3.4)
#     np.testing.assert_allclose(Mnew,M_)
    
#     M_ = np.array([[1.2,2,3,3.4],[8,7,6,6],[-1,3,4,4]])
#     Mnew = pull_locom_tseries_subset(M, start_time=1.2, stop_time=3.4)
#     np.testing.assert_allclose(Mnew,M_)
    
#     M_ = np.array([[1,2,3,4,5],[8,7,6,5,5],[-1,3,4,1,1]])
#     Mnew = pull_locom_tseries_subset(M, start_time=0, stop_time=5)
#     np.testing.assert_allclose(Mnew,M_)
    
#     M_ = np.array([[1.2,1.5],[8,8],[-1,-1]])
#     Mnew = pull_locom_tseries_subset(M, start_time=1.2, stop_time=1.5)
#     np.testing.assert_allclose(Mnew,M_)

#     Mnew = pull_locom_tseries_subset(M, start_time=1, stop_time=7)
#     np.testing.assert_allclose(Mnew,M)
    

# def test_total_time():
#     M = np.array([[1,2,3],[.5,.1,.1],[.3,.4,.6]])
#     TT = total_time_rectangle_bins(M,xbins=2,ybins=2)
#     np.testing.assert_allclose(TT,[[ 0.,   0.],[ 1.,  1.]])

#     M = np.array([[1,2,3],[.5,.6,.1],[.3,.4,.6]])
#     TT = total_time_rectangle_bins(M,xbins=3,ybins=5)
#     np.testing.assert_allclose(TT,[[ 0.,  0.,  0.], [ 0.,  0.,  0.], [ 0.,  1.,  0.], [ 0.,  1.,  0.], [ 0.,  0.,  0.]])

#     M = np.array([[1,2,3,4,5,6],[.51,.61,.11,.81,.21,.3],[.3,.41,.6,.1,.1,.1]])
#     TT = total_time_rectangle_bins(M,xbins=3,ybins=5)
#     np.testing.assert_allclose(TT, [[ 0.,  0.,  0.],[ 1.,  0.,  0.],[ 0. , 1. , 0.],[ 0.,  1.,  0.],[ 1.,  0.,  1.]])
    
#     M = np.array([[1,2],[.5,.5],[.3,.3]])
#     TT = total_time_rectangle_bins(M,xbins=3,ybins=5)
#     np.testing.assert_allclose(TT, [[ 0.,  0.,  0.], [ 0.,  0.,  0.], [ 0.,  0.,  0.], [ 0.,  1.,  0.], [ 0.,  0.,  0.]])


# from sklearn import preprocessing
# from sklearn.model_selection import train_test_split

# # # ML
# def get_dataset_two_strains_and_shuffle(arr, arr_labels, strain1=0, strain2=1, SCALE=True):
#     idx1 = arr_labels[:, 0] == strain1
#     idx2 = arr_labels[:, 0] == strain2
#     data = np.vstack([arr[idx1], arr[idx2]])
#     labels = np.hstack([arr_labels[idx1, 0], arr_labels[idx2, 0]])
#     newarr = np.hstack([data, labels[:, np.newaxis]])
#     np.random.seed(0)
#     np.random.shuffle(newarr)
#     X = newarr[:, :-1]
#     Y = (newarr[:, -1]).astype(int)
#     if SCALE:
#         X = preprocessing.scale(X)
#     return X, Y


# def split_half_dataset(arr, arr_labels):
#     return train_test_split(arr, arr_labels[:, 0], train_size=0.5)


# # # # #general use
# def timestamps_to_interval(array, eps=.01):
#     """ given a 1D array with event timestamps, returns an interval centered
#         on timestamp and eps wide. 
#         default 0.01 is half of minimum HCM sampling rate 
#     """
#     new_arr = zip(array - eps, array + eps)
#     new_I = Intervals(new_arr)   
#     return new_I

# def split_data_in_half_randomly(features, labels):
#     """ given an array of the form:
#             features = M x A x B x C x ...
#         where M is the number of mouse days

#         and an array labels for this data of the form:
#             labels = M x 2
#         where labels[:, 0] are strain numbers and the labels[:, 1] are mice numbers

#         returns 
#             bootstrap_data_1 = a random half of the mouse days
#             bootstrap_labels_1
#             bootstrap_data_2 = the other half
#             bootstrap_labels_2
#     """
#     all_perm_data = np.zeros(features.shape)
#     all_perm_labels = np.zeros(labels.shape)
#     strains = list(set(labels[:, 0]))
#     c = 0

#     for strain in strains:
#         sub_data = features[labels[:, 0] == strain]
#         sub_labels = labels[labels[:, 0] == strain]
#         mice_nums = {}

#         for i in xrange(len(sub_data)):
#             mice_nums[sub_labels[i, 1]] = 1

#         for mouse in mice_nums.keys():
#             # print strain, mouse
#             tmp = sub_data[sub_labels[:, 1] == mouse]
#             tmp_l = sub_labels[sub_labels[:, 1] == mouse]
#             # print tmp, tmp_l
#             perm = np.random.permutation(len(tmp))
#             all_perm_data[c:c + len(tmp)] = tmp[perm]
#             all_perm_labels[c:c + len(tmp_l)] = tmp_l[perm]
#             c += len(tmp)        

#     return all_perm_data[::2], all_perm_labels[::2], all_perm_data[1::2], all_perm_labels[1::2]





