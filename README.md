# DeepForensics

<img src="assets/logo.jpg" alt="logo" width="150"/>

This repository is a python library, which incorperates existing deepfake detection method into an unified framework. 

## Introduction
To date, this toolbox supports following methods: 

| Methods     | Platform            | Required Packages | Modes  | Download |
|----------   |:-------------:      |------:            |------: | ------:  |
| XceptionNet |  py3, pytorch-1.0.1 | pretrainmodels | c23, c40, raw | [Link](https://drive.google.com/open?id=1FjbSxvLR0YVao5ykLGIFj47FVe6eDTNh) |
| MesoNet     |  py3, keras-2.1.5, tf-1.5 |   -   | meso4,mesoinception4 | [Link](https://drive.google.com/open?id=13ChUtbxuqBS4-kRv8BkSKcb-8hDUi3bO) |  
| VA          |  py3                | - | - | [Link](https://drive.google.com/open?id=1MI8YNJ9tnHD6551bxLDl0BngcQyFXxNB) | 
| ClassNSeg   |  py3, pytorch-1.0.1 | - | - | [Link](https://drive.google.com/open?id=1wMpamO38F2tEYH2iNtUVv2yrt2b1osIG) |
| Capsule     |  py3, pytorch-1.0.1 | - | - | [Link](https://drive.google.com/open?id=13XLA8j_Y7XhW8a7opEh4vQvmr3QyOSmz) | 
| FWA         |  py2, tf-1.5        | - | - | [Link](https://drive.google.com/open?id=1mMeVpNub67dNvSvjvwYbx047g1snGo1m) | 
| DSP-FWA     |  py3, pytorch-1.0.1 | - | - | [Link](https://drive.google.com/open?id=1IN7lkav8UbDacCWpO8Cio2ogAas7auvG) |

For the details of each method, please look into our [paper](https://arxiv.org/pdf/1909.12962.pdf.)

## Quick Start

The original method (with slight modification for intergration) can be downloaded from the link shown in above table. Unzip the method to folder `externals`. Then run the following code:

```
import cv2
import deepfor

# Read image
img = cv2.imread('test_img.png')    
conf = deepfor.DSPFWA().run(img) # conf of fake
print('Fake confidence score is: {}'.format(conf))

```

## Logs
* [4/13/2020] The first stage is all set, where seven methods are included.

## Comming Soon
We will employ docker to handle platform issue of each method.

## Citation

Please cite our paper in your publications if this toolbox is used in your research:

```
@inproceedings{Celeb_DF_cvpr20,
   author = {Yuezun Li, Xin Yang, Pu Sun, Honggang Qi and Siwei Lyu},
   title = {Celeb-DF: A Large-scale Challenging Dataset for DeepFake Forensics},
   booktitle= {IEEE Conference on Computer Vision and Patten Recognition (CVPR)},
   year = {2020}
}
```

## To whom may be interested in incorperating their methods into this toolbox 

If you are interested in incorperating your method into this toolbox, please provide interface functions in a python file as follows:

````
# For instance, the interface file is called utils.py, which should contain four functions

def init_model(*args); # This is for initializing the network
def crop_face(*args); # Crop the faces from input image
def preproc(*args); # Any pre-processing operation on cropped faces, eg, normalization
def predict(*args); # Predictions of your method by taking the processed face as input
````
With these interfaces, we can intergrate your method more conviniently.

## Contributors
* [Yuezun Li](https://www.albany.edu/~yl149995/)
* Pu Sun