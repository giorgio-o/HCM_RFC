import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches

from plotting_utils import ax_cleanup

import my_utils
import os
import time


"""
G.A.Onnis, 04.2016

Tecott Lab UCSF
"""



def get_AS_numbers_vs_IST(experiment, ISTS, act_type='F'):

	E = experiment
	num_mousedays = E.num_md_ok

	base_name = 'AS'

	arr = np.zeros((num_mousedays, len(ISTS)))
	data_labels = np.zeros((num_mousedays, 3))
	
	k_b = 0
	
	for IST in ISTS:

		dirname_in = E.binary_dir + 'AS_Sets/IST_%1.2fm/' %IST 
		
		print "loading %s data from: %s" %(base_name, dirname_in)
		
		cnt = 0
		for strain, group in enumerate(E.groups):	
			
			for mouse in group.individuals:

				if not mouse.ignored:

					for MD in mouse.mouse_days:

						if MD.dayNumber in E.daysToUse:

							if not MD.ignored:

								form_ = (group.number, mouse.individualNumber, MD.dayNumber)
								fname = dirname_in + 'strain%d_individual%d_day%d.npy' %form_

								AS = np.load(fname)
								
								arr[cnt, k_b] = AS.shape[0]
								
								if k_b < 1: 
									data_labels[cnt, 0] = group.number
									data_labels[cnt, 1] = mouse.mouseNumber
									data_labels[cnt, 2] = MD.dayNumber

								cnt +=1

		k_b +=1

	return arr, data_labels



def plot_AS_numbers_vs_IST(experiment, ISTS):
	"""Hyper-param analysis on bouts
	"""

	E = experiment

	strain_names = E.strain_names
	num_strains = len(strain_names)

	base_name = 'ASs'

	dirname_out = E.plots_dir + 'Hyper_analysis/%s/' %base_name
	if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

	arr, data_labels = get_AS_numbers_vs_IST(E, ISTS=ISTS)

	# one plot, all strains
	colors = my_utils.get_16_colors()
	fig, ax = plt.subplots()

	for strain in xrange(num_strains):
		data = arr[data_labels[:, 0] == strain]
		avg = data.mean(axis=0)
		std = data.std(axis=0)

		ax.plot(ISTS, avg, lw=1.5, color=colors[strain], label=strain_names[strain])
		ax.fill_between(ISTS, avg - std, avg + std, color=colors[strain], alpha=0.4)
		
	ax.plot(ISTS, arr.mean(axis=0), lw=3, color='k', label='All Strains', zorder=3)
	
	ax.set_xlim([0, ISTS[-1]])
	ax.set_ylim([0, 50])

	ax.set_xlabel('IST Threshold [min]')
	ax.set_ylabel("AS Numbers")
	
	ax_cleanup(ax)

	#legend
	h, l = ax.get_legend_handles_labels()
	legend = ax.legend(h, l, loc=1, prop={'size':10}, frameon=False)

	# title
	fig.text(0.03, 0.95, 'AS Numbers vs IST Thresh', fontsize=8)

	fname = dirname_out + 'ASN_vs_IST.pdf' 
	fig.savefig(fname)
	plt.close()
	print "saved to: ", fname





def get_bout_numbers_vs_BT(experiment, BTS, act_type='F'):

	E = experiment
	num_mousedays = E.num_md_ok

	base_name = 'Bouts'

	arr = np.zeros((num_mousedays, len(BTS)))
	data_labels = np.zeros((num_mousedays, 3))
	
	k_b = 0
	
	for BT in BTS:

		dirname_in = E.binary_dir + 'Bout_Sets/BT_%1.2fs/%s_bout_Sets/' %(BT, act_type) 
		
		print "loading %s data from: %s" %(base_name, dirname_in)
		
		cnt = 0
		for strain, group in enumerate(E.groups):	
			
			for mouse in group.individuals:

				if not mouse.ignored:

					for MD in mouse.mouse_days:

						if MD.dayNumber in E.daysToUse:

							if not MD.ignored:

								form_ = (group.number, mouse.individualNumber, MD.dayNumber)
								fname = dirname_in + 'strain%d_individual%d_day%d.npy' %form_

								b = np.load(fname)
								
								arr[cnt, k_b] = b.shape[0]
								
								if k_b < 1: 
									data_labels[cnt, 0] = group.number
									data_labels[cnt, 1] = mouse.mouseNumber
									data_labels[cnt, 2] = MD.dayNumber

								cnt +=1

		k_b +=1

	return arr, data_labels






def plot_bout_numbers_vs_BT(experiment, BTS, act_type='F'):
	"""Hyper-param analysis on bouts
	"""

	E = experiment

	strain_names = E.strain_names
	num_strains = len(strain_names)

	base_name = 'bouts'

	# BTs = [1, 5, 10, 30, 60, 300, 600]
	# # BTs = [1,2,3,4,5,6,8, 10, 30, 60, 300, 600]
	dirname_out = E.plots_dir + 'Hyper_analysis/%s/' %base_name
	if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

	arr, data_labels = get_bout_numbers_vs_BT(E, BTS=BTS, act_type=act_type)

	# one plot, all strains
	colors = my_utils.get_16_colors()
	fig, ax = plt.subplots()
	
	ymax = 1000
	if act_type == 'M':
		ymax = 4000
	
	for strain in xrange(num_strains):
		data = arr[data_labels[:, 0] == strain]
		avg = data.mean(axis=0)
		std = data.std(axis=0)

		ax.plot(BTS, avg, lw=1.5, color=colors[strain], label=strain_names[strain])
		ax.fill_between(BTS, avg - std, avg + std, color=colors[strain], alpha=0.4)
		
	ax.plot(BTS, arr.mean(axis=0), lw=3, color='k', label='All Strains', zorder=3)
	
	ax.set_xlim([0, BTS[-1]])
	ax.set_ylim([0, ymax])

	ax.set_xlabel('Bout Threshold [sec]')
	ax.set_ylabel("Bout Numbers")
	
	ax_cleanup(ax)

	#legend
	h, l = ax.get_legend_handles_labels()
	legend = ax.legend(h, l, loc=1, prop={'size':10}, frameon=False)

	# title
	fig.text(0.03, 0.95, '%s Bout Numbers vs Bout Thresh' %act_type, fontsize=8)

	fname = dirname_out + '%s_bout_numbers_vs_BT.pdf' %act_type
	fig.savefig(fname)
	plt.close()
	print "saved to: ", fname
			
