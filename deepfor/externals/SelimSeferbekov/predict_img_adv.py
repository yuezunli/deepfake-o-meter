import argparse
import os
import re, cv2
import time
import torch.nn as nn
import numpy as np
import torch
import pandas as pd
from kernel_utils import VideoReader, FaceExtractor, confident_strategy, predict_on_video_set, predict_on_image_adv
from training.zoo.classifiers import DeepFakeClassifier
# os.environ["CUDA_VISIBLE_DEVICES"]= '0,1'

imname = '/media/disk/Backup/02congzhang/deepfake/deepforensics/0621/deepforensics/image/image0.jpg'
wightpath = '/media/disk/Backup/02congzhang/deepfake/dfdc/1/dfdc_deepfake_challenge/weights/'
modellsit = ['final_111_DeepFakeClassifier_tf_efficientnet_b7_ns_0_36']
modellsit = ['final_111_DeepFakeClassifier_tf_efficientnet_b7_ns_0_36',
    'final_555_DeepFakeClassifier_tf_efficientnet_b7_ns_0_19', 'final_777_DeepFakeClassifier_tf_efficientnet_b7_ns_0_31',
    'final_888_DeepFakeClassifier_tf_efficientnet_b7_ns_0_37', 'final_888_DeepFakeClassifier_tf_efficientnet_b7_ns_0_40',
    'final_999_DeepFakeClassifier_tf_efficientnet_b7_ns_0_23']

img = cv2.imread(imname)
input_size = 380
models = []
model_paths = [os.path.join(wightpath, model) for model in modellsit]
ith =  1
for path in model_paths:
    model = DeepFakeClassifier(encoder="tf_efficientnet_b7_ns").to("cuda")
    if ith<=3:
        model.to(torch.device("cuda:2"))
    else:
        model.to(torch.device("cuda:1"))
    ith+=1
    print("loading state dict {}".format(path))
    checkpoint = torch.load(path, map_location="cpu")
    state_dict = checkpoint.get("state_dict", checkpoint)
    model.load_state_dict({re.sub("^module.", "", k): v for k, v in state_dict.items()}, strict=False)
    model.eval()
    del checkpoint
    models.append(model.half())

frames_per_video = 32
strategy = confident_strategy
video_reader = VideoReader()
video_read_fn = lambda x: video_reader.read_frames(x, num_frames=frames_per_video)
face_extractor = FaceExtractor(video_read_fn)
prediction = predict_on_image_adv(face_extractor=face_extractor, img=img, input_size=input_size,
                        models=models, strategy=strategy, apply_compression=False)
