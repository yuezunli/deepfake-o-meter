import requests, os, time, cv2, pdb


def initial_model(methods):
    urls = []
    for method in methods:
        if method == 'upconv':
            os.system('docker run -p 2500:5000 -v /media/disk/Backup/02congzhang/deepfake/fordocker/a/deepforensics/:/deepforensics/ zhangconghh/upconv:env python deepforensics/server/server_upconv.py -m SVM_CelebA &')
            time.sleep(10)
            print('Load the Upconv Model')
            urls.append('http://0.0.0.0:2500/deepforensics')

        elif method == 'dspfwa':
            os.system('docker run -p 2501:5000 -v /media/disk/Backup/02congzhang/deepfake/fordocker/a/deepforensics/:/deepforensics/ --runtime=nvidia -e NVIDIA_VISIBLE_DEVICE=0 zhangconghh/dspfwa:env python3 deepforensics/server/server_dspfwa.py &')
            time.sleep(10)
            print('Load the DSP-FWA Model')
            urls.append('http://0.0.0.0:2501/deepforensics')
    return urls


methods = ['upconv', 'dspfwa']
urls = initial_model(methods)

img_path = './image/'
for imname in os.listdir(img_path):
    img = cv2.imread(img_path+imname)
    for ith  in range(len(urls)):
        r_score = requests.post(urls[ith], json={'feature': img.tolist()})
        print('Score of '+ imname + ' predicted by ' + methods[ith]+ '  is ' + str(r_score.json()))
