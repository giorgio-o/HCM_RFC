import numpy as np
import os
from ceppa.util.intervals import Intervals

"""
G.Onnis, 02.2016
binary generation checks functions

Tecott Lab UCSF
"""


def get_corrected_ingestion_Set(self, act_type='F'):
	""" checks for device firing when mouse is not at device cell
		returns array with corrected events and errors removed
	"""
	I_E = Intervals(getattr(self, '%s_timeSet_uncorrected' %act_type))	
	I_at_device = Intervals(getattr(self, 'at_%s_timeSet' %act_type))
	I_diff = I_E - I_at_device 	#I_at_device.complement().intersect(I_E)	
	if not I_diff.is_empty():
		print "%s_device position error: diff %1.4fmin, corrected" %(act_type, I_diff.measure()/60.)
		I_E = I_E.intersect(I_at_device) 
	else:
		print "%s_device position error check: OK" %act_type

	setattr(self, 'device_%s_position_error_timeSet' %act_type, I_diff.intervals)
	setattr(self, '%s_timeSet' %act_type, I_E.intervals)
	return True, I_E.intervals


def check_ingestion_devices_overlap(self):
	"""checks mouse is not at F and W device at the same time
		i.e. F and W do not intersect
	"""
	at_F = Intervals(self.at_F_timeSet)
	at_W = Intervals(self.at_W_timeSet)
	I_inters = at_F.intersect(at_W)
	if not I_inters.is_empty():
		inters = I_inters.intervals[:,1] - I_inters.intervals[:,0]
		print "*"*200
		print "position overlap: total=%1.1fm, max=%1.1fs" %(I_inters.measure() / 60., inters.max())
	else:
		print "position overlap at devices check: OK"

	setattr(self, 'devices_overlap_error_timeSet', I_inters.intervals)
	return I_inters.intervals


def flag_errors(self):
	""" flag device and error message
	"""
	errors1 = self.check_device_errors()
	errors2 = self.check_platform_errors()
	error_dict = errors1.copy()
	error_dict.update(errors2)
	
	flagged = np.array([self.mouseNumber, self.dayNumber, False])
	errors = np.array(['', ''], dtype='|S4')
	num = 0
	for act_type, (has_error, msg) in error_dict.iteritems():
		if has_error:
			print msg
			flagged[2] = True
			errors = np.vstack([errors, np.array([act_type + '_timeSet', msg])])
			num +=1
	if flagged[2]:
		print "this mouseday will be ignored"
	else:
		print "check for additional errors: OK"

	self.flagged = flagged
	self.flagged_msgs = errors[1:]


def check_device_errors(self):
	"""check for some elementary device errors
	"""
	varNames = ['recording_start_stop_time', 'F_timeSet_uncorrected', 'W_timeSet_uncorrected']
	for varName in varNames:
		if not hasattr(self, varName):
			self.load(varName)

	Rec, F, W = [Intervals(getattr(self, varName)) for varName in varNames]
	
	act_type = ['F', 'W']
	thresh = [30, 15] 	# minutes: F, W
	no_event_thresh = 12 	#hours
	error_dict = {}
	i = 0
	for I in [F, W]:
		error_dict[act_type[i]] = [False, '']
		# check one error at the time
		if I.is_empty():
			error_dict[act_type[i]] = [True, 'no events']
		else:
			long_event = (I.intervals[:, 1] - I.intervals[:,0]).max() > thresh[i]*60.
			no_events_for_long_time = \
				(I.complement().intersect(Rec).intervals[:, 1] - \
					I.complement().intersect(Rec).intervals[:, 0]).max() \
					> no_event_thresh*60*60. # intersect with recording time (hrs after midnight)
			if long_event:
				error_dict[act_type[i]] = [True, 'long event (>%dmin)' %thresh[i]]
			elif no_events_for_long_time:
				error_dict[act_type[i]] = [True, 'long time (>%dh)\nw/o events' %no_event_thresh]	
		i +=1 

	for act_type, (has_error, msg) in error_dict.iteritems():
		if has_error:
			print "%s device error found: %s " %(act_type, msg)
			self.ignored = True
	# if self.ignored:
	# 	return error_dict
	return error_dict
	

def check_platform_errors(self, xbins=12, ybins=24):
	"""
	"""
	varName = 'bin_times_24H_xbins%d_ybins%d' %(xbins, ybins)
	if not hasattr(self, varName):
		self.load(varName)
	bin_times = getattr(self, varName)
	tot_bins = bin_times.size
	num = np.count_nonzero(bin_times)
	# max allowed zeros. using xbins,ybins=(12,24),
	# at least 14 bins are always zero (niche walls)
	max_zeros = 15 + 14 
	error_dict = {}
	error_dict['M'] = [False, '']
	if num < tot_bins - max_zeros:
		print "platform error found"
		error_dict['M'] = [True, 'platform error']
		self.ignored = True
		return error_dict
	return error_dict





