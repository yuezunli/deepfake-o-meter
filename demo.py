import cv2, os
import deepfor

# Read image
os.environ["CUDA_VISIBLE_DEVICES"]= '3'
img = cv2.imread('test_img.png')
conf = deepfor.FWA().run(img) # conf of fake
print('Fake confidence score is: {}'.format(conf))
