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


class FluoxetineExperiment(Experiment): # subclass of Experiment

    def __init__(self, name='FluoxetineExperiment', IST=20., FBT=30., WBT=30., MBVT=1., MBDT=5., MBTT=0.2, 
            IGNORE_MD=False, FULLNAME=True, BIN_SHIFT=False, use_days='acclimated'):
        
        self.exp_dir = dataDirRoot() + 'Experiments/B6FLX/'

        Experiment.__init__(self, name, IST, FBT, WBT, MBVT, MBDT, MBTT, 
                            IGNORE_MD, FULLNAME, BIN_SHIFT, use_days) # have to explicitly call the superclass initializer

        self.short_name = 'B6FLX'
        self.num_strains = 3
        self.initialize()


    def __str__(self):  
        return self.short_name


    def initialize(self):
        print "\ninitializing %s.." %self.name 
        # names for file i/o
        self.group_names = [
                            'B6FLX5',   # Wild Type, Fluoxetine dosage
                            'B6FLX10',  
                            'B6FLX20'
                            ]
        # You need to tell us a list of all MSIFiles:
        self.list_of_MSI_file_names = [self.exp_dir + 'B6FLX_DaySummary/hcmB6FLXe1r1_MSI_FF.csv']
        # You need to tell us the decoding from MSI_files' group number codes to more human readable group names:
        # self.MSI_group_number_to_group_name_dictionary = dict(zip(range(len(self.group_names)), self.group_names))
        self.MSI_group_number_to_group_name_dictionary = {
                1: 'B6FLX5', 2: 'B6FLX10', 3: 'B6FLX20'
                }
        self.numberOfIndividualsInGroup = {
                1: 11, 2: 10, 3: 11
                } 
        self.allPossibleGroupNumbers = [1, 2, 3]
        self.allPossibleDayNumbers = range(1, 28+1)     # for the moment, exclude days [29, 32]
        self.acclimationDayNumbers = range(1, 4+1)
        self.acclimatedDayNumbers = range(5, 28+1)

        self.standardHCMDayNumbers = range(5, 11+1)
        self.novelObjectDayNumbers = [12, 13]
        self.fluoxetineDayNumbers = range(14, 28+1)
        self.fluoxetineFirstFourDayNumbers = range(14, 17+1)
        self.fluoxetineLastFourDayNumbers = range(25, 28+1)

        # time bin shift
        self.binTimeShift = 0 if self.BIN_SHIFT else 0                 # bin alignment: 69 minutes before (CT1051)
        # self.binShiftDayStart = #self.fastDayNumbers[0]          # start day for time bin shift
        # self.binShiftDayStop = #self.acclimatedDayNumbers[-1]    # end day

        if self.use_days == 'acclimated':
            self.daysToUse = self.acclimatedDayNumbers
        elif self.use_days == 'standard_HCM':                   # 5to11
            self.daysToUse = self.standardHCMDayNumbers
        elif self.use_days == 'pre-FLX':                   
            self.daysToUse = self.standardHCMDayNumbers + self.novelObjectDayNumbers
        elif self.use_days == 'post-FLX':
            self.daysToUse = self.fluoxetineDayNumbers 
        elif self.use_days == 'post-FLX_first_4':                   
            self.daysToUse = self.fluoxetineFirstFourDayNumbers
        elif self.use_days == 'post-FLX_last_4':
            self.daysToUse = self.fluoxetineLastFourDayNumbers  
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
            print "flagging ignored mousedays..\n"
            self.flag_ignored_data()
        else:
            print "including all mousedays..\n"
        
        # add groups, mice, mousedays objects
        self.add_group_attributes()
        print 'groups: %d' %self.num_strains
        for group in self.groups:
            print "group%d: %s" %(group.number, group.name)    

        # count mice in admissible groups
        self.count_mice()
        
        print "individuals: %d/%d (%d ignored)" %(
                self.num_mice, self.num_mice_ok, self.num_mice_ignored)

        # count admissible mousedays according to admissible groups, ignored mice and use_days 
        self.count_mousedays()
        
        print "mousedays: %d/%d (%d ignored)" %(
                self.num_mousedays, self.num_md_ok, self.num_md_ignored)
        print "%s_days: %d, %s" %(
                self.use_days, len(self.daysToUse), self.daysToUse)

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
            (701, 17),       # group0: ('F_timeSet', 'long event (>30min)')
            (1801, 23),      # ('F_timeSet', 'long event (>30min)')
            (1801, 25),      # ('F_timeSet', 'long event (>30min)')
            (2601, 23),      # ('F_timeSet', 'long event (>30min)')
            (2001, 12),      # group1: ('F_timeSet', 'long event (>30min)')
            (601, 15),       # group2: ('F_timeSet', 'long event (>30min)')
            (601, 16),       # ('F_timeSet', 'long event (>30min)')
            (601, 20),       # ('F_timeSet', 'long event (>30min)')
            (601, 21),       # ('F_timeSet', 'long event (>30min)')
            (2201, 5),       # ('F_timeSet', 'long event (>30min)')
            (3001, 23)       # ('F_timeSet', 'long event (>30min)')
            ]
        confirmed = [x for x in self.flagged if x not in remove_from_flagged]
        # and add these
        md_added_for_removal = [
            (701, 5), (701, 10),     # group0: ('F_timeSet', 'long time (>12h)\nw/o events')
            (401, 12),               # group1: ('F_timeSet', 'long time (>12h)\nw/o events')
            (2001, 10),              # ('F_timeSet', 'long time (>12h)\nw/o events')
            (2201, 11),              # ('F_timeSet', 'long time (>12h)\nw/o events')
            (2201, 12),              # group2: ('F_timeSet', 'long time (>12h)\nw/o events')
            (2201, 13),              # ('F_timeSet', 'long time (>12h)\nw/o events')
            (2201, 15),              # ('F_timeSet', 'long time (>12h)\nw/o events')
            (2201, 17),              # ('F_timeSet', 'long time (>12h)\nw/o events')
            (2401, 24),              # ('W_timeSet', 'long time (>12h)\nw/o events')
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
            3201,       # group1: many days with ('F_timeSet', 'long time (>12h)\nw/o events')
            2201,       # only days 5 to 9 and few others 
            ]
        
        # here the final list of mice and mousedays to ignore
        mouse_to_ignore.extend(mice_added_for_removal)
        md_to_ignore = [(x, a) for x, a in confirmed if x not in mouse_to_ignore]
        self.mouseNumbers_to_ignore = tuple(mouse_to_ignore)
        self.mouseNumbersAndDays_to_ignore = tuple(md_to_ignore)
        print "mice ignored:", mouse_to_ignore
        print "mousedays ignored:", md_to_ignore


    def get_groups_settings(self):        
        # strain_names for plotting
        self.group_number_to_full_group_name_dict = {1: 'B6FLX5', 2: 'B6FLX10', 3: 'B6FLX20'}
        self.strain_dict = {key: self.group_number_to_full_group_name_dict[key] for key in range(1, 4)}
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


