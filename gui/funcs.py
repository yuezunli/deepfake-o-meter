import sys
sys.path.insert(0, '..')
from py_utils.vid_utils import proc_vid as pv
from py_utils.vid_utils import proc_aud as pa
from py_utils.face_utils import lib
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F


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


def im_test(net, im, front_face_detector, lmark_predictor):
    sample_num = 10
    face_info = lib.align(im[:, :, (2,1,0)], front_face_detector, lmark_predictor)
    # Samples
    if len(face_info) == 0:
        prob = -1
    else:
        _, point = face_info[0]
        rois = []
        for i in range(sample_num):
            roi, _ = lib.cut_head([im], point, i)
            rois.append(cv2.resize(roi[0], (224, 224)))

        # vis_ = np.concatenate(rois, 1)
        # cv2.imwrite('vis.jpg', vis_)

        bgr_mean = np.array([103.939, 116.779, 123.68])
        bgr_mean = bgr_mean[np.newaxis, :, np.newaxis, np.newaxis]
        bgr_mean = torch.from_numpy(bgr_mean).float().cuda()

        rois = torch.from_numpy(np.array(rois)).float().cuda()
        rois = rois.permute((0, 3, 1, 2))
        prob = net(rois - bgr_mean)
        prob = F.softmax(prob, dim=1)
        prob = prob.data.cpu().numpy()
        prob = 1 - np.mean(np.sort(prob[:, 0])[np.round(sample_num / 2).astype(int):])
    return prob, face_info


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


def gen_plot_vid_v2(frame_num, frame_id, fps, prob_list, vid_prob):
    params = {}
    params['title'] = 'Video Integrity Score = {:.2f}'.format(vid_prob)
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


def draw_face_score(im, face_info, prob):
    if len(face_info) == 0:
        return im

    _, points = np.array(face_info[0])
    x1 = np.min(points[:, 0])
    x2 = np.max(points[:, 0])
    y1 = np.min(points[:, 1])
    y2 = np.max(points[:, 1])

    # Real: (0, 255, 0), Fake: (0, 0, 255)
    color = (0, prob * 255, (1 - prob) * 255)
    cv2.rectangle(im, (x1, y1), (x2, y2), color, 10)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(im, '{:.3f}'.format(prob), (x1, y1 - 10), font, 1, color, 3, cv2.LINE_AA)
    return im
