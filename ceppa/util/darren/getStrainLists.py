"""
Last checked for relevance: 2013_11_13
This will extract important info about what the mouseNumbers are and what group they belong to.
"""
import numpy as np #we use np.argsort below
from ceppa.util.darren import bunch
# from ceppa.util.darren.getFileNamesForExperimentMouseDay import * # Given an experiment, mouse, and day, what are the LE, ME, and PE file names 


def get_nest_position_record(list_of_MSI_file_names, MSI_group_number_to_group_name_dictionary, delimiter=','):
	MSI_column_of_this = {
		'round_number' : 0,
		'DAQ_system': 2,
		'enclosure': 3,
		'day_number': 4,
		'mouse_number': 6,
		'MSI_group_number' : 7,
		'NLX' : 19,
		'NLY': 20,
	}
	usecols = [MSI_column_of_this[variable] for index, variable in enumerate(MSI_column_of_this.keys())]
	index_of_variable = {variable:index for index, variable in enumerate(MSI_column_of_this.keys())}
	mouse_number_col_index = 6
	group_col_index = 7
	sys_col_index = 2
	enc_col_index = 3
	day_col_index = 4

	X = {} # X is a dictionary that, upon taking in an MSI_group_number gives out another dictionary, which, upon taking in a mouseNumber, gives another dictionary that takes in dayNumber
	mouse_number_to_round_number_dictionary = {}
	for fileName in list_of_MSI_file_names:
		repetitiveMouseNumbersWithStrain = np.genfromtxt(
			fileName, 
			delimiter=delimiter,  
			usecols=usecols,
			skip_header=1,
			dtype=np.int
		)
		for row_number, row in enumerate(repetitiveMouseNumbersWithStrain):

			mouse_number = row[index_of_variable['mouse_number']]
			MSI_group_number = row[index_of_variable['MSI_group_number']]
			if MSI_group_number != 0:
				day_number = row[index_of_variable['day_number']]
				round_number = row[index_of_variable['round_number']]
				if mouse_number not in mouse_number_to_round_number_dictionary:
					mouse_number_to_round_number_dictionary[mouse_number] = round_number
				group_name = MSI_group_number_to_group_name_dictionary[MSI_group_number]

				if group_name not in X: # the group_name has not been seen before 
					X[group_name] = {} # initialize a dictionary corresponding to that group_number 
				if mouse_number not in X[group_name]: # this group has never seen this mouse_number before
					X[group_name][mouse_number] = {}
				if day_number in X[group_name][mouse_number]:
					raise Exception("This group, mouse, and day triplet occurs on multiple lines from the various MSIFiles")

				X[group_name][mouse_number][day_number] = bunch.Bunch()
				for key in MSI_column_of_this.keys():
					setattr(X[group_name][mouse_number][day_number], key, row[index_of_variable[key]])
		
	output = bunch.Bunch()
	output.group_name_to_mouse_number_list_dictionary = {group_name:sorted(X[group_name].keys()) for group_name in X.keys()}
	output.X = X
	output.mouse_number_to_round_number_dictionary = mouse_number_to_round_number_dictionary
	#print mouse_number_to_round_number_dictionary
	#print "index_of_variable = %s"%index_of_variable
	return output


def group_name_to_mouse_number_list_from_MSIFile(list_of_MSI_file_names, MSI_group_number_to_group_name_dictionary, delimiter=','):
	MSI_column_of_this = {
		'round_number' : 0,
		'DAQ_system': 2,
		'enclosure': 3,
		'day_number': 4,
		'mouse_number': 6,
		'MSI_group_number' : 7,
	}
	usecols = [MSI_column_of_this[variable] for index, variable in enumerate(MSI_column_of_this.keys())]
	index_of_variable = {variable:index for index, variable in enumerate(MSI_column_of_this.keys())}
	mouse_number_col_index = 6
	group_col_index = 7
	sys_col_index = 2
	enc_col_index = 3
	day_col_index = 4
	
	X = {} # X is a dictionary that, upon taking in an MSI_group_number gives out another dictionary, which, upon taking in a mouseNumber, gives another dictionary that takes in dayNumber
	mouse_number_to_round_number_dictionary = {}
	for fileName in list_of_MSI_file_names:
		repetitiveMouseNumbersWithStrain = np.genfromtxt(
			fileName, 
			delimiter=delimiter,  
			usecols=usecols,
			skip_header=1,
			dtype=np.int
		)

		for row_number, row in enumerate(repetitiveMouseNumbersWithStrain):
			mouse_number = row[index_of_variable['mouse_number']]
			MSI_group_number = row[index_of_variable['MSI_group_number']]
			if MSI_group_number != 0:
				day_number = row[index_of_variable['day_number']]
				round_number = row[index_of_variable['round_number']]
				if mouse_number not in mouse_number_to_round_number_dictionary:
					mouse_number_to_round_number_dictionary[mouse_number] = round_number
				group_name = MSI_group_number_to_group_name_dictionary[MSI_group_number]

				if group_name not in X: # the group_name has not been seen before 
					X[group_name] = {} # initialize a dictionary corresponding to that group_number 
				if mouse_number not in X[group_name]: # this group has never seen this mouse_number before
					X[group_name][mouse_number] = {}
				if day_number in X[group_name][mouse_number]:
					raise Exception("This group, mouse, and day triplet occurs on multiple lines from the various MSIFiles")

				X[group_name][mouse_number][day_number] = bunch.Bunch()
				for key in MSI_column_of_this.keys():
					setattr(X[group_name][mouse_number][day_number], key, row[index_of_variable[key]])
		
	output = bunch.Bunch()
	output.group_name_to_mouse_number_list_dictionary = {group_name:sorted(X[group_name].keys()) for group_name in X.keys()}
	output.X = X
	output.mouse_number_to_round_number_dictionary = mouse_number_to_round_number_dictionary
	#print mouse_number_to_round_number_dictionary
	#print "index_of_variable = %s"%index_of_variable
	return output




def getStrainListsFromThisMSIFile(fileName):
	#BEGIN forming mouseNumberStrain, a two Column matrix with column 1 is mouseNumber, column 2 is strain (0-16 inclusive), sorted by mouseNumber
	mouse_number_col_index = 6
	group_col_index = 7
	sys_col_index = 2
	enc_col_index = 3

	repetitiveMouseNumbersWithStrain=np.genfromtxt(
		fileName, 
		delimiter=',', 
		usecols=(mouse_number_col_index, group_col_index, sys_col_index, enc_col_index),
		skip_header=1,
		dtype=np.int
	)
	
	u, indices = np.unique(repetitiveMouseNumbersWithStrain[:,0], return_index=True)
	mouseNumberStrain = repetitiveMouseNumbersWithStrain[indices,:]
	print "This may help associate mousenumber to sys and enc:"
	for i in xrange(mouseNumberStrain.shape[0]):    
		print "            %d:(%d,%d)," % (mouseNumberStrain[i,0], mouseNumberStrain[i,2], mouseNumberStrain[i,3])
	# mouseNumberStrain = mouseNumberStrain[:,:2]           # this has been commented out since for Stress3Study. 03/2014
															# to include System number and Enclosure in return array
	#END forming mouseNumberStrain, a two Column matrix with column 1 is mouseNumber, column 2 is strain (0-16 inclusive),  sorted by mouseNumber

	#BEGIN forming mouseNumberStrain, a two Column matrix with column 1 being strain, and column 2 being mouseNumber, rows sorted by strain
	sortIndices = np.argsort(mouseNumberStrain[:,1], kind='mergesort') #mergesort is stable
	strainMouseNumber=mouseNumberStrain[sortIndices,:]
	print "Here is strainMouseNumber"
	print strainMouseNumber
	#END forming mouseNumberStrain, a two Column matrix with column 1 being strain, and columns to being mouseNumber, rows sorted by strain

	#BEGIN forming the dictionary strainLists, such that strainLists[5] is a list of all mice of strain 5, etc.
	strainLists={}
	for strain in range(1,3+1):
		indices=np.nonzero(strainMouseNumber[:,1]==strain)[0]
		strainLists[strain]=strainMouseNumber[indices,0]
		print "Here are all the mice that are strain %d"%strain
		print strainLists[strain]
	#BEGIN forming the dictionary strainLists, such that strainLists[5] is a list of all mice of strain 5, etc.
	return strainLists, strainMouseNumber


def getStrainLists():
	#BEGIN forming mouseNumberStrain, a two Column matrix with column 1 is mouseNumber, column 2 is strain (0-16 inclusive), sorted by mouseNumber
	mouseNumberStrain=np.zeros((0,2),dtype='int')
	for roundNumber in range(2,8+1):
		#repetitiveMouseNumbers=np.genfromtxt("../Experiments/SS_Data_051905_FV/MSIFiles/StructFormat/aflSSe1r%d_MSI_FF.csv"%roundNumber,delimiter=',', usecols=(6), skip_header=1, dtype=np.int)
		repetitiveMouseNumbersWithStrain=np.genfromtxt(dataDirRoot()+"Experiments/SS_Data_051905_FV/MSIFiles/StructFormat/aflSSe1r%d_MSI_FF.csv"%roundNumber,delimiter=',', usecols=(6,7), skip_header=1, dtype=np.int)
		u, indices = np.unique(repetitiveMouseNumbersWithStrain[:,0], return_index=True)
		#print repetitiveMouseNumbersWithStrain[indices,:]
		mouseNumberStrain=np.vstack((mouseNumberStrain,repetitiveMouseNumbersWithStrain[indices,:]))
	#print mouseNumberStrain.shape
	#END forming mouseNumberStrain, a two Column matrix with column 1 is mouseNumber, column 2 is strain (0-16 inclusive),  sorted by mouseNumber

	#BEGIN forming mouseNumberStrain, a two Column matrix with column 1 being strain, and columns to being mouseNumber, rows sorted by strain
	sortIndices = np.argsort(mouseNumberStrain[:,1], kind='mergesort') #mergesort is stable
	strainMouseNumber=mouseNumberStrain[sortIndices,:]
	#print strainMouseNumber
	#END forming mouseNumberStrain, a two Column matrix with column 1 being strain, and columns to being mouseNumber, rows sorted by strain

	#BEGIN forming the dictionary strainLists, such that strainLists[5] is a list of all mice of strain 5, etc.
	strainLists={}
	for strain in range(17):
		indices=np.nonzero(strainMouseNumber[:,1]==strain)[0]
		strainLists[strain]=strainMouseNumber[indices,0]
		#print "Here are all the mice that are strain %d"%strain
		#print strainLists[strain]
	#BEGIN forming the dictionary strainLists, such that strainLists[5] is a list of all mice of strain 5, etc.
	return strainLists


def getRoundNumberAndMouseNumberForStrainIndividual(strain,individual):
	mouseNumber=strainLists[strain][individual]
	#BEGIN get roundNumber for this individual
	if mouseNumber in [7116, 7216, 7316]:
		roundNumber=6 #bizarrely, miceNumbers 7116, 7216, 7316 happen in round 6, not 7
	else:
		roundNumber=mouseNumber/1000 #mainly if you know the mouseNumber, you know the roundNumber is the thousands-digit
	#END get roundNumber for this individual
	if not mouseNumber % 100 == strain:
		print "ERROR: something the matter: mouseNumber mod 100 should equal the strain"
		print "mouseNumber = %d, whereas strain = %d" % (mouseNumber, strain)
		sys.exit(-1)
	return roundNumber, mouseNumber


def theNumberOfIndividualsOfStrain(strain):
	"""Take a strain (integer from 0 to 16 inclusive) and return the number of distinct mice of that strain in the strainSurvey"""
	if strain not in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]:
		print "ERROR:  this is not a valid strain:"
		print strain
		sys.exit(-1)
	numInstances=12
	if strain==0:
		numInstances=6
	elif strain==6:
		numInstances=11
	elif strain==12:
		numInstances=10
	elif strain==13:
		numInstances=11
	elif strain==16:
		numInstances=14
	return numInstances



if __name__=="__main__":
	print "getStrainLists.py is being run as the main script, i.e. we are going to perform a unit test of the module."
	strainLists=getStrainLists()
	print strainLists
	print "If you are reading this, no errors were found."
