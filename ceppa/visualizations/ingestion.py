import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import os
import csv

from ceppa.util.my_utils import get_num_items
from ceppa.visualizations.plotting_utils import get_nrows_ncols, add_titles_notes, add_xylabels, save_plot


"""
G.Onnis, 06.2017

Tecott Lab UCSF
"""


def get_subplot_specs(num_subplots):
    
    nrows, ncols, sharex, sharey = get_nrows_ncols(num_subplots)
    figsize = (6.4, 4.8)
    return figsize, nrows, ncols, sharex, sharey


def get_figure_titles(E, labels, act=None, cycle=None, tbin_type=None,
        err_type=None, plot_type=None):

    string = E.get_days_to_use_text()
    strain, mouseNumbers = np.unique(labels[:, 0])[0], np.unique(labels[:, 1])
    text = 'Food' if act == 'F' else 'Water'
    fig_title = '%s Experiment\n%s, %s, %s\n%s days: %s' %(
                    E.short_name, plot_type.replace('_', ' ').title(),
                    strain, E.strain_names[strain], 
                    E.use_days.replace('_', ' ').upper(), string,
                    )
    subtitles = ['M%d' %n for n in mouseNumbers]
    return fig_title, subtitles 



def make_annotation(ax, arr, data, k, idx, colors, units):
    xys = np.array([
        [0, arr[0, k]], 
        [len(arr)-1, arr[-1, k]]
        ])
    
    xys_text = np.array([
        [-.3, arr[0, k]], 
        [len(arr)-.7, arr[-1, k]]
        ])

    notes = [
        '%.1f%s' %(data[idx][0, k], units[k]),
        '%.1f%s' %(data[idx][-1, k], units[k])
        ]

    al = ['right', 'left']
    
    ax.scatter(xys[:,0], xys[:,1], s=1, c=colors[k], edgecolor=colors[k])

    for c in range(2):
        tkw = {'xytext':xys_text[c], 'fontsize':4, 'ha':al[c], 'color':colors[k]}
        ax.annotate(notes[c], xys[c], **tkw)
        # ax.set_clip_on(False)


def set_layout(E, ax):
    plt.setp(ax.spines.values(), visible=False)
    # ax.spines['top'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    # ax.spines['right'].set_visible(False)

    from matplotlib.ticker import MultipleLocator, FormatStrFormatter

    days = E.daysToUse
    num_days = len(days)
    ax.set_xlim([-.5, num_days + .5])
    ax.set_ylim(0, 2)

    min_step = 5 if num_days > 12 else 2
    major_xticks, minor_xticks = (min_step, 1) 
    xticklabels = range(days[0], days[-1], min_step) 
    
    ax.xaxis.set_major_locator(MultipleLocator(major_xticks))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_xticks))
    
    ax.set_xticklabels(xticklabels)
    ax.xaxis.set_ticks_position('bottom')
    ax.set_yticks([])
    ax.tick_params(axis='x', labelsize=6, direction='out')


def draw_subplot(experiment, data, labels, data_rescaled, fname,
        act='F', level='mouse', sub_type='line', plot_type='ingestion', ADD_SOURCE=False):

    E = experiment

    i_act = 0 if act == 'F' else 1
    units = ['mg/s', 'g', 'min']
    # var_names = [E.HCM_variables[x][i_act] for x in var_types]
    varTypes = ['coeffs', 'tots', 'durs']
    varNames = [E.HCM_derived['events'][plot_type][x][0] for x in varTypes]
    m_labels = np.unique(labels[:, 1])

    figsize, nrows, ncols, sharex, sharey = get_subplot_specs(num_subplots=len(m_labels))

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=sharex, sharey=sharey)

    colors = [E.fcolors[act].values()[x] for x in [1, 0, 2]]

    title, subtitles = get_figure_titles(E, labels, act=act, plot_type=plot_type)    
    
    hls = []
    for m, mouse in enumerate(m_labels): 
        try:
            ax = axes.flatten()[m]

            idx = labels[:, 1] == mouse 
            arr = data_rescaled[idx]
            
            if sub_type == 'line':                          
                
                for k, var in enumerate(varNames):  

                    ax.plot(arr[:, k], lw=.5, color=colors[k], label=var)
                    # ax.axhline(y=arr.mean()[k], c='grey', alpha='.5', label='')
                    # stop
                    make_annotation(ax, arr, data, k, idx, colors, units)

            elif sub_type == 'bar':
                pass
                # bar_width = .2
                # for k, var in enumerate(varNames):  
                #     ind = np.arange(len(arr)) + k * bar_width -.1
                #     tkw = {'lw':.2, 'label':var,
                #             'color':colors[k], 'edgecolor':None,
                #             }                
                #     ax.bar(ind, arr[:, k], bar_width, **tkw) 

            set_layout(E, ax)

            ax.set_title(subtitles[m], fontsize=10) 
            
            if m == 0:
                h, l = ax.get_legend_handles_labels()             

        except IndexError:
            ax.axis('off')
            continue
    
    # legend
    tkw = {'ncol':3, 'fontsize':8, 'bbox_to_anchor':[0.85, .08], 'frameon':False}
    legend = fig.legend(h, l, **tkw) 
    for label in legend.get_lines():
        label.set_linewidth(3)  # the legend line width

    # set subplot labels
    xlabel = 'Experiment Day'
    ylabel = '%s Coefficient' %act
    add_xylabels(fig, xlabel, ylabel)#, xypad=0, yxpad=0, labelsize=10)
    add_titles_notes(E, fig, 
                            title=title,
                            # typad=typad,
                            # tlxpad=tlxpad, 
                            # tlypad=typad
                            ) 

    plt.subplots_adjust(bottom=.12, hspace=0.6, wspace=0.4)

    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE)#, sypad=-.05)


def plot_coefficients(experiment, act='F', level='mouse', sub_type='line', 
        plot_type='ingestion', ADD_SOURCE=True):
    E = experiment

    print plot_coefficients.__name__

    # load data: coeff[mg/s], tots[mg], durs[s]
    md_data, md_labels = E.generate_ingestion_coeffs_and_totals(act)
    np.testing.assert_almost_equal(md_data[:,0], md_data[:,1]/md_data[:,2], decimal=10)

    md_data[:, 1] /= 1000.  #g
    md_data[:, 2] /= 60.    #min

    # rescale data to [0, 1]. (x-min) / (max - min)
    mx, mn = md_data.max(0), md_data.min(0)
    md_data_rescaled = (md_data - mn) / (mx-mn)
    # stop
    # push-up
    # md_data_rescaled += np.array([0, .5, 1.])
    md_data_rescaled=md_data_rescaled + np.array([1, .5, 0])
    
    dirname = E.figures_dir + '%s/%s_days/' %(plot_type, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)

    for strain in range(E.num_strains):

        idx = md_labels[:, 0] == strain
        data, data_rescaled = md_data[idx], md_data_rescaled[idx]
        labels = md_labels[idx]

        fname = dirname + '%s_%s_group%d_%s' %(plot_type, act, strain, plot_type)

        draw_subplot(E, data, labels, data_rescaled, fname, #fig_title, fname, 
                        act=act, sub_type=sub_type, plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)




# # # second plot
def set_layout2(E, ax, nrow, ncol):
    plt.setp(ax.spines.values(), visible=False)

    from matplotlib.ticker import MultipleLocator, FormatStrFormatter

    days = E.daysToUse
    num_days = len(days)
    ax.set_xlim([-.5, num_days + .5])

    min_step = 5 if num_days > 12 else 2
    major_xticks, minor_xticks = (min_step, 1) 
    xticklabels = range(days[0], days[-1], min_step) 
    
    ax.xaxis.set_major_locator(MultipleLocator(major_xticks))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_xticks))
    
    ax.set_xticklabels(xticklabels)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    if ncol > 0:
        ax.set_yticklabels([])
    ax.tick_params(axis='both', labelsize=6, direction='out')


def draw_histogram_plot(E, mouse_data, arr_preFast, arr_postFast, mouseNumbers, 
        fname, plot_type, ADD_SOURCE):
    
    # ZeroLight is one group only
    # for m in xrange(num_mice):
    #     data = mouse_data[m]
    #     label = mouseNumbers[m]
    #     data_pre, data_post = arr_preFast[m], arr_postFast[m]

    #     stop

    # i_act = 0 if act == 'F' else 1
    units = ['mg/s', 'g', 'min']
    # var_names = [E.HCM_variables[x][i_act] for x in var_types]
    varTypes = ['coeffs', 'tots', 'durs']
    varNames = [E.HCM_derived['events'][plot_type][x][0] for x in varTypes]
    
    num_mice = len(mouseNumbers)
    figsize = (12.8, 3.6)
    nrows, ncols = len(varNames), num_mice

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True, sharey=False)

    colors = [E.fcolors['F'].values()[x] for x in [1, 0, 2]]

    # title, subtitles = get_figure_titles(E, labels, act=act, plot_type=plot_type)    
    
    hls = []
    cnt = 0
    for m in xrange(nrows):             # FC, FT, FD
        data = mouse_data[:, :, m] 
        pre, post = arr_preFast[:, m], arr_postFast[:, m]

        for n in xrange(ncols):         # mouseNumbers
            ax = axes.flatten()[cnt]
            # plot quantity across days for each mouse
            ax.plot(data[n, :], lw=.5, color=colors[m])
            if m == 0:
                xmin, xmax = ax.get_xlim()
                ax.axhline(xmin=xmin, xmax=xmax, y=data[n].mean(0), 
                    linestyle='-', color=colors[m], zorder=0,
                    label='average FC - up to day 35 value')
                ax.axhline(xmin=xmin, xmax=xmax, y=pre[n], 
                    linestyle='--', color='g', zorder=1, 
                    label='day%d, FC 4h-preFast value' %E.fastDayNumbers[0])
                ax.axhline(xmin=xmin, xmax=xmax, y=post[n], 
                    linestyle=':', color='r', zorder=2, 
                    label='day%d FC 1h-postFast value' %E.fastDayNumbers[0])
                
                ax.set_title('M%d' %mouseNumbers[n], fontsize=10)
                if n == 0:
                    h, l = ax.get_legend_handles_labels()

            if n == 0:
                ax.set_ylabel('%s [%s]' %(varNames[m], units[m]), fontsize=10)

            ax.set_ylim([.9*data.min(), 1.1*data.max()])
            set_layout2(E, ax, m, n)

            cnt+=1
        
    # legend
    tkw = {'fontsize':8, 'bbox_to_anchor':[0.8, .15], 'frameon':False}
    legend = fig.legend(h, l, **tkw) 
    for label in legend.get_lines():
        label.set_linewidth(3)  # the legend line width

    # set subplot labels
    xlabel = 'Experiment Day'
    add_xylabels(fig, xlabel)
    add_titles_notes(E, fig, 
                    title='F-Coefficient, F-Total Amounts, F-Total PhotoBeam BreakTime'
                    ) 

    plt.subplots_adjust(bottom=.12)#, hspace=0.6, wspace=0.4)

    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.03)


def check_ZeroLightExp_FC(experiment, act='F', plot_type='ingestion', ADD_SOURCE=True):
    E = experiment

    if E.IGNORE_MD:
        stop

    print check_ZeroLightExp_FC.__name__

    # get FC coeff[mg/s], F totals, F totals durations for mousedays
    md_data, md_labels = E.generate_ingestion_coeffs_and_totals(act)  
    np.testing.assert_almost_equal(md_data[:,0], md_data[:,1] / md_data[:,2], decimal=10)
    
    # convert    
    md_data[:, 1] /= 1000.  #g
    md_data[:, 2] /= 60.    #min

    mouseNumbers = np.unique(md_labels[:, 1])
    dayNumbers = np.unique(md_labels[:, 2])
    num_mice, num_days = len(mouseNumbers), len(dayNumbers)

    # data for days (up to 35) and 36 (do not use)
    idx = md_labels[:, 2] == E.fastDayNumbers[0]
    md_data_36 = md_data[idx]
    md_data_35 = md_data[~idx]
    md_labels_35 = md_labels[~idx]
    mouse_data = md_data_35.reshape(num_mice, num_days - 1, md_data.shape[1])    # day 36 out
    
    # get day 36 for all mice
    arr_preFast, arr_postFast = get_ingestion_coefficients_totals_and_durations_fastDay(E, md_labels)
    
    dirname = E.figures_dir + '%s/%s_days/check_ZeroLightExp_FC/' %(plot_type, E.use_days)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    # ZeroLight is one group only
    fname = dirname + '%s_%s_group0' %(plot_type, act)

    draw_histogram_plot(E, mouse_data, arr_preFast, arr_postFast, mouseNumbers, fname,
                        plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)


    # fname2 = dirname + 'FC_group0_%s.csv' %(E.use_days)
    
    # write_to_csv(E, mouse_data, arr_preFast, arr_postFast, mouseNumbers, fname2, plot_type)


def write_to_csv(E, mouse_data, arr_preFast, arr_postFast, mouseNumbers, fname, plot_type):
    
    # load data: coeff[mg/s], tots[mg], durs[s]
    units = ['mg/s', 'g', 'min']
    # # var_names = [E.HCM_variables[x][i_act] for x in var_types]
    varTypes = ['coeffs', 'tots', 'durs']
    varNames = [E.HCM_derived['events'][plot_type][x][0] for x in varTypes]

    headers = [
        ['Experiment: %s' %E.short_name],
        ['F-Coefficient, F-Total Amounts, F-Total PhotoBeam BreakTime'], 
        ['%s days' %E.use_days],
        ['days: %s' %E.daysToUse]
        ]

    sub_header = ['', 'group', 'mouse', 'day'] + ['%s [%s]' %(var, unit) for var, unit in zip(varNames, units)]

    with open(fname, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        for h in headers:
            writer.writerow(h)
        writer.writerow('\n')
        writer.writerow(sub_header)            
        writer.writerow('\n')
        
        m = 0
        for arr in mouse_data:      #(30, 3)
            c = 0
            for row in arr:
                row_text = [E.use_days, 'group0', mouseNumbers[m], E.daysToUse[c]]
                writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                c +=1
            writer.writerow('\n')

            # add values day 36
            row_text1 = ['', 'group0', mouseNumbers[m], 'day%d\n4h-preFast value' %E.fastDayNumbers[0]]
            row_text2 = ['', 'group0', mouseNumbers[m], 'day%d\n1h-postFast value' %E.fastDayNumbers[0]]
            writer.writerow(row_text1 + ['%1.5f' %r for r in arr_preFast[m]])
            writer.writerow(row_text2 + ['%1.5f' %r for r in arr_postFast[m]])
            writer.writerow('\n')

            # add mean etc
            writer.writerow(['', '', '', 'Mean - up to day 35:'] + ['%1.5f' %r for r in np.nanmean(arr, axis=0)])
            writer.writerow(['', '', '', 'sd:'] + ['%1.5f' %r for r in np.nanstd(arr, axis=0)])
            sem = np.nanstd(arr, axis=0) / np.sqrt(arr.shape[0]-1)
            writer.writerow(['', '', '', 'sem:'] + ['%1.5f' %r for r in sem])
            writer.writerow('\n')
            writer.writerow('\n')

            m += 1
            
    print "csv files saved to:\n%s" % fname
    

def get_ingestion_coefficients_totals_and_durations_fastDay(E, md_labels):
    """ returns FC [mg/s], FT [g], FD [min]
    """
    # totals, from ethel file
    # day 36: 17 hours fast, data from first 4 hours (preFast) 
    # and last 1 hour (postFast). in grams 
    mouseNumbersFromFile = [1405, 1416, 1417, 1418, 1406, 1420, 1421, 1422, 1429, 1430, 1431, 1432, 1439, 1442, 2504, 2506]
    valuesFromFile_pre = [1.1, 1, 1.1, 0.7, 0.9, 1, 1.4, 0.4, 1.2, 1, 0.9, 1.1, 1.1, 0.8, 1, 0.8]
    valuesFromFile_post = [0.4, 0.3, 0.3, 0.4, 0.4, 0.3, 0.5, 0.8, 0.3, 0.2, 0.3, 0.3, 0.6, 0.6, 0.4, 0.5]
    totals = np.array([mouseNumbersFromFile, valuesFromFile_pre, valuesFromFile_post]).T    # grams
    num_mice = len(mouseNumbersFromFile)

    # test
    mouseNumbers = np.unique(md_labels[:, 1])
    dayNumbers = np.unique(md_labels[:, 2])
    num_days = len(dayNumbers)
    assert num_days == len(E.daysToUse) 
    assert num_mice == len(mouseNumbers)

    # reorder 
    totals_reordered = np.zeros([num_mice, 3])
    for m, mouse_num in enumerate(mouseNumbers):
        idx = mouseNumbersFromFile == mouse_num
        totals_reordered[m] = totals[idx]

    totals_pre, totals_post = totals_reordered[:, 1], totals_reordered[:, 2]    #grams
    
    # durations
    durations_pre = np.zeros(num_mice)  # min
    durations_post = np.zeros(num_mice)
    for G in E.groups:
        m = 0
        for M in G.individuals:
            # print M
            # Fast day: 36, ingestion data
            MD = M.mouse_days[-1]
            EV = MD.load('F_timeSet')
            EV_ = EV.copy()
            tstart, tend = E.get_food_insertion_and_removal_times()
            # event durations pre/post fast
            EV_preFast = EV_[EV_[:, 1]<=tstart]
            EV_postFast = EV_[EV_[:, 1]>=tend]
            durations_pre[m] = np.diff(EV_preFast).sum() / 60.
            durations_post[m] = np.diff(EV_postFast).sum() / 60.
            
            m +=1

    # FC
    fc_pre = (1000.* totals_pre) / (60. * durations_pre)          #mg/s
    fc_post = (1000. * totals_post) / (60. * durations_post)

    # day 36, put together
    arr_preFast = np.vstack([fc_pre, np.vstack([totals_pre, durations_pre])]).T
    arr_postFast = np.vstack([fc_post, np.vstack([totals_post, durations_post])]).T
    # note: arr preFast is the same as totals read from npy (md_data)
    # totals data from npy does not include postFast
    # durations differs because md_data has also PB events that do not correspond to actual consumption
    # write a test

    return arr_preFast, arr_postFast


