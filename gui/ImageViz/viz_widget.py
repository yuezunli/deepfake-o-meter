

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

import var

# Note that currently the drawcmd does not support 'fit image to window' mode!

# Subclass from QLabel to perform customized DRAWCMD painting event
# https://stackoverflow.com/questions/43454882/paint-over-qlabel-with-pyqt
class VizWidget (QLabel):
  def __init__ (self, DrawCmdListN=None, parent=None):
    super (VizWidget, self).__init__(parent=parent)
    self.setBackgroundRole (QPalette.Base)
    self.setScaledContents (True)
    self.setSizePolicy (QSizePolicy.Ignored, QSizePolicy.Ignored)
        
    self.DrawCmdListN = DrawCmdListN
    
  # The paintEvent will be called when there is a self.update()
  def paintEvent (self, e):
    super (VizWidget, self).paintEvent (e)
    
    qp = QPainter (self)   
    self.performPaint (qp)
    
    if var.VERBOSE>2:                     
      print ('paintEvent() drawcmd done')

    
  def performPaint (self, qp, force_origin_scale=False):  
    # f: zoomin or scale factor
    if force_origin_scale:
      f = 1
    elif var.VIZ_ZOOMIN==1:
      f = float(var.VIZ_SCALE)
    else:
      f = float(var.VIZ_ZOOMIN)
    
    pen = QPen (Qt.black, 0, Qt.SolidLine)
    qp.setPen (pen)
    brush = None
    font = QFont ()
    font.setPointSize (var.TEXT_FONT_SZ)
    qp.setFont (font)
    

    DRAWCMD_LIST = var.DRAWCMD_LIST
    if self.DrawCmdListN==2:
      DRAWCMD_LIST = var.DRAWCMD_LIST_2
        
    for drawcmd in DRAWCMD_LIST:
      if drawcmd[0] == 'set_fg_col':
        if len (drawcmd[1]) == 3:
          pen.setColor (QColor (drawcmd[1][0], drawcmd[1][1], drawcmd[1][2]))
          qp.setPen (pen)
        elif len (drawcmd[1]) == 4:
          pen.setColor (QColor (drawcmd[1][0], drawcmd[1][1], drawcmd[1][2], drawcmd[1][3]))
          qp.setPen (pen)
        #print ('fg %d %d %d' % (drawcmd[1][0], drawcmd[1][1], drawcmd[1][2]))
      elif drawcmd[0] == 'set_brush_col':
        brush = QBrush (Qt.black)
        if len (drawcmd[1]) == 3:
          brush.setColor (QColor (drawcmd[1][0], drawcmd[1][1], drawcmd[1][2]))
        elif len (drawcmd[1]) == 4:
          brush.setColor (QColor (drawcmd[1][0], drawcmd[1][1], drawcmd[1][2], drawcmd[1][3]))
      elif drawcmd[0] == 'set_font_sz':
        font.setPointSize (drawcmd[1])  
        qp.setFont (font)    
      elif drawcmd[0] == 'line':
        qp.drawLine ( QPointF (drawcmd[1][0]*f + f/2, drawcmd[1][1]*f + f/2),
                      QPointF (drawcmd[1][2]*f + f/2, drawcmd[1][3]*f + f/2) )
      elif drawcmd[0] == 'rect':
        qp.drawRect ( QRectF (drawcmd[1][0]*f + f/2, drawcmd[1][1]*f + f/2,
                              drawcmd[1][2]*f, drawcmd[1][3]*f) )
      elif drawcmd[0] == 'fillrect':
        obrush = qp.brush () 
        if brush is not None:
          qp.setBrush (brush)
        qp.fillRect ( QRectF (drawcmd[1][0]*f + f/2, drawcmd[1][1]*f + f/2,
                              drawcmd[1][2]*f, drawcmd[1][3]*f), brush )
        qp.setBrush (obrush)                      
      elif drawcmd[0] == 'polygon':
        polygon = QPolygonF ()
        #print (drawcmd[1])
        np = int(len(drawcmd[1])/2)
        for i in range (0, np+2, 2):
          polygon.append (QPointF ( drawcmd[1][i]*f + f/2, drawcmd[1][i+1]*f + f/2 ))
        polygon.append (QPointF ( drawcmd[1][0]*f + f/2, drawcmd[1][1]*f + f/2 ))
        qp.drawPolygon (polygon)
      elif drawcmd[0] == 'text':
        qp.drawText ( QPointF (drawcmd[1][0]*f + f/2, drawcmd[1][1]*f + f/2), drawcmd[1][2] )
      elif drawcmd[0] == 'textbg':
        obrush = qp.brush () 
        if brush is not None: 
          qp.setBrush (brush)
        qp.font().pointSize()
        #qp.drawRect ( QPointF (drawcmd[1][0]*f + f/2, drawcmd[1][1]*f + f/2), 
        qp.drawText ( QPointF (drawcmd[1][0]*f + f/2, drawcmd[1][1]*f + f/2), drawcmd[1][2] )
        qp.setBrush (obrush)
      else:
        # Unknown drawcmd, skip
        pass  
        
    
class VizWidgetScrollArea (QScrollArea):
  def __init__(self, widget):
    super (VizWidgetScrollArea, self).__init__()
    self.setWidget (widget)
    self.setBackgroundRole (QPalette.Dark)
    # This size policy should not be set.
    # If set, vbox of this scrollarea will stretch badly.
    #self.setSizePolicy (QSizePolicy.Ignored, QSizePolicy.Ignored)
    
  def sizeHint (self):
    # Add a 2 border pixels to ScrollArea
    return QSize (self.widget().width()+2, self.widget().height()+2)

    
# https://stackoverflow.com/questions/11132597/qslider-mouse-direct-jump    
class JumpSlider (QSlider):
  def __init__ (self, parent=None):
    super (JumpSlider, self).__init__(parent)
    # Default page step is 10
    # We change to 30, so for a 30 FPS video, a page step is 1 sec.
    self.setPageStep (30)

  def mousePressEvent (self, ev):
    if ev.button() == Qt.RightButton:
      ''' Jump to click position for right click'''
      self.setValue (QStyle.sliderValueFromPosition (self.minimum(), self.maximum(), ev.x(), self.width()))
    else:
      super (JumpSlider, self).mousePressEvent (ev)

  #def mouseMoveEvent (self, ev):
  #  ''' Jump to pointer position while moving '''
  #  self.setValue (QStyle.sliderValueFromPosition (self.minimum(), self.maximum(), ev.x(), self.width()))
