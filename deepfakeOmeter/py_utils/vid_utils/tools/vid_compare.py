import sys
sys.path.append('..')
import proc_vid as pv
import numpy as np
import argparse
import cv2

def main(args):
    imgs1, frame_num1, fps1, width1, height1 = pv.parse_vid(args.data_path1)
    imgs2, frame_num2, fps2, width2, height2 = pv.parse_vid(args.data_path2)

    num = np.minimum(frame_num1, frame_num2)
    vis_list = []
    for i in range(num):
        width = np.minimum(width1, width2)
        height = np.minimum(height1, height2)
        imgs1[i] = cv2.resize(imgs1[i], (width, height))
        imgs2[i] = cv2.resize(imgs2[i], (width, height))
        vis_im = np.concatenate([imgs1[i], imgs2[i]], axis=1)
        vis_list.append(vis_im)
    pv.gen_vid(video_path=args.output_path, imgs=vis_list, fps=fps1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generating video from images')
    parser.add_argument('--data_path1', type=str)
    parser.add_argument('--data_path2', type=str)
    parser.add_argument('--output_path', type=str)
    args = parser.parse_args()
    main(args)


