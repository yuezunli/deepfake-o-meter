# This example shows how to use PySide/PyQt to display and process an image
#   - using numpy array as image representation
#   - using QLabel containing a QPixmap, which stores the input QImage
#   - zoomin/zoomout scaling scrollbars
#   - basic shape drawing using QPainter
#   - sub-pixel drawing and zooming

# The only dependency is PySide and numpy.

import numpy as np

from PySide.QtCore import *
from PySide.QtGui import *

# This enables to import PyCVApp/*.py
import sys; sys.path.insert(0, '..')

import var
import ImageViz.viz_widget as viz_widget
import ImageViz.np_ocv_qim_convert as np_ocv_qim_convert
import ImageViz.ImageVizNpWnd as ImageVizNpWnd

class ImageSandboxWnd (ImageVizNpWnd.ImageVizNpWnd):
  def __init__ (self, parent=None):
    super (ImageSandboxWnd, self).__init__ ()
    self.setWindowTitle ('ImageSandbox')
    if var.VERBOSE>3:
      print ('end of ImageSandboxWnd.__init__()')
    
  def createFileActions (self):
    # disable the on_file_new_examples
    super (ImageSandboxWnd, self).createFileActions ()
    self.fileNewExample1Act.setEnabled (False)
    self.fileNewExample2Act.setEnabled (False)
    self.fileNewExample3Act.setEnabled (False)
    
  def createActions (self):
    super (ImageSandboxWnd, self).createActions ()
    self.createSandboxProcActions ()
    
  def createSandboxProcActions (self):
    self.experimentAct = QAction ('&Experiment',
        self, checkable=True, triggered=self.on_experiment)
    
  def setupImgProcMenu (self):
    super (ImageSandboxWnd, self).setupImgProcMenu () 
    self.imgProcMenu.addSeparator ()   
    self.imgProcMenu.addAction (self.experimentAct)
    
  def on_experiment (self):
    if self.activatedProcessAct == self.experimentAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.experimentAct
    self.activatedProcessAct.setChecked (True)

    # process input image self.I, output in self.IOut
    self.experiment_proc ()

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)

  def experiment_proc (self):
    # process input image self.I as numpy array, output in self.IOut
    self.IOut = np.flipud (self.I).copy() 
    
    # calculate mean RGB
    # https://stackoverflow.com/questions/40700501/how-to-calculate-mean-color-of-image-in-numpy-array
    m = np.mean (self.I, axis=(0,1))
    std = np.std (self.I, axis=(0,1))
    print ('mean of image:'+str(m))
    print ('std of image:'+str(std))

if __name__ == '__main__':
  import sys
  app = QApplication(sys.argv)
  wnd = ImageSandboxWnd()
  wnd.show()
  sys.exit(app.exec_())
