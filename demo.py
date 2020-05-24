import cv2
import deepfor

# Read image
img = cv2.imread('test_img.png')
<<<<<<< HEAD
conf = deepfor.EVA().run(img) # conf of fake
=======
conf = deepfor.DSPFWA().run(img) # conf of fake
>>>>>>> b6d5c9268afef0721b8e5b7b1726923b0bd71b2b
print('Fake confidence score is: {}'.format(conf))
