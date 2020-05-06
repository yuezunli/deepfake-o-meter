# Python PySide OpenCV Video GUI App
# Author:  Ming-Ching Chang
# Version / Development Log:
#   2018/01/28  Initial Version

# The only dependency is PySide, numpy, OpenCV.
# No matplotlib

import numpy as np

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
import ImageViz.viz_widget as viz_widget
import ImageViz.np_ocv_qim_convert as np_ocv_qim_convert

import VideoViz.VideoViz_var as VideoViz_var
import VideoViz.ocv_vid as ocv_vid
import VideoViz.VideoVizWnd as VideoVizWnd

# ========== Main GUI Window ==========

class VideoSandboxWnd (VideoVizWnd.VideoVizWnd):
  def __init__ (self, parent=None):
    super (VideoSandboxWnd, self).__init__ ()
    self.APP_NAME = 'VideoSandbox'
    self.setWindowTitle ('%s - %s' % (self.APP_NAME, self.VIDEO_FILE))
    if var.VERBOSE>3:
      print ('end of VideoSandboxWnd.__init__()')

  def createActions (self):
    super (VideoSandboxWnd, self).createActions ()
    self.createSandboxProcActions ()
    
  def createSandboxProcActions (self):
    self.experimentAct = QAction ('&Experiment',
        self, checkable=True, triggered=self.on_experiment)
      
  def setupImgProcMenu (self):
    super (VideoSandboxWnd, self).setupImgProcMenu () 
    self.imgProcMenu.addSeparator ()   
    self.imgProcMenu.addAction (self.experimentAct)
        
  def proc_frame_run_process (self):
    super (VideoSandboxWnd, self).proc_frame_run_process ()     
    if self.activatedProcessAct == self.experimentAct:
      self.experiment_proc ()
  
  def on_experiment (self):  
    if self.activatedProcessAct == self.experimentAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
      self.visualizeImg (self.qImg)    
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.experimentAct
    self.activatedProcessAct.setChecked (True)
      
    # Run process on current frame
    self.proc_frame ()
    
    
  def experiment_proc (self):
    # process input image self.I as numpy array, output in self.IOut

    # In this example, we simply create a upside-down image.
    
    # For the issue of using np.fliplr F_CONTINUOUS problem
    # we need to make a copy to create a continuous array, see https://stackoverflow.com/questions/20175187/numpy-flipped-image-cv2-filter2d-assertion-failed
    self.IOut = np.flipud (self.I).copy() 
    
    drawcmd = ['line', [110, 202, 300, 340]]
    var.DRAWCMD_LIST.append (drawcmd)
    
# ========== App Main ==========

if __name__ == '__main__':
  import sys  
  var.INPUT_VIDEO = '../car.avi'

  if len(var.INPUT_VIDEO) == 0 :
    if len(sys.argv) == 1:
      print ('Run: <input.avi>')
  if len(sys.argv) > 1:
    # Use the command-line input file
    var.INPUT_VIDEO = str(sys.argv[1])
  print ('INPUT_VIDEO = %s' % (var.INPUT_VIDEO))

  app = QApplication (sys.argv)
  app.setWindowIcon (QIcon('../VideoViz.png'))  
  wnd = VideoSandboxWnd ()
  wnd.show ()
  sys.exit (app.exec_())
