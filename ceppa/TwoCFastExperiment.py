import sys
import os
import time
import numpy as np
from experiment import Experiment
from ceppa.util.darren import getStrainLists
from ceppa.util.darren.getFileNamesForExperimentMouseDay import dataDirRoot


"""
G.Onnis, 03.2017
    
Tecott Lab UCSF
"""


class TwoCFastExperiment(Experiment): # subclass of Experiment

    def __init__(self, name='TwoCFastExperiment', IST=20., FBT=30., WBT=30., MBVT=1., MBDT=5., MBTT=0.2, 
            IGNORE_MD=False, FULLNAME=True, BIN_SHIFT=False, use_days='acclimated'):
        
        self.exp_dir = dataDirRoot() + 'Experiments/2CFast/'

        Experiment.__init__(self, name, IST, FBT, WBT, MBVT, MBDT, MBTT, IGNORE_MD, FULLNAME, BIN_SHIFT, use_days) # have to explicitly call the superclass initializer

        self.short_name = '2CFast'
        self.num_strains = 2
        self.initialize()


    def __str__(self):  
        return self.short_name


    def initialize(self):
        print "initializing %s.." %self.name
        # names for file i/o
        self.group_names = [
                            '2CWT', 	# Wild Type/ High Fat
                            '2CKO', 	# KnockOut/ High Fat
                            ]
        # You need to tell us a list of all MSIFiles:
        self.list_of_MSI_file_names = [self.exp_dir + 'hcm2CFASTe1r1_MSI_FF.csv']
        # You need to tell us the decoding from MSI_files' group number codes to more human readable group names:
        # self.MSI_group_number_to_group_name_dictionary = dict(zip(range(len(self.group_names)), self.group_names))
        self.MSI_group_number_to_group_name_dictionary = {
	        	1: '2CWT', 2: '2CKO'
	            }
        self.numberOfIndividualsInGroup = {
	            1: 12, 2: 12
	            } 
        self.allPossibleGroupNumbers = [1, 2]
        self.allPossibleDayNumbers = range(1, 18+1) 
        self.acclimationDayNumbers = range(1, 4+1)
        self.acclimatedDayNumbers = range(5, 18+1)	
        self.chowDayNumbers = range(5, 11+1)

        # diet stuff
        self.fastDayNumbers = [12]      # Fast Day      
        self.fastDayFoodRemovalRunTimeStart = 4.08*3600     # Entered the room at 5:44PM (runtime = 4.08 hrs) to remove the food 
                                                            # Data collection was still running during collection of food.
        self.fastDayFoodRemovalRunTimeStop = 4.19*3600     # Exited the room at 5:50PM (runtime = 4.19 hrs)

        self.reFeedDayNumbers = [13]    # Refeed Day (after 18 hours of no food)
        self.reFeedDayFoodReinsertionDayTimeStart = (11, 50)    # Food was back in at ~11:50AM
                                                                # Data collection followed right after that.
        self.preFastDayNumbers = [9, 10, 11]
        self.afterFastDayNumbers = range(13, 18+1)
        # self.fastAndAfterFastDayNumbers = range(12, 18+1)
        self.transitionDays = [11, 12, 13, 14]                # mike
        self.transitionDays2 = range(10, 15+1)
        # time bin shift
        self.binTimeShift = - 70 * 60 if self.BIN_SHIFT else 0                 # bin alignment: 69 minutes before (CT1051)
        self.binShiftDayStart = self.fastDayNumbers[0]          # start day for time bin shift
        self.binShiftDayStop = self.acclimatedDayNumbers[-1]    # end day

        if self.use_days == 'acclimated':
            self.daysToUse = self.acclimatedDayNumbers
        elif self.use_days == 'chow':                   # 5to12
            self.daysToUse = self.chowDayNumbers
        elif self.use_days == 'fast':
            self.daysToUse = self.fastDayNumbers  
        elif self.use_days == 'refeed':                   
            self.daysToUse = self.reFeedDayNumbers
        elif self.use_days == 'pre_fast':        
            self.daysToUse = self.preFastDayNumbers 
        elif self.use_days == 'after_fast':        
            self.daysToUse = self.afterFastDayNumbers 
        # elif self.use_days == 'fast_and_after_fast':        
        #     self.daysToUse = self.fastAndAfterFastDayNumbers  
        elif self.use_days == 'transition':        
            self.daysToUse = self.transitionDays2                    # 24 HDCLCL_shifted, 24bins_shifted  

        elif self.use_days == 'all':
            self.daysToUse = self.allPossibleDayNumbers  
        
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
	        self.flag_ignored_data()
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


    def flag_ignored_data(self):
        """ defines mouseday to ignore based on experimenter's 
            observation of data_quality plots
        """
        # load flagged from binary generation
        self.flag_ignored_mousedays()
        # after looking at data quality plots, remove these mousedays from flagged list
        remove_from_flagged = [         # (mouseNum, dayNum)
            (7279, 6)               # flagged for long F event (>30mins), not true
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
            # 6645,            # WT, platform
            # 6708,
            # 6663,           # KO
            # 6681
            ]
        
        # here the final list of mice and mousedays to ignore
        mouse_to_ignore.extend(mice_added_for_removal)
        md_to_ignore = [(x, a) for x, a in confirmed if x not in mouse_to_ignore]
        self.mouseNumbers_to_ignore = tuple(mouse_to_ignore)
        self.mouseNumbersAndDays_to_ignore = tuple(md_to_ignore)
        

    def get_groups_settings(self):        
        # strain_names for plotting
        self.group_number_to_full_group_name_dict = {1: '2CWT', 2: '2CKO'}
        self.strain_dict = {key: self.group_number_to_full_group_name_dict[key] for key in range(1, 3)}
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


    def get_food_removal_times(self):
        arr, labels = self.get_HCM_recording_time()
        HCM_start = arr[labels[:, 2]==self.fastDayNumbers[0]].mean(0)[0]
        times = [HCM_start + self.fastDayFoodRemovalRunTimeStart, 
                HCM_start + self.fastDayFoodRemovalRunTimeStop]
        return np.array(times)


    def get_food_reinsertion_times(self):
        arr, labels = self.get_HCM_recording_time()
        HCM_start = arr[labels[:,2]==self.reFeedDayNumbers[0]].mean(0)[0] # + 7) * 3600
        h, m = self.reFeedDayFoodReinsertionDayTimeStart
        food_back_HCM_time = h * 3600 + m * 60
        times = [HCM_start, food_back_HCM_time]
        return np.array(times)


