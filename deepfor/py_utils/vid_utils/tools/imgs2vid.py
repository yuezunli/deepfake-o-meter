import cv2, os, sys
sys.path.append('..')
import proc_vid as pv
import argparse


def main(args):
    imgs_list = sorted(os.listdir(args.data_dir))
    imgs = []
    for fp in imgs_list:
        if '.jpg' not in fp:
            continue
        im = cv2.imread(os.path.join(args.data_dir, fp))
        imgs.append(im)

    pv.gen_vid(video_path=args.output_path, imgs=imgs, fps=args.fps)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generating video from images')
    parser.add_argument('--data_dir', type=str)
    parser.add_argument('--output_path', type=str)
    parser.add_argument('--fps', type=int, default=30)
    args = parser.parse_args()
    main(args)


