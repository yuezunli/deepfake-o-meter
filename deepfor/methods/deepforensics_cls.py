import numpy as np
import os, sys, cv2
import logging
from deepfor.py_utils.face_utils.facelib import Flib
from deepfor.methods.deepforensics import DeepForCls, DeepForLoc


class MesoNet(DeepForCls):
    def __init__(self, mode='meso4'):
        """
        mode = meso4, mesoinception4
        """
        super(MesoNet, self).__init__()
        # Set up env
        pwd = os.path.dirname(__file__)
        root_dir = pwd + '/../'
        sys.path.append(root_dir + '/externals/')

        from MesoNet.classifiers import Meso4, MesoInception4
        import MesoNet.utils as pointer
        self.pointer = pointer
        if mode == 'meso4':
            self.net = Meso4()
            model_path = root_dir + '/externals/MesoNet/weights/Meso4_DF'
        elif mode == 'mesoinception4':
            self.net = MesoInception4()
            model_path = root_dir + '/externals/MesoNet/weights/MesoInception_DF'
        else:
            raise ValueError('name should be meso4 or mesoinception4')
        self.net.load(model_path)
        self.facelib = Flib()
        self.facelib.set_face_detector()
        self.facelib.set_landmarks_predictor(68)

    def preproc(self, im):
        im = self.pointer.preprocess(im)
        return im

    def crop_face(self, im):
        loc, points = self.facelib.get_face_loc_landmarks(im)[0]
        cropped_face = self.pointer.crop_face(im, points)
        return cropped_face, loc

    def get_softlabel(self, im):
        # Model prediction
        conf = self.net.predict(im)[0][0]  # conf of real
        return 1 - conf

    def run(self, im):
        cropped_face = self.crop_face(im)
        preproced_face = self.preproc(cropped_face)
        conf = self.get_softlabel(preproced_face)
        return conf


class XceptionNet(DeepForCls):
    def __init__(self, mode='c23'):
        """
        mode: c23, c40, raw
        """
        super(XceptionNet, self).__init__()
        # Set up env
        pwd = os.path.dirname(__file__)
        root_dir = pwd + '/../'
        sys.path.append(root_dir + '/externals/')
        from xceptionnet.classification import xception_main as df_xception
        self.pointer = df_xception
        self.model = self.pointer.init_model(mode)
        self.facelib = Flib()
        self.facelib.set_face_detector()

    def preproc(self, im):
        # im is face area
        im = self.pointer.preprocess_image(im)
        return im

    def crop_face(self, im):
        face_detector = self.facelib._face_detector
        # Image size
        height, width = im.shape[:2]
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray, 1)
        if len(faces):
            # For now only take biggest face
            face = faces[0]
            x, y, size = self.pointer.get_boundingbox(face, width, height)
            cropped_face = im[y:y+size, x:x+size]
            return cropped_face, [x, y, x+size, y+size]
        else:
            return [], []

    def get_softlabel(self, im):
        # Model prediction
        output = self.pointer.predict(im, self.model)
        conf = output.detach().cpu().numpy()[0][1]
        return conf

    def get_hardlabel(self, im):
        conf = self.get_softlabel(im)
        label = np.argmax(conf)
        return label

    def run(self, im):
        cropped_face = self.crop_face(im)
        preproced_face = self.preproc(cropped_face)
        conf = self.get_softlabel(preproced_face)
        return conf


class ClassNSeg(DeepForCls):
    def __init__(self):
        super(ClassNSeg, self).__init__()
        # Set up env
        pwd = os.path.dirname(__file__)
        root_dir = pwd + '/../'
        sys.path.append(root_dir + '/externals/')
        from ClassNSeg import ClassNSeg_main as df_classnseg
        self.pointer = df_classnseg
        self.model = self.pointer.init_model()
        self.facelib = Flib()
        self.facelib.set_face_detector()

    def preproc(self, im):
        # im is face area
        im = self.pointer.preprocess_image(im)
        return im

    def crop_face(self, im):
        face_detector = self.facelib._face_detector
        bbox, flag = self.pointer.get_bbox(im, face_detector)
        if bbox is None or (not flag):
            return None
        altered_cropped, cors = self.pointer.extract_face(im, bbox)
        return altered_cropped, bbox

    def get_softlabel(self, im):
        # Model prediction
        output = self.pointer.predict(im, self.model)
        conf = output.detach().numpy()[1]
        return conf

    def get_hardlabel(self, im):
        conf = self.get_softlabel(im)
        label = np.argmax(conf)
        return label

    def run(self, im):
        cropped_face = self.crop_face(im)
        preproced_face = self.preproc(cropped_face)
        conf = self.get_softlabel(preproced_face)
        return conf


class VA(DeepForCls):
    def __init__(self):
        super(VA, self).__init__()
        # Set up env
        pwd = os.path.dirname(__file__)
        root_dir = pwd + '/../'
        sys.path.append(root_dir + '/externals/')
        from VA import VA_main as df_VA
        self.pointer = df_VA
        self.model = self.pointer.init_model('deepfake')
        self.facelib = Flib()
        self.facelib.set_face_detector()
        self.facelib.set_landmarks_predictor(68)

    def preproc(self, im):
        # im is face area
        im = self.pointer.preprocess_image(im)
        return im

    def get_softlabel(self, im):
        # Model prediction
        scores = self.pointer.predict(im, 'deepfake', self.model, self.facelib._face_detector, self.facelib._lmark_predictor)
        conf = {'Score_MLP': scores[0][0], 'Score_LogReg': scores[0][1]}
        return conf

    def get_hardlabel(self, im):
        conf = self.get_softlabel(im)
        label = np.argmax(conf)
        return label

    def run(self, im):
        # cropped_face = self.crop_face(im, True)
        preproced_face = self.preproc(im)
        conf = self.get_softlabel(preproced_face)
        return conf


class CapsuleNet(DeepForCls):
    def __init__(self):
        super(CapsuleNet, self).__init__()
        # Set up env
        pwd = os.path.dirname(__file__)
        root_dir = pwd + '/../'
        sys.path.append(root_dir + '/externals/')
        from Capsule import Capsule_main as df_Capsule
        self.pointer = df_Capsule
        self.vgg_ext, self.capnet = self.pointer.init_model()
        self.facelib = Flib()
        self.facelib.set_face_detector()

    def preproc(self, im):
        # im is face area
        im = self.pointer.preprocess_image(im)
        return im

    def crop_face(self, im):
        face_detector = self.facelib._face_detector
        # Image size
        height, width = im.shape[:2]
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray, 1)
        if len(faces):
            face = faces[0]
            x, y, size = self.pointer.get_boundingbox(face, width, height)
            cropped_face = im[y:y+size, x:x+size]
        return cropped_face, [x, y, x+size, y+size]

    def get_softlabel(self, im):
        # Model prediction
        output = self.pointer.predict(im, self.vgg_ext, self.capnet, False)
        conf = output.detach().cpu().numpy()[0][1]
        return conf

    def get_hardlabel(self, im):
        conf = self.get_softlabel(im)
        label = np.argmax(conf)
        return label

    def run(self, im):
        cropped_face = self.crop_face(im)
        preproced_face = self.preproc(cropped_face)
        conf = self.get_softlabel(preproced_face)
        return conf


class FWA(DeepForCls):
    def __init__(self):
        # Set up env
        pwd = os.path.dirname(__file__)
        root_dir = pwd + '/../'
        sys.path.append(root_dir + '/externals/FWA')
        import fwa_utils
        self.pointer = fwa_utils
        self.solver = self.pointer.init_model()
        self.facelib = Flib()
        self.facelib.set_face_detector()
        self.facelib.set_landmarks_predictor(68)

    def crop_face(self, im):
        loc, point = self.facelib.get_face_loc_landmarks(im)[0]
        return self.pointer.crop(im, point), loc

    def get_softlabel(self, im):
        conf = self.pointer.predict(self.solver, im) # fake conf
        return conf

    def run(self, im):
        rois = self.crop_face(im)
        conf = self.get_softlabel(rois)
        return conf


class DSPFWA(DeepForCls):
    def __init__(self):
        # Set up env
        pwd = os.path.dirname(__file__)
        root_dir = pwd + '/../'
        sys.path.append(root_dir + '/externals/')
        from DSP_FWA import dsp_fwa_utils
        self.pointer = dsp_fwa_utils
        self.net = self.pointer.init_model()
        self.facelib = Flib()
        self.facelib.set_face_detector()
        self.facelib.set_landmarks_predictor(68)

    def preproc(self, im):
        return im

    def crop_face(self, im):
        loc, point = self.facelib.get_face_loc_landmarks(im)[0]
        return self.pointer.crop(im, point), loc

    def get_softlabel(self, im):
        conf = self.pointer.predict(self.net, im) # fake conf
        return conf

    def run(self, im):
        rois, _ = self.crop_face(im)
        conf = self.get_softlabel(rois)
        return conf


class Upconv(DeepForCls):
    def __init__(self, mode='LR_CelebA'):
        super(Upconv, self).__init__()
        # Set up env
        pwd = os.path.dirname(__file__)
        root_dir = pwd + '/../'
        sys.path.append(root_dir + '/externals/')
        from Upconv import Upconv_main as df_Upconv
        self.pointer = df_Upconv
        if mode == 'SVM_FacesHQ':
            model_path = root_dir + '/externals/Upconv/models/SVM_FacesHQ.pickle'
            self.praH = 722
        elif mode == 'LR_FacesHQ':
            model_path = root_dir + '/externals/Upconv/models/LR_FacesHQ.pickle'
            self.praH = 722
        elif mode == 'SVM_FF':
            model_path = root_dir + '/externals/Upconv/models/SVM_FF.pickle'
            self.praH = 300
        elif mode == 'LR_FF':
            model_path = root_dir + '/externals/Upconv/models/LR_FF.pickle'
            self.praH = 300
        elif mode == 'SVM_CelebA':
            model_path = root_dir + '/externals/Upconv/models/SVM_CelebA.pickle'
            self.praH = 80
        elif mode == 'SVM_r_CelebA':
            model_path = root_dir + '/externals/Upconv/models/SVM_r_CelebA.pickle'
            self.praH = 80
        elif mode == 'SVM_p_CelebA':
            model_path = root_dir + '/externals/Upconv/models/SVM_p_CelebA.pickle'
            self.praH = 80
        elif mode == 'LR_CelebA':
            model_path = root_dir + '/externals/Upconv/models/LR_CelebA.pickle'
            self.praH = 80
        else:
            raise ValueError(
                'name should be in [SVM_FacesHQ, LR_FacesHQ, SVM_FF, LR_FF, SVM_CelebA, SVM_r_CelebA, SVM_p_CelebA, LR_CelebA]')

        self.model = self.pointer.init_model(model_path)
        self.facelib = Flib()
        self.facelib.set_face_detector()
        self.facelib.set_landmarks_predictor(68)

    def crop_face(self, im):
        face_detector = self.facelib._face_detector
        # Image size
        height, width = im.shape[:2]
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray, 1)
        if len(faces):
            face = faces[0]
            x, y, size = self.pointer.get_boundingbox(face, width, height)
            cropped_face = im[y:y+size, x:x+size]
        return cropped_face

    def preproc(self, im):
        im = self.pointer.preprocess_image(im)
        return im

    def get_softlabel(self, im):
        conf = self.pointer.predict(im, self.model, self.praH)
        return 1 - conf

    def get_hardlabel(self, im):
        conf = self.get_softlabel(im)
        label = np.argmax(conf)
        return label

    def run(self, im):
        cropped_face = self.crop_face(im)
        preproced_face = self.preproc(cropped_face)
        conf = self.get_softlabel(preproced_face)
        return conf
