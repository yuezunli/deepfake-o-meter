
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
import ImageViz.ImageViz_var as ImageViz_var
import VideoViz.VideoViz_var as VideoViz_var

# ========== NewVideoDialog - Start ==========

class NewVideoDialog (QDialog):
  def __init__(self, parent = None):
    super (NewVideoDialog, self).__init__(parent)
    self.setWindowTitle ('New Video')
    
    vboxDialog = QVBoxLayout (self)
    
    labelwidth = 120
    editwidth = 50
        
    W_hbox = QHBoxLayout ()
    self.W_label = QLabel ('Frame Width:')
    self.W_label.setFixedWidth (labelwidth)
    self.W_edit = QLineEdit ()
    W = '%d' % (ImageViz_var.NEW_IMAGE_W)
    self.W_edit.setText (W)
    self.W_edit.setMaximumWidth (editwidth)    
    for w in [ self.W_label, self.W_edit ]:    
      W_hbox.addWidget (w)
      W_hbox.setAlignment (w, Qt.AlignVCenter)
    W_hbox.setSizeConstraint (QLayout.SetMinimumSize)
    vboxDialog.addLayout (W_hbox)
        
    H_hbox = QHBoxLayout ()
    self.H_label = QLabel ('Frame Height:')
    self.H_label.setFixedWidth (labelwidth)
    self.H_edit = QLineEdit ()
    H = '%d' % (ImageViz_var.NEW_IMAGE_H)
    self.H_edit.setText (H)
    self.H_edit.setMaximumWidth (editwidth) 
    for w in [ self.H_label, self.H_edit ]:    
      H_hbox.addWidget (w)
      H_hbox.setAlignment (w, Qt.AlignVCenter)
    H_hbox.setSizeConstraint (QLayout.SetMinimumSize)
    vboxDialog.addLayout (H_hbox)
    
    NF_hbox = QHBoxLayout ()
    self.NF_label = QLabel ('Number of Frames:')
    self.NF_label.setFixedWidth (labelwidth)
    self.NF_edit = QLineEdit ()
    NF = '%d' % (VideoViz_var.NEW_VIDEO_NF)
    self.NF_edit.setText (NF)
    self.NF_edit.setMaximumWidth (editwidth) 
    for w in [ self.NF_label, self.NF_edit ]:    
      NF_hbox.addWidget (w)
      NF_hbox.setAlignment (w, Qt.AlignVCenter)
    NF_hbox.setSizeConstraint (QLayout.SetMinimumSize)
    vboxDialog.addLayout (NF_hbox)
    
    FPS_hbox = QHBoxLayout ()
    self.FPS_label = QLabel ('Frame per Second (FPS):')
    self.FPS_label.setFixedWidth (labelwidth)
    self.FPS_edit = QLineEdit ()
    FPS = '%.2f' % (VideoViz_var.NEW_VIDEO_FPS)
    self.FPS_edit.setText (FPS)
    self.FPS_edit.setMaximumWidth (editwidth) 
    for w in [ self.FPS_label, self.FPS_edit ]:    
      FPS_hbox.addWidget (w)
      FPS_hbox.setAlignment (w, Qt.AlignVCenter)
    FPS_hbox.setSizeConstraint (QLayout.SetMinimumSize)
    vboxDialog.addLayout (FPS_hbox)
    
    FOURCC_hbox = QHBoxLayout ()
    self.FOURCC_label = QLabel ('Codec FourCC:')
    self.FOURCC_label.setFixedWidth (labelwidth)
    self.FOURCC_edit = QLineEdit ()
    FourCC = VideoViz_var.NEW_VIDEO_FOURCC
    self.FOURCC_edit.setText (FourCC)
    self.FOURCC_edit.setMaximumWidth (editwidth) 
    for w in [ self.FOURCC_label, self.FOURCC_edit ]:    
      FOURCC_hbox.addWidget (w)
      FOURCC_hbox.setAlignment (w, Qt.AlignVCenter)
    FOURCC_hbox.setSizeConstraint (QLayout.SetMinimumSize)
    vboxDialog.addLayout (FOURCC_hbox)
    
    # OK and Cancel buttons
    self.buttons = QDialogButtonBox(
      QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
      Qt.Horizontal, self)
    vboxDialog.addWidget (self.buttons)

    vboxDialog.setSizeConstraint (QLayout.SetMinimumSize)
    self.setLayout (vboxDialog)
    
    self.buttons.accepted.connect (self.accept)
    self.buttons.rejected.connect (self.reject)
  
  def dialogReturn (self):
    W = int(self.W_edit.text())
    if W is None:
      W = ImageViz_var.NEW_IMAGE_W
    H = int(self.H_edit.text())
    if H is None:
      H = ImageViz_var.NEW_IMAGE_H
    NF = int(self.NF_edit.text())
    if NF is None:
      NF = VideoViz_var.NEW_VIDEO_NF
    FPS = float(self.FPS_edit.text())
    if FPS is None:
      FPS = VideoViz_var.NEW_VIDEO_FPS
    FourCC = self.FOURCC_edit.text()
    return W, H, NF, FPS, FourCC
  
  def showDialog (self, parent = None):
    dialog = NewVideoDialog (parent)
    result = dialog.exec_()
    W, H, NF, FPS, FourCC = dialog.dialogReturn()
    return W, H, NF, FPS, FourCC, result == QDialog.Accepted
    
# ========== NewVideoDialog - End ==========

# ========== StartEndFrameDialog - Start ==========

class StartEndFrameDialog (QDialog):
  def __init__(self, parent = None):
    super (StartEndFrameDialog, self).__init__(parent)
    self.setWindowTitle ('Start and End Frame')

    vboxDialog = QVBoxLayout (self)
    
    labelwidth = 120
    editwidth = 50
        
    S_hbox = QHBoxLayout ()
    self.S_label = QLabel ('Start Frame:')
    self.S_label.setFixedWidth (labelwidth)
    self.S_edit = QLineEdit ()
    S = '%d' % (VideoViz_var.START_FI)
    self.S_edit.setText (S)
    self.S_edit.setMaximumWidth (editwidth)    
    for w in [ self.S_label, self.S_edit ]:    
      S_hbox.addWidget (w)
      S_hbox.setAlignment (w, Qt.AlignVCenter)
    S_hbox.setSizeConstraint (QLayout.SetMinimumSize)
    vboxDialog.addLayout (S_hbox)

    E_hbox = QHBoxLayout ()
    self.E_label = QLabel ('End Frame:')
    self.E_label.setFixedWidth (labelwidth)
    self.E_edit = QLineEdit ()
    E = '%d' % (VideoViz_var.END_FI)
    self.E_edit.setText (E)
    self.E_edit.setMaximumWidth (editwidth)    
    for w in [ self.E_label, self.E_edit ]:    
      E_hbox.addWidget (w)
      E_hbox.setAlignment (w, Qt.AlignVCenter)
    E_hbox.setSizeConstraint (QLayout.SetMinimumSize)
    vboxDialog.addLayout (E_hbox)
    
    # OK and Cancel buttons
    self.buttons = QDialogButtonBox(
      QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
      Qt.Horizontal, self)
    vboxDialog.addWidget (self.buttons)

    vboxDialog.setSizeConstraint (QLayout.SetMinimumSize)
    self.setLayout (vboxDialog)
    
    self.buttons.accepted.connect (self.accept)
    self.buttons.rejected.connect (self.reject)
    
  def dialogReturn (self):
    S = int(self.S_edit.text())
    if S is None:
      S = VideoViz_var.START_FI
    E = int(self.E_edit.text())
    if E is None:
      E = VideoViz_var.START_FI
    return S, E
    
  def showDialog (self, parent = None):
    dialog = StartEndFrameDialog (parent)
    result = dialog.exec_()
    S, E = dialog.dialogReturn()
    return S, E, result == QDialog.Accepted
     
# ========== StartEndFrameDialog - End ==========
