import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec

from cage import Cage
import plotting_utils
import my_utils 
import os
# import time


"""
G.A.Onnis, 04.2016
update: 09.2016
revised: 11.2016

UCSF Tecott Lab+
"""


def plot_xy(ax, MD, CT_window):

    varNames = ['CT', 'CX', 'CY', 'velocity', 'MB_idx']
    for var in varNames:
        if not hasattr(MD, var):
            MD.load(var) 
    
    T, X, Y, vel, MB_idx = [getattr(MD, var) for var in varNames] 
    C = Cage()
    MBVT, MBDT = [getattr(MD.experiment, x) for x in ['MBVT', 'MBDT']]

    # select window
    idx_start = np.searchsorted(T, CT_window[0]) 
    idx_end = np.searchsorted(T, CT_window[1], side='right') 
    # plot distance to W
    wdist = np.sqrt((X[idx_start : idx_end] - C.xy_o[0]) ** 2 + \
                    (Y[idx_start : idx_end] - C.xy_o[1]) ** 2)
    ax.plot(T[idx_start : idx_end], wdist, label='distance',
        marker='x', lw=1, color='k', ms=5)  
    # velocity plot
    ax2 = ax.twinx()
    ax2.plot(T[idx_start : idx_end], vel[idx_start : idx_end], 
        marker='o', lw=0.5, color='0.5', ms=3, label='velocity')
    # plot MBVT threshold
    ax2.axhline(MBVT, c='.5')
    set_xy_plot_layout(ax, ax2, CT_window)



def plot_activity(ax, MD, CT_window, tstep=30):
    """plots events below distance plot
    """
    varNames = [
        'at_HB_Sets', 'at_F_Sets', 'at_W_Sets', 
        'MB_Sets', 
        'CT_out_HB', 'CT_at_HB', 
        'FB_Sets', 'WB_Sets', 
        'F_Sets', 'W_Sets', 
        'AS_Sets',
        ]
    offsets = [
        10, 10, 10, 
        7, 
        6, 6,
        4, 4,
        2.5, 2.5,
        0.5
        ]
    heights = [
        0.2, 0.2, 0.2,
        0.4, 
        0, 0,
        0.4, 0.4, 
        0.8, 0.8, 
        0.8,
        ]
    color_tup = [
            ('M', 2), ('F', 1), ('W', 1), 
            ('M', 0), 
            ('M', 0), ('M', 2),
            ('F', 0), ('W', 0), 
            ('F', 0), ('W', 0),
            ('AS', 0),
            ]          

    colors = [MD.experiment.fcolors[key][num] for (key, num) in color_tup]
    markers = ['o', 's', 'p', 'v', '^', 'd', '*', 'h', '<', '>', 'D', 'H', '8'] * 4
            
    for v, name in enumerate(varNames):
        if not hasattr(MD, name):
            MD.load(name)
        var = getattr(MD, name) 
        idx_start = np.searchsorted(var.ravel(), CT_window[0]) // var.ndim
        idx_end = np.searchsorted(var.ravel(), CT_window[1], side='right') // var.ndim + 1
        offset, height, color = offsets[v], heights[v], colors[v]
        
        if var.ndim == 1:    # 'CT_out_HB', 'CT_at_HB'
            ax.scatter(var[idx_start: idx_end], 
                offset * np.ones(var[idx_start: idx_end].shape[0]),
                c=color, marker='|', s=25, lw=0.5, edgecolors=None)
        else:            
            cnt = 0
            for x in var[idx_start:idx_end]:
                var_patch = patches.Rectangle((x[0], offset), x[1]-x[0], height,      # xy lower left corner, width, height
                    fc=color, ec=color, lw=0.001)            
                ax.add_patch(var_patch) 
                
                if name == 'MB_Sets':       # draw bout start_stop on raster
                    colors_sq = ['k', 'r']
                    for c1 in range(2):
                        ax.plot(x[c1], offset+1.5, marker=markers[cnt], ms=6, 
                            mfc=colors_sq[c1], mec=colors_sq[c1])
                cnt += 1

    set_activity_layout(ax, CT_window)


def plot_trajectory(ax, MD, CT_window, NEST=True):

    varNames = ['CT', 'CX', 'CY']
    for varName in varNames:
        if not hasattr(MD, varName):
            MD.load(varName) 

    T, X, Y = [getattr(MD, var) for var in varNames]
    # select window
    win_idx = my_utils.get_window_CT_idx(T, CT_window)

    ax.plot(X[win_idx], Y[win_idx], lw=0.2, 
        color='0.3', marker='x', ms=2)

    set_trajectory_layout(ax)
    if NEST:
        display_HB_cell(ax, MD)


def plot_v_field(ax, MD, CT_window):

    varNames = ['CT', 'CX', 'CY', 
        'velocity', 'angle']

    for varName in varNames:
        if not hasattr(MD, varName):
            MD.load(varName) 

    T, X, Y, vel, ang = [getattr(MD, var) for var in varNames]
    # select window
    win_idx = my_utils.get_window_CT_idx(T, CT_window)
    x, y, V, alpha = X[win_idx], Y[win_idx], vel[win_idx], ang[win_idx] 
    x[x == 0] = np.nan
    y[y == 0] = np.nan
    Vx = V * np.sqrt(2) / 2#* np.cos(alpha)
    Vy = V * np.sqrt(2) / 2#* np.sin(alpha)
    Q = ax.quiver(x, y, Vx, Vy, color='.5', 
        # scale_units='y',
        scale_units='xy', scale=5, 
        # angles='xy',
        headwidth=5, headlength=7, clip_on=False)

    qk = ax.quiverkey(Q, 1.2, 0, 10, '10 cm/s', 
        labelpos='N', fontproperties={'size': 8})


def plot_bout_trajectory(ax, MD, CT_window, DRAW_CIRCLE=False):

    varNames = ['CT', 'CX', 'CY', 'MB_idx', 'MB_Sets'] 
        # 'idx_out_HB','MB_idx',]
    for varName in varNames:
        if not hasattr(MD, varName):
            MD.load(varName) 

    T, X, Y, MB_idx, MB_Sets = [getattr(MD, var) for var in varNames]

    # idx_start1 = np.searchsorted(MB_Sets.ravel(), CT_window[0]) // MB_Sets.ndim
    # idx_end1 = np.searchsorted(MB_Sets.ravel(), CT_window[1], side='right') // MB_Sets.ndim + 1

    idx_start = np.min([np.searchsorted(MB_Sets[:, b], CT_window[0]) for b in range(2)])
    idx_end = np.max([np.searchsorted(MB_Sets[:, b], CT_window[1]) for b in range(2)])

    colors_sq = ['k', 'r']
    markers = ['o', 's', 'p', 'v', '^', 'd', '*', 'h', '<', '>', 'D', 'H', '8'] * 4
    cnt = 0
    for start, end in MB_Sets[idx_start : idx_end]:
        idx1, idx2 = [np.searchsorted(T, b) for b in [start, end]]
        x, y = X[idx1 : idx2+1], Y[idx1 : idx2+1]
        x[x == 0], y[y == 0] = np.nan, np.nan
        ax.plot(x, y, lw=2, marker=None, color=MD.experiment.fcolors['M'][1],   # dark green
                alpha=0.6, clip_on=False)  
                  
        # draw bout start_stop on trajectory
        c = 0
        for m in [idx1, idx2]: 
            ax.plot(X[m], Y[m], marker=markers[cnt], ms=6, mfc=colors_sq[c], 
                mec=colors_sq[c], mew=0.75, clip_on=False, zorder=60, alpha=0.7)
            c +=1
        # if DRAW_CIRCLE:     # draw circles around bout start_stop
        #     c1 = 0
        #     for m in [idx_start, idx_end]:
        #         circ = patches.Circle((X[m], Y[m]), 5, color=colors_sq[c], fc='none', alpha=0.7)
        #         ax.add_patch(circ)
        #         c1 += 1
        cnt += 1


# # # FIGURE and LAYOUT
def create_figure():                 
    figsize = (16, 6)
    gs1 = gridspec.GridSpec(2, 2, width_ratios=[4, 1], height_ratios=[4, 1])
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(gs1[0, 0])       # distance raster
    ax3 = fig.add_subplot(gs1[1, 0])
    ax4 = fig.add_subplot(gs1[:, 1])
    return gs1, fig, ax, ax3, ax4


def set_xy_plot_layout(ax, ax2, CT_window, tstep=15):
    # distance
    ax.set_xlim(CT_window)
    ax.set_ylim([0, 45])
    yticks = range(0, 41, 5)
    ax.set_xticks([])
    ax.set_yticks(yticks)
    ax.spines['top'].set_visible(False)  
    ax.spines['left'].set_visible(False)   
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_position(('axes', -0.01))

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.tick_params(axis='y', which='major', direction='out')
    ax.set_ylabel('Distance from W [cm]', labelpad=10)

    # velocity 
    ylim = 121
    ylims = (0, ylim)
    # yticks2 = range(0, 120, 10)
    yticks2 = range(0, ylim, 10)
    ax2.set_ylim(ylims)
    ax2.set_yticks(yticks2)
    ax2.spines['top'].set_visible(False)  
    ax2.spines['left'].set_visible(False)      
    ax2.spines['right'].set_visible(False)     
    ax2.spines['right'].set_position(('axes', 1.01))

    ax2.yaxis.label.set_color('.5')
    ax2.set_ylabel('Velocity [cm/s]', rotation=270, labelpad=10)
    ax2.tick_params(axis='y', which='major', colors='.5', direction='out')


def set_activity_layout(ax, CT_window, step=15):

    ax.set_xlim(CT_window)
    ax.set_ylim(0, 11)
    if np.diff(CT_window) <=15:
        step = 30
    elif np.diff(CT_window) > 15 and np.diff(CT_window) <=30:
        step = 15
    elif np.diff(CT_window) > 30 and np.diff(CT_window) <=60:
        step = 12

    xarr = np.linspace(CT_window[0], CT_window[1], step + 1)
    h, m, s = my_utils.convert_CT_time_to_hms_tuple(xarr)
    xticks = xarr
    xticklabels = ["%d:%02d:%02d" %x for x in zip(h, m, s)]  
    
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_yticks([])
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(axis='x', which='major', labelsize=9, direction='out')
    ax.set_xlabel('Circadian Time [h:m:s]', labelpad=5)
    # text labels
    # ysl = [10, 9, 8, 5.5, 4, 2, 0.1]
    ysl = [10, 8, 7, 6, 4, 3, 1]
    labels = ['at HB/feeder/water', 'M bout start/end', 'M bouts', 'M events', 'F/W bouts', 'F/W events', 'active/inactive']
    for i in xrange(len(ysl)):
        ax.text(ax.get_xlim()[0]-1, ysl[i], labels[i], 
            fontsize=7, ha='right', va='center', clip_on=False
            )


def set_trajectory_layout(ax, SCALE=True):
    if SCALE:
        # display distance scale
        ax.plot([6, 12], [4, 4], color='k', clip_on=False)
        ax.text(7, 4.8, '5 cm', fontsize=8, clip_on=False)

    C = Cage()
    ax.set_xlim([C.CMXLower, C.CMXUpper])
    ax.set_ylim([C.CMYLower, C.CMYUpper])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_aspect('equal')
    plotting_utils.draw_device_labels(ax)
    plotting_utils.draw_xbins_ybins_cage_grid(ax)


def display_HB_cell(ax, MD):
    varNames = ['rect_HB', 'obs_rect']
    for var in varNames:
        if not hasattr(MD, var):
            MD.load(var)

    rect_HB, obs_rect = [getattr(MD, var) for var in varNames]
    C = Cage()
    color = MD.experiment.fcolors['M'][2]
    for rect in rect_HB:
        xy, w, h = C.map_rect4x2_to_cage_coordinates(rect)
        niche = patches.Rectangle(xy, w, h, fc=color, ec='0.85', alpha=0.5, zorder=0)
        ax.add_patch(niche)


def add_text_final(gs1, fig, MD, strain_name):
    title = '%s, M%d, day%d' %(strain_name, MD.mouseNumber, MD.dayNumber)
    title2 = 'IST=%1.1fm, FBT=%1.1fs, WBT=%1.1fs\nMBVT=%1.1fcm/s, MBDT=%1.1fcm' %(MD.experiment.IST / 60., 
        MD.experiment.FBT, MD.experiment.WBT, MD.experiment.MBVT, MD.experiment.MBDT)
    fig.text(0.03, 0.95, title, ha='left')
    fig.text(0.03, 0.9, title2, ha='left', fontsize=8)
    gs1.update(left=0.09, right=0.93, hspace=0.05)#, wspace=0.7)



# # # run stuff
def visualize(experiment, mouse, MD, CT_window=(68400, 68430), BOUT_TRAJ=False, V_FIELD=False, DRAW_CIRCLE=False):

    E = experiment
    IST = getattr(E, 'IST') / 60.
    params = ['FBT', 'WBT', 'MBVT', 'MBDT']
    FBT, WBT, MBVT, MBDT = [getattr(E, x) for x in params]
    
    dirname_out = E.plots_dir + 'bouts/raster_check/' 
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
    
    strain_name = mouse.groupName
    if not mouse.ignored:
        if MD.dayNumber in E.daysToUse and not MD.ignored:
            gs1, fig, ax, ax3, ax4 = create_figure()
            # subplot 1
            plot_xy(ax, MD, CT_window)
            plot_activity(ax3, MD, CT_window)
            # subplot2
            plot_trajectory(ax4, MD, CT_window)
            if BOUT_TRAJ:
                plot_bout_trajectory(ax4, MD, CT_window, DRAW_CIRCLE=DRAW_CIRCLE)
            if V_FIELD:
                plot_v_field(ax4, MD, CT_window)
            add_text_final(gs1, fig, MD, strain_name)

            # save
            id_string = "s%d_M%d" %(MD.groupNumber, MD.mouseNumber)
            dirname_out2 = dirname_out + id_string + '/'
            if not os.path.isdir(dirname_out2): os.makedirs(dirname_out2)
            t1 = "%02d_%02d_%02d" %my_utils.convert_CT_time_to_hms_tuple(CT_window[0])
            t2 = "%02d_%02d_%02d" %my_utils.convert_CT_time_to_hms_tuple(CT_window[1])
            fname = dirname_out2 + "day%d_h%s_to_h%s.pdf" %(MD.dayNumber, t1, t2)
            fig.savefig(fname)
            print "saved to: %s" %fname
            plt.close()
        else:
            print "mouseday ignored"
    else:
        print "mouse ignored"



def run(experiment, mouseNumber=2101, day=5, t_start=(12,0,0), t_end=(12,1,0), tstep=30, GENERATE=False, PRINT_AS=True, BOUT_TRAJ=True, V_FIELD=True, DRAW_CIRCLE=False):

    E = experiment
    mouse = E.get_mouse_object(mouseNumber=mouseNumber)
    MD = mouse.mouse_days[day-1]

    CT_start = my_utils.convert_hms_tuple_to_CT_time(t_start)
    CT_end = my_utils.convert_hms_tuple_to_CT_time(t_end)
    CT_window_list = [(x, x + tstep) for x in np.arange(CT_start, CT_end, tstep)]
    print "plotting bout visualizations check, mouseNumber %d, day %d, CT time [%s, %s].." %(
        mouseNumber, day, t_start, t_end)
    if GENERATE:
        E.generate_binaries(mouseNumber, day)
        E.generate_bouts(mouseNumber, day)
        E.generate_active_states(mouseNumber, day)
        
    for window in CT_window_list:
        visualize(E, mouse, MD, CT_window=window, BOUT_TRAJ=BOUT_TRAJ, V_FIELD=V_FIELD, DRAW_CIRCLE=DRAW_CIRCLE) 

    if PRINT_AS:
        MD.print_active_states()

    # MD.load("AS_Sets")
    # AS = getattr(MD, 'AS_Sets')
    # DC_on = (12 + 7) * 3600
    # DC_off = (24 + 7) * 3600 
    # idx_DC_on = np.searchsorted(AS.ravel(), DC_on) // 2
    # idx_DC_off = np.searchsorted(AS.ravel(), DC_off) // 2
    # arr_converted = my_utils.convert_CT_times_arr2d_to_hms(getattr(MD, 'AS_Sets'))



