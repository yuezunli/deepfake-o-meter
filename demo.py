import cv2
import deepfor

# Read image
img = cv2.imread('test_img.png')    
conf = deepfor.DSPFWA().run(img) # conf of fake
print('Fake confidence score is: {}'.format(conf))

    
