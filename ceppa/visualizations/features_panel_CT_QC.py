import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import os
import csv

from ceppa.util import my_utils 
from ceppa.visualizations.plotting_utils import add_titles_notes
from ceppa.visualizations.plotting_utils import add_xylabels, ax_cleanup, plot_colored_background, save_plot


"""
G.Onnis, 11.2016
    upadted: 04.2016

Tecott Lab UCSF
"""

np.set_printoptions(precision=4, threshold=8000)




def get_figure_titles(E, labels, level, act=None, cycle=None, tbin_type=None,
        err_type=None, plot_type=None):

    days_string = E.get_days_to_use_text()

    add_note = level if level == 'mouseday' else '%s avg$\pm$%s' %(level, err_type)

    fig_title = '%s Experiment\n%s, %s, %s\n%s days: %s' %(
                    E.short_name, plot_type.replace('_', ' ').title(), 
                    add_note, cycle,
                    E.use_days.replace('_', '-').title(), days_string
                    )

    subtitles = ['%s %s' %(x, E.plot_settings_dict[x]['unit']) for x in E.features]

    if level == 'group':
        fig_title += '\ngroup%d: %s' %(labels, E.strain_names[labels])
    
    if level == 'mouse':
        strain, mouseNumber = labels
        fig_title += '\ngroup%d: %s, M%d' %(
                        strain, E.strain_names[strain], mouseNumber)

    elif level == 'mouseday':
        strain, mouseNumber, day = labels
        fig_title += '\ngroup%d: %s, M%d, D%d' %(
                        strain, E.strain_names[strain], 
                        mouseNumber, day)

    return fig_title, subtitles


def get_ymaxs(avgs):
    return np.nanmax(np.nanmax(np.nansum(avgs, axis=-1), axis=2), axis=1) *1.15


def get_panel_ymaxs(experiment, features, level, bin_type, err_type='sd', COMMON_Y=False):
    E = experiment

    if not COMMON_Y:
        if level == 'group':
            ymaxs = np.array([None for n in features])
        elif level == 'mouse':
            ymaxs = np.array([[None for n in features] for x in range(E.num_strains)])
        elif level == 'mouseday':
            ymaxs = np.array([[None for n in features] for x in range(E.num_mousedays)])
            
    else:
        print "computing panel ymaxs for: %s.." %level
        # load data    
        avgs, labels = E.load_features_vectors(features, level, bin_type, 
                                err_type, days=E.acclimatedDayNumbers)
        
        if level == 'group':
            ymaxs = get_ymaxs(avgs)

        elif level in ['mouse', 'mouseday']:
            ymaxs = []
            for strain in xrange(E.num_strains):      # maxs per group      
                idx = labels[:, 0] == strain
                avg = avgs[:, idx]
                ymaxs.append(get_ymaxs(avg))                

        # elif level == 'mouseday':
        #     ymaxs = []
        #     c = 0
        #     for strain in xrange(E.num_strains):      # maxs per group      
        #         idx = labels[:, 0] == strain
        #         avg = [avgs]
                
        #         m_labels = np.unique(labels[idx, 1])
                
        #         for mouse in m_labels:
        #             idx2 = labels[:, 1] == mouse
        #             avg = avgs[:, idx2]
        #             maxs = get_ymaxs(avg)
        #             stop
        #             for n in xrange(idx2.sum()):
        #                 ymaxs[c] = maxs
        #                 c += 1

    return ymaxs


def set_panel_layout(E, fig, ax, feats, num_subplot, bin_type, xticks, xlabels, ymaxs):
    if ymaxs is not None:
        ax.set_ylim([0, ymaxs[num_subplot]])
        
    if bin_type.endswith('cycles'):
        rotation = 0
        # xticks = [1, 2, 3]
        # xlabels = ['24H', 'DC', 'LC']
        ax.set_xlim([.3, 3.7])
        labelsize = 8

    elif bin_type.endswith('bins'):
        x0, x1 = 5, 31
        if E.BIN_SHIFT:
            shift = E.binTimeShift / 3600 if E.binTimeShift < 0 else E.binTimeShift / 3600 + 1
            x0 += shift
            x1 += shift

        if bin_type == '24bins':
            xlabels[1::2] = ['' for i in range(len(xlabels)/2)]
        
        ax.set_xlim([x0, x1])
        DC_start, DC_end = my_utils.get_CT_bins(tbin_type='3cycles')[1]
        plot_colored_background(ax, tstart=DC_start, tend=DC_end)
        labelsize = 6

    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels, rotation='vertical')
    # major_xticks, minor_xticks = (4, 2) #if bin_type == '12bins' else (24, 1)
    # formatter = '%d' if not E.BIN_SHIFT else '%1.1f'
    # ax.xaxis.set_major_locator(MultipleLocator(major_xticks))
    # ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    # ax.xaxis.set_minor_locator(MultipleLocator(minor_xticks))
    # fig.canvas.draw()
    # # ax.set_xticklabels(ax.get_xticks())
    # labels = [int(item.get_text()) for item in ax.get_xticklabels()]
    # # labels = ax.get_xticklabels()
    
    # labels[-2] = u'4'
    # # stop
    # ax.set_xticklabels(labels)

    ylims = [0, 1] if feats[num_subplot] == 'ASP' else np.array(ax.get_ylim())
    ax.set_ylim((0, ylims[1]))
    ax.set_aspect('auto')
    ax_cleanup(ax, labelsize=labelsize)

    plt.subplots_adjust(left=0.1, right=0.88, hspace=0.6)#, wspace=0.15)



def draw_features(E, avg, labels, level, bin_type, err_type, fname, 
        ymaxs=None, plot_type='features', ADD_SOURCE=False):
    
    feats = E.features
    figsize = (6.4, 9.6)#(8, 12)
    nrows, ncols = 8, 3

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True)

    other_color = E.fcolors['other'][0]
    
    title, subtitles  = get_figure_titles(E, labels, level, 
                                cycle=bin_type, err_type=err_type, plot_type=plot_type)


    xticks, xlabels = my_utils.get_CT_ticks_labels(
                                bin_type=bin_type, 
                                SHIFT=E.BIN_SHIFT, 
                                tshift=E.binTimeShift)

    # xs = range(7, 31, 2) if bin_type == '12bins' else np.arange()
    if bin_type == '12bins':
        xs = xticks[:-1] + 1  
    elif bin_type == '24bins': 
        xs = xticks[:-1] + .5
    
    for c in xrange(len(feats)):
        ax = axes.flatten()[c]
        color = E.plot_settings_dict[feats[c]]['color']

        if bin_type in ['12bins', '24bins']:                
            ax.errorbar(xs, avg[c, :, 0], yerr=avg[c, :, 1], 
                lw=1.5, fmt='s-', ms=3, color=color)
        
        elif bin_type == '3cycles':
            xpos = [.7, 1.7, 2.7]
            bar_width = .6
            rect = ax.bar(xpos, avg[c, :, 0], bar_width,
                yerr=[[0,0,0], avg[c, :, 1]], color=color,
                capsize=2,
                ecolor=color, 
                )

        set_panel_layout(E, fig, ax, feats, c, bin_type, 
                            xticks, xlabels, ymaxs)

        ax.set_title(subtitles[c], fontsize=10)

        # show fast
        if E.short_name == '2CFast':
            if hasattr(E, 'fastDayNumbers'):
                if E.use_days in ['fast', 'refeed'] and bin_type.endswith('bins'):
                    if E.use_days == 'fast':
                        tstart, tend = E.get_food_removal_times()
                    elif E.use_days == 'refeed':
                        tstart, tend = E.get_food_reinsertion_times()
                    plot_colored_background(ax, tstart, tend, color=other_color, alpha=.7)



    xlabel = 'Circadian Time [hr]' if bin_type.endswith('bins') else 'Day cycle'
    add_xylabels(fig, xlabel=xlabel, xypad=.02, labelsize=10)

    add_titles_notes(E, fig,
                    title=title,
                    typad=-.02,
                    tlxpad=-.1,
                    tlypad=-.02)    

    # add_text
    tkw = {'fontsize':10, 'ha':'left'}
    fig.text(-.09, .85, 'Active\nStates', **tkw)
    fig.text(-.09, .75, 'Total\nAmounts', **tkw)
    fig.text(-.09, .65, 'AS\nIntensities', **tkw)
    fig.text(-.05, .4, 'B     o     u     t     s', 
                    rotation='vertical', **tkw)

    if level == 'mouse':
        mouse = E.get_mouse_object(mouseNumber=labels[1])
        if mouse.ignored:
            fig.text(-.08, .93, 'MD excluded', fontsize=18,
                    color='.5', 
                    ha='left', va='bottom',
                    transform=ax.transAxes)

    elif level == 'mouseday':

        MD = E.get_mouseday_object(mouseNumber=labels[1], dayNumber=labels[2])
        if MD.ignored:
            fig.text(-.08, .93, 'MD excluded', fontsize=18,
                    color='.5', 
                    ha='left', va='bottom',
                    transform=ax.transAxes)

        # show fast
        if E.short_name == '2CFast':
            if hasattr(E, 'fastDayNumbers'):    
                day = labels[-1]
                if day in E.fastDayNumbers + E.reFeedDayNumbers:
                    text = 'FAST' if day in E.fastDayNumbers else'REFEED' 
                    fig.text(.8, .955, text, fontsize=18,
                            color=other_color, 
                            ha='left', va='bottom',
                            transform=ax.transAxes)


    plt.subplots_adjust(wspace=.3)

    sxpad, sypad = -.05, .03
    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sxpad=sxpad, sypad=sypad)


def plot_features_panel(experiment, level='group', bin_type='12bins', err_type='sd',  
        days=None, COMMON_Y=True, plot_type= 'features', ADD_SOURCE=True):   

    E = experiment

    print "%s, level: %s, bin_type: %s, err_type: %s, %s days, COMMON_Y=%s" %(
            plot_features_panel.__name__, level, bin_type, err_type, E.use_days, COMMON_Y)

    features = E.features
    
    string = '_shifted%+02dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    dirname = E.figures_dir + '%s/vectors/panels_CT_QC/%s/%s%s/' %(plot_type, level, bin_type, string)
    if COMMON_Y:
        dirname += 'y_common/'
    else:
        dirname += 'y_free/'
    if not os.path.isdir(dirname): os.makedirs(dirname)

    # load data  
    data, labels = E.load_features_vectors(features, level, bin_type, err_type, days)
    
    ymaxs = get_panel_ymaxs(E, features, level, bin_type, err_type, COMMON_Y)  

    if level == 'group':
        
        for strain in xrange(E.num_strains):
            dirname_out = dirname + '%s/' %err_type
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
            fname = dirname_out + '%s_panel_CT_group%d' %(plot_type, strain)
            draw_features(E, data[:, strain], labels[strain], 
                            level, bin_type, err_type, fname, 
                            ymaxs=ymaxs, ADD_SOURCE=ADD_SOURCE)
            
    elif level == 'mouse':
        
        for strain in xrange(E.num_strains):            
            idx = labels[:, 0] == strain
            avg, m_labels = data[:, idx], labels[idx]
            
            dirname_out = dirname + 'group%d/%s/' %(strain, err_type)
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

            for c in xrange(avg.shape[1]):
                fname = dirname_out + '%s_panel_group%d_M%d' %(
                                        plot_type, strain, m_labels[c, 1])

                draw_features(E, avg[:, c], m_labels[c], 
                                level, bin_type, err_type, fname, 
                                ymaxs=ymaxs[strain], ADD_SOURCE=ADD_SOURCE)

        
    elif level == 'mouseday':
        
        for strain in xrange(E.num_strains):
            idx = labels[:, 0] == strain
            avg, md_labels = data[:, idx], labels[idx]
            
            dirname_out = dirname + 'group%d/' %strain
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
            
            for c in xrange(avg.shape[1]):
                fname = dirname_out + '%s_panel_group%d_M%d_D%d' %(
                                        plot_type, strain, md_labels[c, 1], md_labels[c, 2])
            
                draw_features(E, avg[:, c], md_labels[c], 
                                level, bin_type, err_type, fname,
                                ymaxs=ymaxs[strain], ADD_SOURCE=ADD_SOURCE)






# # Features csv
def write_to_csv1(E, level, bin_type, err_type='sd', plot_type='features'):

    dirname = os.path.join(E.figures_dir, 'features/vectors/panels_CT_QC/csv_files/%s/' %(level))
    if not os.path.isdir(dirname): os.makedirs(dirname)    
    fname1 = dirname + 'panel_CT_features_vectors_%s_%s.csv' %(level, bin_type)

    print "%s..\nlevel: %s, bin_type: %s, err_type: %s, days: %s, BIN_SHIFT: %s" %(
        write_to_csv1.__name__, level, bin_type, err_type, E.daysToUse, E.BIN_SHIFT)

    # load data
    features = E.features_by_activity 
    data, labels = E.load_features_vectors(features, level, bin_type, err_type)
    new_data = data[:,:,:,0]     # (num_features, num_mousedays, num_bins)
    new_data1 = new_data.swapaxes(0, 1).swapaxes(1, 2)  # (num_mousedays, num_bins, num_features)
    
    # headers
    string = 'BIN_SHIFTED: %dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    header0 = ['Exp: %s' %E.short_name, '%d %s' %(len(features), plot_type), '%s values' %level, bin_type, string]

    feat_unit = ['%s %s' %(feat, E.plot_settings_dict[feat]['unit']) for feat in features]
    sub_header = ['group', 'mouse', 'mouseday', 'bin'] + feat_unit

    with open(fname1, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(header0)
        writer.writerow('\n')
        writer.writerow(sub_header)
        cnt = 0
        for md in new_data1:
            c = 0
            for row in md:
                row_text = [labels[cnt, 0], labels[cnt, 1], labels[cnt, 2], c]
                writer.writerow(np.hstack([row_text, ['%1.4f' %r for r in row]]))
                c +=1
            cnt += 1

    print "csv files saved to:\n%s" % fname1



def write_to_csv2(E, level, bin_type, err_type='sd', plot_type='features'):

    dirname = os.path.join(E.figures_dir, 'features/vectors/panels_CT_QC/csv_files/%s/' %(level))
    if not os.path.isdir(dirname): os.makedirs(dirname)    
    fname1 = dirname + 'panel_CT_features_vectors_%s_%s_breakdown.csv' %(level, bin_type)

    print "%s..\nlevel: %s, bin_type: %s, err_type: %s, days: %s, BIN_SHIFT: %s" %(
        write_to_csv2.__name__, level, bin_type, err_type, E.daysToUse, E.BIN_SHIFT)

    # load data
    features = E.features_by_activity 
    data, labels = E.load_features_vectors(features, level, bin_type, err_type)
    new_data = data[:,:,:,0]     # (num_features, num_mousedays, num_bins)
    new_data1 = new_data.swapaxes(0, 1).swapaxes(1, 2)  # (num_mousedays, num_bins, num_features)
    
    
    # headers
    string = 'BIN_SHIFTED: %dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    header0 = ['Exp: %s' %E.short_name, '%d %s' %(len(features), plot_type), '%s values' %level, bin_type, string]
    
    feat_unit = ['%s %s' %(feat, E.plot_settings_dict[feat]['unit']) for feat in features]
    sub_header = ['group', 'mouse', 'mouseday', 'bin'] + feat_unit
    
    with open(fname1, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(header0)
        writer.writerow('\n')
        writer.writerow(sub_header)
        
        for group_num in range(E.num_strains):
            idx_group = labels[:, 0] == group_num
            group_data = new_data1[idx_group]
            group_labels = labels[idx_group]

            for day in E.daysToUse:
                idx_day = group_labels[:, 2] == day
                day_data = group_data[idx_day]   # mouseday==day, bin, features
                day_labels = group_labels[idx_day]
                new_day_data = day_data.swapaxes(0, 1) # bin, mouseday==day, features

                b = 0
                for bin_data in new_day_data:
                    c = 0
                    for row in bin_data:
                        row_text = [day_labels[c, 0], day_labels[c, 1], day_labels[c, 2], b]
                        writer.writerow(np.hstack([row_text, ['%1.4f' %r for r in row]]))
                        c +=1
                    
                    writer.writerow(['', '', '', 'Mean:'] + ['%1.4f' %r for r in bin_data.mean(0)])
                    writer.writerow(['', '', '', 'sd:'] + ['%1.4f' %r for r in bin_data.std(0)])
                    sem = bin_data.std(0) / np.sqrt(row.shape[0]-1)
                    writer.writerow(['', '', '', 'sem:'] + ['%1.4f' %r for r in sem])
                    writer.writerow('\n')
                    b +=1

    print "csv files saved to:\n%s" % fname1

# # # old stuff 
def write_panel_to_csv(E, level, bin_type, err_type='sd', plot_type='features'):
    
    dirname = os.path.join(E.figures_dir, 'features/vectors/panels_CT_QC/%s/csv_files/' %(level))
    if not os.path.isdir(dirname): os.makedirs(dirname)    

    print "%s..\nlevel: %s\nbin_type: %s\nerr_type: %s" %(
        write_panel_to_csv.__name__, level, bin_type, err_type)

    # load data
    features = E.features 
    data, labels = E.load_features_vectors(features, level, bin_type, err_type)
    data = data.swapaxes(0, 1)
    avgs, errs = data[:, :, :, 0], data[:, :, :, 1]

    # headers
    stop
    bins = ['CT%d-%d' %(x, x+2) for x in range(6, 30, 2)]

    # bins = ['CT%d-%d' %(x, x+2) for x in range(6, 26, 2)] + ['CT%d-%d' %(x, x+2) for x in range(2, 6, 2)]
    cols = bins if bin_type.endswith('bins') else ['24H', 'DC', 'LC']
    
    header0 = '%sExp\n%d %s, %s avg, %s' %(E.short_name, len(features), plot_type, level, bin_type)
    sub_header = ['feature_name [unit] \ time_bin'] + cols

    cnt = 0
    for row in avgs:

        if level == 'group':
            s_num = labels[cnt]

            header1 = 'group%d: %s' %(s_num, E.strain_names[s_num])
            labels = labels[:, np.newaxis]

            dirname_out = dirname + '%s/' %bin_type
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
            fname = 'panel_CT_features_vectors_%s_group%d.csv' %(bin_type, cnt)
        
        elif level == 'mouse':
            s_num, m_num = labels[cnt]

            header1 = 'group%d: %s, M%d' %(
                        s_num, E.strain_names[s_num], m_num)
            
            dirname_out = dirname + 'group%d/%s/' %(s_num, bin_type)
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
            fname = 'panel_CT_features_vectors_%s_group%d_mouse%d.csv' %(
                                             bin_type, s_num, m_num)
        
        elif level == 'mouseday':
            s_num, m_num, md_num = labels[cnt]

            header1 = 'group%d: %s, M%d, D%d' %(
                        s_num, E.strain_names[s_num], m_num, md_num)
            
            dirname_out = dirname + 'strain%d/%s/' %(s_num, bin_type)
            if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
            fname = 'panel_CT_features_vectors_%s_group%d_mouse%d_day%d.csv' %(
                                            bin_type, s_num, m_num, md_num)
        
        with open(dirname_out + fname, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow([header0])
            writer.writerow([header1])
            writer.writerow(sub_header)
            c = 0
            for line in row:
                feat = E.features[c]
                unit = E.plot_settings_dict[feat]['unit']
                writer.writerow(np.hstack(['%s, %s' %(feat, unit), ['%1.4f' %r for r in line]]))
                c += 1
            cnt += 1
    print "csv files saved to:\n%s" % dirname_out


def get_dirname_out(E, bin_type, level, err_type, base_name, group=None):
    dirname1 = os.path.join(E.figures_dir, 'features/vectors/csv_files/%s/%s/' %(
                                                                    level, bin_type))
    if bin_type.endswith('bins') and level in ['mouse', 'mouseday']:
        dirname1 += 'group%d/' %group
    dirname2 = dirname1 + '%s/' %err_type
    for dirname in [dirname1, dirname2]:
        if not os.path.isdir(dirname): os.makedirs(dirname)
    return os.path.join(dirname1, base_name + '_avg.csv'), os.path.join(dirname2, base_name + '_%s.csv' %err_type)


def write_vector_to_csv(E, avgs, errs, labels, level, bin_type, err_type, base_name, 
        headers, sub_header, group=None):
    
    fnames = get_dirname_out(E, bin_type, level, err_type, base_name, group)  
    n = 0
    for fname, arr in zip(fnames, [avgs, errs]):
        with open(fname, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow([headers[n]])
            writer.writerow(sub_header)
            c = 0
            for row in arr:
                if level == 'group':
                    row_label = E.strain_names[labels[c]]
                elif level == 'mouse':
                    row_label = 'M%d' %labels[c, 1]
                elif level == 'mouseday':
                    row_label = 'M%d' %labels[c, 1] + ' day%d' %labels[c, 2]
                writer.writerow(np.hstack([row_label, ['%1.4f' %r for r in row]]))
                c += 1
            print "csv files saved to:\n%s" % fname
        n +=1


def write_feature_vectors_to_csv(E, level, bin_type, group_avg_type='over_mds',
        plot_type='features'):
       
    features = E.features_by_activity
    
    bins = ['24H', 'DC', 'LC'] if bin_type == '24HDCLC' \
                else ['CT%d_%d' %(x, x+2) for x in range(6, 30, 2)] 
    

    for err_type in ['sd', 'sem']:

        print "%s..\nlevel: %s, bin_type: %s, err_type: %s" %(
            write_feature_vectors_to_csv.__name__, level, bin_type, err_type)

        # load data
        data, labels = E.load_features_vectors(features, level, bin_type, err_type)
        data = data.swapaxes(0, 1)
        avgs, errs = data[:, :, :, 0], data[:, :, :, 1]

        cols = ['%s %s' %(x, E.plot_settings_dict[x]['unit']) for x in features]
        sub_header = ['%s \ feature_name [unit]' %level] + cols

        text=['avg', err_type]
        b = 0
        for tbin in bins:
                    
            if level == 'group':
                headers = [
                            ['%sExp, %d %s, %s %s, %s' %(
                            E.short_name, len(features), plot_type, level, x, tbin)] \
                            for x in text
                            ]
                base_name = 'features_vectors_%s_%s' %(level, tbin)
                write_vector_to_csv(E, avgs[:, :, b], errs[:, :, b], labels, 
                                        level, bin_type, err_type, 
                                        base_name, headers, sub_header)

            elif level in ['mouse', 'mouseday']:
                for strain in xrange(E.num_strains):
                    idx = labels[:, 0] == strain

                    headers = [
                                ['%sExp, %d %s, %s %s, %s, group%d: %s' %(
                                E.short_name, len(features), plot_type, level, 
                                x, tbin, strain, E.strain_names[strain])] for x in text
                                ]

                    base_name = 'feature_vectors_%s_%s_group%d' %(level, tbin, strain)
                    write_vector_to_csv(E, avgs[idx, :, b], errs[idx, :, b], labels[idx], 
                                            level, bin_type, err_type, 
                                            base_name, headers, sub_header, strain)

            b +=1

            # b = 0
            # for tbin in bins:
            #     avg_type = 'avg_' + group_avg_type
            #     header = [level, tbin, avg_type] 
            #     sub_header = [''] + E.features_by_activity
            #     if level == 'strain':
            #         base_name = '%s_%s_feature_vectors_table_%s.csv' %(level, tbin, avg_type)
            #         write_vector_to_csv(E, avgs, errs, labels, bin_type, level, err_type,
            #                             base_name, header, sub_header)




def write_feature_vector_mouse_avgs_12bins_to_csv(E, level='mouse', bin_type='12bins', plot_type='features'):
    """ this is for 'mouse' and '12bins'
    """
    dirname_out = os.path.join(E.figures_dir, 'features/vectors/csv_files/mouse_avgs_12_bins/')
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)    
    print "%s..\nlevel: %s\nbin_type: %s" %(
        write_feature_vector_mouse_avgs_12bins_to_csv.__name__, level, bin_type)

    # load data
    features = E.features
    data, labels = E.load_features_vectors(features, level, bin_type)  # shape: feats, mice, tbins, avg/err
    data = data.swapaxes(0, 1)      # shape: mice, feats, tbins, avg/err

    avgs = data[:, :, :, 0]         #shape: mice, feats, tbins
    avgs = avgs.swapaxes(1,2)       #shape: mice, tbins, feats

    # mouse_data = avgs.swapaxes(0, 1).swapaxes(1,2)

    # bins = ['bin%d' %x for x in range(12)]
    bins = ['CT%d-%d' %(x, x+2) for x in range(6, 30, 2)]
    header0 = '%sExp\n%d %s, %s, %s' %(E.short_name, len(features), plot_type, level, bin_type)
    cols = ['%s %s' %(x, E.plot_settings_dict[x]['unit']) for x in features]
    sub_header = ['%s, time_bin \ feature_name [unit]' %level] + cols

    for strain in xrange(E.num_strains):
        idx = labels[:, 0] == strain
        arr = avgs[idx]
        header1 = 'group%d: %s' %(strain, E.strain_names[strain])
        new_labels = np.tile(labels[:,1][:, np.newaxis], len(bins)).ravel()
        new_bins = bins * len(labels[:, 1])
        fname = 'feature_vectors_mouse_avgs_%s_group%d.csv' %(bin_type, strain)
        
        with open(dirname_out + fname, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow([header0])
            writer.writerow([header1])
            writer.writerow(sub_header)
            c = 0
            for row in arr:
                for line in row:
                    writer.writerow(np.hstack(['M%d, %s' %(
                                new_labels[c], new_bins[c]), ['%1.4f' %r for r in line]]))
                    c += 1

    print "csv files saved to:\n%s" % dirname_out

