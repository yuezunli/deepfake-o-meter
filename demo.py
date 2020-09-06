import cv2, os
import deepfor
import warnings

warnings.filterwarnings('ignore')
# Read image
img = cv2.imread('deepforensics/test_img.png')
conf = deepfor.CNNDetection().run(img) # conf of fake
print('Fake confidence score is: {}'.format(conf))
