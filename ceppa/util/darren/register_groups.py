import numpy as np
import os
import sys
import inspect

from ceppa.group import Group
import getStrainLists

"""
D. Rhea, 2013
Here's Darren core stuff. Experiment initialization and loading stuff.
These are Experiment methods.

Tecott Lab UCSF
"""


def add_group_attributes(self):
    """
    usually this is invoked at the end of an experiments __init__ definition
    """ 
    # # ticket: hack for delimiter on MSIFile. 
    delimiter = ','
    if self.name == 'DREADDExperiment':
        delimiter = '\t'

    output = getStrainLists.group_name_to_mouse_number_list_from_MSIFile(
        list_of_MSI_file_names=self.list_of_MSI_file_names, 
        MSI_group_number_to_group_name_dictionary=self.MSI_group_number_to_group_name_dictionary,
        delimiter=delimiter
    )

    self.output2 = getStrainLists.get_nest_position_record(
        list_of_MSI_file_names=self.list_of_MSI_file_names, 
        MSI_group_number_to_group_name_dictionary=self.MSI_group_number_to_group_name_dictionary,
        delimiter=','
    )

    self.group_name_to_mouse_number_list_dictionary = output.group_name_to_mouse_number_list_dictionary
    self.mouse_number_to_round_number_dictionary = output.mouse_number_to_round_number_dictionary
    self.groups = [] # a list registering all groups in the experiment
    self.group_numbered = {} # the groups of the experiment indexed by number / index.  Use sparingly 
    self.group_named = {} # the groups indexed by name.  
    
    for groupNumber, name in enumerate(self.group_names):
        G = Group() # make a Group
        G.name = name # of that name
        G.number = groupNumber # and groupNumber, for legacy reasons
        G.experiment = self
        G.register_and_populate()       # add mice and mousedays
        
    for group in self.groups:
        for M in group.individuals:
            M.add_stuff_to_mouse()    
            for MD in M.mouse_days:
                if MD.dayNumber in M.experiment.daysToUse:   # this is to accomodate ZeroLightExperiment corrupt messy data
                                                            # Sys A and Sys B failed.  
                    MD.add_stuff_to_mouse_day()
                    self.getChowWaterFromMSIFile(MD)        # add bw, food, water quantitites
            
    # fileUtilities.mkdirIfNonexistent(self.derivedDataDirectory()) # make sure the derivedDataDirectory exists
    self.allPossibleGroupNumbers = [group.number for group in self.groups]  # for legacy purposes
    self.groupNames={}
    for group in self.groups:
        self.groupNames[group.number]=group.name


def getChowWaterFromMSIFile(self, mouse_day):
    """
    given an experiment (via method call binding) and a mouse_day, adds on 
    the attributes of chow_eaten_grams, water_drunk_grams to mouse_day,
    and body_weight_start_of_experiment_grams, body_weight_end_of_experiment_grams, body_weight_average_grams to mouse
    """
    # # ticket: hack for delimiter on MSIFile. 
    delimiter = ','
    if self.name == 'DREADDExperiment':
        delimiter = '\t'

    try:
        roundNumber=mouse_day.roundNumber
        MSIFile = mouse_day.individual.MSIFile
    except:
        roundNumber = 1 # roundNumber not so meaningful anywhere but StrainSurvey
        assert not self.short_name == 'StrainSurvey', 'Error: StrainSurvey should never wind up here.' 
        MSIFile = mouse_day.individual.experiment.MSIFile # this kind of experiment should have only one MSIFile, attached to the experiment itself, unlike StrainSurvey

    dayNumber = mouse_day.dayNumber
    mouseNumber = mouse_day.mouseNumber

    try:
        dayNumberMouseNumber = self.dayNumberMouseNumber[roundNumber] # MSIFile info might be cached attached to the experiment indexed by round, check if it is
    except:
        if not hasattr(self, 'dayNumberMouseNumber'):
            self.dayNumberMouseNumber = {}
        self.dayNumberMouseNumber[roundNumber] = np.genfromtxt(MSIFile, delimiter=delimiter, usecols=(4,6), skip_header=1, dtype=np.int)
        dayNumberMouseNumber=self.dayNumberMouseNumber[roundNumber]

    indices=np.nonzero(np.logical_and(dayNumberMouseNumber[:,0]==dayNumber, dayNumberMouseNumber[:,1]==mouseNumber))[0]
    if len(indices)!=1:
        print "something is wrong: mouseNumber %d dayNumber %d occurs on none or several lines of the MSIFile %s"%(mouseNumber, dayNumber, MSIFile) 
        print "Namely these lines"
        print indices
        sys.exit(-1)
    rowIndexOfMSIMatrix=indices[0]
    
    try:
        wholeMSIFile = self.wholeMSIFile[roundNumber]
    except:
        if not hasattr(self, 'wholeMSIFile'):
            self.wholeMSIFile = {}
        self.wholeMSIFile[roundNumber]=np.genfromtxt(MSIFile, delimiter=delimiter, skip_header=1, dtype=np.double)
        wholeMSIFile = self.wholeMSIFile[roundNumber]

    correct_row = wholeMSIFile[rowIndexOfMSIMatrix, :]

    mouse_day.chow_eaten_grams = correct_row[13]-correct_row[14]
    mouse_day.water_drunk_grams = correct_row[16]-correct_row[17]
    
    mouse_day.individual.body_weight_end_of_experiment_grams = correct_row[11]
    mouse_day.individual.body_weight_start_of_experiment_grams = correct_row[10]
    mouse_day.individual.body_weight_average_grams = (mouse_day.individual.body_weight_end_of_experiment_grams + mouse_day.individual.body_weight_start_of_experiment_grams) / 2.0
    
    mouse_day.chow_intake_grams_per_30g_body_weight = mouse_day.chow_eaten_grams / mouse_day.individual.body_weight_average_grams * 30.0
    mouse_day.water_intake_grams_per_30g_body_weight = mouse_day.water_drunk_grams / mouse_day.individual.body_weight_average_grams * 30.0
    
    mouse_day.body_weight_end_of_experiment_grams = mouse_day.individual.body_weight_end_of_experiment_grams
    mouse_day.body_weight_start_of_experiment_grams = mouse_day.individual.body_weight_start_of_experiment_grams
    mouse_day.body_weight_average_grams = mouse_day.individual.body_weight_average_grams


# def mouseFromAbstractIndices(self, groupNumber, individualNumber):   # this is so that old-school code will still run
#     return self.group_numbered[groupNumber].individuals[individualNumber]
    

# def mouseDayFromAbstractIndices(self, groupNumber, dayNumber, individualNumber): # this is so that old-school code will still run
#     # print "Requested was groupNumber=%d, dayNumber=%d, individualNumber=%d"%(groupNumber, dayNumber, individualNumber)
#     temp = self.group_numbered[groupNumber].individuals[individualNumber].mouse_day_number[dayNumber]
#     return temp


# # # We are going to enforce that any subclass of Experiment has a method with this name and with this signature:
# # # def mouseDayFromAbstractIndices(self, groupNumber, dayNumber, individualNumber):
# def checkSignatureOfMouseDayFromAbstractIndices(self):
#     signature=inspect.getargspec(self.mouseDayFromAbstractIndices)[0]
#     assert signature == ['self', 'groupNumber', 'dayNumber', 'individualNumber'], 'mouseDayFromAbstractIndices does not have the right signature'

    
# def getRandomGroupDayIndividualNumbers(self): # so often we just want to look at a random group day individual
#     """
#     Typical invocation:
#     randomGroupNumber, randomDayNumber, randomIndividualNumber = E.getRandomGroupDayIndividualNumbers()
#     """
#     randomGroupIndex=np.random.randint(len(self.allPossibleGroupNumbers))
#     randomGroupNumber=self.allPossibleGroupNumbers[randomGroupIndex]
#     print "randomGroupNumber = %d"%randomGroupNumber
#     randomDayIndex=np.random.randint(len(self.allPossibleDayNumbers))
#     randomDayNumber=self.allPossibleDayNumbers[randomDayIndex]
#     print "randomDayNumber = %d"%randomDayNumber
#     randomIndividualNumber=np.random.randint(self.numberOfIndividualsInGroup[randomGroupNumber])
#     print "randomIndividualNumber = %d"%randomIndividualNumber
#     return randomGroupNumber, randomDayNumber, randomIndividualNumber
 

# # # end core Darren Stuff
