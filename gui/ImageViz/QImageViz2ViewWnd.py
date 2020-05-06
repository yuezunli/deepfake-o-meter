
from PySide.QtCore import *
from PySide.QtGui import *

# This enables to import PyCVApp/*.py
import sys; sys.path.insert(0, '..')

import var
import ImageViz_var
import viz_widget
import ImageViz.QImageVizWnd as QImageVizWnd

class QImageViz2ViewWnd (QImageVizWnd.QImageVizWnd):
  def __init__(self):
    super (QImageViz2ViewWnd, self).__init__()
    self.setWindowTitle ('QImageViz2View')

  def createMainFrame (self):
    self.vizWidget = viz_widget.VizWidget()
    self.vizWidgetScrollArea = viz_widget.VizWidgetScrollArea (self.vizWidget)
    self.vizWidget2 = viz_widget.VizWidget(2)
    self.vizWidgetScrollArea2 = viz_widget.VizWidgetScrollArea (self.vizWidget2)

    if 1:
      # Sync the scroll of the scrollAreas
      # see https://stackoverflow.com/questions/35585086/one-single-scroll-bar-for-two-qtextedit-pyqt4-python
      self.vizWidgetScrollArea.horizontalScrollBar().valueChanged.connect(self.vizWidgetScrollArea2.horizontalScrollBar().setValue)
      self.vizWidgetScrollArea.verticalScrollBar().valueChanged.connect(self.vizWidgetScrollArea2.verticalScrollBar().setValue)
      self.vizWidgetScrollArea2.horizontalScrollBar().valueChanged.connect(self.vizWidgetScrollArea.horizontalScrollBar().setValue)
      self.vizWidgetScrollArea2.verticalScrollBar().valueChanged.connect(self.vizWidgetScrollArea.verticalScrollBar().setValue)

    hbox2View = QHBoxLayout ()
    for w in [self.vizWidgetScrollArea, self.vizWidgetScrollArea2]:
      hbox2View.addWidget (w)
      hbox2View.setAlignment (w, Qt.AlignVCenter)
    hbox2View.setSizeConstraint (QLayout.SetMinimumSize)

    self.mainWidget = QWidget ()
    self.mainWidget.setLayout (hbox2View)
    self.mainWidget.setSizePolicy (QSizePolicy.Ignored, QSizePolicy.Ignored)
    self.setCentralWidget (self.mainWidget)

    # Status Bar
    self.statusLabel = QLabel ('', self)
    self.statusBar().addWidget(self.statusLabel, 1)

  def initImageVizAndView (self):
    super (QImageViz2ViewWnd, self).initImageVizAndView()
    
    self.qImg2 = self.qImg.copy()
    var.DRAWCMD_LIST_2 = []    
    
    self.visualizeImgAdjustSize2View (self.qImg, self.qImg2)    
    self.on_fit_window_to_view()
    
  # ===== Menu Handlers =====

  def on_file_new_example1 (self):
    self.ImgFile = 'tiny_col.png'
    self.scale_idx = 0
    self.zoom_idx = 9
    var.DRAWCMD_LIST = []
    drawcmd = ['line', [0, 1, 2, 3]]
    var.DRAWCMD_LIST.append (drawcmd) 
    drawcmd = ['rect', [-0.25, -0.25, 1.5, 0.5]]
    var.DRAWCMD_LIST.append (drawcmd) 

    var.DRAWCMD_LIST_2 = []
    drawcmd = ['line', [0, 1, 3, 1]]
    var.DRAWCMD_LIST_2.append (drawcmd)
    drawcmd = ['rect', [0.75, -0.25, 2.5, 0.5]]
    var.DRAWCMD_LIST_2.append (drawcmd)
    
    self.load_im_show ()

  def on_file_new_example2 (self):
    self.ImgFile = 'monkeys.jpg'
    self.scale_idx = 0
    self.zoom_idx = 0
    drawcmd = ['rect', [5, 5, 262, 175]]
    var.DRAWCMD_LIST = []
    var.DRAWCMD_LIST.append (drawcmd)  
    
    drawcmd = ['rect', [15, 15, 242, 155]]
    var.DRAWCMD_LIST_2 = []
    var.DRAWCMD_LIST_2.append (drawcmd)
    
    self.load_im_show ()
    
  def on_file_new_example3 (self):
    self.ImgFile = 'lena.png'
    self.scale_idx = 0
    self.zoom_idx = 0
    drawcmd = ['rect', [5, 5, 500, 500]]
    var.DRAWCMD_LIST = []
    var.DRAWCMD_LIST.append (drawcmd) 
    
    drawcmd = ['rect', [10, 10, 490, 490]]
    var.DRAWCMD_LIST_2 = []
    var.DRAWCMD_LIST_2.append (drawcmd)
    
    self.load_im_show ()

  def on_file_open_image (self):
    var.DRAWCMD_LIST_2 = [] 
    super (QImageViz2ViewWnd, self).on_file_open_image ()
     
  
  def load_im_show (self, ImgFile = None):
    if ImgFile is not None:
      self.ImgFile = ImgFile
    if self.ImgFile is not None:  
      self.qImg = QImage (self.ImgFile)
      if self.qImg.isNull():
        QMessageBox.information(self, 'Image Loader',
                'Load %s Failed!' % ImgFile)
        return
    self.qImg.convertToFormat (QImage.Format.Format_RGB32)
    print ('load_im_show(): %s loaded' % (self.ImgFile))

    # Initially just show identical views
    self.qImg2 = self.qImg.copy()
    
    self.visualizeImgAdjustSize2View (self.qImg, self.qImg2) 
    self.on_fit_window_to_view()   
    str = '%s [W %d, H %d] %s bits' % (self.ImgFile, self.qImg.width(), self.qImg.height(),  self.qImg.depth())
    self.updateStatusBar (str)
    
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      
  def visualizeImg2 (self, qImg2, updateGeom=True):
    var.VIZ_ZOOMIN = self.VIZ_ZOOMIN_LIST[self.zoom_idx]
    var.VIZ_SCALE = self.VIZ_SCALE_LIST[self.scale_idx]
    if var.VERBOSE>1:
      print ('visualizeImg2: VIZ_ZOOMIN %d (idx %d) VIZ_SCALE %.3f (idx %d)' % (var.VIZ_ZOOMIN, self.zoom_idx, var.VIZ_SCALE, self.scale_idx))
      self.vizWidget2.setPixmap (self.VizZoominPixmap2)
    
    self.VizZoominPixmap2 = self.getVizZoominPixelmap2 (qImg2)
    self.vizWidget2.setPixmap (self.VizZoominPixmap2)
    
    if updateGeom:
      self.vizWidget2.updateGeometry ()
      self.vizWidgetScrollArea2.updateGeometry ()
      self.vizWidget2.update()

  def getVizZoominPixelmap2 (self, qImg2):
    self.VizPixmap2 = QPixmap.fromImage (qImg2)
    if self.zoom_idx > 0:
      # Zoom image
      self.VizZoominPixmap2 = self.VizPixmap2.scaled (
        self.VizPixmap2.width()*var.VIZ_ZOOMIN,
        self.VizPixmap2.height()*var.VIZ_ZOOMIN,
        Qt.IgnoreAspectRatio,
        Qt.FastTransformation)
    else:
      # Scale image
      self.VizZoominPixmap2 = self.VizPixmap2.scaled (
          self.VizPixmap2.width()*var.VIZ_SCALE,
          self.VizPixmap2.height()*var.VIZ_SCALE,
          Qt.IgnoreAspectRatio,
          Qt.FastTransformation)
    return self.VizZoominPixmap2
  
  def visualizeImgAdjustSize2View (self, qImg, qImg2):    
    self.visualizeImg (qImg)
    self.visualizeImg2 (qImg2)
    self.fitToWindowAct.setEnabled (True)
    self.updateFitToWindowCheck ()
    self.adjustViewSize2View ()

  def adjustViewSize2View (self):  
    # see https://stackoverflow.com/questions/10758267/how-to-force-layout-update-resize-when-child-it-manages-resizes
    if not self.fitToWindowAct.isChecked():
      self.vizWidget.adjustSize()
      self.vizWidget2.adjustSize()
      self.vizWidgetScrollArea.adjustSize ()
      self.vizWidgetScrollArea2.adjustSize ()
    self.mainWidget.adjustSize ()
      
  def zoom_in (self):
    if self.scale_idx == 0:
      self.zoom_idx += 1
      var.VIZ_ZOOMIN = self.VIZ_ZOOMIN_LIST[self.zoom_idx]
      self.scaleImage (var.VIZ_ZOOMIN)
      self.scaleImage2 (var.VIZ_ZOOMIN)
    else:
      self.scale_idx -= 1
      var.VIZ_SCALE = self.VIZ_SCALE_LIST[self.scale_idx]
      self.scaleImage (var.VIZ_SCALE)
      self.scaleImage2 (var.VIZ_SCALE)

  def zoom_out (self):
    if self.zoom_idx == 0:
      self.scale_idx += 1
      var.VIZ_SCALE = self.VIZ_SCALE_LIST[self.scale_idx]
      self.scaleImage (var.VIZ_SCALE)
      self.scaleImage2 (var.VIZ_SCALE)
    else:
      self.zoom_idx -= 1
      var.VIZ_ZOOMIN = self.VIZ_ZOOMIN_LIST[self.zoom_idx]
      self.scaleImage (var.VIZ_ZOOMIN)
      self.scaleImage2 (var.VIZ_ZOOMIN)

  def scaleImage2 (self, factor):
    if var.VERBOSE>1:
      print ('scaleImage2(%.3f): VIZ_ZOOMIN %d (idx %d) VIZ_SCALE %.3f (idx %d)' % (factor, var.VIZ_ZOOMIN, self.zoom_idx, var.VIZ_SCALE, self.scale_idx))
    self.VizZoominPixmap2 = self.VizPixmap2.scaled (
        self.VizPixmap2.width()*factor,
        self.VizPixmap2.height()*factor,
        Qt.IgnoreAspectRatio,
        Qt.FastTransformation)
    self.vizWidget2.setPixmap (self.VizZoominPixmap2)
    self.vizWidget2.updateGeometry()
    self.vizWidget2.adjustSize()
    self.vizWidget2.update()
    self.vizWidgetScrollArea2.updateGeometry ()
    self.vizWidgetScrollArea2.adjustSize ()
    self.adjustScrollBar(self.vizWidgetScrollArea2.horizontalScrollBar(), factor)
    self.adjustScrollBar(self.vizWidgetScrollArea2.verticalScrollBar(), factor)
    
  def on_reset_zoom (self):
    super (QImageViz2ViewWnd, self).on_reset_zoom ()

    self.VizZoominPixmap2 = self.VizPixmap2.scaled (
        self.VizPixmap2.width()*var.VIZ_ZOOMIN,
        self.VizPixmap2.height()*var.VIZ_ZOOMIN,
        Qt.IgnoreAspectRatio,
        Qt.FastTransformation)
    self.vizWidget2.setPixmap(self.VizZoominPixmap2)
    self.vizWidget2.updateGeometry ()
    self.vizWidget2.adjustSize()
    self.vizWidget2.update()
    self.vizWidgetScrollArea2.updateGeometry ()
    self.vizWidgetScrollArea2.adjustSize ()

  def on_fit_img_to_window (self):
    fitToWin = self.fitToWindowAct.isChecked()
    self.vizWidgetScrollArea.setWidgetResizable(fitToWin)
    self.vizWidgetScrollArea2.setWidgetResizable(fitToWin)
    if not fitToWin:
      if var.VIZ_ZOOMIN == 1:
        self.on_reset_zoom ()
      else:
        self.scaleImage (var.VIZ_ZOOMIN)
        self.scaleImage2 (var.VIZ_ZOOMIN)

    self.vizWidgetScrollArea.updateGeometry ()
    self.vizWidgetScrollArea2.updateGeometry ()
    self.updateFitToWindowCheck ()

  def on_fit_window_to_view (self):
    # Resize window to fit current image view (with scale or zoom)
    # Done by proper use of sizeHint(), updateGeometry(), adjustSize()
    w = self.vizWidget.width()
    w2 = self.vizWidget2.width()
    h = self.vizWidget.height()
    h2 = self.vizWidget2.height()
    if var.VERBOSE>1:
      print ('on_fit_window_to_view(): vizWidget [w %d, h %d], [w2 %d, h2 %d]' % (w, h, w2, h2))
    # Add a 2 border pixels to ScrollArea
    self.vizWidgetScrollArea.setMinimumSize (w+var.VIZ_AREA_PADDING_W, h+var.VIZ_AREA_PADDING_H)
    self.vizWidgetScrollArea2.setMinimumSize (w2+var.VIZ_AREA_PADDING_W, h2+var.VIZ_AREA_PADDING_H)
    self.vizWidgetScrollArea.adjustSize ()
    self.vizWidgetScrollArea2.adjustSize ()
    self.mainWidget.adjustSize ()
    self.updateGeometry ()
    self.adjustSize ()
    # After adjustSize(), reset min size to (0,0) to disable it.
    self.vizWidgetScrollArea.setMinimumSize (0, 0)
    self.vizWidgetScrollArea2.setMinimumSize (0, 0)
    
    
    '''
    # Win10: W+12, H+43 with status bar
    w = self.vizWidget.width()
    w2 = self.vizWidget2.width()
    h = self.vizWidget.height()
    wb = 52
    hb = 63
    print ('on_fit_window_to_view(): w %d + w2 %d + wb %d, h %d + hb %d, VIZ_SCALE %.3f, scale_idx %d, VIZ_ZOOMIN %.3f, zoom_idx %d' % (w, w2, wb, h, hb, var.VIZ_SCALE, self.scale_idx, var.VIZ_ZOOMIN, self.zoom_idx))
    self.APP_WND_W = w+w2+wb
    self.APP_WND_H = h+hb
    self.vizWidgetScrollArea.updateGeometry ()
    self.vizWidgetScrollArea2.updateGeometry ()
    self.resize (self.APP_WND_W, self.APP_WND_H)
    '''
    
  def on_negative_img (self):
    if self.activatedProcessAct == self.negativeImgAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      self.visualizeImg2 (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.negativeImgAct
    self.activatedProcessAct.setChecked (True)
    
    # Invert qImg2
    self.qImg2 = self.qImg.copy()
    self.qImg2.invertPixels()
    self.visualizeImg2 (self.qImg2)

  def on_mirror_img (self):
    if self.activatedProcessAct == self.mirrorImgAct:
      self.activatedProcessAct.setChecked (False)
      self.activatedProcessAct = None
      self.visualizeImg (self.qImg)
      self.visualizeImg2 (self.qImg)
      return
    if self.activatedProcessAct is not None:
      self.activatedProcessAct.setChecked (False)
    self.activatedProcessAct = self.mirrorImgAct
    self.activatedProcessAct.setChecked (True)

    # Mirror qImg2
    self.qImg2 = self.qImg.copy()
    self.qImg2 = self.qImg2.mirrored (True, False)
    self.visualizeImg2 (self.qImg2)

if __name__ == '__main__':
  import sys
  app = QApplication (sys.argv)
  app.setWindowIcon (QIcon('ImageViz.png'))
  wnd = QImageViz2ViewWnd ()
  wnd.show ()
  sys.exit (app.exec_())