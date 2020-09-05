import cv2, os
import deepfor
import warnings
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '--name',
    type=str,
    help=
    'Method Name: MesoNet, XceptionNet, ClassNSeg, VA, CapsuleNet, FWA, DSPFWA, Upconv, WM, SelimSeferbekov, CNNDetection',
    default='XceptionNet')
args = parser.parse_args()

name = args.name

warnings.filterwarnings('ignore')
# Read image
img = cv2.imread('test_img.png')
exec('detector = deepfor.{}()'.format(name))
conf = detector.run(img)  # conf of fake
print('Fake confidence score is: {}'.format(conf))
