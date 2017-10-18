import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm
from matplotlib.ticker import LogFormatterMathtext
import time
import os 

from intervals import Intervals
from cage import Cage
from option_colormaps import get_optionD_cmap
from plotting_utils import draw_device_labels, truncate_colormap#, cmap_discretize
from plot_settings import *

"""
G.Onnis, 02.2016

Tecott Lab UCSF
"""


def plot_data_quality(experiment):

    cstart = time.clock()

    E = experiment

    strain_names = E.strain_names

    base_name = 'data_quality'

    dirname_out = E.plots_dir + base_name + '/'
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

    flagged, reason = getattr(E, 'flagged'), getattr(E, 'reason')

    print "flagged %d/%d mousedays" %(len(flagged), E.num_mousedays)
    
    # Turn interactive plotting off
    plt.ioff()

    start_day, end_day = E.daysToUse[0], E.daysToUse[-1]

    strain = 0
    error_cnt = 0
    for group in E.groups:    
        for individual in group.individuals:
            for MD in individual.mouse_days:
                if MD.dayNumber >= start_day and MD.dayNumber <= end_day:

                    cstart2 = time.clock()
                    print base_name, MD
                    
                    #grid
                    gs1, fig, ax0, ax1, ax2 = create_dq_figure()

                    plot_distance_events(fig, ax0, MD)

                    plot_pos_dens(fig, ax1, MD, xbins=12, ybins=24)
                    
                    plot_pos_dens(fig, ax2, MD, xbins=2, ybins=4, nest=True)
                    
                    form_ = (strain_names[strain], MD.mouseNumber, MD.dayNumber)
                    title = '%s, M%d, day%d' %form_
                    fig.text(0.7, 0.9, title, ha='left')


                    #flag
                    if (MD.mouseNumber, MD.dayNumber) in flagged:
                        draw_flagged(fig, flag=reason[error_cnt])
                        error_cnt += 1

                    gs1.update(left=0.05, wspace=0.5)


                    # save
                    form_ = (MD.groupNumber, MD.individualNumber, MD.dayNumber)
                    id_string = "strain%d_individual%d_day%d" %form_
                    
                    print "saving.."
                    fname = dirname_out + basename + '_' + id_string + ".pdf"
                    fig.savefig(fname)
                    print "saved to: %s" %fname
                    plt.close()

                    cstop2 = time.clock()

                    print "This mouseday took %fs..\n"%(cstop2-cstart2)

        strain += 1

    cstop = time.clock()

    print "%s plotting script took %fm..\n" %(base_name, (cstop-cstart)/60.)





def plot_distance_events(fig, ax, MD):

    C = Cage()

    for varName in ['CT', 'CX', 'CY']:
        if not hasattr(MD, varName):
            MD.load(varName)

    color = MD.experiment.fcolors['M'][0]
    
    print "plotting distance.."
    dist = np.sqrt((MD.CX - C.xy_o[0])**2 + (MD.CY - C.xy_o[1])**2)

    ax.plot(MD.CT / 3600. -7, dist, lw=0.5, color='0.3')    

    plot_events(ax, MD)

    set_distance_raster_layout(fig, ax)





def plot_events(ax, MD):
    """plots events below distance plot
    """

    coord_vars = ['CT_at_HB', 'CT_out_HB']
    ingestion_vars = ['F_Sets', 'at_F_Sets', 'W_Sets', 'at_W_Sets']
    all_vars = coord_vars + ingestion_vars

    labels = ['at HB', 'out HB', 'F', 'times at F', 'W', 'times at W']
    
    names = ['M', 'M', 'F', 'F', 'W', 'W']
    idx = [2, 0, 0, 1, 0, 1]
    colors = [MD.experiment.fcolors[name][idx[c]] for c, name in enumerate(names)]

    offsets = [-3, -5, -9, -11, -14, -16]
    height = 1.
    
    print "plotting events.."


    for c, name in enumerate(all_vars):

        # load
        if not hasattr(MD, name):
            MD.load(name)

        events = getattr(MD, name) / 3600. - 7 

        offset = offsets[c]
        color = colors[c]
        label = str(events.shape[0]) + ' ' + labels[c]

        if name in ['CT_at_HB', 'CT_out_HB', 'F_Sets', 'W_Sets']:
            label += ' events'

        if name in coord_vars:
            
            ax.scatter(
                events, offset * np.ones(events.shape[0]),
                c=color,
                marker='|',
                linewidths=1,
                edgecolors=None
                )
            

        elif name in ingestion_vars:

            for x in events:            
                event_patch = patches.Rectangle(
                    (x[0], offset), x[1]-x[0], height,      # xy lower left corner, width, height
                    linewidth=0.001,
                    fc=color, 
                    ec=color
                    )   
                ax.add_patch(event_patch) 

        # event descritpion
        ax.text(31, offset, label, color=color, 
            fontsize=7, ha='left', va='bottom'
            )

    
    



    
def plot_pos_dens(fig, ax, MD, xbins=12, ybins=24, nest=False):

    print "plotting position density xbins=%d, ybins=%d.." %(xbins, ybins)

    varName = 'bin_times_24H_xbins%d_ybins%d' %(xbins, ybins)
    if not hasattr(MD, varName):
        MD.load(varName)

    # settings

    bin_times = getattr(MD, varName)
        
    # pos_dens = np.zeros([xbins, ybins])
    if bin_times.sum() > 0:
        pos_dens = bin_times / bin_times.sum()


    im = ax.imshow(pos_dens, interpolation='nearest', 
        cmap=ax.cmap, 
        norm=LogNorm(vmin=ax.vmin, vmax=ax.vmax), 
        extent=fig.extent
        )

    set_pos_dens_layout(fig, ax, im)    

    if nest:
        add_hb_info(ax, MD, bin_times)







# plotting layout
def set_distance_raster_layout(fig, ax, DC=True):

    ax.autoscale(False)

    ax.set_xlim(fig.xlims)
    ax.set_ylim(fig.ylims)

    ax.set_xticks(fig.xticks)
    ax.set_xticklabels(fig.xticks)
    ax.set_yticks(fig.yticks)
    ax.set_yticklabels(fig.yticks)

    ax.spines['top'].set_visible(False)     
    ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_position('zero')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    ax.tick_params(axis='both', which='both', direction='out')

    ax.set_xlabel('Circadian Time', labelpad=5)
    ax.set_ylabel('Distance from W [cm]', labelpad=5)

    if DC:
        add_DC_gray_background_to_raster(fig, ax)


def add_DC_gray_background_to_raster(fig, ax):
    
    height = 43
    DC = patches.Rectangle([12, 0], 12, height, 
        fc='0.85', ec='0.85', zorder=0#, clip_on=False
        )
    
    ax.add_patch(DC)


def set_pos_dens_layout(fig, ax, im, draw_labels=True):
    ax.set_xticks([])
    ax.set_yticks([])
    
    set_colorbar(fig, ax, im)

    if draw_labels:
        draw_device_labels(ax, fontsize=14, labelpad=3)



def set_colorbar(fig, ax, im):

    cbar = fig.colorbar(im, cax=ax.axCbar, format=mpl.ticker.LogFormatterMathtext())
    
    # axes_obj = plt.getp(axCbar,'axes')
    ytl_obj = plt.getp(ax.axCbar, 'yticklabels')
    plt.setp(ytl_obj, fontsize=10)
    cbar.ax.set_ylabel('Occupancy', fontsize=10, rotation=270, labelpad=15)



def add_hb_info(ax, MD, bin_times):

    draw_homebase_star(ax, MD)

    percent_time = bin_times / bin_times.sum()
    draw_percent_time(ax, percent_time)


def draw_flagged(fig, flag):
    """ flags ignored mousedays
    """
    act, msg = flag
    text1 = 'FLAGGED' 
    text2 = act + ' - ' + msg
    fig.text(0.85, 0.9, text1, color='r')
    fig.text(0.85, 0.85, text2, fontsize=9)



def draw_homebase_star(ax, MD):

    varName = 'rect_HB'
    if not hasattr(MD, varName):
        MD.load(varName)

    rect_HB = getattr(MD, varName)
    
    obs_rect, is_consistent_ethyl, is_niche = MD.compare_homebase_locations_to_ethel_obs()

    width = 0.2
    height = 0.2
    tkw = {'ms':10, 'transform':ax.transAxes}
    
    for cell in rect_HB:
        yc, xc = cell
        y1, x1 = 0.92 - 0.25*yc, 0.2 + 0.5*xc,
        ax.plot(x1, y1, '*', color='y', label='coded HB', **tkw)

    if obs_rect is not None:
        for cell in obs_rect:
            yb, xb = cell
            y2, x2 = 0.92 - 0.25*yb, 0.3 + 0.5*xb

            ax.plot(x2, y2, '*', color='r', label='obs HB', **tkw)

    ax.legend(numpoints=1, bbox_to_anchor=[2.1, 1.07], frameon=False, handletextpad=0, prop={'size':7})



def draw_percent_time(ax, Z3, fontsize=8):
    ybins, xbins = Z3.shape
    for x in xrange(xbins):
        for y in xrange(ybins):
            ax.text(0.25 + 0.5*x, 0.85 - 0.25*y, round(100*Z3[y, x], 2), 
                color='k', fontsize=fontsize, ha='center', va='center', 
                transform=ax.transAxes
                )
            # print 'xbin%d'%x, 'ybin%d'%y, 0.1 + 0.5*x, 0.85 - 0.25*y

    ax.text(1.5, 0.88, '(percent time)', fontsize=8, transform=ax.transAxes)






def create_dq_figure():                 
    
    C = Cage()
    figsize = (16, 5)
    gs1 = gridspec.GridSpec(3, 6)
    fig = plt.figure(figsize=figsize)

    fig.xlims = [4, 32]
    fig.ylims = [-18, 43]
    fig.xticks = range(6, 31, 2)
    fig.yticks = range(0, 45, 10)

    ax0 = fig.add_subplot(gs1[:, :4])       # distance raster
    ax1 = fig.add_subplot(gs1[1:, 4])       # position density xbins,ybins=12,24
    ax2 = fig.add_subplot(gs1[1:, 5])       # position density xbins,ybins=2,4
    # ax1.set_aspect(aspect=2, adjustable='box')

    # colormap and figure options
    setattr(fig, 'extent', [C.CMXLower, C.CMXUpper, C.CMYLower, C.CMYUpper])

    cmap = get_optionD_cmap()
    setattr(ax1, 'cmap', cmap)
    setattr(ax2, 'cmap', truncate_colormap(cmap, 0.5, 1))

    setattr(ax1, 'vmin', 0.0001)
    setattr(ax2, 'vmin', 0.01)      
    setattr(ax1, 'vmax', 1)
    setattr(ax2, 'vmax', 1)
    
    # colorbar axes
    setattr(ax1, 'axCbar', fig.add_axes([0.75, 0.1, .01, 0.4]))     # [left, bottom, width, height]
    setattr(ax2, 'axCbar', fig.add_axes([0.9, 0.1, .01, 0.4]))  

    return gs1, fig, ax0, ax1, ax2




    


