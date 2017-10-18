import numpy as np 
import matplotlib as mpl
import matplotlib.pyplot as plt 
import matplotlib.patches as patches
import matplotlib.cm as cm
from matplotlib.colors import LogNorm

import os
import csv

from ceppa.util.cage import Cage
from ceppa.util import my_utils
from ceppa.visualizations.plotting_utils import add_titles_notes
# from ceppa.visualizations.plotting_utils import get_nrows_ncols, show_devices_labels, save_plot


"""
G.Onnis, 01.2017
    updated, 06.2017

Tecott Lab UCSF
"""


def get_subplot_specs(num_subplots, tbin_type=None):
    
    nrows, ncols, sharex, sharey = get_nrows_ncols(num_subplots)
    
    if tbin_type is not None:
        # nrows, ncols = (int(tbin_type.strip('AS').strip('bins')), num_subplots)
        sharex, sharey = True, True
        if nrows == 1:
            figsize = (4.8, 3.6) if num_subplots == 1 else (6.4, 3.6)
        elif nrows > 2 and nrows <= 4:
            figsize = (4.8, 4.8)
        else:
            figsize = (6.4, 5.6)
    else:
                
        if nrows == 1:
            figsize = (4.8, 3.6)                        # width_to_height=1.33
        elif nrows == 2:
            figsize = (6.4, 3.6)
        elif nrows >= 3 and nrows <= 5:
            figsize = (6.4, 8.5) 
        else:
            figsize = (6, 10) 
    return figsize, nrows, ncols, sharex, sharey


def get_figure_titles(E, labels, level, act=None, cycle=None, tbin_type=None,
        err_type=None, plot_type=None):

    days_string = E.get_days_to_use_text()
    text = my_utils.get_text(cycle, tbin_type)
    
    # labels are a bunch of labels
    fig_title = '%s Experiment\n%s, %s, %s\n%s days: %s' %(
                    E.short_name, 
                    plot_type.replace('_', ' ').title(), level, text,
                    E.use_days.replace('_', ' ').upper(), days_string,
                    )

    if level == 'group':
        subtitles = ['%d: %s' %(n, name) for n, name in zip(labels, E.strain_names)]

    elif level == 'mouse':
        strain, mouseNumbers = np.unique(labels[:, 0])[0], labels[:, 1]
        subtitles = ['M%d' %n for n in mouseNumbers]
        fig_title += '\ngroup%d: %s' %(
            strain, E.strain_names[strain])

    elif level == 'mouseday':
        strain, mouseNumber, days = np.unique(labels[:, 0])[0], np.unique(labels[:, 1])[0], labels[:, 2]
        subtitles = ['D%d' %n for n in days]
        fig_title += '\ngroup%d: %s, M%d' %(
            strain, E.strain_names[strain], mouseNumber)

    return fig_title, subtitles


def draw_homebase_star(ax, rect_HB, obs_rect, color):
    width, height = .2, .2
    tkw = {'markersize':8, 'transform':ax.transAxes}
    for cell in rect_HB:
        yc, xc = cell
        y1, x1 = 0.93 - 0.25*yc, 0.2 + 0.5*xc,
        ax.plot(x1, y1, '*', color=color, label='coded HB', **tkw)
    if obs_rect is not None:
        for cell in obs_rect:
            yb, xb = cell
            y2, x2 = 0.93 - 0.25*yb, 0.3 + 0.5*xb
            ax.plot(x2, y2, '*', color='g', label='obs HB', **tkw)


def draw_percent_time(ax, arr, color, fontsize=6):
    ybins, xbins = arr.shape
    for x in xrange(xbins):
        for y in xrange(ybins):
            ax.text(0.25 + 0.5*x, 0.85 - 0.25*y, np.floor(arr[y, x]*1000)/10, 
                color=color, fontsize=fontsize, ha='center', va='center', 
                transform=ax.transAxes
                )
            # print 'xbin%d'%x, 'ybin%d'%y, 0.1 + 0.5*x, 0.85 - 0.25*y


def set_position_density_layout(fig, ax, im):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    ax.axis('off')
        

def set_colorbar(fig, ax, im):
    axCbar = fig.add_axes([0.97, 0.32, .03, 0.4])       # [left, bottom, width, height]
    cbar = fig.colorbar(im, cax=axCbar, format=mpl.ticker.LogFormatterMathtext())
    cbar.ax.set_ylabel('Occupancy', rotation=270, labelpad=15, fontsize=10)
    ytl_obj = plt.getp(axCbar, 'yticklabels')
    plt.setp(ytl_obj, fontsize=10)
    # cbar.ax.set_ylabel('Occupancy', fontsize=10, rotation=270, labelpad=15)


def set_legend(fig, h, l, text_color):
    fig.legend(h[::-1], l[::-1], numpoints=1, bbox_to_anchor=[1., .88], 
                handletextpad=0, prop={'size':10}, frameon=False)



def draw_it(E, fig, ax, Z3, subplot_num, level, subtitles, xbins, ybins, rect_HB, obs_rect):

    C = Cage()

    cmap = plt.get_cmap("viridis")
    vmin, vmax = .0001, 1.
    if (xbins, ybins) == (2, 4):
        vmin = 0.01
    extent = [C.CMXLower, C.CMXUpper, C.CMYLower, C.CMYUpper]   

    percent_time_color = E.fcolors['other'][0]

    if np.isnan(Z3).all():
        ax.text(.5, .5, subtitles[subplot_num] + '\nexcluded', 
            fontsize=12, color='.5', ha='center', va='center')
        ax.axis('off')
    
    else:   
        Z3_ = Z3.copy()
        Z3_[Z3<1e-4] = 1e-4     # round small numbers to almost zero for plotting

        im = ax.imshow(Z3_, interpolation='nearest', cmap=cmap, 
            norm=LogNorm(vmin=vmin, vmax=vmax))#, extent=extent)

        ax.set_title(subtitles[subplot_num], fontsize=10)
        set_position_density_layout(fig, ax, im)
        
        if (xbins, ybins) == (2, 4):
            draw_percent_time(ax, Z3 / Z3.sum(), color=percent_time_color)            
            if level == 'mouseday':
                draw_homebase_star(ax, rect_HB[subplot_num], obs_rect[subplot_num], color=percent_time_color)

        set_colorbar(fig, ax, im)

        
    # add some labeling
    if level == 'group':
        show_devices_labels(E, ax)

    elif level == 'mouseday':
        # show fast
        if E.short_name == '2CFast':
            if hasattr(E, 'fastDayNumbers'):    
                day = int(subtitles[subplot_num][1:])
                if day in E.fastDayNumbers + E.reFeedDayNumbers:
                    text = 'FAST' if day in E.fastDayNumbers else'REFEED' 
                    ax.text(.15, 1.03, text, fontsize=14,
                            color=E.fcolors['F'][0], 
                            ha='right', va='bottom',
                            transform=ax.transAxes)

    return fig, ax


def finish_plot(E, fig, level, xbins, ybins, h, l, nrows, title, fname, ADD_SOURCE):

    percent_time_color = E.fcolors['other'][0]
    set_legend(fig, h, l, text_color=percent_time_color)

    if (xbins, ybins) == (2, 4):
        fig.text(.94, .25, 'percent time', color=percent_time_color, fontsize=10, ha='left')

    if nrows == 1:
        typad = 0
        sypad = -.05
    elif nrows >=2 or nrows < 6:
        typad = 0
        sypad = .05

    add_titles_notes(E, fig, 
                    title=title,
                    typad=typad)

    plt.subplots_adjust(hspace=.3)

    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=sypad)


def draw_position_density(E, data, labels, cycle, tbin_type, level, err_type, xbins, ybins, fname,
        rect_HB=None, obs_rect=None, plot_type='position_density', ADD_SOURCE=False):


    # figure    
    figsize, nrows, ncols, sharex, sharey = get_subplot_specs(num_subplots=data.shape[0], tbin_type=tbin_type) 

    fig_title, subtitles  = get_figure_titles(E, labels=labels, level=level, cycle=cycle, tbin_type=tbin_type,
                                            err_type=err_type, plot_type=plot_type)

    percent_time_color = E.fcolors['other'][0]

    if tbin_type is not None:
        arr = my_utils.get_CT_bins(bin_type=tbin_type.strip('AS')) / 3600 -7
        
        for b in xrange(data.shape[1]):

            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, sharex=sharex, sharey=sharey)
            
            for c in xrange(nrows * ncols):
                try:
                    ax = axes.flatten()[c] if type(axes) is np.ndarray else axes        # when just one axis
                    Z3 = data[c, b, :, :, 0]
                    fig, ax = draw_it(E, fig, ax, Z3, c, level, subtitles, xbins, ybins, rect_HB, obs_rect)

                    if c < 1:
                        h, l = ax.get_legend_handles_labels()
                    
                except IndexError:
                    ax.axis('off')
                    continue
            
            title = fig_title + '\nbin%d: CT%d-%d' %(b, arr[b, 0], arr[b, 1])
            fname1 = fname + '_tbin%d' %b
            finish_plot(E, fig, level, xbins, ybins, h, l, nrows, title, fname1, ADD_SOURCE)

    else:

        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)

        for c in xrange(nrows * ncols):
            
            try: 
                ax = axes.flatten()[c] if type(axes) is np.ndarray else axes        # when just one axis
            
                Z3 = data[c, :, :, 0]       # plt average only for the moment
                fig, ax = draw_it(E, fig, ax, Z3, c, level, subtitles, xbins, ybins, rect_HB, obs_rect)
                if c < 1:
                    h, l = ax.get_legend_handles_labels()
                
            except IndexError:
                ax.axis('off')
                continue

        finish_plot(E, fig, level, xbins, ybins, h, l, nrows, fig_title, fname, ADD_SOURCE)



def plot_position_density(experiment, cycle='24H', tbin_type=None, level='mouseday', 
        xbins=12, ybins=24, err_type='sd', plot_type='position_density', ADD_SOURCE=True):

    E = experiment

    text = my_utils.get_text(cycle, tbin_type)

    print "%s, %s, %s, xbins:%d, ybins:%d, %s" %(
            plot_position_density.__name__, text, level, xbins, ybins, E.use_days)

    dirname_out = E.figures_dir + '%s/xbins%d_ybins%d/%s/%s/%s_days/' %(
                                    plot_type, xbins, ybins, level, text, E.use_days)
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

    # load data
    data, labels = E.generate_position_density(
                        cycle=cycle, tbin_type=tbin_type, level=level, 
                        xbins=xbins, ybins=ybins, err_type=err_type)
    

    if level == 'group':
        fname = dirname_out + '%s_%s_%dgroups_xbins%d_ybins%d' %(
                        plot_type, text, E.num_strains, xbins, ybins)

        draw_position_density(E, data, labels, cycle, tbin_type, 
                                level, err_type, 
                                xbins, ybins, fname,
                                plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)

    elif level == 'mouse':
        for strain in xrange(E.num_strains):
            idx = labels[:, 0] == strain
            m_data, m_labels = data[idx], labels[idx]
            fname = dirname_out + '%s_%s_group%d_xbins%d_ybins%d' %(
                plot_type, text, strain, xbins, ybins)

            draw_position_density(E, m_data, m_labels, cycle, tbin_type, 
                                    level, err_type, 
                                    xbins, ybins, fname,
                                    plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)
            
    elif level == 'mouseday':
        # nest
        rects_HB = np.array([None] * len(data))
        obs_rects = np.array([None] * len(data))
        
        condition = (xbins, ybins) == (2, 4)
        if condition:
            rects_HB, obs_rects = E.generate_homebase_data()

        for strain in range(E.num_strains):
            idx_m = labels[:, 0] == strain
            mouseNumbers = np.unique(labels[idx_m,1])
            for c in xrange(len(mouseNumbers)):
                idx_md = labels[:, 1] == mouseNumbers[c]
                md_data, md_labels = data[idx_md], labels[idx_md]
                
                fname = dirname_out + '%s_%s_group%d_M%d_xbins%d_ybins%d' %(
                                        plot_type, text, strain, mouseNumbers[c],
                                        xbins, ybins)
                                
                rect_HB, obs_rect = None, None
                if condition:
                    idx_start, idx_end = my_utils.find_nonzero_runs(idx_md)[0]
                    rect_HB = rects_HB[idx_start:idx_end]
                    obs_rect = obs_rects[idx_start:idx_end]
                
                draw_position_density(E, md_data, md_labels, cycle, tbin_type, 
                                        level, err_type, 
                                        xbins, ybins, fname,
                                        rect_HB=rect_HB, obs_rect=obs_rect,
                                        plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)

    







# # position density csv
def write_to_csv(experiment, cycle='24H', tbin_type=None, AS_FLAG=False, level='group', 
        xbins=12, ybins=24, err_type='sd', plot_type='position_density'):

    E = experiment
    use_days = E.use_days + '_days'

    text = my_utils.get_text(cycle, tbin_type, AS_FLAG)

    print "%s, %s, %s, xbins:%d, ybins:%d, %s" %(
            write_to_csv.__name__, text, level, 
            xbins, ybins, use_days)



    suffix = '%s/csv_files/xbins%d_ybins%d/%s/%s/%s_days/' %(
                    plot_type, xbins, ybins, level, text, E.use_days)

    dirname = os.path.join(E.figures_dir, suffix)
    if not os.path.isdir(dirname): os.makedirs(dirname)
    fname = dirname + '%s_%s_%s_xbins%d_ybins%d.csv' %(
                    plot_type, text, level, xbins, ybins)

    # load data
    data, labels = E.generate_position_density(
                        cycle=cycle, tbin_type=tbin_type, AS_FLAG=AS_FLAG, level=level, 
                        xbins=xbins, ybins=ybins, err_type=err_type)

    if tbin_type is not None:
        arr = my_utils.get_CT_bins(bin_type=tbin_type) / 3600 -7
        tbins = ['bin%d: CT%d-%d' %(b, row[0], row[1]) for b, row in enumerate(arr)]
        new_data = data[:, :,:,:,0].reshape(data.shape[0], data.shape[1], -1)     # (num_mousedays, 4x2 raveled)
    else:
        new_data = data[:,:,:,0].reshape(data.shape[0], -1)     # (num_mousedays, 4x2 raveled)
    
    # headers
    # string = ', BIN_SHIFTED: %dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
    headers = [
        ['Experiment: %s' %E.short_name],
        ['%s, xbins=%d, ybins=%d' %(plot_type, xbins, ybins)],
        ['%s, %s' %(level, text)], 
        ['%s days' %E.use_days],
        ['days: %s' %E.daysToUse]
        ]
        

    if level == 'group':
        sub_header = ['use_days', 'group']
        if tbin_type is not None:
            if (xbins, ybins) == (2, 4):
                sub_header += ['tbins', 'Niche', 'TopLeft', '[]', '[]', '[]', '[]', 'Feeder', 'Lick']
            else:
                sub_header += ['tbins']
        else:
            sub_header += ['Niche', 'TopLeft', '[]', '[]', '[]', '[]', 'Feeder', 'Lick']

        with open(fname, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            for h in headers:
                writer.writerow(h)
            writer.writerow('\n')
            writer.writerow(sub_header)            
            writer.writerow('\n')

            if tbin_type is not None:
                new_data_ = new_data.swapaxes(0, 1)     # tbin, days, (raveled xbins, ybins)
                for b in xrange(len(new_data_)):
                    bin_data = new_data_[b]
                    c = 0
                    for row in bin_data:
                        row_text = [use_days+ ', %s' %text, labels[c], tbins[b]]
                        writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                        c +=1
                    writer.writerow('\n')

            else:
                c = 0
                for row in new_data:
                    row_text = [use_days+ ', %s' %text, labels[c]]
                    writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                    c +=1
                writer.writerow('\n')



    elif level == 'mouse':
        sub_header = ['use_days', 'group', 'mouse'] 
        if tbin_type is not None:
            if (xbins, ybins) == (2, 4):
                sub_header += ['tbins', 'Niche', 'TopRight', '[]', '[]', '[]', '[]', 'Feeder', 'Lick']
            else:
                sub_header += ['tbins']
        else:
            sub_header += ['Niche', 'TopLeft', '[]', '[]', '[]', '[]', 'Feeder', 'Lick']

        with open(fname, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            for h in headers:
                writer.writerow(h)
            writer.writerow('\n')
            writer.writerow(sub_header)
            writer.writerow('\n')
            
            for group_num in range(E.num_strains):
                idx_group = labels[:, 0] == group_num
                group_data = new_data[idx_group]
                group_labels = labels[idx_group]

                if tbin_type is not None:
                    group_data_ = group_data.swapaxes(0, 1)     # tbin, days, (raveled xbins, ybins)
                    for b in xrange(len(group_data_)):
                        bin_data = group_data_[b]
                        c = 0
                        for row in bin_data:
                            row_text = [use_days+ ', %s' %text, group_labels[c, 0], group_labels[c, 1], tbins[b]]
                            writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                            c +=1
                        # stop
                        writer.writerow('\n')
                        writer.writerow(['', '', '', 'Mean:'] + ['%1.5f' %r for r in np.nanmean(bin_data, axis=0)])
                        writer.writerow(['', '', '', 'sd:'] + ['%1.5f' %r for r in np.nanstd(bin_data, axis=0)])
                        sem = np.nanstd(bin_data, axis=0) / np.sqrt(bin_data.shape[0]-1)
                        writer.writerow(['', '', '', 'sem:'] + ['%1.5f' %r for r in sem])
                        writer.writerow('\n')

                else:
                    c = 0
                    for row in group_data:

                        row_text = [use_days+ ', %s' %text, group_labels[c, 0], group_labels[c, 1]]
                        writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                        c +=1
                    
                    writer.writerow('\n')
                    writer.writerow(['', '', 'Mean:'] + ['%1.5f' %r for r in np.nanmean(group_data, axis=0)])
                    writer.writerow(['', '', 'sd:'] + ['%1.5f' %r for r in np.nanstd(group_data, axis=0)])
                    sem = np.nanstd(group_data, axis=0) / np.sqrt(group_data.shape[0]-1)
                    writer.writerow(['', '', 'sem:'] + ['%1.5f' %r for r in sem])
                    writer.writerow('\n')
                    



    elif level == 'mouseday':
        sub_header = ['', 'group', 'mouse', 'mouseday'] 
        if tbin_type is not None:
            if (xbins, ybins) == (2, 4):
                sub_header += ['tbins', 'Niche', 'TopLeft', '[]', '[]', '[]', '[]', 'Feeder', 'Lick']
            else:
                sub_header += ['tbins']
        else:
            sub_header += ['Niche', 'TopLeft', '[]', '[]', '[]', '[]', 'Feeder', 'Lick']

        with open(fname, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            for h in headers:
                writer.writerow(h)
            writer.writerow('\n')
            writer.writerow(sub_header)
            writer.writerow('\n')

            for group_num in range(E.num_strains):
                idx_group = labels[:, 0] == group_num
                group_data = new_data[idx_group]
                group_labels = labels[idx_group]
                
                m_labels = np.unique(group_labels[: ,1])

                for mouse in m_labels:
                    idx_mouse = group_labels[:, 1] == mouse
                    m_data = group_data[idx_mouse]
                    m_labels = group_labels[idx_mouse]

                    if tbin_type is not None:
                        
                        m_data_ = m_data.swapaxes(0, 1)     # tbin, days, (raveled xbins, ybins)
                        for b in xrange(len(m_data_)):
                            bin_data = m_data_[b]
                            c = 0
                            for row in bin_data:
                                row_text = [use_days+ ', %s' %text, m_labels[c, 0], m_labels[c, 1], m_labels[c, 2], tbins[b]]
                                writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                                c +=1
                            # stop
                            writer.writerow('\n')
                            writer.writerow(['', '', '', '', 'Mean:'] + ['%1.5f' %r for r in np.nanmean(bin_data, axis=0)])
                            writer.writerow(['', '', '', '', 'sd:'] + ['%1.5f' %r for r in np.nanstd(bin_data, axis=0)])
                            sem = np.nanstd(bin_data, axis=0) / np.sqrt(bin_data.shape[0]-1)
                            writer.writerow(['', '', '', '', 'sem:'] + ['%1.5f' %r for r in sem])
                            writer.writerow('\n')

                    else:
                        c = 0
                        for row in m_data:
                            row_text = [use_days+ ', %s' %text, m_labels[c, 0], m_labels[c, 1], m_labels[c, 2]]
                            writer.writerow(np.hstack([row_text, ['%1.5f' %r for r in row]]))
                            c +=1
                        
                        writer.writerow('\n')
                        writer.writerow(['', '', '', 'Mean:'] + ['%1.5f' %r for r in np.nanmean(m_data, axis=0)])
                        writer.writerow(['', '', '', 'sd:'] + ['%1.5f' %r for r in np.nanstd(m_data, axis=0)])
                        sem = np.nanstd(m_data, axis=0) / np.sqrt(m_data.shape[0]-1)
                        writer.writerow(['', '', '', 'sem:'] + ['%1.5f' %r for r in sem])
                        writer.writerow('\n')
                    
                         

    print "csv files saved to:\n%s" % fname

