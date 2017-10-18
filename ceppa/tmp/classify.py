from Experiments import StrainSurveyExperiment
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import preprocessing, metrics
from sklearn.model_selection import KFold, cross_val_score

import numpy as np 
import matplotlib.pyplot as plt 
import itertools
import os
import seaborn as sns
import time
import my_utils
"""
G.A.Onnis, 11.2016

Tecott Lab UCSF
"""


def Kfold_score(experiment, clf, name, feature='ASP', n_splits=10):

	E = experiment
	num_strains = E.num_strains

	dir_out = E.derived_dir + 'learning/classification/pairwise/%s_data/' %feature
	if not os.path.isdir(dir_out): os.makedirs(dir_out)

	fname1, fname2 = ['%s_%s_%s' %(feature, name, text) for text in ['_pairwise_score.npy', '_pairwise_score_std.npy']]
	
	try:
		score = np.load(dir_out + fname1)
		score_std = np.load(dir_out + fname2)
		print "loaded %s, 11d %s vector data" %(name, feature)	
	except IOError:
		cstart = time.clock()
		arr, arr_labels = E.generate_feature_vectors(feature, GET_AVGS=False)
		feature_names = ['%sbin%d' %(feature, n) for n in xrange(11)]
		
		print "computing %s, 11d %s vector.." %(name, feature)
		k_fold = KFold(n_splits=n_splits, shuffle=True)
		score = np.ones((num_strains, num_strains))
		score_std = np.zeros((num_strains, num_strains))
		for strain1, strain2 in itertools.combinations(range(num_strains), 2):
			print "strain%d vs. strain%d, %s, %s, 11d %s vector\n%s" %(strain1, strain2, k_fold, name, feature, clf)
			X, Y = my_utils.get_dataset_two_strains_and_shuffle(
				arr, arr_labels, strain1, strain2)

			cv_scores = cross_val_score(clf, X, Y, cv=k_fold, n_jobs=-1)
			score[strain1, strain2] = cv_scores.mean()
			score_std[strain1, strain2] = cv_scores.std()

		np.save(dir_out + fname1, score)
		np.save(dir_out + fname2, score_std)
		cstop = time.clock()
		print "%s took %1.2fs" %(name, (cstop-cstart)/60.)
		print "binary output saved to: %s" %dir_out

	return score, score_std


def plot_score(experiment, name, feature, score, score_std, n_splits):
	num_strains = score.shape[0]
	mask = np.zeros_like(score, dtype=bool)
	mask[np.tril_indices_from(mask)] = True

	fig, (ax1, ax2) = plt.subplots(1, 2, figsize= (12, 8))

	g1 = sns.heatmap(score, mask=mask, cmap=plt.get_cmap("viridis"), linewidths=0.5, 
		vmin=.8, vmax=1, square=True, annot=False, fmt='', cbar_kws={'shrink':.5}, ax=ax1)

	g2 = sns.heatmap(score_std, mask=mask, linewidths=.5, 
		vmin=0, vmax=0.12, square=True, annot=False, fmt='', cbar_kws={'shrink':.5},ax=ax2)

	[g.set_xticklabels(E.strain_names, fontsize=8, rotation=315, ha='left', y=0.015) for g in [g1, g2]]
	[g.set_yticklabels(E.strain_names[::-1], fontsize=8, rotation=0) for g in [g1, g2]]
	[ax.set_aspect('equal', adjustable='box') for ax in [ax1, ax2]]
	
	ax1.set_xlabel('Strain')
	ax1.set_ylabel('Strain')
	ax1.set_title('avg score=%1.4f' %score[~mask].mean())
	ax2.set_title('avg stdev=%1.4f' %score_std[~mask].mean())

	title = 'Classification - Pairwise %s\nusing %s 11D feature vectors\n%d-fold cross-validated score on mousedays' \
		%(name, feature, n_splits)
	fig.text(.5, 0.77, title, fontsize=14, ha='center', transform=fig.transFigure)

	dir_out = E.plots_dir + 'learning/classification/pairwise/'
	if not os.path.isdir(dir_out): os.makedirs(dir_out)
	fname = dir_out + '%s_pairwise_%s_score.pdf' %(feature, name)
	fig.savefig(fname, bbox_inches='tight')
	plt.close()
	print "figures output saved to: %s" %fname


def run(experiment, feature='ASP', n_splits=10):
	E = experiment	
	# params
	# n_splits = 10 		#Kfold
	n_neighbors = 3 	#KNN
	C = 1.0				#SVM
	n_estimators = 30	#Random forest
	classifiers = [
		LogisticRegression(),
		# KNeighborsClassifier(n_neighbors),
		# SVC(kernel='linear', C=C),
		# SVC(gamma=2, C=1),
		# SVC(kernel='poly', degree=3, C=C),
		# RandomForestClassifier(n_estimators=n_estimators),
		# MLPClassifier(alpha=1.0),
		# GaussianNB()
		]
	names = ["Logistic Regression"]#, "Nearest Neighbors", "Linear SVM", "RBF SVM", "Poly SVM", 
		# "Random Forest", "Neural Net", "Gaussian Naive Bayes"]

	for name, clf in zip(names, classifiers):
		score, score_std = Kfold_score(experiment=E, clf=clf, name=name,
								feature=feature, n_splits=n_splits)
		plot_score(E, name, feature, score, score_std, n_splits)


if __name__ == '__main__':
	E = StrainSurveyExperiment.StrainSurveyExperiment()
	run(E, feature='ASP')




