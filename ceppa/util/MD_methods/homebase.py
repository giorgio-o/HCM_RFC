import numpy as np
import time
from ceppa.util.cage import Cage

"""
G.Onnis, 03.2016

Tecott Lab UCSF
"""


def designate_homebase(self, xbins=2, ybins=4):
    """ Takes self.CT, self.CX, self.CY data and tries to find Mouse cage Nest
        returns list of tuples, each tuple the index in 2 x 4 discretization of cage
        (e.g. most mice will return [(0,0)])
    """
    C = Cage()
    tot = getattr(self, 'bin_times_24H_xbins%d_ybins%d' %(xbins, ybins))
    idx = np.unravel_index(tot.argmax(), tot.shape)
    max_time = tot.max()
    # set observed homebase
    self.obs_HB = np.array(self.map_obs_rectangle_to_cage((self.NLX, self.NLY)))    #obs_ethel
    # if largest time at niche
    if idx == (0, 0):# and (max_time / tot.sum()) > .5:
        print "designated single homebase: niche, ", idx
        self.rect_HB = [idx]
        return [idx]

    # if not niche, use domino
    idx_domino = self.max_domino(tot)
    self.rect_HB = idx_domino
    return idx_domino


def max_domino(self, tot):
    """ given top left is (0, 0) and given a cell idx = (y, x), returns
        three kinds of dominoes and sums in tot: (L)eft, (R)ight, (M)iddle  
    """
    ybins, xbins = tot.shape
    L_max = 0
    for y in xrange(ybins - 1):
        domino_tot = tot[y, 0] + tot[y + 1, 0]
        if domino_tot > L_max:
            L = [(y, 0), (y + 1, 0)]
            L_max = domino_tot
    R_max = 0
    for y in xrange(ybins - 1):
        domino_tot = tot[y, 1] + tot[y + 1, 1]
        if domino_tot > R_max:
            R = [(y, 1), (y + 1, 1)]
            R_max = domino_tot
    M_max = 0
    for y in xrange(ybins):
        domino_tot = tot[y, 0] + tot[y, 1]
        if domino_tot > M_max:
            M = [(y, 0), (y, 1)]
            M_max = domino_tot

    all_arr = [L, R, M]
    idx = np.argmax([L_max, R_max, M_max])
    hb_domino = all_arr[idx]    # coordinates
    domino_times = [tot[hb_domino[0]] / tot.sum(), tot[hb_domino[1]] / tot.sum()]
    id_max = np.argmax(domino_times) # either 0 or 1
    hb_max = hb_domino[id_max]
    if (0, 0) not in hb_domino:     # niche can't be in a domino        
        if domino_times[1 - id_max] > 0.25:#0.2:    
            print "designated domino homebase, ", hb_domino        
            return hb_domino
    print "designated single homebase, ", hb_max
    return [hb_max]


def index_coordinates_at_homebase(self, xbins=2, ybins=4):
    """breaks up CT, CX, CY into Move components and corresponding M_at_HB_Set vs M_out_HB_Set:
        nest, or homebase, is given as a rectangle in a 2 x 4 dicretization of cage.
        _at_HB: movemements that occur at nest location (will be part of IS) 
        _out_HB: outside homebase
        returns CT idx at nest
    """
    startTime = time.clock()

    C = Cage()
    
    rectangle = getattr(self, 'rect_HB')
    
    num_movements = self.CT.shape[0]
    
    idx_list = []
    for rect in rectangle:
        tl, tr, bl, br = self.map_xbins_ybins_to_cage(rectangle=rect, xbins=xbins, ybins=ybins)
        print "Homebase location in original coordinates top_left, top_right, bot_left, bot_right: "
        print tl, tr, bl, br

        if rect == (0, 0):  
            # REMOVE NEST ENCLOSURE
            string = 'in Niche'
            # these are correct cage boundaries -/+something to allow for match 
            # with gridcells in a 2x4 discretization
            less_than_x = C.nestRightX - 1.2 
            greater_than_y = C.nestBottomY + 0.7 
            # 200x faster 
            idx = (self.CX < less_than_x) & (self.CY > greater_than_y)
            idx_list.append(idx)
        else:  
            # REMOVE other HB
            string = 'at other HB'
            idx1 = (self.CX > tl[0]) & (self.CX < tr[0])
            idx2 = (self.CY < tl[1]) & (self.CY > bl[1])
            idx = idx1 & idx2
            idx_list.append(idx)

    if len(idx_list) == 1:
        idx = idx_list[0]
    else:
        idx = idx_list[0] | idx_list[1]

    stopTime = time.clock()
    formatter = (sum(idx), num_movements, 100.*sum(idx)/num_movements, string, stopTime-startTime)
    print "indexed %d/%d (%1.1fpercent) movements %s, took: %fs" %formatter
    self.idx_at_HB = idx
    return idx      # when at nest


def map_xbins_ybins_to_cage(self, rectangle=(0, 0), xbins=2, ybins=4):
    """ converts a rectangle in xbins x ybins to corresponding rectangle in Cage coordinates 
        format is [[p1, p2], [p3, p4]] where pi = (cage_height_location, cage_length_location)
        ### THIS GIVES WRONG CAGE LOCATIONS for top bottom left right
        # # # xbins ybins do NOT reflect cage geometry perfectly    
    """
    C = Cage()
    L = C.CMXUpper - C.CMXLower 
    H = C.CMYUpper - C.CMYLower
    delta_x = L / xbins
    delta_y = H / ybins
    h, l = rectangle
    coord_y = C.CMYUpper - delta_y * h
    coord_x = C.CMXLower + delta_x * l
    return ((coord_x, coord_y), (coord_x + delta_x, coord_y),
        (coord_x, coord_y - delta_y), (coord_x + delta_x, coord_y - delta_y))


def get_cage_cell_id(self, T, X, Y, xbins=2, ybins=4, NUMERIC=False):
    """ returns cell id given position
    """
    print "computing cell idx positions.."
    cell_ids = []
    cell_nums = []
    for t in xrange(T.shape[0]):
        if X[t] <= -6.25:
            if Y[t] >= 31.8:
                rect = (0, 0)
            elif (Y[t] >= 20.6 and Y[t] < 31.8):
                rect = (1, 0)
            elif (Y[t] >= 9.4 and Y[t] < 20.6):
                rect = (2, 0)
            elif (Y[t] >= -2 and Y[t] < 9.4):
                rect = (3, 0)
        elif X[t] > -6.25:
            if Y[t] >= 31.8:
                rect = (0, 1)
            elif (Y[t] >= 20.6 and Y[t] < 31.8):
                rect = (1, 1)
            elif (Y[t] >= 9.4 and Y[t] < 20.6):
                rect = (2, 1)
            elif (Y[t] >= -2 and Y[t] < 9.4):
                rect = (3, 1)

        cell_ids.append(rect)
        cell_nums.append(2 * rect[0] + rect[1])
    if NUMERIC:
        return np.array(cell_nums)
    return cell_ids


# # # # # #  #  HB checking stuff

def compare_homebase_locations_to_ethel_obs(self):
    nest = getattr(self, 'rect_HB')
    is_niche = False
    # if [0, 0] in nest:
    if [0, 0] in nest.tolist():
        is_niche = True
    # observed nest ETHEL: (ybins, xbins): (3, 7) top left. (1, 1) bottom right.  
    obs_ethel = (self.NLX, self.NLY)

    # # correct observations by ethel's remarks
    # 3:6 is not in the niche. My guess is, sometimes, the experimenter would assign 3:6 if the nest is in the corner of the cage & the niche. 
    # The more accurate location would be 3:5. Unfortunately, this might be true for other experiments as well. 
    
    # As for 2,7 & 2,6, as far as I remember, I have never recorded those coordinates for a standard HCM experiment (1-bottle). 
    # Maybe because half of the grid is covered by the niche. 
    # If you see 2, 7, it is more likely a typo error. It could be a 3,7 instead of 2,7. 
    # For 2,6, that will be 1,6. 
    # One way of checking if the designation is correct is by looking at the X,Y plotts (Matlab). 
    # The blue square you see on the figure is what the experimenter has assigned as the nest location. 
    # If in case the blue square has a different location from what the system has picked up, then the system will have the right coordinates.
    if (self.NLX, self.NLY) == (3, 6):
        obs_ethel = (3, 5)
        print "corrected by Ethel: %s to %s" %((self.NLX, self.NLY), (3, 5))
        
    elif (self.NLX, self.NLY) == (2, 7):
        obs_ethel = (3, 7)
        print "corrected by Ethel: %s to %s" %((self.NLX, self.NLY), (3, 7))
    elif (self.NLX, self.NLY) == (2, 6):
        obs_ethel = (1, 6)
        print "corrected by Ethel: %s to %s" %((self.NLX, self.NLY), (1, 6))

    # test correspondence in (2, 4)
    is_consistent_ethyl, obs_newcoord = self.test_homebase_locations(nest, obs_ethel)
    # printout
    string1 = ', same as Ethyl'
    if not is_consistent_ethyl:
        string1 = ', different than Ethyl: nest %s, obs %s' %(nest, obs_ethel)
        if self.ignored:
            string1 = ', different than Ethyl: nest %s, obs %s (this MD is ignored)' %(nest, obs_ethel)

    if [0, 0] in nest.tolist() and len(nest) == 1:
        print "..single HB in Niche" + string1
    else:
        if len(nest) == 1:
            print "..single HB off Niche" + string1
        else:
            print "..domino HB off Niche" + string1
    return obs_newcoord, is_consistent_ethyl, is_niche


def test_homebase_locations(self, rect, obs_ethel):
    """ converts observed homebase rectangle from (3, 7) cage 
        (ybins, xbins): (3, 7) top left, (1, 1) bottom right. 
        to (0, 0) top left, (3, 1) bottom right
        into a (2, 4) cage discretization
    """
    print "testing obs vs detected homebase.."
    # (2, 4) cells consistent with a (3, 7)
    # niche: according to ethel
    consistent = map_obs_rectangle_to_cage(obs_ethel)
    # test
    if len(rect) == 1:
        if rect.tolist()[0] in consistent:
            return True, consistent
    elif len(rect) == 2:
        if (rect.tolist()[0] in consistent) or (rect.tolist()[1] in consistent):
            return True, consistent
    return False, consistent


def map_obs_rectangle_to_cage(self, obs_ethel):
    """ return ethel coordinates in (2,4) grid discretization
    """
    a, b = obs_ethel
    if a >= 2 and b == 7:
        consistent = [[0, 0]]

    # out of niche
    elif a == 3 and b == 6:
        consistent = [[1, 0]]
    elif a == 2 and b == 6:
        consistent =  [[0, 1]]  

    elif a == 1 and b >= 6:
        consistent = [[0, 1]]
    elif a == 1 and b == 5:
        consistent = [[1, 1]]
    elif a == 1 and b == 4:
        consistent =  [[1, 1], [2, 1]]
    elif a == 1 and b == 3:
        consistent =  [[2, 1]]
    elif a == 1 and b <= 2:
        consistent =  [[3, 1]]

    elif a == 2 and b == 5:
        consistent =  [[1, 0], [1, 1]]
    elif a == 2 and b == 4:
        print "!! Whoa mouse slept in the middle of the cage !!"
        consistent = [[1, 0], [1, 1], [2, 0], [2, 1]]
    elif a == 2 and b == 3:
        consistent =  [[2, 0], [2, 1]]
    elif a == 2 and b <= 2:
        consistent =  [[3, 0], [3, 1]]

    elif a == 3 and b == 5:
        consistent =  [[1, 0]]
    elif a == 3 and b == 4:
        consistent =  [[1, 0], [2, 0]]
    elif a == 3 and b == 3:
        consistent =  [[2, 0]]
    elif a == 3 and b <= 2:
        consistent =  [[3, 0]]

    # elif a == 0 and b == 0:         # check with Ethel
    #     consistent = [[3, 1]]
    
    return consistent




