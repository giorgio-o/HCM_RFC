import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import os
import time

from newcode import my_utils 
from newcode import plotting_utils
from newcode import plot_settings

"""
G.A.Onnis, 07.2016
    revised: 10.2016, 01.2017
Tecott Lab UCSF
"""

def plot_bout_numbers_data(experiment, act='F', level='strain'):
    cstart = time.clock()
    E = experiment  

    dirname = E.figures_dir + 'bouts/distributions/%s/' %act
    if not os.path.isdir(dirname): os.makedirs(dirname)
    
    print "plotting %s bout numbers distributions.." %act
    arr, arr_labels = E.get_numbers(act, what='bout')
    
    gs1, fig = create_4x4_xy_gridspec(level)
    for strain in xrange(E.num_strains):
        subtitles = [name for name in E.strain_names]
        idx = arr_labels[:, 0] == strain
        idx_start, idx_end = my_utils.find_nonzero_runs(idx)[0]
        data = np.hstack(arr[idx_start:idx_end])
        bin_width = draw_distribution(E, gs1, fig, data, act, '%sB_numbers' %act, level, strain, subtitles)
        
    # plot all strain average
    
    plot_title = '%s bout number distribution (normalized)\nall_strains\nbin_size=%d' %(act, bin_width)
    fig.text(0.03, 0.93, plot_title, fontsize=8)
    gs1.update(bottom=0.12, top=0.89, hspace=0.4)
    # save
    fname = dirname + 'all_strains_%s_bout_numbers_distribution.pdf' %act
    plt.savefig(fname)
    plt.close()
    print "output saved to: %s" %fname


def plot_bout_data_distribution(E, act='M', level='strain', num_bins=100, LOG=False):
    """
    """
    cstart = time.clock()
    
    dirname = E.figures_dir + 'distributions/bouts/%s/' %act
    if not os.path.isdir(dirname): os.makedirs(dirname)
    
    print "%s..\nlevel: %s\nact: %s\num_bins: %d" %(
        plot_bout_data_distribution.__name__, level, act, num_bins)

    # names = ['duration', 'size', 'intensity']
    # if act == 'M':
    #     names = ['duration', 'distance', 'velocity'] 
    # varNames = ['%sB_%s' %(act, x) for x in names]
    varNames = [val for val in E.HCM_variables['stats'] if val[0] == act]
    for varName in varNames:
        # get data
        arrays, arr_labels = E.generate_bout_data(act, varName)
        # plot
        if level == 'strain':
            gs1, fig = plotting_utils.create_4x4_xy_gridspec(level)
            for strain in xrange(E.num_strains):
                subtitles = [name for name in E.strain_names]
                idx = arr_labels[:, 0] == strain
                idx_start, idx_end = my_utils.find_nonzero_runs(idx)[0]
                data = np.hstack(arrays[idx_start:idx_end])
                bin_width = draw_distribution(E, gs1, fig, data, act, varName, level, strain, subtitles)

            # plot all strain average
            
            plot_title = '%s bout %s distribution (normalized)\nall_strains\nbin_size=%d' %(act, varName[3:], bin_width)
            fig.text(0.03, 0.93, plot_title, fontsize=8)
            gs1.update(bottom=0.12, top=0.89, hspace=0.4)
            # save
            fname1 = dirname + 'all_strains_%s_bout_%s_distribution.pdf' %(act, varName[3:])
            plt.savefig(fname1)
            plt.close()
            print "output saved to: %s" %fname1
        else:
            dirname += '%s/%s/' %(level, varName)
            if not os.path.isdir(dirname): os.makedirs(dirname)
            if level == 'mouse':
                for strain in xrange(E.num_strains):
                    gs1, fig = create_4x4_xy_gridspec(level)
                    m_labels = np.unique(arr_labels[arr_labels[:,0]==strain][:,1])
                    for m_num in xrange(len(m_labels)):
                        subtitles = ['M%d' %num for num in m_labels]
                        # data
                        idx = arr_labels[:, 1] == m_labels[m_num]
                        idx_start, idx_end = my_utils.find_nonzero_runs(idx)[0]
                        data = np.hstack(arrays[idx_start:idx_end])
                        bin_width = draw_distribution(E, gs1, fig, data, act, varName, level, m_num, subtitles)
                        # plot strain average . TODO ################

                    plot_title = '%s bout %s distribution (normalized)\n%s\nbin_size=%ds' %(act, varName[3:], E.strain_names[strain], bin_width)
                    fig.text(0.03, 0.93, plot_title, fontsize=8)
                    gs1.update(bottom=0.12, top=0.89, hspace=0.4)
                    # save
                    fname1 = dirname + '%s_bout_%s_distribution_strain%s.pdf' %(act, varName[3:], strain)
                    plt.savefig(fname1)
                    plt.close()
                    print "output saved to: %s" %fname1


def draw_distribution(E, gs1, fig, data, act, varName, level, num_subplot, subtitles, normed=1):
    
    settings_dict = plot_settings.get_settings(E)
    # bin_width = settings_dict[varName]['bin_width']
    # bin_max = settings_dict[varName]['bin_max']
    bins = settings_dict[varName]['bins']
    # bins = np.arange(0, bin_max + bin_width, bin_width)

    ax = fig.add_subplot(gs1[num_subplot])
    ax.hist(data, bins, normed=normed, fc=E.fcolors[act][0])
    ax.set_title(subtitles[num_subplot], fontsize=10)
    ax.text(0.7, 0.85, '%d %sBouts' %(int(data.sum()), act), fontsize=6, transform=ax.transAxes)
    set_layout(fig, ax, act, varName, level, bins, num_subplot)
    return bin_width


def set_layout(fig, ax, act, varName, level, bins, num_subplot):
    settings_dict = get_settings()
    xlims = settings_dict[varName]['xlims']
    ylims = settings_dict[varName]['ylims']
    xticks = settings_dict[varName]['major_xticks']
    yticks = settings_dict[varName]['yticks']
    xlabel = '%s %s' %(varName, settings_dict[varName]['unit'])

    ax.set_xlim(xlims)
    ax.set_xticks(xticks)
    ax.set_xticklabels([])
    if num_subplot >= 12 and level == 'strain':
        ax.set_xticklabels(xticks) 
    elif num_subplot >= 9 and level != 'strain':
        ax.set_xticklabels(xticks) 

    ax.set_ylim(ylims)
    ax.set_yticks(yticks)
    ax.set_yticklabels([])
    if num_subplot in [0, 4, 8, 12] and level == 'strain':
        ax.set_yticklabels(yticks) 
    elif num_subplot in [0, 3, 6, 9] and level != 'strain':
        ax.set_yticklabels(yticks)

    ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
    ax.tick_params(axis='both', which='both', labelsize=7)
    fig.text(0.5, 0.04, xlabel, ha='center')
    fig.text(0.05, 0.5, 'Probability', va='center', rotation='vertical')
    plotting_utils.ax_cleanup(ax)


# def create_4x4_xy_gridspec(level):
#     figsize = (12, 7)
#     sub_high, sub_wide = 4, 4
#     if level != 'strain':
#         figsize = (9, 6)
#         sub_wide = 3
#     gs1 = gridspec.GridSpec(sub_high, sub_wide)
#     fig = plt.figure(figsize=figsize)
#     return gs1, fig


# def get_settings():
#     settings_dict = {

#         # # # AS features
#         'FB_numbers':  
#             {
#             'bin_width' : 5,
#             'bin_max' : 400,
#             'xlims' : (0, 400),
#             'ylims' : (0, .05),
#             'major_xticks': np.range(0, 400, 50),
#             'yticks': np.linspace(0, .05, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[-]',    
#             },

#         'FB_duration':  
#             {
#             'bin_width' : 1,
#             'bin_max' : 60,
#             'xlims' : (0, 60),
#             'ylims' : (0, .5),
#             'major_xticks': np.range(0, 60, 10),
#             'yticks': np.linspace(0, .5, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[s]',    
#             },

#         'FB_size':  
#             {
#             'bin_width' : 1,
#             'bin_max' : 60,
#             'xlims' : (0, 60),
#             'ylims' : (0, .5),
#             'major_xticks': np.range(0, 60, 10),
#             'yticks': np.linspace(0, .5, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[mg]',    
#             },

#         'FB_intensity':  
#             {
#             'bin_width' : .1,
#             'bin_max' : 4,
#             'xlims' : (0, 4),
#             'ylims' : (0, 3),
#             'major_xticks': np.range(4),
#             'yticks': np.linspace(0, 3, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[mg/s]',    
#             },

#         'WB_numbers':  
#             {
#             'bin_width' : 5,
#             'bin_max' : 400,
#             'xlims' : (0, 400),
#             'ylims' : (0, .1),
#             'major_xticks': np.range(0, 400, 50),
#             'yticks': np.linspace(0, .1, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[-]',    
#             },

#         'WB_duration':  
#             {
#             'bin_width' : 1,
#             'bin_max' : 60,
#             'xlims' : (0, 60),
#             'ylims' : (0, .5),
#             'major_xticks': np.range(0, 60, 10),
#             'yticks': np.linspace(0, .5, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[s]',    
#             },

#         'WB_size':  
#             {
#             'bin_width' : 2,
#             'bin_max' : 200,
#             'xlims' : (0, 200),
#             'ylims' : (0, .1),
#             'major_xticks': np.range(0, 200, 50),
#             'yticks': np.linspace(0, .1, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[mg]',    
#             },

#         'WB_intensity':  
#             {
#             'bin_width' : 1,
#             'bin_max' : 50,
#             'xlims' : (0, 50),
#             'ylims' : (0, .5),
#             'major_xticks': np.range(0, 50, 10),
#             'yticks': np.linspace(0, .5, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[mg/s]',    
#             },

#         'MB_numbers':  
#             {
#             'bin_width' : 100,
#             'bin_max' : 2000,
#             'xlims' : (0, 2000),
#             'ylims' : (0, .006),
#             'major_xticks': np.range(0, 2000, 500),
#             'yticks': np.linspace(0, .006, 3+1),
#             # 'title': 'Active State Probability',
#             'unit': '[-]',    
#             },

#         'MB_duration':  
#             {
#             'bin_width' : .5,
#             'bin_max' : 20,
#             'xlims' : (0, 20),
#             'ylims' : (0, .5),
#             'major_xticks': np.range(0, 20, 5),
#             'yticks': np.linspace(0, .5, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[s]',    
#             },

#         'MB_distance':  
#             {
#             'bin_width' : 2,
#             'bin_max' : 200,
#             'xlims' : (0, 200),
#             'ylims' : (0, .1),
#             'major_xticks': np.range(0, 20, 5),
#             'yticks': np.linspace(0, .1, 5+1),
#             # 'title': 'Active State Probability',
#             'unit': '[cm]',    
#             },

#         'MB_velocity':  
#             {
#             'bin_width' : 1,
#             'bin_max' : 50,
#             'xlims' : (0, 50),
#             'ylims' : (0, .2),
#             'major_xticks': np.range(0, 50, 10),
#             'yticks': np.linspace(0, .5, 4+1),
#             # 'title': 'Active State Probability',
#             'unit': '[cm/s]',    
#             },
#         }

#     return settings_dict






