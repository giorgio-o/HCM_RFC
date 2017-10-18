""" Finite Union of Intervals

Darren Rhea, 2012
Chris Hillar revised, April 30, 2013
Ram Mehta revised, 2013
Copyright (c) 2013. All rights reserved.
Chris Hillar revised, 2015

Implements a class to handle finite (disjoint) unions of intervals.

* assumes that intervals are always closed and that the union is disjoint
* open intervals remaining at the end of any operations (eg. complement) 
* are always made closed.  e.g. [0,1]^C = [-np.inf,0] [1,np.inf]
* end intervals being unbounded is handled using -np.inf and np.inf
* does some okay handling for point intervals [a,a]
"""
import numpy as np


class Intervals(object):
    """ Finite Union of Intervals [ai,bi] backed by sorted lists.

    parameters
        intervals: (M x 2) numpy np.double array
    """
    def __init__(self, intervals=None):
        if intervals is None or len(intervals) == 0:
            self.intervals = np.array([])
            return
        intervals = np.atleast_2d(np.asarray(intervals))
        idx = intervals[:, 0].argsort()
        self.intervals = intervals[idx, :]
        if not self._is_disjoint():
            self._make_disjoint()

    def __iter__(self):
        return iter(self.intervals)

    def __len__(self):
        return self.measure()

    def __str__(self):
        if self.is_empty():
            return "EmptySet"
        ivt = self.intervals
        return " ".join(["[%s,%s]" % (ivt[i, 0], ivt[i, 1]) for i in xrange(ivt.shape[0])])

    def __add__(self, F):
        return self.union(F)

    def __mul__(self, F):
        return self.intersect(F)

    def __sub__(self, F):
        return self.remove(F)

    def __invert__(self):
        return self.complement()

    def _is_disjoint(self):
        """ Checks if intervals are indeed disjoint """
        self.intervals = np.atleast_2d(self.intervals)
        if (self.intervals is None) or (self.intervals.shape[0] < 2):
            return True
        return ((self.intervals[:-1, 1] < self.intervals[1:, 0]).all() and \
            (self.intervals[:, 1] >= self.intervals[:,0]).all())

    def _make_disjoint(self):
        """ Remove intervals [a, b] with a > b """
        good_intervals_idx = self.intervals[:, 1]>=self.intervals[:, 0]
        self.intervals = self.intervals[good_intervals_idx, :]
        # union together intervals that overlap
        tot = None
        curr_idx = 0
        curr_lhs = self.intervals[curr_idx, 0]
        curr_rhs = self.intervals[curr_idx, 1]
        while curr_idx < self.intervals.shape[0]:
            while curr_rhs >= self.intervals[curr_idx, 0]:
                curr_rhs = max(curr_rhs,self.intervals[curr_idx, 1])
                curr_idx += 1
                if curr_idx >= self.intervals.shape[0]:
                    break
            if tot is None:
                tot = np.array([curr_lhs, curr_rhs])
            else:
                tot = np.vstack((tot, np.array([curr_lhs, curr_rhs])))
            if curr_idx < self.intervals.shape[0]:
                curr_lhs = self.intervals[curr_idx, 0]
                curr_rhs = self.intervals[curr_idx, 1]
        self.intervals = np.atleast_2d(tot)

    def copy(self):
        return Intervals(self.intervals.copy())

    def contains(self, x):
        """ Check if x is in the Finite Union of Intervals. """
        if self.is_empty():
            return False
        idx = self.intervals[:, 0].searchsorted(x)
        if idx == 0:
            return x >= self.intervals[idx, 0]
        if idx >= self.intervals.shape[0]:
            return x <= self.intervals[idx - 1, 1]
        if (self.intervals[idx - 1,0] <= x) and (self.intervals[idx-1, 1] >= x):
            return True
        if (self.intervals[idx,0] <= x) and (self.intervals[idx, 1] >= x):
            return True
        return False

    def index_of_first_intersection(self, x, find_nearest=False):
        """ finds interval nearest to given number x and containing x 
            if find_nearest=False: doesn't require x to be in the interval """
        if self.is_empty():
            return -1
        idx = self.intervals[:, 0].searchsorted(x)
        if idx == 0:
            if x >= self.intervals[idx, 0]:
                return idx
            else:
                return -1
        if find_nearest:
            return idx
        if idx >= self.intervals.shape[0]:
            if x <= self.intervals[idx - 1, 1]:
                return -1
            else:
                return idx - 1
        if (self.intervals[idx - 1,0] <= x) and (self.intervals[idx-1, 1] >= x):
            return idx - 1
        if (self.intervals[idx,0] <= x) and (self.intervals[idx, 1] >= x):
            return idx - 1
        return -1

    def is_empty(self):
        return self.intervals.shape[0] == 0

    def union(self, F):
        """ New Intervals object which is the union of self and Intervals F. """
        if F.is_empty():
            return self
        if self.is_empty():
            return F
        return Intervals(np.vstack((self.intervals, F.intervals)))

    def intersect(self, F):
        """ New Intervals object which is the intersection of self and Intervals F. """
        if F.is_empty():
            return F
        if self.is_empty():
            return self
        return ~(~self + ~F)

    def intersect_with_interval(self, a, b):
        """ returns (not a copy) Intervals object which is the intersection of self and [a, b]
            (faster than intersect) """
        if self.is_empty():
            return self
        if (self.intervals[:, 1] > a).sum() == 0 or (self.intervals[:, 0] < b).sum() == 0:
            return Intervals()
        idx_first_gta = (self.intervals[:, 1] > a).nonzero()[0][0]
        idx_last_ltb = self.intervals.shape[0] - (self.intervals[:, 0] < b)[::-1].nonzero()[0][0]
        return Intervals(self.intervals[idx_first_gta:idx_last_ltb, :])

    def complement(self):
        """ New Intervals object which is the complement of self. """
        if self.is_empty():
            return Intervals([-np.inf, np.inf])
        M = self.intervals.shape[0]
        # complement bulk
        # 2 * M - 2 points
        list_endpoints = self.intervals.ravel()
        I = np.zeros((M - 1, 2))
        odds = range(1, (M - 1) * 2, 2)
        evens = range(0, (M - 1) * 2, 2)
        I[:,1] = list_endpoints[1: -1][odds]
        I[:,0] = list_endpoints[1: -1][evens]

        # fix complement ends
        a, b = list_endpoints[0], list_endpoints[-1]
        if a > -np.inf:
            I = np.vstack((np.array([-np.inf, a]), I))
        if b < np.inf:
            I = np.vstack((I, np.array([b, np.inf])))
        return Intervals() if I.shape[0] == 0 else Intervals(I)

    def measure(self):
        if self.is_empty():
            return 0
        diff_arr = self.intervals[:, 1] - self.intervals[:, 0]
        return diff_arr.sum()

    def trim(self, eps=0.001):
        """ Removes intervals with lengths < eps. """
        if self.is_empty():
            return self
        diff_arr = self.intervals[:, 1] - self.intervals[:, 0]
        idx = diff_arr > eps
        self.intervals = self.intervals[idx, :]
        return self

    def connect_gaps(self, eps=0.001):
        """ connects consecutive intervals separated by lengths < eps """
        H = ~self
        diff_arr = H.intervals[:, 1] - H.intervals[:, 0]
        idx = diff_arr < eps
        if idx.sum() == 0:
            return self
        B = Intervals(H.intervals[idx, :])
        A = self.union(B)
        self.intervals = A.intervals
        return self

    def connect_gaps_by_rule(self, rule):
        """ Returns a new object with gaps connected when rule returns True.
        parameters
            rule: Callable that takes parameters start_time and end_time.
        """
        if self.is_empty(): 
            return self
        new_intervals = []
        i = 0
        dim = self.intervals.shape[0]
        while i < dim:
            a = self.intervals[i, 0]
            while i + 1 < dim and rule(self.intervals[i, 1], self.intervals[i + 1, 0]):
                i += 1
            b = self.intervals[i, 1]
            new_intervals.append([a, b])
            i += 1
        return Intervals(np.array(new_intervals))

    def remove(self, other):
        return self.intersect(~other)
        
    def symmetric_difference(self, other):
        return (self - other) + (other - self)

    def subordinate_to_array(self, arr):
        """ returns a new Intervals object with only intervals containing elements of arr 
            (NOTE: arr is assumed sorted)
        """
        arr = np.array(arr)
        F = Intervals()
        for interval in self.intervals:
            a, b = interval[0], interval[1]
            idxa = arr.searchsorted(a)
            idxb = arr.searchsorted(b)
            if idxa != idxb or (idxa < len(arr) and a == arr[idxa]):  # arr has a point in interval
                F += Intervals([a,b])
        return F

    def save(self, filename='Intervals_save'):
        np.savez(filename, intervals=self.intervals)

    def load(self, filename='Intervals_save.npz'):
        import os

        if os.path.exists(filename):
            arr = np.load(filename)
            self.intervals = arr['intervals']
        return self




def intervals_from_binary(bin_array, times):
    """
    Given a one dimensional bin_array of 0s and 1s,
    returns a Intervals object of times corresponding to consecutives 1s
    """
    F = Intervals()
    idx = 0
    while idx < bin_array.shape[0]:
        curr_bit = bin_array[idx]
        if curr_bit == 0:
            idx +=1
        else:
            AS_idx = idx + 1
            start_idx = idx
            while AS_idx < bin_array.shape[0] and bin_array[AS_idx] == 1:
                AS_idx +=1
            F = F.union(Intervals([times[start_idx], times[AS_idx-1]]))
            idx = AS_idx
    return F



def binary_from_intervals(intervals, length=None):
    """ From an intervals object produce a binary sequence of size length """
    if length is None:
        length = int(intervals.intervals[-1, 1] - intervals.intervals[0, 0])
    binary = np.zeros(length)
    start = intervals.intervals[0, 0]
    end = intervals.intervals[-1, 1]
    arr = np.linspace(start, end, length)
    for c, time in enumerate(arr):
        if intervals.contains(time):
            binary[c] = 1
    return binary
