import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import os

from ceppa.util import my_utils
from ceppa.util.intervals import Intervals
from ceppa.visualizations.plotting_utils import add_titles_notes, plot_colored_background, save_plot
from ceppa.visualizations.plotting_utils import show_fast_times, remove_axes_not_used, ax_cleanup
from ceppa.visualizations.raster_mouseday import add_DC_rectangle_to_raster


"""
G.Onnis, 03.2016
    updated: 06.2017

Tecott Lab UCSF
"""


def set_raster_layout(fig, ax, num_days, bin_type='12bins', SHIFT=False, tshift=0):
    """
    """
    y_low = -10. * num_days
    xlims = [4, 32]
    ylims = [y_low, 5]
    
    xticks, xlabels = my_utils.get_CT_ticks_labels(bin_type, SHIFT, tshift)

    # if bin_type == '24bins':
    #     xlabels[1::2] = ['' for i in range(len(xlabels)/2)] 

    ax.set_xlim(xlims)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)    
    ax.xaxis.set_ticks_position('top')
    ax.set_ylim(ylims)
    ax.set_yticks([])
    
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(True)
    ax.spines['top'].set_linewidth(0.5) 

    ax.tick_params(axis='x', direction='in', pad=2, labelsize=8) 
    


def show_days(MD, ax, y_offset, labelsize=8):

    E = MD.experiment
    text = 'D%d' %MD.dayNumber 
    color = '.3'

    if E.short_name in ['2CFast', 'ZeroLight']:
        if hasattr(E, 'fastDayNumbers'):
            color = E.fcolors['F'][0]
            if hasattr(E, 'reFeedDayNumbers'):
                if MD.dayNumber in E.fastDayNumbers + E.reFeedDayNumbers:
                    if MD.dayNumber in E.fastDayNumbers:
                        text = 'FAST D%d' %MD.dayNumber
                    elif MD.dayNumber in E.reFeedDayNumbers:
                        text = 'REFEED D%d' %MD.dayNumber 
            else:
                if MD.dayNumber in E.fastDayNumbers:
                    if MD.dayNumber in E.fastDayNumbers:
                        text = 'FAST D%d' %MD.dayNumber

    ax.text(3.5, y_offset - 2.1, text, fontsize=labelsize, 
                color=color, ha='right', va='center')


def get_settings_and_annotations(MD, y_offset):
    varNames = [
        'IS_timeSet', 'AS_timeSet', 
        'MB_timeSet', 
        'FB_timeSet', 'WB_timeSet'
        ]
    color_tup = [
            ('IS', 0), ('AS', 0),
            ('M', 1), 
            ('F', 0), ('W', 0),
            ]          
    colors = [MD.experiment.fcolors[key][num] for (key, num) in color_tup]
    offsets = [(y_offset - x) for x in [2.1, 3, 5, 7, 9]]
    heights = [0.4, 2.4, 1, 1, 1]
    return varNames, colors, offsets, heights


def plot_events(MD, fig, ax, y_offset):

    varNames, colors, offsets, heights = \
            get_settings_and_annotations(MD, y_offset)    
    c = 0    
    for name in varNames: 

        events = MD.load(name) / 3600. - 7
        color, offset, height = colors[c], offsets[c], heights[c]
        
        for x in events:                
            event_patch = patches.Rectangle((x[0], offset), x[1]-x[0], height,      
                            lw=0.001, fc=color, ec=color)   
            ax.add_patch(event_patch)

        c += 1


def plot_raster_groups(E, group_list, bin_type='12bins', SHOW_DAYS=True, 
        plot_type='raster', ADD_SOURCE=True):
    """ does not plot ignored mice/mousedays
    """
    dirname_out = E.figures_dir + '%ss/%s/group/%s_days/' %(plot_type, bin_type, E.use_days)
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
    
    print "%s, %s days.." %(plot_raster_groups.__name__, E.use_days)

    y_sep = 10  
    for strain in group_list:
        group = E.get_group_object(groupNumber=strain)

        num_mice = len(group.count_mice()[0])    # mice ok
        if num_mice > 12 and num_mice <=16:
            nrows, ncols = (4,4) 
        elif num_mice > 8 and num_mice <=12:
            nrows, ncols = (3, 4)
            figsize = (12.8, 6.4)
          
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)

        m = 0       # mouse counter
        for mouse in group.individuals:
            
            ax = axes.flatten()[m]

            if mouse.ignored:
                print mouse, 'excluded'
                ax.text(.5, .6, 'M%d\nexcluded' %mouse.mouseNumber, 
                    fontsize=12, color='.5', ha='center', va='center')
                ax.axis('off')

            else:

                cnt = 0
                for MD in mouse.mouse_days:
                    if MD.dayNumber in E.daysToUse: 

                        y_offset = y_sep * (-cnt)
                        
                        if MD.ignored:
                            print MD, 'excluded'
                            ax.text(18, y_offset-5, 'D%d excluded' %MD.dayNumber, 
                                    fontsize=8, color='.5', ha='center', va='center')
                            ax.axis('off')

                        else:
                            print MD
                            plot_events(MD, fig, ax, y_offset)

                            if SHOW_DAYS:
                                if m%4 == 0:
                                    show_days(MD, ax, y_offset, 
                                                labelsize=8)

                        cnt += 1
                
                # subtitle
                ax.set_title('M%d' %mouse.mouseNumber, y=1.1, fontsize=10)
                set_raster_layout(fig, ax, num_days=len(E.daysToUse)), 
                add_DC_rectangle_to_raster(ax, ypos=5, height=1.5)

            m += 1

        remove_axes_not_used(group, axes, nrows, ncols, m)

        add_titles_notes(E, fig, title=group.get_figtitle())

        plt.subplots_adjust(hspace=0.4)
        
        print "saving.."
        fname = dirname_out + '%s_group%d' %(plot_type, group.number)
        save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=.03)
        






# def plot_raster_mouse(E, mouse, bin_type='12bins', SHOW_DAYS=False, 
#         plot_type='rasters', ADD_SOURCE=True):
#     """ 
#     """ 
    
#     figsize, _, _ = get_subplot_specs(E, num_subplots=1, plot_type=plot_type) 
#     fig, ax = plt.subplots(figsize=figsize)

#     other_color = E.fcolors['other'][0]

#     y_sep = 10  
#     cnt = 0
#     for MD in mouse.mouse_days:
#         if MD.dayNumber in E.daysToUse:

#             y_offset = y_sep * (-cnt)
            
#             if not MD.ignored:
#                 print MD
#                 plot_events(MD, fig, ax, y_offset)                

#                 # begin / end fast
#                 if E.short_name == '2CFast':
#                     if hasattr(E, 'fastDayNumbers'):
#                         if MD.dayNumber in E.fastDayNumbers + E.reFeedDayNumbers:  
#                             ymin = 1. - (1.+cnt)/len(E.daysToUse) -.015      # fractions of axis
#                             ymax = 1. - 1.*cnt/len(E.daysToUse) -.015                    
#                             show_fast_times(E, ax, ymin=ymin, ymax=ymax, 
#                                             day_num=MD.dayNumber, color=other_color)
                
#                 if SHOW_DAYS:
#                     show_days(MD, ax, y_offset)

#             else:
#                 print MD, 'excluded'
#                 ax.text(18, y_offset-4, 'D%d excluded' %MD.dayNumber, 
#                         color='.5', ha='center', va='center')
#                 ax.axis('off')

#             cnt += 1   
   
#     set_raster_layout(fig, ax, num_days=len(E.daysToUse)) 
#     add_DC_rectangle_to_raster(ax, ypos=2, height=3)

#     add_titles_notes(E, fig, 
#                         title = mouse.get_figtitle(),
#                         tl_note2='showing bouts')       

#     print "saving.."
#     dirname_out = E.figures_dir + '%ss/%s/mouse/%s_days/' %(plot_type, bin_type, E.use_days)
#     if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
    
#     fname = dirname_out + '%s_group%d_M%d' %(
#                             plot_type, mouse.groupNumber, mouse.mouseNumber)
    
#     save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=.03)


# def plot_rasters_mice(E, group=None, mouseNumber=None, bin_type='12bins', SHOW_DAYS=True, 
#         plot_type='raster', ADD_SOURCE=True):
    
#     if group is None:      # plot individual mouse
#         print "%s, M%d, %s days.." %(plot_rasters_mice.__name__, mouseNumber, E.use_days)
#         mouse = E.get_mouse_object(mouseNumber)
#         plot_raster_mouse(E, mouse, bin_type=bin_type, SHOW_DAYS=SHOW_DAYS, 
#                             plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)
    
#     else:      # plot this group
#         group = E.groups[group]
#         print "%s, group%d, %s days.." %(plot_rasters_mice.__name__, group.number, E.use_days)
#         for mouse in group.individuals:
#             plot_raster_mouse(E, mouse, bin_type=bin_type, SHOW_DAYS=SHOW_DAYS, 
#                                 plot_type=plot_type, ADD_SOURCE=ADD_SOURCE)





# # # # # # # 
def plot_HCM_system_time(E, ttype='maintenance', ADD_SOURCE=True):
    """plots system_on_off 
    """
    if ttype == 'maintenance':
        HCM_time, labels = E.get_HCM_maintenance_time() 
        xlims = [2, 8]
        xticks = range(2, 10+1, 2)
        xticklabels = xticks

    elif ttype == 'recording':
        HCM_time, labels = E.get_HCM_recording_time() 
        xlims = [2, 34]
        xticks = range(4, 32+1, 4)
        xticklabels = [str(x) for x in range(4, 24+1, 4)] \
                    + [str(x) for x in range(4, 10+1, 4)]
        
    print "%s, %s days.." %(plot_HCM_system_time.__name__, E.use_days)

    figsize, nrows, ncols, sharex, sharey = \
            get_subplot_specs(E, num_subplots=len(E.groups), plot_type='subplot')
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=sharex, sharey=sharey)

    for strain in range(nrows * ncols):
        ax = axes.flatten()[strain] if type(axes) == np.ndarray else axes
        idx = labels [:, 0] == strain
        data = HCM_time[idx] / 3600. - 7
        c = 0
        for row in data:
            ax.plot([row[0], row[1]], [c, c], lw=0.5, color='0.5')
            c += 1

        ax.set_xlim(xlims)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
        
        if ttype == 'maintenance':
            text = 'avg:\n%1.1fmin' %(np.diff(data).mean() * 60)
        
        elif ttype == 'recording':
            text = 'avg:\n%1.2fhrs' %np.diff(data).mean()
            ax.axvline(x=12, linestyle='--', color='k')
            ax.axvline(x=24, linestyle='--', color='k')

        ax.text(.9, .9, text, fontsize=10, 
                ha='center', transform=ax.transAxes)  
        

        ax.set_xlabel('Circadian Time')
        ax.set_ylabel('Obs. days', labelpad=10)
        ax.set_title('group%d: %s' %(strain, E.strain_names[strain]), y=1.05)  

        ax_cleanup(ax, labelsize=10)


    title = '%sExp\n%s days\nDaily %s Time' %(
                E.short_name, E.use_days.replace('_', '-').title(), ttype.title())
    add_titles_notes(E, fig, 
                    title=title,
                    typad=.18,
                    tlxpad=-.1,
                    tlypad=.15,
                    HP_TEXT=False)

    plt.subplots_adjust(wspace=0.4)
    
    # save
    dirname_out = E.figures_dir + 'HCM_recording_time/%s_days/' %E.use_days
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
    fname = dirname_out + 'HCMsystem_%s_time_%s_days' %(ttype, E.use_days)
    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE, sypad=-.1)        



