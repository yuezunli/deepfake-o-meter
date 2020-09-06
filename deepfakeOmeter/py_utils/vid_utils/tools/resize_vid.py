import cv2, os, sys
sys.path.append('..')
import proc_vid as pv
import argparse

parser = argparse.ArgumentParser(
        description='resize video')
parser.add_argument('--input_path', type=str)
parser.add_argument('--output_path', type=str)
parser.add_argument('--scale', type=float, default=0)
parser.add_argument('--size', type=str, default='256,256', help='h,w')
args = parser.parse_args()

if args.scale != 0:
    pv.resize_video(args.input_path, w=None, h=None, scale=args.scale, out_path=args.output_path)
else:
    size = [int(item) for item in args.size.split(',')]
    pv.resize_video(args.input_path, w=size[1], h=size[0], scale=args.scale, out_path=args.output_path)