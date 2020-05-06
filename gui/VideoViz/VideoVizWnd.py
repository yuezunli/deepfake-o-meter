# Python PySide OpenCV Video GUI App
# Author:  Ming-Ching Chang
# Version / Development Log:
#   2018/01/28  Initial Version

# The only dependency is PySide, numpy, OpenCV.
# No matplotlib

import os
import numpy as np
import timeit

import skimage.io as io
import cv2
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

# This enables to import PyCVApp/*.py
import sys; sys.path.insert(0, '..')

import var
import ImageViz.ImageViz_var as ImageViz_var
import ImageViz.viz_widget as viz_widget
import ImageViz.np_ocv_qim_convert as np_ocv_qim_convert
import ImageViz.ImageVizNpWnd as ImageVizNpWnd

import VideoViz.VideoViz_var as VideoViz_var
import VideoViz.ocv_vid as ocv_vid
import VideoViz.VideoVizDialogs as VideoVizDialogs

# ========== General Parameters ==========


# ========== Main GUI Window ==========

class VideoVizWnd (ImageVizNpWnd.ImageVizNpWnd):
  def __init__ (self, parent=None):
    super (VideoVizWnd, self).__init__ ()

    print ('INPUT_PATH %s, INPUT_VIDEO %s, OUTPUT_PATH %s, OUTPUT_VIDEO %s' % (VideoViz_var.INPUT_PATH, VideoViz_var.INPUT_VIDEO, VideoViz_var.OUTPUT_PATH, VideoViz_var.OUTPUT_VIDEO))

    # ===== Initialization =====
    self.FI = 0         #frame index
    self.startFI = 0
    self.endFI = -1
    self.I = None
    self.FI_PREV = -1
    self.I_PREV = None
    self.NF = 0
    self.NX = 0
    self.NY = 0
    self.NC = 0
    self.VIDEO_FPS = VideoViz_var.NEW_VIDEO_FPS
    self.VIDEO_HMS = ''
    # run mode: 'INTERACTIVE', 'BATCH_RUN'
    self.RUN_MODE = VideoViz_var.RUN_MODE
    # Video data mode: 'FILE', 'LIVE', 'MEMORY'
    self.VIDEO_DATA_MODE = VideoViz_var.INPUT_VIDEO_DATA_MODE
    self.VIDEO_MEM_BLOCK = np.array([])
    self.VIDEO_FILE = ''
    self.VIDEO_FULL_PATH = ''
    self.VIDFP = None
    self.PROCESS_FPS = 0
    self.FOURCC = VideoViz_var.NEW_VIDEO_FOURCC

    self.app_init_time = timeit.default_timer()

    video_full_path = VideoViz_var.INPUT_PATH + '/' + VideoViz_var.INPUT_VIDEO
    if os.path.isfile (video_full_path):
      self.VIDEO_FULL_PATH = video_full_path
      self.VIDEO_FILE = VideoViz_var.INPUT_VIDEO
      if var.VERBOSE>1:
        print ('VideoVizWnd init: VIDEO_FULL_PATH = %s, set VIDEO_DATA_MODE to FILE' % (self.VIDEO_FULL_PATH))
      self.VIDEO_DATA_MODE = 'FILE'
    else:
      if var.VERBOSE>1:
        print ('VideoVizWnd init: VIDEO_FULL_PATH %s does not exist!' % (var.VIDEO_FULL_PATH))
    self.VIDEO_OUT_FULL_PATH = VideoViz_var.OUTPUT_PATH + '/' + VideoViz_var.OUTPUT_VIDEO

    # ===== App init =====
    self.createMainFrame ()
    self.setupToolBar ()
    self.setMouseTracking (True)
    self.setupKeyShortcuts ()

    self.APP_NAME = 'VideoViz'
    self.setWindowTitle ('%s - %s' % (self.APP_NAME, self.VIDEO_FILE))

    ret = self.load_video_show ()
    if ret == False:
      self.initImageVizAndView ()
      self.initVideoVizAndView ()

    if VideoViz_var.START_FI !=0:
      self.startFI = VideoViz_var.START_FI
    if VideoViz_var.END_FI != -1:
      self.endFI = VideoViz_var.END_FI

    self.timer = QTimer()
    self.timer.timeout.connect (self.on_tick)
    # For QTime the default interval is 0:
    #    time out as soon as all the events in the window system's event queue have been processed
    self.timerTickms = 0 #1
    if VideoViz_var.START_VIDEO_PLAYING:
      self.on_play()

    if var.VERBOSE>3:
      print ('end of VideoVizWnd init')

  def createActions (self):
    super (VideoVizWnd, self).createActions ()
    self.createVidProcActions ()

  def createFileActions (self):
    self.fileNewAct = QAction ('&New',
        self, triggered=self.on_file_new)

    self.fileOpenVideoAct = QAction('Open &Video...',
        self, shortcut='Ctrl+V', triggered=self.on_file_open_video)

    self.fileOpenVideoToMemAct = QAction('Open Video to Memory...',
        self, triggered=self.on_file_open_video_to_mem)

    self.fileSaveVideoSrcAct = QAction('Save Video Source...',
        self, triggered=self.on_save_video_src)
    self.fileGUIBatchRunAct = QAction('GUI Batch Run...',
        self, triggered=self.on_GUI_batch_run)

    self.exitAct = QAction ('E&xit',
        self, shortcut='Ctrl+X',
        triggered=self.close)

  def createEditActions (self):
    super (VideoVizWnd, self).createEditActions ()

    self.pasteIntoCurFrameAct = QAction ('&Paste as a New Image',
        self, triggered=self.on_paste_into_cur_frame)

  def createVidProcActions (self):
    self.frameDiffAct = QAction ('&Frame Difference',
        self, checkable=True, triggered=self.on_frame_diff)

  def createMenus (self):
    self.fileMenu = QMenu ('&File', self)
    self.setupFileMenu ()
    self.editMenu = QMenu ('&Edit', self)
    self.setupEditMenu ()
    self.viewMenu = QMenu ('&View', self)
    self.setupViewMenu ()
    self.imgProcMenu = QMenu ('&Image Process', self)
    self.setupImgProcMenu ()
    self.vidProcMenu = QMenu ('Video &Process', self)
    self.setupVidProcMenu ()
    self.helpMenu = QMenu ('&Help', self)
    self.setupHelpMenu ()

    self.menuBar().addMenu (self.fileMenu)
    self.menuBar().addMenu (self.editMenu)
    self.menuBar().addMenu (self.viewMenu)
    self.menuBar().addMenu (self.imgProcMenu)
    self.menuBar().addMenu (self.vidProcMenu)
    self.menuBar().addMenu (self.helpMenu)

  def setupFileMenu (self):
    self.fileMenu.addAction (self.fileNewAct)
    self.fileMenu.addAction (self.fileOpenVideoAct)
    self.fileMenu.addAction (self.fileOpenVideoToMemAct)
    self.fileMenu.addSeparator ()
    self.fileMenu.addAction (self.fileSaveVideoSrcAct)
    self.fileMenu.addAction (self.fileGUIBatchRunAct)
    self.fileMenu.addSeparator ()
    self.fileMenu.addAction (self.exitAct)

  def setupEditMenu (self):
    self.editMenu.addAction (self.copyImageAct)
    self.editMenu.addAction (self.copyImageVizScaleAct)
    self.editMenu.addSeparator ()
    self.editMenu.addAction (self.pasteIntoCurFrameAct)

  def setupVidProcMenu (self):
    self.vidProcMenu.addAction (self.frameDiffAct)

  def createMainFrame (self):
    # Image display using VizWidget defined in viz_widget.py
    self.vizWidget = viz_widget.VizWidget ()
    self.vizWidgetScrollArea = viz_widget.VizWidgetScrollArea (self.vizWidget)

    vboxMainFrame = QVBoxLayout()
    vboxMainFrame.addWidget (self.vizWidgetScrollArea)

    hboxVideoCtrl = self.createVideoCtrlHBox ()
    vboxMainFrame.addLayout (hboxVideoCtrl)

    self.mainWidget = QWidget()
    self.mainWidget.setLayout (vboxMainFrame)
    self.setCentralWidget (self.mainWidget)

    # Status Bar
    self.statusLabel = QLabel('', self)
    self.statusBar().addWidget(self.statusLabel, 1)

  def createVideoCtrlHBox (self):
    # Video GUI controls
    #
    self.playButton = QPushButton ('Play')
    self.playButton.setMaximumWidth (40)
    self.connect (self.playButton, SIGNAL('clicked()'), self.on_play)

    self.playSpeedComboBox = QComboBox ()
    self.playSpeedComboBox.addItem('fastest')
    #self.playSpeedComboBox.addItem('16x')
    #self.playSpeedComboBox.addItem('8x')
    self.playSpeedComboBox.addItem('4x')
    self.playSpeedComboBox.addItem('2x')
    self.playSpeedComboBox.addItem('1x')
    self.playSpeedComboBox.addItem('1/2x')
    self.playSpeedComboBox.addItem('1/4x')
    self.playSpeedComboBox.addItem('1/8x')
    self.playSpeedComboBox.addItem('1/16x')
    self.playSpeedComboBox.currentIndexChanged.connect (self.on_play_tick_speed_change)

    self.procButton = QPushButton ('Proc')
    self.procButton.setMaximumWidth (40)
    self.connect (self.procButton, SIGNAL('clicked()'), self.on_proc_button)

    self.stepButton = QPushButton ('Step')
    self.stepButton.setMaximumWidth (40)
    self.connect (self.stepButton, SIGNAL('clicked()'), self.on_step_button)

    self.stepSizeSpinBox = QSpinBox ();
    self.stepSizeSpinBox.setRange (1, 999);
    self.stepSizeSpinBox.setSingleStep (1);
    self.stepSizeSpinBox.setValue (1);

    # to display video time HH:MM:SS.ss at current frame
    self.timeTextEdit = QLineEdit()
    self.timeTextEdit.setMaximumWidth(68)
    self.connect(self.timeTextEdit, SIGNAL('editingFinished ()'), self.on_time_textbox_update)

    self.frameFirstButton = QPushButton('|<')
    self.frameFirstButton.setMaximumWidth (17)
    self.connect(self.frameFirstButton, SIGNAL('clicked()'), self.on_frame_first)

    self.framePrevButton = QPushButton('<')
    self.framePrevButton.setMaximumWidth (15)
    self.connect(self.framePrevButton, SIGNAL('clicked()'), self.on_frame_prev)

    self.frameNextButton = QPushButton('>')
    self.frameNextButton.setMaximumWidth (15)
    self.connect(self.frameNextButton, SIGNAL('clicked()'), self.on_frame_next)

    self.frameLastButton = QPushButton('>|')
    self.frameLastButton.setMaximumWidth (17)
    self.connect(self.frameLastButton, SIGNAL('clicked()'), self.on_frame_last)

    # ==========
    self.sliderLabel = QLabel ('Frame#')

    # Set the slider range to be the video's total frame numbers.
    self.slider = viz_widget.JumpSlider (Qt.Horizontal)
    self.slider.setTracking (True)
    self.slider.setTickPosition (viz_widget.JumpSlider.TicksBothSides)
    self.connect (self.slider, SIGNAL('valueChanged(int)'), self.on_slider_update)

    # to display frame number
    self.frameTextEdit = QLineEdit()
    self.frameTextEdit.setMaximumWidth(50)
    self.connect(self.frameTextEdit, SIGNAL('editingFinished ()'), self.on_frame_textbox_update)

    #
    # Layout with box sizers
    #
    hboxVideoCtrl = QHBoxLayout()

    for w in [ self.playButton, self.playSpeedComboBox,
               self.procButton, self.stepButton, self.stepSizeSpinBox,
               self.sliderLabel,
               self.slider, self.frameTextEdit, self.timeTextEdit,
               self.frameFirstButton, self.framePrevButton,
               self.frameNextButton, self.frameLastButton
             ]:
      hboxVideoCtrl.addWidget (w)
      hboxVideoCtrl.setAlignment (w, Qt.AlignVCenter)
    # set min size for this layout
    hboxVideoCtrl.setSizeConstraint (QLayout.SetMinimumSize)
    return hboxVideoCtrl

  # ========== Setup ToolBar ==========

  def setupToolBar (self):
    # Toolbar
    # https://stackoverflow.com/questions/11643221/are-there-default-icons-in-pyqt-pyside
    # default style icon http://srinikom.github.io/pyside-docs/PySide/QtGui/QStyle.html#PySide.QtGui.PySide.QtGui.QStyle.StandardPixmap
    # See https://joekuan.wordpress.com/2015/09/23/list-of-qt-icons/
    self.toolBar = self.addToolBar ('ToolBar')

    # default theme icon at https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
    #newIcon = QIcon.fromTheme ('document-new', QIcon(':/document-new.png'))
    #undoicon = QIcon.fromTheme('edit-undo')

    icon = self.style().standardIcon(QStyle.SP_FileIcon)
    toolNewAction = QAction (icon, 'new', self)
    self.toolBar.addAction (toolNewAction)
    toolNewAction.triggered.connect (self.on_file_new)

    icon = self.style().standardIcon(QStyle.SP_DialogOpenButton)
    toolOpenAction = QAction (icon, 'open', self)
    self.toolBar.addAction (toolOpenAction)
    toolOpenAction.triggered.connect (self.on_file_open_video)

    # Enforce toolBar button to be a fixed size
    for a in self.toolBar.actions():
      widget = self.toolBar.widgetForAction (a)
      widget.setFixedSize (24, 24)

    self.toolBar.addSeparator ()

    # zoomScaleLabel: show view zoom / scale info
    self.zoomScaleLabel = QLabel ('Zoom Z[idx], Scale Z[idx]')
    self.zoomScaleLabel.setStyleSheet ('QLabel { background-color : white; color : blue; }')
    self.toolBar.addWidget (self.zoomScaleLabel)

    self.toolBar.addSeparator ()

    # pixelInfoLabel: show pixel info at mouse location.
    self.pixelInfoLabel = QLabel ('(x, y)[R, G, B]')
    self.pixelInfoLabel.setStyleSheet ('QLabel { background-color : white; color : black; }')
    self.toolBar.addWidget (self.pixelInfoLabel)

    self.toolBar.addSeparator ()

    # procInfoLabl: show process and FPS info.
    self.procInfoLabel = QLabel ('Proc FPS ( x)')
    self.procInfoLabel.setStyleSheet ('QLabel { background-color : white; color : green; }')
    self.toolBar.addWidget (self.procInfoLabel)

    self.toolBar.addSeparator ()

    #self.toolBar.actionTriggered[QAction].connect (self.toolButtonPressed)

  #def toolButtonPressed (self, action):
  #  print ('toolBar button %s pressed.' % (action.text()))

  def setupKeyShortcuts (self):
    # Keypress Shortcuts
    # https://stackoverflow.com/questions/3169233/pyqt4-global-shortcuts
    QShortcut (QKeySequence('Space'), self, self.on_play) #'Ctrl+Q'

    QShortcut (QKeySequence('Left'), self, self.on_frame_prev)
    QShortcut (QKeySequence('Right'), self, self.on_frame_next)
    QShortcut (QKeySequence(','), self, self.on_play_tick_speed_dec)
    QShortcut (QKeySequence('.'), self, self.on_play_tick_speed_inc)
    QShortcut (QKeySequence('['), self, self.on_step_size_dec)
    QShortcut (QKeySequence(']'), self, self.on_step_size_inc)

  # ==========================================================

  def visualizeImgAdjustSize (self, qImg):
    super (VideoVizWnd, self).visualizeImgAdjustSize (qImg)
    self.mainWidget.adjustSize ()

  def updateStatusBar (self, str=None):
    if str is not None:
      self.status_text = str
    else:
      self.status_text = '%s [%d, %d] %d frames, %d ch, %.2f FPS, len %s. FI %d ProcFPS %.2f (%.2fx)' % (self.VIDEO_FILE, self.NX, self.NY, self.NF, self.NC, self.VIDEO_FPS, self.VIDEO_HMS, self.FI, self.PROCESS_FPS, self.PROCESS_FPS/self.VIDEO_FPS)
    self.statusBar().showMessage (self.status_text)

  def initVideoVizAndView (self, W=None, H=None, NF=None, FPS=None, FourCC=None):
    self.initVideoViz (W, H, NF, FPS, FourCC)

    # Update slider
    self.slider.setRange (0, self.NF-1)
    self.slider.setValue (self.FI)

    self.visualizeImgAdjustSize (self.qImg)
    self.on_fit_window_to_view()

    f_str = '%d' % (self.FI)
    self.frameTextEdit.setText (f_str)
    t = 0
    t_str = '%.2f' % (t)
    self.timeTextEdit.setText (t_str)
    self.updateStatusBar ()

  def initVideoViz (self, W=None, H=None, NF=None, FPS=None, FourCC=None):
    if W is None:
      W = ImageViz_var.NEW_IMAGE_W
    if H is None:
      H = ImageViz_var.NEW_IMAGE_H
    if NF is None:
      NF = VideoViz_var.NEW_VIDEO_NF
    if FPS is None:
      FPS = VideoViz_var.NEW_VIDEO_FPS
    if FourCC is None:
      FourCC = VideoViz_var.NEW_VIDEO_FOURCC

    # Init Video Data
    self.FI = 0
    self.qImg = QImage (W, H, QImage.Format_RGB32)
    self.qImg.fill (Qt.white)
    self.I = np.zeros((H, W, 3), dtype=np.uint8)
    self.I.fill (255)
    self.I_PREV = None
    BLOCK = []
    for f in range (NF):
      BLOCK.append (self.I)
    self.VIDEO_MEM_BLOCK = np.array (BLOCK)

    # Init Video Info
    self.NF = NF

    self.startFI = 0
    if self.endFI == -1:
      self.endFI = self.NF-1
    else:
      self.endFI = min (self.NF, self.endFI)

    self.NX = W
    self.NY = H
    self.NC = 1
    self.VIDEO_DATA_MODE = 'MEMORY'
    self.VIDEO_FULL_PATH = ''
    self.VIDEO_FILE = ''
    if self.VIDFP is not None:
      self.VIDFP.release ()
    self.VIDFP = None
    self.VIDEO_FPS = FPS
    self.VIDEO_HMS = ''
    self.FOURCC = FourCC
    if var.VERBOSE>1:
      print ('initVideoViz(): VIDEO_DATA_MODE = %s' % (self.VIDEO_DATA_MODE))


  # ========== Menu Handlers ==========

  # ========== File Menu Handler ==========

  def on_file_new (self):
    dialog = VideoVizDialogs.NewVideoDialog (self)
    W, H, NF, FPS, FourCC, ok = dialog.showDialog (self)
    if not ok:
      return

    print ('on_file_new(): create video of [W%d, H%d] NF%d FPS%.2f FourCC %s' % (W, H, NF, FPS, FourCC))
    self.initImageVizAndView ()
    self.initVideoVizAndView (W, H, NF, FPS, FourCC)

    self.VIDEO_FILE = 'New.AVI'
    self.setWindowTitle ('%s - %s' % (self.APP_NAME, self.VIDEO_FILE))

    self.RUN_MODE = VideoViz_var.RUN_MODE

    # pause the play (if it is currently on)
    if self.timer.isActive():
      self.playButton.setText ('Pause')
      self.timer.stop ()
      if var.VERBOSE>2:
        print ('Paused: timer stopped')

  def load_video_show (self):
    ret = self.load_video()
    if ret == False:
      return False
    self.show_video_after_load ()

  def show_video_after_load (self):
    # step and display the first frame
    newFI = 0
    # ret = self.proc_frame_read_video (newFI)
    ret = self.proc_frame(newFI)
    self.scale_viz_if_outfit_screen (self.I.shape[1], self.I.shape[0])

    info = self.get_zoom_scale_info ()
    self.zoomScaleLabel.setText (info)

    self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
    self.visualizeImg (self.qImg, updateGeom=True)

    self.slider.setValue (newFI)

    # adjust window
    self.adjustViewSize ()
    self.on_fit_window_to_view ()

    # update statusBar
    self.frameTextEdit.setText (str(self.FI))
    t = ocv_vid.frame_to_video_time (self.VIDFP, self.VIDEO_FPS, self.FI)
    t_str = ocv_vid.time_s_to_hms (t)
    self.timeTextEdit.setText (t_str)
    self.updateStatusBar ()
    return True

  def load_video (self):
    if not os.path.isfile (self.VIDEO_FULL_PATH):
      print ('load_video() error! file %s does not exist!' % (self.VIDEO_FULL_PATH))
      return False

    print ('load_video(): Opening %s' % (self.VIDEO_FULL_PATH))
    self.VIDFP = cv2.VideoCapture (self.VIDEO_FULL_PATH)
    self.VIDEO_DATA_MODE = 'FILE'
    self.NF, self.NX, self.NY, self.NC, self.VIDEO_FPS = ocv_vid.vid_get_video_dim (self.VIDFP)

    if self.NF <= 0:
      return False

    s = float(self.NF) / self.VIDEO_FPS
    self.VIDEO_HMS = ocv_vid.time_s_to_hms (s)

    #self.NF = self.NF + 1 (are we reading the last frame?
    self.FI = 0
    self.I = None
    self.I_PREV = None
    print ('  %s [%d, %d] %d frames, channel %d, FPS %.2f, length %s.' % (self.VIDEO_FILE, self.NX, self.NY, self.NF, self.NC, self.VIDEO_FPS, self.VIDEO_HMS))

    self.slider.setRange (0, self.NF-1)
    print ('  slider range [0, %d]' % (self.NF-1))

    title = '%s - %s' % (self.APP_NAME, self.VIDEO_FILE)
    self.setWindowTitle (title)
    return True

  def on_file_open_video (self):
    fileName = self.open_video_dialog ()
    if fileName:
      fi = QFileInfo (fileName)
      self.VIDEO_FULL_PATH = fileName
      # See https://stackoverflow.com/questions/1207457/convert-a-unicode-string-to-a-string-in-python-containing-extra-symbols
      fn = fi.fileName()
      fn = fn.encode('ascii', 'ignore')
      self.VIDEO_FILE = fn
      if var.VERBOSE:
        print ('file in ASCII %s' % (fn))
      self.reset_viz_zoom ()
      success = self.load_video_show ()
      return success

  def on_file_open_video_to_mem (self):
    fileName = self.open_video_dialog ()
    if not os.path.isfile (fileName):
      print ('on_file_open_video_to_mem() error! file %s does not exist!' % (fileName))
      return False
    self.VIDEO_MEM_BLOCK = ocv_vid.vid_read_imgseq (fileName)
    if self.VIDEO_MEM_BLOCK.shape[0] > 0:
      self.VIDEO_DATA_MODE = 'MEMORY'
      self.show_video_after_load ()
      return True

  def open_video_dialog (self):
    dialog_title = self.tr('Load Video')
    directory = ''
    selfilter = self.tr('Videos (*.avi *.mp4 *.mpg *.wmv *.asf *.mov *.qt *.flv *.asf)')
    fileName, filter = QFileDialog.getOpenFileName (self,
        dialog_title, directory,
        self.tr('Videos (*.avi *.mp4 *.mpg *.wmv *.asf *.mov *.qt *.flv *.asf);;AVI (*.avi);;MPEG4 (*.mp4);;MPEG or MPEG2 (*.mpg);;Microsoft WMV or ASF (*.wmv *.asf);;QuickTime MOV (*.mov *.qt);;Flash Video (*.flv *.swf);;All Files (*.*)'),
        selfilter)
    print ('on_file_open_video() %s' % (fileName))
    return fileName

  def on_save_video_src (self):
    ofile = self.VIDEO_OUT_FULL_PATH
    #if 1: # get from dialog box
    #  self.FOURCC = 'XVID'

    if self.VIDEO_FPS == 0:
      self.VIDEO_FPS = var.NEW_VIDEO_FPS
    if self.FOURCC=='XVID':
      fourcc = cv2.cv.CV_FOURCC('X','V','I','D')
    elif self.FOURCC=='MJPG':
      fourcc = cv2.cv.CV_FOURCC('M','J','P','G')

    NY = self.NY
    NX = self.NX
    isColor = False
    if self.I.ndim > 2:
      isColor = True
    self.BATCH_RUN_vw = cv2.VideoWriter (ofile, fourcc, self.VIDEO_FPS, (NX,NY), isColor)

    if self.VIDEO_DATA_MODE == 'MEMORY':
      for f in range (self.NF):
        I = self.VIDEO_MEM_BLOCK[f]
        #convert rgb_img I to bgr_img
        r,g,b = cv2.split (I)
        bgr_img = cv2.merge ([b,g,r])
        self.BATCH_RUN_vw.write (bgr_img)
        print ('%d' % (f)),
      print ('')
      print ('MEMORY_BLOCK video written to %s' % (ofile))
    elif self.VIDEO_DATA_MODE == 'FILE':
      # Loop through input video and write all video frames
      vidfp = cv2.VideoCapture (self.VIDEO_FULL_PATH)
      for f in range (self.NF):
        I = ocv_vid.vid_read_frame (vidfp)
        #convert rgb_img I to bgr_img
        r,g,b = cv2.split (I)
        bgr_img = cv2.merge ([b,g,r])
        self.BATCH_RUN_vw.write (bgr_img)
        print ('%d' % (f)),
      print ('')
      print ('INPUT_FILE video written to %s' % (ofile))
      vidfp.release()
    self.BATCH_RUN_vw.release()


  def on_GUI_batch_run (self):
    self.BATCH_RUN_ofile = self.VIDEO_OUT_FULL_PATH
    # get input from dialog box
    dialog = VideoVizDialogs.StartEndFrameDialog (self)
    S, E, ok = dialog.showDialog (self)
    if ok:
      self.startFI = S
      self.endFI = E

    if self.endFI == -1:
      self.endFI = self.NF-1
    else:
      self.endFI = min (self.NF, self.endFI)
    print ('on_GUI_batch_run(): NF %d, startFI %d, endFI %d, write to %s' % (self.NF, self.startFI, self.endFI, self.BATCH_RUN_ofile))

    if self.VIDEO_FPS == 0:
      self.VIDEO_FPS = var.NEW_VIDEO_FPS
    if self.FOURCC=='XVID':
      fourcc = cv2.cv.CV_FOURCC('X','V','I','D')
    elif self.FOURCC=='MJPG':
      fourcc = cv2.cv.CV_FOURCC('M','J','P','G')

    NY = self.NY
    NX = self.NX
    isColor = False
    if self.I.ndim > 2:
      isColor = True

    self.RUN_MODE = 'BATCH_RUN'
    print ('self.RUN_MODE = %s' % (self.RUN_MODE))
    self.BATCH_RUN_vw = cv2.VideoWriter (self.BATCH_RUN_ofile, fourcc, self.VIDEO_FPS, (NX,NY), isColor)
    if self.BATCH_RUN_vw.isOpened() == False:
      print ('Error: failed to open %s to write!' % (self.BATCH_RUN_ofile))
      return

    print ('Start batch processing... VIDEO_DATA_MODE = %s' % (self.VIDEO_DATA_MODE))
    if self.VIDEO_DATA_MODE == 'MEMORY':
      self.BATCH_RUN_f = self.startFI
      # Turn tick on, set tick to 0 for batch run.
      self.timer.start (0)

    elif self.VIDEO_DATA_MODE == 'FILE':
      # Loop through input video and write all video frames
      self.BATCH_RUN_vidfp = cv2.VideoCapture (self.VIDEO_FULL_PATH)

      self.BATCH_RUN_f = self.startFI
      if self.startFI != 0:
        print ('seek to startFI %d' % (self.startFI))
        ocv_vid.vid_goto_frame (self.BATCH_RUN_vidfp, self.startFI)

      # Turn tick on, set tick to 0 for batch run.
      self.timer.start (0)

    return ok

  def finish_GUI_batch_run (self):
    self.RUN_MODE = 'INTERACTIVE'

    #turn tick off
    self.timer.stop ()

    # Update viz after the loop
    self.proc_frame_viz ()

    self.slider.setValue (self.FI)
    # Update frameTextEdit, timeTextEdit and status bar
    f_str = '%d' % (self.FI)
    self.frameTextEdit.setText (f_str)
    t = ocv_vid.frame_to_video_time (self.VIDFP, self.VIDEO_FPS, self.FI)
    t_str = ocv_vid.time_s_to_hms (t)
    self.timeTextEdit.setText (t_str)
    self.updateStatusBar ()



  def cmd_batch_run (self):
    self.BATCH_RUN_ofile = self.VIDEO_OUT_FULL_PATH
    if self.endFI == -1:
      self.endFI = self.NF-1
    else:
      self.endFI = min (self.NF, self.endFI)
    print ('cmd_batch_run(): NF %d, startFI %d, endFI %d' % (self.NF, self.startFI, self.endFI))

    if self.VIDEO_FPS == 0:
      self.VIDEO_FPS = var.NEW_VIDEO_FPS
    if self.FOURCC=='XVID':
      fourcc = cv2.cv.CV_FOURCC('X','V','I','D')
    elif self.FOURCC=='MJPG':
      fourcc = cv2.cv.CV_FOURCC('M','J','P','G')

    NY = self.NY
    NX = self.NX
    isColor = False
    if self.I.ndim > 2:
      isColor = True

    self.RUN_MODE = 'BATCH_RUN'
    self.BATCH_RUN_vw = cv2.VideoWriter (self.BATCH_RUN_ofile, fourcc, self.VIDEO_FPS, (NX,NY), isColor)
    if self.BATCH_RUN_vw.isOpened() == False:
      print ('Error: failed to open %s to write!' % (self.BATCH_RUN_ofile))
      return

    print ('Start cmd batch processing...')

    # Loop through input video and write all video frames
    print ('input %s' % (self.VIDEO_FULL_PATH))
    print ('write to %s' % (self.BATCH_RUN_ofile))
    self.BATCH_RUN_vidfp = cv2.VideoCapture (self.VIDEO_FULL_PATH)

    self.BATCH_RUN_f = self.startFI
    if self.startFI != 0:
      print ('seek to startFI %d' % (self.startFI))
      ocv_vid.vid_goto_frame (self.BATCH_RUN_vidfp, self.startFI)

    while self.BATCH_RUN_f <= self.endFI:
      # Run process step on I
      ts = timeit.default_timer()
      I = ocv_vid.vid_read_frame (self.BATCH_RUN_vidfp)
      if I is None:
        print ('frame %d not readable, skipped proc.' % (self.BATCH_RUN_f))
      else:
        self.I = I
        self.FI = self.BATCH_RUN_f
        self.proc_frame_run_process ()
        self.proc_frame_viz ()
        vizI = self.proc_frame_viz_drawcmd (force_origin_scale=True)
        #io.imsave ('vizI%d.png' % (self.FI), vizI)

        #convert rgb_img vizI to bgr_img
        r,g,b = cv2.split (vizI) #self.IOut
        bgr_img = cv2.merge ([b,g,r])
        self.BATCH_RUN_vw.write (bgr_img)
        print ('%d' % (self.BATCH_RUN_f)),

      te = timeit.default_timer()
      elapsed_t = te - ts
      self.PROCESS_FPS = 1.0/elapsed_t
      proc_text = 'Proc %.2fs FPS %.2f (%.2fx)' % (elapsed_t, self.PROCESS_FPS, self.PROCESS_FPS/self.VIDEO_FPS)

      # increase BATCH_RUN step
      self.BATCH_RUN_f = self.BATCH_RUN_f+1

    # BATCH_RUN finished
    print ('')
    print ('BATCH_RUN finished: video written to %s' % (self.BATCH_RUN_ofile))
    self.BATCH_RUN_vidfp.release()
    self.BATCH_RUN_vw.release()

    self.RUN_MODE = 'INTERACTIVE'


  def on_save_canvas (self):
    fileName, filter = QFileDialog.getSaveFileName(self,
                                     self.tr('Save current plot (frame)'),
                                     '',
                                     self.tr('PNG Files (*.png);;All Files (*)'))
    print ('on_save_canvas() %s' % (fileName))
    global FIG_DPI
    if len (fileName):
      self.canvas.print_figure (fileName, dpi=FIG_DPI)
      self.statusBar().showMessage('Saved to %s' % fileName, 10000)

  # ========== Edit Menu Handler ==========

  def on_paste_into_cur_frame (self):
    if self.VIDEO_DATA_MODE != 'MEMORY':
      print ('This action is only supported in VIDEO_DATA_MODE = MEMORY')
      return
    clipb = QApplication.clipboard()
    qImg = clipb.image()
    if qImg.isNull():
      print ('clipboard does not contain an image!')
      return
    I = np_ocv_qim_convert.QImageToNpRGB888 (qImg)
    print ('on_paste_into_cur_frame(): paste I %dx%d into cur frame %dx%d' % (I.shape[1], I.shape[0], self.I.shape[1], self.I.shape[0]))
    h = min (I.shape[0], self.I.shape[0])
    w = min (I.shape[1], self.I.shape[1])
    # To resolve error of 'cannot get single-segment buffer for dis-contiguous array'
    # we need to make a copy of the new numpy array
    self.I = I[:h, :w, :].copy()
    self.VIDEO_MEM_BLOCK[self.FI] = self.I
    self.IOut = self.I
    self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
    self.visualizeImg (self.qImg)

  # ========== View Menu Handler ==========

  def get_zoom_scale_info (self):
    if var.VIZ_ZOOMIN == 1:
      info = 'Scale %.4f[%d]' % (var.VIZ_SCALE, self.scale_idx)
    else:
      info = 'Zoom %d[%d]' % (var.VIZ_ZOOMIN, self.zoom_idx)
    return info

  def zoom_in (self):
    super (VideoVizWnd, self).zoom_in ()
    info = self.get_zoom_scale_info ()
    self.zoomScaleLabel.setText (info)

  def zoom_out (self):
    super (VideoVizWnd, self).zoom_out ()
    info = self.get_zoom_scale_info ()
    self.zoomScaleLabel.setText (info)

  def on_fit_window_to_view (self):
    # Resize window to fit current image view (with scale or zoom)
    # Done by proper use of sizeHint(), updateGeometry(), adjustSize()
    w = self.vizWidget.width()
    h = self.vizWidget.height()
    if var.VERBOSE>1:
      print ('on_fit_window_to_view(): vizWidget [w %d, h %d]' % (w, h))
    # Add a 2 border pixels to ScrollArea -- good for Win10
    self.vizWidgetScrollArea.setMinimumSize (w+var.VIZ_AREA_PADDING_W, h+var.VIZ_AREA_PADDING_H)
    self.vizWidgetScrollArea.adjustSize ()
    self.mainWidget.adjustSize ()
    self.updateGeometry ()
    self.adjustSize ()
    # After adjustSize(), reset min size to (0,0) i.e. disable it.
    self.vizWidgetScrollArea.setMinimumSize (0, 0)

  def on_negative_img (self):
    if self.activatedProcessAct == self.negativeImgAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.negativeImgAct
    self.activatedProcessAct.setChecked (True)
    # Run process on current frame
    self.proc_frame ()

  def on_mirror_img (self):
    if self.activatedProcessAct == self.mirrorImgAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.mirrorImgAct
    self.activatedProcessAct.setChecked (True)
    # Run process on current frame
    self.proc_frame ()

  def on_img_conv (self):
    if self.activatedProcessAct == self.convolveImgAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.convolveImgAct
    self.activatedProcessAct.setChecked (True)
    # Run process on current frame
    self.proc_frame ()

  def on_sobel_gradient (self):
    if self.activatedProcessAct == self.sobelGradientAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.sobelGradientAct
    self.activatedProcessAct.setChecked (True)
    # Run process on current frame
    self.proc_frame ()

  def on_frame_diff (self):
    if self.activatedProcessAct == self.frameDiffAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.frameDiffAct
    self.activatedProcessAct.setChecked (True)
    # Run process on current frame
    self.proc_frame ()

  def frame_diff_proc (self):
    if self.I_PREV is None:
      print ('frame_diff_proc(): self.I_PREV is None!')
      self.IOut = self.I
    else:
      self.IOut = self.I - self.I_PREV + 128


  ###############################################

  def on_about(self):
    msg = ''' Video Visualizer :
      <p> This <b> Video Visualizer </b> visualize a video in a PySide GUI App.
      <p/>
      Author: Ming-Ching Chang
      Version: 2018

      Run:
        VideoViz.py <input.avi>
    '''
    QMessageBox.about(self, 'VideoViz', msg.strip())

  ###############################################
  # Video Frame Playback and Process
  ###############################################

  def on_frame_first (self):
    newFI = 0
    if self.FI == 0:
      print ('on_frame_first(): already at first frame')
      self.proc_frame (newFI)
    self.slider.setValue (newFI)

  def on_frame_last (self):
    newFI = self.NF-1
    if self.FI == newFI:
      print ('on_frame_last(): already at last frame')
      self.proc_frame (newFI)
    self.slider.setValue (newFI)

  def on_frame_prev (self):
    if self.FI-1 >= 0:
      newFI = self.FI-1
    else:
      print ('on_frame_prev(): already at first frame')
      newFI = 0
      self.proc_frame (newFI)
    self.slider.setValue (newFI)

  def on_frame_next (self):
    if self.FI+1 < self.NF:
      newFI = self.FI+1
    else:
      print ('on_frame_next(): already at last frame')
      newFI = self.NF-1
      self.proc_frame (newFI)
    self.slider.setValue (newFI)

  def on_play (self):
    if self.timer.isActive():
      self.playButton.setText ('Pause')
      self.timer.stop ()
      if var.VERBOSE>2:
        print ('Paused: timer stopped')
    else:
      self.playButton.setText ('Play')
      self.timer.start (self.timerTickms)
      if var.VERBOSE>2:
        print ('Playing: timer is active')

  def stop_playing (self):
    self.playButton.setText ('Pause')
    self.timer.stop ()
    if var.VERBOSE>2:
      print ('Paused: timer stopped')

  def on_proc_button (self):
    self.proc_frame ()

  def on_step_button (self):
    step_size = self.stepSizeSpinBox.value()
    n = self.FI + step_size
    if n < self.NF:
      newFI = n
    else:
      if VideoViz_var.LOOP_VIDEO:
        if var.VERBOSE>1:
          print ('Loop video to frame 0')
        newFI = 0
      else:
        print ('on_step_button(): already at last frame')
        newFI = self.NF-1
      self.proc_frame (newFI)
    self.stop_playing ()
    self.slider.setValue (newFI)

  def on_play_tick_speed_change (self):
    str = self.playSpeedComboBox.currentText()
    if str == 'fastest':
      self.timerTickms = 0
      print ('on_play_tick_speed_change(): set timer tick delay to 0 (fastest)')
    else:
      s = str.split('x')
      # use eval('value') to evaluate things like eval('1/3')
      # See https://stackoverflow.com/questions/9407640/python-eval-that-coerces-values-to-floating-point
      s2 = s[0]+'.0'
      s3 = s2.encode('ascii', 'ignore')
      speed = eval(s3)
      speedv = self.VIDEO_FPS * speed
      self.timerTickms = 1000.0/speedv
      print ('on_play_tick_speed_change(): %s , speed = %.3f, timer = %.2f ms' % (str, speed, self.timerTickms))

    self.timer.setInterval (self.timerTickms)

  def on_play_tick_speed_inc (self):
    # decrease playSpeedComboBox.currentIndex() by 1
    ci = max (self.playSpeedComboBox.currentIndex()-1, 0)
    self.playSpeedComboBox.setCurrentIndex (ci)

  def on_play_tick_speed_dec (self):
    # increase playSpeedComboBox.currentIndex() by 1
    ci = min (self.playSpeedComboBox.currentIndex()+1, self.playSpeedComboBox.count()-1)
    self.playSpeedComboBox.setCurrentIndex (ci)

  def on_step_size_inc (self):
    # increase stepSizeSpinBox.value() by 1
    v = min (self.stepSizeSpinBox.maximum(), self.stepSizeSpinBox.value()+1)
    self.stepSizeSpinBox.setValue (v)

  def on_step_size_dec (self):
    # decrease stepSizeSpinBox.value() by 1
    v = max (self.stepSizeSpinBox.minimum(), self.stepSizeSpinBox.value()-1)
    self.stepSizeSpinBox.setValue (v)

  def on_tick (self):
    if self.RUN_MODE == 'INTERACTIVE':
      # In every tick, increase FI and handle Loop
      step_sz = self.stepSizeSpinBox.value()
      newFI = self.FI + step_sz
      if newFI >= self.NF:
        if VideoViz_var.LOOP_VIDEO:
          if var.VERBOSE>1:
            print ('on_tick(): Loop video to frame 0')
          newFI = 0
        else:
          newFI = self.NF-1
          if var.CLOSE_PROGRAM_AT_VIDEO_END:
            print ('on_tick(): End of video reached. Exit program.')
            self.close()
          else:
            print ('on_tick(): End of video reached. Stop ticking.')
            self.stop_playing ()

      if var.VERBOSE>2:
        print ('on_tick(): go to frame %d' % (newFI))
      self.proc_frame (newFI)
      self.slider.setValue (newFI)

    elif self.RUN_MODE == 'BATCH_RUN':
      if self.VIDEO_DATA_MODE == 'MEMORY':
        #proc_text = 'Processing %d' % (self.BATCH_RUN_f)
        #self.procInfoLabel.setText (proc_text)
        ts = timeit.default_timer()

        # Run process step on I
        I = self.VIDEO_MEM_BLOCK[self.BATCH_RUN_f]
        self.I = I
        self.proc_frame_run_process ()
        self.proc_frame_viz ()
        vizI = self.proc_frame_viz_drawcmd (force_origin_scale=True)
        #io.imsave ('vizI%d.png' % (self.FI), vizI)

        #convert rgb_img I to bgr_img
        r,g,b = cv2.split (vizI) #self.IOut
        bgr_img = cv2.merge ([b,g,r])
        self.BATCH_RUN_vw.write (bgr_img)
        print ('%d' % (self.BATCH_RUN_f)),

        te = timeit.default_timer()
        elapsed_t = te - ts
        self.PROCESS_FPS = 1.0/elapsed_t
        proc_text = 'Proc %.2fs FPS %.2f (%.2fx)' % (elapsed_t, self.PROCESS_FPS, self.PROCESS_FPS/self.VIDEO_FPS)
        self.procInfoLabel.setText (proc_text)

        self.slider.setValue (self.FI)
        # Update frameTextEdit, timeTextEdit and status bar
        f_str = '%d' % (self.FI)
        self.frameTextEdit.setText (f_str)
        t = ocv_vid.frame_to_video_time (self.VIDFP, self.VIDEO_FPS, self.FI)
        t_str = ocv_vid.time_s_to_hms (t)
        self.timeTextEdit.setText (t_str)
        self.updateStatusBar ()

        # increase BATCH_RUN step
        self.BATCH_RUN_f = self.BATCH_RUN_f+1

        if self.BATCH_RUN_f >= self.endFI:
          # BATCH_RUN finished
          print ('')
          print ('MEMORY_BLOCK mode: video written to %s' % (self.BATCH_RUN_ofile))
          self.BATCH_RUN_vw.release()
          self.finish_GUI_batch_run ()

      elif self.VIDEO_DATA_MODE == 'FILE':
        #proc_text = 'Processing %d' % (self.BATCH_RUN_f)
        #self.procInfoLabel.setText (proc_text)

        # Run process step on I
        ts = timeit.default_timer()
        I = ocv_vid.vid_read_frame (self.BATCH_RUN_vidfp)
        if I is None:
          print ('frame %d not readable, skipped proc.' % (self.BATCH_RUN_f))
        else:
          self.I = I
          self.FI = self.BATCH_RUN_f
          self.proc_frame_run_process ()
          self.proc_frame_viz ()
          vizI = self.proc_frame_viz_drawcmd (force_origin_scale=True)
          #io.imsave ('vizI%d.png' % (self.FI), vizI)

          #convert rgb_img vizI to bgr_img
          r,g,b = cv2.split (vizI) #self.IOut
          bgr_img = cv2.merge ([b,g,r])
          self.BATCH_RUN_vw.write (bgr_img)
          print ('%d' % (self.BATCH_RUN_f)),

        te = timeit.default_timer()
        elapsed_t = te - ts
        self.PROCESS_FPS = 1.0/elapsed_t
        proc_text = 'Proc %.2fs FPS %.2f (%.2fx)' % (elapsed_t, self.PROCESS_FPS, self.PROCESS_FPS/self.VIDEO_FPS)
        self.procInfoLabel.setText (proc_text)

        self.slider.setValue (self.FI)
        # Update frameTextEdit, timeTextEdit and status bar
        f_str = '%d' % (self.FI)
        self.frameTextEdit.setText (f_str)
        t = ocv_vid.frame_to_video_time (self.VIDFP, self.VIDEO_FPS, self.FI)
        t_str = ocv_vid.time_s_to_hms (t)
        self.timeTextEdit.setText (t_str)
        self.updateStatusBar ()

        # increase BATCH_RUN step
        self.BATCH_RUN_f = self.BATCH_RUN_f+1

        if self.BATCH_RUN_f >= self.endFI:
          # BATCH_RUN finished
          print ('')
          print ('FILE mode: video written to %s' % (self.BATCH_RUN_ofile))
          self.BATCH_RUN_vidfp.release()
          self.BATCH_RUN_vw.release()
          self.finish_GUI_batch_run ()

  def on_slider_update (self):
    # If slider (newFI) is at current FI, no need to update.
    if self.I is not None and self.FI == self.slider.value():
      return

    # Update cur frame index self.FI from slider value
    newFI = self.slider.value()

    if var.VERBOSE>1:
      print ('on_slider_update(): go to frame %d' % (newFI))

    # Run process and visualize
    self.proc_frame (newFI)

    # Update frameTextEdit, timeTextEdit and status bar
    f_str = '%d' % (self.FI)
    self.frameTextEdit.setText (f_str)
    t = ocv_vid.frame_to_video_time (self.VIDFP, self.VIDEO_FPS, self.FI)
    t_str = ocv_vid.time_s_to_hms (t)
    self.timeTextEdit.setText (t_str)


  def proc_frame (self, newFI = None):
    if newFI is None:
      newFI = self.FI
    if var.VERBOSE>1:
      print ('proc_frame%d ' % (newFI)),
    #proc_text = 'Processing %d' % (newFI)
    #self.procInfoLabel.setText (proc_text)
    ts = timeit.default_timer()
    ret = self.proc_frame_read_video (newFI)
    if ret:
      # Run active process for a single step, result in self.IOut
      self.proc_frame_run_process ()
      self.proc_frame_viz ()

      # At step end, make a copy of self.I to be previous frame self.I_PREV
      self.I_PREV = self.I.copy()
      self.FI_PREV = self.FI
    else:
      # In case video frame not readable (broken video, last frame error)
      print ('frame %d not readable, skipped proc.' % (self.FI))

    te = timeit.default_timer()
    elapsed_t = te - ts
    self.PROCESS_FPS = 1.0/elapsed_t
    proc_text = 'Proc %.2fs FPS %.2f (%.2fx)' % (elapsed_t, self.PROCESS_FPS, self.PROCESS_FPS/self.VIDEO_FPS)
    self.procInfoLabel.setText (proc_text)

    self.updateStatusBar ()
    return ret

  def proc_frame_read_video (self, newFI):
    video_changed = True
    if self.VIDEO_DATA_MODE == 'FILE':
      # If current frame self.I is None, read frame Fi
      if self.I is not None and self.FI == newFI:
        # Assume current frame is ready
        if var.VERBOSE>1:
          print ('proc_frame_read_video(): newFI = %d self.I not changed.' % (newFI))
        video_changed = False
      elif newFI == 0:
        # Need to rewind the sequential frame reading
        ocv_vid.vid_goto_frame (self.VIDFP, 0)
        if var.VERBOSE>1:
          print ('proc_frame_read_video(): rewind video to frame 0')
        self.FI = 0
        self.I = ocv_vid.vid_read_frame (self.VIDFP)
      elif newFI == self.FI + 1:
        self.FI = newFI
        # For reading the next frame, no need to seek in video
        self.I = ocv_vid.vid_read_frame (self.VIDFP)
      else:
        forward = newFI - self.FI
        if forward > 0 and forward < 10:
          # For seeking forward for less than 10 frames,
          # reading sequential frames is generally faster than goto frame
          # For 720x480 videos, this is true even up to 20 frames.
          # For 1920x1080 videos, this is true for about 10 frames.
          for f in range(forward):
            I = ocv_vid.vid_read_frame (self.VIDFP)
          self.I = I
          self.FI = newFI
        else:
          # Update self.FI and read self.I from video
          if var.VERBOSE>1:
            print ('proc_frame_read_video(): go to newFI = %d.' % (newFI))
          self.FI = newFI
          ocv_vid.vid_goto_frame (self.VIDFP, self.FI)
          self.I = ocv_vid.vid_read_frame (self.VIDFP)
    elif self.VIDEO_DATA_MODE == 'LIVE':
      # Grab a frame from camera
      self.FI = newFI
      print ('to implement!')
    elif self.VIDEO_DATA_MODE == 'MEMORY':
      # read frame FI from memory block
      if newFI < self.VIDEO_MEM_BLOCK.shape[0]:
        self.I = self.VIDEO_MEM_BLOCK[newFI]
      else:
        print ('proc_frame_read_video() error! newFI %d >= VIDEO_MEM_BLOCK size %d' % (newFI, self.VIDEO_MEM_BLOCK.shape[0]))
      self.FI = newFI

    # Update frameTextEdit and status bar
    f_str = '%d' % (self.FI)
    self.frameTextEdit.setText (f_str)
    t = ocv_vid.frame_to_video_time (self.VIDFP, self.VIDEO_FPS, self.FI)
    t_str = ocv_vid.time_s_to_hms (t)
    self.timeTextEdit.setText (t_str)
    self.updateStatusBar ()

    if video_changed: # update pixelInfoLabel
      if self.mouseX is not None and self.mouseY is not None:
        x = int(self.mouseX)
        y = int(self.mouseY)
        str = self.getMousePixelStr (x, y, self.mouseX, self.mouseY)
        self.pixelInfoLabel.setText (str)

    return self.I is not None

  def proc_frame_run_process (self):
    # By default set IOut to I (no deep copy involved)
    self.IOut = self.I

    if self.activatedProcessAct == self.negativeImgAct:
      self.negative_img_proc ()
    elif self.activatedProcessAct == self.mirrorImgAct:
      self.mirror_img_proc ()
    elif self.activatedProcessAct == self.toGrayImgAct:
      self.to_gray_img_proc ()
    elif self.activatedProcessAct == self.convolveImgAct:
      self.conv_img_proc ()
    elif self.activatedProcessAct == self.sobelGradientAct:
      self.sobel_gradient_proc ()
    elif self.activatedProcessAct == self.frameDiffAct:
      self.frame_diff_proc ()

  def proc_frame_viz (self):
    if var.VERBOSE>1:
      print ('proc_frame_viz FI%d' % (self.FI))
    # Draw self.I or self.IOut
    if self.activatedProcessAct is None:
      self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
      self.visualizeImg (self.qImg, updateGeom=False)
    else:
      self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
      self.visualizeImg (self.qImgOut, updateGeom=False)
      #print ('self.IOut.shape='+str(self.IOut.shape))

  def proc_frame_viz_drawcmd (self, force_origin_scale=False):
    qp = QPainter ()
    # Draw all DRAWCMDS to a visualization Pixmap
    # Note that VizPixmap is in 100% scale.
    # To draw to VizZoominPixmap for the current viewing scale.
    if force_origin_scale:
      pixmap = self.VizPixmap.copy()
      qp.begin (pixmap)
    else:
      pixmap = self.VizZoominPixmap.copy()
      qp.begin (pixmap)

    self.vizWidget.performPaint (qp, force_origin_scale)
    qp.end()
    # Convert pixmap (QPixmap) to QImage
    qImg = pixmap.toImage ()
    vizI = np_ocv_qim_convert.QImageToNpRGB888 (qImg)
    return vizI

  def on_frame_textbox_update (self):
    # Update cur frame index self.FI
    str = unicode(self.frameTextEdit.text())
    frames = map(int, str.split())
    newFI = 0
    if not frames:
      print ('Error on_frame_textbox_update() str = %s' % (str))
      return
    else:
      # take the first integer value
      newFI = frames[0]
    if newFI < 0:
      print ('on_frame_textbox_update() newFI %d < 0, reset to 0' % (newFI))
      newFI = 0
    elif newFI >= self.NF:
      print ('on_frame_textbox_update() newFI %d >= NF %d, reset to %d' % (newFI, self.NF, self.NF-1))
      newFI = self.NF-1

    # Update slider
    self.slider.setValue (newFI)

  def on_time_textbox_update (self):
    # calculate frame newFI from new time
    str = unicode(self.timeTextEdit.text())
    print ('on_frame_textbox_update(): go to time %s' % (str))
    newFI = ocv_vid.video_time_to_frame (self.VIDEO_FPS, str)
    if newFI < 0:
      print ('on_time_textbox_update() newFI %d < 0, reset to 0' % (newFI))
      newFI = 0
    elif newFI >= self.NF:
      print ('on_time_textbox_update(): newFI %d >= NF %d, reset to %d' % (newFI, self.NF, self.NF-1))
      newFI = self.NF-1

    # Update slider
    self.slider.setValue (newFI)

  def close (self):
    if self.VIDFP is not None:
      self.VIDFP.release ()
    super (VideoVizWnd, self).close ()

  # ==================== Mouse Event Handling - Start ====================

  # https://stackoverflow.com/questions/19825650/python-pyqt4-how-to-detect-the-mouse-click-position-anywhere-in-the-window
  def mousePressEvent (self, event):
    pos = event.pos()
    str = None
    if event.buttons() == Qt.LeftButton:
      str = 'L-Click (%d, %d)' % (pos.x(), pos.y())
    elif event.buttons() == Qt.RightButton:
      str = 'R-Click (%d, %d)' % (pos.x(), pos.y())
    self.updateStatusBar (str)


  def mouseMoveEvent (self, event):
    # Show mouse pixel info at pixelInfoLabel
    str = self.calMousePixelStr (event)
    self.pixelInfoLabel.setText (str)
    #self.updateStatusBar (str)

  # ==================== Mouse Event Handling - End ====================

  # ==================== File Drag and Drop - Start ====================
  def dropEvent (self, e):
    # Drop files directly onto the widget
    if e.mimeData().hasUrls:
      e.setDropAction (Qt.CopyAction)
      e.accept()
      # Workaround for OSx dragging and dropping
      for url in e.mimeData().urls():
        fname = str (url.toLocalFile())
        print ('dropEvent: %s' % (fname))

      # We open the last file in the list
      self.VIDEO_FULL_PATH = fname
      fi = QFileInfo (fname)
      fn = fi.fileName()
      fn = fn.encode('ascii', 'ignore')
      self.VIDEO_FILE = fn
      print ('file in ASCII %s' % (fn))

      #print ('dropEvent(): ImgFile = %s' % (self.ImgFile))
      var.VIZ_SCALE = 1.0
      var.VIZ_ZOOMIN = 1
      self.scale_idx = 0
      self.zoom_idx = 0
      var.DRAWCMD_LIST = []
      self.load_video_show ()
    else:
      e.ignore()
  # ==================== File Drag and Drop - End ====================


# ========== App Main ==========

if __name__ == '__main__':
  import sys
  if len(VideoViz_var.INPUT_VIDEO) == 0:
    if len(sys.argv) == 1:
      print ('Run: VideoVizWnd.py batch')
      print ('Run: <input.avi>')

  # RUNMODE can be 'CMDLINE', 'GLOBAL_VAR', 'BATCH'
  RUNMODE = 'GLOBAL_VAR'

  #VideoViz_var.INPUT_PATH = '.'
  #VideoViz_var.INPUT_VIDEO = 'avi_frames.avi' #'Loc1_1a.avi'

  if len(sys.argv) > 1:
    if sys.argv[1] == 'batch':
      RUNMODE = 'BATCH'   # Enable batch mode
    else:
      RUNMODE = 'CMDLINE' # Use the command-line input file
      VideoViz_var.INPUT_VIDEO = str(sys.argv[1])

  print ('main(): RUNMODE = %s' % (RUNMODE))
  if RUNMODE != 'BATCH': # GUI mode:
    app = QApplication (sys.argv)
    # Set application Icon
    # See https://stackoverflow.com/questions/35272349/window-icon-does-not-show
    app.setWindowIcon (QIcon('VideoViz.png'))
    wnd = VideoVizWnd ()
    wnd.show ()
    sys.exit (app.exec_())

  else: # BATCH mode
    print ('main(): Run Batch Mode: %d batch jobs.' % (len(VideoViz_var.BATCH_CASES)))
    # Create app for batch run
    app = QApplication (sys.argv)

    print ('BATCH_CASES = ' + str (VideoViz_var.BATCH_CASES))

    batch_start_time = timeit.default_timer()

    for r,RUNCASE in enumerate(VideoViz_var.BATCH_CASES):
      print ('========== Batch %d/%d %s ==========' % (r, len(VideoViz_var.BATCH_CASES), RUNCASE))

      if RUNCASE == 'avi_frames':
        INPUT_VIDEO = 'avi_frames.avi'
      elif RUNCASE == 'ball_rolling':
        INPUT_VIDEO = 'ball_rolling_108x72_1.avi'
      elif RUNCASE == 'car':
        INPUT_VIDEO = 'car.avi'
      elif RUNCASE == 'Loc1_1a':
        INPUT_VIDEO = 'Loc1_1a.avi'
      elif RUNCASE == 'MiceBrainArtery':
        INPUT_VIDEO = 'MiceBrainArtery_seq15c.avi'
      elif RUNCASE == 'Track2_9_10s':
        INPUT_VIDEO = 'Track2_9_10s.mp4'

      VideoViz_var.INPUT_VIDEO = INPUT_VIDEO

      OUTPUT_VIDEO = RUNCASE + '_VideoOut.avi'
      VideoViz_var.OUTPUT_VIDEO = OUTPUT_VIDEO

      wnd = VideoVizWnd ()

      # Turn on RUNPROC and run on_GUI_batch_run()
      if VideoViz_var.RUNPROC == 'negative_img':
        wnd.on_negative_img ()
      elif VideoViz_var.RUNPROC == 'mirror_img':
        wnd.on_mirror_img ()
      elif VideoViz_var.RUNPROC == 'conv_img':
        wnd.on_conv_img ()
      elif VideoViz_var.RUNPROC == 'sobel_gradient':
        wnd.on_sobel_gradient ()
      elif VideoViz_var.RUNPROC == 'morph_dilation':
        wnd.on_morph_dilation ()
      elif VideoViz_var.RUNPROC == 'morph_dilation':
        wnd.on_morph_dilation ()
      elif VideoViz_var.RUNPROC == 'morph_erosion':
        wnd.on_morph_erosion ()
      elif VideoViz_var.RUNPROC == 'morph_opening':
        wnd.on_morph_opening ()
      elif VideoViz_var.RUNPROC == 'morph_closing':
        wnd.on_morph_closing ()
      elif VideoViz_var.RUNPROC == 'frame_diff':
        wnd.on_frame_diff ()

      wnd.cmd_batch_run ()

      print ('========== Batch %d/%d %s - Done ==========' % (r, len(VideoViz_var.BATCH_CASES), RUNCASE))

    batch_end_time = timeit.default_timer()
    elapsed_sec = batch_end_time - batch_start_time
    m, s = divmod (elapsed_sec, 60)
    h, m = divmod (m, 60)
    print ('---> Batch Run takes %d:%02d:%02d' % (h, m, s))

    sys.exit ()
