# Python PySide OpenCV Video GUI App
# Author:  Ming-Ching Chang
# Version / Development Log:
#   2018/01/28  Initial Version

# The only dependency is PySide, numpy, OpenCV.
# No matplotlib

import numpy as np

import cv2
from PySide.QtCore import *
from PySide.QtGui import *

# This enables to import PyCVApp/*.py
import sys; sys.path.insert(0, '..')

import var
import ImageViz.viz_widget as viz_widget
import ImageViz.np_ocv_qim_convert as np_ocv_qim_convert
import VideoViz.ocv_vid as ocv_vid
import VideoViz.VideoViz2ViewWnd as VideoViz2ViewWnd

# ========== Main GUI Window ==========

class Video2ViewSandboxWnd (VideoViz2ViewWnd.VideoViz2ViewWnd):
  def __init__ (self, parent=None):
    super (Video2ViewSandboxWnd, self).__init__ ()
    self.APP_NAME = 'Video2ViewSandbox'
    self.setWindowTitle ('%s - %s' % (self.APP_NAME, self.VIDEO_FILE))
    if var.VERBOSE>3:
      print ('end of Video2ViewSandboxWnd.__init__()')

  def createActions (self):
    super (Video2ViewSandboxWnd, self).createActions ()
    self.createSandboxProcActions ()
    
  def setupImgProcMenu (self):
    super (Video2ViewSandboxWnd, self).setupImgProcMenu () 
    self.imgProcMenu.addSeparator ()   
    self.imgProcMenu.addAction (self.experimentAct)
        
  def createSandboxProcActions (self):
    self.experimentAct = QAction ('&Experiment',
        self, checkable=True, triggered=self.on_experiment)
      
  def proc_frame_run_process (self):
    super (Video2ViewSandboxWnd, self).proc_frame_run_process ()     
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
    
# ========== App Main ==========

if __name__ == '__main__':
  import sys
  var.INPUT_VIDEO = '../car.avi'

  if len(var.INPUT_VIDEO) == 0:
    if len(sys.argv) == 1:
      print ('Run: <input.avi>')
      #sys.exit()

  if len(sys.argv) > 1:
    # Use the command-line input file
    var.INPUT_VIDEO = str(sys.argv[1])
  print ('main(): INPUT_VIDEO = %s' % (var.INPUT_VIDEO))

  app = QApplication (sys.argv)
  app.setWindowIcon (QIcon('../VideoViz.png'))

  wnd = Video2ViewSandboxWnd ()
  wnd.show ()
  sys.exit (app.exec_())
