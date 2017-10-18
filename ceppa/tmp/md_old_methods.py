



    # # # old active states (Oct2016)

    # def generate_active_states_old_def(self):
    #     """ old definition, using events
    #     """
    #     IST = getattr(self.experiment, 'IST') 
    #     print "designating AS, IST=%1.2fm.." %(IST / 60)
    #     varNames = ['F_Sets', 'W_Sets', 'CT_out_HB', 'idx_at_HB']
    #     for varName in varNames:
    #         if not hasattr(self, varName):
    #             self.load(varName)

    #     food, water, move, idx = [getattr(self, name) for name in varNames]
        
    #     F, W = Intervals(food), Intervals(water)    

    #     print "%d F events\n%d W events" %(food.shape[0], water.shape[0])
        
    #     # # from ethologic definition of AS, movements at homebase are part of inactive state.
    #     # # and must be removed 
    #     # # builds arrays of start/stop times (HCM min resolution) wide out of position timestamps
    #     M = my_utils.timestamps_to_interval(move)
        
    #     print "%d out_HB, %d at_HB Move events\n%d Move total" %(move.shape[0], idx.sum(), idx.sum() + move.shape[0])
        
    #     # use CT_NHB with nest removed timestamps. 
    #     tmp = F + W
    #     I_events = M + tmp                        
        
    #     arr_AS = I_events.connect_gaps(eps=IST).intervals       # apply IST
    #     I_start_stop = Intervals([self.recordingStartTime, self.recordingEndTime])
    #     IAS = I_events.complement().intersect(I_start_stop).trim(eps=IST*60.)

    #     print "designated %s AS" %arr_AS.shape[0]        
    #     setattr(self, varName, arr_AS)
    #     return arr_AS


    # # # old bouts



    # def get_CT_bins(self, num_bins=11):
    #   """ returns a list of (num_bins) Intervals for the 24 hours.
    #       adds bin.center attribute to bin interval. 
    #       bin in hours after midnight:
    #       bin 0: [[ 15.  17.]]
    #       bin 1: [[ 17.  19.]]
    #       ...
    #       bin 10:[[ 35.  37.]]

    #       CT time is bin-7:
    #       bin 0: [[ 8.  10.]]
    #       bin 1: [[ 10.  12.]]
    #       ...
    #       bin 10:[[ 28.  30.]]

    #       Note bin 11: CT 30-32 (CT6-8) is excluded from analysis.
    #   """
        
    #   starth = 16     # hours after midnight
    #   endh = 38
    #   step = 2
    #   bins = [Intervals([center-1.0, center+1.0]) for center in xrange(starth, endh, step)]


    #   for c, bin in enumerate(bins): 
    #       setattr(bin, 'center', bin.intervals.mean())
        
    #   return bins

    # # # old
    # def log_ignored_mouse(self, string, sub_dir=''):
    #   f=open(self.experiment.binary_dir + sub_dir + 'log_ignored_mousedays.txt','a') #open for appending
    #   f.write(string+'\n')
    #   f.close()







    # def check_and_correct_events_at_device(self, I_E, I_at_device, act='F'):
    #     I_diffs = I_at_device.complement().intersect(I_E)
    #     if not I_diffs.is_empty():
    #         print "%s_device position error, diff %1.4f" %(act, I_diffs.measure())
    #         I_E = I_E.intersect(I_at_device)
    #     else:
    #         print "position at %s_device check ok" %act
    #     return I_E



    # def get_bouts_Ch(self, F, BT=30., act='F'):
    #     """Chris' method
    #     """
    #     startTime = time.clock()

    #     print "computing %s bouts, Ch, BT=%1.1fs.." %(act_type, BT)

    #     # F = self.load('feedingSet')
    #     F = Intervals(F)
    #     CT, CX, CY = self.load('CT'), self.load('CX'), self.load('CY')
    #     start_time, stop_time = self.load('recordingStartTimeEndTime')
    #     M = np.vstack([CT, CX, CY])
    #     pos_subset = pull_locom_tseries_subset(M, start_time, stop_time)

    #     TXY_F_idx = idx_restrict_to_rectangles(pos_subset, rects=[(3, 0)])  # M events in FOOD area
    #     TXY_W_idx = idx_restrict_to_rectangles(pos_subset, rects=[(3, 1)])  # M evenets in Water area

    #     F_bout = F.union(plot_utils.timestamps_to_interval(pos_subset[0, TXY_F_idx])).connect_gaps(BT)
        
        
    #     num_bouts = F_bout.intervals.shape[0]
    #     print "num_bouts =", num_bouts

    #     stopTime = time.clock()

    #     print "%s bout designation took %fs"%(act_type, stopTime-startTime)


    #     return F_bout




    # def get_bouts(self, act_type='F', BT=1):
    #     """
    #     """
    #     startTime = time.clock()

    #     if act_type == 'F':
    #         I_E = self.load('feedingSet')   
    #     elif act_type == 'W':
    #         I_E = self.load('drinkingSet')  

        
    #     I_at_device = self.get_interval_at_device(act_type=act_type)

    #     # # check pb events subset of at_F. if not, correct
    #     I_E_corr = self.check_and_correct_events_at_device(I_E, I_at_device, act_type=act_type)         

    #     print "computing %s bouts, BT=%1.1fs.." %(act_type, BT)

    #     # get bouts
    #     B = np.zeros((1, 2))    
        
    #     # # # no at_device constraint   
    #     # bout = I_E_corr.connect_gaps(eps=BT)
            
    #     # B = np.vstack([B, bout.intervals])
        
    #     # w at_device constraint
    #     for k, x in enumerate(I_at_device.intervals):
            
    #         X = Intervals(x)        
    #         Y = X.intersect(I_E_corr)   # compute bouts on corrected
            
    #         if Y.intervals.shape[0] == 0:       # no feeding events at feeder
    #             bout = Intervals(np.array([]))
                
    #         elif Y.intervals.shape[0] == 1:     # one event only at feeder
    #         # may add additional constraint on this event to be a bout
    #             bout = Y

    #         elif Y.intervals.shape[0] > 1:      # BT threshold [sec]
    #             bout = Y.connect_gaps(eps=BT)
                
    #         if not bout.is_empty():
    #             B = np.vstack([B, bout.intervals])


    #     num_bouts = B.shape[0]
    #     print "num_bouts =", num_bouts

    #     stopTime = time.clock()

    #     print "%s bout designation took %fs"%(act_type, stopTime-startTime)
        
    #     return Intervals(B[1:]), I_at_device, I_E_corr




    # def get_interval_at_device(self, act_type='F'):
    #     """
    #     """

    #     C = Cage()
        
    #     CT, CX, CY = self.load('CT'), self.load('CX'), self.load('CY')

    #     num_movements = CT.shape[0]


    #     # get start and stop time at Feeder cell 
    #     xbins = 2
    #     ybins = 4
    #     if act_type == 'F':
    #         D_cell = (3, 0)
    #     elif act_type == 'W':
    #         D_cell = (3, 1)
    
    #     tl, tr, bl, br = self.map_xbins_ybins_to_cage(rectangle=D_cell, xbins=xbins, ybins=ybins)

    #     # print "Mouse at device location in original coordinates top_left, top_right, bot_left, bot_right: "
    #     # print tl, tr, bl, br
    #     # # nest: (0, 0)(-16.25, 43.0) (-6.25, 43.0) (-16.25, 32.5) (-6.25, 32.5)

    #     less_than_x = tr[0]
    #     less_than_y = tl[1] 

    #     # is at feeder, binary
    #     is_at_device = np.zeros(num_movements, dtype=bool)

    #     for t in xrange(num_movements):

    #         if CX[t] < less_than_x and CY[t] < less_than_y:
                
    #             is_at_device[t] = True

    #     is_at_device[0] = False     # get rid of problems
    #     is_at_device[-1] = False

    #     # start/stop time 
    #     arr = np.zeros((1, 2))

    #     for t in xrange(1, num_movements-1):
            
    #         if not is_at_device[t-1] and is_at_device[t]:

    #             t_start = CT[t]

        
    #         elif is_at_device[t] and not is_at_device[t+1]:

    #             t_stop = CT[t]

    #             arr = np.vstack([arr, np.array([t_start, t_stop])])

        
    #     arr = arr[1:]

    #     return Intervals(arr)








    # # # # # # OTHER. DO NOT DELETE.
    ########### USEFUL FUNCTIONALITIES (to be reworked)


    # def get_active_state_counts(self, num_bins=11):
    #   """returns array with active state count in 11 2hr bins,
    #       starting at 15 after midnight: bin0 = 15.00-17.00 = 08-10 CT
    #   """
    #   if not hasattr(self, 'activeStateSet'):
    #       self.load('activeStateSet')

    #   activeStateSet = Intervals(self.activeStateSet.intervals/3600.)     # hrs

    #   counts_today = activeStateSet.intervals.shape[0]

    #   bins = self.get_CT_bins()
        
    #   arr = np.zeros(num_bins)
    #   for c, bin in enumerate(bins):
    #       AS_restr = activeStateSet.intersect(bin)
    #       arr[c] = AS_restr.intervals.shape[0]

    #   return arr, counts_today


    # def get_active_state_duration(self, num_bins=11):
    #   """returns array with active state duration in 11 2hr bins
    #   """
    #   if not hasattr(self, 'activeStateSet'):
    #       self.load('activeStateSet')

    #   activeStateSet = Intervals(self.activeStateSet.intervals/3600.)     # hrs

    #   bins = self.get_CT_bins()
        
    #   arr = np.zeros(num_bins)

    #   # print activeStateSet.intervals
    #   # print "#AS = %d" %activeStateSet.intervals.shape[0]
    #   # print

    #   for c, bin in enumerate(bins):
            
    #       bin_start = bin.intervals[0][0]
    #       bin_end = bin.intervals[0][1]
    #       bin_time = 0
            
    #       cnt = 1
    #       for AS in activeStateSet:
    #           start = AS[0]
    #           end = AS[1]
    #           if start > bin_start and start < bin_end:
    #               # print "Mouse%dDay%d, bin [%d, %d]" %(self.mouseNumber, self.dayNumber, bin_start, bin_end)
    #               # print "AS#%d, start %1.2f, end %1.2f" %(cnt, start, end)
    #               # print
    #               bin_time += AS[1] - AS[0]
    #           cnt +=1

    #       arr[c] = bin_time *60.

        
    #   # for c, bin in enumerate(bins):
    #   #   AS_restr = activeStateSet.intersect(bin)
    #   #   arr[c] = AS_restr.measure()     # this way duration is trivial, just a multiple of ASProb
            
    #   return arr



    # def get_active_state_probability(self, num_bins=11):
    #   """ returns array with active state probability in 11 2hr bins,
    #       starting at 15 after midnight: bin0 = 15.00-17.00 = 08-10 CT
    #   """
    #   if not hasattr(self, 'activeStateSet'):
    #       self.load('activeStateSet')

    #   activeStateSet = Intervals(self.activeStateSet.intervals/3600.)     # hrs

    #   bins = self.get_CT_bins()
        
    #   arr = np.zeros(num_bins)
    #   for c, bin in enumerate(bins):
    #       arr[c] = bin.intersect(activeStateSet).measure() /  bin.measure() 
        
    #   return arr


    # def get_active_state_counts(self, num_bins=11):
    #   """returns array with active state count in 11 2hr bins,
    #       starting at 15 after midnight: bin0 = 15.00-17.00 = 08-10 CT
    #   """
    #   if not hasattr(self, 'activeStateSet'):
    #       self.load('activeStateSet')

    #   activeStateSet = Intervals(self.activeStateSet.intervals/3600.)     # hrs

    #   counts_today = activeStateSet.intervals.shape[0]

    #   bins = self.get_CT_bins()
        
    #   arr = np.zeros(num_bins)
    #   for c, bin in enumerate(bins):
    #       AS_restr = activeStateSet.intersect(bin)
    #       arr[c] = AS_restr.intervals.shape[0]

    #   return arr, counts_today


    # def get_active_state_duration(self, num_bins=11):
    #   """returns array with active state duration in 11 2hr bins,
    #       starting at 15 after midnight: bin0 = 15.00-17.00 = 08-10 CT
    #   """
    #   if not hasattr(self, 'activeStateSet'):
    #       self.load('activeStateSet')

    #   activeStateSet = Intervals(self.activeStateSet.intervals/3600.)     # hrs

    #   bins = self.get_CT_bins()
        
    #   arr = np.zeros(num_bins)

    #   # print activeStateSet.intervals
    #   # print "#AS = %d" %activeStateSet.intervals.shape[0]
    #   # print

    #   for c, bin in enumerate(bins):
            
    #       bin_start = bin.intervals[0][0]
    #       bin_end = bin.intervals[0][1]
    #       bin_time = 0
            
    #       cnt = 1
    #       for AS in activeStateSet:
    #           start = AS[0]
    #           end = AS[1]
    #           if start > bin_start and start < bin_end:
    #               # print "Mouse%dDay%d, bin [%d, %d]" %(self.mouseNumber, self.dayNumber, bin_start, bin_end)
    #               # print "AS#%d, start %1.2f, end %1.2f" %(cnt, start, end)
    #               # print
    #               bin_time += AS[1] - AS[0]
    #           cnt +=1

    #       arr[c] = bin_time *60.

        
    #   # for c, bin in enumerate(bins):
    #   #   AS_restr = activeStateSet.intersect(bin)
    #   #   arr[c] = AS_restr.measure()     # this way duration is trivial, just a multiple of ASProb
            
    #   return arr




    # def get_food_water_loco_totals(self, num_bins=11, M_type='out_HB'):
    #     """ returns (3, num_bins) array with totals in 11 2hr bins,
    #         starting at 15 after midnight: bin0 = 15.00-17.00 = 08-10 CT
    #         'out_HB' : the green, or active state loco
    #         'HB' : move at homebase cell/s. the yellow, or move at homebase
    #         'TL' : all move. green and yellow
    #         'AS' : move at and out of HB, restrivted to AS. green and yellow intersected with AS
    #     """

    #     attributes = ['activeStateSet', 'feedingSet', 'drinkingSet', 'locomotionSet', 'non_locomotionSet', 'CX', 'CY', 'CT', 'C_idx_loco']

    #     for attr in attributes:
    #         if not hasattr(self, attr):
    #             self.load(attr)


    #     # feed an drink
    #     feedingSet = self.feedingSet 
    #     drinkingSet = self.drinkingSet 

    #     # get bins. transform in seconds
    #     bins = self.get_CT_bins()
    #     bins_s = [Intervals(bin.intervals*3600.) for bin in bins]

    #     fc = self.chow_eaten_grams / feedingSet.measure() * 1000.       # feeding coefficient [mg/s]
    #     lc = self.water_drunk_grams / drinkingSet.measure() * 1000.     # drinking coefficient [mg/s]

    #     food = np.zeros(num_bins)
    #     water = np.zeros(num_bins)
    #     for c, bin in enumerate(bins_s):
    #         if not feedingSet.intersect(bin).is_empty():
    #             food[c] = feedingSet.intersect(bin).measure() * fc / 1000.      # grams
    #             water[c] = drinkingSet.intersect(bin).measure() * lc / 1000.    # grams


    #     # # get movement data
    #     if M_type == 'out_HB':      # use green locomotion
    #         idx = self.C_idx_loco

    #     elif M_type == 'HB':        # yellow locomotion
    #         idx = - self.C_idx_loco

    #     elif M_type == 'TL':        # all. green and yellow, total locomotion
    #         idx = np.ones(self.C_idx_loco.shape, dtype=bool)            

    #     elif M_type == 'AS':        # green and yellow restricted to AS
    #         nts, C_idx_AS = plot_utils.time_series_intersect_intervals(self.CT, self.activeStateSet)            
    #         idx = C_idx_AS


    #     X = self.CX[idx]
    #     Y = self.CY[idx]
    #     T = self.CT[idx]


    #     # get bins in seconds
    #     bins = self.get_CT_bins()

    #     # total distance
    #     deltaDist = np.sqrt((X[1:] - X[:-1]) ** 2 + (Y[1:] - Y[:-1]) ** 2)
    #     dtpd = deltaDist.sum()  

    #     hour_idxs = np.floor(T[:-1] / 3600.0)
    #     min_idxs = np.floor(T[:-1] / 60.0)

    #     if ((min_idxs < 0) + (min_idxs >= 48 * 60)).any():
    #         print "ERROR:  hour outside of 48 hour range! hour=%f"%(T[n]/3600.0)
    #         sys.exit(-1)

    #     test = np.zeros(48)
    #     for hourIndex in xrange(48):
    #         idx = (hour_idxs == hourIndex)
    #         test[hourIndex] = deltaDist[idx].sum() / 100.       # meters

    #     loco = np.zeros(num_bins)
    #     for c, bin in enumerate(bins):
    #         loco[c] = (test[bin.center-1] + test[bin.center])

    #     M = np.zeros((3, num_bins))
    #     M[0], M[1], M[2] = food, water, loco

    #     return M





    # def get_active_state_intensity(self, M=None, num_bins=11):
    #     """returns array with active_State_intesities [/min] for: 
    #         feeding, drinking and locomotion (matrix M) into 11 2hr bins; 
    #         starting at 15 after midnight: bin0 = 15.00-17.00 = 08-10 CT
    #         if you give totals, save on computing
    #     """
    #     if not hasattr(self, 'activeStateSet'):
    #         self.load('activeStateSet')

    #     activeStateSet = Intervals(self.activeStateSet.intervals/3600.)     # hrs

    #     if M is not None:
    #         totals = M
    #     else:
    #         totals = self.get_food_water_loco_totals(M_type='AS')       # restrict to AS movements
            
    #     # transform food and drink to milligrams (loco stays in meters)
    #     totals[0] *= 1000.  
    #     totals[1] *= 1000   

    #     bins = self.get_CT_bins()
        
    #     as_time_per_bin = np.zeros(num_bins)
    #     for bin_num, bin in enumerate(bins):
    #         as_time_per_bin[bin_num] = bin.intersect(activeStateSet).measure() *60*60. # sec
    #         as_time_per_bin[as_time_per_bin < 0.05] = 0.5       # regularization

    #     arr = np.zeros((3, num_bins))
    #     for c in xrange(3):
    #         arr[c] =  np.nan_to_num(totals[c] / as_time_per_bin)

    #     return arr




#     def get_binary_AS(self, value_sys_off=-1):

#         print "input to LS, ", self

#         # set time bin width
#         step = 60.  # secs
#         # set day lenght: hours after midnight
#         CT_interval = np.array([6., 30.])       # for CT: - 7. CT6_30
#         dayStart = (CT_interval[0] + 7) * 3600.
#         dayEnd = (CT_interval[1] + 7) * 3600.

#         # array of bins with binStart time (in secs after midnight)
#         bin_arr = np.arange(dayStart, dayEnd, step)
#         num_bins = bin_arr.shape[0]

#         start_time, stop_time = self.load('recordingStartTimeEndTime')
#         active_states = self.load('activeStateSet')
#         inactive_states = self.load('inactiveStateSet')
#         loco = self.load('locomotionSet')
#         nonloco = self.load('non_locomotionSet')

#         TL = loco.union(nonloco)
#         # PL = loco 
        
#         # initialize AS with -1s, loco with 0s.     
#         arr_AS = value_sys_off * np.ones(num_bins)
#         arr_TL = np.zeros(num_bins)
#         # arr_PL = np.zeros(num_bins)
        
#         # as_cut = Intervals()      # to be eventually completed
#         # is_cut = Intervals()

#         # intersect what is out of day_interval. use variables _u 
#         # active_states_u = active_states.intersect(recording_start_stop).union(as_cut)
#         # inactive_states_u = inactive_states.intersect(recording_start_stop).union(is_cut)
        
#         for bin_ in xrange(num_bins - 1):
#             a = bin_arr[bin_]
#             b = bin_arr[bin_+1]
            
#             # active states
#             inters_measure_as = active_states.intersect_with_interval(a, b).measure()
#             inters_measure_is = inactive_states.intersect_with_interval(a, b).measure()
#             if inters_measure_as > 0:
#                 arr_AS[bin_] = 1
#             elif inters_measure_is > 0:
#                 arr_AS[bin_] = 0


#             if a <= start_time or a > stop_time:
#                 arr_TL[bin_] = value_sys_off
#                 # arr_PL[bin_] = value_sys_off
#             else:
#                 inters_measure_TL = TL.intersect_with_interval(a, b).measure()                              
#                 # inters_measure_PL = PL.intersect_with_interval(a, b).measure()                                
#                 if inters_measure_TL > 0:
#                     arr_TL[bin_] = 1
#                 # if inters_measure_PL > 0:
#                 #   arr_PL[bin] = 1

#             # # hack to get rid of spurious 0s at the end of the day
#             # if bin == num_bins-2 and a > stop_time:
#             #   arr_TL[cnt+1] = value_sys_off
#             if stop_time < dayEnd:
#                 arr_TL[-1] = value_sys_off

#             # or use .contains method of Intervals..


#         return arr_AS, arr_TL#, arr_PL







#     def get_time_budgets(self, eps=.01, num_items=6):

#         cycles = [c for c in self.experiment.cycles.values()][:-1]
#         num_cycles = len(cycles)

#         # get events as Intervals
#         AS = self.load('activeStateSet')    
#         IS = self.load('inactiveStateSet')
        
#         D = self.load('drinkingSet')
#         F = self.load('feedingSet')
#         M = self.load('locomotionSet')
#         M_HB = self.load('non_locomotionSet')
        
#         M_AS = M.union(M_HB.intersect(AS))

#         recording_start_stop = self.load('recordingStartTimeEndTime')                               
#         recordingTimeInterval = Intervals(recording_start_stop)
        
#         # connect events at eps
#         F = F.connect_gaps(eps=eps)
#         D = D.connect_gaps(eps=eps)
#         M = M.connect_gaps(eps=eps)
#         M_AS = M_AS.connect_gaps(eps=eps)
        

#         # dark/light
#         DC = Intervals([19.0 * 3600., 31.0 * 3600.])
#         LC_ = Intervals(np.vstack(([10.0, 19.0], [31.0, 40.0]))* 3600.)     # make it large enough

#         # params = recordingTimeInterval, F, D, M_AS, IS, AS, DC, LC_

    
#         from multiprocessing import Pool, Process
#         from plot_utils import worker_TB

#         p1 = Pool(4)

#         arr = np.zeros((num_cycles, num_items))

# #       params0 = recordingTimeInterval.copy(), F.copy(), D.copy(), L.copy(), NL_AS.copy(), NL_IS.copy(), IS.copy(), AS.copy(), DC.copy(), LC_.copy(), 0
#         params1 = recordingTimeInterval.copy(), F.copy(), D.copy(), M_AS.copy(), IS.copy(), AS.copy(), DC.copy(), LC_.copy(), 1
#         params2 = recordingTimeInterval.copy(), F.copy(), D.copy(), M_AS.copy(), IS.copy(), AS.copy(), DC.copy(), LC_.copy(), 2
# #       params3 = recordingTimeInterval.copy(), F.copy(), D.copy(), L.copy(), NL_AS.copy(), NL_IS.copy(), IS.copy(), AS.copy(), DC.copy(), LC_.copy(), 3
#         params4 = recordingTimeInterval.copy(), F.copy(), D.copy(), M_AS.copy(), IS.copy(), AS.copy(), DC.copy(), LC_.copy(), 4
#         params5 = recordingTimeInterval.copy(), F.copy(), D.copy(), M_AS.copy(), IS.copy(), AS.copy(), DC.copy(), LC_.copy(), 5

#         # p1 = Process(target=worker_TB, args=(params1,))

#         arr2 = np.array(p1.map(worker_TB, [params1, params2, params4, params5]))
        
#         arr[0] = arr2[0] + arr2[1]
#         arr[1] = arr2[0]
#         arr[2] = arr2[1]
#         arr[3] = arr2[2] + arr2[3]
#         arr[4] = arr2[2]
#         arr[5] = arr2[3]

#         # tests
#         np.testing.assert_almost_equal(0, np.abs((arr[4] + arr[5] - arr[3])).sum(), decimal=1, err_msg='AS DC/LC != AS 24')
#         np.testing.assert_almost_equal(0, np.abs((arr[1] + arr[2] - arr[0])).sum(), decimal=1, err_msg='DC/LC != 24')
        
# #       np.testing.assert_array_almost_equal(arr[:, 0], arr[:, 1:-1].sum(axis=1), decimal=0, err_msg='pie does not sum to one')
#         if np.abs(arr[:, 0] - arr[:, 1:].sum(axis=1)).sum() > 0.01:
#             print "\nPoqodio! %1.3f off\n" % np.abs(arr[:, 0] - arr[:, 1:].sum(axis=1)).sum()

#         p1.terminate()

#         return arr








#     def get_this_AS_food_drink_binning(self, F, D, AS_start, AS_end, ONSET=True, eps=0.01):
#         """breakfast
#         """


#         feed_interval = F.intersect_with_interval(AS_start, AS_end)
#         drink_interval = D.intersect_with_interval(AS_start, AS_end)

#         # initialize
#         bins = plot_utils.bins_for_breakfast(AS_start, AS_end)
#         num_bins = len(bins)
        
#         arr = np.zeros((2, num_bins))   # food/drink
#         arr_c = np.zeros((2, num_bins))

#         # probability
#         b = 0
#         for bin in bins:
#             l = bin_.intervals[0][0]
#             r = bin_.intervals[0][1]
            
#             if not feed_interval.intersect_with_interval(l, r).is_empty():
#                 arr[0, b] = 1
            
#             if not drink_interval.intersect_with_interval(l, r).is_empty():
#                 arr[1, b] = 1
            
#             b += 1


#         # cumulative
#         if ONSET:
#             idx_f = arr[0].argmax()
#             idx_d = arr[1].argmax()
            
#             if arr[0][idx_f] != 1:
#                 idx_f = num_bins
#             if arr[1][idx_d] != 1:
#                 idx_d = num_bins
            
#             # arr_c[0] = [0] * idx_f + [1] * (num_bins - idx_f)
#             # arr_c[1] = [0] * idx_d + [1] * (num_bins - idx_d)

#         else:       
#             idx_f = 0           
#             if len(np.where(arr[0]==1)[0]) > 0:
#                 idx_f = np.where(arr[0]==1)[0][-1]
            
#             idx_d = 0
#             if len(np.where(arr[1]==1)[0]) > 0:
#                 idx_d = np.where(arr[1]==1)[0][-1]
            
#             arr_c[0] = [1] * idx_f + [0] * (num_bins - idx_f)
#             arr_c[1] = [1] * idx_d + [0] * (num_bins - idx_d)

#         arr_c[0] = [0] * idx_f + [1] * (num_bins - idx_f)
#         arr_c[1] = [0] * idx_d + [1] * (num_bins - idx_d)       

#         return arr, arr_c




#     def get_AS_food_drink_profile(self, num_bins=180, num_seconds=900, ONSET=True, eps=0.01):
#         """ breakfast  
#         """

#         attributes = ['activeStateSet', 'feedingSet', 'drinkingSet']
            
#         for attr in attributes:
#             self.load(attr)

#         AS = self.activeStateSet
        
#         F = self.feedingSet.connect_gaps(eps=eps)
#         D = self.drinkingSet.connect_gaps(eps=eps)

#         num_AS = AS.intervals.shape[0]

#         arr_p = np.zeros((2, num_AS, num_bins))     #f/d
#         arr_c = np.zeros((2, num_AS, num_bins))

#         for k in xrange(num_AS):

#             if ONSET:
#                 AS_start = AS.intervals[k, 0]
#                 AS_end = AS_start + num_seconds

#             else:
#                 AS_end = AS.intervals[k, 1]
#                 AS_start = AS_end - num_seconds

#             arr_p[:, k], arr_c[:, k] = self.get_this_AS_food_drink_binning(F, D, AS_start, AS_end, ONSET=ONSET) 
            

#         return arr_p.mean(axis=1), arr_c.mean(axis=1)





#     def get_move_food_drink_profile(self, num_bins=180, num_seconds=900, move_sample=12, ntrials=20, ONSET=True, eps=0.01):
#         """ breakfast null
#         """

#         attributes = ['feedingSet', 'drinkingSet', 'locomotionSet', 'non_locomotionSet']
            
#         for attr in attributes:
#             self.load(attr)

#         M = self.locomotionSet.connect_gaps(eps=eps)
#         M_HB = self.non_locomotionSet.connect_gaps(eps=eps)
#         M_AS = M.union(M_HB)

#         F = self.feedingSet.connect_gaps(eps=eps)
#         D = self.drinkingSet.connect_gaps(eps=eps)

#         arr_p = np.zeros((ntrials, 2, move_sample, num_bins))   #f/d
#         arr_c = np.zeros((ntrials, 2, move_sample, num_bins))

#         for trial in xrange(ntrials):
            
#             subset_M_idx = np.random.permutation(M_AS.intervals.shape[0])[0: move_sample]   
            
#             k = 0
#             for move in M_AS.intervals[subset_M_idx]:   
#                 if ONSET:
#                     M_start = move[0]
#                     M_end = num_seconds + M_start
#                 else:
#                     M_end = move[1]
#                     M_start = M_end - num_seconds


#                 arr_p[trial, :, k], arr_c[trial, :, k] = self.get_this_AS_food_drink_binning(F, D, M_start, M_end, ONSET=ONSET)     
            
#                 k +=1

        
#         return arr_p.mean(axis=2), arr_c.mean(axis=2)









    ##### position density stuff


    # def get_homebase_stuff(self):

    #   nest = self.load('nest_rectangle')

    #   is_niche = False
        
    #   if (0, 0) in nest:
    #       is_niche = True

    #   # observed nest ETHEL: (ybins, xbins): (3, 7) top left. (1, 1) bottom right.  
    #   obs_ethel = (self.NLX, self.NLY)

    #   # # correct observations by ethel's remarks
    #   # 3:6 is not in the niche. My guess is, sometimes, the experimenter would assign 3:6 if the nest is in the corner of the cage & the niche. 
    #   # The more accurate location would be 3:5. Unfortunately, this might be true for other experiments as well. 
        
    #   # As for 2,7 & 2,6, as far as I remember, I have never recorded those coordinates for a standard HCM experiment (1-bottle). 
    #   # Maybe because half of the grid is covered by the niche. 
    #   # If you see 2, 7, it is more likely a typo error. It could be a 3,7 instead of 2,7. 
    #   # For 2,6, that will be 1,6. 
    #   # One way of checking if the designation is correct is by looking at the X,Y plotts (Matlab). 
    #   # The blue square you see on the figure is what the experimenter has assigned as the nest location. 
    #   # If in case the blue square has a different location from what the system has picked up, then the system will have the right coordinates.

    #   if (self.NLX, self.NLY) == (3, 6):
    #       obs_ethel = (3, 5)
    #       print "corrected by Ethel: %s to %s" %((self.NLX, self.NLY), (3, 5))
            
    #   elif (self.NLX, self.NLY) == (2, 7):
    #       obs_ethel = (3, 7)
    #       print "corrected by Ethel: %s to %s" %((self.NLX, self.NLY), (3, 7))
    #   elif (self.NLX, self.NLY) == (2, 6):
    #       obs_ethel = (1, 6)
    #       print "corrected by Ethel: %s to %s" %((self.NLX, self.NLY), (1, 6))

    #   # obs_ethel in (2, 4) coord
    #   # obs = self.map_obs_rectangle_to_cage(obs_ethel)  # returns list of tuples 

    #   # test correspondence in (2, 4)
    #   is_consistent_ethyl = self.test_homebase_locations(nest, obs_ethel)


    #   # printout
    #   # test

    #   string1 = ', same as Ethyl'
    #   if not is_consistent_ethyl:
    #       string1 = ', different than Ethyl: nest %s, obs %s' %(nest, obs_ethel)
    #       if self.ignored:
    #           string1 = ', different than Ethyl: nest %s, obs %s (this MD is ignored)' %(nest, obs_ethel)

    #   if nest[0] == (0, 0):
    #       print "..single HB in Niche" + string1
    #   else:
    #       if len(nest) == 1:
    #           print "..single HB off Niche" + string1
    #       else:
    #           print "..domino HB off Niche" + string1

    #   return nest, obs_ethel, is_consistent_ethyl, is_niche



    # def test_homebase_locations(self, rect, obs):
    #   """ converts observed homebase rectangle from (3, 7) cage 
    #       # (ybins, xbins): (3, 7) top left. (1, 1) bottom right. 
    #       upper left, niche: (3, 7) 
    #       lower right: (1, 1)
    #       into a (2, 4) cage discretization
    #   """
    #   a, b = obs

    #   # (2, 4) cells consistent with a (3, 7)
    #   # niche: according to ethel
    #   if a >= 2 and b == 7:
    #       consistent = [(0, 0)]

    #   # out of niche
    #   elif a == 3 and b == 6:
    #       consistent = [(1, 0)]
    #   elif a == 2 and b == 6:
    #       consistent =  [(0, 1)]  


    #   elif a == 1 and b >= 6:
    #       consistent = [(0, 1)]
    #   elif a == 1 and b == 5:
    #       consistent = [(1, 1)]
    #   elif a == 1 and b == 4:
    #       consistent =  [(1, 1), (2, 1)]
    #   elif a == 1 and b == 3:
    #       consistent =  [(2, 1)]
    #   elif a == 1 and b <= 2:
    #       consistent =  [(3, 1)]

    #   elif a == 2 and b == 5:
    #       consistent =  [(1, 0), (1, 1)]
    #   elif a == 2 and b == 4:
    #       print "!! Whoa mouse slept in the middle of the cage !!"
    #       consistent = [(1, 0), (1, 1), (2, 0), (2, 1)]
    #   elif a == 2 and b == 3:
    #       consistent =  [(2, 0), (2, 1)]
    #   elif a == 2 and b <= 2:
    #       consistent =  [(3, 0), (3, 1)]

    #   elif a == 3 and b == 5:
    #       consistent =  [(1, 0)]
    #   elif a == 3 and b == 4:
    #       consistent =  [(1, 0), (2, 0)]
    #   elif a == 3 and b == 3:
    #       consistent =  [(2, 0)]
    #   elif a == 3 and b <= 2:
    #       consistent =  [(3, 0)]
        
    #   # test
    #   if len(rect) == 1:
    #       if rect[0] in consistent:
    #           return True
    #   elif len(rect) == 2:
    #       if (rect[0] in consistent) or (rect[1] in consistent):
    #           return True

    #   return False






    # #### events

    # def get_events(self):
    #     """events descriptive statistics
    #     """

    #     AS = self.load('activeStateSet')

    #     F = self.load('feedingSet')
    #     W = self.load('drinkingSet')
    #     CT = self.load('CT')

    #     num_AS = AS.intervals.shape[0]
        
    #     num_F = F.intervals.shape[0]
    #     num_W = W.intervals.shape[0]
    #     num_M = CT.shape[0]

    #     return num_M, num_F, num_W, num_AS





    # ##### raw binary stuff



    # def calculate_active_states(self, eps=.01, IST=20.):
    #     """ist in minutes
    #     """
    #     startTime = time.clock()

    #     # LE = self.LE[1:,:].copy() #seems to always be a lick event at the beginning: chop it off
    #     # PE = self.PE[1:,:].copy() #seems to always be a photobeam event at the beginning: chop it off

    #     # LE[:,1] += LE[:,0]
    #     # PE[:,1] += PE[:,0]
        
    #     # # original trip on connecting ME events
    #     # I_CT_ = Intervals(zip(self.CT, self.CT + .0000001))
    #     # I_CT_connect = Intervals(I_CT_.intervals).copy().connect_gaps(eps=MTT).trim(eps=.000000101)   
    #     # I_CT_trim = I_CT_connect.complement() * I_CT_         # could be redundant
    #     # I_CT = I_CT_ - I_CT_trim                          # could be redundant
    #     # I_CT = Intervals(I_CT_.intervals).copy().connect_gaps(eps=.MTT)#.trim(eps=.000000101)     # this alone could be better
        
    #     # # or
    #     # delta_x = self.CX[1:]-self.CX[:-1]
    #     # delta_y = self.CY[1:]-self.CY[:-1]
    #     # delta_t = self.CT[1:]-self.CT[:-1]
    #     # dist = np.sqrt(delta_x**2 + delta_y**2)
    #     # # # trim movements shorter than dx
    #     # idx = (dist > MTT)
    #     # # or trim events that are farther than dt apart
    #     # idx = (delta_t > MTT)
    #     # I_CT = Intervals(zip(self.CT[idx], self.CT[idx] + .0000001))

    #     # # look into a window: quantities
    #     # idx = np.where((self.CT>25.6*3600) & (self.CT<25.8*3600))[0]
    #     # arr = self.CT[idx]                # select time in window
    #     # dt = arr[1:]-arr[:-1]         # time diff in secs
    #     # dist = np.sqrt(delta_x[idx]**2 + delta_y[T]**2)     # distance run in cm



    #     # nest. single or domino (list of tuples)
    #     nest_rectangle = self.designate_homebase()          # (ybins, xbins): (0, 0) top left. (3, 1) bottom right. 

    #     setattr(self, 'nest_rectangle', nest_rectangle)
        
    #     # from ethological definition of AS, movements at homebase are part of inactive state.
    #     # remove nest movements     
    #     idx_loco = self.remove_nest_movements(nest_rectangle)       # idx_loco: when not at nest

    #     setattr(self, 'C_idx_loco', idx_loco)

    #     idx_nonloco = -idx_loco         # when at nest



    #     print "designating active states.."
    #     # # from ethologic definition of AS, movements at homebase are part of inactive state.
    #     # # and must be removed 
        
    #     # use CT_loco with nest removed timestamps. just connect events at 2*minimum amount.
    #     CT_loco = self.CT[idx_loco]
    #     CT_nonloco = self.CT[idx_nonloco]

    #     # builds interval (HCM min resolution) wide out of timestamps
    #     I_CT_loco = plot_utils.timestamps_to_interval(CT_loco, eps=eps)
    #     I_CT_nonloco = plot_utils.timestamps_to_interval(CT_nonloco, eps=eps)
        
    #     # I_LE = Intervals(LE)        
    #     # I_PE = Intervals(PE)    

    #     tmp = I_LE + I_PE 
    #     I_events = I_CT_loco + tmp                               # pure events

    #     IAS = I_events.complement().trim(eps=IST*60.)       # apply IST
    #     # I_start_stop = Intervals([self.recordingStartTime, self.recordingEndTime])
    #     # IAS = I_events.complement().intersect(I_start_stop).trim(eps=IST*60.)
        

    #     setattr(self, 'activeStateSet', IAS.complement())
    #     setattr(self, 'drinkingSet', I_LE)
    #     setattr(self, 'feedingSet', I_PE)
    #     setattr(self, 'locomotionSet', I_CT_loco)
    #     setattr(self, 'non_locomotionSet', I_CT_nonloco)
    #     # setattr(self, 'recordingStartTimeEndTime', np.array([self.recordingStartTime, self.recordingEndTime],dtype=np.double)) #TICKET: probably wrong
        
    #     stopTime = time.clock()

    #     print "active state designation took %fs"%(stopTime-startTime)
        
    #     # # do some checks on feed and drink:
    #     self.check_food_drink_device_errors()

    #     return IAS.complement()





    # def check_food_drink_device_errors(self):
    #   """check for some elementary device errors
    #   """
    #   startTime = time.clock()
        
    #   c = 0
    #   # # feeding empty
    #   if self.feedingSet.is_empty():
    #       ignore = (self.mouseNumber, self.dayNumber)
    #       self.log_ignored_mouse('%d, %d' %(ignore[0], ignore[1]))  
    #       c += 1      
    #   # # extra feed: max feeding duration is more than 30 minutes
    #   elif (self.feedingSet.intervals[:, 1] - self.feedingSet.intervals[:,0]).max() > 30*60.: 
    #       ignore = (self.mouseNumber, self.dayNumber)
    #       self.log_ignored_mouse('%d, %d' %(ignore[0], ignore[1]))    
    #       c += 1  
        
    #   # # # photobeam error: no feeding for > 12hrs
    #   else: 
    #       feed_comp_set = self.feedingSet.complement().intersect(Intervals(self.recordingStartTimeEndTime))   # intersect with recording time (hrs after midnight)
    #       delta_t = feed_comp_set.intervals[:, 1] - feed_comp_set.intervals[:, 0]
    #       if delta_t.max() > 12*3600.:                                          
    #           ignore = (self.mouseNumber, self.dayNumber)
    #           self.log_ignored_mouse('%d, %d' %(ignore[0], ignore[1]))    

    #           c += 1  
                
    #   # # drinking empty
    #   if self.drinkingSet.is_empty():
    #       ignore = (self.mouseNumber, self.dayNumber)
    #       self.log_ignored_mouse('%d, %d' %(ignore[0], ignore[1]))        
    #       c += 1  

    #   # # extra drink: max drinking duration is more than 15 mins
    #   elif (self.drinkingSet.intervals[:, 1] - self.drinkingSet.intervals[:,0]).max() > 15*60.:       
    #       ignore = (self.mouseNumber, self.dayNumber)
    #       self.log_ignored_mouse('%d, %d' %(ignore[0], ignore[1]))        
    #       c += 1  

    #   # # lick error: no drinking for > 12hrs
    #   else: 
    #       drink_comp_set = self.drinkingSet.complement().intersect(Intervals(self.recordingStartTimeEndTime))   # intersect with recording time (hrs after midnight)
    #       delta_t = drink_comp_set.intervals[:, 1] - drink_comp_set.intervals[:, 0]
    #       if delta_t.max() > 12*3600.:                                          
    #           ignore = (self.mouseNumber, self.dayNumber)
    #           self.log_ignored_mouse('%d, %d' %(ignore[0], ignore[1]))        
    #           c += 1  

    #   stopTime = time.clock()
        
    #   print "found %d device errors check, took %fs"%(c, stopTime-startTime)    











# safetycopy

            # D_cell = (3, 0)
            # if act_type == 'W':
            #   D_cell = (3, 1)
        
            # tl, tr, bl, br = self.map_xbins_ybins_to_cage(rectangle=D_cell, xbins=xbins, ybins=ybins)

            # # print "Mouse at device location in original coordinates top_left, top_right, bot_left, bot_right: "
            # # print tl, tr, bl, br
            # # # nest: (0, 0)(-16.25, 43.0) (-6.25, 43.0) (-16.25, 32.5) (-6.25, 32.5)
            
            # is_at_device = np.zeros(num_movements, dtype=bool)
            
            # if act_type == 'F':
            #   less_than_x = tr[0]
            #   less_than_y = tl[1]

            #   for t in xrange(num_movements):

            #       if CX[t] < less_than_x and CY[t] < less_than_y:
                        
            #           is_at_device[t] = True

            
            # elif act_type == 'W':
            #   more_than_x = tl[0]
            #   less_than_y = tl[1]

            #   for t in xrange(num_movements):

            #       if CX[t] > more_than_x and CY[t] < less_than_y:
                        
            #           is_at_device[t] = True


            # is_at_device[0] = False       # get rid of problems
            # is_at_device[-1] = False

            # setattr(self, 'is_at_%s' %act_type, is_at_device)





# kind of old




# def get_feed_drink_coefficients(self):

#   attributes = ['feedingSet', 'drinkingSet']

#   for attr in attributes:
#       if not hasattr(self, attr):
#           self.load(attr)

#   # feed an drink
#   feedingSet = self.feedingSet 
#   drinkingSet = self.drinkingSet 

#   fc = self.chow_eaten_grams / feedingSet.measure() * 1000.       # feeding coefficient [mg/s]
#   lc = self.water_drunk_grams / drinkingSet.measure() * 1000.     # drinking coefficient [mg/s]
    
#   return fc, lc


# def get_events_durations(self):
#   """ some connecting eps for time budgets.
#       used by eps_tb_plot.py only
#   """
    
#   AS = self.load('activeStateSet')    
#   IS = self.load('inactiveStateSet')

#   D = self.load('drinkingSet')
#   F = self.load('feedingSet')
#   L = self.load('locomotionSet')
#   # # add non_locomotion in AS only. this should eat up from the red NonLoco (old for OTHER) slice.
#   NL = self.load('non_locomotionSet')
#   TL = L.union(NL)
#   # NL_AS = NL.intersect(AS)
#   # NL_IS = NL.intersect(IS)


#   # durations
#   f_durs = (F.intervals[:, 1]-F.intervals[:, 0])      # F and D events are real intervals
#   d_durs = (D.intervals[:, 1]-D.intervals[:, 0])
#   L_durs = (L.intervals[:,1]-L.intervals[:,0])
#   NL_durs = (NL.intervals[:,1]-NL.intervals[:,0])
#   TL_durs = (TL.intervals[:,1]-TL.intervals[:,0])
#   # L_durs = (L.intervals[1:, 0]-L.intervals[:-1, 0])  # most we can ask is inter_event duration. L intervals is fixed (0.02s blip). 
#   # NL_durs = (NL.intervals[1:, 0]-NL.intervals[:-1, 0])
#   # TL_durs = (TL.intervals[1:, 0]-TL.intervals[:-1, 0])
    
#   return f_durs, d_durs, L_durs, NL_durs, TL_durs


        
            

#   def is_interval_in_DC(self, interval):
#       """ returns:
#           0: lightCycle
#           1: darkCycle
#           2: starts in LC, ends in DC
#           3: starts in DC, ends in LC
#           where event is an array (start_time, endtime)
#           DC_ and LC_ are Intervals
#       """

#       start = interval[0]
#       end = interval[1]
#       event_interval = Intervals([start, end])

#       if not hasattr(self, 'recordingStartTimeEndTime'):
#           self.load('recordingStartTimeEndTime')
        
#       CT12 = 19.0 * 3600.
#       CT24 = 31.0 * 3600.
#       darkCycle = Intervals([CT12, CT24])
#       lightCycle_ = Intervals(np.array(([10.0 * 3600., CT12], [CT24, 40.0 * 3600.])))     # make it large enough
#       lightCycle = lightCycle_.intersect(Intervals(self.recordingStartTimeEndTime))

#       isLight = not event_interval.intersect(lightCycle).is_empty()
#       isDark = not event_interval.intersect(darkCycle).is_empty()
        
#       # events spanning DC and LC 
#       if isLight and isDark:
            
#           meas_lc = event_interval.intersect(lightCycle).measure() 
#           meas_dc = event_interval.intersect(darkCycle).measure()
            
#           dc_to_lc = meas_dc / meas_lc

#           if start < CT12:
#               return 2
#           else: 
#               return 3

#       return isDark



#   def get_active_states_DC_LC_signature(self):
#       """ returns array with a number code:
#           0: lightCycle
#           1: darkCycle
#           2: starts in LC, ends in DC
#           3: starts in DC, ends in LC
#           4: starts in LC, ends in DC, and this is the only DC that day 
#           5: starts in LC, ends in LC, spanning all DC        
#           for AS that start in LC, ends in DC or LC, but has no AS in DC a "5" is given
#       """
#       if not hasattr(self, 'activeStateSet'):
#           self.load('activeStateSet')

#       CT12 = 19.0 * 3600.
#       CT24 = 31.0 * 3600.
#       active_states = self.activeStateSet
#       num_AS = active_states.intervals.shape[0]
#       arr = np.zeros(num_AS)

#       for k, AS in enumerate(active_states):
#           arr[k] = self.is_interval_in_DC(interval=AS)

#       # test for too long AS in LC
#       # typical cases: [(6205.0, 11.0), (7107.0, 7.0), (8107.0, 5.0), (8107.0, 13.0), (5411.0, 15.0)]
#       # whose arr[k] look like
#       # [ 0.  2.]
#       # [ 0.  0.  0.  0.  2.  0.  0.  0.  0.]
#       # [ 0.  0.  0.  0.  0.  2.  0.  0.  0.  0.  0.]
#       # [ 0.  0.  0.  0.  0.  2.  0.  0.  0.  0.  0.  0.  0.]
#       # [ 0.  0.  0.  2.  0.  0.]
#       # mark with 5
#       if not (arr==1).any():
#           idx = np.where(arr==2.)[0][0]
#           end_AS = active_states.intervals[idx][1]
#           arr[idx] = 4        
#           if end_AS > CT24:
#               arr[idx] = 5            
            
#       return arr#, arr.shape[0]




    # # # old
    # def log_ignored_mouse(self, string, sub_dir=''):
    #   f=open(self.experiment.binary_dir + sub_dir + 'log_ignored_mousedays.txt','a') #open for appending
    #   f.write(string+'\n')
    #   f.close()




    # def get_time_interval_at_nest(self):
    #   """returns interval with consecutive non_loco events connected,
    #       unless broken by a loco event. used by rasters
    #   """

    #   print "computing time at nest location.."

    #   # get CT breakdown in _loco and _nonloco
    #   CT = self.CT
    #   idx_loco = self.C_idx_loco
    #   idx_nonloco = -idx_loco

    #   CT_loco = CT[idx_loco]
    #   CT_nonloco = CT[idx_nonloco]
    #   # CT_loco = self.CT_loco
    #   # CT_nonloco = self.CT_nonloco
        
    #   # connect nonloco. get array of connected non_loco
    #   max_time = min(37*3600., CT_nonloco[-1])

    #   arr = np.zeros((1, 2))
    #   idx_nl = 0
    #   a = 0
    #   while a < CT_loco[-1]:
    #       # take non_loco
    #       a = CT_nonloco[idx_nl]

    #       # take first loco > last non_loco
    #       idx_l = np.argmax(CT_loco > a)
    #       b = CT_loco[idx_l]
    #       # print idx_nl, idx_l
    #       arr = np.vstack((arr, np.array((a, b))))
            
    #       # jump to next non_loco
    #       idx_nl = np.argmax(CT_nonloco > b)
    #       print a, b, max_time, a > max_time

    #   arr = np.vstack((arr, np.array((a, max_time))))

    #   return Intervals(arr)       # arr[1:]



