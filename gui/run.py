
# This enables to import PyCVApp/*.py
import sys; sys.path.insert(0, '..')
# from py_utils.vid_utils import proc_vid as pv
# from py_utils.vid_utils import proc_aud as pa
# import matplotlib
# matplotlib.use('Agg')
from Sandbox.VideoSandbox import VideoSandboxWnd
import numpy as np
# ===== Import QT Between Versions - Begin =====
import pkgutil
if pkgutil.find_loader ('PyQt4'):
  from PyQt4.QtCore import *
  from PyQt4.QtGui import *
elif pkgutil.find_loader ('PyQt5'):
  from PyQt5.QtCore import *
  from PyQt5.QtGui import *
  from PyQt5.QtWidgets import *
elif pkgutil.find_loader ('PySide'):
  from PySide.QtCore import *
  from PySide.QtGui import *
# ===== Import QT Between Versions - End =====
import ImageViz.viz_widget as viz_widget
import os, cv2
# from init import net, front_face_detector, lmark_predictor
# import funcs

import deepfor
import utils, requests, socket, time

pwd = os.path.join(os.path.dirname(__file__))


class ComboCheckBox(QComboBox):
    def __init__(self, items):  # items==[str,str...]
        super(ComboCheckBox, self).__init__()
        self.items = items
        self.qCheckBox = []
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setReadOnly(True)
        qListWidget = QListWidget()

        self.row_num = len(self.items)
        for i in range(self.row_num):
            self.qCheckBox.append(QCheckBox())
            qItem = QListWidgetItem(qListWidget)
            self.qCheckBox[i].setText(self.items[i])
            qListWidget.setItemWidget(qItem, self.qCheckBox[i])
            self.qCheckBox[i].stateChanged.connect(self.Selectlist)

        self.setLineEdit(self.qLineEdit)
        self.setModel(qListWidget.model())
        self.setView(qListWidget)

    def Selectlist(self):
        self.Outputlist = []
        for i in range(self.row_num):
            if self.qCheckBox[i].isChecked() == True:
                self.Outputlist.append(self.qCheckBox[i].text())
        print('Method {} is selected.'.format(self.Outputlist))
        return self.Outputlist



class VidForGui(VideoSandboxWnd):
    def __init__(self):
        super(VidForGui, self).__init__()
        self.out_dir = os.path.join(pwd, 'out/')
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        self.init_model()
        self.init = 1
        self.max_height = 400
        self.max_width = 800



    def init_model(self):
        # windows
        self.urls = {}
        self.urls['Upconv'] = 'http://' + '124.16.70.204' + ':5001/deepforensics'
        print('Load the Upconv Model')

        self.urls['DSP-FWA'] = 'http://' + '124.16.70.204' + ':5002/deepforensics'
        print('Load the DSP-FWA Model')

        self.urls['WM'] = 'http://' + '124.16.70.204' + ':5003/deepforensics'
        print('Load the WM Model')

        self.urls['Selim'] = 'http://' + '124.16.70.204' + ':5004/deepforensics'
        print('Load the Selim Model')

        self.urls['VA'] = 'http://' + '124.16.70.204' + ':5005/deepforensics'
        print('Load the VA Model')

        self.urls['Capsule'] = 'http://' + '124.16.70.204' + ':5006/deepforensics'
        print('Load the Capsule Model')

        self.urls['ClassNSeg'] = 'http://' + '124.16.70.204' + ':5007/deepforensics'
        print('Load the ClassNSeg Model')

        self.urls['XceptionNet'] = 'http://' + '124.16.70.204' + ':5008/deepforensics'
        print('Load the XceptionNet Model')

        self.urls['FWA'] = 'http://' + '124.16.70.148' + ':5009/deepforensics'
        print('Load the FWA Model')

        self.urls['MesoNet'] = 'http://' + '124.16.70.204' + ':5010/deepforensics'
        print('Load the MesoNet Model')




    def open_video_dialog(self):
        dialog_title = self.tr('Load Video')
        directory = 'input/'
        selfilter = 'Videos (*.avi *.mp4 *.mpg *.wmv *.asf *.mov *.qt *.flv *.asf);;AVI (*.avi);;MPEG4 (*.mp4);;MPEG or MPEG2 (*.mpg);;Microsoft WMV or ASF (*.wmv *.asf);;QuickTime MOV (*.mov *.qt);;Flash Video (*.flv *.swf);;All Files (*.*)' #self.tr('Videos (*.avi *.mp4 *.mpg *.wmv *.asf *.mov *.qt *.flv *.asf)')
        fileName = QFileDialog.getOpenFileName (self, dialog_title, directory, selfilter)
        # selfilter = self.tr('Videos (*.avi *.mp4 *.mpg *.wmv *.asf *.mov *.qt *.flv *.asf)');
        # fileName, filter = QFileDialog.getOpenFileName(self,
        #                                                dialog_title, directory,
        #                                                self.tr(
        #                                                    'Videos (*.avi *.mp4 *.mpg *.wmv *.asf *.mov *.qt *.flv *.asf);;AVI (*.avi);;MPEG4 (*.mp4);;MPEG or MPEG2 (*.mpg);;Microsoft WMV or ASF (*.wmv *.asf);;QuickTime MOV (*.mov *.qt);;Flash Video (*.flv *.swf);;All Files (*.*)'),
        #                                                selfilter)
        print ('on_file_open_video() %s' % (fileName[0]))
        return fileName[0]

    def createMainFrame(self):
        # Image display using VizWidget defined in viz_widget.py
        self.vizWidget = viz_widget.VizWidget()
        self.vizWidgetScrollArea = viz_widget.VizWidgetScrollArea(self.vizWidget)

        vboxMainFrame = QVBoxLayout()
        vboxMainFrame.addWidget(self.vizWidgetScrollArea)

        hboxVideoCtrl = self.createVideoCtrlHBox()
        vboxMainFrame.addLayout(hboxVideoCtrl)

        hLabel = QHBoxLayout()
        hLabel.setAlignment(Qt.AlignLeft)
        Label = QLabel('DeepFake Process:')
        hLabel.addWidget(Label)
        self.DF_info = QLabel()
        # l1.setText("Hello World")
        hLabel.addWidget(self.DF_info)
        vboxMainFrame.addLayout(hLabel)

        hboxProcCtrl = self.createProcCtrlHBox()
        vboxMainFrame.addLayout(hboxProcCtrl)

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(vboxMainFrame)
        self.setCentralWidget(self.mainWidget)

        # Status Bar
        self.statusLabel = QLabel('', self)
        self.statusBar().addWidget(self.statusLabel, 1)

    def createProcCtrlHBox(self):
        proc_ctrl_hbox = QHBoxLayout()
        proc_ctrl_hbox.setAlignment(Qt.AlignLeft)

        # self.playSpeedComboBox = QComboBox ()
        # self.playSpeedComboBox.addItem('Mehtod')
        # self.playSpeedComboBox.addItem('DSP-FWA')
        # self.playSpeedComboBox.addItem('Upconv')
        # self.method_name = self.playSpeedComboBox.currentText()
        # self.playSpeedComboBox.currentIndexChanged.connect (self.on_select_method)
        # proc_ctrl_hbox.addWidget(self.playSpeedComboBox)

        self.playSpeedComboBox = ComboCheckBox(
            ['Upconv', 'DSP-FWA', 'WM', 'Selim', 'VA', 'Capsule', 'ClassNSeg', 'XceptionNet', 'FWA', 'MesoNet'])
        # self.playSpeedComboBox = ComboCheckBox(['Upconv', 'DSP-FWA'])
        self.methods = self.playSpeedComboBox.Selectlist()
        self.playSpeedComboBox.resize(640, 480)
        self.playSpeedComboBox.setGeometry(QRect(0, 0, 640, 480))

        proc_ctrl_hbox.addWidget(self.playSpeedComboBox)

        self.analyze_btn = QPushButton('Analyze')
        self.analyze_btn.setEnabled(False)
        # self.connect(self.analyze_btn, SIGNAL('clicked()'), self.on_analyze)
        self.analyze_btn.clicked.connect(self.on_analyze)
        proc_ctrl_hbox.addWidget(self.analyze_btn)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setEnabled(False)
        proc_ctrl_hbox.addWidget(self.progress_bar)

        self.smoothBox = QSpinBox()
        self.smoothBox.setRange(1, 999)
        self.smoothBox.setSingleStep(1)
        self.smoothBox.setValue(1)
        self.smoothBox.setEnabled(False)
        proc_ctrl_hbox.addWidget(self.smoothBox)

        self.smooth_btn = QPushButton('TempSmooth')
        self.smooth_btn.setEnabled(False)
        # self.connect(self.smooth_btn, SIGNAL('clicked()'), self.on_smooth)
        self.smooth_btn.clicked.connect(self.on_smooth)
        proc_ctrl_hbox.addWidget(self.smooth_btn)

        self.smooth_progress_bar = QProgressBar(self)
        self.smooth_progress_bar.setEnabled(False)
        proc_ctrl_hbox.addWidget(self.smooth_progress_bar)

        self.save_btn = QPushButton('Save')
        self.save_btn.setEnabled(False)
        # self.connect(self.save_btn, SIGNAL('clicked()'), self.on_save)
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setEnabled(False)
        proc_ctrl_hbox.addWidget(self.save_btn)
        return proc_ctrl_hbox

    def on_save(self):
        self.DF_info.setText("Save video...")
        self.save_btn.setEnabled(False)
        input_vid_path = self.VIDEO_FULL_PATH
        vid_name = os.path.basename(input_vid_path).split('.')[0]
        imgs, frame_num, fps, width, height = self.vid_info
        # pv.gen_vid('tmp.mp4', np.array(self.final_vis)[:, :, :, (2, 1, 0)], fps)
        # pa.audio_transfer(input_vid_path, 'tmp.mp4', os.path.join(self.out_dir, vid_name + '_vis.mp4'))
        # os.remove('tmp.mp4')
        vid_name = vid_name + '_vis.mp4'
        utils.gen_vid_with_aud(self.final_vis, fps, self.out_dir, vid_name, input_vid_path)
        self.save_btn.setEnabled(True)
        self.DF_info.setText("")

    def on_smooth(self):
        self.DF_info.setText("Time Smoothing...")
        self.analyze_btn.setEnabled(False)
        self.smooth_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        input_vid_path = self.VIDEO_FULL_PATH
        vid_name = os.path.basename(input_vid_path).split('.')[0]
        imgs, frame_num, fps, width, height = self.vid_info
        # Smooth
        value = self.smoothBox.value()
        delta = int((value - 1) / 2)
        smooth_probs = []
        prob_plot_vis = []
        for fid in range(frame_num):
            mean_prob = np.mean(self.probs[np.maximum(0, fid - delta):fid + value - delta])
            smooth_probs.append(mean_prob)

        for fid, vis_im in enumerate(self.vis_imgs):
            QCoreApplication.processEvents()
            prob_plot = utils.gen_plot_vid_v2(frame_num, fid, fps, smooth_probs, self.vid_prob)[:, :, (2, 1, 0)]
            scale1 = float(vis_im.shape[0]) / prob_plot.shape[0]
            # Resize plot size to same size with video
            plot = cv2.resize(prob_plot, None, None, fx=scale1, fy=scale1)
            prob_plot_vis.append(plot)
            v = np.ceil(float(fid) / frame_num * 80.0)
            self.smooth_progress_bar.setValue(v)

        self.final_vis = []
        for fid in range(frame_num):
            QCoreApplication.processEvents()
            self.final_vis.append(np.concatenate(
                [self.vis_imgs[fid],
                 prob_plot_vis[fid]], axis=1))
            v = np.ceil(float(fid) / frame_num * 19.0)
            self.smooth_progress_bar.setValue(v + 80)
        self.smooth_progress_bar.setValue(100)
        # Check consistency
        assert self.NF == len(self.final_vis)
        self.show_video_after_load()
        self.smooth_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.DF_info.setText("")


    def on_analyze(self):
        self.DF_info.setText("Analyzing...")
        self.analyze_btn.setEnabled(False)
        self.init = 0
        self.smoothBox.setValue(1)
        self.smooth_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.smooth_progress_bar.setValue(0)
        # self.load_video_show()

        input_vid_path = self.VIDEO_FULL_PATH
        vid_name = os.path.basename(input_vid_path).split('.')[0]
        imgs, frame_num, fps, width, height = utils.parse_vid(input_vid_path)
        scale = np.minimum(float(self.max_height) / height,
                           float(self.max_width) / width)
        self.vid_info = [imgs, frame_num, fps, width, height]
        self.methods = self.playSpeedComboBox.Selectlist()

        prob = {}
        loc = {}
        self.probs = {}
        self.vis_imgs = {}
        self.prob_plot_vis = []
        self.final_vis = []
        for method in self.methods:
            self.probs[method] = []
            self.vis_imgs[method] = []
            # self.prob_plot_vis[method] = []
            # self.final_vis[method] = []
        for fid, im in enumerate(imgs):
            QCoreApplication.processEvents()
            for method in self.methods:
                resp = requests.post(self.urls[method], json={'feature': im.tolist()}).json()[1:-1]
                resp_split = resp.split(',')
                if len(resp_split) == 5:
                    prob[method] = 1 - float(resp_split[4])
                    loc[method] = [int(resp_split[0]), int(resp_split[1]), int(resp_split[2]), int(resp_split[3])]
                else:
                    loc[method] = []
                    prob[method] = 1 - float(resp)
                self.probs[method].append(prob[method])
            # import pdb; pdb.set_trace()
            vis_im = utils.draw_face_score_v1(im.copy(), loc, prob)[:, :, (2, 1, 0)]
            vis_im = cv2.resize(vis_im, None, None, fx=scale, fy=scale)
            self.vis_imgs[method].append(vis_im)

            prob_plot = utils.gen_plot_vid_v1(frame_num, fid, fps, self.probs)[:, :, (2, 1, 0)]
            scale1 = float(vis_im.shape[0]) / prob_plot.shape[0]
            # Resize plot size to same size with video
            plot = cv2.resize(prob_plot, None, None, fx=scale1, fy=scale1)
            self.prob_plot_vis.append(plot)
            self.final_vis.append(np.concatenate(
             [self.vis_imgs[method][fid],
             self.prob_plot_vis[fid]], axis=1))
            v = np.ceil(float(fid) / frame_num * 60.0)
            self.progress_bar.setValue(v)
            print( prob)
            self.proc_frame(fid)
            if fid == 0:
                self.adjustViewSize()
            self.on_fit_window_to_view()

        prob_ary = np.array(self.probs[method])
        frame_no_faces = np.sum(prob_ary == -1)
        self.vid_prob = np.mean(sorted(self.probs[method])[frame_no_faces:frame_no_faces + int((frame_num - frame_no_faces) / 3)])

        # self.DF_info.setText('Analyzing done. Processing visual plots...')
        # self.prob_plot_vis = []
        # for fid, vis_im in enumerate(self.vis_imgs):
        #     QCoreApplication.processEvents()
        #     prob_plot = funcs.gen_plot_vid_v2(frame_num, fid, fps, self.probs, self.vid_prob)[:, :, (2, 1, 0)]
        #     scale1 = float(vis_im.shape[0]) / prob_plot.shape[0]
        #     # Resize plot size to same size with video
        #     plot = cv2.resize(prob_plot, None, None, fx=scale1, fy=scale1)
        #     self.prob_plot_vis.append(plot)
        #     v = np.ceil(float(fid) / frame_num * 30.0)
        #     self.progress_bar.setValue(v + 60)

        # self.final_vis = []
        # for fid in range(frame_num):
        #     QCoreApplication.processEvents()
        #     self.final_vis.append(np.concatenate(
        #         [self.vis_imgs[fid],
        #          self.prob_plot_vis[fid]], axis=1))
        #     v = np.ceil(float(fid) / frame_num * 10.0)
        #     self.progress_bar.setValue(v + 90)
        # self.progress_bar.setValue(100)

        # self.init = 0
        self.show_video_after_load()
        self.analyze_btn.setEnabled(True)
        self.smooth_btn.setEnabled(True)
        self.smoothBox.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.DF_info.setText("")

    def proc_frame_run_process(self):
        # By default set IOut to I (no deep copy involved)
        super(VidForGui, self).proc_frame_run_process()

        if self.init:
            height, width = self.I.shape[:2]
            scale = min(float(self.max_height) / height, float(self.max_width) / width)
            self.I = cv2.resize(self.I, None, None, fx=scale, fy=scale)
        else:
            # for method in self.methods:
            self.I = self.final_vis[self.FI]

    def on_file_open_video(self):
        self.init = 1
        self.progress_bar.setValue(0)
        self.smooth_progress_bar.setValue(0)
        self.analyze_btn.setEnabled(True)
        self.smooth_btn.setEnabled(False)
        self.smoothBox.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.smoothBox.setValue(1)
        self.DF_info.setText("")
        super(VidForGui, self).on_file_open_video()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    wnd = VidForGui()
    wnd.show()
    sys.exit(app.exec_())
