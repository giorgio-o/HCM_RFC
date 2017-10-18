import sys
import os
import time

from experiment import Experiment
from ceppa.util.darren import getStrainLists
from ceppa.util.darren.getFileNamesForExperimentMouseDay import dataDirRoot


"""
G.Onnis, 03.2017
    
Tecott Lab UCSF
"""


class HiFat1Experiment(Experiment): # subclass of Experiment

    def __init__(self, name='HiFat1Experiment', IST=20., FBT=30., WBT=30., MBVT=1., MBDT=5., MBTT=0.2, IGNORE_MD=True, FULLNAME=True, use_days='acclimated'): 
        
        self.exp_dir = dataDirRoot() + 'Experiments/HiFat1/'

        Experiment.__init__(self, name, IST, FBT, WBT, MBVT, MBDT, MBTT, IGNORE_MD, FULLNAME, use_days) # have to explicitly call the superclass initializer

        self.short_name = 'HFD1_Exp'
        self.num_strains = 4
        self.initialize()


    def __str__(self):  
        return self.short_name


    def initialize(self):
        print "initializing %s.." %self.name 
        # names for file i/o
        self.group_names = [
                            'WTHF', 	# Wild Type/ High Fat
                            '2CHF', 	# KnockOut/ High Fat
                            'WTLF', 	# Wild Type/ Low Fat
                            '2CLF', 	# KnockOut/ Low Fat
                            ]
        # You need to tell us a list of all MSIFiles:
        self.list_of_MSI_file_names = [
                self.exp_dir + "Round%d/HFD_DaySummary/hcmHFDe1r%d_MSI_FF.csv"%(roundNumber, roundNumber) \
                for roundNumber in [1, 2]]
        # You need to tell us the decoding from MSI_files' group number codes to more human readable group names:
        # self.MSI_group_number_to_group_name_dictionary = dict(zip(range(len(self.group_names)), self.group_names))
        self.MSI_group_number_to_group_name_dictionary = {
	        	1: 'WTHF', 2: '2CHF', 3: 'WTLF', 4: '2CLF'
	            }
        self.numberOfIndividualsInGroup = {
	            1: 17, 2: 16, 3: 15, 4: 16
	            } 
        self.allPossibleGroupNumbers = range(1, 4+1)
        self.allPossibleDayNumbers = range(1, 16+1) 	# Standard HCM, all special diet
        self.nonAcclimationDayNumbers = range(5, 16+1)
        self.acclimationDayNumbers = range(1, 4+1)
        self.acclimatedDayNumbers = range(5, 16+1)
        self.allExperimentDayNumbers = range(5, 16+1)
        if self.use_days in ['acclimated', 'all']:
            self.daysToUse = self.acclimatedDayNumbers

        # IST
        self.IST_in_minutes_by_group_name = {name: self.IST for name in self.group_names}
        #strain to mousenumber, roundnumber
        output = getStrainLists.group_name_to_mouse_number_list_from_MSIFile(
            list_of_MSI_file_names=self.list_of_MSI_file_names, 
            MSI_group_number_to_group_name_dictionary=self.MSI_group_number_to_group_name_dictionary
        )
        self.group_name_to_mouse_number_list_dictionary = output.group_name_to_mouse_number_list_dictionary
        self.mouse_number_to_round_number_dictionary = output.mouse_number_to_round_number_dictionary   

        # add ignored mice and mousedays
        if self.IGNORE_MD:
	        self.add_ignored_data_labels()
        else:
            print "using all mousedays.."
        # add groups, mice, mousedays objects
        self.add_group_attributes()      
        # count mice in admissible groups
        self.count_mice()
        # count admissible mousedays according to admissible groups, ignored mice and use_days 
        self.count_mousedays()
        # group plot settings
        self.get_groups_settings()

        self.assertProperInitialization() # this must be the last in __init__


    def add_ignored_data_labels(self):
        """ defines mouseday to ignore based on experimenter's 
            observation of data_quality plots
        """
        # load flagged from binary generation
        self.flag_ignored_mousedays()
        # after looking at data quality plots, remove these mousedays from flagged list
        remove_from_flagged = [         # (mouseNum, dayNum)
            (5736, 5),
            (5736, 6),
            (5736, 7),
            (5736, 10)
            ]
        confirmed = [x for x in self.flagged if x not in remove_from_flagged]
        # and add these
        md_added_for_removal = [
            # (5704, 5)
            ]
        confirmed.extend(md_added_for_removal)
        
        # completely ignorable mice
        counts = dict()
        for x, a in confirmed:
            counts[x] = counts.get(x, 0) + 1
        # mouse_to_ignore = [m for  in d.iterkeys() if d[key]==len(self.daysToUse)]
        mouse_to_ignore = [key for key in counts.iterkeys() if counts[key]==len(self.daysToUse)]
        # also, the experimenter does not want these mice
        mice_added_for_removal = [
            ]
        
        # here the final list of mice and mousedays to ignore
        mouse_to_ignore.extend(mice_added_for_removal)
        md_to_ignore = [(x, a) for x, a in confirmed if x not in mouse_to_ignore]
        self.mouseNumbers_to_ignore = tuple(mouse_to_ignore)
        self.mouseNumbersAndDays_to_ignore = tuple(md_to_ignore)
        

    def get_groups_settings(self):        
        # strain_names for plotting
        self.group_number_to_full_group_name_dict = {
	        1: 'WTHF', 2: '2CHF', 3: 'WTLF', 4: '2CLF'
	        }
        self.strain_dict = {key: self.group_number_to_full_group_name_dict[key] for key in range(1, 5)}
        self.strain_names = [name for name in self.MSI_group_number_to_group_name_dictionary.values()]
        if self.FULLNAME:
            self.strain_names = [name for name in self.group_number_to_full_group_name_dict.values()]
        # selected raster individuals
        self.selected_individuals = [
            ] 
        self.individual_days_dict={}
        # for k in self.allPossibleGroupNumbers:
        #     self.individual_days_dict[k] = (self.selected_individuals[k], _days)
        # selected rasters for individuals, order is important:
        self.selected_individuals_sub = [
            ]
        self.individual_days_dict_sub={}
        # for k in xrange(12):
        #     self.individual_days_dict_sub[k] = (self.selected_individuals_sub[k], range(9, 14))




	
