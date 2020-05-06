
from __future__ import print_function

import numpy as np
import cv2

if str(cv2.__version__).startswith('3.'):
    CV_CAP_PROP_FRAME_COUNT = cv2.CAP_PROP_FRAME_COUNT
    CV_CAP_PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
    CV_CAP_PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT
    CV_CAP_PROP_FORMAT = cv2.CAP_PROP_FORMAT
    CV_CAP_PROP_FPS = cv2.CAP_PROP_FPS
    CV_CAP_PROP_POS_FRAMES = cv2.CAP_PROP_POS_FRAMES
    CAP_PROP_POS_MSEC = cv2.CAP_PROP_POS_MSEC
    CV_RGB2GRAY = cv2.COLOR_RGB2GRAY
    CV8UC1 = cv2.CV_8UC1
    CV8UC3 = cv2.CV_8UC3
elif str(cv2.__version__).startswith('2.'):
    CV_CAP_PROP_FRAME_COUNT = cv2.cv.CV_CAP_PROP_FRAME_COUNT
    CV_CAP_PROP_FRAME_WIDTH = cv2.cv.CV_CAP_PROP_FRAME_WIDTH
    CV_CAP_PROP_FRAME_HEIGHT = cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
    CV_CAP_PROP_FORMAT = cv2.cv.CV_CAP_PROP_FORMAT
    CV_CAP_PROP_FPS = cv2.cv.CV_CAP_PROP_FPS
    CV_CAP_PROP_POS_FRAMES = cv2.cv.CV_CAP_PROP_POS_FRAMES
    CAP_PROP_POS_MSEC = cv2.cv.CV_CAP_PROP_POS_MSEC
    CV_RGB2GRAY = cv2.cv.CV_RGB2GRAY
    CV8UC1 = cv2.cv.CV_8UC1
    CV8UC3 = cv2.cv.CV_8UC3
else:
    raise ValueError('opencv version should be 2 or 3...')


# ========== Video Modules ==========

# Read a specified frame from a video
# result is numpy img[y,x,c] in RGB
def vid_get_frame_i (video_in, frame_num):
    vidfp = cv2.VideoCapture(video_in)
    vidfp.set(CV_CAP_PROP_POS_FRAMES, frame_num)
    _, bgr_img = vidfp.read()
    if bgr_img is None:
        return bgr_img
    else:
        b, g, r = cv2.split(bgr_img)  # get b,g,r
        rgb_img = cv2.merge([r, g, b])  # switch it to rgb
    return rgb_img


def vid_goto_frame(vidfp, frame_num):
    vidfp.set(CV_CAP_PROP_POS_FRAMES, frame_num)


def vid_read_frame(vidfp):
    _, bgr_img = vidfp.read()
    if bgr_img is None:
        return bgr_img
    else:
        b, g, r = cv2.split(bgr_img)  # get b,g,r
        rgb_img = cv2.merge([r, g, b])  # switch it to rgb
    return rgb_img


# Return the video time of the current frame in ms
def vid_cur_frame_time_ms(vidfp):
    t = vidfp.get(CAP_PROP_POS_MSEC)
    return t


# Read an image sequence from the video
# result is numpy vid[t,y,x,c] in RGB
def vid_read_imgseq(video_in):
    print ('vid_read_imgseq (%s)' % (video_in))
    vidfp = cv2.VideoCapture(video_in)
    imgseq = []
    count = 0
    while True:
        _, bgr_img = vidfp.read()
        if bgr_img is None:
            break
        b, g, r = cv2.split(bgr_img)  # get b,g,r
        rgb_img = cv2.merge([r, g, b])  # switch it to rgb
        imgseq.append(rgb_img)
        print ('%d' % (count), end=' ')
        count += 1
    print ('')
    return np.array(imgseq)


# Read an image sequence from the video
# result is numpy vid[t,y,x]
def vid_read_imgseq_gray(video_in):
    print ('vid_read_imgseq_gray (%s)' % (video_in))
    vidfp = cv2.VideoCapture(video_in)
    imgseq = []
    count = 0
    while True:
        _, bgr_img = vidfp.read()
        if bgr_img is None:
            break
        gray = cv2.cvtColor(bgr_img, CV_RGB2GRAY)
        imgseq.append(gray)
        print ('%d' % (count)),
        count += 1
    print ('')
    return np.array(imgseq)


# input imgseq is [t,y,x,c] in BGR, output is [t,y,x]
def imgseq_color_to_gray(imcseq):
    NF = imcseq.shape[0]
    NY = imcseq.shape[1]
    NX = imcseq.shape[2]
    imgseq = np.zeros((NF, NY, NX), 'uint8')
    for f in ranges(NF):
        bgr_img = imcseq[f]
        gray = cv2.cvtColor(bgr_img, CV_RGB2GRAY)
        imgseq[f] = gray
    return imgseq


# count total number of frames in the input video
def vid_count_num_frames(video_in):
    vidfp = cv2.VideoCapture(video_in)
    if not vidfp.isOpened():
        print ('could not open :', video_in)
        return

    length = int(vidfp.get(CV_CAP_PROP_FRAME_COUNT))
    return length


# count total number of frames in the input video
def vid_get_video_dim(vidfp):
    if not vidfp.isOpened():
        print ('vid_get_dim error: vidfp is not opened')
        return

    length = int(vidfp.get(CV_CAP_PROP_FRAME_COUNT))
    width = int(vidfp.get(CV_CAP_PROP_FRAME_WIDTH))
    height = int(vidfp.get(CV_CAP_PROP_FRAME_HEIGHT))
    format = int(vidfp.get(CV_CAP_PROP_FORMAT))
    if format == CV8UC1:
        channel = 1
    elif format == CV8UC3:
        channel = 3
    else:
        channel = 0  # !! Wrong
    fps = vidfp.get(CV_CAP_PROP_FPS)
    return length, width, height, channel, fps


# write [t,y,x,c] numpy array to video.avi
# See http://docs.opencv.org/trunk/doc/py_tutorials/py_gui/py_video_display/py_video_display.html
def write_imgseq_to_video(imgseq, name, FOURCC='XVID'):
    # NT = imgseq.shape[0]
    NY = imgseq.shape[1]
    NX = imgseq.shape[2]
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # fourcc = cv2.cv.CV_FOURCC('M','J','P','G')
    if FOURCC == 'XVID':
        fourcc = cv2.cv.CV_FOURCC('X', 'V', 'I', 'D')
    fps = 25
    isColor = False
    if imgseq.ndim > 3:
        isColor = True
    vw = cv2.VideoWriter(name, fourcc, fps, (NX, NY), isColor)
    for rgb_img in imgseq:
        # convert rgb_img to bgr_img
        r, g, b = cv2.split(rgb_img)
        bgr_img = cv2.merge([b, g, r])
        vw.write(bgr_img)
    vw.release()


# count total number of frames in the input video
# This is the dumb way (slow).
"""
def vid_count_num_frames_old (video_in):
  vidfp = cv2.VideoCapture (video_in)
  count = 0
  while True:
    _,img = vidfp.read()
    if img is None:
      break
    count += 1
  return count
"""


#################################################

# Calculate video time for a given frame #
def frame_to_video_time(vidfp, vid_fps, f=None):
    # https://stackoverflow.com/questions/37695376/python-and-opencv-getting-the-duration-time-of-a-video-at-certain-points
    # If the input current_frame_number f is None, use CAP_PROP_POS_MSEC
    # Otherwise calculate from video FPS
    if f is None:
        videotime_ms = ocv_vid.vid_cur_frame_time_ms(vidfp)
        videotime_s = videotime_ms / 1000.0
    else:
        videotime_s = float(f) / vid_fps
    return videotime_s


def time_s_to_hms(s):
    # https://stackoverflow.com/questions/1384406/python-convert-seconds-to-hhmmss
    seconds = int(s)
    hours = seconds // 3600  # (60*60)
    seconds %= 3600  # (60*60)
    minutes = seconds // 60
    seconds %= 60
    ss = (s - int(s)) * 100
    return "%02i:%02i:%02i.%02i" % (hours, minutes, seconds, ss)


def video_time_to_frame(vid_fps, time):
    time = time.replace(':', ' ')
    time = time.replace('.', ' ')
    res = map(int, time.split())
    # h, m, s, ss = map (int, time.split())
    if len(res) > 0:
        h = res[0]
    else:
        print ('video_time_to_frame() hour:x:x.x not found')
        h = 0
    if len(res) > 1:
        m = res[1]
    else:
        print ('video_time_to_frame() x:minute:x.x not found')
        m = 0
    if len(res) > 2:
        s = res[2]
    else:
        print ('video_time_to_frame() x:x:second.x not found')
        s = 0
    if len(res) > 3:
        ss = res[3]
    else:
        print ('video_time_to_frame() x:x:x.ss not found')
        ss = 0

    t = h * 3600 + m * 60 + s + ss / 100.0
    f = int(t * vid_fps)
    print ('video_time_to_frame() %s --> %f sec, frame %d' % (time, t, f))
    return f



