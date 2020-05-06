# Python PySide OpenCV Video GUI App
# Author:  Ming-Ching Chang
# Version / Development Log:
#   2018/01/28  Initial Version

import copy
import numpy as np
#import skimage.io as io
from scipy.linalg import rq
from scipy.linalg import sqrtm
import random

import cv2
import cv
import sys
from PySide.QtCore import *
from PySide.QtGui import *

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
#import pylab

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

# for Matplotlib 1.3 and before
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
# for Matplotlib 1.5 and after
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# import the im_draw_text.py
#import im_draw_text as imdt

# verbose print level:
#   0: no print out
#   1: succinct
#   2: verbose
#   3: detailed info
#   4: detailed debug info
VERBOSE = 1

# ========== Video Modules ==========

# Read a specified frame from a video
# result is numpy img[y,x,c] in RGB
def vid_get_frame (video_in, frame_num):
  vidfp = cv2.VideoCapture (video_in)
  vidfp.set (cv.CV_CAP_PROP_POS_FRAMES, frame_num)
  _,bgr_img = vidfp.read()
  if bgr_img is None:
    return bgr_img
  else:
    b,g,r = cv2.split (bgr_img)       # get b,g,r
    rgb_img = cv2.merge ([r,g,b])     # switch it to rgb
  return rgb_img

# count total number of frames in the input video
# This is the dumb way (slow). Better solution?
def vid_count_num_frames (video_in):
  vidfp = cv2.VideoCapture (video_in)
  count = 0
  while True:
    _,img = vidfp.read()
    if img is None:
      break
    count += 1
  return count


# ========== Main GUI Window ==========

class AppForm (QMainWindow):
  def __init__(self, parent=None):

    # ===== Initialization =====
    self.FI = 0
    self.NF = 0
    self.NX = 0
    self.NY = 0
    self.NC = 0
    self.input_video = ''
    self.READ_FULL_VIDEO = False
    
    global INPUT_VIDEO
    self.input_video = INPUT_VIDEO

    # ===== App init =====
    QMainWindow.__init__(self, parent)
    self.setWindowTitle ('Py Video App')

    self.load_video (self.input_video)
              
    self.create_menu()
    self.createMainFrame()
    
    # Status Bar
    self.status_label = QLabel('', self)
    self.statusBar().addWidget(self.status_label, 1)
    self.updateStatusBar()

    self.on_draw()

    if VERBOSE>3:
      print ('end of AppForm (QMainWindow).__init__()')

  def createMainFrame (self):
    self.main_frame = QWidget()

    # Create the mpl Figure and FigCanvas objects.
    # 5x4 inches, 100 dots-per-inch
    # self.fig = Figure((5, 4), dpi=100)
    global FIG_WIDTH_IN, FIG_HEIGHT_IN, FIG_DPI

    self.fig = Figure((FIG_WIDTH_IN, FIG_HEIGHT_IN), dpi=FIG_DPI)
    self.canvas = FigureCanvas (self.fig)
    self.canvas.setParent (self.main_frame)

    # Since we have only one plot, we can use add_axes
    # instead of add_subplot, but then the subplot
    # configuration tool in the navigation toolbar wouldn't
    # work.
    #
    self.axes = self.fig.add_subplot(111)

    # Bind the 'pick' event for clicking on one of the bars
    #self.canvas.mpl_connect('pick_event', self.on_pick)

    #self.canvas.mpl_connect('button_press_event', self.on_click)

    # Create the navigation toolbar, tied to the canvas
    #
    self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

    # Other GUI controls
    #
    self.slider_label = QLabel('Frame#')
    self.textbox = QLineEdit()
    #self.textbox.setMinimumWidth(200)
    self.textbox.setMaximumWidth(40)
    self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_textbox_update)

    self.frame_first_button = QPushButton('|<')
    self.frame_first_button.setMaximumWidth (15)
    self.connect(self.frame_first_button, SIGNAL('clicked()'), self.on_frame_first)

    self.frame_prev_button = QPushButton('<')
    self.frame_prev_button.setMaximumWidth (15)
    self.connect(self.frame_prev_button, SIGNAL('clicked()'), self.on_frame_prev)

    self.frame_next_button = QPushButton('>')
    self.frame_next_button.setMaximumWidth (15)
    self.connect(self.frame_next_button, SIGNAL('clicked()'), self.on_frame_next)

    self.frame_last_button = QPushButton('>|')
    self.frame_last_button.setMaximumWidth (15)
    self.connect(self.frame_last_button, SIGNAL('clicked()'), self.on_frame_last)

    # Set the slider range to be the video's total frame numbers.
    self.slider = QSlider(Qt.Horizontal)
    self.slider.setRange(0, self.NF-1)
    print ('  slider range [0, %d]' % (self.NF-1))
    # Start with the first frame
    #self.slider.setValue(0)
    self.slider.setValue (self.FI)
    self.slider.setTracking(True)
    self.slider.setTickPosition(QSlider.TicksBothSides)
    self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_slider_update)

    #
    # Layout with box sizers
    #
    hbox = QHBoxLayout()

    for w in [ self.slider_label, self.slider, self.textbox, self.frame_first_button, self.frame_prev_button, self.frame_next_button, self.frame_last_button ]:
      hbox.addWidget(w)
      hbox.setAlignment(w, Qt.AlignVCenter)
    #hbox.setFixedHeight (50)
    #hbox.setMaximumHeight (50)
    #hbox.setSizeConstraint (QLayout.SetFixedSize)
    hbox.setSizeConstraint (QLayout.SetMinimumSize)

    vbox = QVBoxLayout()
    vbox.addWidget(self.canvas)
    vbox.addLayout(hbox)
    vbox.addWidget(self.mpl_toolbar)

    self.main_frame.setLayout(vbox)
    self.setCentralWidget(self.main_frame)
   
  def create_menu (self):
    # ==========
    self.file_menu = self.menuBar().addMenu('&File')

    file_new_clear_data_action = self.create_action ('&New (Clear Data)', shortcut='Ctrl+R', slot=self.on_file_new_clear_data, tip='Reset the plot')
    
    load_video_action = self.create_action ('&Load Video...', shortcut='Ctrl+V', slot=self.on_load_video, tip='Load Video (standard formats AVI, MP4, WMV, ...)')
    
    save_plot_action = self.create_action ('&Save Plot...',
        shortcut='Ctrl+S', slot=self.on_save_frame_plot,
        tip='Save the plot')
    quit_action = self.create_action('&Quit', slot=self.close,
        shortcut='Ctrl+Q', tip='Close the application')

    self.add_actions (self.file_menu,
        (file_new_clear_data_action, 
         load_video_action, None, 
         save_plot_action, None, quit_action))

    # ==========
    self.help_menu = self.menuBar().addMenu('&Help')
    about_action = self.create_action ('&About',
        shortcut='F1', slot=self.on_about,
        tip='About the demo')
        
    set_verbose_action = self.create_action ('Verbose',
        shortcut='', slot=self.on_set_verbose,
        tip='Set verbose level')        

    self.add_actions(self.help_menu, (about_action, None, set_verbose_action))

  def on_file_new_clear_data (self):
    # Show the first frame
    self.FI = 0
    f_str = '%d' % (self.FI)
    self.textbox.setText (f_str)
    
    global FIG_WIDTH_IN, FIG_HEIGHT_IN, FIG_DPI
    print ('on_file_new_clear_data() fig W%.2f H%.2f in, DPI=%.2f' % (FIG_WIDTH_IN, FIG_HEIGHT_IN, FIG_DPI)
    self.fig.set_size_inches (FIG_WIDTH_IN, FIG_HEIGHT_IN))
    
    # Clear Video
    self.IMGSEQ_IN = None
    self.NF = 0
    self.NY = 0
    self.NX = 0
    self.NC = 0
    self.CUR_FRAME = None
    
    self.on_draw ()
    
  def load_video (self, input_video):
    print ('load_video(): %s' % (input_video))
    self.NF =  vid_count_num_frames (input_video)
    self.CUR_FRAME = vid_get_frame (input_video, self.FI)
    if self.CUR_FRAME is not None:
      self.NY = self.CUR_FRAME.shape[0]
      self.NX = self.CUR_FRAME.shape[1]
      self.NC = self.CUR_FRAME.shape[2]
    else:
      self.NY = 0
      self.NX = 0
      self.NC = 0      
    print ('  %s %d frames [y%d,x%d] color%d in RGB' % (input_video, self.NF, self.NY, self.NX, self.NC))
    if self.NF > 0:    
      return True
    else:
      return False
      
  def on_load_video (self):
    fileName, filter = QFileDialog.getOpenFileName(self,
                                     self.tr('Load Video'),
                                     '',
                                     self.tr('AVI (*.avi);;MP4 (*.mp4);;All Files (*)'))
    print ('on_load_video() %s' % (fileName))
    if fileName:
      success = self.load_video (fileName)
      if success:
        self.input_video = fileName
        # current frame index
        self.FI = 0
        f_str = '%d' % (self.FI)
        self.textbox.setText (f_str)        
        self.slider.setRange(0, self.NF-1)
        self.on_draw()
        self.updateStatusBar()
    
  def on_save_frame_plot(self):
    fileName, filter = QFileDialog.getSaveFileName(self,
                                     self.tr('Save current plot (frame)'),
                                     '',
                                     self.tr('PNG Files (*.png);;All Files (*)'))
    print ('on_save_frame_plot() %s' % (fileName))
    global FIG_DPI
    if len (fileName):
      self.canvas.print_figure (fileName, dpi=FIG_DPI)
      self.statusBar().showMessage('Saved to %s' % fileName, 10000)

  def on_about(self):
    msg = ''' PySide OpenCV Video GUI App :
    
      Author: Ming-Ching Chang
      Version: 2018
      
      Run: 
        vidapp.py <input.avi>
    '''
    QMessageBox.about(self, 'Video GUI App', msg.strip())

  def on_set_verbose (self):
    global VERBOSE
    v_str = '%d' % (VERBOSE)
    prompt_text = 'Set verbose level:'
    text, ok = QInputDialog.getText(self, '(0: xx, 1: xx, 2: xx, 3: xx, 4: xx', prompt_text)
    if ok:
      v = map(float, text.split())
      print ('new VERBOSE value = %d' % (v[0])) 
      VERBOSE = v[0]    
      
  def on_frame_first (self):
    self.FI = 0
    f_str = '%d' % (self.FI)
    self.textbox.setText (f_str)
    self.slider.setValue (self.FI)
    self.updateStatusBar()

  def on_frame_last (self):
    self.FI = self.NF-1
    f_str = '%d' % (self.FI)
    self.textbox.setText (f_str)
    self.slider.setValue (self.FI)
    self.updateStatusBar()

  def on_frame_prev (self):
    f = self.FI
    if f-1 >= 0:
      self.FI = f-1

    f_str = '%d' % (self.FI)
    self.textbox.setText (f_str)
    self.slider.setValue (self.FI)
    self.updateStatusBar()

  def on_frame_next (self):
    f = self.FI
    if f+1 < self.NF:
      self.FI = f+1

    f_str = '%d' % (self.FI)
    self.textbox.setText (f_str)
    self.slider.setValue (self.FI)
    self.updateStatusBar()

  def on_slider_update (self):
    # Update cur frame index self.FI
    f = self.slider.value()
    self.FI = f

    # Update textbox
    f_str = '%d' % (f)
    self.textbox.setText (f_str)
    self.on_draw ()
    self.updateStatusBar()

  def on_textbox_update (self):
    # Update cur frame index self.FI
    str = unicode(self.textbox.text())
    frames = map(int, str.split())
    f = 0
    if not frames:
      print ('Error on_textbox_update() str = %s' % (str))
      return
    else:
      # take the first integer value
      f = frames[0]
    if f >= 0 and f < self.NF:
      self.FI = f
    else:
      print ('Error on_textbox_update() fi=%d NF=%d' % (f, NF))
      return

    # Update slider
    self.slider.setValue (self.FI)
    self.updateStatusBar()

  def on_draw (self):
    # Redraws the figure
    self.axes.cla()

    # Draw current frame specified in self.FI
    if self.FI >=0 and self.FI < self.NF:
      if VERBOSE>1:  
        print ('  frame %d' % (self.FI))
      if self.READ_FULL_VIDEO:
        self.CUR_FRAME = self.IMGSEQ_IN[self.FI]
      else:
        self.CUR_FRAME = vid_get_frame (self.input_video, self.FI)

      self.axes.imshow (self.CUR_FRAME, aspect='equal', interpolation='nearest')
      #self.axes.axis([0, self.NX-1, 0, self.NY-1])
      # Here we set the Y axis to go from 480 to 0 so that the image is flipped to the way we want.
      self.axes.axis([0, self.NX-1, self.NY-1, 0])
    else:
      #draw empty image
      I = np.zeros((640, 480, 3), dtype=np.uint8)
      I.fill (255)
      self.axes.imshow (I, aspect='equal', interpolation='nearest')
      self.axes.axis([0, 640, 480, 0])
      
    # Tighten figure layout (remove white space)
    # http://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot    
    self.fig.tight_layout()
    
    # Run canvas.draw() at the end after all visualization are done.
    self.canvas.draw()

    return True

    
  def updateStatusBar (self):
    if self.READ_FULL_VIDEO:
      video_in_mem_str =  '(Full video in memory)'
    else:
      video_in_mem_str = '(Current frame %d)' % (self.FI)
    self.status_text = '%s [nx=%d, ny=%d] nf=%d nc=%d %s' % (self.input_video, self.NX, self.NY, self.NF, self.NC, video_in_mem_str)
    self.statusBar().showMessage (self.status_text)


  def add_actions (self, target, actions):
    for action in actions:
      if action is None:
        target.addSeparator()
      else:
        target.addAction(action)

  def create_action (self, text, slot=None, shortcut=None,
                     icon=None, tip=None, checkable=False,
                     signal='triggered()'):
    action = QAction (text, self)
    if icon is not None:
      action.setIcon (QIcon(':/%s.png' % icon))
    if shortcut is not None:
      action.setShortcut(shortcut)
    if tip is not None:
      action.setToolTip(tip)
      action.setStatusTip(tip)
    if slot is not None:
      self.connect(action, SIGNAL(signal), slot)
    if checkable:
      action.setCheckable(True)
    return action

# ========== General Parameters ==========
INPUT_VIDEO = ''

# Set figure to be at least 16x12 inches (better match your display)
# This is related to fig drawing size and window size
FIG_WIDTH_IN = 16 #8
FIG_HEIGHT_IN = 12 #6
FIG_DPI = 100

# ========== Output ==========
OUTPUT_VIDEO = 'output.avi'

def main():
  global INPUT_VIDEO
  if len(INPUT_VIDEO) == 0 :
    if len(sys.argv) == 1:
      print ('Run: <input.avi>')
      #sys.exit()

  if len(sys.argv) > 1:
    # Use the command-line input file
    INPUT_VIDEO = str(sys.argv[1])
  else:
    # Use the pre-defined INPUT_VIDEO
    pass
  print ('INPUT_VIDEO = %s' % (INPUT_VIDEO))

  app = QApplication (sys.argv)
  form = AppForm ()
  form.show ()
  app.exec_()


if __name__ == '__main__':
  main()
