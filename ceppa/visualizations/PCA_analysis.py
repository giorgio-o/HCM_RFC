import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

from sklearn.decomposition import PCA

import os
import csv 

from ceppa.visualizations.features_panel_CT import get_feature_panel_data
from ceppa.visualizations.plotting_utils import get_subplot_specs, subplot_labels, ax_cleanup, save_plot
from ceppa.visualizations.plotting_utils import write_2darray_to_csv, get_16_colors


"""
G.Onnis, C.J.Hillar, 01.2015
G.Onnis, 05.2017

Tecott Lab UCSF
"""

       
np.set_printoptions(precision=2, threshold=8000)


def plot_explained_variance_ratio(experiment, X, pca, level, lastcomp, fname, EXCLUDE_SS):
    E = experiment

    components = pca.components_
    num_components = pca.n_components_
    expl_variance = pca.explained_variance_ratio_

    figsize, nrows, ncols, _, _ = get_subplot_specs(E, num_subplots=2)
    fig, (ax0, ax1) = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    ax0.plot(range(len(components)), expl_variance, color='.4')
    ax1.plot(range(len(components))[-lastcomp:], expl_variance[-lastcomp:], color='.4')
    
    ax0.set_ylim([0, .35])
    ax1.set_ylim([0, .0006])

    ax1.xaxis.set_major_locator(MultipleLocator(1))
    for ax in [ax0, ax1]:
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax_cleanup(ax)
    
    # annotate close-up
    text = 'close up,\nlast %d components' %lastcomp
    ax1.text(.5, .7, text, fontsize=8, transform=ax1.transAxes)

    text = '%d strains, ' %E.num_strains if not EXCLUDE_SS \
            else '%d strains (no AKR, CAST, CZECH), ' %(E.num_strains-3)
    level_ = 'mice' if level == 'mouse' else level
    fig_title = 'Explained variance ratio, %d principal components\n%s%d %s, 24H avg data' %(
                    num_components, text, X.shape[0], level_)
    subplot_labels(E, fig, xlabel='Principal component', ylabel='explained variance', fig_title=fig_title)
    plt.subplots_adjust(bottom=.15, wspace=.4)
    save_plot(fname, fig)


def plot_loadings(experiment, X, pca_components, feature_names, level, comps_idx, 
    fname, plot_type, EXCLUDE_SS, ADD_SOURCE=True):
    E = experiment

    num_items = X.shape[0]
    num_components = len(pca_components)
    num_features = len(feature_names)
    assert num_features == num_components, 'wtf'

    # select components
    selected_comps = pca_components[comps_idx]

    fig, ax = plt.subplots(figsize=(7,3))
    bar_width = .03 if len(comps_idx) == num_components else .1
    colors = [E.plot_settings_dict[feat]['color'] for feat in feature_names]

    if plot_type == 'bar':
        for c, comp in enumerate(selected_comps):
            ind = np.arange(num_features) + c * bar_width
            alpha_step = .03*comp if len(comps_idx) == num_components else .2*comp 
            tkw = {'lw':.2, 'alpha':(1-alpha_step), 
                    'color':colors, 'edgecolor':None,
                    'label':'PC%d' %comp}
            
            ax.bar(ind, pca_components[-(comp+1)], bar_width, **tkw) 

    elif plot_type == 'line':
        colors = get_16_colors()[1::4]
        tkw = {'numpoints':1, 'fontsize':6, 'handletextpad':1.2, 
                'labelspacing':.8, 'borderaxespad':1.5, 'frameon':False,
                'bbox_to_anchor':(1., 1.2), 'bbox_transform':ax.transAxes}
        for c, comp in enumerate(selected_comps):
            ax.plot(comp, color=colors[c], 
                    label='comp%d' %(comps_idx[c]))
        leg = ax.legend(**tkw)

    ax.set_xticks(range(num_features))
    ax.set_xticklabels([])
    ax.set_ylim(-1, 1)

    ax.axhline(xmin=0, xmax=num_features, lw=.5, color='k')
    ax.spines['bottom'].set_position('zero')
    ax.spines['bottom'].set_visible(False)
    ax_cleanup(ax)

    # display feature names on top of bars
    xpos = np.arange(num_features) + .2
    heights = selected_comps.max(axis=0) + .04
    heights[5] = heights[4] + .05    # correct FBASR
    if plot_type == 'line': heights += .1
    for p, feat in enumerate(feature_names):
        ax.text(xpos[p], heights[p], feat, fontsize=6, ha='center', transform=ax.transData)

    # annotate
    if plot_type == 'hist':
        annotation = 'Color-code by feature type.\n' \
                    + 'AS:purple, Feeding:orange, Drinking:blue, Move:green.\n' \
                    + 'For each feature, components from %d (opaque) to\n' %comps_idx[0] \
                    + '%dth (transparent) are shown on a sliding\ntransparency scale.' %comps_idx[-1]
        ax.text(13.8, ax.get_ylim()[0], annotation, fontsize=6, va='center', transform=ax.transData)

    # title
    text = '%d strains, ' %E.num_strains if not EXCLUDE_SS \
            else '%d strains (no AKR, CAST, CZECH), ' %(E.num_strains-3)
    level_ = 'mice' if level == 'mouse' else level
    fig_title = 'Principal Component loadings, components: %s of %d total\n%s%d %s, 24H avg data\n%s days:%dto%d' %(
                comps_idx, num_components, text, num_items, level_, E.use_days, E.daysToUse[0], E.daysToUse[-1])
    subplot_labels(E, fig, xlabel='', ylabel='Loading', fig_title=fig_title)
    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE)


def plot_component_loadings(E, X, pca_components, feature_names, level, 
        fname, EXCLUDE_SS=False, BY_STRAIN=False, strain=None, ADD_SOURCE=True):
    
    num_items = X.shape[0]
    num_components = len(pca_components)
    num_features = len(feature_names)

    figsize, nrows, ncols, sharex, sharey = get_subplot_specs(E, num_subplots=num_components)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=sharex, sharey=sharey)

    xs = range(1, num_components+1)
    for c, comp in enumerate(pca_components):
        ax = axes.flatten()[c]
        ax.plot(xs, comp, color='.4')
        ax.set_xlim(0, ax.get_xlim()[1])
        ax.set_xticks(range(num_features))
        ax.set_xticklabels([])

        ax.set_title('PC%d' %c, fontsize=8, position=(.5, 1.15), ha='center')
        ax.axhline(xmin=0, xmax=num_features, lw=.5, color='k')
        ax.spines['bottom'].set_position('zero')
        ax.spines['bottom'].set_visible(False)
        ax_cleanup(ax)

        # display feature names on top
        heights = list(np.linspace(1.05, .55, 4)) * 8
        for p, feat in enumerate(feature_names):
            ax.text(xs[p], heights[p], feat, fontsize=4, ha='center', transform=ax.transData)
            ax.axvline(x=xs[p], ymin=.4, ymax=heights[p], lw=.2, color='.5')
    
    # title
    text = '%d strains,' %E.num_strains if not EXCLUDE_SS \
            else '%d strains (no AKR, CAST, CZECH),' %(E.num_strains-3)
    level_ = 'mice' if level == 'mouse' else level
    fig_title = 'Principal Component loadings, %d components\n' %num_components \
                + '%s %d %s, 24H avg data\n%s days:%dto%d' %(
                text, num_items, level_, E.use_days, E.daysToUse[0], E.daysToUse[-1])
    if BY_STRAIN:
        fig_title = 'Principal Component loadings, %d components\n' %num_components \
                    + '%s %d %s, 24H avg data\ngroup%d: %s\n%s days:%dto%d' %(
                    text, num_items, level_, strain, E.strain_names[strain],
                    E.use_days, E.daysToUse[0], E.daysToUse[-1])
    subplot_labels(E, fig, xlabel='', ylabel='Loading', fig_title=fig_title)
    plt.subplots_adjust(hspace=.4, wspace=.3)
    save_plot(fname, fig, ADD_SOURCE=ADD_SOURCE)



def plot_PCA(experiment, bin_type='24HDCLC', level='mouse', comps_idx=None, 
        plot_type='hist', EXCLUDE_SS=False, BY_STRAIN=False):

    E = experiment

    print "%s..\nlevel: %s\nbin_type: %s\ncomponents: %s" %(
            plot_PCA.__name__, level, bin_type, comps_idx)

    # load data
    features_names = E.features_by_activity
    num_features = len(features_names)
    avgs, _, labels = get_feature_panel_data(E, features_names, bin_type, level)

    # # exclude strains 6.AKR, 11.CAST, 12.CZECH
    if E.short_name == 'SS' and EXCLUDE_SS:
        print "excluding groups: 6.AKR, 11.CAST, 12.CZECH\n"
        mask = np.ones(avgs.shape[1], dtype=bool)
        idx1, idx2, idx3 = [labels[:, 0] == x for x in [6, 11, 12]]
        idx = idx1 + idx2 + idx3
        mask[idx] = False
        avgs = avgs[:, mask]

    # PCA
    X = avgs[:, :, 0].T                             # 24H data
    Xz = (X - X.mean(axis=0)) / X.std(axis=0)       # z-score
    pca = PCA(whiten=False, random_state=42)
    X_transf = pca.fit_transform(Xz)                # (n_samples, n_components)
    # stop
    subdir = ''
    if E.short_name == 'SS': 
        subdir = 'all_strains/' if not EXCLUDE_SS else 'no_AKR_CAST_CZECH/'   

    dirname_out = E.figures_dir_subpar + 'features/PCA/%s_days/%s' %(E.use_days, subdir)    
    if not os.path.isdir(dirname_out): os.makedirs(dirname_out)

    if comps_idx is None:

        E = experiment

        num_components = len(pca.components_)
        num_features = len(features_names)
        assert num_features == num_components, 'wtf'

        if level == 'mouse':
            fig = plot_component_loadings(E, Xz, pca.components_, features_names, level,
                    fname=dirname_out + 'pca_loadings_all_components_24H_%s' %level,
                    EXCLUDE_SS=EXCLUDE_SS)


        elif level == 'mouseday':
            plot_component_loadings(E, Xz, pca.components_, features_names, level, 
                fname=dirname_out + 'pca_loadings_all_components_24H_%s' %level,
                EXCLUDE_SS=EXCLUDE_SS
                )
            if BY_STRAIN:
                dirname_out2 = dirname_out + 'by_strain/'    
                if not os.path.isdir(dirname_out2): os.makedirs(dirname_out2)
                for strain in xrange(E.num_strains):
                    idx = labels[:, 0] == strain
                    pca2 = PCA(whiten=False, random_state=53)
                    pca2.fit(Xz[idx])

                    plot_component_loadings(E, Xz[idx], pca2.components_, features_names, level, 
                        fname=dirname_out2 + 'pca_loadings_all_components_24H_%s_strain%d' %(level, strain),
                        BY_STRAIN=BY_STRAIN, strain=strain,
                        EXCLUDE_SS=EXCLUDE_SS
                        )

    else:
        plot_loadings(E, Xz, pca.components_, features_names, level, comps_idx, 
            fname=dirname_out + 'pca_loadings_%s_24H_comps_%s_%s' %(level, comps_idx, plot_type),
            plot_type=plot_type, EXCLUDE_SS=EXCLUDE_SS
            )


    # plot_explained_variance_ratio(E, Xz, pca, level, lastcomp=5, 
    #     fname=dirname_out + 'pca_explained_variance_%s_24H' %level,
    #     EXCLUDE_SS=EXCLUDE_SS
    #     )

    # text = '%d strains, ' %E.num_strains if not EXCLUDE_SS \
    #         else '%d strains (no AKR, CAST, CZECH), ' %(E.num_strains-3)
    # write_2darray_to_csv(E, pca.components_,
    #     header='PCA loadings, %s%s, 24H' %(text, level),
    #     subheader='(n_component, n_features)', 
    #     row_labels=['PCA%d' %x for x in range(pca.n_components_)], 
    #     col_labels=features,
    #     fname=dirname_out + 'pca_loadings_%s_24H.csv' %level)



#     get_oblique_rotation(Xz)

# def get_oblique_rotation(X):
    
    # import ceppa.util.factor_rotation_master.factor_rotation as fr

    #https://stats.stackexchange.com/questions/185216/factor-rotation-methods-varimax-oblimin-etc-what-do-the-names-mean-and-wh    
    # rotation Q is performend on A (loadings matrix) iteratively on pairs of factors/components 
    # (columns of the loading matrix)
    # structure matrix: S = AQ 
    # methods: 
    # - 'varimax', orthogonal rotation tries to maximize variance of the squared loadings in each factor in S.
    # - 'oblimin', flexible due to Gamma parameter: G=0, most oblique (equivalent ot quartimin), 
    #   G=1 least oblique. usually done with Kaiser Normalization

    # use oblimin, i.e. assume components are not orthogonal, i.e. to some extent correlated.
    # L, T = fr.rotate_factors(X, method='oblimin', rotation_method='orthogonal')
    # stop



