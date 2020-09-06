import sys
sys.path.insert(0, '..')
from py_utils.vid_utils import proc_vid as pv
from py_utils.vid_utils import proc_aud as pa
from py_utils.face_utils import lib
import cv2, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
# import torch
# import torch.nn.functional as F

def gen_vid_with_aud(imgs, fps, out_dir, vid_name, input_vid_path):
    # self.final_vis, fps, self.out_dir, vid_name, input_vid_path
    pv.gen_vid('tmp.mp4', np.array(imgs)[:, :, :, (2, 1, 0)], fps)
    pa.audio_transfer(input_vid_path, 'tmp.mp4', os.path.join(out_dir, vid_name + '_vis.mp4'))
    os.remove('tmp.mp4')

def parse_vid(input_vid_path):
    return pv.parse_vid(input_vid_path)


def draw2D(X, Y, order, xname, yname, params, xlim=None, ylim=None, rcparams=None, idx=None):
    title = params['title']
    colors = params['colors']
    markers = params['markers']
    linewidth = params['linewidth']
    markersize = params['markersize']
    figsize = params['figsize']
    legend_loc = params['legend_loc']
    is_legend = params['is_legend']

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
        if idx is not None:
            plt.plot(X[i][idx], Y[i][idx], 'o', markersize=10, color='r')

    plt.grid()
    if is_legend:
        plt.legend(loc=legend_loc)
    fig.canvas.draw()
    # grab the pixel buffer and dump it into a numpy array
    im = np.array(fig.canvas.renderer._renderer)[:, :, :-1]
    # plt.show()
    plt.close()
    return im[:, :, (2, 1, 0)]


def draw2D_v1(X, Y, order, xname, yname, params, xlim=None, ylim=None, rcparams=None, idx=None, method=None):
    title = params['title']
    colors = params['colors']
    markers = params['markers']
    linewidth = params['linewidth']
    markersize = params['markersize']
    figsize = params['figsize']
    legend_loc = params['legend_loc']
    is_legend = params['is_legend']

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

    fig = plt.figure(facecolor='white',figsize=figsize)
    plt.title(title)
    plt.ylabel(yname)
    if ylim is not None:
        plt.ylim(ylim[0], ylim[1])
    plt.xlabel(xname)
    if xlim is not None:
        plt.xlim(xlim[0], xlim[1])

    for ith, YY in enumerate(Y):
        YY = [YY]
        for i, type_name in enumerate(order):
            plt.plot(X[i], YY[i], colors[ith], label=method[ith], linewidth=linewidth, markersize=markersize, marker=markers[i])
            if idx is not None:
                plt.plot(X[i][idx], YY[i][idx], 'o', markersize=10, color='r')

    plt.legend(loc='upper right')
    plt.grid()
    if is_legend:
        plt.legend(loc=legend_loc)
    fig.canvas.draw()
    # grab the pixel buffer and dump it into a numpy array
    im = np.array(fig.canvas.renderer._renderer)[:, :, :-1]
    # plt.show()
    plt.close()
    return im[:, :, (2, 1, 0)]


def gen_plot_vid(frame_num, frame_id, fps, prob_list):
    params = {}
    params['title'] = ' '
    params['colors'] = ['b-']
    params['markers'] = [None]
    params['linewidth'] = 3
    params['markersize'] = None
    params['figsize'] = None
    params['is_legend'] = False
    params['legend_loc'] = 0

    prob_ary = np.array(prob_list)
    prob_ary[prob_ary == -1] = 0.5  # For better visualization

    # Vis plots
    max_X = frame_num / fps
    prob_plot = draw2D([np.arange(frame_num)[:frame_id+1] / fps],
                            [prob_ary[:frame_id+1]],
                            order=[''],
                            xname='Seconds',
                            yname='Frame Integrity Score',
                            params=params,
                            xlim=[0, max_X],
                            ylim=[-0.1, 1.1],
                            idx=frame_id)
    return prob_plot


def gen_plot_vid_v1(frame_num, frame_id, fps, prob_list):
    params = {}
    params['title'] = ' '
    params['colors'] = ['b-', 'g-', 'r-', 'c-', 'm-',  'y-', 'k-']
    params['markers'] = [None]
    params['linewidth'] = 3
    params['markersize'] = None
    params['figsize'] = None
    params['is_legend'] = False
    params['legend_loc'] = 0

    prob_ary = []
    method = []
    for key in prob_list.keys():
        method.append(key)
        prob_ary.append(np.array(prob_list[key]))
    prob_ary = np.array(prob_ary)
    prob_ary[prob_ary == -1] = 0.5  # For better visualization

    max_X = frame_num / fps
    prob_plot = draw2D_v1([np.arange(frame_num)[:frame_id+1] / fps],
                            prob_ary[:, :frame_id+1],
                            order=[''],
                            xname='Seconds',
                            yname='Frame Integrity Score',
                            params=params,
                            xlim=[0, max_X],
                            ylim=[-0.1, 1.1],
                            idx=frame_id,
                            method=method)
    return prob_plot


def gen_plot_vid_v2(frame_num, frame_id, fps, prob_list, vid_prob):
    params = {}
    params['title'] = 'Video Integrity Score = {:.2f}'.format(vid_prob)
    params['colors'] = ['b-', 'g-', 'r-', 'c-', 'm-',  'y-', 'k-']
    params['markers'] = [None]
    params['linewidth'] = 3
    params['markersize'] = None
    params['figsize'] = None
    params['is_legend'] = False
    params['legend_loc'] = 0

    prob_ary = np.array(prob_list)
    prob_ary[prob_ary == -1] = 0.5  # For better visualization

    # Vis plots
    max_X = frame_num / fps
    prob_plot = draw2D([np.arange(frame_num) / fps],
                            [prob_ary],
                            order=[''],
                            xname='Seconds',
                            yname='Frame Integrity Score',
                            params=params,
                            xlim=[0, max_X],
                            ylim=[-0.1, 1.1],
                            idx=frame_id)
    return prob_plot


def draw_face_score(im, face_loc, prob):
    if len(face_loc) == 0:
        return im

    # _, points = np.array(face_info)
    # x1 = np.min(points[:, 0])
    # x2 = np.max(points[:, 0])
    # y1 = np.min(points[:, 1])
    # y2 = np.max(points[:, 1])
    x1, y1, x2, y2 = face_loc

    # Real: (0, 255, 0), Fake: (0, 0, 255)
    color = (0, prob * 255, (1 - prob) * 255)
    cv2.rectangle(im, (x1, y1), (x2, y2), color, 10)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(im, '{:.3f}'.format(prob), (x1, y1 - 10), font, 1, color, 3, cv2.LINE_AA)
    return im


def draw_face_score_v1(im, face_locs, probs):

    for key in probs.keys():
        # import pdb; pdb.set_trace()
        face_loc = face_locs[key]
        prob = probs[key]
        if len(face_loc) == 0:
            continue

        x1, y1, x2, y2 = face_loc
        # Real: (0, 255, 0), Fake: (0, 0, 255)
        color = (0, prob * 255, (1 - prob) * 255)
        cv2.rectangle(im, (x1, y1), (x2, y2), color, 10)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(im, key+'{:.3f}'.format(prob), (x1, y1 - 10), font, 1, color, 3, cv2.LINE_AA)
    return im
