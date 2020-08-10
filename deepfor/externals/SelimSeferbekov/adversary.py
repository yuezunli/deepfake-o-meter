"""adversary.py"""
from pathlib import Path
# from model_def import WSDAN, xception
import numpy as np
import torch, cv2, os
import argparse
import os
import re, cv2
import time
import numpy as np
import torch
import pandas as pd
from training.zoo.classifiers import DeepFakeClassifier
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torchvision.transforms import Normalize

mean = torch.tensor([0.485, 0.456, 0.406], dtype=torch.float32)
std = torch.tensor([0.229, 0.224, 0.225], dtype=torch.float32)
un_normalize_transform = Normalize((-mean / std).tolist(), (1.0 / std).tolist())
normalize_transform = Normalize(mean.tolist(), std.tolist())




def cuda(tensor,is_cuda):
    if is_cuda : return tensor.cuda()
    else : return tensor

def where(cond, x, y):
    """
    code from :
        https://discuss.pytorch.org/t/how-can-i-do-the-operation-the-same-as-np-where/1329/8
    """
    cond = cond.float()
    return (cond*x) + ((1-cond)*y)




class Attack(object):
    def __init__(self, criterion, models):
        # self.net = net
        self.criterion = criterion
        self.models = models


    def fgsm(self, x, y, targeted=False, eps=0.03, x_val_min=0, x_val_max=1):

        x_adv = Variable(x, requires_grad=True)
        with torch.no_grad():
            for i in range(len(x_adv)):
                x_adv[i] = normalize_transform(x_adv[i] / 255.)
        h_adv = self.calsc(x_adv, self.models)
        if targeted:
            cost = self.criterion(h_adv, y)
        else:
            cost = -self.criterion(h_adv, y)

        # add noise
        if x_adv.grad is not None:
            x_adv.grad.data.fill_(0)
        cost.backward(retain_graph=True)
        x_adv.grad.sign_()
        # noise = x_adv.grad*127+127
        x_adv = x_adv - eps*x_adv.grad
        # un_normalize_transform
        for i in range(len(x_adv)):
            x_adv[i] = un_normalize_transform(x_adv[i])
        x_adv = torch.clamp(x_adv, x_val_min, x_val_max)


        # save noise image
        # noise = (x_adv - x)*20+127
        # noise = noise.int()
        im3 = x_adv.cpu().detach().numpy()*255
        im3_s =  np.zeros((np.shape(im3)[2],np.shape(im3)[2],3))
        im3_s[:,:,0] = im3[0, 2, :, :]
        im3_s[:,:,1] = im3[0, 1, :, :]
        im3_s[:,:,2] = im3[0, 0, :, :]
        cv2.imwrite('adv.jpg' , im3_s)

        with torch.no_grad():
            for i in range(len(x_adv)):
                x_adv[i] = normalize_transform(x_adv[i])
        score1 = self.calsc(x_adv, self.models)
        print('detect score is', h_adv.cpu().detach().numpy()[0,-1], ', adversary score is', score1.cpu().detach().numpy()[0,-1])

        return x_adv



    def i_fgsm(self, x, y, targeted=False, eps=0.03, alpha=1, iteration=1, x_val_min=-1, x_val_max=1):
        x_adv = Variable(x, requires_grad=True)

        with torch.no_grad():
            for i in range(len(x_adv)):
                x_adv[i] = normalize_transform(x_adv[i] / 255.)
        h_adv0 = self.calsc(x_adv, self.models)
        with torch.no_grad():
            for j in range(len(x_adv)):
                x_adv[j] = un_normalize_transform(x_adv[j])

        for ith in range(iteration):
            with torch.no_grad():
                for i in range(len(x_adv)):
                    x_adv[i] = normalize_transform(x_adv[i])
            h_adv = self.calsc(x_adv, self.models)
            print('Processing the', ith, 'th interation')
            if targeted:
                cost = self.criterion(h_adv, y)
            else:
                cost = -self.criterion(h_adv, y)
            # self.net.zero_grad()
            if x_adv.grad is not None:
                x_adv.grad.data.fill_(0)
            cost.backward(retain_graph=True)
            grad = torch.sign(x_adv.grad.data)
            x_adv = x_adv - alpha*grad
            x_adv = where(x_adv > x+eps, x+eps, x_adv)
            x_adv = where(x_adv < x-eps, x-eps, x_adv)
            with torch.no_grad():
                for j in range(len(x_adv)):
                    x_adv[j] = un_normalize_transform(x_adv[j])
            x_adv = torch.clamp(x_adv, x_val_min, x_val_max)
            x_adv = Variable(x_adv.data, requires_grad=True)


        im3 = x_adv.cpu().detach().numpy()*255
        im3_s =  np.zeros((np.shape(im3)[2],np.shape(im3)[2],3))
        im3_s[:,:,0] = im3[0, 2, :, :]
        im3_s[:,:,1] = im3[0, 1, :, :]
        im3_s[:,:,2] = im3[0, 0, :, :]
        cv2.imwrite('advImageSlim.jpg' , im3_s)
        for i in range(len(x_adv)):
            x_adv[i] = normalize_transform(x_adv[i] / 255.)
        score1 = self.calsc(x_adv, self.models)
        print('detect score is', h_adv0.cpu().detach().numpy()[0,-1], ', adversary score is', score1.cpu().detach().numpy()[0,-1])

        return x_adv



    def calsc(self, im, models):
        preds = []
        ith = 0
        modelth = 1
        for model in models:
            if modelth<=3:
                im = im.to(torch.device("cuda:2"))
            else:
                im = im.to(torch.device("cuda:1"))
            modelth += 1

            y_pred = model(im.half())
            y_pred = torch.sigmoid(y_pred.squeeze())
            bpred = torch.stack([1-y_pred,y_pred],0)
            bpred = torch.unsqueeze(bpred, 0)
            bpred = bpred.to(torch.device("cuda:0"))

            if ith == 0:
                ith += 1
                predsum = bpred
            else:
                ith += 1
                predsum.add_(bpred)

        return predsum.mul_(1/ith)
