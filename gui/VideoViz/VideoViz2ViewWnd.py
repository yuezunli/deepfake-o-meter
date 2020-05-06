
from PySide.QtCore import *
from PySide.QtGui import *

# This enables to import PyCVApp/*.py
import sys; sys.path.insert(0, '..')

import var
import ImageViz.viz_widget as viz_widget
import ImageViz.np_ocv_qim_convert as np_ocv_qim_convert

import ocv_vid
import VideoViz.VideoVizWnd as VideoVizWnd

class VideoViz2ViewWnd (VideoVizWnd.VideoVizWnd):
  def __init__(self):
    super (VideoViz2ViewWnd, self).__init__()
    self.setWindowTitle ('VideoViz2View')
    if var.VERBOSE>3:
      print ('end of VideoViz2ViewWnd.__init__()')
      
  def createMainFrame (self):
    # Image display using VizWidget defined in viz_widget.py
    self.vizWidget = viz_widget.VizWidget ()
    self.vizWidgetScrollArea = viz_widget.VizWidgetScrollArea (self.vizWidget)
    self.vizWidget2 = viz_widget.VizWidget (2)
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
    # set min size for this layout
    hbox2View.setSizeConstraint (QLayout.SetMinimumSize)

    vboxMainFrame = QVBoxLayout()
    vboxMainFrame.addLayout (hbox2View)
    #dummyWidget = QLabel()   
    #dummyWidget.setSizePolicy (QSizePolicy.Ignored, QSizePolicy.Ignored)
    #vboxMainFrame.addWidget (dummyWidget)
    hboxVideoCtrl = self.createVideoCtrlHBox ()
    vboxMainFrame.addLayout (hboxVideoCtrl)
    # set min size for this layout
    vboxMainFrame.setSizeConstraint (QLayout.SetMinimumSize)
    
    self.mainWidget = QWidget ()
    self.mainWidget.setLayout (vboxMainFrame)
    self.mainWidget.setSizePolicy (QSizePolicy.Ignored, QSizePolicy.Ignored)
    self.setCentralWidget (self.mainWidget)

    # Status Bar
    self.statusLabel = QLabel ('', self)
    self.statusBar().addWidget(self.statusLabel, 1)
      
  # ===== Menu Handlers =====

  def initVideoVizAndView (self):
    super (VideoViz2ViewWnd, self).initVideoVizAndView ()
    self.qImg2 = self.qImg.copy()
    self.vizWidget2.DRAWCMD_LIST = []

    self.visualizeImgAdjustSize2View(self.qImg, self.qImg2)
    self.on_fit_window_to_view()
       
  def on_file_open_video (self):
    var.DRAWCMD_LIST_2 = [] 
    super (VideoViz2ViewWnd, self).on_file_open_video ()
  
  def load_video_show (self):
    ret = self.load_video()
    if ret == False:
      print ('load_video_show(): load_video() failed!')
      return False

    # step and display the first frame
    newFI = 0
    self.proc_frame (newFI)
    self.slider.setValue (newFI)
    
    # adjust window
    self.adjustViewSize2View ()
    self.on_fit_window_to_view ()
    
    # update statusBar
    self.frameTextEdit.setText (str(self.FI))
    t = ocv_vid.frame_to_video_time (self.VIDFP, self.VIDEO_FPS, self.FI)
    t_str = ocv_vid.time_s_to_hms (t)
    self.timeTextEdit.setText (t_str)
    self.updateStatusBar ()
    return True
  
  def visualizeImg2 (self, qImg2, updateGeom=True):
    var.VIZ_ZOOMIN = self.VIZ_ZOOMIN_LIST[self.zoom_idx]
    var.VIZ_SCALE = self.VIZ_SCALE_LIST[self.scale_idx]
    if var.VERBOSE>1:
      print ('visualizeImg2: VIZ_ZOOMIN %d (idx %d) VIZ_SCALE %.3f (idx %d)' % (var.VIZ_ZOOMIN, self.zoom_idx, var.VIZ_SCALE, self.scale_idx))
    self.VizPixmap2 = QPixmap.fromImage (qImg2)
        
    self.VizZoominPixmap2 = self.getVizZoominPixelmap (qImg2)
    self.vizWidget2.setPixmap (self.VizZoominPixmap2)
    
    if updateGeom:
      self.vizWidget2.updateGeometry ()
      self.vizWidgetScrollArea2.updateGeometry ()
      self.vizWidget2.update()
    
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
      var.VIZ_SCALE = var.VIZ_SCALE_LIST[self.scale_idx]
      self.scaleImage (var.VIZ_SCALE)
      self.scaleImage2 (var.VIZ_SCALE)

  def zoom_out (self):
    if self.zoom_idx == 0:
      self.scale_idx += 1
      var.VIZ_SCALE = var.VIZ_SCALE_LIST[self.scale_idx]
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
    super (VideoViz2ViewWnd, self).on_reset_zoom ()

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
    #self.vizWidgetScrollArea.setMinimumSize (0, 0)
    #self.vizWidgetScrollArea2.setMinimumSize (0, 0)
        
  def proc_frame_viz (self):  
    # Draw self.I in view1 and self.IOut in view2
    self.qImg = np_ocv_qim_convert.NpArrayToQImage (self.I)
    self.visualizeImg (self.qImg, updateGeom=False)
    self.qImgOut = np_ocv_qim_convert.NpArrayToQImage (self.IOut)
    self.visualizeImg2 (self.qImgOut, updateGeom=False) 
        
      
    
if __name__ == '__main__':
  import sys
  var.INPUT_VIDEO = 'avi_frames.avi'
  
  if len(var.INPUT_VIDEO) == 0:
    if len(sys.argv) == 1:
      print ('Run: <input.avi>')
      #sys.exit()
  if len(sys.argv) > 1:
    # Use the command-line input file
    var.INPUT_VIDEO = str(sys.argv[1])
  print ('main(): INPUT_VIDEO = %s' % (var.INPUT_VIDEO))
  
  app = QApplication (sys.argv)
  app.setWindowIcon (QIcon('VideoViz.png'))
  wnd = VideoViz2ViewWnd ()
  wnd.show ()
  sys.exit (app.exec_())