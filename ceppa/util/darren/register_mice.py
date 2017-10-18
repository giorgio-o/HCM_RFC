
import getFileNamesForExperimentMouseDay

"""
D. Rhea, 2013
Here's Darren core stuff. register mice with groups and add mousedays
These are Mouseday methods.

Tecott Lab UCSF
"""


def register_with_mouse(self):
    """
    must have dayNumber and mouse attributes already assigned
    """
    experiment = self.individual.group.experiment
    mouseNumber = self.individual.mouseNumber
    self.ignored = False
    if experiment.IGNORE_MD:
        if (mouseNumber, self.dayNumber) in experiment.mouseNumbersAndDays_to_ignore or mouseNumber in experiment.mouseNumbers_to_ignore: 
            self.ignored = True
    
    # self.BIN_SHIFT = True
    # if experiment.BIN_SHIFT:
    #     if self.dayNumber >= experiment.binShiftDayStart and \
    #         self.dayNumber <= experiment.binShiftDayStop:
    #         self.BIN_SHIFT = True
            
    self.individual.mouse_days.append(self)                         # add both ignored and not ignored
    self.individual.mouse_day_number[self.dayNumber] = self


def add_stuff_to_mouse_day(self):
    """
    """
    MD = self
    # experiment = self.experiment            # add 01.2017
    MD.group = MD.individual.group 
    MD.experiment = MD.individual.group.experiment
    MD.individualNumber = MD.individual.individualNumber
    MD.experimentName = MD.individual.group.experiment.name
    MD.groupNumber = MD.individual.group.number
    MD.groupName = MD.individual.group.name
    MD.mouseNumber = MD.individual.mouseNumber
    MD.startActiveTimeThreshold = MD.individual.startActiveTimeThreshold
    MD.startInactiveTimeThreshold = MD.individual.startInactiveTimeThreshold

    MD.roundNumber = MD.experiment.mouse_number_to_round_number_dictionary[MD.mouseNumber]
    MD.MSIFile = MD.individual.MSIFile # individuals possess MSIFiles
    
    experiment_list = [
                        'HiFat1Experiment', 
                        'HiFat2Experiment', 
                        'TwoCFastExperiment',
                        'FluoxetineExperiment'
                        ]

    
    if MD.experiment.name == 'StrainSurveyExperiment':
        successful, MD.AMFileName, MD.LEFileName, MD.MEFileName, MD.PEFileName = \
            getFileNamesForExperimentMouseDay.fileNamesForStrainSurvey(MD.experiment.exp_dir, MD.roundNumber, MD.dayNumber, MD.mouseNumber)    
    elif MD.experiment.name in experiment_list:
        MD.roundNumber = MD.experiment.mouse_number_to_round_number_dictionary[MD.mouseNumber]
        MD.MSIFile = MD.individual.MSIFile # individuals possess MSIFiles
        MD.AMFileName, MD.LEFileName, MD.MEFileName, MD.PEFileName = \
            getFileNamesForExperimentMouseDay.fileNamesForExperiment(MD.experiment, MD.roundNumber, MD.dayNumber, MD.mouseNumber)    
    elif MD.experiment.name == 'ZeroLightExperiment':
        MD.roundNumber = MD.experiment.mouse_number_to_round_number_dictionary[MD.mouseNumber]
        MD.MSIFile = MD.individual.MSIFile # individuals possess MSIFiles
        MD.AMFileName, MD.LEFileName, MD.MEFileName, MD.PEFileName = \
            getFileNamesForExperimentMouseDay.fileNamesForExperiment(MD.experiment, MD.roundNumber, MD.dayNumber, MD.mouseNumber)    
        
        # stop at day 10
        
    # elif MD.experiment.name == 'HiFat1Experiment':
    #     MD.roundNumber = MD.experiment.mouse_number_to_round_number_dictionary[MD.mouseNumber]
    #     MD.MSIFile = MD.individual.MSIFile # individuals possess MSIFiles
    #     MD.AMFileName, MD.LEFileName, MD.MEFileName, MD.PEFileName = \
    #         getFileNamesForExperimentMouseDay.fileNamesForExperiment(MD.experiment, MD.roundNumber, MD.dayNumber, MD.mouseNumber)    
    # elif MD.experiment.name == 'HiFat2Experiment':
    #     MD.roundNumber = MD.experiment.mouse_number_to_round_number_dictionary[MD.mouseNumber]
    #     MD.MSIFile = MD.individual.MSIFile # individuals possess MSIFiles
    #     MD.AMFileName, MD.LEFileName, MD.MEFileName, MD.PEFileName = \
    #         getFileNamesForExperimentMouseDay.fileNamesForHiFat2(MD.experiment.exp_dir, MD.roundNumber, MD.dayNumber, MD.mouseNumber)    
    # elif MD.experiment.name == 'TwoCFastExperiment':
    #     MD.roundNumber = MD.experiment.mouse_number_to_round_number_dictionary[MD.mouseNumber]
    #     MD.MSIFile = MD.individual.MSIFile # individuals possess MSIFiles
    #     MD.AMFileName, MD.LEFileName, MD.MEFileName, MD.PEFileName = \
    #         getFileNamesForExperimentMouseDay.fileNamesForTwoCFast(MD.experiment.exp_dir, MD.roundNumber, MD.dayNumber, MD.mouseNumber)    
        
    else:
        stop
        MD.MSIFile = MD.individual.MSIFile
        MD.AMFileName, MD.LEFileName, MD.MEFileName, MD.PEFileName = getFileNamesForExperimentMouseDay.fileNamesForExperimentMouseDay(
            experimentDirectoryName=MD.experiment.experimentDirectoryName, 
            mouseNumber=MD.mouseNumber, 
            dayNumber=MD.dayNumber
        )

    try:
        obj = MD.experiment.output2.X[MD.groupName][MD.mouseNumber][MD.dayNumber]
        MD.NLX = obj.NLX
        MD.NLY = obj.NLY
    except Exception:
        stop
    #   print "\nNESTFUCK, %s\n", MD

    try:
        MD.intro_time = experiment.mouse_day_pair_to_intro_time[(MD.mouseNumber, MD.dayNumber)]
    except(Exception):
        pass

    try:
        MD.intro_time=inverseTimeFormatter(experiment.intro_times_on_day[MD.dayNumber][MD.mouseNumber])
    except(Exception):
        pass
        #print "Failure to assign intro_time to day %d mouseNumber %d"%(MD.dayNumber, MD.mouseNumber)

    try:
        MD.system = {1:'A', 2:'B', 3:'C', 4:'D'}[experiment.mouse_number_to_sys_enc_pair[MD.mouseNumber][0]]
        MD.enclosure_number = experiment.mouse_number_to_sys_enc_pair[MD.mouseNumber][1]
        if dayNumber==21:
            left_and_right_objects=experiment.sys_enc_pair_to_left_right_pair[experiment.mouse_number_to_sys_enc_pair[MD.mouseNumber]]
            MD.left_object=left_and_right_objects[0]
            MD.right_object=left_and_right_objects[1]
        elif dayNumber==20:
            MD.left_object = 'pen'
            MD.right_object = 'metal_clip'
        else:
            try:
                MD.right_object = experiment.novelObjectOnDay[dayNumber]
            except:
                pass
    except:
        pass
    return MD
