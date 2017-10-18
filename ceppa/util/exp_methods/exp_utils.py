import numpy as np

from ceppa.util.my_utils import wipe_data_outside_CT6_30
"""
G.A.Onnis, 01.2017
experiment utils

Tecott Lab UCSF
"""


def get_max_AS(experiment, days=None):
    E = experiment
    counts = count_AS(E)
    max_AS = []
    for group in E.groups:           
        maxs = []
        for mouse in group.individuals:
            if not mouse.ignored:
                maxs.extend([max(counts[group.number][mouse.mouseNumber])])
        max_AS.extend([max(maxs)])
    return max_AS


def count_AS(experiment, days=None):
    E = experiment
    days_to_use = E.daysToUse if days is None else days
    counts = dict()
    for group in E.groups:
        counts[group.number] = {}             
        for mouse in group.individuals:
            if not mouse.ignored:
                counts[group.number][mouse.mouseNumber] = []
                for MD in mouse.mouse_days:
                    if MD.dayNumber in days_to_use: 
                        if not MD.ignored:
                            AS = MD.load('AS_timeSet')
                            AS_clean = wipe_data_outside_CT6_30(AS)
                            counts[group.number][mouse.mouseNumber].extend([AS_clean.shape[0]]) 

    return counts


def get_mouseNumber_to_group_dict(experiment):
    d = {}
    for group in experiment.groups:
        for mouse in group.individuals:
            d[mouse.mouseNumber] = group.number
    return d

def get_groupNumber_to_mouseNumber_dict(experiment, groupNumber):
    d = {}
    for group in experiment.groups:
        d[group.number] = [m.mouseNumber for m in group.individuals]
    return d


def get_groupNumber_from_mouseNumber(experiment, mouseNumber):
    labels_dict = experiment.get_mouseNumber_to_group_dict()
    return labels_dict[mouseNumber]


def get_mouseNumbers_from_groupNumber(experiment, groupNumber):
    labels_dict = experiment.get_groupNumber_to_mouseNumber_dict(groupNumber)
    return labels_dict[groupNumber]


def get_mouse_object(experiment, mouseNumber=2101, day=None):
    E = experiment
    if day is None:
        for group in E.groups:
            for mouse in group.individuals:
                if mouse.mouseNumber == mouseNumber:
                    if not mouse.ignored:
                        return mouse
                    # else:
                    #     print "M%d ignored" %mouseNumber
                    #     return None
    else:
        for group in E.groups:
            for mouse in group.individuals:
                if mouse.mouseNumber == mouseNumber:
                    # if not mouse.ignored:
                    for MD in mouse.mouse_days:
                        # if not MD.ignored:
                        if MD.dayNumber == day:
                            return MD
                            # else:
                            #     print "M%d, day%d ignored" %(mouseNumber, day)


# def get_MD_feature(self, mouseNumber, day, name):
#     return self.get_mouse_object(mouseNumber, day).load(name)


def count_mice(experiment):
    E = experiment
    cnt_tot = 0
    cnt_ok = 0
    for group in E.groups:             
        for mouse in group.individuals:
            if not mouse.ignored:
                cnt_ok +=1
            cnt_tot += 1
    print "individuals: %d/%d (%d ignored)" %(cnt_ok, cnt_tot, cnt_tot - cnt_ok)
    E.num_mice = cnt_tot
    E.num_mice_ok = cnt_ok
    E.num_mice_ignored = cnt_tot - cnt_ok
    return cnt_tot, cnt_ok


def count_mousedays(experiment, days=None):
    E = experiment
    days_to_use = E.daysToUse if days is None else days
    cnt_tot = 0
    cnt_ok = 0
    for group in E.groups:             
        for mouse in group.individuals:
            if 1:#not mouse.ignored:
                for MD in mouse.mouse_days:
                    if MD.dayNumber in days_to_use: 
                        if not MD.ignored:
                            cnt_ok +=1
                        cnt_tot += 1
    print "mousedays: %d/%d (%d ignored)" %(cnt_ok, cnt_tot, cnt_tot - cnt_ok)
    print "days: %d, " %len(E.daysToUse), E.daysToUse

    if days is None:
        E.num_mousedays = cnt_tot
        E.num_md_ok = cnt_ok
        E.num_md_ignored = cnt_tot - cnt_ok
    return cnt_tot, cnt_ok


def get_HCM_maintenance_time(experiment):
    E = experiment
    maintenance_time = np.zeros((1, 2))
    labels = np.zeros((1, 3))
    cnt = 0
    for group in E.groups:
        for mouse in group.individuals:
            md_time, md_labels = mouse.get_maintenance_time()
            maintenance_time = np.vstack([maintenance_time, md_time])
            labels = np.vstack([labels, md_labels])
    return maintenance_time[1:], labels[1:]


def get_HCM_recording_time(experiment):
    E = experiment
    recording_time = np.zeros((E.num_mousedays, 2))
    labels = np.zeros((E.num_mousedays, 3))
    cnt = 0
    for group in E.groups:
        for mouse in group.individuals:
            for MD in mouse.mouse_days:
                if MD.dayNumber in E.daysToUse:
                    recording_time[cnt] = MD.load('recording_start_stop_time')
                    labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
                    cnt += 1
    recording_time /= 3600.
    recording_time -= 7
    return recording_time, labels


def get_exp_info(experiment):
    E = experiment
    print "Experiment: %s" %E.short_name
    E.count_mice()
    E.count_mousedays()

    c = 0
    flagged, reason = E.flag_ignored_mousedays()
    for group in E.groups: 
        print '\ngroup %d: %s' %(group.number, group.name)  
        mice_ok, mice_no = group.count_mice()
        print '%d individuals' %(len(mice_ok) + len(mice_no))
        print '%d valid: %s' %(len(mice_ok), mice_ok)        
        print '%d ignored: %s' %(len(mice_no), mice_no)        
        for mouse in group.individuals:
            if not mouse.ignored:
                days_ok, days_no = mouse.count_mousedays()
                if len(days_no) > 0:
                    print "M%d, %d ignored mouseday/s: %s" %(
                            mouse.mouseNumber, len(days_no), days_no)
                for MD in mouse.mouse_days:
                    if MD.dayNumber in E.daysToUse: 
                        if MD.ignored:
                            # assert MD.mouseNumber == flagged[c][0]
                            # assert MD.dayNumber == flagged[c][1]
                            print flagged[c], reason[c]
                            c +=1
    # assert len(flagged) == c

def test_features(experiment, vec_type='24HDCLC', level='mouseday', err_type='stdev'):   

    E = experiment
    num_strains = len(E.strain_names)

    # load data, all days    
    avgs, errs, labels = E.generate_feature_panel_data(vec_type, level, err_type)

    # # 24 hours
    # test 1: ASP-TF-FASInt
    fidx = [0, 3, 6]
    ASP, TF, FASInt = avgs[fidx, :, 0]
    

# def get_all_data_labels(experiment):
#     """ returns labels (strain, mouse, day) for all legit mousedays
#     """
#     E = experiment
#     mouse_labels = np.zeros([E.num_mice_ok, 2], dtype=int)
#     md_labels = np.zeros([E.num_md_ok, 3], dtype=int)
#     print "loading data labels.."
#     cnt = 0
#     cnt_mice = 0
#     for group in E.groups:    
#         for mouse in group.individuals:
#                 for MD in mouse.mouse_days:
#                     if MD.dayNumber in E.daysToUse:
#                         md_labels[cnt] = MD.groupNumber, MD.mouseNumber, MD.dayNumber
#                         cnt +=1
#                 mouse_labels[cnt_mice] = group.number, mouse.mouseNumber
#                 cnt_mice +=1
#     return mouse_labels, md_labels


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


