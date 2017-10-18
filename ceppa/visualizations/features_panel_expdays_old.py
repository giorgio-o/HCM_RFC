import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import os
import csv

from ceppa.visualizations.plotting_utils import ax_cleanup, plot_colored_background
from ceppa.visualizations.features_panel_CT import get_panel_ymaxs


"""
G.Onnis, 04.2016

Tecott Lab UCSF
"""


# def get_panel_ymaxs(experiment, avgs, errs, labels, level):
#     E = experiment
#     if level == 'strain':
#         ymaxs = get_ymaxs(avgs, errs)

#     elif level == 'mouse':
#         ymaxs = []
#         for strain in xrange(E.num_strains):      # maxs per strain      
#             idx = labels[:, 0] == strain
#             avg, err = avgs[:, idx], errs[:, idx]
#             ymaxs.append(get_ymaxs(avg, err))

#     elif level == 'mouseday':
#         ymaxs = None

#     return ymaxs


def get_ymaxs(avgs, errs):
    tops = avgs + errs
    return np.nanmax(np.nanmax(tops, axis=3), axis=2).max(axis=1)


def set_panel_layout(E, fig, ax, feats, num_subplot, ymaxs): 
    # xticks = E.daysToUse
    ax.set_xlim([xticks[0]-1, xticks[-1]+1])
    if ymaxs is not None:
        ax.set_ylim([0, ymaxs[num_subplot]])

    if len(E.daysToUse) > 20:
        xticks = E.daysToUse[::2]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks) 
    ylims = np.array(ax.get_ylim())
    if feats[num_subplot] == 'ASP':
        ylims = [0, 1]
    ax.set_ylim([0, ylims[1]])
    ax.tick_params(axis='both', which='both', labelsize=7)
    ax.set_aspect('auto')
    ax_cleanup(ax)

    plt.subplots_adjust(left=0.1, right=0.88, hspace=0.6)#, wspace=0.15)


def get_labels_and_markers(bin_type):
    if bin_type == '24HDCLC':
        labels = ['24H', 'DC', 'LC']
        fmts = ['o', 's', '^']
        alphas = [.5, .3, .15]
    elif bin_type == '12bins':
        labels = ['CT%d-%d' %(x, x+2) for x in range(6, 30, 2)] 
        fmts = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D')#, 'd', 'P', 'X')
        # fmts = ['-', '--', '-.', ':', '.', ',', 'o', 'v', '^', '<', '>', '1']
    return labels, fmts, alphas


def draw_features(E, avg, err, bin_type, fig_title, ymaxs=None, plotType='markers'):
    
    feats = E.features
    labels, fmts, alphas = get_labels_and_markers(bin_type)

    fig, axes = plt.subplots(8, 3, figsize=(8, 12), sharex=True)
    xs = E.daysToUse 
    num_bins = avg.shape[-1]

    for c in xrange(len(feats)):
        ax = axes.flatten()[c]
        color = E.plot_settings_dict[feats[c]]['color']
        
        for _bin in xrange(num_bins): 
            y, yerr = avg[c, :, _bin], err[c, :, _bin]

            if plotType == 'markers':
                ax.errorbar(xs, y, yerr=yerr, 
                    fmt=fmts[_bin], ms=4, color=color, label=labels[_bin])
            elif plotType == 'lines':
                fmts = ['-', '--', ':']
                ax.plot(xs, y, fmts[_bin], color=color, 
                    ms=3, label=labels[_bin], zorder=1)
                # ax.fill_between(xs, y-yerr, y+yerr, color=color, alpha=alphas[_bin])

        set_panel_layout(E, fig, ax, feats, c, ymaxs)
        ax.set_title('%s %s' %(feats[c], E.plot_settings_dict[feats[c]]['unit']), 
            fontsize=10)
        if c == 1:
            h0, l0 = ax.get_legend_handles_labels()    
        
        if E.short_name == 'HiFat2' and E.use_days== 'all':
            ax.axvline(x=E.dietDayNumbers[0], ymax=1, color='.7', zorder=0)

    fig.legend(h0, l0, numpoints=1, bbox_to_anchor=[.85, .93], prop={'size':8}, frameon=False)

    fig.text(.5, .06, 'Experiment day [-]', fontsize=8, ha='center')
    fig.text(.03, .95, fig_title, fontsize=8, va='center')



def get_feature_panel_data_expdays(experiment, bin_type, level, err_type, days=None, group_avg_type='over_mds'):
    E = experiment
    feature_names = E.features
    num_items = E.num_strains
    if level == 'mouse':
        num_items = E.num_mice_ok
    
    num_bins = 12 if bin_type.endswith('bins') else 3
    num_days = len(E.daysToUse) if days is None else len(days)
    avgs = np.zeros((len(feature_names), num_items, num_days, num_bins))
    errs = np.zeross((len(feature_names), num_items, num_days, num_bins))
    for c, feat in enumerate(feature_names):

        s_data, s_labels, m_data, m_labels, md_data, md_labels = \
                    E.generate_feature_vectors_expdays(feat, bin_type, days, GET_AVGS=True, group_avg_type='over_mds')     

        if level == 'strain':
            data = s_data[0]
            yerr = s_data[1] if err_type == 'stdev' else s_data[2]
            avgs[c], errs[c], labels = data, yerr, s_labels
        
        elif level == 'mouse':
            avgs[c], errs[c], labels = m_data, np.zeros_like(m_data), m_labels

    return avgs, errs, labels


def plot_features_panel_expdays(experiment, bin_type='12bins', level='strain', err_type='stdev', COMMON_Y=False, plotType='markers'):   

    E = experiment
    num_strains = len(E.strain_names)

    # load data, all days    
    avgs, errs, labels = get_feature_panel_data_expdays(E, bin_type, level, err_type)

    dirname = E.figures_dir_subpar + 'features/vectors/panels_expdays/%s_days/%s/' %(E.use_days, level)
    if COMMON_Y:
        dirname += 'common_yscale/'
        ymaxs = get_panel_ymaxs(E, avgs, errs, labels, level)
    else:
        dirname += 'free_yscale/'
        ymaxs = [None for n in E.features]
    if not os.path.isdir(dirname): os.makedirs(dirname)

    print "%s..\nlevel: %s\nbin_type: %s\nerr_type: %s" %(
            plot_features_panel_expdays.__name__, level, bin_type, err_type)

    
    # plotting 
    if level == 'strain':
        for strain in range(num_strains):
            avg_text = 'avg$\pm$%s' %err_type if plotType == 'markers' else 'average'
            fig_title = 'group%d: %s\n%s\n%s\n%s_days:%dto%d' %(
                        strain, E.strain_names[strain], bin_type, avg_text, 
                        E.use_days, E.daysToUse[0], E.daysToUse[-1])

            draw_features(E, avgs[:, strain], errs[:, strain], bin_type, 
                            fig_title, ymaxs, plotType)
            
            #save
            dirname_out = dirname + '%s_%s/' %(bin_type, plotType)
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
            fname = dirname_out + 'feature_panel_strain%d.pdf' %strain
            plt.savefig(fname, bbox_inches='tight')
            plt.close()
            print "figures saved to: %s" %fname

    elif level == 'mouse':
        avg_text = 'avg$\pm$%s' %err_type if plotType == 'markers' else ''
        for strain in xrange(num_strains):            
            idx = labels[:, 0] == strain
            mouseNumbers = labels[idx, 1]
            num_mice = idx.sum()
            avg, err = avgs[:, idx], errs[:, idx]
            for c in xrange(num_mice):
                fig_title = 'group%d: %s\nM%d\n%s\n%s\n%s_days:%dto%d' %(
                            strain, E.strain_names[strain], mouseNumbers[c], 
                            bin_type, avg_text, E.use_days, E.daysToUse[0], E.daysToUse[-1])
                
                # ymaxs = get_ymaxs(avg, err)
                draw_features(E, avg[:, c], err[:, c], bin_type, 
                                fig_title, ymaxs[strain], plotType='lines')

                #save
                dirname_out = dirname + 'strain%d/%s/' %(strain, bin_type)
                if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
                fname = dirname_out + \
                        'feature_panel_strain%d_mouse%d.pdf' %(strain, c)
                plt.savefig(fname, bbox_inches='tight')
                plt.close()
                print "figures saved to: %s" %fname


def write_csv_panel_table(E, bin_type='12bins', level='strain'):
    
    dirname = os.path.join(E.figures_dir_subpar, 'features/vectors/panels/%s/%s_days/' %(level, E.use_days))
    if not os.path.isdir(dirname): os.makedirs(dirname)    
    print "%s..\nlevel: %s\nbin_type: %s" %(write_csv_panel_table.__name__, level, bin_type)

    # load data
    # feature_names = E.features 
    avgs, errs, labels = load_panel_data(E, bin_type, level) 
    
    # bins = ['CT%d-%d' %(x, x+2) for x in range(6, 26, 2)] + ['CT%d-%d' %(x, x+2) for x in range(2, 6, 2)]
    bins = ['CT%d-%d' %(x, x+2) for x in range(6, 30, 2)]
    
    cols = bins if bin_type == '12bins' else ['24H', 'DC', 'LC']
    sub_header = ['feature_name, [units]'] + cols
    
    data = avgs.swapaxes(0, 1)
    cnt = 0
    for row in data:
        if level == 'strain':
            header = E.strain_names[cnt]
            labels = labels[:, np.newaxis]
            dirname_out = dirname + '%s/csv/' %bin_type
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
            fname = 'all_feature_vectors_table_%s_strain%d.csv' %(bin_type, cnt)
        
        elif level == 'mouse':
            s_num, m_num = [int(labels[cnt, i]) for i in range(2)]
            # mouse_num = E.get_mouse_object(mouseNumber=m_num).individualNumber
            header = E.strain_names[s_num], 'M%d' %m_num
            
            dirname_out = dirname + 'strain%d/%s/csv/' %(s_num, bin_type)
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
            fname = 'all_feature_vectors_table_%s_strain%d_mouse%d.csv' %(
                                             bin_type, s_num, m_num)
        
        elif level == 'mouseday':
            s_num, m_num, md_num = [int(labels[cnt, i]) for i in range(3)]
            # mouse_num = E.get_mouse_object(mouseNumber=m_num).individualNumber
            # day_num = E.get_mouse_object(mouseNumber=m_num, day=md_num).dayNumber
            header = E.strain_names[s_num], 'M%d' %m_num, 'day%d' %md_num
            
            dirname_out = dirname + 'strain%d/%s/csv/' %(s_num, bin_type)
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
            fname = 'all_feature_vectors_table_%s_strain%d_mouse%d_day%d.csv' %(
                                            bin_type, s_num, m_num, md_num)
        
        with open(dirname_out + fname, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow([header])
            writer.writerow(sub_header)
            c = 0
            for line in row:
                feat = E.feature_names[c]
                unit = E.plot_settings_dict[feat]['unit']
                writer.writerow(np.hstack(['%s, %s' %(feat, unit), ['%1.4f' %r for r in line]]))
                c += 1
            cnt += 1
    print "csv files saved to:\n%s" % dirname_out







# def get_panel_ymaxs(experiment, avgs, errs, labels, level):
#     E = experiment
#     if level == 'strain':
#         ymaxs = get_ymaxs(avgs, errs)

#     elif level == 'mouse':
#         ymaxs = []
#         for strain in xrange(E.num_strains):      # maxs per strain      
#             idx = labels[:, 0] == strain
#             avg, err = avgs[:, idx], errs[:, idx]
#             ymaxs.append(get_ymaxs(avg, err))

#     elif level == 'mouseday':
#         ymaxs = None

#     return ymaxs

# def get_panel_data(E, bin_type, level, err_type):
#     feature_names = E.features
#     num_items = E.num_strains
#     if level == 'mouse':
#         num_items = E.num_mice_ok
#     elif level == 'mouseday':
#         num_items = E.num_md_ok
    
#     num_bins = 12 if bin_type.endswith('bins') else 3
#     num_days = len(E.daysToUse)
#     avgs = np.ones((len(feature_names), num_items, num_days, num_bins))
#     errs = np.ones((len(feature_names), num_items, num_days, num_bins))
#     for c, feat in enumerate(feature_names):
        
#         s_data, s_labels, m_data, m_labels, md_data, md_labels = \
#                     E.generate_expdays_feature_vectors(feat, bin_type)     

#         if level == 'strain':
#             data = s_data[0]
#             yerr = s_data[1] if err_type == 'stdev' else s_data[2]
#             avgs[c], errs[c], labels = data, yerr, s_labels
        
#         elif level == 'mouse':
#             avgs[c], errs[c], labels = m_data, np.zeros_like(m_data), m_labels

#     fname1, fname2, fname3 = get_fnames(E, bin_type, level, err_type)
#     np.save(fname1, avgs)
#     np.save(fname2, errs)
#     np.save(fname3, labels)
#     print "binary output saved to:\n%s\n%s\n%s" %(fname1, fname2, fname3) 
#     return avgs, errs, labels


# def get_fnames(E, bin_type, level, err_type):
#     file1, file2 = ['panel_expdays_%s_%s_%s_%s.npy' %(level, name, err_type, bin_type) \
#                         for name in ['avgs', 'errs']]
#     if bin_type == '24HDCLC':
#         file1, file2 = ['panel_expdays_%s_%s_%s.npy' %(level, name, bin_type) \
#                         for name in ['avgs', 'errs']]
#     file3 = '%s_labels.npy' %level
#     dirname = E.features_dir + 'panel_data/'
#     if not os.path.isdir(dirname): os.makedirs(dirname)
#     return [dirname + x for x in [file1, file2, file3]]


# def load_panel_data(E, bin_type='12bins', level='strain', err_type='stdev', GENERATE=False):
#     if not GENERATE:
#         try:
#             avgs, errs, labels = [np.load(x) \
#                                     for x in get_fnames(E, bin_type, level, err_type)]
#         except IOError:
#             avgs, errs, labels = get_panel_data(E, bin_type, level, err_type)
#     else:
#         avgs, errs, labels = get_panel_data(E, bin_type, level, err_type)
#     return avgs, errs, labels
