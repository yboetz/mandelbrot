# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 11:03:55 2015

@author: somebody
"""

import numpy as np
from Mandelbrot import Mandel
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from time import time


xmin, xmax = -2,1
ymin, ymax =  -1.5,1.5
#xmin, xmax = -0.7436438870576386, -0.7436438870166787
#ymin, ymax = 0.1318259041848326, 0.1318259042257926

xsize  = 16
ysize = 16
#ysize = int(xsize / (xmax - xmin) * (ymax - ymin))

maxit, col = 200, 50

stops = np.array([ 0.0, 0.33, 0.66, 1.0])
colArr = np.array([[0, 0, 0, 1], [1, 0, 0, 1], [1, .6, 0, 1], [0,0,0, 1]])
colMap = pg.ColorMap(stops, colArr)
lut = colMap.getLookupTable(0.0, 1.0, col)

# GraphicsLayoutWidget class with controls & fractal data
class FractalWidget(pg.GraphicsLayoutWidget):
    def __init__(self):
        super(FractalWidget, self).__init__()
        self.init()
     
    def init(self):
        self.data = np.zeros(xsize*ysize,dtype = np.int32)
        st = time()
        self.fractal = Mandel(xsize, ysize, xmin, xmax, ymin, ymax, maxit, col, self.data)
        print("Image calculated in %.6f s" %(time() - st))
        
        # Create image item
        self.ip = pg.ImageItem(border = 'w')
        self.ip.setImage(self.data.reshape((ysize,xsize)).transpose()[:,::-1])
        self.ip.setLookupTable(lut)
        print(self.data.reshape((ysize, xsize)))
        print(np.max(self.data), np.min(self.data))
        
        # Add view box
        view = self.addViewBox()
        view.setMouseEnabled(x=False, y=False)
        view.setAspectLocked(lock=True, ratio = ysize/xsize)
        
        # Add image item to widget
        view.addItem(self.ip)
    
    def resetInitial(self):
        st = time()
        self.fractal = Mandel(xsize, ysize, xmin, xmax, ymin, ymax, maxit, col, self.data)
        print("Image calculated in %.6f s" %(time() - st))
        self.ip.setImage(self.data.reshape((ysize,xsize)).transpose()[:,::-1])
    
    def zoomIn(self):
        st = time()
        self.fractal.zoom(.5)
        print("Image calculated in %.6f s" %(time() - st))
        self.ip.setImage(self.data.reshape((ysize,xsize)).transpose()[:,::-1])
    
    def zoomOut(self):
        st = time()
        self.fractal.zoom(2.0)
        print("Image calculated in %.6f s" %(time() - st))
        self.ip.setImage(self.data.reshape((ysize,xsize)).transpose()[:,::-1])
    
    def moveL(self):
        st = time()
        self.fractal.moveL(xsize//32)
        print("Image calculated in %.6f s" %(time() - st))
        self.ip.setImage(self.data.reshape((ysize,xsize)).transpose()[:,::-1])
    
    def moveR(self):
        st = time()
        self.fractal.moveR(xsize//32)
        print("Image calculated in %.6f s" %(time() - st))
        self.ip.setImage(self.data.reshape((ysize,xsize)).transpose()[:,::-1])
    
    def moveD(self):
        st = time()
        self.fractal.moveD(ysize//32)
        print("Image calculated in %.6f s" %(time() - st))
        self.ip.setImage(self.data.reshape((ysize,xsize)).transpose()[:,::-1])
    
    def moveU(self):
        st = time()
        self.fractal.moveU(ysize//32)
        print("Image calculated in %.6f s" %(time() - st))
        self.ip.setImage(self.data.reshape((ysize,xsize)).transpose()[:,::-1])
    
    def setMaxIt(self):
        m = int(input("Please set number of iterations to check:\n"))
        st = time()
        self.fractal.setMaxIt(m)
        print("Image calculated in %.6f s" %(time() - st))
        self.ip.setImage(self.data.reshape((ysize,xsize)).transpose()[:,::-1])


# Main window, to have file menu & statusbar
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init()
        self.show()
        
    def init(self):
        self.resize(ysize, xsize)
        self.setWindowTitle('Mandelbrot')
        
        self.window = FractalWidget()
        self.window.keyPressEvent = self.keyPressEvent
        self.setCentralWidget(self.window)
#        self.statusBar()
        # Menubar entries
        closeApp = QtGui.QAction(QtGui.QIcon('quit.png'), 'Quit', self)
        closeApp.setShortcut('Escape')
        closeApp.setStatusTip('Exits application')
        closeApp.triggered.connect(pg.exit)
        # Add menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(closeApp)
        # Defines which function to call at what keypress
        self.keyList = {
                        QtCore.Qt.Key_R: self.window.resetInitial,
                        QtCore.Qt.Key_E: self.window.zoomIn,
                        QtCore.Qt.Key_Q: self.window.zoomOut,
                        QtCore.Qt.Key_A: self.window.moveL,
                        QtCore.Qt.Key_D: self.window.moveR,
                        QtCore.Qt.Key_S: self.window.moveD,
                        QtCore.Qt.Key_W: self.window.moveU
                        }

    def doNothing(self):
        pass

    # Calls function according to pressed key
    def keyPressEvent(self, e):
        if e.isAutoRepeat():
            pass
        else:
            self.keyList.get(e.key(), self.doNothing)()


if __name__ == "__main__":
    # Start Qt applicatoin
    app = QtGui.QApplication([])
    # Create main window
    win = MainWindow()
    app.exec()
    pg.exit()