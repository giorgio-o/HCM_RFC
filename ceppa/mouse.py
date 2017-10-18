import sys
import numpy as np
from mouseday import MouseDay
import os
import pickle
from operator import itemgetter

from ceppa.util.intervals import Intervals


"""
D. Rhea, 2013
G.Onnis, rebuilt: 09.2016
        updated, 05.2017

Tecott Lab UCSF
"""

class Mouse():
    def __init__(self):
        pass
    def __str__(self):
        s=''
        if hasattr(self,'experiment'):
            s += self.experiment.short_name+', '
        if hasattr(self,'groupNumber'):
            s += "groupNumber=%d, "%(self.groupNumber)
            if hasattr(self,'experiment'):
                s += "groupName=%s, " % (self.experiment.groupNames[self.groupNumber])
        if hasattr(self,'individualNumber'):
            s += "individualNumber=%d, "%(self.individualNumber)
        if hasattr(self, 'mouseNumber'):
            s += "mouseNumber=%d"%(self.mouseNumber)
        return s
    

    def add_days_and_register_with_group(self):
        self.ignored = False
        if self.group.experiment.IGNORE_MD:
            if self.mouseNumber in self.group.experiment.mouseNumbers_to_ignore:
                self.ignored = True

        # if not self.ignored: # old: ignored mice were not added to the group
        self.group.individuals.append(self)                        # add bot ignored and not ignored
        self.group.individual_numbered[self.individualNumber] = self
        self.group.mouse_numbered[self.mouseNumber] = self

        self.mouse_days = []
        self.mouse_day_number = {}
        for dayNumber in self.group.experiment.allPossibleDayNumbers:
            MD = MouseDay()
            MD.individual = self # each mouseday should point to its "parent" mouse
            MD.dayNumber = dayNumber
            MD.register_with_mouse()        # add mousedays
                
                
    def add_stuff_to_mouse(self):
        M = self 
        M.experiment=M.group.experiment # point at parent
        M.experimentName=M.experiment.name # this is redundant, why not M.experiment.name?
        M.groupNumber=M.group.number # this should go eventually
        M.groupName = M.group.name # why not M.group.name?
        M.startActiveTimeThreshold=30.0 # always seem to use this   (supposedly seconds)
                                        # mouse goes quantizationDist in less than 30 seconds? Turn on active state

        M.roundNumber = M.experiment.mouse_number_to_round_number_dictionary[M.mouseNumber]
        if M.experiment.name == 'StrainSurveyExperiment':
            M.MSIFile = M.experiment.exp_dir + "MSIFiles/StructFormat/aflSSe1r%d_MSI_FF.csv"%(M.roundNumber)
        elif M.experiment.name == 'HiFat1Experiment':
            M.MSIFile = M.experiment.exp_dir + "Round%d/HFD_DaySummary/hcmHFDe1r%d_MSI_FF.csv"%(M.roundNumber, M.roundNumber)
        elif M.experiment.name == 'HiFat2Experiment':
            M.MSIFile = M.experiment.exp_dir + "hcmHFD2e2r1_MSI_FF.csv"
        elif M.experiment.name == 'TwoCFastExperiment':
            M.MSIFile = M.experiment.exp_dir + "hcm2CFASTe1r1_MSI_FF.csv"
        elif M.experiment.name == 'FluoxetineExperiment':
            M.MSIFile = M.experiment.exp_dir + "B6FLX_DaySummary/hcmB6FLXe1r1_MSI_FF.csv"
        elif M.experiment.name == 'ZeroLightExperiment':
            M.MSIFile = M.experiment.exp_dir + "ZeroLight_DaySummary/hcmZEROLIGHTe1r1_MSI_FF.csv"
            
        # print "mouseNumber %d has been assigned MSIFile %s"%(M.mouseNumber, M.MSIFile)
        M.startInactiveTimeThreshold = 60.0*M.experiment.IST_in_minutes_by_group_name[M.group.name]    # secs


    def count_mousedays(self):  
        days_no=[]
        days_ok=[]
        start_day = self.experiment.daysToUse[0]-1
        end_day = self.experiment.daysToUse[-1]
        for MD in self.mouse_days[start_day:end_day]:
            if MD.ignored:
                days_no.append(MD.dayNumber)
            else:
                days_ok.append(MD.dayNumber)
        
        return days_ok, days_no


    def get_maintenance_time(self): 
        rec_time = []
        labels = []
        for MD in self.mouse_days:
            if MD.dayNumber in self.experiment.daysToUse:
                rec_time.append(MD.load('recording_start_stop_time'))
                labels.append([MD.groupNumber, MD.mouseNumber, MD.dayNumber])

        rec_time = np.array(rec_time)
        arr_size = len(rec_time) - 1

        maintenance_time = np.zeros((arr_size, 2))
        new_labels = np.zeros((arr_size, 3))
        for c in xrange(arr_size):
            maintenance_time[c] = rec_time[c, 1] - 24*3600, rec_time[c+1, 0]
            new_labels[c] = labels[c+1] 
        return maintenance_time, new_labels


    def generate_AS_structure(self, days, cycle='24H'):

        days_to_use = self.experiment.daysToUse if days is None else days

        cnt_AS = 0
        d = {}
        for MD in self.mouse_days:
            if MD.dayNumber in days_to_use:
                if not MD.ignored:
                    allAS = MD.get_AS_in_cycle(cycle)
                    allF, allW, allM = [MD.load(x) \
                            for x in ['FB_timeSet', 'WB_timeSet', 'MB_timeSet']]
                    FWM_union = Intervals(allM).union(Intervals(allF)).union(Intervals(allW))
                    FWM_c = FWM_union.complement().intervals 
                    for AS in allAS:
                        # intersect bouts with AS
                        F, W, M, other = [Intervals(AS).intersect(Intervals(x)).intervals - AS[0] \
                                    for x in [allF, allW, allM, FWM_c]]
                        d[cnt_AS] = ([F, W, M, other], np.diff(AS)[0])
                        cnt_AS +=1

        sorted_values = sorted(d.values(), key=itemgetter(1))
        sorted_list = [k[0] for k in sorted_values]

        return sorted_list


    def get_figtitle(self):
        string = self.experiment.get_days_to_use_text()
        fig_title = '%s Experiment\n%s days: %s\ngroup%d: %s, M%d' %(
                        self.experiment.short_name,
                        self.experiment.use_days.replace('_', '-').title(), string,
                        self.groupNumber, self.experiment.strain_names[self.groupNumber], 
                        self.mouseNumber)
        return fig_title


        # title = '%s\ngroup%d: %s\nM%d\n' %(self.experiment.short_name, self.groupNumber, self.experiment.strain_names[self.groupNumber], self.mouseNumber, self.experiment.use_days, self.experiment.daysToUse[0], self.experiment.daysToUse[-1])

