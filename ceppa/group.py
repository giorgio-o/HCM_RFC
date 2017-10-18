import sys
import numpy as np
import os 
import pickle
from operator import itemgetter

from mouse import Mouse
from ceppa.util.intervals import Intervals


"""
D. Rhea, 2013
G.Onnis, updated: 09.2016

Tecott Lab UCSF
"""


class Group():
    def __init__(self):
        pass

    def register_and_populate(self):
        """
        this method can be run on a Group given that group.name and group.experiment have been assigned
        """
        experiment = self.experiment
        experiment.group_named[self.name] = self # register it with its parent experiment indexed by name
        experiment.group_numbered[self.number] = self # register it as indexed by group.number
        experiment.groups.append(self) # register it in the list of groups
        
        # self.color = experiment.groupname_to_color_dictionary[self.name]
        # self.marker = experiment.groupname_to_marker_dictionary[self.name]
        self.individual_numbered = {} # the individuals of the group indexed by their number
        self.mouse_numbered = {} # the individuals of the group indexed by mouseNumber
        self.individuals = [] # the list of all the individuals in the group

        for individualNumber, mouseNumber in enumerate(experiment.group_name_to_mouse_number_list_dictionary[self.name]):
            M = Mouse()
            M.mouseNumber = mouseNumber # the true name of a mouse
            M.group = self # point to its parent
            M.individualNumber = individualNumber   # legacy stuff
            M.add_days_and_register_with_group()    # add mousedays

            
    def __str__(self):
        s='Group('
        for attribute in ['experiment', 'number', 'name']:
            if hasattr(self, attribute):
                s += '%s=%s, ' % (attribute, getattr(self,attribute))
            else:
                s += '%s=Unknown, ' % (attribute)

        s = s[:-2] # remove that last comma space
        s += ')' 
        return s
        

    def __repr__(self):
        s='Group('
        for attribute in ['experiment', 'number', 'name']:
            if hasattr(self,attribute):
                s += '%s=%s, ' % (attribute, getattr(self,attribute))
            else:
                s += '%s=Unknown, ' % (attribute)
        if hasattr(self, 'individuals'):
            s += 'individuals=['
            for mouse in self.individuals:
                s += "%d, " % (mouse.mouseNumber)
            s = s[:-2] # remove that last comma space
            s += '])' 
        else:
            s += 'individuals=Unknown)'

        return s



    def count_mice(self):
        # used in subplot_all_bin_statistics, plot position density and excel table generator
        mice_no = []
        mice_ok = []
        for mouse in self.individuals:
            if mouse.ignored:
                mice_no.append(mouse.mouseNumber)
            else:
                mice_ok.append(mouse.mouseNumber)
        return mice_ok, mice_no


    def generate_AS_structure(self, day, num_AS, GENERATE=False):

        var = ['AS_timeSet', 'FB_timeSet', 'WB_timeSet', 'MB_timeSet']

        cnt_AS = 0
        d = {}
        for mouse in self.individuals:
            if not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber == day:
                        if not MD.ignored:
                            allAS, allF, allW, allM = [MD.load(x) for x in var] 
                            use_AS = allAS if num_AS is None else allAS[:num_AS]
                            for AS in use_AS:
                                F, W, M = [Intervals(AS).intersect(Intervals(x)).intervals - AS[0] \
                                            for x in [allF, allW, allM]]
                                d[cnt_AS] = ([F, W, M], np.diff(AS)[0])
                                cnt_AS +=1

        sorted_values = sorted(d.values(), key=itemgetter(1))
        sorted_list = [k[0] for k in sorted_values]

        return sorted_list


    def get_figtitle(self):
        string = self.experiment.get_days_to_use_text()
        fig_title = '%s Experiment\ngroup%d: %s\n%s days: %s' %(
            self.experiment.short_name,
            self.number, self.experiment.strain_names[self.number],
            self.experiment.use_days.replace('_', '-').title(), string
            )
        return fig_title


    # def generate_AS_structure(self, num_AS=5):

    #   all_AS = []
    #   for mouse in self.individuals:
    #       if not mouse.ignored:
    #           print mouse
    #           _AS_list = mouse.generate_AS_structure(days=self.experiment.daysToUse[0])
    #           AS_list = _AS_list if num_AS is None else _AS_list[:num_AS]
    #           all_AS.extend(AS_list)

    #   # sort AS list
    #   stop

    #   return all_AS

