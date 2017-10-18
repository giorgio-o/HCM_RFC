import numpy as np

from ceppa.util.my_utils import count_onsets_in_bin
from ceppa.util.intervals import Intervals


"""
D. Rhea, 2013
G.Onnis, C. Hillar revised, 05.2015
G.Onnis, revised, 04.2017

Tecott Lab UCSF
"""



def get_bin_counts_within_AS(self, act, AS_start, AS_end, tbins, ONSET=True):
	"""breakfast
	"""

	FW = self.load('%s_timeSet' %act) # '%sB_timeSet' %act
	FW_AS = Intervals(FW).intersect_with_interval(AS_start, AS_end)

	arr = np.zeros(len(tbins)) 
	# arr_c = np.zeros(len(tbins))

	b = 0
	for tbin in tbins:
		if not FW_AS.intersect_with_interval(tbin[0], tbin[1]).is_empty():
			arr[b] = 1
		b += 1

	# # cumulative
	# if ONSET:
	# 	fidx = arr[0].argmax()
	# 	wixd = arr[1].argmax()
	# 	if arr[0][fidx] != 1:
	# 		idx_f = num_bins
	# 	if arr[1][wixd] != 1:
	# 		wixd = num_bins

	# else: 		
	# 	fidx = 0			
	# 	if len(np.where(arr[0]==1)[0]) > 0:
	# 		fidx = np.where(arr[0]==1)[0][-1]
		
	# 	wixd = 0
	# 	if len(np.where(arr[1]==1)[0]) > 0:
	# 		wixd = np.where(arr[1]==1)[0][-1]
		
	# 	arr_c[0] = [1] * fidx + [0] * (num_bins - fidx)
	# 	arr_c[1] = [1] * wixd + [0] * (num_bins - wixd)

	# arr_c[0] = [0] * fidx + [1] * (num_bins - fidx)
	# arr_c[1] = [0] * wixd + [1] * (num_bins - wixd)		

	return arr#, arr_c


def get_breakfast_probability(self, act, ONSET=True, num_secs=900, tbin_size=5, cycle='24H'):
	""" breakfast  
	"""
	num_bins = int(num_secs / tbin_size)
	# get AS in cycle
	AS = self.get_AS_in_cycle(cycle)
	
	num_AS = AS.shape[0]
	if num_AS == 0:
		return np.zeros(num_bins)

	arr_p = np.zeros((num_AS, num_bins))
	# arr_c = np.zeros((num_AS, num_bins)) 	
	for k in xrange(num_AS):

		if ONSET:
			AS_start = AS[k, 0]
			AS_end = AS_start + num_secs

		else:
			AS_end = AS[k, 1]
			AS_start = AS_end - num_secs

		tbins = np.array([[i, i + tbin_size] for i in np.linspace(AS_start, AS_end, num_bins)])
		
		arr_p[k] = self.get_bin_counts_within_AS(act, AS_start, AS_end, tbins, ONSET) 
	
	return arr_p.mean(axis=0)#, arr_c.mean(axis=0)


