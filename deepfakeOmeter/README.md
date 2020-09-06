# DeepFakeOmeter

<img src="static/images/deepfakeometer2.png" alt="logo" width="150"/>


## Preparation

+ change the email information in scanEmail.py

https://github.com/yuezunli/deepfake-o-meter/blob/zc/deepfakeOmeter/scanEmail.py#L44-L47
+ change the local direction of the deepforensics in scanVideo.py

https://github.com/yuezunli/deepfake-o-meter/blob/zc/deepfakeOmeter/scanVideo.py#L30

+ change the enviroment

 First, you should set up the environment for each method, and run the following code:
 ```
 docker build -t capsulenet ./dockerfile/CapsuleNet/
 docker build -t classnseg ./dockerfile/ClassNSeg/
 docker build -t cnndetection ./dockerfile/CNNDetetion/
 docker build -t dspfwa ./dockerfile/DSPFWA/
 docker build -t fwa ./dockerfile/FWA/
 docker build -t mesonet ./dockerfile/MesoNet/
 docker build -t selim ./dockerfile/SelimSefer/
 docker build -t upconv ./dockerfile/Upconv/
 docker build -t va ./dockerfile/VA/
 docker build -t wm ./dockerfile/WM/
 docker build -t xception ./dockerfile/XceptionNet/
 ```
Then, you should make sure environment names are consistent with the names in scanVideo.py.

https://github.com/yuezunli/deepfake-o-meter/blob/zc/deepfakeOmeter/scanVideo.py#L15-L27
+ Run the four python files:
```
python demo_video.py
python scanVideo.py
python scanEmail.py
python scanPort.py
```

## Instruction

This website including four components.

+ Monitor the submission from the website. The demo_video.py will save the submitted video and detection methods under the tmp folder named by its submission email and submission time. You can directly upload the video or upload an url.
+ Monitor the submission video. Once the video has been completely saved, the  scanVideo.py will detect the signal and analysis the submission video with its selected methods.
+ Send the E-mail. When finish analysising the video, we will send an e-mail to te user to inform him to download the result in 5 days.
+ Clean ports. Since we will open a port for each submission, we will automatically close the ports opened 5 days ago.
