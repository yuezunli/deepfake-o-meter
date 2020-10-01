# -*- coding: gbk -*-

import cv2, os, time, sys, pdb
pwd =os.path.dirname(os.path.abspath(__file__))
root_dir = pwd + '/../'
sys.path.append(root_dir)
import numpy as np
from gui import utils
import  pdb, argparse
from PIL import Image
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import requests
import deepfor


def gen_vid(video_path, imgs, fps, width=None, height=None):
    # Combine video
    ext = video_path.split('.')[-1]
    if ext == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
        # How to use H264 if install opencv by pip install opencv-python?
        # x264 encoding falls under GPL license in FFmpeg.
        # Unfortunately you have to do a manual build if you wish to use x264 encoder.
        # Installing libx264-dev will not help. You can't use global system packages with opencv-python,
        # Python's wheel format is self contained and already includes all the necessary dependencies.
    elif ext == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')  #*'XVID')
    else:
        # if not .mp4 or avi, we force it to mp4
        video_path = video_path.replace(ext, '.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
    if width is None or height is None:
        height, width = imgs[0].shape[:2]
    else:
        imgs_ = [cv2.resize(img, (width, height)) for img in imgs]
        imgs = imgs_

    out = cv2.VideoWriter(video_path, fourcc, fps, (np.int32(width), np.int32(height)))

    for image in imgs:
        out.write(np.uint8(image))  # Write out frame to video

    # Release everything if job is finished
    out.release()
    print('The output video is ' + video_path)





def AnalysisVideo(method, input_vid_path):

    vid_name = os.path.basename(input_vid_path).split('/')[-1].split('.')[0]
    imgs, frame_num, fps, width, height = utils.parse_vid(input_vid_path)
    print(len(imgs),vid_name, method)
    pathToSave = os.path.join(os.path.dirname(__file__), 'result', input_vid_path.split('/')[-3], input_vid_path.split('/')[-2])


    if method ==  'DSP-FWA':
        model = deepfor.DSPFWA()
    elif method == 'Upconv':
        model = deepfor.Upconv()
    elif method == 'WM':
        model = deepfor.WM()
    elif method =='Capsule':
        model = deepfor.CapsuleNet()
    elif method =='ClassNSeg':
        model = deepfor.ClassNSeg()
    elif method =='XceptionNet':
        model = deepfor.XceptionNet()
    elif method =='VA':
        model = deepfor.VA()
    elif method =='CNNDetection':
        model = deepfor.CNNDetection()
    elif method =='Selim':
        model = deepfor.SelimSeferbekov()
    elif method =='MesoNet':
        model = deepfor.MesoNet()
    elif method =='FWA':
        model = deepfor.FWA()


    prob = []
    final_vis = []
    imgnum = len(imgs)

    for ith in range(imgnum):
        im = imgs[ith]
        score = model.run(im)
        prob.append(1-score)
        print(ith, score)
        max_height = 400
        max_width = 800
        scale = np.minimum(float(max_height) / height, float(max_width) / width)
        vis_im = cv2.resize(im, None, None, fx=scale, fy=scale)
        prob_plot = utils.gen_plot_vid(frame_num, ith, fps, prob)[:, :, (2, 1, 0)]
        scale1 = float(vis_im.shape[0]) / prob_plot.shape[0]
        plot = cv2.resize(prob_plot, None, None, fx=scale1, fy=scale1)
        final_vis_iim = np.concatenate([vis_im,  plot], axis=1)
        final_vis.append(final_vis_iim  )

    gen_vid(os.path.join(pathToSave, vid_name+method+'.mp4'), np.array(final_vis)[:, :, :,:], fps)


    # save jpeg score
    prob = np.array(prob)
    plt.plot(range(len(prob)), sorted(prob, reverse=True), 'r-', linewidth=2.0)
    plt.ylim(0, 1.0)
    plt.xlabel('Frames')
    plt.ylabel('Frame Integrity Score')
    plt.grid()
    plt.title('The Average Score is %.3f' % np.average(np.array(prob)))
    jpgpath = './static/jpg/'
    plt.savefig(os.path.join(pathToSave, vid_name+method+'.jpg'))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', help='Model Name', default='WM')
    parser.add_argument('-v', '--video', help='Video Path', default='test.mp4')
    args = parser.parse_args()


    model =  args.model
    input_vid_path = args.video
    AnalysisVideo(model,  input_vid_path)
