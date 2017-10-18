import sys
import os
import time

from experiment import Experiment
from ceppa.util.darren import getStrainLists
from ceppa.util.darren.getFileNamesForExperimentMouseDay import dataDirRoot

"""
G.Onnis, 01.2017
    
Tecott Lab UCSF
"""

class StrainSurveyExperiment(Experiment): # subclass of Experiment

    def __init__(self, name='StrainSurveyExperiment', IST=20., FBT=30., WBT=30., MBVT=1., MBDT=5., MBTT=0.2, 
            IGNORE_MD=True, FULLNAME=True, BIN_SHIFT=False, use_days='acclimated'):
        
        self.exp_dir = dataDirRoot() + 'Experiments/SS_Data_051905_FV/'

        Experiment.__init__(self, name, IST, FBT, WBT, MBVT, MBDT, MBTT, 
            IGNORE_MD, FULLNAME, BIN_SHIFT, use_days) # have to explicitly call the superclass initializer

        self.short_name = 'SS'
        self.num_strains = 16
        self.initialize()


    def __str__(self):  
        return self.short_name


    def initialize(self):
        print "initializing %s.." %self.name 
        # names for file i/o
        self.group_names = [
                            'C57BL6J', 'BALB', 'A', '129S1', 
                            'DBA', 'C3H', 'AKR', 'SWR', 
                            'SJL', 'FVB', 'WSB', 'CZECH', 
                            'CAST', 'JF1', 'MOLF', 'SPRET'
                            ]
        # You need to tell us a list of all MSIFiles:
        self.list_of_MSI_file_names = [
                self.exp_dir + "MSIFiles/StructFormat/aflSSe1r%d_MSI_FF.csv"%(roundNumber) \
                for roundNumber in [2,3,4,5,6,7,8]]
        # You need to tell us the decoding from MSI_files' group number codes to more human readable group names:
        # self.MSI_group_number_to_group_name_dictionary = dict(zip(range(len(self.group_names)), self.group_names))
        self.MSI_group_number_to_group_name_dictionary = {0: 'C57BL6T', 
            1: 'C57BL6J', 2: 'BALB', 3: 'A', 4: '129S1', 
            5: 'DBA', 6: 'C3H', 7: 'AKR', 8: 'SWR', 
            9: 'SJL', 10: 'FVB', 11: 'WSB', 12: 'CZECH', 
            13: 'CAST', 14: 'JF1', 15: 'MOLF', 16: 'SPRET',
            }
        self.numberOfIndividualsInGroup = {
            0: 12,
            1: 12, 2: 12, 3: 12, 4: 12,
            5: 11, 6: 12, 7: 12, 8: 12,
            9: 12, 10: 12, 11: 10, 12: 11,
            13: 12, 14: 12, 15: 14, 16: 14
            } 
        self.allPossibleGroupNumbers = range(16)
        self.allPossibleDayNumbers = range(1, 16+1)
        self.nonAcclimationDayNumbers = range(5, 16+1)
        self.acclimatedDayNumbers = range(5, 16+1)
        self.acclimationDayNumbers = range(1, 4+1)
        if self.use_days == 'acclimated':
            self.daysToUse = self.acclimatedDayNumbers
        
        # time bin shift
        self.binTimeShift = 0 if self.BIN_SHIFT else 0                

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
            (4201, 15),
            (3203, 5),
            (7106, 5), (7106, 7), (7106, 8), (7106, 9), (7106, 11), (7106, 15),
            (4114, 5), (4114, 7), (4114, 8), (4114, 9), (4114, 10), (4114, 11), 
            (4114, 12), (4114, 13), (4114, 14), (4114, 15), (4114, 16),
            (4214, 5), (4214, 6), (4214, 8), (4214, 9), (4214, 12), (4214, 13), (4214, 14),
            (6214, 12),
            (6314, 9), (6314, 12), (6314, 14),
            (6414, 7), (6414, 12),
            (7214, 5), 
            (7314, 7), (7314, 9), (7314, 11), (7314, 12), (7314, 14), (7314, 16), 
            (7414, 11)
            ]
        confirmed = [x for x in self.flagged if x not in remove_from_flagged]
        # and add these
        md_added_for_removal = [
            (8102, 11),     # water
            (2103, 13),     # TF, TW too small
            (5103, 5),                  # water 
            (5103, 7), (5103, 9),       # water 
            (7203, 8),
            (5204, 16),         # water
            (5205, 14),
            (3106, 16),         # TW too large
            (7206, 10),         # TW too large
            (8106, 16),         # drink
            (3108, 11),         #pb break    
            (4109, 14),         #water
            (8409, 6),          #water
            (7210, 10), (7210, 11), (7210, 12), (7210, 13), (7210, 14), (7210, 15), (7210, 16),
            (6315, 16),
            (6616, 5), (6616, 7), (6616, 10), (6616, 11)
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
            3104,               # position wrong or heavily shifted. other features look ok.
            2204,
            6105, 
            5106,
            4211, 5311, 
            8613, 
            2115,               # day 10 to 16 TW is too large
            6216, 7316
            ]
        
        # here the final list of mice and mousedays to ignore
        mouse_to_ignore.extend(mice_added_for_removal)
        md_to_ignore = [(x, a) for x, a in confirmed if x not in mouse_to_ignore]
        self.mouseNumbers_to_ignore = tuple(mouse_to_ignore)
        self.mouseNumbersAndDays_to_ignore = tuple(md_to_ignore)
        

    def get_groups_settings(self):        
        # strain_names for plotting
        self.group_number_to_full_group_name_dict = {0: '',
            1: 'C57BL/6J', 2: 'BALB/cByJ', 3: 'A/J', 4: '129S1/SvImJ',
            5: 'DBA/2J', 6: 'C3H/HeJ', 7: 'AKR/J', 8: 'SWR/J',
            9: 'SJL/J', 10: 'FVB/NJ', 11: 'WSB/Ei', 12: 'CZECHII/Ei',
            13: 'CAST/Ei', 14: 'JF1/Ms', 15: 'MOLF/Ei', 16: 'SPRET/Ei',
        }
        self.strain_dict = {key: self.group_number_to_full_group_name_dict[key] for key in xrange(1, 17)}
        self.strain_names = [name for name in self.MSI_group_number_to_group_name_dictionary.values()][1:]
        if self.FULLNAME:
            self.strain_names = [name for name in self.group_number_to_full_group_name_dict.values()][1:]
        # selected raster individuals
        self.selected_individuals = [
            3201, 3102, 5203, 7204, 3105, 2206, 3207, 7408,
            6209, 3110, 3111, 3212, 4113, 7214, 5215, 6816
            ] 
        self.individual_days_dict={}
        for k in self.allPossibleGroupNumbers:
            # days_ = range(7, 16+1)
            # if k == 3 or k == 15: 
            #   days_ = range(6, 15+1)          # A, SPRET:6to15+1. counting from day5...
            _days = range(9, 14)
            self.individual_days_dict[k] = (self.selected_individuals[k], _days)
        # selected rasters for individuals: strains 1.B6, 2.BALB, 4.129S1. 
        # #order is important
        self.selected_individuals_sub = [
            3201, 3104, 2202, 
            4101, 4204, 3102, 
            4201, 5204, 4102, 
            5101, 8104, 7202
            ]
        self.individual_days_dict_sub={}
        for k in xrange(12):
            self.individual_days_dict_sub[k] = (self.selected_individuals_sub[k], range(9, 14))

	"""
		self.group_name_to_mouse_number_list_dictionary = {
			'C57BL6T': [2100, 2200, 2300, 2400, 2500, 2600],
			'C57BL6J': [2101, 2201, 3101, 3201, 4101, 4201, 5101, 5201, 7101, 7201, 8101, 8201],
			'BALB': [2102, 2202, 3102, 3202, 4102, 4202, 5102, 5202, 7102, 7202, 8102, 8202],
			'A': [2103, 2203, 3103, 3203, 4103, 4203, 5103, 5203, 6103, 6203, 7103, 7203],
			'129S1': [2104, 2204, 3104, 3204, 4104, 4204, 5104, 5204, 7104, 7204, 8104, 8204],
			'DBA': [2105, 2205, 3105, 3205, 4105, 4205, 5105, 5205, 6105, 6205, 7105, 7205],

			'C3H': [2106, 2206, 3106, 3206, 4106, 4206, 5106, 5206, 7106, 7206, 8106],
			'AKR': [2107, 2207, 3107, 3207, 4107, 4207, 7107, 7207, 8107, 8207, 8307, 4211],
			'SWR': [2108, 2208, 3108, 3208, 4108, 4208, 5108, 5208, 7108, 7208, 7308, 7408],
			'SJL': [3109, 3209, 4109, 4209, 6109, 6209, 7109, 7209, 8109, 8209, 8309, 8409],
			'FVB': [2110, 2210, 3110, 3210, 4110, 4210, 5110, 5210, 7110, 7210, 8110, 8210],
			'WSB': [2111, 2211, 3111, 3211, 4111, 4211, 5111, 5211, 5311, 5411, 6111, 6211],

			'CZECH': [2112, 2212, 3112, 3212, 4112, 5112, 5212, 5312, 5412, 6112],
			'CAST': [2113, 2213, 3113, 3213, 4113, 5113, 5213, 5313, 8113, 8413, 8613],
			'JF1': [4114, 4214, 5114, 5214, 6114, 6214, 6314, 6414, 7114, 7214, 7314, 7414],
			'MOLF': [2115, 2215, 4115, 5115, 5215, 5315, 6115, 6215, 6315, 6415, 7115, 7215],
			'SPRET': [3116, 3216, 6116, 6216, 6316, 6416, 6516, 6616, 6716, 6816, 6916, 7116, 7216, 7316],
		}
		self.mouse_number_to_round_number_dictionary = { # almost without exception, the roundNumber is the thousands digit of the mouseNumber, except for 7116: 6, 7216: 6, 7316: 6,
			2100: 2, 2200: 2, 2300: 2, 2400: 2, 2500: 2, 2600: 2, 2101: 2, 2201: 2, 3101: 3, 
			3201: 3, 4101: 4, 4201: 4, 5101: 5, 5201: 5, 7101: 7, 7201: 7, 8101: 8, 8201: 8, 
			2102: 2, 2202: 2, 3102: 3, 3202: 3, 4102: 4, 4202: 4, 5102: 5, 5202: 5, 7102: 7, 
			7202: 7, 8102: 8, 8202: 8, 2103: 2, 2203: 2, 3103: 3, 3203: 3, 4103: 4, 4203: 4, 
			5103: 5, 5203: 5, 6103: 6, 6203: 6, 7103: 7, 7203: 7, 2104: 2, 2204: 2, 3104: 3, 
			3204: 3, 4104: 4, 4204: 4, 5104: 5, 5204: 5, 7104: 7, 7204: 7, 8104: 8, 8204: 8,
			2105: 2, 2205: 2, 3105: 3, 3205: 3, 4105: 4, 4205: 4, 5105: 5, 5205: 5, 6105: 6, 
			6205: 6, 7105: 7, 7205: 7, 2106: 2, 2206: 2, 3106: 3, 3206: 3, 4106: 4, 4206: 4, 
			5106: 5, 5206: 5, 7106: 7, 7206: 7, 8106: 8, 2107: 2, 2207: 2, 3107: 3, 3207: 3, 
			4107: 4, 4207: 4, 7107: 7, 7207: 7, 8107: 8, 8207: 8, 8307: 8, 4211: 8, 2108: 2, 
			2208: 2, 3108: 3, 3208: 3, 4108: 4, 4208: 4, 5108: 5, 5208: 5, 7108: 7, 7208: 7, 
			7308: 7, 7408: 7, 3109: 3, 3209: 3, 4109: 4, 4209: 4, 6109: 6, 6209: 6, 7109: 7, 
			7209: 7, 8109: 8, 8209: 8, 8309: 8, 8409: 8, 2110: 2, 2210: 2, 3110: 3, 3210: 3, 
			4110: 4, 4210: 4, 5110: 5, 5210: 5, 7110: 7, 7210: 7, 8110: 8, 8210: 8, 2111: 2, 
			2211: 2, 3111: 3, 3211: 3, 4111: 4, 4211: 4, 5111: 5, 5211: 5, 5311: 5, 5411: 5, 
			6111: 6, 6211: 6, 2112: 2, 2212: 2, 3112: 3, 3212: 3, 4112: 4, 5112: 5, 5212: 5,
			5312: 5, 5412: 5, 6112: 6, 2113: 2, 2213: 2, 3113: 3, 3213: 3, 4113: 4, 5113: 5, 
			5213: 5, 5313: 5, 8113: 8, 8413: 8, 8613: 8, 4114: 4, 4214: 4, 5114: 5, 5214: 5, 
			6114: 6, 6214: 6, 6314: 6, 6414: 6, 7114: 7, 7214: 7, 7314: 7, 7414: 7, 2115: 2,
			2215: 2, 4115: 4, 5115: 5, 5215: 5, 5315: 5, 6115: 6, 6215: 6, 6315: 6, 6415: 6,
			7115: 7, 7215: 7, 3116: 3, 3216: 3, 6116: 6, 6216: 6, 6316: 6, 6416: 6, 6516: 6, 
			6616: 6, 6716: 6, 6816: 6, 6916: 6, 7116: 6, 7216: 6, 7316: 6,
		}
		# ist matlab group averages values
		if ist is None:
			self.IST_in_minutes_by_group_name={
				'C57BL6T' : 8.3346,
				'C57BL6J' : 8.3346,
				'BALB' : 11.2473,
				'A' : 13.4762,
				'129S1' : 9.8505,
				'DBA' : 15.6794,
				'C3H' : 18.4259,
				'AKR' : 12.0076,
				'SWR' : 8.5690,
				'SJL' : 8.1320, 
				'FVB' : 11.2363, 
				'WSB' : 9.0797,
				'CZECH' : 15.6061,
				'CAST' : 11.4716,
				'JF1' : 24.3425,
				'MOLF' :  10.3805,
				'SPRET' : 18.6785,
			}	
		##### END within specification guidelines
	# def addExperimentSpecificAttributesToIndividual(self,IA):
	#     IA.roundNumber, IA.mouseNumber = getRoundNumberAndMouseNumberForStrainIndividual(strain=IA.group.number,individual=IA.number)
	"""



	
