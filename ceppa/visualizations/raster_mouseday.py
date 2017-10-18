import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import os

from ceppa.util import my_utils
from ceppa.util.intervals import Intervals
from ceppa.visualizations.plotting_utils import add_titles_notes, plot_colored_background
from ceppa.visualizations.plotting_utils import show_fast_times, save_plot


"""
G.Onnis, 10.2016
    updated: 06.2017

Tecott Lab UCSF
"""


            

def set_raster_layout(fig, ax, num_days, bin_type='12bins', SHIFT=False, tshift=0,
        labelsize=8, SHOWBINS=True):
    """
    """
    y_low = -10. * num_days
    xlims = [4, 32]

    ylims = [-7, 0]
    
    xticks, xlabels = my_utils.get_CT_ticks_labels(bin_type='12bins', 
                    SHIFT=SHIFT, tshift=tshift, CUT=False)

    # if bin_type == '24bins':
    #     xlabels[1::2] = ['' for i in range(len(xlabels)/2)] 
    
    if SHOWBINS:       # vertical lines at bin edges
        for x in xticks:
            ax.axvline(x=x, color='.3', linestyle='-', lw=.5, zorder=0)

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

    ax.tick_params(axis='x', direction='in', pad=2, labelsize=labelsize) 
    


def add_DC_rectangle_to_raster(ax, ypos=-1, height=1):
    """ draws DC_LC rectangle as a background
    """
    patch1 = ax.add_patch(patches.Rectangle((6, ypos), 6, height, 
        linewidth=0.5, facecolor='w', edgecolor='k'))
    patch2 = ax.add_patch(patches.Rectangle((12, ypos), 12, height, 
        linewidth=0.5, facecolor='0.7'))
    patch3 = ax.add_patch(patches.Rectangle((24, ypos), 6, height, 
        linewidth=0.5, facecolor='w', edgecolor='k'))
    patch1.set_clip_on(False)
    patch2.set_clip_on(False)
    patch3.set_clip_on(False)
    

def print_duration(ax, events, offset, name, color):
    """
    """
    for c, x in enumerate(events):
        xpos = x[0]+(x[1]-x[0])/2.
        if name == 'AS_timeSet':
            ypos = offset + .9
            mins, sec = (x[1]-x[0])*3600. // 60, (x[1]-x[0])*3600. % 60
            ax.text(xpos, ypos, '%d\'\n%d\'\'' %(mins, sec), ha='center', fontsize=8)
        else:   
            ytop, yspace = 0.55, 0.015
            numcol = 7
            if name == 'WB_timeSet': 
                ytop = 0.45
            elif name == 'MB_timeSet':
                ytop = 0.65
                numcol = 20
            ypos = offset + ytop - yspace * (c%numcol)
            sec = (x[1]-x[0])*3600.
            ax.text(xpos, ypos, '%d' %sec, color=color, fontsize=0.5)


def get_settings_and_annotations(MD):
    """
    """
    E = MD.experiment
    varNames = [
        'IS_timeSet', 'AS_timeSet', 
        'MB_timeSet',
        'CT_out_HB', 'CT_at_HB',
        'at_HB_timeSet', 'at_F_timeSet', 'at_W_timeSet',
        'FB_timeSet', 'WB_timeSet',
        'F_timeSet', 'W_timeSet',
        ]
    color_tup = [
            ('IS', 0), ('AS', 0),
            ('M', 1), 
            ('M', 0), ('M', 2), 
            ('M', 2), ('F', 1), ('W', 1),
            ('F', 0), ('W', 0), 
            ('F', 2), ('W', 2),
            ]          
    colors = [E.fcolors[key][num] for (key, num) in color_tup]
    y_offset = 0
    offsets = [(y_offset - x) for x in [
        1.7, 2, 
        2.8, 
        3.2, 3.2,
        4., 4.25, 4.5,  
        5.2, 5.2, 
        5.8, 5.8]
        ]
    label_offsets = [(y_offset - x) for x in [
        1.5, 1.8, 
        2.7,           
        3.1, 3.4,
        3.9, 4.2, 4.5,  
        4.9, 5.2, 
        5.5, 5.8]
        ]
    heights = [
        0.1, 0.7, 
        0.25, 
        0, 0,
        0.1, 0.1, 0.1,
        0.25, 0.25, 
        0.4, 0.4,
        ]
    labels = [
        'Inactive', 'vs. Active',
        'Move bouts',
        'Move events outside', 'vs. at HomeBase', 
        'Position at HomeBase', 'at Feeder', 'at Lickometer',
        'Feeding bouts', 'Drinking bouts',
        'Feeding events', 'Drinking events', 
        ]

    return varNames, colors, offsets, heights, labels, label_offsets


def plot_events(MD, fname, plot_type, bin_type='12bins', FLAG_IGNORED=False):
    
    E = MD.experiment
    
    varNames, colors, offsets, heights, labels, label_offsets = \
                                                get_settings_and_annotations(MD)
    
    figsize = (12., 3.6)
    fig, ax = plt.subplots(figsize=figsize)

    other_color = E.fcolors['other'][0]

    c = 0    
    for tup in zip(varNames, colors, offsets, heights, labels, label_offsets): 

        name, color, offset, height, label, label_offset = tup

        events = MD.load(name) / 3600. - 7            # why here did I use -6.5 ??
        if name in ['CT_out_HB', 'CT_at_HB']:
            ax.scatter(events, offset * np.ones(events.shape[0]), 
                c=color, marker='|', s=150, lw=0.01, edgecolor=None)
        else:
            for x in events:                
                event_patch = patches.Rectangle(
                    (x[0], offset), x[1]-x[0], height,      # xy lower left corner, width, height
                    lw=0.001, fc=color, ec=color)   
                ax.add_patch(event_patch)
            
            if name in ['AS_timeSet', 'FB_timeSet', 'WB_timeSet', 'MB_timeSet']:
                print_duration(ax, events, offset, name, color)
        
        
        ax.text(4.5, label_offset, label, color=color,
            ha='right', va='center', fontsize=8, clip_on=False)

    set_raster_layout(fig, ax, num_days=len(E.daysToUse), bin_type=bin_type, 
        SHIFT=E.BIN_SHIFT, tshift=E.binTimeShift)   

    add_DC_rectangle_to_raster(ax, ypos=-.3, height=.3)
    
    add_titles_notes(E, fig,
        title=MD.get_figtitle() + ', %s' %bin_type,
        TL_NOTE=True, 
        )

    if MD.ignored:
        fig.text(.3, 1.02, 'MD excluded', 
            fontsize=18,
            color='.5', 
            ha='right', va='bottom',
            transform=ax.transAxes)

    # begin/end fast
    if E.short_name == '2CFast':
        if MD.dayNumber in E.fastDayNumbers + E.reFeedDayNumbers:   
            text = '"FAST"' if MD.dayNumber in E.fastDayNumbers else '"REFEED"' 
            fig.text(.15, 1.05, text, fontsize=18,
                    color=other_color, 
                    ha='left', va='bottom',
                    transform=ax.transAxes)

            show_fast_times(E, ax, day_num=MD.dayNumber, 
                                TEXT=True, color=other_color)

    print "saving.."
    save_plot(fname, fig, ADD_SOURCE=True)

    # if FLAG_IGNORED and MD.ignored:     # tbc
    #     stop
    #     MD.flag_errors()
    #     act = MD.flagged_msgs[0, 0][:1]
    #     fig.text(.05, 0.93, 'FLAG', color='r', ha='left') 
    #     fig.text(.05, 0.85, '%s:\n%s' %(MD.flagged_msgs[0, 0], MD.flagged_msgs[0, 1]), 
    #                 fontsize=8, color=MD.experiment.fcolors[act][0], ha='left', va='center') 



def plot_raster_mouseday(E, mouseNumber=2101, dayNumber=5, bin_type='12bins', plot_type='raster', 
        GENERATE=False, FLAG_IGNORED=False):
    """
    """ 

    mouse = E.get_mouse_object(mouseNumber)
    MD = mouse.mouse_days[dayNumber-1]
    print 'Exp: %s, %s, %s, BIN_SHIFT: %s' %(
            E.short_name, plot_raster_mouseday.__name__, bin_type, E.BIN_SHIFT)
    text = 'excluded' if MD.ignored else ''
    print MD, text
    
    if GENERATE:
        E.generate_binaries(mouse.mouseNumber, MD.dayNumber)
        E.generate_bouts(mouse.mouseNumber, MD.dayNumber)
        E.generate_active_states(mouse.mouseNumber, MD.dayNumber)
        print ""

    string = '_shifted%+02dm' %(E.binTimeShift/60) if E.BIN_SHIFT else ''

    dirname_out = E.figures_dir + '%ss/%s/mouseday/group%d/M%d/%s_days/' %(
                    plot_type, bin_type+string, mouse.groupNumber, mouseNumber, E.use_days)
                    
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)
    
    fname = dirname_out + '%s_group%d_M%d_D%d' %(
                            plot_type, mouse.groupNumber, mouse.mouseNumber, MD.dayNumber)

    
    plot_events(MD, fname, plot_type, bin_type, FLAG_IGNORED=FLAG_IGNORED)  




