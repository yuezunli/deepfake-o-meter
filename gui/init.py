# import tensorflow as tf
import sys, yaml, dlib
from easydict import EasyDict as edict
sys.path.append('../')
from py_utils.DL.pytorch_utils.models.classifier import SPPNet
import torch

net = SPPNet(backbone=50, num_class=2, pretrained=False)
checkpoint = torch.load('/home/lyz/0-Yuezun/Code-origin/bitbucket/face-artifacts-pytorch/model/ckpt/SPP-res50.pth')
net.load_state_dict(checkpoint['net'])
net = net.cuda()
net.eval()

# Employ dlib to extract face area and landmark points
front_face_detector = dlib.get_frontal_face_detector()
lmark_predictor = dlib.shape_predictor('../dlib_model/shape_predictor_68_face_landmarks.dat')
