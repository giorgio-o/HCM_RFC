import numpy as np


"""
G.Onnis, 01.2017
updated: 03.2016

Mouseday Class methods for corrections to data

Tecott Lab UCSF
"""


def correct_bouts_intersecting_bin(self, dist, AS_num):
    """correct for AS without move.    
        idx_th AS has no move. insert zero. HB at W. 
        lick event triggers short AS (a few secs)
    """
    _idx = []

    if self.experiment.short_name == 'HFD2':

        if self.mouseNumber == 6676 and self.dayNumber == 14 and AS_num == 0:
            _idx = 0

    return np.insert(dist, _idx, 0)



def correct_AS_without_move(self, amounts, bin_type, bin_num=None):
    """correct for AS without move.    
        idx_th AS has no move. insert zero. HB at W. 
        lick event triggers short AS (a few secs)
    """
    _idx = []


    ###### ZeroLight
    if self.experiment.short_name == 'ZeroLight':
            if self.mouseNumber == 1405 and self.dayNumber == 24:
                if bin_type == '12bins':
                    if bin_num == 5:
                        _idx = 1




    ###### 2CFast
    elif self.experiment.short_name == '2CFast':
        if self.mouseNumber == 7250 and self.dayNumber == 5:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        #'24H':
                    _idx = [4, 16]
                elif bin_num == 2:      #'LC':
                    _idx = [4, 9]
            
            elif bin_type == '12bins':
                if not self.experiment.BIN_SHIFT: 
                    if bin_num == 2:
                        _idx = 0
                    elif bin_num == 10:
                        _idx = 1
                else:
                    if bin_num in [2, 11]:
                        _idx = 1 

            elif bin_type == '24bins': 
                if not self.experiment.BIN_SHIFT:   
                    if bin_num == 4:
                        _idx = 0
                    elif bin_num == 21:
                        _idx = 1
                else:
                    if bin_num in [5, 22]:
                        _idx = 1

        elif self.mouseNumber == 7250 and self.dayNumber == 6:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [1, 9, 14]
                elif bin_num == 1:
                    _idx = 5
                elif bin_num == 2:
                    _idx = [1, 6]

            elif bin_type == '12bins': 
                if not self.experiment.BIN_SHIFT:
                    if bin_num == 1:
                        _idx = 0
                    elif bin_num in [6, 10]:
                        _idx = 1
                else:
                    if bin_num == 1:
                        _idx = 1
                    elif bin_num == 7:
                        _idx = 0
                    elif bin_num == 10:
                        _idx = 2

            elif bin_type == '24bins':
                if not self.experiment.BIN_SHIFT:     
                    if bin_num in [2, 13]:
                        _idx = 0
                    elif bin_num == 20:
                        _idx = 1
                else:
                    if bin_num in [3, 14]:
                        _idx = 0
                    elif bin_num == 21:
                        _idx = 1


        elif self.mouseNumber == 7250 and self.dayNumber == 7:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 1

            elif bin_type == '12bins':
                if not self.experiment.BIN_SHIFT: 
                    if bin_num == 0:
                        _idx = 1
                else:
                    if bin_num == 1:
                        _idx = 1

            elif bin_type == '24bins':
                if not self.experiment.BIN_SHIFT: 
                    if bin_num == 1:
                        _idx = 1
                else:
                    if bin_num == 2:
                        _idx = 1

        elif self.mouseNumber == 7250 and self.dayNumber == 8:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = 12
                elif bin_num == 1:
                    _idx = 6

            elif bin_type == '12bins': 
                if not self.experiment.BIN_SHIFT:
                    if bin_num == 8:
                        _idx = 1
                else:
                    if bin_num == 9:
                        _idx = 0

            elif bin_type == '24bins': 
                if not self.experiment.BIN_SHIFT: 
                    if bin_num == 17:
                        _idx = 0
                else:
                    if bin_num == 18:
                        _idx = 0

        elif self.mouseNumber == 7250 and self.dayNumber == 10:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    if not self.experiment.BIN_SHIFT:
                        _idx = [0, 9]
                    else:
                        _idx = [1, 10]
                elif bin_num == 1:
                    _idx = 3
                elif bin_num == 2:
                    if not self.experiment.BIN_SHIFT:
                        _idx = 0
                    else:
                        _idx = 1

            elif bin_type == '12bins': 
                if not self.experiment.BIN_SHIFT:
                    if bin_num == 0:
                        _idx = 0
                    elif bin_num == 5:
                        _idx = 1
                else:
                    if bin_num in [0, 6]:
                        _idx = 1

            elif bin_type == '24bins': 
                if not self.experiment.BIN_SHIFT: 
                    if bin_num in [0, 11]:
                        _idx = 0
                else:
                    if bin_num == 1:
                        _idx = 0
                    elif bin_num == 12:
                        _idx = 1

        elif self.mouseNumber == 7250 and self.dayNumber == 11:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [10, 12]
                elif bin_num == 2:
                    _idx = [5, 7]

            elif bin_type == '12bins': 
                if not self.experiment.BIN_SHIFT:
                    if bin_num == 9:
                        _idx = 0
                    elif bin_num == 10:
                        _idx = 1
                else:
                    if bin_num in [9, 11]:
                        _idx = 1

            elif bin_type == '24bins': 
                if not self.experiment.BIN_SHIFT:
                    if bin_num in [18, 21]:
                        _idx = 0
                else:
                    if bin_num == 19:
                        _idx = 0
                    elif bin_num == 22:
                        _idx = 1

        elif self.mouseNumber == 7250 and self.dayNumber == 12:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 1

            elif bin_type == '12bins':
                if not self.experiment.BIN_SHIFT: 
                    if bin_num == 0:
                        _idx = 1
                else:      # shifted tbins
                    if bin_num == 1:
                        _idx = 0

            elif bin_type =='24bins':
                if not self.experiment.BIN_SHIFT:
                    if bin_num == 1:
                        _idx = 0
                else:
                    if bin_num == 2:
                        _idx = 0

        elif self.mouseNumber == 7250 and self.dayNumber == 13:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    if not self.experiment.BIN_SHIFT:
                        _idx = [0, 1]
                    else:
                        _idx = [1, 2, 3]

            elif bin_type == '12bins':
                if not self.experiment.BIN_SHIFT: 
                    if bin_num == 0:
                        _idx = [0, 1]
                else:
                    if bin_num == 0:
                        _idx = [1, 1, 1]

            elif bin_type =='24bins':
                if not self.experiment.BIN_SHIFT:
                    if bin_num == 0:
                        _idx = [0, 0]
                else:
                    if bin_num == 0:
                        _idx = 1
                    elif bin_num == 1:
                        _idx = [0, 0]
                    elif bin_num == 5:
                        _idx = 0    

        elif self.mouseNumber == 7250 and self.dayNumber == 14:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 1

            elif bin_type == '12bins': 
                if not self.experiment.BIN_SHIFT:
                    if bin_num == 0:
                        _idx = 1
                else:
                    if bin_num in [1, 3, 5, 8]:
                        _idx = 0

            elif bin_type =='24bins':
                if not self.experiment.BIN_SHIFT:
                    if bin_num == 1:
                        _idx = 0
                else:
                    if bin_num in [2, 6, 10, 16]:
                        _idx = 0






    # # # HFD2
    elif self.experiment.short_name == 'HFD2':

        if self.mouseNumber == 6645 and self.dayNumber == 10:
            if bin_type == '12bins' and bin_num == 5:
                _idx = 1

        elif self.mouseNumber == 6645 and self.dayNumber == 11:
            if bin_type.endswith('cycles'):
                if bin_num == 0:              #'24H'
                    _idx = [1, 14]
                elif bin_num == 2:     #'LC'
                    _idx = [1, 6]

            elif bin_type == '12bins' and bin_num in [0, 9]:
                _idx = 1
        
        elif self.mouseNumber == 6645 and self.dayNumber == 12:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [8, 10]
                elif bin_num == 1:
                    _idx = [3, 5]

            elif bin_type == '12bins':
                if bin_num == 5:
                    _idx = 1
                elif bin_num == 6:
                    _idx = 2

        elif self.mouseNumber == 6645 and self.dayNumber == 14:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 4

            elif bin_type == '12bins' and bin_num == 2:
                _idx = 1

        elif self.mouseNumber == 6645 and self.dayNumber == 15:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = 5
                elif bin_num == 1:
                    _idx = 1

            elif bin_type == '12bins' and bin_num == 4:
                _idx = 1

        elif self.mouseNumber == 6645 and self.dayNumber == 16:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [1, 6]
                elif bin_num == 1:
                    _idx = 4
                elif bin_num == 2:
                    _idx = 1

            elif bin_type == '12bins':
                if bin_num == 1:
                    _idx = 1
                elif bin_num == 5:
                    _idx = 0

        elif self.mouseNumber == 6645 and self.dayNumber == 17:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [1, 7, 11, 12]
                elif bin_num == 1:
                    _idx = 3
                elif bin_num == 2:
                    _idx = [1, 5, 6]

            elif bin_type == '12bins':
                if bin_num == 0:
                    _idx = 1
                elif bin_num == 6:
                    _idx = 1
                elif bin_num == 9:
                    _idx = [1, 2]

        elif self.mouseNumber == 6645 and self.dayNumber == 18:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [6, 9]
                elif bin_num == 1:
                    _idx = [2, 5]

            elif bin_type == '12bins':
                if bin_num == 4:
                    _idx = 2
                elif bin_num == 7:
                    _idx = 1

        elif self.mouseNumber == 6645 and self.dayNumber == 19:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = [0, 1]

            elif bin_type == '12bins' and bin_num in [0, 1]:
                _idx = 0

        elif self.mouseNumber == 6645 and self.dayNumber == 20:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [1, 6, 8]
                elif bin_num == 1:
                    _idx = [2, 4]
                elif bin_num == 2:
                    _idx = 1

            elif bin_type == '12bins':
                if bin_num in [0, 5]:
                    _idx = 1
                elif bin_num == 6:
                    _idx = 2

        elif self.mouseNumber == 6645 and self.dayNumber == 21:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = 5
                elif bin_num == 1:
                    _idx = 1

            elif bin_type == '12bins' and bin_num == 4:
                    _idx = 1

        elif self.mouseNumber == 6645 and self.dayNumber == 22:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 3

            elif bin_type == '12bins' and bin_num == 1:
                _idx = 2

        elif self.mouseNumber == 6645 and self.dayNumber == 23:
            if bin_type == '12bins' and bin_num == 1:
                _idx = 0

        elif self.mouseNumber == 6645 and self.dayNumber == 24:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = 9
                elif bin_num == 1:
                    _idx = 4
                elif bin_num == 2:
                    _idx = 6

            elif bin_type == '12bins': 
                if bin_num == 6:
                    _idx = 2
                elif bin_num == 9:
                    _idx = 0

        elif self.mouseNumber == 6645 and self.dayNumber == 25:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 2
                    
            elif bin_type == '12bins' and bin_num == 1:
                _idx = 1


        elif self.mouseNumber == 6645 and self.dayNumber == 26:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 0

            elif bin_type == '12bins' and bin_num == 0:
                _idx = 0

        elif self.mouseNumber == 6645 and self.dayNumber == 27:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = 8
                elif bin_num == 1:
                    _idx = 2

            elif bin_type == '12bins' and bin_num == 4:
                _idx = 1

        elif self.mouseNumber == 6647 and self.dayNumber == 20:
            if bin_type == '12bins' and bin_num == 5:
                amounts[2] = 0
                return amounts

        elif self.mouseNumber == 6708 and self.dayNumber == 14:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = 7
                elif bin_num == 1:
                    _idx = 3

            elif bin_type == '12bins' and bin_num == 6:
                _idx = 1        

        elif self.mouseNumber == 6708 and self.dayNumber == 16:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 1

            elif bin_type == '12bins' and bin_num == 0:
                _idx = 1 

        elif self.mouseNumber == 6708 and self.dayNumber == 23:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 3

            elif bin_type == '12bins' and bin_num == 1:
                _idx = 1 

        elif self.mouseNumber == 6708 and self.dayNumber == 24:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [1, 8]
                elif bin_num == 1:
                    _idx = 4
                elif bin_num == 2:
                    _idx = 1

            elif bin_type == '12bins':
                if bin_num in [0, 6]:
                    _idx = 1

        elif self.mouseNumber == 6708 and self.dayNumber == 25:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = [1, 3]

            elif bin_type == '12bins':
                if bin_num == 0:
                    _idx = 1 
                elif bin_num == 1:
                    _idx = 2


        elif self.mouseNumber == 6708 and self.dayNumber == 26:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [5, 13]
                elif bin_num == 2:
                    _idx = [5, 7]

            elif bin_type == '12bins': 
                if bin_num == 2:
                    _idx = [0, 1]
                elif bin_num == 10:
                    _idx = 0

        elif self.mouseNumber == 6708 and self.dayNumber == 27:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 3

            elif bin_type == '12bins' and bin_num == 1:
                _idx = 1







    ######## HFD1
    elif self.experiment.short_name == 'HFD1':
        # correct as above HFD2
        if self.mouseNumber == 5737 and self.dayNumber == 5:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        # 24H
                    _idx = 14
                elif bin_num == 2:      # LC
                    _idx = 6

            elif bin_type == '12bins' and bin_num == 10:
                _idx = 1

        elif self.mouseNumber == 5737 and self.dayNumber == 6:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        # 24H
                    _idx = [0, 7, 10]
                elif bin_num == 1:      # DC
                    _idx = 6
                elif bin_num == 2:      # LC
                    _idx = [0, 3]

            elif bin_type == '12bins': 
                if bin_num in [1, 10]:
                    _idx = 0
                elif bin_num == 7:
                    _idx = 1

        elif self.mouseNumber == 5737 and self.dayNumber == 7:
            if bin_type.endswith('cycles'):
                if bin_num == 0:      
                    _idx = [5, 10]
                elif bin_num in [1, 2]:    
                    _idx = 4

            elif bin_type == '12bins':
                if bin_num in [7, 11]:
                    _idx = 0

        elif self.mouseNumber == 5737 and self.dayNumber == 8:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        
                    _idx = 11
                elif bin_num == 2:     
                    _idx = 4

            elif bin_type == '12bins' and bin_num == 10:
                _idx = 1

        elif self.mouseNumber == 5737 and self.dayNumber == 9:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        
                    _idx = 9
                elif bin_num == 1:     
                    _idx = 6

            elif bin_type == '12bins' and bin_num == 7:
                _idx = 2

        elif self.mouseNumber == 5737 and self.dayNumber == 10:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        
                    _idx = 8
                elif bin_num == 1:     
                    _idx = 5

            elif bin_type == '12bins' and bin_num == 6:
                _idx = 1

        elif self.mouseNumber == 5737 and self.dayNumber == 11:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        
                    _idx = [2, 12]
                elif bin_num == 2:     
                    _idx = [2, 3]

            elif bin_type == '12bins':
                if bin_num == 2:
                    _idx = 1
                elif bin_num == 9:
                    _idx = 0

        elif self.mouseNumber == 5737 and self.dayNumber == 12:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        
                    _idx = 14
                elif bin_num == 2:     
                    _idx = 7

            elif bin_type == '12bins' and bin_num == 10:
                _idx = 1

        elif self.mouseNumber == 5737 and self.dayNumber == 13:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:        
                    _idx = [0, 2]

            elif bin_type == '12bins':
                if bin_num == 1:
                    _idx = 0
                elif bin_num == 2:
                    _idx = 1

        elif self.mouseNumber == 5737 and self.dayNumber == 14:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        
                    _idx = [10, 15]
                elif bin_num == 1:     
                    _idx = [5, 10]

            elif bin_type == '12bins':
                if bin_num == 5:
                    _idx = 2
                elif bin_num == 8:
                    _idx = 0

        elif self.mouseNumber == 5737 and self.dayNumber == 15:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        
                    _idx = [12, 15]
                elif bin_num == 2:     
                    _idx = [5, 8]

            elif bin_type == '12bins' and bin_num in [9, 11]:
                _idx = 1

        elif self.mouseNumber == 5737 and self.dayNumber == 16:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        
                    _idx = [4, 10, 12]
                elif bin_num == 1:      
                    _idx = 6
                elif bin_num == 2:      
                    _idx = [4, 5]

            elif bin_type == '12bins':
                if bin_num == 2:
                    _idx = 1
                elif bin_num == 7:
                    _idx = 2
                elif bin_num == 10:
                    _idx = 0





    # # # # ## Strain Survey
    elif self.experiment.short_name == 'SS':

        if self.mouseNumber == 3103 and self.dayNumber == 10:
            if bin_type.endswith('cycles'):
                if bin_num == 0:        #24H
                    _idx = 7
                elif bin_num == 1:      #DC
                    _idx = 4
            
            elif bin_type == '12bins' and bin_num == 6:
                _idx = 1

        elif self.mouseNumber == 2107 and self.dayNumber == 12:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 0
            
            elif bin_type == '12bins' and bin_num == 0:
                _idx = 0

        elif self.mouseNumber == 2207 and self.dayNumber == 7:
            if bin_type.endswith('cycles'):
                if bin_num == 0: 
                    _idx = 8
                elif bin_num == 1: 
                    _idx = 3

            elif bin_type == '12bins' and bin_num == 7:
                _idx = 1

        elif self.mouseNumber == 2207 and self.dayNumber == 9:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [1, 11]
                elif bin_num == 2:
                    _idx = [1, 6]

            elif bin_type == '12bins':
                if bin_num == 1:
                    _idx = 0
                elif bin_num == 9:
                    _idx = 1

        elif self.mouseNumber == 2207 and self.dayNumber == 10:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = 12
                elif bin_num == 2:
                    _idx = 6

            elif bin_type == '12bins' and bin_num == 9:
                _idx = 0

        elif self.mouseNumber == 2207 and self.dayNumber == 12:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = [0, 3]

            elif bin_type == '12bins':
                if bin_num in [0, 2]:
                    _idx = 0

        elif self.mouseNumber == 2207 and self.dayNumber == 13:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = [1, 3]
            
            elif bin_type == '12bins':
                if bin_num == 0:
                    _idx = 1
                elif bin_num == 2:
                    _idx = 0

        elif self.mouseNumber == 2207 and self.dayNumber == 15:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 1

            elif bin_type == '12bins' and bin_num == 1:
                _idx = 0

        elif self.mouseNumber == 2207 and self.dayNumber == 16:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = 10
                elif bin_num == 1:
                    _idx = 4

            elif bin_type == '12bins' and bin_num == 7:
                _idx = 1

        elif self.mouseNumber == 8107 and self.dayNumber == 9:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 0

            elif bin_type == '12bins' and bin_num == 0:
                _idx = 0

        elif self.mouseNumber == 8107 and self.dayNumber == 16:         # this one here. look at food bin0,1
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 0

            elif bin_type == '12bins' and bin_num in [0, 1]:
                _idx = 0

        elif self.mouseNumber == 8407 and self.dayNumber == 6:
            if bin_type.endswith('cycles'):
                    if bin_num == 0:
                        _idx = 11
                    elif bin_num == 2:
                        _idx = 4

            elif bin_type == '12bins' and bin_num == 9:
                _idx = 1

        elif self.mouseNumber == 8407 and self.dayNumber == 7:
            if bin_type.endswith('cycles'):
                    if bin_num == 0:
                        _idx = 10
                    elif bin_num == 1:
                        _idx = 6

            elif bin_type == '12bins' and bin_num == 6:
                _idx = 1

        elif self.mouseNumber == 8407 and self.dayNumber == 8:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 1

            elif bin_type == '12bins' and bin_num == 1:
                _idx = 1

        elif self.mouseNumber == 8407 and self.dayNumber == 11:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 1

            elif bin_type == '12bins' and bin_num == 0:
                _idx = 1

        elif self.mouseNumber == 8407 and self.dayNumber == 12:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 1

            elif bin_type == '12bins' and bin_num == 2:
                _idx = 0

        elif self.mouseNumber == 8407 and self.dayNumber == 13:
            if bin_type.endswith('cycles'):
                    if bin_num == 0:
                        _idx = [2, 13]
                    elif bin_num == 1:
                        _idx = 10
                    elif bin_num == 2:
                        _idx = 2

            elif bin_type == '12bins':
                if bin_num == 2:
                    _idx = 0
                elif bin_num == 8:
                    _idx = 1

        elif self.mouseNumber == 8407 and self.dayNumber == 14:
            if bin_type.endswith('cycles'):
                    if bin_num == 0:
                        _idx = 9
                    elif bin_num == 1:
                        _idx = 6

            elif bin_type == '12bins' and bin_num == 5:
                _idx = 2

        elif self.mouseNumber == 8407 and self.dayNumber == 16:
            if bin_type.endswith('cycles'):
                    if bin_num == 0:
                        _idx = 13
                    elif bin_num == 2:
                        _idx = 3

            elif bin_type == '12bins' and bin_num == 9:
                _idx = 0


        # the following will anyway be ignored
        elif self.mouseNumber == 7210 and self.dayNumber == 10:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [4, 7]
                elif bin_num == 1:
                    _idx = [1, 4]

        elif self.mouseNumber == 7210 and self.dayNumber == 11:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = [1, 1]

        elif self.mouseNumber == 7210 and self.dayNumber == 12:
            if bin_type.endswith('cycles'):
                if bin_num in [0, 2]:
                    _idx = 2

        elif self.mouseNumber == 7210 and self.dayNumber == 13:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [3, 4]
                elif bin_num == 1:
                    _idx = [1, 2]

        elif self.mouseNumber == 7210 and self.dayNumber == 14:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [5, 6, 6, 9]
                elif bin_num == 1:
                    _idx = [4, 5, 5]
                elif bin_num == 2:
                    _idx = 4

        elif self.mouseNumber == 7210 and self.dayNumber == 15:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = 6
                elif bin_num == 1:
                    _idx = 3

        elif self.mouseNumber == 7210 and self.dayNumber == 16:
            if bin_type.endswith('cycles'):
                if bin_num == 0:
                    _idx = [1, 7, 9]
                elif bin_num == 1:
                    _idx = [5, 7]
                elif bin_num == 2:
                    _idx = 1


    return np.insert(amounts, _idx, 0)

