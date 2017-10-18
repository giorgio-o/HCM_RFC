from Experiments import StrainSurveyExperiment
import numpy as np
import matplotlib.pyplot as plt 
# from matplotlib import pyplot, mpl, cm
from matplotlib import pyplot, cm

from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from matplotlib import animation

import matplotlib.gridspec as gridspec

from ellipsoids import *
import itertools
import plot_utils
import os
from kmeans import utils
import nanfunctions  
import scipy.misc
from scipy import stats
import option_colormaps



"""
G.Onnis, 02.2015
revised 05.2015, 08.2015

UCSF Tecott lab
"""	

np.set_printoptions(precision=2)
np.set_printoptions(threshold=8000)
np.set_printoptions(linewidth=250)
np.set_printoptions(suppress=True)





def plot_master_classifier_performance_16colors_3x2(experiment, num_trials=20, BIN_FILE=False, CSV_FILE=False, savekw={}):
	"""Figure for Strain paper. plot classifier accuracy for mice
		and mousedays as a bar
	"""

	E = experiment

	strain_names = E.strain_names
	strain_dict = E.strain_dict
	num_strains = len(strain_names)

	num_mice = E.total_individuals_ok	
	num_mousedays = E.total_md_ok

	days_to_use = E.daysToUse

	
	features = ['Dist', 'Prob', 'Prob_Counts'] 
	num_features = len(features)
	labels_f = ['Distance', 'ASProb', 'All features']

	levels = ['Mouseday', 'Individuals']
	num_levels = len(levels)

	np.set_printoptions(precision=4)
	
	# load
	dirname_in = E.plots_dir + 'Kmeans/npy/'
	# # save to
	base_name = 'master_classifier_accuracy'
	dirname_out = E.plots_dir + 'Kmeans/master_classifier/'
	if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

	
	# # load data for IST=20min and average
	
	# # old good best wrong values. 
	# fname = dirname_in + 'all_tot_table_all_feat_ms_avgs.npz'
	# fname2 = dirname_in + 'ASP_ASN_tot_table_all_feat_ms_avgs.npz'
	# # average over bootstrap trials
	# M = np.zeros((num_features, num_trials, num_levels, num_strains))
	# M[0], M[1], M[2] = tot_data['tot_table'][5], tot_data['tot_table'][0], tot_data2['tot_table'][0], 

	fname0 = dirname_in + 'Distance_LR_classify.npz'
	fname1 = dirname_in + 'ASProb_LR_classify.npz'
	fname2 = dirname_in + 'ASProbASCountsASDurFoodWaterTotalLocoF_ASIntD_ASIntL_ASInt_LR_classify.npz'
	# alternatively use: 'ASProbASCountsASDurFoodWaterDistance_LR_classify.npz'
	print "loading data from file:\n%s\n%s\n%s" %(fname0, fname1, fname2)

	tot_data0 = np.load(fname0)['LR_classify'].swapaxes(1,2)
	tot_data1 = np.load(fname1)['LR_classify'].swapaxes(1,2)
	tot_data2 = np.load(fname2)['LR_classify'].swapaxes(1,2)
	
	# average over bootstrap trials
	M = np.zeros((num_features, num_trials, num_levels, num_strains))
	M[0], M[1], M[2] = tot_data0, tot_data1, tot_data2

	
	# # test/train set, mousedays
	tot_mice, tot_md_train, tot_md_test = E.get_number_individuals_mousedays(days_to_use=days_to_use, TEST_SET=True)
	
	# initialize arrays
	correctly_labeled = np.zeros((num_features, num_levels, num_strains)) 
	percent_avg = np.zeros((num_features, num_levels, num_strains)) 
	percent_std = np.zeros((num_features, num_levels, num_strains)) 
	
	for f in xrange(num_features):
	
		for strain in xrange(num_strains):
			# individuals
			correctly_labeled[f, 0, strain] = M[f].mean(axis=0)[0, strain]
			percent_avg[f, 0, strain] = correctly_labeled[f, 0, strain] / tot_mice[strain]
			percent_std[f, 0, strain] = M[f].std(axis=0)[0, strain] / tot_mice[strain]
			
			# mousedays
			correctly_labeled[f, 1, strain] = M[f].mean(axis=0)[1, strain]
			percent_avg[f, 1, strain] = correctly_labeled[f, 1, strain] / tot_md_test[strain]			
			percent_std[f, 1, strain] = M[f].std(axis=0)[1, strain] / tot_md_test[strain]


	correctly_labeled = correctly_labeled[:, ::-1]
	percent_avg = percent_avg[:, ::-1] 		# reverse individuals <-> mousedays
	percent_std = percent_std[:, ::-1]
	

	
	# Plotting
	print "plotting %s for 16 strains, colors\nfeatures:\n%s\nlevels:\n%s\nnum_trials: %d" %(base_name, features, levels, num_trials)
	print "percent_avg, by feature"
	print percent_avg
	print "percent_std, by feature"
	print percent_std


	# do the plot
	fig, ax = plt.subplots(figsize=(11, 6))
	colors = plot_utils.get_16_colors()

	ind2 = np.array([3, 46, 89]) 	# positions
	sep = 6 					# separation
	bar_width = 0.7
	
	xlims = [0, 125]
	ylims = [0, 1.1]

	for c in xrange(num_levels):

		for strain in xrange(num_strains):

			rect = ax.bar(ind2 + c * (num_strains * bar_width + sep) + strain * (bar_width+0.15), 
				percent_avg[:, c, strain], bar_width,
				yerr=[[0,0,0], percent_std[:, c, strain]],	
				label=strain_names[strain],
				lw=1., 
				color=colors[strain],
				edgecolor=colors[strain],
				capsize=2,
				ecolor=colors[strain], 
				)


	plt.xlim(xlims)
	plt.ylim(ylims)

	xticks = [idx + c * (num_strains * bar_width + sep) + (num_strains * (bar_width + 0.15)) / 2 \
				for idx in ind2 for c in range(num_levels)]
	
	yticks = np.linspace(0, 1, 5+1)

	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	ax.xaxis.set_ticks_position('bottom')
	ax.yaxis.set_ticks_position('left')
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	ax.tick_params(axis='both', labelsize=12)

	ax.get_xaxis().tick_bottom()
	ax.get_yaxis().tick_left()


	xlabels = ['MD', 'Indiv'] * 3 
	# xlabels = ['ASC', 'ASP', 'ASP+C'] * 2
	ylabels = [str(x) + '$\%$' for x in range(0, 101, 20)] 
	ax.set_xticklabels(xlabels)
	ax.xaxis.set_ticks_position('none') 
	ax.set_yticklabels(ylabels)


	# horizontal line at 100%
	plt.plot([xlims[0], xlims[1]], [1, 1], '--', c='k', lw=0.5, zorder=0)

	if 1:
		# # yticks lines
		ax.spines['left'].set_visible(False)
		ax.tick_params(axis='y', which='major', pad=10)
		for y in yticks:
			ax.plot(xlims, [y] * len(xlims), "--", lw=0.75, color='.3', zorder=0)


	# Shrink current axis by 20%, allow space to custom legend
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width*0.93, box.height])


	# custom legend
	# handles, labels = ax.get_legend_handles_labels()
	# mylist = zip(handles, labels)
	mylist = []
	for num, color in enumerate(colors):
		p3 = patches.Rectangle((0, 0), 0, 0, fc=color, ec=color)
		mylist.append([p3, '%s' %strain_names[num]]) 

	h0, l0 = zip(*mylist)
	ax.legend(h0, l0, bbox_to_anchor=[1.21, 0.87], frameon=False, prop={'size':10})


	# # # legend with colored labels
	# # col = 0 		# color counter
	# # for l in xrange(num_strains):
	# # 	fig.text(.93, .75-.03*col, '%s' %(strain_names[l]), 
	# # 		fontsize=10,
	# # 		color=colors[col],
	# # 		horizontalalignment='center'
	# # 		)
	# # 	col +=1

	# # # custom legend box	
	# # frame = patches.Rectangle((0.88, 0.28), 0.1, .51, 
	# # 				facecolor='none', edgecolor='0.3',
	# # 				transform=ax.figure.transFigure, 
	# # 				clip_on=False,
	# # 				zorder=0
	# # 				)
	
	# # ax.add_patch(frame)  	



	# # axis labels
	fig.text(.19, .02, labels_f[0], fontsize=14)
	fig.text(.44, .02, labels_f[1], fontsize=14)
	fig.text(.68, .02, labels_f[2], fontsize=14)
	fig.text(.03, .5, 'Classification accuracy', fontsize=14, va='center', rotation='vertical')
	fig.text(.03, .95, '6a', weight='bold')

	# title
	plot_title = '#K-means master classifier accuracy\nstrain averages ($\pm$ stdev), %d bootstrap trials\n%d features, mousedays/individuals, %d strains' %(num_trials, num_features, num_strains)
	# fig.text(0.05, 0.93, plot_title, fontsize=8)


	print "saving plot.."
	filename = dirname_out + base_name + '_16strains_3x2.pdf'

	if len(savekw) > 0:
		filename = E.plots_dir + 'SS_figures/' + base_name + '_16strains.pdf'

	# plt.savefig(filename, bbox_inches='tight', **savekw)
	plt.savefig(filename[:-4], bbox_inches='tight', format='eps', dpi=300, **savekw)

	plt.close()

	print "saved to %s" %filename
	

	if BIN_FILE:
		fname = dirname_out + base_name + '_means.npy'
		np.save(fname, percent_avg)
		fname2 = dirname_out + base_name + '_stds.npy'
		np.save(fname2, percent_std)
	

	# write data to file
	if CSV_FILE:
		data_file = dirname_out + base_name + '.txt'

		print 'saving data to file:\n%s' %data_file

		with file(data_file, 'w') as outfile:
			outfile.write(plot_title)
			outfile.write('\n\n#%d features:\n%s\n' %(num_features, features))
			outfile.write('\n#%d strains:\n%s\n' %(num_strains, strain_dict))
		
			cnt = 0
	 		for f, feature in enumerate(features):
				avg = M[f].mean(axis=0).sum(axis=1) / [170, 961]
				outfile.write('\n\n#%s, avg. correct [ind, md]:\n%s\n' %(features[f], avg))
				
				outfile.write('\n#by strain [ind, md]:\n%s\n' %percent_avg[f].T)		

				cnt +=1










# 




def plot_pairwise_classifier_mousedays(experiment, ntrials=20, BIN_FILE=False, CSV_FILE=False, savekw={}):
	"""Figure for Strain Paper. plots pairwise classifier as imshow
		for 16 strains
	"""

	E = experiment

	strain_names = E.strain_names
	strain_dict = E.strain_dict
	num_strains = len(strain_names)

	set_names = ['Train', 'Test']
	set_size = [960, 961]
	num_sets = len(set_names)

	features = ['Dist', 'Prob']
	num_features = len(features)
	
	number_of_features = [11, 11]
	label_f = ['Distance', 'ASProb']

	# all
	# features = ['Loco', 'Counts', 'Prob', 'Prob_Counts']
	# number_of_features = [11, 11, 11, 22]
	# label_f = ['Locomotion', 'ASCounts', 'ASProb', 'ASProb$+$Counts']


	# load
	dirname_in = E.plots_dir + 'Kmeans/npy/'	
	# save to:
	base_name = 'pairwise_classifier_scores' 
	dirname_out = E.plots_dir + 'Kmeans/pairwise_classifier/mousedays/'
	if not os.path.isdir(dirname_out): os.makedirs(dirname_out)


	# load 
	fname = dirname_in + 'all_tot_table_all_feat_ms_avgs.npz' 
	print "loading data from file:\n%s" %fname
	
	tot_data = np.load(fname) 
	PW_score_avg_train = tot_data['PW_score_avg_train']
	PW_score_avg_test = tot_data['PW_score_avg_test'] 
	# PW_pval_test = 0.1 	# missing

	# average over bootstrap trials
	PW_score = np.zeros((2, num_features, num_strains, num_strains)) 	#train, test
	
	PW_score[0] = PW_score_avg_train[5].mean(axis=0), PW_score_avg_train[0].mean(axis=0)
	PW_score[1] = PW_score_avg_test[5].mean(axis=0), PW_score_avg_test[0].mean(axis=0)


	# plot settings
	figsize = (15, 12)
	sub_high = 2
	sub_wide = 2

	# plot settings
	# #all
	# figsize = (25, 13)
	# sub_high = 2
	# sub_wide = 4

	xvar = range(1, num_strains+1)
	yvar = range(1, num_strains+1)
	vmin = 0.5
	vmax = 1.

	# colormap options
	# num_steps = 20
	# cmap = plot_utils.cmap_discretize(cm.afmhot, num_steps) 
	cmap=cm.afmhot
	print "plotting %s .." %base_name

	gs1 = gridspec.GridSpec(sub_high, sub_wide)
	fig = plt.figure(figsize=figsize)

	k_sub = 0
	Z_list= []
	for t, tset in enumerate(set_names):

		for f, feature in enumerate(features):
			
			print "plotting mousedays, feature: %s.." %feature

			Z = PW_score[t, f] 
			# Z3 = PW_pval_test					# pval missing
			Z[Z==0] = np.nan

			Z = Z.T
			
			ax = fig.add_subplot(gs1[k_sub])
			
			print 'plotting %s set: %d mousedays ' %(set_names[t], set_size[t])
			# print 'average correct = %1.3f' %nanfunctions.nanmean(Z)
			# print 'min accuracy:', np.nanmin(Z)

			im = ax.imshow(Z, interpolation='nearest', cmap=cmap, vmin=vmin, vmax=vmax)		

			ax.set_xticks(np.arange(num_strains) - 0.25) 
			ax.set_yticks(range(num_strains))
			ax.set_xticklabels(strain_names, rotation=315, ha='left')
			ax.set_yticklabels(strain_names)

			ax.tick_params(axis='x', which='major', pad=2)
			ax.tick_params(axis='y', which='major', pad=5)

			ax.spines['right'].set_visible(False)
			ax.spines['bottom'].set_visible(False)
			ax.spines['left'].set_visible(False)
			ax.spines['top'].set_visible(False)

			ax.xaxis.set_ticks_position('none')
			ax.yaxis.set_ticks_position('none')

			plot_utils.draw_squares_on_diagonal(ax, HATCH=True)
			
			plot_utils.draw_beehive(ax, position='bottom')

			ax.set_aspect('equal')

			ax.set_title('%s, avg = %1.3f' %(label_f[f], nanfunctions.nanmean(Z)), fontsize=20)

			Z_list.append(Z) 	# 4 items: test, train + ASProb, Loco

			k_sub += 1


			if BIN_FILE:

				fname = dirname_out + base_name + '_means_%s_%s.npy' %(set_names[t], features[f])
				np.save(fname, Z)



		# colorbar
		if t == 0:
			axCbar = plt.axes([0.91, 0.6, 0.01, 0.25])			# [left, bottom, width, height]
			cbar = fig.colorbar(im, cax=axCbar)
			cbar.ax.set_ylabel('Clustering Accuracy', fontsize=16, rotation=270, labelpad=25.)
			cbytick_obj = plt.getp(cbar.ax.axes, 'yticklabels')                
			plt.setp(cbytick_obj)
			
			y_ = 0.75
		
		else:
			axCbar = plt.axes([.91, 0.15, .01, 0.25])			# [left, bottom, width, height]
			cbar = fig.colorbar(im, cax=axCbar)
			cbar.ax.set_ylabel('Clustering Accuracy', fontsize=16, rotation=270, labelpad=25.)
			cbytick_obj = plt.getp(cbar.ax.axes, 'yticklabels')                
			plt.setp(cbytick_obj)

			y_ = 0.3

		fig.text(0.05, y_, '%s' %set_names[t], fontsize=28, rotation=90)



	# title
	plot_title = '#K-means pairwise classifier accuracy, strain averages, %d bootstrap trials\nFeatures: Locomotion, AS Probability\n%d strains, top 9/9 features, Test: %d MDs, Train: %d MDs' %(ntrials, num_strains, set_size[0], set_size[1])

	# fig.text(0.05, 0.95, plot_title, fontsize=10) 
		
	gs1.update(hspace=0.35, wspace=0.3)
	
	# filename = dirname_out + base_name + '_mousedays_all_features_%dntrials.pdf' %ntrials
	filename = dirname_out + base_name + '_mousedays_ASProb_Loco_%dntrials.pdf' %ntrials
	

	if len(savekw) > 0:
		filename = E.plots_dir + 'SS_figures/' + base_name + '_mousedays_ASProb_Loco_%dntrials.pdf' %ntrials

	plt.savefig(filename, bbox_inches='tight', **savekw)
	plt.savefig(filename[:-4], bbox_inches='tight', format='eps', dpi=300, **savekw)	
	print "saved to:\n%s" %filename



	# write data to file
	if CSV_FILE:
		data_file = dirname_out + base_name + '.txt'

		print 'saving data to file:\n%s' %data_file

		with file(data_file, 'w') as outfile:

			outfile.write(plot_title)
			outfile.write('\n\n#%d features:\n%s\n' %(num_features, features))
			outfile.write('\n#%d strains:\n%s\n' %(num_strains, strain_dict))
			outfile.write('\n#%d sets:\n %s\n\n' %(num_sets, set_names))

			cnt = 0
			for t, tset in enumerate(set_names):

				for f, feature in enumerate(features):

					avg = nanfunctions.nanmean(Z_list[cnt])

					outfile.write('\n\n#%s, %s set, avg. correct: %1.3f\n\n' %(features[f], set_names[t], avg))
					np.savetxt(outfile, Z_list[cnt], fmt='%-7.4f')
				
					cnt +=1












def plot_pairwise_classifier_individuals(experiment, BIN_FILE=False, CSV_FILE=False):
	"""Figure for Strain Paper. plots pairwise classifier as imshow
		for 16 strains, individuals only

		BROKEN FOR NOW. adapting to _mousedays function below
	"""

	E = experiment

	strain_names = E.strain_names
	strain_dict = E.strain_dict
	num_strains = len(strain_names)

	features = ['Loco', 'Counts', 'Prob', 'Prob_Counts']
	num_features = len(features)

	number_of_features = [11, 11, 11, 22]
	label_f = ['Locomotion', 'ASCounts', 'ASProb', 'ASProb and Counts']

	np.set_printoptions(precision=3)


	# load
	dirname_in = E.plots_dir + 'Kmeans/npy/'

	# save to:
	base_name = 'pairwise_classifier_scores' 
	dirname_out = E.plots_dir + 'Kmeans/pairwise_classifier/individuals/'
	if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

	# test_set_size = 170 / 2		

	# # load data for IST=20min and average
	fname1 = dirname_in + '_tot_table_all_feat_ms_avgs.npz'
	fname2 = dirname_in + 'ASP_ASN_tot_table_all_feat_ms_avgs.npz'
	print "loading data from file:\n%s\n%s" %(fname1, fname2)

	tot_data = np.load(fname1) 
	data2 = np.load(fname2)

	PW_score_avg_train = tot_data['PW_score_avg_train'] 
	PW_score_avg_test = tot_data['PW_score_avg_test'] 
	# PW_pval_test = 0.1 	# missing

	aspn_train = data2['PW_score_avg_train']
	aspn_test = data2['PW_score_avg_test']


	# average over bootstrap trials
	PW_score = np.zeros((2, num_features, num_strains, num_strains)) 	#train, test
	
	PW_score[0] = PW_score_avg_train[5].mean(axis=0), PW_score_avg_train[1].mean(axis=0), PW_score_avg_train[0].mean(axis=0), aspn_train[0].mean(axis=0)
	PW_score[1] = PW_score_avg_test[5].mean(axis=0), PW_score_avg_test[1].mean(axis=0), PW_score_avg_test[0].mean(axis=0), aspn_test[0].mean(axis=0)



	# plot settings
	xvar = range(1, num_strains+1)
	yvar = range(1, num_strains+1)
	vmin = .5
	vmax = 1.
	# colormap options
	# cmap1 = option_colormaps.get_optionD_cmap()
	cmap1 = plt.cm.jet_r
	# discretize
	num_steps = 20
	cmap = plot_utils.cmap_discretize(cmap1, num_steps)


	print "plotting %s .." %base_name

	Z2_list = []

	for f, feature in enumerate(features):
		
		print "feature: %s" %feature

		print fname
		# rename variables
		Z1 = PW_score_avg_train 			# class_score individuals
		Z2 = PW_score_avg_test				
		# Z3 = PW_pval_test					# pval missing
		Z1[Z1==0] = np.nan
		Z2[Z2==0] = np.nan 	

		
		# # plot test set
		set_name = 'test'
		Z2=Z2.T
		# Z3=Z3.T

		print '%s set: %d individuals' %(set_name, test_set_size)
		print 'average correct = %1.3f' %nanfunctions.nanmean(Z2)
		print 'min accuracy:', np.nanmin(Z2)


		# plot
		fig, ax = plt.subplots()

		im = ax.imshow(Z2, interpolation='nearest', cmap=cmap, vmin=vmin, vmax=vmax)		

		ax.set_xticks(np.arange(num_strains) - 0.25) 
		ax.set_yticks(range(num_strains))
		ax.set_xticklabels(strain_names, rotation=315, ha='left')
		ax.set_yticklabels(strain_names)

		ax.tick_params(axis='x', which='major', pad=2)
		ax.tick_params(axis='y', which='major', pad=5)

		ax.spines['right'].set_visible(False)
		ax.spines['bottom'].set_visible(False)
		ax.spines['left'].set_visible(False)
		ax.spines['top'].set_visible(False)

		ax.xaxis.set_ticks_position('none')
		ax.yaxis.set_ticks_position('none')

		plot_utils.draw_squares_on_diagonal(ax, HATCH=True)
	
		plot_utils.draw_beehive(ax, position='bottom')

		ax.set_aspect('equal')

		# ax.set_title('%s, avg = %1.4f' %(label_f[f], nanfunctions.nanmean(Z2)))

		# colorbar
		# labels = [str(x) + "$\%$" for x in range(60, 102, 4)]
		# labels = range(60, 102, 4)
		axCbar = plt.axes([.85, 0.3, .025, .5])			# [left, bottom, width, height]
		cbar = fig.colorbar(im, cax=axCbar)
		# cbar.ax.set_yticklabels(labels)
		# cbar.set_ticks(labels)
		cbar.ax.set_ylabel('Clustering Accuracy', fontsize=14, rotation=270, labelpad=10.)
		cbytick_obj = plt.getp(cbar.ax.axes, 'yticklabels')                
		plt.setp(cbytick_obj)

		# Shrink current axis by 20%, allow space to custom legend
		box = ax.get_position()
		ax.set_position([box.x0, box.y0 + 0.03, box.width*0.95, box.height*0.95])

		Z2_list.append(Z2)

		# if LABELS:
		# 	# # plot num individuals and average
		# 	ax.text(9, 1.3, '%s set: %d individuals' %(set_name, test_set_size), fontsize=10)
		# 	ax.text(9, 1.9, 'average correct = %1.3f' %nanfunctions.nanmean(Z2), fontsize=10)

				# # # plot some square if p.value < minp
				# minp = .001
				# maxp = .05
				# cut = .98
				# for ii in range(num_strains):
				# 	for jj in range(num_strains):
				# 		if ii < jj:
				# 			if Z3[ii, jj] <= minp:
				# 				# square = patches.Rectangle((-.5+ii, -.5+jj), 1, 1, facecolor=None, edgecolor='r')
				# 				square = patches.Rectangle((+.25+ii, -.4+jj), .15, .15, facecolor='r', lw=.5)
				# 				ax.add_patch(square)
				# 				# # print pvalue
				# 				# ax.text(ii-.4, jj+.1, utils.sci_notation(Z3[ii, jj]), color='r', fontsize=4) 
				# 			else:
				# 				square = patches.Rectangle((+.25+ii, -.4+jj), .15, .15, facecolor='y', lw=.5)
				# 				ax.add_patch(square)

				# # # add to text
				# square_l = patches.Rectangle((8., 3.8), .15, .15, facecolor='y', lw=.5)
				# ax.add_patch(square_l)
				# ax.text(8.4, 4.1, '%1.2f $\leq$ p-value $<$ %1.3f' %(maxp, minp), color='y', fontsize=8, fontweight='bold')
				# square_l1 = patches.Rectangle((8., 4.6), .15, .15, facecolor='r', lw=.5)
				# ax.add_patch(square_l1)
				# ax.text(8.4, 4.9, 'p-value $\leq$ %1.3f' %minp, color='r', fontsize=8, fontweight='bold')
			# 	# # plot values>98%
			# 	for row in range(Z2.shape[0]):
			# 		for col in range(Z2.shape[1]):
			# 			if Z2[col, row] >= cut and Z2[col, row] <1:
			# 				ax.text(row-.3, col+.1, '.%d' %(1000*Z2[col, row]), color='w', fontsize=6, weight='bold') 
			# 				# ax.text(row-.3, col+.1, '%1.2f' %Z2[col, row], color='w', fontsize=6, weight='bold') 
			# 			elif Z2[col, row] == 1:
			# 				ax.text(row-.3, col+.1, '%1.2f' %(Z2[col, row]), color='w', fontsize=6, weight='bold') 
			# 				# ax.text(row-.1, col+.1, '%1.0f' %(Z2[col, row]), color='w', fontsize=6, weight='bold') 


		
		# title
		print label_f[f]
		t1 = '#K-means pairwise classifier accuracy, strain averages, %d strains' %num_strains
		t2 = '\nFeature: %s\nTest set: %d individuals' %(label_f[f], test_set_size)
		plot_title = t1 + t2
		# plot_title = '#K-means pairwise classifier accuracy, strain averages\
		# 	\n#Feature: %s, Test set (%d individuals), 16 strains' %(label_f[f], test_set_size)
		fig.text(0.05, 0.93, plot_title, fontsize=8)
		
		print "saving figure.."
		
		filename = dirname_out + base_name + '_individuals_%s_%s.pdf' %(feature, set_name)
		plt.savefig(filename)
	
		print "saved to:\n%s" %filename


		if BIN_FILE:

			fname = dirname_out + base_name + '_means_%s_%s.npy' %(set_name, features[f])
			np.save(fname, Z2)



	# write data to file
	if CSV_FILE:
		data_file = dirname_out + base_name + '.txt'

		print 'saving data to file:\n%s' %data_file

		with file(data_file, 'w') as outfile:

			outfile.write(plot_title)
			outfile.write('\n\n#%d features:\n%s\n' %(num_features, features))
			outfile.write('\n#%d strains:\n%s\n' %(num_strains, strain_dict))
			outfile.write('\n#%s set, %d individuals\n\n' %(set_name, test_set_size))
			
			for f in xrange(num_features):
				outfile.write('\n#' + features[f] + ':\n')	
				np.savetxt(outfile, Z2_list[f], fmt='%-7.4f')
			
				avg = nanfunctions.nanmean(Z2_list[f])
				outfile.write('\n#%s average correct, %s:\n' %(features[f], set_name) )
				outfile.write('%s\n\n' %avg)





# def plot_master_classifier_performance_16colors_2x3(experiment, num_trials=20, BIN_FILE=False, CSV_FILE=False):
# 	"""Figure for Strain paper. plot classifier accuracy for mice
# 		and mousedays as a bar
# 	"""

# 	E = experiment

# 	strain_names = E.strain_names
# 	strain_dict = E.strain_dict
# 	num_strains = len(strain_names)

# 	num_mice = E.total_individuals_ok	
# 	num_mousedays = E.total_md_ok

# 	days_to_use = E.daysToUse

	
# 	features = ['Dist', 'Prob', 'Prob_Counts'] 
# 	num_features = len(features)

# 	levels = ['Mouseday', 'Individuals']
# 	num_levels = len(levels)

# 	np.set_printoptions(precision=4)
	
# 	# load
# 	dirname_in = E.plots_dir + 'Kmeans/npy/'
# 	# # save to
# 	base_name = 'master_classifier_accuracy'
# 	dirname_out = E.plots_dir + 'Kmeans/master_classifier/'
# 	if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

	
# 	# # load data for IST=20min and average
# 	fname1 = dirname_in + 'all_tot_table_all_feat_ms_avgs.npz'
# 	fname2 = dirname_in + 'ASP_ASN_tot_table_all_feat_ms_avgs.npz'
# 	print "loading data from file:\n%s\n%s" %(fname1, fname2)

# 	tot_data = np.load(fname1) 
# 	tot_table = tot_data['tot_table']
# 	data2 = np.load(fname2)
# 	aspn_data = data2['tot_table']

# 	# average over bootstrap trials
# 	M = np.zeros((num_features, num_trials, num_levels, num_strains))
# 	M[0], M[1], M[2] = tot_table[5], tot_table[0], aspn_data[0]

# 	# test/train set, mousedays
# 	tot_mice, tot_md_train, tot_md_test = E.get_number_individuals_mousedays(days_to_use=days_to_use, TEST_SET=True)


# 	# initialize arrays
# 	correct = np.zeros((num_features, num_levels, num_strains)) 
# 	percent_avg = np.zeros((num_features, num_levels, num_strains)) 
# 	percent_std = np.zeros((num_features, num_levels, num_strains)) 
	
# 	for f in xrange(num_features):
	
# 		for strain in xrange(num_strains):
# 			# individuals
# 			correct[f, 0, strain] = M[f].mean(axis=0)[0, strain]
# 			percent_avg[f, 0, strain] = correct[f, 0, strain] / tot_mice[strain]
# 			percent_std[f, 0, strain] = M[f].std(axis=0)[0, strain] / tot_mice[strain]
# 			# mousedays
# 			correct[f, 1, strain] = M[f].mean(axis=0)[1, strain]
# 			percent_avg[f, 1, strain] = correct[f, 1, strain] / tot_md_test[strain]			
# 			percent_std[f, 1, strain] = M[f].std(axis=0)[1, strain] / tot_md_test[strain]


# 	correct = correct[:, ::-1]
# 	percent_avg = percent_avg[:, ::-1] 		# reverse individuals <-> mousedays
# 	percent_std = percent_std[:, ::-1]
	

	
# 	# Plotting
# 	print "plotting %s for 16 strains, colors\nfeatures:\n%s\nlevels:\n%s\nnum_trials: %d" %(base_name, features, levels, num_trials)
# 	print "percent_avg, by feature"
# 	print percent_avg
# 	print "percent_std, by feature"
# 	print percent_std


# 	# do the plot
# 	fig, ax = plt.subplots(figsize=(10,6))
# 	colors = plot_utils.get_16_colors()

# 	ind = np.array([3, 51]) 	# positions
# 	sep = 5 					# separation
# 	bar_width = 0.5
	
# 	xlims = [0, 90]
# 	ylims = [0, 1.1]

# 	for f in xrange(num_features):

# 		for strain in xrange(num_strains):

# 			rect = ax.bar(ind + f * (num_strains * bar_width + sep) + strain * (bar_width+0.15), 
# 				percent_avg[f, :, strain], bar_width,
# 				yerr=[[0,0], percent_std[f, :, strain]],	
# 				label=strain_names[strain],
# 				lw=1., 
# 				color=colors[strain],
# 				edgecolor=colors[strain],
# 				capsize=2,
# 				ecolor=colors[strain], 
# 				)


# 	plt.xlim(xlims)
# 	plt.ylim(ylims)

# 	xticks = [idx + f * (num_strains * bar_width + sep) + (num_strains * (bar_width + 0.15)) / 2 \
# 				for idx in ind for f in range(num_features)]
	
# 	yticks = np.linspace(0, 1, 5+1)

# 	ax.set_xticks(xticks)
# 	ax.set_yticks(yticks)
# 	ax.xaxis.set_ticks_position('bottom')
# 	ax.yaxis.set_ticks_position('left')
# 	ax.spines['top'].set_visible(False)
# 	ax.spines['right'].set_visible(False)
# 	ax.tick_params(axis='both', labelsize=14)

# 	ax.get_xaxis().tick_bottom()
# 	ax.get_yaxis().tick_left()


# 	xlabels = ['Loco', 'ASP', 'ASP+N'] * 2
# 	# xlabels = ['ASC', 'ASP', 'ASP+C'] * 2
# 	ylabels = [str(x) + '$\%$' for x in range(0, 101, 20)] 
# 	ax.set_xticklabels(xlabels)
# 	ax.xaxis.set_ticks_position('none') 
# 	ax.set_yticklabels(ylabels)


# 	# horizontal line at 100%
# 	plt.plot([xlims[0], xlims[1]], [1, 1], '--', c='k', lw=0.5, zorder=0)

# 	if 1:
# 		# # yticks lines
# 		ax.spines['left'].set_visible(False)
# 		ax.tick_params(axis='y', which='major', pad=10)
# 		for y in yticks:
# 			ax.plot(xlims, [y] * len(xlims), "--", lw=0.75, color='.3', zorder=0)


# 	# Shrink current axis by 20%, allow space to custom legend
# 	box = ax.get_position()
# 	ax.set_position([box.x0, box.y0, box.width*0.93, box.height])


# 	# custom legend
# 	# handles, labels = ax.get_legend_handles_labels()
# 	# mylist = zip(handles, labels)
# 	mylist = []
# 	for num, color in enumerate(colors):
# 		p3 = patches.Rectangle((0, 0), 0, 0, fc=color, ec=color)
# 		mylist.append([p3, '%s' %strain_names[num]]) 

# 	h0, l0 = zip(*mylist)
# 	ax.legend(h0, l0, bbox_to_anchor=[1.21, 0.87], frameon=False, prop={'size':10})


# 	# # # legend with colored labels
# 	# # col = 0 		# color counter
# 	# # for l in xrange(num_strains):
# 	# # 	fig.text(.93, .75-.03*col, '%s' %(strain_names[l]), 
# 	# # 		fontsize=10,
# 	# # 		color=colors[col],
# 	# # 		horizontalalignment='center'
# 	# # 		)
# 	# # 	col +=1

# 	# # # custom legend box	
# 	# # frame = patches.Rectangle((0.88, 0.28), 0.1, .51, 
# 	# # 				facecolor='none', edgecolor='0.3',
# 	# # 				transform=ax.figure.transFigure, 
# 	# # 				clip_on=False,
# 	# # 				zorder=0
# 	# # 				)
	
# 	# # ax.add_patch(frame)  	



# 	# # axis labels
# 	fig.text(.23, .02, levels[0], fontsize=16)
# 	fig.text(.63, .02, levels[1], fontsize=16)
# 	fig.text(.03, .55, 'Accuracy', fontsize=16, rotation='vertical')

# 	# title
# 	plot_title = '#K-means master classifier accuracy\nstrain averages ($\pm$ stdev), %d bootstrap trials\nmousedays/individuals, %d features, %d strains' %(num_trials, num_features, num_strains)
# 	fig.text(0.05, 0.93, plot_title,
# 		fontsize=8
# 		)


# 	print "saving plot.."
# 	filename = dirname_out + base_name + '_16strains_2x3.pdf'
# 	plt.savefig(filename)
# 	plt.close()

# 	print "saved to %s" %filename
	

# 	if BIN_FILE:
# 		fname = dirname_out + base_name + '_means.npy'
# 		np.save(fname, percent_avg)
# 		fname2 = dirname_out + base_name + '_stds.npy'
# 		np.save(fname2, percent_std)
	
# 	# write data to file
# 	if CSV_FILE:
# 		data_file = dirname_out + base_name + '.txt'

# 		print 'saving data to file:\n%s' %data_file

# 		with file(data_file, 'w') as outfile:
# 			# I'm writing a header here just for the sake of readability
# 			# Any line starting with "#" will be ignored by numpy.loadtxt
# 			outfile.write(plot_title)
# 			outfile.write('\n\n#%d features:\n%s\n' %(num_features, features))
# 			outfile.write('\n#%d strains:\n%s\n' %(num_strains, strain_dict))
# 			outfile.write('\n#%d levels:\n%s\n\n' %(num_levels, levels))

# 			outfile.write('#Total individuals: %d\n' %num_mice)
# 			outfile.write('Total mousedays: %d\n' %num_mousedays)
# 			outfile.write('Test Set mousedays: %d\n' %tot_md_test.sum())
			

# 			# stop
# 			outfile.write('\n\n')
# 			for f in xrange(num_features):

# 				# Writing out a break to indicate different features
# 				outfile.write('\n#%s\n' %features[f])	

# 				outfile.write('Correctly labeled mousedays/individuals, by strain:\n')	
# 				outfile.write('%s\n\n' %percent_avg[f])
# 				# values in left-justified columns 7 characters in width with 2 decimal places.  
# 				# np.savetxt(outfile, percent_avg[f], fmt='%-7.4f')
				
# 				outfile.write('Stdev:\n%s\n\n' %percent_std[f])

# 				md1 = M[f,:,1,:].sum(axis=1).mean() / tot_md_test.sum()
# 				m1 = M[f,:,0,:].sum(axis=1).mean() / tot_mice.sum()
# 				# outfile.write('16 strains average:\n%s\n' %percent_avg[f].mean(axis=1))
# 				outfile.write('16 strains average:\n%1.4f  %1.4f\n\n' %(md1, m1))
				
# 				md2 = np.std(M[f, :, 1, :].sum(axis=1) / tot_md_test.sum())
# 				m2 = np.std(M[f, :, 0, :].sum(axis=1) / tot_mice.sum())
# 				# outfile.write('Stdev:\n%s\n' %percent_avg[f].std(axis=1))
# 				outfile.write('Stdev:\n%1.4f  %1.4f\n\n\n' %(md2, m2))
				
				
				


