import requests
import cv2


im = cv2.imread('Selection_001.png')
url = 'http://169.226.117.97:2500/deepforensics'
resp = requests.post(url, json={'feature': im.tolist()}).json()
print(resp)