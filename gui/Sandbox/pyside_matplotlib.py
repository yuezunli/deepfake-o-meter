# http://www.scipy.org/Cookbook/Matplotlib/PySide
# http://stackoverflow.com/questions/6723527/getting-pyside-to-work-with-matplotlib

#!/usr/bin/env python
import sys
from PySide import QtCore, QtGui
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
import pylab

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


if __name__ == '__main__':
  app = QtGui.QApplication(sys.argv)

  # generate the plot
  fig = Figure(figsize=(600,600), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
  ax = fig.add_subplot(111)
  ax.plot([0,1])
  # generate the canvas to display the plot
  canvas = FigureCanvas(fig)

  win = QtGui.QMainWindow()
  # add the plot canvas to a window
  win.setCentralWidget(canvas)

  win.show()

  sys.exit(app.exec_())