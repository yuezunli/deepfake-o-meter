# Python PySide OpenCV Video GUI Example
# Ming-Ching Chang


import numpy as np
import skimage.io as io

import cv2
import cv

import sys
from PySide.QtCore import *
from PySide.QtGui import *

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
import pylab

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

# for Matplotlib 1.3 and before
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
# for Matplotlib 1.5 and after
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

# ========== Input ==========
INPUT_VIDEO = 'car.avi'
#INPUT_VIDEO = 'Sony_PTZ_south_calibration.avi'
#INPUT_VIDEO = ''

# ========== Output ==========
OUTPUT_VIDEO = 'output.avi'


# ========== Modules ==========

# Read a specified frame from a video
# result is numpy img[y,x,c] in RGB
def vid_get_frame (video_in, frame_num):
  vidfp = cv2.VideoCapture (video_in)
  vidfp.set (cv.CV_CAP_PROP_POS_FRAMES, frame_num)
  _,bgr_img = vidfp.read()
  if bgr_img == None:
    return bgr_img
  else:
    b,g,r = cv2.split (bgr_img)       # get b,g,r
    rgb_img = cv2.merge ([r,g,b])     # switch it to rgb
  return rgb_img

# Read an image sequence from the video
# result is numpy vid[t,y,x,c] in RGB
def vid_read_imgseq (video_in):
  vidfp = cv2.VideoCapture (video_in)
  imgseq = []
  count = 0
  while True:
    _,bgr_img = vidfp.read()
    if bgr_img == None:
      break
    b,g,r = cv2.split (bgr_img)       # get b,g,r
    rgb_img = cv2.merge ([r,g,b])     # switch it to rgb
    imgseq.append (rgb_img)
    print ('%d' % (count), end=' ')
    count += 1
  print ('')
  return np.array (imgseq)

# Read an image sequence from the video
# result is numpy vid[t,y,x]
def vid_read_imgseq_gray (video_in):
  vidfp = cv2.VideoCapture (video_in)
  imgseq = []
  count = 0
  while True:
    _,bgr_img = vidfp.read()
    if bgr_img == None:
      break
    gray = cv2.cvtColor (bgr_img, cv.CV_RGB2GRAY)
    imgseq.append (gray)
    _,img = vidfp.read()
    print ('%d' % (count), end=' ')
  print ('')
  return np.array (imgseq)


# count total number of frames in the input video
# This is the dumb way (slow). Better solution?
def vid_count_num_frames (video_in):
  vidfp = cv2.VideoCapture (video_in)
  count = 0
  while True:
    _,img = vidfp.read()
    if img == None:
      break
    count += 1
  return count

# write [t,y,x,c] numpy array to video.avi
# See http://docs.opencv.org/trunk/doc/py_tutorials/py_gui/py_video_display/py_video_display.html
def write_imgseq_to_video (imgseq, name):
  NT = imgseq.shape[0]
  NY = imgseq.shape[1]
  NX = imgseq.shape[2]
  #fourcc = cv2.VideoWriter_fourcc(*'XVID')
  #fourcc = cv2.cv.CV_FOURCC('M','J','P','G')
  fourcc = cv2.cv.CV_FOURCC('X','V','I','D')
  fps = 25
  isColor = False
  if imgseq.ndim > 3:
    isColor = True
  vw = cv2.VideoWriter (name, fourcc, fps, (NX,NY), isColor)
  for rgb_img in imgseq:
    #convert rgb_img to bgr_img
    r,g,b = cv2.split (rgb_img)
    bgr_img = cv2.merge ([b,g,r])
    vw.write (bgr_img)
  vw.release()


# ========== Main GUI Window ==========

class AppForm (QMainWindow):
  def __init__(self, parent=None):

    # ===== Initialization =====
    self.input_video = INPUT_VIDEO
    self.imgseq_in = vid_read_imgseq (self.input_video)
    NF = self.imgseq_in.shape[0]
    NY = self.imgseq_in.shape[1]
    NX = self.imgseq_in.shape[2]
    NC = self.imgseq_in.shape[3]
    print ('Read %s, %d frames [y%d,x%d] color%d in RGB' % (self.input_video, NF, NY, NX, NC))

    # current frame index
    self.fi = 0

    QMainWindow.__init__(self, parent)
    self.setWindowTitle ('PySide OpenCV Video GUI')

    self.create_menu()
    self.create_main_frame()
    self.create_status_bar()

    self.textbox.setText('0')
    self.on_draw()

  def reset_plot (self):
    self.fig_width_in = 8.0
    self.fig_height_in = 6.0
    print ('reset_plot() reset to W%f H%f in)' % (self.fig_width_in, self.fig_height_in))
    self.fig.set_size_inches (self.fig_width_in, self.fig_height_in)
    self.on_draw ()

  def save_plot(self):  
    fileName, filter = QFileDialog.getSaveFileName(self,
                                     self.tr('QFileDialog.getSaveFileName()'),
                                     '',
                                     self.tr('PNG Files (*.png);;All Files (*)'))
    print ('save_plot() %s' % (fileName))                   
    if len (fileName):
      self.canvas.print_figure (fileName, dpi=self.fig_dpi)
      self.statusBar().showMessage('Saved to %s' % fileName, 10000)

  def on_about(self):
    msg = ''' PySide OpenCV matplotlib Video GUI :

     * Load <input.avi>
     * Use the matplotlib navigation bar
     * Drag the slider to jump to a frame
     * Click on frame buttons to navigate the video
     * Status bar showing info
     * Click to receive information
     * Save plot as PNG
    '''
    QMessageBox.about(self, 'PySide OpenCV Matplotlib Video GUI', msg.strip())

  def on_click (self, event):
    if event.xdata:
      print ('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % (
          event.button, event.x, event.y, event.xdata, event.ydata))  
    else:
      print ('button=%d, x=%d, y=%d' % (
          event.button, event.x, event.y))
    

  def on_frame_first (self):
    self.fi = 0
    f_str = '%d' % (self.fi)
    self.textbox.setText (f_str)
    self.slider.setValue (self.fi)
    self.on_draw ()

  def on_frame_last (self):
    NF = self.imgseq_in.shape[0]
    self.fi = NF-1
    f_str = '%d' % (self.fi)
    self.textbox.setText (f_str)
    self.slider.setValue (self.fi)
    self.on_draw ()

  def on_frame_prev (self):
    f = self.fi
    if f-1 >= 0:
      self.fi = f-1

    f_str = '%d' % (self.fi)
    self.textbox.setText (f_str)
    self.slider.setValue (self.fi)
    self.on_draw ()

  def on_frame_next (self):
    f = self.fi
    NF = self.imgseq_in.shape[0]
    if f+1 < NF:
      self.fi = f+1

    f_str = '%d' % (self.fi)
    self.textbox.setText (f_str)
    self.slider.setValue (self.fi)
    self.on_draw ()

  def on_slider_update (self):
    # Update cur frame index self.fi
    f = self.slider.value()
    self.fi = f

    # Update textbox
    f_str = '%d' % (f)
    self.textbox.setText (f_str)
    self.on_draw ()

  def on_textbox_update (self):
    # Update cur frame index self.fi
    str = unicode(self.textbox.text())
    frames = map(int, str.split())
    f = 0
    if not frames:
      print ('Error on_textbox_update() str = %s' % (str))
      return
    else:
      # take the first integer value
      f = frames[0]
    NF = self.imgseq_in.shape[0]
    if f >= 0 and f < NF:
      self.fi = f
    else:
      print ('Error on_textbox_update() fi=%d NF=%d' % (f, NF))
      return

    # Update slider
    self.slider.setValue (self.fi)
    self.on_draw ()

  def on_draw(self):
    # Redraws the figure

    # draw current frame specified in self.fi
    NF = self.imgseq_in.shape[0]
    if self.fi < 0 or self.fi>=NF:
      print ('Error on_draw() fi=%d NF=%d' % (self.fi, NF))
      return

    print ('  frame %d' % (self.fi))
    self.frame_image = self.imgseq_in[self.fi]
    self.axes.imshow (self.frame_image, aspect='equal', interpolation='nearest')

    self.canvas.draw()

  def create_main_frame(self):
    self.main_frame = QWidget()

    # Create the mpl Figure and FigCanvas objects.
    # 5x4 inches, 100 dots-per-inch
    # self.fig = Figure((5, 4), dpi=100)
    self.fig_width_in = 8.0
    self.fig_height_in = 6.0
    self.fig_dpi = 100
    self.fig = Figure((self.fig_width_in, self.fig_height_in), dpi=self.fig_dpi)
    self.canvas = FigureCanvas(self.fig)
    self.canvas.setParent(self.main_frame)

    # Since we have only one plot, we can use add_axes
    # instead of add_subplot, but then the subplot
    # configuration tool in the navigation toolbar wouldn't
    # work.
    #
    self.axes = self.fig.add_subplot(111)

    # Bind the 'pick' event for clicking on one of the bars
    #self.canvas.mpl_connect('pick_event', self.on_pick)
    
    self.canvas.mpl_connect('button_press_event', self.on_click)

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
    NF = self.imgseq_in.shape[0]
    self.slider = QSlider(Qt.Horizontal)
    self.slider.setRange(0, NF-1)
    print ('  slider range [0, %d]' % (NF-1))
    # Start with the first frame
    #self.slider.setValue(0)
    self.slider.setValue (self.fi)
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

  def create_status_bar(self):
    #self.status_label = QLabel('PySide OpenCV Matplotlib Video GUI')
    NF = self.imgseq_in.shape[0]
    NY = self.imgseq_in.shape[1]
    NX = self.imgseq_in.shape[2]
    NC = self.imgseq_in.shape[3]
    self.status_text = '%s [nx=%d, ny=%d] nf=%d nc=%d' % (self.input_video, NX, NY, NF, NC)
    self.status_label = QLabel(self.status_text)
    self.statusBar().addWidget(self.status_label, 1)

  def create_menu(self):
    self.file_menu = self.menuBar().addMenu('&File')

    reset_plot_action = self.create_action ('&Reset plot', shortcut='Ctrl+R', slot=self.reset_plot, tip='Reset the plot')

    save_plot_action = self.create_action ('&Save plot',
        shortcut='Ctrl+S', slot=self.save_plot,
        tip='Save the plot')
    quit_action = self.create_action('&Quit', slot=self.close,
        shortcut='Ctrl+Q', tip='Close the application')

    self.add_actions (self.file_menu,
        (reset_plot_action, save_plot_action, None, quit_action))

    self.help_menu = self.menuBar().addMenu('&Help')
    about_action = self.create_action('&About',
        shortcut='F1', slot=self.on_about,
        tip='About the demo')

    self.add_actions(self.help_menu, (about_action))

  def add_actions(self, target, actions):
    for action in actions:
      if action is None:
        target.addSeparator()
      else:
        target.addAction(action)

  def create_action (self, text, slot=None, shortcut=None,
                     icon=None, tip=None, checkable=False,
                     signal='triggered()'):
    action = QAction(text, self)
    if icon is not None:
      action.setIcon(QIcon(':/%s.png' % icon))
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


def main():
  global INPUT_VIDEO
  if len(INPUT_VIDEO) == 0 :
    if len(sys.argv) == 1:
      print ('Run: <input.avi>')
      sys.exit()

  if len(sys.argv) > 1:
    # Use the command-line input file
    INPUT_VIDEO = str(sys.argv[1])
  else:
    # Use the pre-defined INPUT_VIDEO
    pass
  print ('INPUT_VIDEO = %s' % (INPUT_VIDEO))

  app = QApplication(sys.argv)
  form = AppForm()
  form.show()
  app.exec_()


if __name__ == '__main__':
  main()
