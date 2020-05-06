# This example shows how to use PySide/PyQt to display an image
#   - using QLabel containing a QPixmap, which stores the input QImage
#   - zoomin/zoomout scaling scrollbars
#   - basic shape drawing using QPainter
#   - sub-pixel drawing and zooming
# Minimum dependency is PySide.

'''
http://programmingexamples.wikidot.com/qt-basic-drawing

Difference between QPixmap, QImage and QPicture
Qt provides four classes for handling image data: QImage, QPixmap and QPicture.
QImage provides a hardware-independent image representation. It is is designed and optimized for I/O, and for direct pixel access and manipulation
QPixmap is designed and optimized for showing images on screen.
QPicture class is a paint device that records and replays QPainter commands.
'''

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

# This enables to import PyCVApp/*.py
import sys; sys.path.insert(0, '..')

import var
import ImageViz.ImageViz_var as ImageViz_var
import ImageViz.viz_widget as viz_widget
import ImageViz.np_ocv_qim_convert as np_ocv_qim_convert

class QImageVizWnd (QMainWindow):
  def __init__(self):
    super (QImageVizWnd, self).__init__()

    self.createActions ()
    self.createMenus ()
    self.createMainFrame ()
 
    self.setMouseTracking (True)
    
    self.activatedProcessAct = None

    # subpixel VIZ_ZOOMIN = scale each pixel by 1,2,3,4,5,6,7,8,16,32,64
    self.VIZ_ZOOMIN_LIST = [1,2,3,4,5,6,8,16,32,64,128,256,512]
    # non-subpixel zoom in / out: VIZ_SCALE = 1, 7/8, 3/4, 2/3, 1/2, 1/3, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128
    self.VIZ_SCALE_LIST = [1.0, 7.0/8, 3.0/4, 2.0/3, 5.0/8, 1.0/2, 1.0/3, 1.0/4, 1.0/8, 1.0/16, 1.0/32, 1.0/64, 1.0/128, 1.0/256, 1.0/512]

    self.zoom_idx = 0
    self.scale_idx = 0
    
    # https://doc.qt.io/qt-5.10/qimage.html#reading-and-writing-image-files
    self.readImageFilter = 'Images (*.png *.jpg *.jpeg *.bmp *.gif *.pbm *.pgm *.ppm *.xbm *.xpm);;Portable Network Graphics (*.png);;Joint Photographic Experts Group (*.jpg *.jpeg);;Windows Bitmap (*.bmp);;Graphic Interchange Format (*.gif);;Portble Bitmap (*.pbm);;Portable Graymap (*.pgm);;Portable Pixmap (*.ppm);;X11 Bitmap (*.xbm);;X11 Pixmap (*.xpm);;All Files (*.*)'
    self.saveImageFilter = 'Images (*.png *.jpg *.jpeg *.bmp *.tiff *.ppm *.xbm *.xpm);;Portable Network Graphics (*.png);;Joint Photographic Experts Group (*.jpg *.jpeg);;Windows Bitmap (*.bmp);;Tagged Image File Format (*.tiff);;Portable Pixmap (*.ppm);;X11 Bitmap (*.xbm);;X11 Pixmap (*.xpm);;All Files (*.*)'
    
    # Enable dragging and dropping onto this Widget
    self.setAcceptDrops (True)
    
    #self.APP_WND_W = 400
    #self.APP_WND_H = 300
    #self.resize (self.APP_WND_W, self.APP_WND_H)

    # display screen resolution
    screenRes = QDesktopWidget().screenGeometry()
    var.SCREEN_RES_W = screenRes.width()
    var.SCREEN_RES_H = screenRes.height()
    if var.VERBOSE>1:
      print ('screen res %dx%d' % (screenRes.width(), screenRes.height()))
  
    self.setWindowTitle ('QImageViz')
    self.initImageVizAndView()

  def createActions (self):
    self.createFileActions ()
    self.createEditActions ()
    self.createViewActions ()
    self.createImgProcActions ()
    self.createHelpActions ()

  def createFileActions (self):
    self.fileNewAct = QAction ('&New',
        self, triggered=self.on_file_new)
    self.fileNewExample1Act = QAction ('New Example &1 (Tiny Image)',
        self, triggered=self.on_file_new_example1)
    self.fileNewExample2Act = QAction ('New Example &2 (Monkey)',
        self, triggered=self.on_file_new_example2)
    self.fileNewExample3Act = QAction ('New Example &3 (Lena)',
        self, triggered=self.on_file_new_example3)

    self.fileOpenImageAct = QAction ('Open &Image...',
        self, shortcut='Ctrl+I', triggered=self.on_file_open_image)
        
    self.fileSaveImageSrcAct = QAction('Save Image Source...',
        self, triggered=self.on_save_image_src)
    self.fileSaveImageOutAct = QAction('Save Image Output...',
        self, triggered=self.on_save_image_out)
        
    self.exitAct = QAction ('E&xit',
        self, shortcut='Ctrl+X',
        triggered=self.close)
    
  def createEditActions (self):
    self.copyImageAct = QAction ('&Copy Image (Original Scale)',
        self, triggered=self.on_copy_image)
    self.copyImageVizScaleAct = QAction ('&Copy Image (Current Viz Scale)',
        self, triggered=self.on_copy_image_viz_scale)
        
    self.pasteAsANewImageAct = QAction ('&Paste as a New Image',
        self, triggered=self.on_paste_as_a_new_image)
                
  
  def createViewActions (self):
    self.zoomInAct = QAction ('Zoom &In (25%)',
        self, shortcut='=',  #'Ctrl+='
        enabled=False, triggered=self.on_zoom_in_adj_win)

    self.zoomOutAct = QAction ('Zoom &Out (25%)',
        self, shortcut='-',
        enabled=False, triggered=self.on_zoom_out_adj_win)

    self.originalSizeAct = QAction ('&Original Size',
        self, shortcut='0',
        enabled=False, triggered=self.on_reset_zoom_adj_win)

    self.fitToWindowAct = QAction ('&Fit to Window',
        self, enabled=False, checkable=True, shortcut='Ctrl+F',
        triggered=self.on_fit_img_to_window)

    self.fitWindowToImgAct = QAction ('&Fit Window to Image',
        self, checkable=False, triggered=self.on_fit_window_to_view)
    
  def createImgProcActions (self):
    self.negativeImgAct = QAction ('&Negative Image',
        self, checkable=True, triggered=self.on_negative_img)

    self.mirrorImgAct = QAction ('&Mirror Image',
        self, checkable=True, triggered=self.on_mirror_img)

  def createHelpActions (self):
    self.aboutAct = QAction ('&About',
        self, triggered=self.on_about)

    self.setVerboseAction = QAction ('Set &Verbose',
        self, triggered=self.on_set_verbose)


  def createMenus (self):
    self.fileMenu = QMenu ('&File', self)
    self.setupFileMenu ()    
    self.editMenu = QMenu ('&Edit', self)
    self.setupEditMenu ()    
    self.viewMenu = QMenu ('&View', self)
    self.setupViewMenu ()
    self.imgProcMenu = QMenu ('&Image Process', self)
    self.setupImgProcMenu ()
    self.helpMenu = QMenu ('&Help', self)
    self.setupHelpMenu ()

    self.menuBar().addMenu (self.fileMenu)
    self.menuBar().addMenu (self.editMenu)
    self.menuBar().addMenu (self.viewMenu)
    self.menuBar().addMenu (self.imgProcMenu)
    self.menuBar().addMenu (self.helpMenu)

  def setupFileMenu (self):
    self.fileMenu.addAction (self.fileNewAct)
    self.fileMenu.addAction (self.fileNewExample1Act)
    self.fileMenu.addAction (self.fileNewExample2Act)
    self.fileMenu.addAction (self.fileNewExample3Act)
    self.fileMenu.addAction (self.fileOpenImageAct)
    self.fileMenu.addSeparator ()
    self.fileMenu.addAction (self.fileSaveImageSrcAct)
    self.fileMenu.addAction (self.fileSaveImageOutAct)
    self.fileMenu.addSeparator ()
    self.fileMenu.addAction (self.exitAct)

  def setupEditMenu (self):
    self.editMenu.addAction (self.copyImageAct)
    self.editMenu.addAction (self.copyImageVizScaleAct)
    self.editMenu.addSeparator ()
    self.editMenu.addAction (self.pasteAsANewImageAct)
  
  def setupViewMenu (self):
    self.viewMenu.addAction (self.zoomInAct)
    self.viewMenu.addAction (self.zoomOutAct)
    self.viewMenu.addAction (self.originalSizeAct)
    self.viewMenu.addSeparator ()
    self.viewMenu.addAction (self.fitToWindowAct)
    self.viewMenu.addAction (self.fitWindowToImgAct)
  
  def setupImgProcMenu (self):
    self.imgProcMenu.addAction (self.negativeImgAct)
    self.imgProcMenu.addAction (self.mirrorImgAct)
  
  def setupHelpMenu (self):
    self.helpMenu.addAction (self.aboutAct)
    self.helpMenu.addSeparator ()
    self.helpMenu.addAction (self.setVerboseAction)
  
  def createMainFrame (self):
    self.vizWidget = viz_widget.VizWidget ()       
    self.vizWidgetScrollArea = viz_widget.VizWidgetScrollArea (self.vizWidget)
    self.setCentralWidget (self.vizWidgetScrollArea)

    # Status Bar
    self.statusLabel = QLabel('', self)
    self.statusBar().addWidget(self.statusLabel, 1)

  # =============================================  
    
  def initImageVizAndView (self, W=None, H=None):
    self.initImageViz (W, H)

    self.visualizeImgAdjustSize (self.qImg)
    self.on_fit_window_to_view()
      
  def initImageViz (self, W=None, H=None):
    if W is None:
     W = ImageViz_var.NEW_IMAGE_W
    if H is None:
     H = ImageViz_var.NEW_IMAGE_H
     
    self.ImgFile = ''
    self.qImg = QImage (W, H, QImage.Format_RGB32)
    self.qImg.fill (Qt.white)
    self.reset_viz_zoom ()
    
    self.scale_viz_if_outfit_screen (self.qImg.width(), self.qImg.height())
    
    str = '%s [W %d, H %d] %s bits' % (self.ImgFile, self.qImg.width(), self.qImg.height(),  self.qImg.depth())
    self.updateStatusBar (str)
    
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      
  def scale_viz_if_outfit_screen (self, imW, imH):    
    # scale down if qImg is larger than screen resolution
    
    print_msg = var.VERBOSE>0
    if imW < 400 and imH < 300:
      print_msg = False
    
    # considering border, space used by task bar etc.
    sw = var.SCREEN_RES_W - var.SCREEN_MARGIN_W
    sh = var.SCREEN_RES_H - var.SCREEN_MARGIN_H
    
    rw = float(sw) / imW
    rh = float(sh) / imH
    r = min (rw, rh)
    if print_msg:
      print ('scale_viz_if_outfit_screen(): im %dx%d, screen %dx%d.' % (imW, imH, var.SCREEN_RES_W, var.SCREEN_RES_H))
    if print_msg:
      print ('  displayable %dx%d, im-screen-ratio (rw%.4f, rh%.4f).' % (sw, sh, rw, rh))
    
    if r > 1:
      self.scale_idx = 0
      var.VIZ_SCALE = self.VIZ_SCALE_LIST[self.scale_idx]
      if print_msg:
        print ('  r=%.2f > 1: Reset VIS_SCALE (=%.3f) %dx%d' % (r, var.VIZ_SCALE, imW*var.VIZ_SCALE, imH*var.VIZ_SCALE))
    else:      
      # need to scale vis by r
      # find the closest value in self.VIZ_SCALE_LIST
      # See https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array/2566508
      list = np.array(self.VIZ_SCALE_LIST)
      idx = (np.abs(list - r)).argmin()
      self.scale_idx = idx
      var.VIZ_SCALE = self.VIZ_SCALE_LIST[self.scale_idx]
      if print_msg:
        print ('  Rescale viz: idx %d, scale_idx %d, VIZ_SCALE %.3f %dx%d' % (idx, self.scale_idx, var.VIZ_SCALE, imW*var.VIZ_SCALE, imH*var.VIZ_SCALE))
      
  def reset_viz_zoom (self):
    var.VIZ_SCALE = 1.0
    var.VIZ_ZOOMIN = 1
    self.scale_idx = 0
    self.zoom_idx = 0
    # ToDo: fix this
    var.DRAWCMD_LIST = []  

  # ===== Menu Handlers =====

  def on_file_new (self):
    self.initImageVizAndView ()

  def on_file_new_example1 (self):
    self.ImgFile = 'tiny_col.png'
    self.scale_idx = 0
    self.zoom_idx = 9
    var.DRAWCMD_LIST = []
    drawcmd = ['line', [0, 1, 2, 3]]
    var.DRAWCMD_LIST.append (drawcmd)
    drawcmd = ['set_fg_col', [0, 128, 192]]
    var.DRAWCMD_LIST.append (drawcmd)
    drawcmd = ['rect', [-0.25, -0.25, 1.5, 0.5]]
    var.DRAWCMD_LIST.append (drawcmd)
    self.load_im_show ()

  def on_file_new_example2 (self):
    self.ImgFile = 'monkeys.jpg'
    self.scale_idx = 0
    self.zoom_idx = 0
    var.DRAWCMD_LIST = []
    drawcmd = ['set_fg_col', [0, 128, 192]]
    var.DRAWCMD_LIST.append (drawcmd)
    drawcmd = ['rect', [5, 5, 262, 175]]
    var.DRAWCMD_LIST.append (drawcmd)
    self.load_im_show ()

  def on_file_new_example3 (self):
    self.ImgFile = 'lena.png'
    self.scale_idx = 0
    self.zoom_idx = 0
    var.DRAWCMD_LIST = []
    drawcmd = ['rect', [5, 5, 500, 500]]
    var.DRAWCMD_LIST.append (drawcmd)
    drawcmd = ['text', [20, 20, 'lena']]
    var.DRAWCMD_LIST.append (drawcmd)
    self.load_im_show ()

  def on_file_open_image (self):
    default_dir = QDir.currentPath()
    fileName = QFileDialog.getOpenFileName (self, 
        'Open File', default_dir, self.readImageFilter)
    if fileName[0] is None:
      return False

    self.ImgFile = fileName[0]
    print ('ImgFile = %s' % (self.ImgFile))

    var.VIZ_SCALE = 1.0
    var.VIZ_ZOOMIN = 1
    self.scale_idx = 0
    self.zoom_idx = 0
    var.DRAWCMD_LIST = []
    self.load_im_show ()

  def load_im_show (self, ImgFile = None):
    ret = self.load_qImg (ImgFile)
    if ret == False:
      return False
      
    self.scale_viz_if_outfit_screen (self.qImg.width(), self.qImg.height())
      
    self.visualizeImgAdjustSize (self.qImg)
    
    self.on_fit_window_to_view()
    str = '%s [W %d, H %d] %s bits' % (self.ImgFile, self.qImg.width(), self.qImg.height(),  self.qImg.depth())
    self.updateStatusBar (str)

    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      
  def load_qImg (self, ImgFile):
    if ImgFile is not None:
      self.ImgFile = ImgFile
    if self.ImgFile is not None:
      self.qImg = QImage (self.ImgFile)
      if self.qImg.isNull():
        QMessageBox.information(self, 'Image Loader',
                'Load %s Failed!' % self.ImgFile)
        return False
    print ('load_qImg(): %s loaded' % (self.ImgFile))
    self.qImg.convertToFormat (QImage.Format.Format_RGB32)
    return True    
    
  def on_save_image_src (self):
    ofile = 'ImageSrc.png'
    default_dir = QDir.currentPath()
    fileName = QFileDialog.getSaveFileName (self, 
        'Save Source Image', default_dir, self.saveImageFilter)
    if fileName[0] is not None:
      ofile = fileName[0]
    self.qImg.save (ofile)
    print ('Source image saved to %s' % (ofile))
  
  def on_save_image_out (self):
    ofile = 'ImageOut.png'
    default_dir = QDir.currentPath()
    fileName = QFileDialog.getSaveFileName (self, 
        'Save Output Image', default_dir, self.saveImageFilter)
    if fileName[0] is not None:
      ofile = fileName[0]
      
    self.qImgOut.save (ofile)
    if 0:
      #http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/doc/html/qimagewriter.html
      writer = QImageWriter ('images/outimage.png', 'png');  
      writer.setFormat ('png')
      writer.setQuality (100)
      writer.write (self.qImgOut)
    print ('Output image saved to %s' % (ofile))
  
      
  def visualizeImg (self, qImg, updateGeom=True):
    var.VIZ_ZOOMIN = self.VIZ_ZOOMIN_LIST[self.zoom_idx]
    var.VIZ_SCALE = self.VIZ_SCALE_LIST[self.scale_idx]
    if var.VERBOSE>1:
      print ('visualizeImg: VIZ_ZOOMIN %d (idx %d) VIZ_SCALE %.3f (idx %d)' % (var.VIZ_ZOOMIN, self.zoom_idx, var.VIZ_SCALE, self.scale_idx))
      
    self.VizZoominPixmap = self.getVizZoominPixelmap (qImg)
    self.vizWidget.setPixmap (self.VizZoominPixmap)
    
    if updateGeom:
      self.vizWidget.updateGeometry ()
      self.vizWidgetScrollArea.updateGeometry ()
      self.vizWidget.update()

  def getVizZoominPixelmap (self, qImg):
    self.VizPixmap = QPixmap.fromImage (qImg)
    if self.zoom_idx > 0:
      # Zoom image
      self.VizZoominPixmap = self.VizPixmap.scaled (
        self.VizPixmap.width()*var.VIZ_ZOOMIN,
        self.VizPixmap.height()*var.VIZ_ZOOMIN,
        Qt.IgnoreAspectRatio,
        Qt.FastTransformation)
    else:
      # Scale image
      self.VizZoominPixmap = self.VizPixmap.scaled (
          self.VizPixmap.width()*var.VIZ_SCALE,
          self.VizPixmap.height()*var.VIZ_SCALE,
          Qt.IgnoreAspectRatio,
          Qt.FastTransformation)
    return self.VizZoominPixmap
      
      
  def visualizeImgAdjustSize (self, qImg):
    self.visualizeImg (qImg)
    self.fitToWindowAct.setEnabled (True)
    self.updateFitToWindowCheck ()
    self.adjustViewSize ()

  def adjustViewSize (self):
    if not self.fitToWindowAct.isChecked():
      self.vizWidget.adjustSize()
      self.vizWidgetScrollArea.adjustSize()

  def on_copy_image (self): 
    # Note that VizPixmap is in 100% scale.
    # Draw to the original scale on VizPixmap.
    vizPm = self.VizPixmap.copy()      
    qp = QPainter ()
    qp.begin (vizPm)
    self.vizWidget.performPaint (qp, force_origin_scale=True)    
    qp.end()
  
    # https://stackoverflow.com/questions/17676373/python-matplotlib-pyqt-copy-image-to-clipboard
    QApplication.clipboard().setPixmap (vizPm)   
  
  
  def on_copy_image_viz_scale (self):
    # Note that VizPixmap is in 100% scale.
    # In order to draw to the viewing scale, must draw to VizZoominPixmap.
    vizPm = self.VizZoominPixmap.copy()      
    qp = QPainter ()
    qp.begin (vizPm)
    self.vizWidget.performPaint (qp)    
    qp.end()
  
    # https://stackoverflow.com/questions/17676373/python-matplotlib-pyqt-copy-image-to-clipboard
    QApplication.clipboard().setPixmap (vizPm)  
                    
    
  def on_paste_as_a_new_image (self):
    clipb = QApplication.clipboard()
    qImg = clipb.image()
    if qImg.isNull():
      print ('clipboard does not contain an image!')
      return

    self.qImg = qImg  
    self.qImg.convertToFormat (QImage.Format.Format_RGB32)
    self.visualizeImgAdjustSize (self.qImg)
    self.on_fit_window_to_view()
    str = 'Paste Image: %s [W %d, H %d] %s bits' % (self.ImgFile, self.qImg.width(), self.qImg.height(),  self.qImg.depth())
    self.updateStatusBar (str)
    
  def on_paste_image (self):
    # https://stackoverflow.com/questions/3602482/qt-qimage-is-there-a-method-to-paste-qimage-into-another-qimage
    pass    
      
  def zoom_in (self):
    if self.scale_idx == 0:
      if self.zoom_idx+1 < len(self.VIZ_ZOOMIN_LIST):
        self.zoom_idx += 1
        var.VIZ_ZOOMIN = self.VIZ_ZOOMIN_LIST[self.zoom_idx]
        self.scaleImage (var.VIZ_ZOOMIN)
    else:
      if self.scale_idx > 0:
        self.scale_idx -= 1
        var.VIZ_SCALE = self.VIZ_SCALE_LIST[self.scale_idx]
        self.scaleImage (var.VIZ_SCALE)
      
  def on_zoom_in_adj_win (self):
    self.zoom_in ()
    self.on_fit_window_to_view ()    

  def zoom_out (self):
    if self.zoom_idx == 0:
      if self.scale_idx+1 < len(self.VIZ_SCALE_LIST):
        self.scale_idx += 1
        var.VIZ_SCALE = self.VIZ_SCALE_LIST[self.scale_idx]
        self.scaleImage (var.VIZ_SCALE)
    else:
      if self.zoom_idx > 0:
        self.zoom_idx -= 1
        var.VIZ_ZOOMIN = self.VIZ_ZOOMIN_LIST[self.zoom_idx]
        self.scaleImage (var.VIZ_ZOOMIN)

  def on_zoom_out_adj_win (self):
    self.zoom_out ()
    self.on_fit_window_to_view ()  
    
  def scaleImage (self, factor):
    if var.VERBOSE>1:
      print ('scaleImage(%.3f): VIZ_ZOOMIN %d (idx %d) VIZ_SCALE %.3f (idx %d)' % (factor, var.VIZ_ZOOMIN, self.zoom_idx, var.VIZ_SCALE, self.scale_idx))
    self.VizZoominPixmap = self.VizPixmap.scaled (
        self.VizPixmap.width()*factor,
        self.VizPixmap.height()*factor,
        Qt.IgnoreAspectRatio,
        Qt.FastTransformation)
    self.vizWidget.setPixmap (self.VizZoominPixmap)
    self.vizWidget.updateGeometry()
    self.vizWidget.adjustSize()
    self.vizWidget.update ()
    self.vizWidgetScrollArea.updateGeometry ()
    self.vizWidgetScrollArea.adjustSize ()
    self.adjustScrollBar (self.vizWidgetScrollArea.horizontalScrollBar(), factor)
    self.adjustScrollBar (self.vizWidgetScrollArea.verticalScrollBar(), factor)

  def on_reset_zoom (self):
    var.VIZ_SCALE = 1.0
    var.VIZ_ZOOMIN = 1
    self.scale_idx = 0
    self.zoom_idx = 0
    if var.VERBOSE>1:
      print ('on_reset_zoom(): VIZ_SCALE %.3f, scale_idx %d, VIZ_ZOOMIN %.3f, zoom_idx %d' % (var.VIZ_SCALE, self.scale_idx, var.VIZ_ZOOMIN, self.zoom_idx))
    self.VizZoominPixmap = self.VizPixmap.scaled (
        self.VizPixmap.width()*var.VIZ_ZOOMIN,
        self.VizPixmap.height()*var.VIZ_ZOOMIN,
        Qt.IgnoreAspectRatio,
        Qt.FastTransformation)
    self.vizWidget.setPixmap (self.VizZoominPixmap)
    self.vizWidget.updateGeometry ()
    self.vizWidget.adjustSize()
    self.vizWidget.update()
    self.vizWidgetScrollArea.updateGeometry ()
    self.vizWidgetScrollArea.adjustSize ()

  def on_reset_zoom_adj_win (self):
    self.on_reset_zoom ()
    self.on_fit_window_to_view () 
    
  def on_fit_img_to_window (self):
    fitToWin = self.fitToWindowAct.isChecked()
    self.vizWidgetScrollArea.setWidgetResizable (fitToWin)
    if not fitToWin:
      if var.VIZ_ZOOMIN == 1:
        self.on_reset_zoom ()
      else:
        self.scaleImage (var.VIZ_ZOOMIN)

    self.updateFitToWindowCheck()

  def on_fit_window_to_view (self):
    # Resize window to fit current image view (with scale or zoom)
    # Done by proper use of sizeHint(), updateGeometry(), adjustSize()
    w = self.vizWidget.width()
    h = self.vizWidget.height()
    if var.VERBOSE>1:
      print ('on_fit_window_to_view(): vizWidget w %d, h %d' % (w, h))
    self.vizWidgetScrollArea.setMinimumSize (w+var.VIZ_AREA_PADDING_W, h+var.VIZ_AREA_PADDING_H)
    self.vizWidgetScrollArea.adjustSize ()
    self.adjustSize ()
    # After adjustSize(), reset min size to (0,0) i.e. disable it.
    self.vizWidgetScrollArea.setMinimumSize (0, 0)

    # Obsolete approach by brute-force calculation
    # Win10: W+2, H+23 without status bar
    # Win10: W+2, H+43 status bar
    #w = self.vizWidget.width()
    #h = self.vizWidget.height()
    #print ('on_fit_window_to_view(): w %d + wb %d, h %d + hb %d, VIZ_SCALE %.3f, scale_idx %d, VIZ_ZOOMIN %.3f, zoom_idx %d' % (w, wb, h, hb, var.VIZ_SCALE, self.scale_idx, var.VIZ_ZOOMIN, self.zoom_idx))
    #self.APP_WND_W = w+wb
    #self.APP_WND_H = h+hb
    #self.resize (self.APP_WND_W, self.APP_WND_H)

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

    self.qImgOut = self.qImg.copy()
    self.qImgOut.invertPixels()
    self.visualizeImg (self.qImgOut)

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

    self.qImgOut = self.qImg.copy()
    self.qImgOut = self.qImgOut.mirrored (True, False)
    self.visualizeImg (self.qImgOut)

  def on_about (self):
    QMessageBox.about(self, 'Image Visualizer',
            '<p>The <b>PySide Image Visualizer</b>'
            'shows how to use PySide/PyQt to display a image in a GUI window.</p>'
            '<p>The only dependency is PySide. ')

  def on_set_verbose (self):
    v_str = '%d' % (var.VERBOSE)
    prompt_text = 'Set verbose level:'
    text, ok = QInputDialog.getText(self, '(0: xx, 1: xx, 2: xx, 3: xx, 4: xx', prompt_text, text=v_str)
    if ok:
      v = list(map(float, text.split()))
      print ('new VERBOSE value = %d' % (v[0]))
      var.VERBOSE = v[0]

      
  def updateFitToWindowCheck (self):
    self.zoomInAct.setEnabled (not self.fitToWindowAct.isChecked())
    self.zoomOutAct.setEnabled (not self.fitToWindowAct.isChecked())
    self.originalSizeAct.setEnabled (not self.fitToWindowAct.isChecked())

  def adjustScrollBar (self, scrollBar, factor):
    scrollBar.setValue(int(  factor * scrollBar.value()
                + ((factor - 1) * scrollBar.pageStep()/2)  ))

  def updateStatusBar (self, str):
    self.status_text = str
    self.statusBar().showMessage (self.status_text)

  # https://stackoverflow.com/questions/19825650/python-pyqt4-how-to-detect-the-mouse-click-position-anywhere-in-the-window
  def mousePressEvent (self, event):
    pos = event.pos()
    str = None
    if event.buttons() == Qt.LeftButton:
      str = 'L-Click (%d, %d)' % (pos.x(), pos.y())
    elif event.buttons() == Qt.RightButton:
      str = 'R-Click (%d, %d)' % (pos.x(), pos.y())
    self.updateStatusBar (str)
  
  # https://stackoverflow.com/questions/25368295/qwidgetmousemoveevent-not-firing-when-cursor-over-child-widget
  def setMouseTracking (self, flag):
    def recursive_set (parent):
      for child in parent.findChildren (QObject):
        try:
          child.setMouseTracking (flag)
        except:
          pass
        recursive_set (child)
    QWidget.setMouseTracking (self, flag)
    recursive_set (self)

  # https://stackoverflow.com/questions/7829829/pyqt4-mousemove-event-without-mousepress
  def mouseMoveEvent (self, event):
    pos = event.pos()
    str = '(x%d y%d)' % (pos.x(), pos.y())
    if event.buttons() == Qt.NoButton:
      pass
    elif event.buttons() == Qt.LeftButton:
      str = 'L-Drag: (%d, %d)' % (pos.x(), pos.y())
    elif event.buttons() == Qt.RightButton:
      str = 'R-Drag: (%d, %d)' % (pos.x(), pos.y())
    if str is not None:
      self.updateStatusBar (str)

  # ==================== File Drag and Drop - Start ====================
  def dragEnterEvent (self, e):
    if e.mimeData().hasUrls:
      e.accept()
    else:
      e.ignore()

  def dragMoveEvent (self, e):
    if e.mimeData().hasUrls:
      #e.setDropAction (Qt.CopyAction)
      e.accept()
    else:
      e.ignore()

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
      self.ImgFile = fname
      #print ('dropEvent(): ImgFile = %s' % (self.ImgFile))
      var.VIZ_SCALE = 1.0
      var.VIZ_ZOOMIN = 1
      self.scale_idx = 0
      self.zoom_idx = 0
      var.DRAWCMD_LIST = []
      self.load_im_show ()
    else:
      e.ignore()
  # ==================== File Drag and Drop - End ====================

if __name__ == '__main__':
  import sys
  app = QApplication (sys.argv)
  # Set application Icon
  # See https://stackoverflow.com/questions/35272349/window-icon-does-not-show
  app.setWindowIcon (QIcon('ImageViz.png'))
  
  wnd = QImageVizWnd ()
  wnd.show ()
  sys.exit (app.exec_())

