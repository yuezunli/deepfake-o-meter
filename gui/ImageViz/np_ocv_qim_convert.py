
from __future__ import print_function

import sys
import numpy as np

# ===== Import QT Between Versions - Begin =====
import pkgutil
if pkgutil.find_loader ('PyQt4'):
  from PyQt4.QtCore import *
  from PyQt4.QtGui import *
  if 'PySide' in sys.modules:
    del sys.modules['PySide']
  import PyQt4
  QImage_RGB888 = QImage.Format_RGB888
  QImage_RGB32 = QImage.Format_RGB32
elif pkgutil.find_loader ('PyQt5'):
  from PyQt5.QtCore import *
  from PyQt5.QtGui import *
  from PyQt5.QtWidgets import *
  if 'PySide' in sys.modules:
    del sys.modules['PySide']
  import PyQt5
  QImage_RGB888 = QImage.Format_RGB888
  QImage_RGB32 = QImage.Format_RGB32
elif pkgutil.find_loader ('PySide'):
  from PySide.QtCore import *
  from PySide.QtGui import *
  if 'PyQt4' in sys.modules:
    del sys.modules['PyQt4']
  import PySide
  QImage_RGB888 = QImage.Format.Format_RGB888
  QImage_RGB32 = QImage.Format.Format_RGB32
# ===== Import QT Between Versions - End =====

# ========== qimage2ndarray - Begin ==========
# Install:
#   pip install qimage2ndarray
# We assume PySide is used (not PyQt4 or PyQt5). To check , try:
#   import sys
##  import PySide
#   'PySide' in sys.modules
# You should get True  
# The hack of  del sys.modules['PyQt4']  is to force a possible case
# that PyQt4 is already in sys.modules!
# See https://stackoverflow.com/questions/437589/how-do-i-unload-reload-a-python-module
#     if 'PyQt4' in sys.modules:
#       del sys.modules['PyQt4']
# Keep the line of 'import PySide' prior to import qimage2ndarray
# So you don't need to set OS ENV:    SET QT_DRIVER=PySide
# before importing qimage2ndarray
#       import PySide
import qimage2ndarray  
# ========== qimage2ndarray - End ==========

def QImageToCVBGRA (qIm):
  MatBGRA = qimage2ndarray.byte_view (qIm)  
  return MatBGRA
'''
# Converts a QImage into OpenCV BGRA format
# https://stackoverflow.com/questions/19902183/qimage-to-numpy-array-using-pyside
# This PySide working version
def QImageToCVBGRA (qIm):
  qIm = qIm.convertToFormat (QImage_RGB32)
  width = qIm.width()
  height = qIm.height()
  ptr = qIm.constBits()
  MatBGRA = np.array(ptr).reshape (height, width, 4)
  return MatBGRA
'''

def QImageToNpRGB888 (qIm):
  MatRGB = qimage2ndarray.rgb_view (qIm)  
  return MatRGB
  
'''
# Converts a QImage into Numpy RGB888 format
# This PySide working version
def QImageToNpRGB888 (qIm):
  qIm = qIm.convertToFormat (QImage_RGB32)
  width = qIm.width()
  height = qIm.height()
  ptr = qIm.constBits()
  MatBGRA = np.array(ptr).reshape (height, width, 4)
  # We want to convert OpenCV BGRA array into numpy RGB array
  # see https://stackoverflow.com/questions/41500637/how-to-extract-r-g-b-values-with-numpy-into-seperate-arrays
  # https://stackoverflow.com/questions/10443295/combine-3-separate-numpy-arrays-to-an-rgb-image-in-python
  [b, g, r, a] = np.dsplit(MatBGRA, MatBGRA.shape[-1])
  RGB = np.dstack((r,g,b))
  return RGB
'''  
  
# Ming 2019/0209
# I found that this function has memory leak issue
#   where the created QImage object will never be free
# This is a bug in PySide, which occurs in Python 3.x but not 2.x !!
# see https://gist.github.com/bsdnoobz/8464000
# see https://bugreports.qt.io/browse/PYSIDE-140?page=com.atlassian.jira.plugin.system.issuetabpanels%3Acomment-tabpanel&showAll=true
# My workaround solution is to use a package called 'qimage2ndarray'
# But that needs additional tweaks!!
# You need to set OS ENV    SET QT_DRIVER=PySide 
# such that qimage2ndarray is compatible with PySide (default is PyQt4)
  
# http://pythonhosted.org/python-qwt/_modules/qwt/toqimage.html#array_to_qimage
# https://gist.githubusercontent.com/smex/5287589/raw/toQImage.py
'''
  Convert NumPy array to QImage object
  
  :param numpy.array arr: NumPy array
  :param bool copy: if True, make a copy of the array
  :return: QImage object
'''
'''
def NpArrayToQImage_mem_leak (arr, copy=False):  
  if arr is None:
    return QImage()
  if len(arr.shape) not in (2, 3):
    raise NotImplementedError('Unsupported array shape %r' % arr.shape)
  data = arr.data
  ny, nx = arr.shape[:2]
  stride = arr.strides[0]  # bytes per line
  color_dim = None
  if len(arr.shape) == 3:
    color_dim = arr.shape[2]
  if arr.dtype == np.uint8:
    if color_dim is None:
      qimage = QImage (data, nx, ny, stride, QImage.Format_Indexed8)
      qimage.setColorTable ([qRgb(i, i, i) for i in range(256)])
      qimage.setColorCount (256)
    elif color_dim == 3:
      qimage = QImage (data, nx, ny, stride, QImage.Format_RGB888)
    elif color_dim == 4:
      qimage = QImage (data, nx, ny, stride, QImage.Format_ARGB32)
    else:
      raise TypeError('Invalid third axis dimension (%r)' % color_dim)
  elif arr.dtype == np.uint32:
    qimage = QImage (data, nx, ny, stride, QImage.Format_ARGB32)
  else:
    raise NotImplementedError('Unsupported array data type %r' % arr.dtype)
  if copy:
    #return qimage.copy()
    return qimage
  return qimage
'''
    
# Note in order for qimage2ndarray to work,
# you need to set OS ENV:    SET QT_DRIVER=PySide 
# such that qimage2ndarray is compatible with PySide (default is PyQt4)
# Suggested: put this in C:\CondaEnv.bat

# I also tried modified C:\Anaconda3\envs\py36\Lib\site-packages\qimage2ndarray\qt_driver.py 
# to change default to PySide
#   DEFAULT = 'PyQt5'
#   DEFAULT = 'PySide'
# however it does not work alone (i.e. still need the above   SET QT_DRIVER=PySide

def NpArrayToQImage (arr): 
 qIm = qimage2ndarray.array2qimage (arr)  
 # qImg is type: QtGui.QImage.Format.Format_ARGB32
 # Next convert to RGB888 
 qIm888 = qIm.convertToFormat (QImage_RGB888)
 return qIm888
 
# To debug memory leak, see https://benbernardblog.com/tracking-down-a-freaky-python-memory-leak/#monitoringmemoryusingperformancemonitor

 
# import numpy as np

# # ===== Import QT Between Versions - Begin =====
# import pkgutil
# if pkgutil.find_loader ('PyQt4'):
#   from PyQt4.QtCore import *
#   from PyQt4.QtGui import *
# elif pkgutil.find_loader ('PyQt5'):
#   from PyQt5.QtCore import *
#   from PyQt5.QtGui import *
#   from PyQt5.QtWidgets import *
# elif pkgutil.find_loader ('PySide'):
#   from PySide.QtCore import *
#   from PySide.QtGui import *
# # ===== Import QT Between Versions - End =====

# # https://stackoverflow.com/questions/19902183/qimage-to-numpy-array-using-pyside
# # Converts a QImage into OpenCV BGRA format
# def QImageToCVBGRA (qIm):
#   qIm = qIm.convertToFormat (QImage.Format_RGB32)
#   width = qIm.width()
#   height = qIm.height()
#   ptr = qIm.constBits()
#   MatBGRA = np.array(ptr).reshape (height, width, 4)
#   return MatBGRA

# # Converts a QImage into Numpy RGB888 format
# def QImageToNpRGB888 (qIm):
#   qIm = qIm.convertToFormat (QImage.Format_RGB32)
#   width = qIm.width()
#   height = qIm.height()
#   ptr = qIm.constBits()
#   MatBGRA = np.array(ptr).reshape (height, width, 4)
#   #b,g,r,a = cv2.split (Mat)       # get b,g,r
#   #I = cv2.merge ([r,g,b])
#   # We want to convert OpenCV BGRA array into numpy RGB array
#   # see https://stackoverflow.com/questions/41500637/how-to-extract-r-g-b-values-with-numpy-into-seperate-arrays
#   # https://stackoverflow.com/questions/10443295/combine-3-separate-numpy-arrays-to-an-rgb-image-in-python
#   [b, g, r, a] = np.dsplit(MatBGRA, MatBGRA.shape[-1])
#   RGB = np.dstack((r,g,b))
#   return RGB
  
# # http://pythonhosted.org/python-qwt/_modules/qwt/toqimage.html#array_to_qimage
# # https://gist.githubusercontent.com/smex/5287589/raw/toQImage.py
# """
#   Convert NumPy array to QImage object
  
#   :param numpy.array arr: NumPy array
#   :param bool copy: if True, make a copy of the array
#   :return: QImage object
#  """
# def NpArrayToQImage (arr, copy=False):  
#   if arr is None:
#     return QImage()
#   if len(arr.shape) not in (2, 3):
#     raise NotImplementedError("Unsupported array shape %r" % arr.shape)
#   data = arr.data
#   ny, nx = arr.shape[:2]
#   stride = arr.strides[0]  # bytes per line
#   color_dim = None
#   if len(arr.shape) == 3:
#     color_dim = arr.shape[2]
#   if arr.dtype == np.uint8:
#     if color_dim is None:
#       qimage = QImage(data, nx, ny, stride, QImage.Format_Indexed8)
#       #qimage.setColorTable([qRgb(i, i, i) for i in range(256)])
#       qimage.setColorCount(256)
#     elif color_dim == 3:
#       qimage = QImage(data, nx, ny, stride, QImage.Format_RGB888)
#     elif color_dim == 4:
#       qimage = QImage(data, nx, ny, stride, QImage.Format_ARGB32)
#     else:
#       raise TypeError("Invalid third axis dimension (%r)" % color_dim)
#   elif arr.dtype == np.uint32:
#     qimage = QImage(data, nx, ny, stride, QImage.Format_ARGB32)
#   else:
#     raise NotImplementedError("Unsupported array data type %r" % arr.dtype)
#   if copy:
#     return qimage.copy()
#   return qimage
