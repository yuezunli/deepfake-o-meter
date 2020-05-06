# This example shows how to use PySide/PyQt to display and process an image
#   - using numpy array as image representation
#   - using QLabel containing a QPixmap, which stores the input QImage
#   - zoomin/zoomout scaling scrollbars
#   - basic shape drawing using QPainter
#   - sub-pixel drawing and zooming

# The only dependency should be PySide and numpy.
import numpy as np
import cv2 # to run opencv convolution

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
import ImageViz.np_ocv_qim_convert as np_ocv_qim_convert
import ImageViz.QImageVizWnd as QImageVizWnd

class ImageVizNpWnd (QImageVizWnd.QImageVizWnd):
  def __init__ (self, parent=None):
    super (ImageVizNpWnd, self).__init__ ()
    self.setMouseTracking (True)
    self.mouseX = None
    self.mouseY = None
    self.setWindowTitle ('ImageVizNp')

  def createImgProcActions (self):
    super (ImageVizNpWnd, self).createImgProcActions ()
    
    self.toGrayImgAct = QAction ('To &Grayscale (Luminance)',
        self, checkable=True, triggered=self.on_to_gray_img)
    
    # create new actions to be added to the Process menu
    self.convolveImgAct = QAction ('&Convolve Image',
        self, checkable=True, triggered=self.on_img_conv)

    self.sobelGradientAct = QAction ('&Sobel Gradient',
        self, checkable=True, triggered=self.on_sobel_gradient)

    self.morphDilationAct = QAction ('Morphology Dilation',
        self, checkable=True, triggered=self.on_morph_dilation)
        
    self.morphErosionAct = QAction ('Morphology Erosion',
        self, checkable=True, triggered=self.on_morph_erosion)
        
    self.morphOpeningAct = QAction ('Morphology Opening',
        self, checkable=True, triggered=self.on_morph_opening)
        
    self.morphClosingAct = QAction ('Morphology Closing',
        self, checkable=True, triggered=self.on_morph_closing)

  def setupImgProcMenu (self):
    super (ImageVizNpWnd, self).setupImgProcMenu ()
    # add new actions to the Process menu
    self.imgProcMenu.addSeparator ()
    self.imgProcMenu.addAction (self.toGrayImgAct)
    self.imgProcMenu.addSeparator ()
    self.imgProcMenu.addAction (self.convolveImgAct)
    self.imgProcMenu.addAction (self.sobelGradientAct)
    self.imgProcMenu.addSeparator ()
    self.imgProcMenu.addAction (self.morphDilationAct)
    self.imgProcMenu.addAction (self.morphErosionAct)
    self.imgProcMenu.addAction (self.morphOpeningAct)
    self.imgProcMenu.addAction (self.morphClosingAct)

  def initImageViz (self, W=None, H=None):
    super (ImageVizNpWnd, self).initImageViz (W, H)
    self.I = np_ocv_qim_convert.QImageToNpRGB888 (self.qImg)
    self.IOut = self.I

  def load_im_show (self, ImgFile = None):
    super (ImageVizNpWnd, self).load_im_show (ImgFile)
    self.I = np_ocv_qim_convert.QImageToNpRGB888 (self.qImg)
    self.IOut = self.I

  def on_paste_as_a_new_image (self): 
    super (ImageVizNpWnd, self).on_paste_as_a_new_image ()
    self.I = np_ocv_qim_convert.QImageToNpRGB888 (self.qImg)
    self.IOut = self.I
    
  def on_negative_img (self):
    if self.activatedProcessAct == self.negativeImgAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.negativeImgAct
    self.activatedProcessAct.setChecked (True)

    x=2
    y=0
    p = self.qImg.pixel(x,y)
    if var.VERBOSE>1:
      print ('on_negative_img:  qImg (%d,%d) R %d G %d B %d' % (x, y, qRed(p), qGreen(p), qBlue(p)))

    # process input image self.I, output in self.IOut
    self.negative_img_proc ()

    #self.I[1,0,1] = 128
    #self.I.fill (64)

    if var.VERBOSE>1:
      print ('negative_img_proc:  IOut (%d,%d) R %d G %d B %d' % (x, y, self.IOut[y,x,0], self.IOut[y,x,1], self.IOut[y,x,2]))

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)

  def negative_img_proc (self):
    # process input image self.I as numpy array, output in self.IOut
    self.IOut = 255 - self.I


  def on_mirror_img (self):
    if self.activatedProcessAct == self.mirrorImgAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.mirrorImgAct
    self.activatedProcessAct.setChecked (True)

    # process input image self.I, output in self.IOut
    self.mirror_img_proc ()

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)

  def mirror_img_proc (self):
    # process input image self.I as numpy array, output in self.IOut

    # For the issue of using np.fliplr F_CONTINUOUS problem
    # we need to make a copy to create a continuous array, see https://stackoverflow.com/questions/20175187/numpy-flipped-image-cv2-filter2d-assertion-failed
    #self.I = np.fliplr (self.I)
    self.IOut = np.fliplr (self.I).copy()
    
  def on_to_gray_img (self):
    if self.activatedProcessAct == self.toGrayImgAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.toGrayImgAct
    self.activatedProcessAct.setChecked (True)

    # process input image self.I, output in self.IOut
    self.to_gray_img_proc ()

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)
      
  def to_gray_img_proc (self):
    RGB = self.I 
    Y = 0.2989 * RGB[:,:,0] + 0.5870 * RGB[:,:,1] + 0.1140 * RGB[:,:,2]
    Y = Y.astype ('uint8')
    self.IOut[:,:,0] = Y
    self.IOut[:,:,1] = Y
    self.IOut[:,:,2] = Y
    
  def img_intensity_transform (self):
    pass


  def on_img_conv (self):
    if self.activatedProcessAct == self.convolveImgAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.convolveImgAct
    self.activatedProcessAct.setChecked (True)

    # process input image self.I, output in self.IOut
    self.conv_img_proc ()

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)

  def conv_img_proc (self):
    # process input image self.I as numpy array, output in self.IOut
    # See https://github.com/sunsided/python-conv2d
    K1 = np.array([[1, 0, -1],
                   [2, 0, -2],
                   [1, 0, -1]])
    K2 = np.array([[0, 1, 0],
                   [1, -4, 1],
                   [0, 1, 0]])
    self.IOut = cv2.filter2D (src=self.I, kernel=K1, ddepth=-1)


  def on_sobel_gradient (self):
    if self.activatedProcessAct == self.sobelGradientAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.sobelGradientAct
    self.activatedProcessAct.setChecked (True)

    # process input image self.I, output in self.IOut
    self.sobel_gradient_proc ()

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)

  def sobel_gradient_proc (self):
    # process input image self.I as numpy array, output in self.IOut
    # see https://stackoverflow.com/questions/41971663/use-numpy-to-convert-rgb-pixel-array-into-grayscale
    #from skimage import color
    #Gray = color.rgb2gray (self.I)
    Gray = np.dot(self.I[...,:3], [.299, .587, .114])

    #See https://stackoverflow.com/questions/5710842/fastest-2d-convolution-or-image-filter-in-python
    #Slower
    #  import scipy.ndimage as ndi
    #  sigma = 1.4
    #  Gfloat = np.array (Gray, dtype = float)
    #  Gfiltered = ndi.filters.gaussian_filter (Gfloat, sigma)

    gaussian = np.array([[1, 2, 1],
                         [2, 4, 2],
                         [1, 2, 1]])
    Gfiltered = cv2.filter2D (src=Gray, kernel=gaussian, ddepth=-1)

    #Gimg = G / G.max()
    #from skimage import io
    #io.imsave('canny_edge_steps_out1_smoothed.png', Gimg)

    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1],
                        [0, 0, 0],
                        [1, 2, 1]])

    gradx = cv2.filter2D (src=Gfiltered, kernel=sobel_x, ddepth=-1)
    grady = cv2.filter2D (src=Gfiltered, kernel=sobel_y, ddepth=-1)

    gradMag = np.hypot (gradx, grady)
    S = gradMag / gradMag.max()
    #io.imsave('canny_edge_steps_out2_edgemag.png', S)
    S = S * 255
    P = S.astype (np.uint8)
    self.IOut = cv2.merge ([P,P,P])

    #sobeloutdir = np.arctan2(grady, gradx)

  def on_morph_dilation (self):
    if self.activatedProcessAct == self.morphDilationAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.morphDilationAct
    self.activatedProcessAct.setChecked (True)
      
    # process input image self.I, output in self.IOut
    self.morph_dilation_proc ()

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)
    
  def morph_dilation_proc (self):
      
    if 1:  
      a = 0
      b = 255
      SE = np.array([[a, b, a],
                     [b, b, b],
                     [a, b, a]], dtype=np.uint8)
    elif 0:   
      c = 192  
      b = 128 
      a = 64
      SE = np.array([[a, b, c, b, a],
                     [b, c, c, c, b],
                     [c, c, c, c, c],
                     [b, c, c, c, b],
                     [a, b, c, b, a]], dtype=np.uint8)          
                   
    src = np.uint8 (self.I)               
    self.IOut = cv2.dilate (src, SE, iterations=1)
    
  def on_morph_erosion (self):
    if self.activatedProcessAct == self.morphErosionAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.morphErosionAct
    self.activatedProcessAct.setChecked (True)
      
    # process input image self.I, output in self.IOut
    self.morph_erosion_proc ()

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)
    
  def morph_erosion_proc (self):
      
    if 1:  
      a = 0
      b = 255
      SE = np.array([[a, b, a],
                     [b, b, b],
                     [a, b, a]], dtype=np.uint8)
    elif 0:   
      a = 64
      b = 128 
      c = 192  
      SE = np.array([[a, b, c, b, a],
                     [b, c, c, c, b],
                     [c, c, c, c, c],
                     [b, c, c, c, b],
                     [a, b, c, b, a]], dtype=np.uint8)          
                   
    src = np.uint8 (self.I)               
    self.IOut = cv2.erode (src, SE, iterations=1)
    
  def on_morph_opening (self):
    if self.activatedProcessAct == self.morphOpeningAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.morphOpeningAct
    self.activatedProcessAct.setChecked (True)
      
    # process input image self.I, output in self.IOut
    self.morph_opening_proc ()

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)
    
  def morph_opening_proc (self):
      
    if 1:  
      a = 0
      b = 255
      SE = np.array([[a, b, a],
                     [b, b, b],
                     [a, b, a]], dtype=np.uint8)
    elif 0:   
      c = 192  
      b = 128 
      a = 64
      SE = np.array([[a, b, c, b, a],
                     [b, c, c, c, b],
                     [c, c, c, c, c],
                     [b, c, c, c, b],
                     [a, b, c, b, a]], dtype=np.uint8)          
                   
    src = np.uint8 (self.I)               
    self.IOut = cv2.morphologyEx (src, cv2.MORPH_OPEN, SE)
    
  def on_morph_closing (self):
    if self.activatedProcessAct == self.morphClosingAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.morphClosingAct
    self.activatedProcessAct.setChecked (True)
      
    # process input image self.I, output in self.IOut
    self.morph_closing_proc ()

    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg (self.qImgOut)
    
  def morph_closing_proc (self):
      
    if 0:  
      b = 192
      a = 128
      SE = np.array([[a, b, a],
                     [b, b, b],
                     [a, b, a]], dtype=np.uint8)
    elif 1:   
      c = 192  
      b = 128 
      a = 64
      SE = np.array([[a, b, c, b, a],
                     [b, c, c, c, b],
                     [c, c, c, c, c],
                     [b, c, c, c, b],
                     [a, b, c, b, a]], dtype=np.uint8)          
                   
    self.IOut = cv2.morphologyEx (self.I, cv2.MORPH_CLOSE, SE)
                   
    
  ###############################################


  # https://stackoverflow.com/questions/19825650/python-pyqt4-how-to-detect-the-mouse-click-position-anywhere-in-the-window
  def mousePressEvent (self, event):
    pos = event.pos()
    str = None
    if event.buttons() == Qt.LeftButton:
      str = 'L-Click (%d, %d)' % (pos.x(), pos.y())
    elif event.buttons() == Qt.RightButton:
      str = 'R-Click (%d, %d)' % (pos.x(), pos.y())
    self.updateStatusBar (str)

  def getMousePixel (self, event):
    # https://stackoverflow.com/questions/7829829/pyqt4-mousemove-event-without-mousepress
    # pos is the mouse position in the main window coordinate
    pos = event.pos()
    # posv is the mouse position in the vizWidget coordinate
    posv = self.vizWidget.mapFrom (self, pos)
    # (x,y) is the mouse position in the numpy image coordinate
    s = var.VIZ_SCALE
    z = var.VIZ_ZOOMIN
    if z==1:
      x = int(posv.x()/s)
      y = int(posv.y()/s)
      xf = float(posv.x())/s
      yf = float(posv.y())/s
    else:
      x = posv.x()/z
      y = posv.y()/z
      xf = (float(posv.x()) - z/2)/z
      yf = (float(posv.y()) - z/2)/z
    return x, y, xf, yf  
    

  def calMousePixelStr (self, event):
    x, y, xf, yf = self.getMousePixel (event)
    self.mouseX = xf
    self.mouseY = yf

    str = self.getMousePixelStr (x, y, xf, yf)

    if event.buttons() == Qt.LeftButton:
      str = 'L-Drag' + str
    elif event.buttons() == Qt.RightButton:
      str = 'R-Drag' + str
    return str
    
  def getMousePixelStr (self, x, y, xf, yf):  
    str = '(x %.2f, y %.2f)' % (xf, yf)
    if x>=0 and y>=0:
      I = None
      if self.activatedProcessAct is None:
        if self.I is not None:
          I = self.I
      else:
        if self.IOut is not None:
          I = self.IOut
      if I is not None and I.ndim > 1:
        NY = I.shape[0]
        NX = I.shape[1]
        if x<NX and y<NY:
          if I.ndim > 2:
            r = I[y,x,0]
            g = I[y,x,1]
            b = I[y,x,2]
            str = '(x %.2f, y %.2f) I(x %d, y %d) [R %d, G %d, B %d]' % (xf, yf, x, y, r, g, b)
          else:
            p = I[y,x]
            str = '(x %.2f, y %.2f) I(x %d, y %d) [P %d]' % (xf, yf, x, y, p)
    return str        

  def mouseMoveEvent (self, event):
    str = self.calMousePixelStr (event)
    self.updateStatusBar (str)

if __name__ == '__main__':
  import sys
  app = QApplication (sys.argv)
  # Set application Icon
  # See https://stackoverflow.com/questions/35272349/window-icon-does-not-show
  app.setWindowIcon (QIcon('ImageViz.png'))

  wnd = ImageVizNpWnd ()
  wnd.show ()
  sys.exit (app.exec_())
