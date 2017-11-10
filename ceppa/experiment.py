import numpy as np
import time
import os

from ceppa.util.darren import register_groups
from ceppa.util.exp_methods import experiment_variables, plot_settings
from ceppa.util import my_utils

"""
G.Onnis, 01.2017
    updated: 06.2017

Tecott Lab UCSF
"""


class Experiment(object): 
    
    def __init__(self, name='', IST=20., FBT=30., WBT=30., MBVT=1., MBDT=5., 
            MBTT=.2, IGNORE_MD=False, FULLNAME=True, BIN_SHIFT=False, 
            use_days='acclimated'):
        
        self.name = name 
        self.IST = IST * 60.    # sec, hyper_parameter     
        # ingestion bouts
        self.FBT = FBT*1.        # sec, hyper_parameter        
        self.WBT = WBT*1.        # same as FBT, for the moment
        # move bouts
        self.MBVT = MBVT*1.        # cm/s. velocity threshold.
        self.MBDT = MBDT*1.        # cm. distance threshold
        self.MBTT = MBTT*1.       # s, connect bouts < MBTT apart
        
        self.IGNORE_MD = IGNORE_MD
        self.FULLNAME = FULLNAME
        self.use_days = use_days
        self.BIN_SHIFT = BIN_SHIFT
        
        self.add_directories()
        experiment_variables.add_variables_to_experiment(self)
        plot_settings.get_settings(self)


    def __str__(self):
        string = self.short_name + '\n' + self.hypar_text
        return string


    def add_directories(self):
        # machine = os.uname()[1] 
        # if machine == "ucsf2-71-19":        # if Beast
        #     self.exp_dir = '/media/BeastHD_/Experiments/SS_Data_051905_FV/'

        # binaries
        self.binary_dir = self.exp_dir + 'binary/'
        self.HCM_data_dir = self.binary_dir + 'HCM_data/'
        self.derived_dir = self.binary_dir + 'derived/'
        self.events_dir = self.derived_dir + 'events/'
        self.active_states_dir = self.derived_dir + \
                                'active_states/IST_%1.2fm/' %(self.IST / 60.)
        self.bouts_dir = self.derived_dir + 'bouts/'
        self.F_bouts_dir = self.bouts_dir + 'FBT_%1.1fs/' %self.FBT       
        self.W_bouts_dir = self.bouts_dir + 'WBT_%1.1fs/' %self.WBT       
        self.M_bouts_dir = self.bouts_dir \
                            + 'MBVT_%1.1fcms/MBDT_%1.1fcm/' %(self.MBVT, self.MBDT)    
        
        self.features_dir = self.derived_dir + 'features/'

        self.breakfast_dir = self.derived_dir + 'breakfast/'
        self.within_AS_dir = self.derived_dir + 'within_AS/'
        self.time_budgets_dir = self.derived_dir + 'time_budgets/'

        # figures
        self.hypar_str = 'IST%1.2fm_FBT%1.1fs_WBT%1.1fs_MBVT%1.1fcms_MBDT%1.1fcm' %(
            self.IST/60., self.FBT, self.WBT, self.MBVT, self.MBDT)
        self.hypar_text = self.hypar_str.replace('_', ', ').replace('T', 'T=')
        self.hypar_caption = self.hypar_text.replace(', ', '\n')

        self.figures_dir = self.exp_dir + 'figures/%s/' %self.hypar_str
        # self.figures_dir_ = self.exp_dir + 'figures/%s/' %self.hypar_str
        
        if not self.IGNORE_MD:
            self.figures_dir = self.exp_dir + 'figures/%s/_DATA_REVIEW/' %self.hypar_str

        # make
        for dirname in [self.HCM_data_dir, self.derived_dir, self.figures_dir]:
            if not os.path.isdir(dirname): os.makedirs(dirname)


    def flag_ignored_mousedays(self):
        """ returns a list of flagged mousedays based on devices' errors
        """
        dirname_in = self.binary_dir + 'HCM_data/qc/flagged/'
        dirname_in2 = self.binary_dir + 'HCM_data/qc/flagged_msgs/'
        flagged = []
        reason = []
        for strain in xrange(20):           # wide enough
            for mouse in xrange(20):
                    for day in xrange(40):                
                        id_string = "group%d_individual%d_day%d.npy" %(strain, mouse, day)
                        fname = dirname_in + id_string
                        fname2 = dirname_in2 + id_string
                        try:
                            mouseNumber, dayNumber, flag = np.load(fname)
                            if flag:
                                act, msgs = np.load(fname2)[0]
                                assert (len(msgs) > 0)
                                flagged.append((mouseNumber, dayNumber))
                                reason.append((act, msgs))
                        except IOError:
                            pass
        self.flagged = flagged
        self.reason = reason 

        return flagged, reason


    def assertProperInitialization(self):
        #assert hasattr(self, 'group_name_to_mouse_number_list_dictionary'), "This experiment does not have group_name_to_mouse_number_list_dictionary"
        print "binary data from:", self.binary_dir
        print "TIME_BINS_SHIFT: %s" %self.BIN_SHIFT
        print "--"*10 
        print "Hyper-parameters:\n-Active State:\nIST=%1.2fm" %(self.IST /60.)
        print "-Bouts:\nFBT=%1.1fs\nWBT=%1.1fs\nMBVT=%1.1fcm/s\nMBDT=%1.1fcm" \
                    %(self.FBT, self.WBT, self.MBVT, self.MBDT)
        print "--"*10        
        print "The experiment called %s has been initialized"%(self.name)
        print "--"*10
        print ""
        # assert not self.name=='', 'This experiment does not have a name'
        # assert self.mouseDayFromAbstractIndices
        # self.checkSignatureOfMouseDayFromAbstractIndices()


    def get_exp_info(self):
        print "Experiment: %s" %self.short_name
        self.count_mice()
        self.count_mousedays()

        c = 0
        flagged, reason = self.flag_ignored_mousedays()
        for group in self.groups: 
            print '\ngroup %d: %s' %(group.number, group.name)  
            mice_ok, mice_no = group.count_mice()
            print 'individuals: %d' %(len(mice_ok) + len(mice_no))
            print 'valid: %d\nMice: %s' %(len(mice_ok), mice_ok)        
            print 'ignored: %d\nMice: %s\n' %(len(mice_no), mice_no)        
            for mouse in group.individuals:
                if not mouse.ignored:
                    days_ok, days_no = mouse.count_mousedays()
                    if len(days_no) > 0:
                        print "M%d, %d ignored mouseday/s: %s" %(
                                mouse.mouseNumber, len(days_no), days_no)
                    for MD in mouse.mouse_days:
                        if MD.dayNumber in self.daysToUse: 
                            if MD.ignored:
                                print flagged[c], reason[c]
                                c +=1


    def count_mice(self):
        cnt_tot, cnt_ok, cnt_ignored = 0, 0, 0
        for group in self.groups:             
            for mouse in group.individuals:
                if not mouse.ignored:
                    cnt_ok +=1
                else:
                    cnt_ignored += 1
                cnt_tot += 1

        self.num_mice = cnt_tot
        self.num_mice_ok = cnt_ok
        self.num_mice_ignored = cnt_ignored

        return cnt_tot, cnt_ok


    def count_mousedays(self, days=None):
        days_to_use = self.daysToUse if days is None else days
        
        cnt_tot, cnt_ok, cnt_ignored = 0, 0, 0
        for group in self.groups:             
            for mouse in group.individuals:
                # if not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in days_to_use: 
                        if not MD.ignored:
                            cnt_ok +=1
                        else: 
                            cnt_ignored +=1
                        cnt_tot += 1

        if days is None:
            self.num_mousedays = cnt_tot
            self.num_md_ok = cnt_ok
            self.num_md_ignored = cnt_ignored
        
        return cnt_tot, cnt_ok


    def get_max_AS(self, days=None):
        counts = self.count_AS()
        max_AS = []
        for group in self.groups:           
            maxs = []
            for mouse in group.individuals:
                if not mouse.ignored:
                    maxs.extend([max(counts[group.number][mouse.mouseNumber])])
            max_AS.extend([max(maxs)])
        return max_AS


    def count_AS(self, days=None):
        days_to_use = self.daysToUse if days is None else days
        counts = dict()
        for group in self.groups:
            counts[group.number] = {}             
            for mouse in group.individuals:
                if not mouse.ignored:
                    counts[group.number][mouse.mouseNumber] = []
                    for MD in mouse.mouse_days:
                        if MD.dayNumber in days_to_use: 
                            if not MD.ignored:
                                AS = MD.load('AS_timeSet')
                                AS_clean = my_utils.wipe_data_outside_CT6_30(AS)
                                counts[group.number][mouse.mouseNumber].extend([AS_clean.shape[0]]) 

        return counts



    def get_mouseNumber_to_group_dict(self):
        d = {}
        for group in self.groups:
            for mouse in group.individuals:
                d[mouse.mouseNumber] = group.number
        return d

    def get_groupNumber_to_mouseNumber_dict(self, groupNumber):
        d = {}
        for group in self.groups:
            d[group.number] = [m.mouseNumber for m in group.individuals]
        return d


    def get_groupNumber_from_mouseNumber(self, mouseNumber):
        labels_dict = self.get_mouseNumber_to_group_dict()
        return labels_dict[mouseNumber]


    def get_mouseNumbers_from_groupNumber(self, groupNumber):
        labels_dict = self.get_groupNumber_to_mouseNumber_dict(groupNumber)
        return labels_dict[groupNumber]


    def get_group_object(self, groupNumber):
        for group in self.groups:
            if group.number == groupNumber:
                return group


    def get_mouse_object(self, mouseNumber=2101):
        for group in self.groups:
            for mouse in group.individuals:
                if mouse.mouseNumber == mouseNumber:
                    return mouse

    
    def get_mouseday_object(self, mouseNumber=2101, dayNumber=None):
        for group in self.groups:
            for mouse in group.individuals:
                if mouse.mouseNumber == mouseNumber:
                    # if not mouse.ignored:
                    for MD in mouse.mouse_days:
                        # if not MD.ignored:
                        if MD.dayNumber == dayNumber:
                            return MD


    # load
    def load_features_vectors(self, features, level='mouseday', bin_type='12bins', 
            err_type='sd', days=None):
        """
        """
        num_bins = bin_type.strip('cycles').strip('bins').strip('AS')
        # int(bin_type[:2]) if bin_type.endswith('bins') else 3

        print "loading features:\n", features

        arr_list = []
        for f, feature in enumerate(features):  
            data, labels = self.generate_feature_vectors(
                                feature, level, bin_type, err_type, 
                                days)
            arr_list.append(data)

        return np.array(arr_list), labels


    # def load_feature_vectors_(self, features, bin_type='12bins', level='strain', 
    #         group_avg_type='over_mds'):
    #     """
    #     """
    #     num_bins = 12 if bin_type.endswith('bins') else 3
    #     print "loading features:\n", features
    #     s_data = np.zeros([len(features), self.num_strains, num_bins])
    #     m_data =  np.zeros([len(features), self.num_mice_ok, num_bins])
    #     md_data =  np.zeros([len(features), self.num_md_ok, num_bins])
    #     for f, feat in enumerate(features):
    #         s, sl, m, ml, md, mdl = self.generate_feature_vectors(feat, bin_type, GET_AVGS=True, group_avg_type=group_avg_type)
    #         s_data[f], s_labels, m_data[f], m_labels, md_data[f], md_labels = s[0], sl, m[0], ml, md, mdl   # 0:mean

    #     if level == 'strain':
    #         return s_data, s_labels
    #     elif level == 'mouse':
    #         return m_data, m_labels
    #     elif level == 'mouseday':
    #         return md_data, md_labels

    #     return s_data, s_labels, m_data, m_labels, md_data, md_labels



    def get_HCM_maintenance_time(self):
        maintenance_time = np.zeros((1, 2))
        labels = np.zeros((1, 3))
        cnt = 0
        for group in self.groups:
            for mouse in group.individuals:
                md_time, md_labels = mouse.get_maintenance_time()
                maintenance_time = np.vstack([maintenance_time, md_time])
                labels = np.vstack([labels, md_labels])
        return maintenance_time[1:], labels[1:]


    def get_HCM_recording_time(self):
        recording_time = np.zeros((self.num_mousedays, 2))
        labels = np.zeros((self.num_mousedays, 3), dtype=int)
        cnt = 0
        for group in self.groups:
            for mouse in group.individuals:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in self.daysToUse:
                        recording_time[cnt] = MD.load('recording_start_stop_time')
                        labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                        cnt += 1
        
        return recording_time, labels
    

    def get_data_labels(self):
        """ returns labels (strain, mouse, day) for all legit mousedays
        """
        mouse_labels = np.zeros([self.num_mice_ok, 2], dtype=int)
        md_labels = np.zeros([self.num_md_ok, 3], dtype=int)
        print "loading data labels.."
        cnt = 0
        cnt_mice = 0
        for group in self.groups:    
            for mouse in group.individuals:
                if not mouse.ignored:
                    for MD in mouse.mouse_days:
                        if not MD.ignored:
                            if MD.dayNumber in self.daysToUse:
                                md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                                cnt +=1
                    
                    mouse_labels[cnt_mice] = group.number, mouse.mouseNumber
                    cnt_mice +=1

        return mouse_labels, md_labels


    # def test_features(experiment, bin_type='24HDCLC', level='mouseday', err_type='stdev'):   

    #     E = experiment
    #     num_strains = len(E.strain_names)

    #     # load data, all days    
    #     avgs, errs, labels = E.generate_feature_panel_data(bin_type, level, err_type)

    #     # # 24 hours
    #     # test 1: ASP-TF-FASInt
    #     fidx = [0, 3, 6]
    #     ASP, TF, FASInt = avgs[fidx, :, 0]


    # def get_max_number_mice_per_group(self):
    #     num = []
    #     for group in self.groups:   
    #         cnt = 0          
    #         for mouse in group.individuals:
    #             if not mouse.ignored:
    #                 cnt +=1
    #         num.append(cnt)
    #     return np.array(num).max()

    # def get_max_number_mds_per_group(self):
    #     num = []
    #     for group in self.groups:   
    #         cnt = 0          
    #         for mouse in group.individuals:
    #             if not mouse.ignored:
    #                 for MD in mouse.mouse_days:
    #                     if MD.dayNumber in self.daysToUse:
    #                         cnt +=1
    #         num.append(cnt)
    #     return np.array(num).max()



    # generate 
    def generate_binaries(self, mouseNumber=None, dayNumber=None):
        cstart = time.clock()
        print "Exp: %s, %s, from raw HCM data." %(
                self.short_name, self.generate_binaries.__name__) + \
                " IST, and other hyper-parameters play no role here.." 
        if mouseNumber is None:
            for group in self.groups:    
                for mouse in group.individuals:
                    for MD in mouse.mouse_days: 
                        if MD.dayNumber in self.daysToUse:              
                            MD.generate_binaries()
                            
        else:           
            mouse = self.get_mouse_object(mouseNumber)
            MD = mouse.mouse_days[dayNumber-1]  # check dayNumber
            MD.generate_binaries()
                   
        cstop = time.clock()
        if mouseNumber is None:
            print "binary output saved to:\n%s" %self.HCM_data_dir
            print "..took: %1.2f minutes"%((cstop-cstart)/60.)
            

    def generate_bouts(self, mouseNumber=None, dayNumber=None):
        """
        """
        cstart = time.clock()
        if mouseNumber is None:
            for group in self.groups:    
                for mouse in group.individuals:
                    if not mouse.ignored:
                        for MD in mouse.mouse_days:
                            if MD.dayNumber in self.daysToUse:
                                if not MD.ignored:
                                    MD.generate_bouts()
        else:
            mouse = self.get_mouse_object(mouseNumber)
            if not mouse.ignored:
                MD = mouse.mouse_days[dayNumber-1]
                if not MD.ignored:
                    MD.generate_bouts()
        cstop = time.clock()

        if mouseNumber is None:
            print "binary output saved to: %s/bouts/" %self.derived_dir
            print "..took: %1.2f minutes"%((cstop-cstart)/60.)
            

    def generate_active_states(self, mouseNumber=None, dayNumber=None):
        cstart = time.clock() 
        if mouseNumber is None:
            cnt = 0
            for group in self.groups:    
                for mouse in group.individuals:
                    for MD in mouse.mouse_days:
                        if MD.dayNumber in self.daysToUse:
                            MD.generate_active_states()
                            my_utils.print_progress(cnt, self.num_md_ok)
                            cnt += 1
        else:
            mouse = self.get_mouse_object(mouseNumber)
            MD = mouse.mouse_days[dayNumber-1]
            MD.generate_active_states()
                    
        cstop = time.clock()
        if mouseNumber is None:
            print "binary output saved to: %s" %self.active_states_dir
            print "..took: %1.2f minutes"%((cstop-cstart)/60.)
            

    def generate_homebase_data(self):
        rects_HB, obs_rects = [], []
        for group in self.groups:    
            for mouse in group.individuals:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in self.daysToUse:
                        rect_HB, obs_rect = [MD.load(var) for var in ['rect_HB', 'obs_HB']] 
                        rects_HB.append(rect_HB)
                        obs_rects.append(obs_rect)
        return rects_HB, obs_rects


    def check_position_bin_times(self, xbins=12, ybins=24, tbin_type=None):
        text = 'cycles' if tbin_type is None else tbin_type
        print "Exp: %s, %s, %s, days: %s" %(self.short_name, 
                    self.check_position_bin_times.__name__, text, self.daysToUse)

        for group in self.groups:    
            for mouse in group.individuals:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in self.daysToUse:
                        MD.check_position_bin_times(xbins, ybins, tbin_type)

        print "\nSUCCESS\n"


    def generate_position_density(self, cycle='24H', tbin_type=None, level='mouseday', 
            xbins=12, ybins=24, days=None, err_type='sd', GENERATE=False, VERBOSE=False):
        """ returns position density data 
        """
        cstart = time.clock()

        if days is None:
            days_to_use = self.daysToUse 
            num_md = self.num_mousedays
        else: 
            days_to_use = days 
            num_md, _ = self.count_mousedays(days=days_to_use)

        if tbin_type is not None:
            num_tbins = my_utils.get_CT_bins(tbin_type=tbin_type.strip('AS')).shape[0]
            md_data = np.zeros((num_md, num_tbins, ybins, xbins))
        else:
            md_data = np.zeros((num_md, ybins, xbins)) 

        text = my_utils.get_text(cycle, tbin_type)
        
        print "Exp: %s, %s, tbin_type: %s, level:%s, xbins=%d, ybins=%d, err_type: %s, %s days" %(
                self.short_name, self.generate_position_density.__name__, 
                text, level, xbins, ybins, err_type, days_to_use)
        
        md_labels = np.zeros((num_md, 3), dtype=int)
        cnt = 0
        for group in self.groups:    
            for mouse in group.individuals:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in days_to_use:

                        if MD.ignored:
                            md_data[cnt] = np.nan

                        else:
                            bin_times = MD.generate_position_bin_times(
                                            cycle, tbin_type, xbins, ybins, GENERATE)
                            if tbin_type is not None:
                                b = 0
                                for btimes in bin_times:
                                    if btimes.sum() >= 0:
                                        md_data[cnt, b] = btimes / btimes.sum()      
                                    b +=1
                            else:
                                if bin_times.sum() >= 0:
                                    md_data[cnt] = bin_times / bin_times.sum()
                                      
                        md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber

                        # if GENERATE and not VERBOSE:
                        #     my_utils.print_progress(cnt, self.num_md_ok)
                        
                        cnt +=1

        cstop = time.clock()
        
        if GENERATE:
            if not VERBOSE: 
                print

            dirname = self.derived_dir + \
                        'position_data/xbins%d_ybins%d/%s/bin_times/' %(xbins, ybins, text)   # copied from: MD.generate_position_bin_times
            print "binary output saved to: %s" %dirname 
            print "..took %1.2f minutes"%((cstop-cstart)/60.)

        E = self
        data, labels = my_utils.get_2d_averages_errors(
                            E, md_data, md_labels, tbin_type, level, err_type)
        
        return data, labels


    def get_bodyweights(self):
        # get bodyweight for the dataset
        print "--Exp: %s, %s, getting bodyweight -pre/-post/-gain " %(
                self.short_name, self.get_bodyweights.__name__, )

        bws, labels = [], []
        for group in self.groups:
            for mouse in group.individuals:
                if mouse.ignored:
                    bws.append([np.nan, np.nan, np.nan])
                else:
                    bw_start, bw_end = mouse.body_weight_start_of_experiment_grams, mouse.body_weight_end_of_experiment_grams
                    bws.append([bw_start, bw_end, bw_end-bw_start])       # bw_pre, bw_post, bw_gain = bw_pre - bw_post

                labels.append([mouse.groupNumber, mouse.mouseNumber])

        return np.array(bws), np.array(labels)


    def generate_feature_vectors(self, feature='ASP', level='mouseday', bin_type='12bins',  
            err_type='sd', days=None, group_avg_type='over_mds', GENERATE=False, 
            VERBOSE=False):
        """ 
        """ 

        cstart = time.clock() 
        
        num_bins = int(bin_type.strip('bins').strip('AS').strip('cycles'))
        
        # days_to_use = self.daysToUse if days is None else days
        if days is None:
            days_to_use = self.daysToUse 
            num_md = self.num_mousedays
        else: 
            days_to_use = days 
            num_md, _ = self.count_mousedays(days=days_to_use)

        print "--Exp: %s, %s\n%s, %s, bin_type: %s, err_type: %s,\ndays: %s, BIN_SHIFT: %s" %(
                self.short_name, self.generate_feature_vectors.__name__, 
                feature, level, bin_type, err_type, 
                days_to_use, self.BIN_SHIFT)

        md_data = np.zeros((num_md, num_bins))
        md_labels = np.zeros((num_md, 3), dtype=int)
        
        cnt = 0
        for group in self.groups:  
            for mouse in group.individuals:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in days_to_use:

                        if MD.ignored:
                            # md_data.append(np.nan)
                            md_data[cnt] = np.nan
                        
                        else:
                            # md_data.append(MD.generate_feature_vector(feature, bin_type, GENERATE, VERBOSE))
                            md_data[cnt] = MD.generate_feature_vector(
                                                feature, bin_type, GENERATE, VERBOSE)

                        # md_labels.append((MD.groupNumber, MD.mouseNumber, MD.dayNumber))
                        md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber

                        if GENERATE and not VERBOSE:
                            my_utils.print_progress(cnt, self.num_md_ok)

                        cnt +=1

        
        cstop = time.clock()
        
        if GENERATE:
            if not VERBOSE: 
                print
            string = '_shifted%+02dm' %(self.binTimeShift/60) if self.BIN_SHIFT else ''
            dirname = self.features_dir + 'vectors_CT/%s/%s%s/' %(feature, bin_type, string)
            print "binary output saved to: %s" %dirname 
            print "..took %1.2f minutes"%((cstop-cstart)/60.)

        E = self
        data, labels = my_utils.get_1d_averages_errors(
                            E, md_data, md_labels, level, err_type, group_avg_type)
        
        return data, labels      


    def generate_feature_vectors_expdays(self, features, level='group', bin_type='3cycles', 
            err_type='sd'):
        """ 
        """ 
        # load data  
        data, labels = self.load_features_vectors(
                                    features=features, 
                                    level='mouseday', 
                                    bin_type=bin_type)
        E = self
        if bin_type.endswith('cycles'):
            new_data = my_utils.get_1d_expdays_averages_errors_24H(
                                E, data, labels, level, err_type)
        
        elif bin_type.endswith('bins'):
            new_data = my_utils.get_1d_expdays_averages_errors_12bins(
                                E, data, labels, level, err_type)
        
        return new_data     


    def generate_feature_vectors_LC_DC_ratio_expdays(self, features, level='group', bin_type='3cycles', 
            err_type='sd'):
        """ 
        """ 
        # load data  
        data, labels = self.load_features_vectors(
                                    features=features, 
                                    level='mouseday', 
                                    bin_type=bin_type)
        E = self
        ratios = np.divide(data[:, :, 2, 0], data[:, :, 1, 0])
        new_ratios = my_utils.get_1d_expdays_averages_errors_DC_LC(
                            E, ratios, labels, level, err_type)
        
        return new_ratios     



    def generate_time_budgets(self, cycle='24H', level='mouseday',
            err_type='sd', AS=False, days=None, group_avg_type='over_mds', 
            GENERATE=False, VERBOSE=False):
        
        cstart = time.clock() 

        if days is None:
            days_to_use = self.daysToUse 
            num_md = self.num_mousedays
        else: 
            days_to_use = days 
            num_md, _ = self.count_mousedays(days=days_to_use)

        print "Exp: %s, %s, %s" %(
                self.short_name, self.generate_time_budgets.__name__, cycle)

        num_act = 5 if not AS else 4    #move, feed, drink, other_AS, inactive
        md_data = np.zeros((num_md, num_act))
        md_labels = np.zeros((num_md, 3), dtype=int)
        cnt = 0
        for group in self.groups:  
            for mouse in group.individuals:
                    for MD in mouse.mouse_days:
                        if MD.dayNumber in days_to_use:
                            
                            if MD.ignored:
                                md_data[cnt] = np.nan
                            
                            else:
                                md_data[cnt] = MD.generate_time_budgets(
                                                    cycle, num_act, GENERATE)
                                
                                md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                                
                                if not VERBOSE:
                                    my_utils.print_progress(cnt, self.num_md_ok)
                                else:
                                    print MD
                                cnt +=1


        cstop = time.clock()

        if GENERATE:
            if not VERBOSE: 
                print
            dirname = self.time_budgets_dir + '%s/' %cycle
            print "binary output saved to: %s" %dirname 
            print "..took %1.2f minutes"%((cstop-cstart)/60.)

        E = self
        data, labels = my_utils.get_1d_averages_errors(
                            E, md_data, md_labels, level, err_type)
        
        return data, labels


    def generate_breakfast_data(self, cycle='24H', level='mouseday', act='F', err_type='sd',
            ONSET=True, num_mins=15, tbin_size=5, days=None, group_avg_type='over_mds', 
            GENERATE=False, VERBOSE=False):
        
        cstart = time.clock() 

        if days is None:
            days_to_use = self.daysToUse 
            num_md = self.num_mousedays
        else: 
            days_to_use = days 
            num_md, _ = self.count_mousedays(days=days_to_use)

        print "Exp: %s, %s, %s, ONSET: %s, cycle: %s, GENERATE:%s" %(
            self.short_name, self.generate_breakfast_data.__name__, 
            act, ONSET, cycle, GENERATE)

        num_bins = int(num_mins * 60 / tbin_size)
        text = 'AS_onset' if ONSET else 'AS_offset'
        
        md_data = np.zeros((num_md, num_bins))
        md_labels = np.zeros((num_md, 3), dtype=int)

        cnt = 0
        for group in self.groups:  
            for mouse in group.individuals:
                    for MD in mouse.mouse_days:
                        if MD.dayNumber in days_to_use:

                            if MD.ignored:
                                md_data[cnt] = np.nan
                            
                            else:
                                md_data[cnt] = MD.generate_breakfast_data(
                                                cycle, act, ONSET, num_mins, 
                                                tbin_size, GENERATE)
                            md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                            if not VERBOSE:
                                my_utils.print_progress(cnt, self.num_md_ok)
                            else:
                                print MD
                            cnt +=1
        
        cstop = time.clock()
        
        if GENERATE:
            if not VERBOSE: 
                print
            dirname = self.breakfast_dir + \
                        '%s/%s/prob_%dmin_tbin%ds_%s/' %(
                            act, text, num_mins, tbin_size, cycle)
            print "binary output saved to: %s" %dirname 
            print "..took %1.2f minutes"%((cstop-cstart)/60.)
        
        E = self
        data, labels = my_utils.get_1d_averages_errors(
                            E, md_data, md_labels, level, err_type, group_avg_type)

        return data, labels




    def generate_ingestion_coeffs_and_totals(self, act='F'):
        
        varNames = ['FC', 'FT', 'FD'] if act =='F' else ['LC', 'WT', 'WD']
        
        print "Exp: %s, %s, act: %s" %(
                self.short_name, self.generate_ingestion_coeffs_and_totals.__name__, act)

        md_data = np.zeros((self.num_md_ok, 3))         # coeffs, tot amount, tot duration
        md_labels = np.zeros((self.num_md_ok, 3), dtype=int)
        cnt = 0
        for group in self.groups:  
            for mouse in group.individuals:
                if not mouse.ignored:
                    for MD in mouse.mouse_days:
                        if MD.dayNumber in self.daysToUse:
                            if not MD.ignored:
                                md_data[cnt] = [MD.load(x) for x in varNames]
                                md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                                cnt +=1
                        
        return md_data, md_labels



    # other stuff
    def get_days_to_use_text(self):
        days_to_use = np.array(self.daysToUse)
        idx = np.diff(days_to_use) > 1
        if idx.sum() == 0:
            if len(days_to_use) == 1:
                string = '\nD%d' %days_to_use[0]
            else:
                string = 'D%d->D%d' %(days_to_use[0], days_to_use[-1])
                
        else:
            idx_ = np.argmax(idx)
            if idx.sum() == 1:      # days_to_use has two day windows
                d0 = days_to_use[0] 
                d1 = days_to_use[idx_]
                d2 = days_to_use[idx_+1]
                d3 = days_to_use[-1]
                string = '\nD%d->D%d and D%d->D%d' %(d0, d1, d2, d3)
            elif idx.sum() == 2:    # more than two days windows
                stop

        return string

    # to review
    # def _check_bout_counts_in_bins(experiment, act, bin_type='12bins'):
    #     num_bins = 12 
    #     print "%s, %s, %dbins" %(_check_bout_counts_in_bins.__name__, act, num_bins)

    #     arr = np.zeros((experiment.num_md_ok, num_bins + 3))
    #     cnt = 0
    #     for group in experiment.groups:  
    #         for mouse in group.individuals:
    #             if not mouse.ignored:
    #                 for MD in mouse.mouse_days:
    #                     if MD.dayNumber in experiment.daysToUse:
    #                         if not MD.ignored:
    #                             arr[cnt, :3] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
    #                             arr[cnt, 3:] = MD._check_bout_counts_in_bins(act)
    #                             my_utils.print_progress(cnt, experiment.num_md_ok)
    #                             cnt +=1

    #     dirname = experiment.features_dir + 'vectors/_bout_counts_check/'
    #     import os
    #     if not os.path.isdir(dirname): os.makedirs(dirname)
    #     np.save(dirname + '%s_bout_counts_check' %act, arr)

    #     return arr

    # def generate_bout_feature_vectors_per_AS(experiment, feat='ASP', days=None, 
    #         GET_AVGS=True, group_avg_type='over_mds', GENERATE=False, VERBOSE=False):
    #     """ returns: 
    #         array with data for all legit mousedays
    #             arr: (num_mousedays, num_bins)
    #         mice and strain data 
    #             data[0]: avgs 
    #             data[1]: stdev
    #             data[2]: stderr
    #         labels
    #     """ 
    #     E = experiment
    #     cstart = time.clock() 

    #     print "%s, %s" %(generate_bout_feature_vectors_per_AS.__name__, feat)
        
    #     days_to_use = E.daysToUse if days is None else days
    #     _, num_md_ok = E.count_mousedays(days=days_to_use)

    #     md_data = []
    #     md_labels = np.zeros((num_md_ok, 3), dtype=int)
    #     cnt = 0
    #     for group in E.groups:  
    #         for mouse in group.individuals:
    #             if not mouse.ignored:
    #                 for MD in mouse.mouse_days:
    #                     if MD.dayNumber in days_to_use:
    #                         if not MD.ignored:
    #                             md_data.append(MD.generate_bout_feature_vector_per_AS(
    #                                                 feat, GENERATE, VERBOSE)
    #                                     )
    #                             md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
    #                             if GENERATE and not VERBOSE:
    #                                 my_utils.print_progress(cnt, E.num_md_ok)
    #                             cnt +=1

    #     cstop = time.clock()
        
    #     if GENERATE:
    #         if not VERBOSE: 
    #             print
    #         print "binary output saved to: %s" %E.features_dir 
    #         print "..took %1.2f minutes"%((cstop-cstart)/60.)
        
    #     if GET_AVGS:
    #         s_data, s_labels, m_data, m_labels = \
    #                 my_utils.get_1d_list_mouse_strain_averages(
    #                             E, md_data, md_labels, days, group_avg_type)
    #         return s_data, s_labels, m_data, m_labels, md_data, md_labels

    #     return md_data, md_labels


    # def generate_feature_vectors_expdays(experiment, feat, bin_type, days=None, 
    #         GET_AVGS=False, group_avg_type='over_mds'):
    #     """ relies on generate_feature_vector values
    #     """ 
    #     E = experiment
    #     num_bins = 12 if bin_type.endswith('bins') else 3
    #     print "%s, %s, %s" %(generate_feature_vectors_expdays.__name__, feat, bin_type)

    #     days_to_use = E.daysToUse if days is None else days
    #     num_md, _ = E.count_mousedays(days=days_to_use)

    #     md_data = np.zeros((num_md, num_bins))           
    #     md_labels = np.zeros((num_md, 3), dtype=int)
    #     cnt = 0
    #     for group in E.groups:  
    #         for mouse in group.individuals:
    #             for MD in mouse.mouse_days:
    #                 if MD.dayNumber in days_to_use:
    #                     if not MD.ignored:
    #                         md_data[cnt] = MD.generate_feature_vector(feat, bin_type)
    #                     else:
    #                         # print "ignored", MD
    #                         md_data[cnt] = np.nan

    #                     md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
    #                     cnt +=1

    #     if GET_AVGS:
    #         s_data, s_labels, m_data, m_labels = \
    #             my_utils.get_mouse_strain_averages_expdays(
    #                 E, md_data, md_labels, days, group_avg_type
    #                 )
    #         return s_data, s_labels, m_data, m_labels, md_data, md_labels

    #     return md_data, md_labels


    # def generate_feature_arrays(experiment, feat, GENERATE=False, VERBOSE=False):
    #     """ generate a list - 16 strains - of lists - all feature values during days
    #     """
    #     cstart = time.clock()
    #     print "%s, %s.." %(generate_feature_arrays.__name__, feat)

    #     cnt = 0
    #     all_arrays = []     
    #     for group in experiment.groups:
    #         arrs = [] 
    #         for mouse in group.individuals:
    #             if not mouse.ignored:
    #                 for MD in mouse.mouse_days:
    #                     if MD.dayNumber in experiment.daysToUse:
    #                         if not MD.ignored:                    
    #                             arr = MD.generate_feature_array(feat, GENERATE, VERBOSE) 
    #                             arrs.extend(arr)
    #                             if GENERATE and not VERBOSE:
    #                                 my_utils.print_progress(cnt, experiment.num_md_ok)
    #                             cnt +=1
    #         all_arrays.append(arrs)                  
        
    #     cstop = time.clock()
    #     if GENERATE:
    #         if not VERBOSE:
    #             print
    #         print "binary output saved to: %s" %experiment.features_dir+'arrays'
    #         print "..took %1.2f minutes"%((cstop-cstart)/60.)
    #     return all_arrays#, arr_labels



    # # old
    # # bout stats
    # def generate_bout_data(self, act='M', varName=None):
    #     """ generate numbers for bout stats
    #     """
    #     cstart = time.clock()
    #     print "generating %s distribution data.." %varName
    #     arrays = []
    #     arr_labels = np.zeros((self.num_md_ok, 3))
    #     cnt = 0
    #     for group in self.groups:   
    #         for mouse in group.individuals:
    #             if not mouse.ignored:
    #                 for MD in mouse.mouse_days:
    #                     if MD.dayNumber in self.daysToUse:
    #                         if not MD.ignored:                    
    #                             arr = MD.generate_bout_data(act, varName)                  
    #                             arrays.append(arr)
    #                             arr_labels[cnt] = int(MD.groupNumber), int(MD.mouseNumber), int(MD.dayNumber)
    #                             cnt +=1
    #     cstop = time.clock()
    #     if (cstop-cstart) > 100:
    #         print "-> %s for %s took: %1.2f minutes"%(self.generate_bout_data.__name__, act, (cstop-cstart)/60.)
    #         print "binary output saved to: %s" %getattr(self, '%s_bouts_dir' %act)
    #     return arrays, arr_labels


    # # events
    # def get_event_days_data(self, feat):
    #     print "loading %s event data.." %feat
    #     mouse_arr = np.zeros((self.num_mice_ok, len(self.daysToUse))) 
    #     mouse_labels = np.zeros((self.num_mice_ok, 2)) 
    #     c = 0
    #     for group in self.groups:
    #         for mouse in group.individuals:
    #             if not mouse.ignored:
    #                 k = 0
    #                 for MD in mouse.mouse_days:
    #                     if MD.dayNumber in self.daysToUse:
    #                         if not MD.ignored:
    #                             mouse_arr[c, k] = MD.load(feat)
    #                         k += 1
    #                 mouse_labels[c] = MD.groupNumber, MD.mouseNumber
    #                 c += 1
    #     return mouse_arr, mouse_labels


    # #stats
    # def get_numbers(self, act='F', what='AS'):
    #     print "getting %s %s numbers distribution data.." %(act, what)
    #     arr = np.zeros(self.num_md_ok)
    #     arr_labels = np.zeros((self.num_md_ok, 3))
    #     cnt = 0
    #     varName = 'AS_timeSet'
    #     if what == 'bout':
    #         varName = '%sB_timeSet' %act
    #     elif what == 'event':
    #         varName = '%s_timeSet' %act
    #     for group in self.groups:   
    #         for mouse in group.individuals:
    #             if not mouse.ignored:
    #                 for MD in mouse.mouse_days:
    #                     if MD.dayNumber in self.daysToUse:
    #                         if not MD.ignored:                    
    #                             arr[cnt] = MD.load(varName).shape[0]                
    #                             arr_labels[cnt] = int(MD.groupNumber), int(MD.mouseNumber), int(MD.dayNumber)
    #                             cnt +=1
    #     return arr, arr_labels





# Monkey-patch of methods
# core Darren's stuff
Experiment.add_group_attributes = register_groups.add_group_attributes
Experiment.getChowWaterFromMSIFile = register_groups.getChowWaterFromMSIFile


