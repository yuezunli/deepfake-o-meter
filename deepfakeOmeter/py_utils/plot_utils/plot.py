"""
Proj: YZ_utils
Date: 3/29/18
Written by Yuezun Li
--------------------------
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


# Draw line plot
def draw2D(X, Y, order, xname, yname, params, xlim=None, ylim=None, rcparams=None, legend_loc=0, save_path=None):

    title = params['title']
    colors = params['colors']
    markers = params['markers']
    linewidth = params['linewidth']
    markersize = params['markersize']
    figsize = params['figsize']

    if rcparams is None:
        rcparams = {
            'figure.autolayout': True,
            'legend.fontsize': 15,
            'axes.labelsize': 25,
            'axes.titlesize': 25,
            'xtick.labelsize': 25,
            'ytick.labelsize': 25,
            }
    matplotlib.rcParams.update(rcparams)

    # X = np.array(X)
    # Y = np.array(Y)

    fig = plt.figure(facecolor='white',figsize=figsize)
    plt.title(title)
    plt.ylabel(yname)
    if ylim is not None:
        plt.ylim(ylim[0], ylim[1])
    plt.xlabel(xname)
    if xlim is not None:
        plt.xlim(xlim[0], xlim[1])

    for i, type_name in enumerate(order):
        plt.plot(X[i], Y[i], colors[i], label=type_name, linewidth=linewidth, markersize=markersize, marker=markers[i])

    plt.tight_layout()
    plt.grid()
    plt.legend(loc=legend_loc)
    fig.canvas.draw()
    if save_path:
        fig.savefig(save_path, dpi=600, format='pdf')
    # grab the pixel buffer and dump it into a numpy array
    im = np.array(fig.canvas.renderer._renderer)[:, :, :-1]
    plt.close()
    return im[:, :, (2, 1, 0)]


# Draw bar plot
def draw_barchart(X, Y, order, xname, yname, params, xlim=None, ylim=None):

    title = params['title']
    colors = params['colors']
    barwidth = params['barwidth']
    figsize = params['figsize']
    xticks = params['xticks']

    rcparams = {
        'figure.autolayout': True,
        'legend.fontsize': 20,
        'axes.labelsize': 30,
        'axes.titlesize': 35,
        'xtick.labelsize': 30,
        'ytick.labelsize': 30}
    matplotlib.rcParams.update(rcparams)

    X = np.array(X)
    Y = np.array(Y)

    fig = plt.figure(facecolor='white',figsize=figsize)
    plt.title(title)
    plt.ylabel(yname)
    if ylim is not None:
        plt.ylim(ylim[0], ylim[1])
    plt.xlabel(xname)
    if xlim is not None:
        plt.xlim(xlim[0], xlim[1])
    plt.xticks(X[0] + barwidth, xticks)
    offset = 0
    for i, type_name in enumerate(order):
        plt.bar(offset + X[i], Y[i], barwidth, color=colors[i], label=type_name)
        offset += barwidth
    plt.grid()
    plt.legend()
    fig.canvas.draw()
    # grab the pixel buffer and dump it into a numpy array
    im = np.array(fig.canvas.renderer._renderer)[:, :, :-1]
    # plt.show()
    plt.close()
    return im[:, :, (2, 1, 0)]


def draw_heatmap(input, output_name, cmap='coolwarm'):
    hm = sns.heatmap(input, cmap)
    plt.savefig(output_name + '.png')
    plt.clf()
    return hm


def draw_heatmap_v2(input, output_name):
    heatmap = plt.pcolor(input)
    plt.colorbar(heatmap)
    plt.savefig(output_name + '.png')
    plt.clf()

"""    
The shape of Heat map is not square.
 
fig, axes = plt.subplots(nrows=1, ncols=2)
feat = [feat1, feat2]
i = 0
for ax in axes.flat:
    im = ax.imshow(feat[i][0])
    i = i + 1

fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.4)
plt.savefig('c_{}'.format(0) + '.png')
plt.clf()

fig, axes = plt.subplots(nrows=1, ncols=2)
i = 0
for ax in axes.flat:
    im = ax.imshow(feat[i][1])
    i = i + 1

fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.4)
plt.savefig('c_{}'.format(1) + '.png')
plt.clf()
"""

