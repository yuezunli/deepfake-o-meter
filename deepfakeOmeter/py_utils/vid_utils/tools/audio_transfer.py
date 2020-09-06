
import argparse, sys
sys.path.append('../')
from proc_aud import audio_transfer


def main(args):
    output = args.dst.split('.')[0] + '_audio.mp4'
    audio_transfer(args.src, args.dst, output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Transferring audio')
    parser.add_argument('--src', type=str)
    parser.add_argument('--dst', type=str)
    args = parser.parse_args()
    main(args)