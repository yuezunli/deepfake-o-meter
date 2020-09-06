# DeepFakeOmeter

<img src="static/images/deepfakeometer2.png" alt="logo" width="150"/>


## Preparation

+ change the email information in scanEmail.py

https://github.com/yuezunli/deepfake-o-meter/blob/zc/deepfakeOmeter/scanEmail.py#L44-L47
+ change the local direction of the deepforensics

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
You should make sure environment names are consistent with the names in scanVideo.py.

https://github.com/yuezunli/deepfake-o-meter/blob/zc/deepfakeOmeter/scanVideo.py#L15-L27
+ Run the four python file:
```
python demo_video.py
python scanEmail.py
python scanVideo.py
python scanPort.py
```

## Instruction

This website including four bufen

+ The video Saving
+ video Process
+ Eamil
+ claen port
