
import os, sys
pwd = os.path.dirname(__file__)
sys.path.append(pwd + '/../../')
import py_utils.face_utils.lib as lib
from py_utils.face_utils.umeyama import umeyama
import numpy as np
import dlib, os


class Flib(object):
    def __init__(self):
        self._face_detector = None
        self._face_detector_mode = None
        self._lmark_predictor = None
        self._face_rec = None

    def set_face_detector(self, mode='front'):
        if mode == 'front':
            self._face_detector = dlib.get_frontal_face_detector()            
        if mode == 'cnn':
            if not dlib.DLIB_USE_CUDA:
                print('@ dlib is not using CUDA.')
            self._face_detector = dlib.cnn_face_detection_model_v1(pwd + '/dlib_model/mmod_human_face_detector.dat') 
        self._face_detector_mode = mode
        return self._face_detector 

    def set_landmarks_predictor(self, mode=5):
        # mode is 5 or 68
        self._lmark_predictor = dlib.shape_predictor(pwd + '/dlib_model/shape_predictor_{}_face_landmarks.dat'.format(mode)) 
        return self._lmark_predictor

    def set_face_rec(self):
        self._face_rec = dlib.face_recognition_model_v1(pwd + '/dlib_model/dlib_face_recognition_resnet_model_v1.dat')
        return self._face_rec

    def face_verify(self, im1, im2, thres=0.6):
        # im1 im2 rgb order
        dets1 = self._face_detector(im1, 1)
        dets2 = self._face_detector(im2, 1)

        try:
            shape1 = self._lmark_predictor(im1, dets1[0])
            shape2 = self._lmark_predictor(im2, dets2[0])
        except:
            shape1 = self._lmark_predictor(im1, dets1[0].rect)
            shape2 = self._lmark_predictor(im2, dets2[0].rect)

        face_descriptor1 = np.array(self._face_rec.compute_face_descriptor(im1, shape1))
        face_descriptor2 = np.array(self._face_rec.compute_face_descriptor(im2, shape2))
        distance = np.sqrt(np.sum(np.power(face_descriptor1 - face_descriptor2, 2)))
        result = True if distance < thres else False
        return result

    def align(self, im, scale=0):
        # This version we handle all faces in view
        # channel order rgb
        im = np.uint8(im)
        faces = self._face_detector(im, scale)
        face_list = []
        if faces is not None or len(faces) > 0:
            for pred in faces:
                try:
                    points = lib.shape_to_np(self._lmark_predictor(im, pred))  # xy
                except:
                    points = lib.shape_to_np(self._lmark_predictor(im, pred.rect))
                trans_matrix = umeyama(points[17:], lib.landmarks_2D, True)[0:2]
                face_list.append([trans_matrix, points])
        return face_list

    def get_face_loc(self, im, scale=0):
        """ get face locations, color order of images is rgb """
        faces = self._face_detector(np.uint8(im), scale)
        face_list = []
        if faces is not None or len(faces) > 0:
            for i, d in enumerate(faces):
                try:
                    face_list.append([d.left(), d.top(), d.right(), d.bottom()])
                except:
                    face_list.append([d.rect.left(), d.rect.top(), d.rect.right(), d.rect.bottom()])
        return face_list

    def get_face_loc_landmarks(self, im, scale=0):
        """ get face locations, color order of images is rgb """
        faces = self._face_detector(np.uint8(im), scale)
        face_list = []
        if faces is not None or len(faces) > 0:
            for i, d in enumerate(faces):
                try:
                    loc = [d.left(), d.top(), d.right(), d.bottom()]
                    points = lib.shape_to_np(self._lmark_predictor(im, d))
                except:
                    loc = [d.rect.left(), d.rect.top(), d.rect.right(), d.rect.bottom()]
                    points = lib.shape_to_np(self._lmark_predictor(im, d.rect))
                face_list.append([loc, points])
        return face_list

    def get_face_landmarks(self, im, scale=0):
        """ get face locations, color order of images is rgb """
        faces = self._face_detector(np.uint8(im), scale)
        face_list = []
        if faces is not None or len(faces) > 0:
            for i, d in enumerate(faces):
                try:
                    points = lib.shape_to_np(self._lmark_predictor(im, d))
                except:
                    points = lib.shape_to_np(self._lmark_predictor(im, d.rect))
                face_list.append(points)
        return face_list


if __name__ == '__main__':
    from PIL import Image
    flib = Flib()
    flib.set_face_detector('cnn')
    flib.set_landmarks_predictor()
    flib.set_face_rec()

    im1 = np.array(Image.open('im1.jpg'))
    im2 = np.array(Image.open('im2.jpg'))
    flib.face_verify(im1, im2)

    flib.align(im1)
    flib.get_face_loc(im1)
    flib.get_face_loc_landmarks(im1)
    flib.get_face_landmarks(im1)