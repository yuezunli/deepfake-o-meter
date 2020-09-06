import cv2, os, sys
sys.path.append('..')
import proc_vid as pv
import argparse


def main(args):
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    imgs, frame_num, fps, width, height = \
        pv.parse_vid(args.vid_path)
    for i, im in enumerate(imgs):
        name = '{:05d}.jpg'.format(i)
        if args.image_size != 0:
            im = cv2.resize(im, (args.image_size, args.image_size))
        cv2.imwrite(os.path.join(args.output_dir, name), im)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generating video from images')
    parser.add_argument('--vid_path', type=str)
    parser.add_argument('--output_dir', type=str)
    parser.add_argument('--image_size', type=int, default=256)
    args = parser.parse_args()
    main(args)


