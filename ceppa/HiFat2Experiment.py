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


class HiFat2Experiment(Experiment): # subclass of Experiment

    def __init__(self, name='HiFat2Experiment', IST=20., FBT=30., WBT=30., MBVT=1., MBDT=5., MBTT=0.2, 
            IGNORE_MD=True, FULLNAME=True, BIN_SHIFT=False, use_days='chow'):
        
        self.exp_dir = dataDirRoot() + 'Experiments/HiFat2/'

        Experiment.__init__(self, name, IST, FBT, WBT, MBVT, MBDT, MBTT, 
            IGNORE_MD, FULLNAME, BIN_SHIFT, use_days) # have to explicitly call the superclass initializer

        self.short_name = 'HFD2'
        self.num_strains = 2
        self.initialize()


    def __str__(self):  
        return self.short_name


    def initialize(self):
        print "initializing %s.." %self.name 
        # names for file i/o
        self.group_names = [
                            'WT',   # Wild Type/ High Fat
                            '2C',   # KnockOut/ High Fat
                            ]
        # You need to tell us a list of all MSIFiles:
        self.list_of_MSI_file_names = [self.exp_dir + 'hcmHFD2e2r1_MSI_FF.csv']
        # You need to tell us the decoding from MSI_files' group number codes to more human readable group names:
        # self.MSI_group_number_to_group_name_dictionary = dict(zip(range(len(self.group_names)), self.group_names))
        self.MSI_group_number_to_group_name_dictionary = {
                1: 'WT', 2: '2C'
                }
        self.numberOfIndividualsInGroup = {
                1: 15, 2: 15
                } 
        self.allPossibleGroupNumbers = [1, 2]
        self.allPossibleDayNumbers = range(1, 28+1) 
        self.acclimationDayNumbers = range(1, 4+1)
        self.acclimatedDayNumbers = range(5, 28+1)  
        
        self.chowDayNumbers = range(5, 12+1)
        self.allHiFatDayNumbers = range(13, 28+1)
        self.dietChangeDayNumbers = [13]
        
        self.chowToHFDayNumbers = range(10, 17+1)
        self.preDietDayNumbers = range(10, 12+1)
        self.postDietDayNumbers = range(13, 17+1)  
        self.acrossDietDayNumbers = [11, 12, 13, 14]
        # self.chowToHFAndBaselineDayNumbers = self.chowToHFDayNumbers + [27, 28, 29]
        self.HiFatDayNumbers = range(21, 28+1)           

        # time bin shift
        self.binTimeShift = 0 if self.BIN_SHIFT else 0                 

        if self.use_days == 'acclimated':
            self.daysToUse = self.acclimatedDayNumbers 
        elif self.use_days == 'chow':                   # 5 to 12
            self.daysToUse = self.chowDayNumbers
        elif self.use_days == 'HiFat':                  # 13 to 28
            self.daysToUse = self.HiFatDayNumbers
        elif self.use_days == 'diet_change':        
            self.daysToUse = self.dietChangeDayNumbers 

        elif self.use_days == 'transition':                   
            self.daysToUse = self.chowToHFDayNumbers 
        elif self.use_days == 'pre_diet':                   
            self.daysToUse = self.preDietDayNumbers 
        elif self.use_days == 'post_diet':                   
            self.daysToUse = self.postDietDayNumbers 
        elif self.use_days == 'across_diet_change':                   
            self.daysToUse = self.acrossDietDayNumbers 
        elif self.use_days == 'all':
            self.daysToUse = self.allPossibleDayNumbers 
        # elif self.use_days == 'chow_to_HF_and_baseline':             
        #     self.daysToUse = self.chowToHFAndBaselineDayNumbers              

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
            (6645, 5)
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
            6645,            # WT, platform
            6708,
            6663,           # KO
            6681
            ]
        
        # here the final list of mice and mousedays to ignore
        mouse_to_ignore.extend(mice_added_for_removal)
        md_to_ignore = [(x, a) for x, a in confirmed if x not in mouse_to_ignore]
        self.mouseNumbers_to_ignore = tuple(mouse_to_ignore)
        self.mouseNumbersAndDays_to_ignore = tuple(md_to_ignore)
        

    def get_groups_settings(self):        
        # strain_names for plotting
        self.group_number_to_full_group_name_dict = {1: 'WT', 2: '2C'}
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




    
