import cv2, os
import deepfor
import warnings
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--img', type=str, help='image path')
parser.add_argument(
    '--name',
    type=str,
    help=
    'Method Name: MesoNet, XceptionNet, ClassNSeg, VA, CapsuleNet, FWA, DSPFWA, Upconv, WM, SelimSeferbekov, CNNDetection',
    default='XceptionNet')
args = parser.parse_args()

warnings.filterwarnings('ignore')
# Read image
img = cv2.imread(args.img)
exec('detector = deepfor.{}()'.format(args.name))
conf = detector.run(img)  # conf of fake
print('Fake confidence score is: {}'.format(conf))
