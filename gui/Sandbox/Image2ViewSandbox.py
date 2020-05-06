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
import ImageViz.ImageVizNp2ViewWnd as ImageVizNp2ViewWnd

class Image2ViewSandboxWnd (ImageVizNp2ViewWnd.ImageVizNp2ViewWnd):
  def __init__ (self, parent=None):
    super (Image2ViewSandboxWnd, self).__init__ ()
    self.setWindowTitle ('Image2ViewSandbox')
    if var.VERBOSE>3:
      print ('end of Image2ViewSandboxWnd.__init__()')
    
  def createFileActions (self):
    # disable the on_file_new_examples
    super (Image2ViewSandboxWnd, self).createFileActions ()
    self.fileNewExample1Act.setEnabled (False)
    self.fileNewExample2Act.setEnabled (False)
    self.fileNewExample3Act.setEnabled (False)
    
  def createActions (self):
    super (Image2ViewSandboxWnd, self).createActions ()
    self.createSandboxProcActions ()
    
  def setupImgProcMenu (self):
    super (Image2ViewSandboxWnd, self).setupImgProcMenu () 
    self.imgProcMenu.addSeparator ()   
    self.imgProcMenu.addAction (self.experimentAct)
    
  def createSandboxProcActions (self):
    self.experimentAct = QAction ('&Experiment',
        self, checkable=True, triggered=self.on_experiment)
    
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
    self.visualizeImg2 (self.qImgOut)

  def experiment_proc (self):
    # process input image self.I as numpy array, output in self.IOut
    self.IOut = np.flipud (self.I).copy() 

if __name__ == '__main__':
  import sys
  app = QApplication(sys.argv)
  wnd = Image2ViewSandboxWnd()
  wnd.show()
  sys.exit(app.exec_())
