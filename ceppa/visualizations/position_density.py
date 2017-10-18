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
from ceppa.visualizations.plotting_utils import add_titles_notes, show_devices_labels, save_plot


"""
G.Onnis, 01.2017
    updated, 06.2017

Tecott Lab UCSF
"""


def draw_homebase_star(ax, rect_HB, color):
    width, height = .2, .2
    tkw = {'markersize':2, 'color':color, 'markerfacecolor':color, 
            'markeredgecolor':color, 'transform':ax.transAxes}
    for cell in rect_HB:
        yc, xc = cell
        y1, x1 = 0.93 - 0.25*yc, 0.2 + 0.5*xc,
        ax.plot(x1, y1, '*', label='code HB', **tkw)



def set_position_density_layout(fig, ax, im):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    ax.axis('off')
        

def set_colorbar(fig, ax, im):
    axCbar = fig.add_axes([0.97, 0.32, .03, 0.4])       # [left, bottom, width, height]
    cbar = fig.colorbar(im, cax=axCbar, format=mpl.ticker.LogFormatterMathtext())
    cbar.ax.set_ylabel('Occupancy', rotation=270, labelpad=15, fontsize=12)
    ytl_obj = plt.getp(axCbar, 'yticklabels')
    plt.setp(ytl_obj, fontsize=10)
    # cbar.ax.set_ylabel('Occupancy', fontsize=10, rotation=270, labelpad=15)


def set_legend(fig, h, l, xbins, ybins, text_color):
    fig.legend(h[::-1], l[::-1], numpoints=1, bbox_to_anchor=[1.05, .88], 
                handletextpad=0, prop={'size':10}, frameon=False)


def draw_position_density_tbins2(E, data, mouseNumbers, tbin_type, err_type, 
        xbins, ybins, fig_title, fname, rect_HB=None, obs_rect=None, 
        plot_type='position_density', ADD_SOURCE=False):

    C = Cage()

    # figure    
    figsize = (6.4, 6.4)
    nrows, ncols = data.shape[0], data.shape[1]

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    
    cmap = plt.get_cmap("viridis")
    vmin, vmax = .0001, 1.
    if (xbins, ybins) == (2, 4):
        vmin = 0.01
    extent = [C.CMXLower, C.CMXUpper, C.CMYLower, C.CMYUpper]   

    percent_time_color = E.fcolors['other'][0]

    row_labels = ['M%d' %m for m in mouseNumbers]
    column_labels = ['D%d' %d for d in E.daysToUse]

    for r in xrange(nrows):
        # display row labels
        top, bottom, left, right = [getattr(fig.subplotpars, x) for x in ['top', 'bottom', 'left', 'right']]
        yy = top -.025 - (top-bottom) * r / nrows
        fig.text(left - .1, yy, row_labels[r], va='center', fontsize=8)

        for c in xrange(ncols):
            # display column labels
            if r < 1:
                xx = left + .02 + (right-left) * c / ncols
                fig.text(xx, top + .02, column_labels[c], ha='center', fontsize=8)                

            try:
                ax = axes[r, c] if type(axes) is np.ndarray else axes        # when just one axis

                Z3 = data[r, c, :, :, 0]       # plt average only for the moment
                
                if np.isnan(Z3).all():
                    ax.axis('off')
                
                else:   
                    Z3_ = Z3.copy()
                    Z3_[Z3<1e-4] = 1e-4     # round small numbers to almost zero for plotting

                    im = ax.imshow(Z3_, interpolation='nearest', cmap=cmap, 
                        norm=LogNorm(vmin=vmin, vmax=vmax))#, extent=extent)

                    set_position_density_layout(fig, ax, im)

                    if (xbins, ybins) == (2, 4):
                        draw_homebase_star(ax, rect_HB[r, c], color=percent_time_color)

                if r*c < 1:
                    hh, ll = ax.get_legend_handles_labels()

            except IndexError:
                ax.axis('off')
                continue

    set_colorbar(fig, ax, im)
    set_legend(fig, hh, ll, xbins, ybins, 
                text_color=percent_time_color)

    add_titles_notes(E, fig, 
                    title=fig_title,
                    titlesize=14,
                    typad=.08,
                    TL_NOTE=False)    

    plt.subplots_adjust(hspace=.2, wspace=.05)

    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=.03)



def plot_position_density_panel2(experiment, cycle='24H', tbin_type=None, xbins=12, ybins=24, 
        err_type='sd', plot_type='position_density', ADD_SOURCE=True):

    E = experiment

    text = cycle if tbin_type is None else tbin_type
    string = E.get_days_to_use_text()

    print "%s, %s, xbins:%d, ybins:%d, %s" %(
            plot_position_density_panel2.__name__, text, xbins, ybins, E.use_days)

    dirname_out = E.figures_dir + '%s/panel2/xbins%d_ybins%d/%s/%s_days/' %(
                                    plot_type, xbins, ybins, text, E.use_days)
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

    # load data
    data, labels = E.generate_position_density(cycle=cycle, tbin_type=tbin_type, 
                        level='mouseday', xbins=xbins, ybins=ybins, err_type=err_type)
    new_data = data.swapaxes(0, 1)       
    # new_data = data_.reshape(data_.shape[0], data_.shape[1], -1)      # tbins, mousedays, xbins, ybins, (avg, err)
    
    # tbins
    arr = my_utils.get_CT_bins(bin_type=tbin_type) / 3600 -7     # CT in hours. num_tbins=arr.shape[0]
    tbins = ['CT%d-%d' %(row[0], row[1]) for row in arr]

    # nest
    rects_HB = np.array([None] * len(data))
    obs_rects = np.array([None] * len(data))
    
    condition = (xbins, ybins) == (2, 4)
    if condition:
        rects_HB, obs_rects = E.generate_homebase_data()

    for strain in range(E.num_strains):
        idx = labels[:, 0] == strain
        mouseNumbers = np.unique(labels[idx, 1])

        for b in xrange(new_data.shape[0]):
            bin_data =  new_data[b].reshape(len(mouseNumbers), len(E.daysToUse), ybins, xbins, 2)

            fig_title = '%s Experiment\n%s, %s\n%s days: %s\ngroup%d: %s, bin %d: %s' %(
                            E.short_name, 
                            plot_type.replace('_', ' ').title(), text, 
                            E.use_days.replace('_', ' ').upper(), string,
                            strain, E.strain_names[strain], b, tbins[b]
                            )

            fname = dirname_out + '%s_%s_group%d_xbins%d_ybins%d_tbin%d' %(
                                    plot_type, text, strain, xbins, ybins, b)
                            
            rect_HB, obs_rect = None, None
            if condition:
                idx_start, idx_end = my_utils.find_nonzero_runs(idx)[0]
                rect_HB = np.array(rects_HB[idx_start:idx_end]).reshape(len(mouseNumbers), len(E.daysToUse))
                # obs_rect = np.array(obs_rects[idx_start:idx_end]).reshape(len(mouseNumbers), len(E.daysToUse))
            
            if tbin_type is not None:
                draw_position_density_tbins2(E, bin_data, mouseNumbers, 
                                        tbin_type, err_type, 
                                        xbins, ybins, fig_title, fname,
                                        rect_HB=rect_HB, obs_rect=obs_rect,
                                        plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)


















# def draw_position_density(E, data, labels, cycle, level, err_type, xbins, ybins, fname,
#         rect_HB=None, obs_rect=None, plot_type='position_density', ADD_SOURCE=False):
#     stop
    # C = Cage()

    # # figure    
    # figsize, nrows, ncols = get_subplot_specs(E, num_subplots=data.shape[0], plot_type=plot_type) 

    # fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    
    # cmap = plt.get_cmap("viridis")
    # vmin, vmax = .0001, 1.
    # if (xbins, ybins) == (2, 4):
    #     vmin = 0.01
    # extent = [C.CMXLower, C.CMXUpper, C.CMYLower, C.CMYUpper]   

    # percent_time_color = E.fcolors['other'][0]

    # title, subtitles  = get_figure_titles(E, labels=labels, level=level, cycle=cycle, 
    #                                         err_type=err_type, plot_type=plot_type)

    # for c in xrange(nrows * ncols):
    #     try:
    #         ax = axes.flatten()[c] if type(axes) is np.ndarray else axes        # when just one axis
            

    #         Z3 = data[c, :, :, 0]       # plt average only for the moment
    #         if np.isnan(Z3).all():
    #             ax.text(.5, .5, subtitles[c] + '\nexcluded', 
    #                 fontsize=12, color='.5', ha='center', va='center')
    #             ax.axis('off')
            
    #         else:   
    #             Z3_ = Z3.copy()
    #             Z3_[Z3<1e-4] = 1e-4     # round small numbers to almost zero for plotting

    #             im = ax.imshow(Z3_, interpolation='nearest', cmap=cmap, 
    #                 norm=LogNorm(vmin=vmin, vmax=vmax))#, extent=extent)

    #             ax.set_title(subtitles[c])
    #             set_position_density_layout(fig, ax, im)
    #             set_colorbar(fig, ax, im)
                
    #             if (xbins, ybins) == (2, 4):
    #                 draw_percent_time(ax, Z3 / Z3.sum(), color=percent_time_color)            
    #                 if level == 'mouseday':
    #                     draw_homebase_star(ax, rect_HB[c], obs_rect[c], color=percent_time_color)

    #         # add some labeling
    #         if level == 'group':
    #             show_devices_labels(E, ax)

    #         elif level == 'mouseday':
    #             # show fast
    #             if E.short_name == '2CFast':
    #                 if hasattr(E, 'fastDayNumbers'):    
    #                     day = int(subtitles[c][1:])
    #                     if day in E.fastDayNumbers + E.reFeedDayNumbers:
    #                         text = 'FAST' if day in E.fastDayNumbers else'REFEED' 
    #                         ax.text(.15, 1.03, text, fontsize=14,
    #                                 color=E.fcolors['F'][0], 
    #                                 ha='right', va='bottom',
    #                                 transform=ax.transAxes)

    #         if c < 1:
    #             h, l = ax.get_legend_handles_labels()

    #         # if FLAG_IGNORED:
    #         #     mouseNumber, dayNumber = (labels[c, 1], None) if level=='mouse' else labels[c, 1:]
    #         #     is_ignored = E.get_mouse_object(mouseNumber, dayNumber).ignored
    #         #     if is_ignored:
    #         #         box = patches.Rectangle((0, 0), 1, 1,     # xy bottom left, w, h
    #         #                     color='r', alpha=.5, transform=ax.transAxes) 
    #         #         ax.add_patch(box)

    #     except IndexError:
    #         ax.axis('off')
    #         continue

    # set_legend(fig, h, l, xbins, ybins, 
    #             text_color=percent_time_color)

    # typad = .15 if level == 'group' else 0
    # tlxpad = -.12 if level == 'group' else -.05
    # add_titles_notes(E, fig, 
    #                         title=title,
    #                         typad=typad,
    #                         tlxpad=tlxpad, 
    #                         tlypad=typad)    

    # plt.subplots_adjust(hspace=.3, wspace=.4)

    # sypad = -.05 if level == 'group' else .05
    # save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=sypad)




def draw_position_density_tbins(E, data, labels, tbin_type, level, err_type, xbins, ybins, fname, 
        rect_HB=None, obs_rect=None, plot_type='position_density', ADD_SOURCE=False):

    C = Cage()

    # figure    
    figsize, nrows, ncols = get_subplot_specs(E, num_subplots=data.shape[0], 
                                                plot_type=plot_type, sub_type=tbin_type) 

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    
    cmap = plt.get_cmap("viridis")
    vmin, vmax = .0001, 1.
    if (xbins, ybins) == (2, 4):
        vmin = 0.01
    extent = [C.CMXLower, C.CMXUpper, C.CMYLower, C.CMYUpper]   

    percent_time_color = E.fcolors['other'][0]

    title, subtitles  = get_figure_titles(E, labels=labels, level=level, tbin_type=tbin_type, 
                                            err_type=err_type, plot_type=plot_type)
    

    data_ = data.swapaxes(0, 1)
    arr = my_utils.get_CT_bins(bin_type=tbin_type) / 3600 -7     # CT in hours. num_tbins=arr.shape[0]
    row_labels = ['CT%d-%d' %(row[0], row[1]) for row in arr]
    column_labels = subtitles
    
    
    for r in xrange(nrows):
        # row labels
        top, bottom, left, right = [getattr(fig.subplotpars, x) for x in ['top', 'bottom', 'left', 'right']]
        yy = top - .03 - (top-bottom) * r / nrows
        fig.text(left - .1, yy, row_labels[r], va='center', fontsize=8)

        for c in xrange(ncols):
            # column labels
            if r < 1:
                xx = left +.01 + (right-left) * c / ncols
                fig.text(xx, top+.03, column_labels[c], fontsize=8)                

            bin_data = data_[r, c, :, :]

            try:
                ax = axes[r, c] if type(axes) is np.ndarray else axes        # when just one axis

                Z3 = bin_data[:, :, 0]       # plt average only for the moment

                if np.isnan(Z3).all():
                    # ax.text(.5, .5, subtitles[r] + ' excluded', 
                    #     fontsize=12, color='.5', ha='center', va='center')
                    ax.axis('off')
                
                else:   
                    Z3_ = Z3.copy()
                    Z3_[Z3<1e-4] = 1e-4     # round small numbers to almost zero for plotting

                    im = ax.imshow(Z3_, interpolation='nearest', cmap=cmap, 
                        norm=LogNorm(vmin=vmin, vmax=vmax))#, extent=extent)

                    # ax.set_title(subtitles[c])
                    set_position_density_layout(fig, ax, im)
                    if (xbins, ybins) == (2, 4):
                        draw_homebase_star(ax, rect_HB[c], color=percent_time_color)

                if r*c < 1:
                    hh, ll = ax.get_legend_handles_labels()

            except IndexError:
                ax.axis('off')
                continue

    set_colorbar(fig, ax, im)
    set_legend(fig, hh, ll, xbins, ybins, 
                text_color=percent_time_color)

    typad = .15 #if level == 'group' else 0
    add_titles_notes(E, fig, 
                    title=title,
                    typad=typad,
                    titlesize=14,
                    TL_NOTE=False)    

    plt.subplots_adjust(hspace=.2, wspace=.05)

    sypad = -.05 if level == 'group' else .05

    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=sypad)


def plot_position_density_panel1(experiment, cycle='24H', tbin_type=None, level='mouseday',
        xbins=12, ybins=24, err_type='sd', plot_type='position_density', ADD_SOURCE=True):

    E = experiment

    text = cycle if tbin_type is None else tbin_type

    print "%s, %s, %s, xbins:%d, ybins:%d, %s" %(
            plot_position_density_panel1.__name__, text, level, xbins, ybins, E.use_days)

    dirname_out = E.figures_dir + '%s/panel1/xbins%d_ybins%d/%s/%s_days/' %(
                                    plot_type, xbins, ybins, text, E.use_days)
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

    # load data
    data, labels = E.generate_position_density(cycle=cycle, tbin_type=tbin_type, 
                        level=level, xbins=xbins, ybins=ybins, err_type=err_type)
    
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
                # obs_rect = np.array(obs_rects[idx_start:idx_end]).reshape(len(mouseNumbers), len(E.daysToUse))


            if tbin_type is not None:
                draw_position_density_tbins(E, md_data, md_labels, 
                                        tbin_type, level, err_type, 
                                        xbins, ybins, fname,
                                        rect_HB=rect_HB, obs_rect=obs_rect,
                                        plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)

            # else:
            #     draw_position_density(E, md_data, md_labels, 
            #                             cycle, level, err_type, 
            #                             xbins, ybins, fname,
            #                             rect_HB=rect_HB, obs_rect=obs_rect,
            #                             plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)









# # #old csv for two different days windows
# # # position density csv
# def write_to_csv1(experiment0, experiment1, cycle='24H', level='group', xbins=12, ybins=24, err_type='sd',  
#         plot_type='position_density'):

#     E0 = experiment0
#     E1 = experiment1
#     use_days0 = E0.use_days + '_days'
#     use_days1 = E1.use_days + '_days'

#     print "%s, %s, %s, xbins:%d, ybins:%d, %s-%s" %(
#             plot_position_density.__name__, cycle, level, 
#             xbins, ybins, E0.use_days, E1.use_days)

#     suffix = '%s/csv_files/xbins%d_ybins%d/%s/%s-%s_days/' %(plot_type, 
#                                 xbins, ybins, level, E0.use_days, E1.use_days)

#     dirname = os.path.join(E0.figures_dir, suffix)
#     if not os.path.isdir(dirname): os.makedirs(dirname)
#     fname1 = dirname + '%s_%s_%s_xbins%d_ybins%d.csv' %(
#                     plot_type, cycle, level, xbins, ybins)

#     # load data
#     data0, labels0 = E0.generate_position_density(cycle, level, 
#                                     xbins, ybins, err_type=err_type)
#     data1, labels1 = E1.generate_position_density(cycle, level, 
#                                     xbins, ybins, err_type=err_type)

    
#     new_data0 = data0[:,:,:,0].reshape(data0.shape[0], -1)     # (num_mousedays, 4x2 raveled)
#     new_data1 = data1[:,:,:,0].reshape(data1.shape[0], -1)     # (num_mousedays, 4x2 raveled)
    
#     # headers
#     # string = ', BIN_SHIFTED: %dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''
#     headers = [
#         ['Experiment: %s' %E0.short_name],
#         ['%s, xbins=%d, ybins=%d' %(plot_type, xbins, ybins)],
#         ['%s, %s' %(level, cycle,)], 
#         ['%s-%s days' %(E0.use_days, E1.use_days)],
#         ]
        

#     if level == 'group':
#         sub_header = ['use_days', 'group']
#         with open(fname1, 'wb') as csv_file:
#             writer = csv.writer(csv_file, delimiter=",")
#             for h in headers:
#                 writer.writerow(h)
#             writer.writerow('\n')
#             writer.writerow(sub_header)

#             c = 0
#             for row in new_data0:

#                 row_text = [use_days0, labels0[c]]
#                 writer.writerow(np.hstack([row_text, ['%1.4f' %r for r in row]]))
#                 c +=1
#             writer.writerow('\n')
            
#             c1 = 0
#             for row in new_data1:
#                 row_text = [use_days1, labels1[c1]]
#                 writer.writerow(np.hstack([row_text, ['%1.4f' %r for r in row]]))
#                 c1 +=1
            
#             writer.writerow('\n')


#     elif level == 'mouse':
#         sub_header = ['use_days', 'group', 'mouse'] 

#         with open(fname1, 'wb') as csv_file:
#             writer = csv.writer(csv_file, delimiter=",")
#             for h in headers:
#                 writer.writerow(h)
#             writer.writerow('\n')
#             writer.writerow(sub_header)
            
#             for group_num in range(E0.num_strains):
#                 idx_group0 = labels0[:, 0] == group_num
#                 idx_group1 = labels1[:, 0] == group_num
#                 group_data0 = new_data0[idx_group0]
#                 group_data1 = new_data1[idx_group1]
#                 group_labels0 = labels0[idx_group0]
#                 group_labels1 = labels1[idx_group1]

#                 c = 0
#                 for row in group_data0:

#                     row_text = [use_days0, group_labels0[c, 0], group_labels0[c, 1]]
#                     writer.writerow(np.hstack([row_text, ['%1.4f' %r for r in row]]))
#                     c +=1
                
#                 writer.writerow('\n')
#                 writer.writerow([use_days0, '', 'Mean:'] + ['%1.4f' %r for r in np.nanmean(group_data0, axis=0)])
#                 writer.writerow(['', '', 'sd:'] + ['%1.4f' %r for r in np.nanstd(group_data0, axis=0)])
#                 sem = np.nanstd(group_data0, axis=0) / np.sqrt(group_data0.shape[0]-1)
#                 writer.writerow(['', '', 'sem:'] + ['%1.4f' %r for r in sem])
#                 writer.writerow('\n')
                
#                 c1 = 0
#                 for row in group_data1:
#                     row_text = [use_days1, group_labels1[c1, 0], group_labels1[c1, 1]]
#                     writer.writerow(np.hstack([row_text, ['%1.4f' %r for r in row]]))
#                     c1 +=1
                
#                 writer.writerow('\n')
#                 writer.writerow([use_days1, '', 'Mean:'] + ['%1.4f' %r for r in np.nanmean(group_data1, axis=0)])
#                 writer.writerow(['', '', 'sd:'] + ['%1.4f' %r for r in np.nanstd(group_data1, axis=0)])
#                 sem = np.nanstd(group_data1, axis=0) / np.sqrt(group_data1.shape[0]-1)
#                 writer.writerow(['', '', 'sem:'] + ['%1.4f' %r for r in sem])
#                 writer.writerow('\n')


#     elif level == 'mouseday':
#         sub_header = ['', 'group', 'mouse', 'mouseday'] 

#         with open(fname1, 'wb') as csv_file:
#             writer = csv.writer(csv_file, delimiter=",")
#             for h in headers:
#                 writer.writerow(h)
#             writer.writerow('\n')
#             writer.writerow(sub_header)
            
#             for group_num in range(E0.num_strains):
#                 idx_group0 = labels0[:, 0] == group_num
#                 idx_group1 = labels1[:, 0] == group_num
#                 group_data0 = new_data0[idx_group0]
#                 group_data1 = new_data1[idx_group1]
#                 group_labels0 = labels0[idx_group0]
#                 group_labels1 = labels1[idx_group1]
                
#                 m_labels = np.unique(group_labels0[: ,1])

#                 for mouse in m_labels:
#                     idx_mouse0 = group_labels0[:, 1] == mouse
#                     idx_mouse1 = group_labels1[:, 1] == mouse
#                     m_data0 = group_data0[idx_mouse0]
#                     m_data1 = group_data1[idx_mouse1]
#                     m_labels0 = group_labels0[idx_mouse0]
#                     m_labels1 = group_labels1[idx_mouse1]

#                     c = 0
#                     for row in m_data0:

#                         row_text = [use_days0, m_labels0[c, 0], m_labels0[c, 1], m_labels0[c, 2]]
#                         writer.writerow(np.hstack([row_text, ['%1.4f' %r for r in row]]))
#                         c +=1
                    
#                     writer.writerow('\n')
#                     writer.writerow(['', '', '', 'Mean:'] + ['%1.4f' %r for r in np.nanmean(m_data0, axis=0)])
#                     writer.writerow(['', '', '', 'sd:'] + ['%1.4f' %r for r in np.nanstd(m_data0, axis=0)])
#                     sem = np.nanstd(m_data0, axis=0) / np.sqrt(m_data0.shape[0]-1)
#                     writer.writerow(['', '', '', 'sem:'] + ['%1.4f' %r for r in sem])
#                     writer.writerow('\n')
                    
#                     c1 = 0
#                     for row in m_data1:
#                         row_text = [use_days1, m_labels1[c1, 0], m_labels1[c1, 1], m_labels1[c1, 2]]
#                         writer.writerow(np.hstack([row_text, ['%1.4f' %r for r in row]]))
#                         c1 +=1
                    
#                     writer.writerow('\n')
#                     writer.writerow(['', '', '', 'Mean:'] + ['%1.4f' %r for r in np.nanmean(m_data1, axis=0)])
#                     writer.writerow(['', '', '', 'sd:'] + ['%1.4f' %r for r in np.nanstd(m_data1, axis=0)])
#                     sem = np.nanstd(m_data1, axis=0) / np.sqrt(m_data1.shape[0]-1)
#                     writer.writerow(['', '', '', 'sem:'] + ['%1.4f' %r for r in sem])
#                     writer.writerow('\n')
                         

#     print "csv files saved to:\n%s" % fname1

