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

#xmin, xmax = -0.7436438870576386, -0.7436438870166787
#ymin, ymax = 0.1318259041848326, 0.1318259042257926

def get_color_map(filename):
    try:
        x = np.fromfile(filename, dtype = np.float64, sep = ' ')
    except FileNotFoundError:
        return None
    x = x.reshape((x.size//3, 3))
    x = np.append(x, x[::-1], axis = 0)
    colmap = np.ones((len(x),4), dtype = np.float64)
    colmap[:,:3] = x
    return colmap

def generate_lut(color_map = None, colors = 2000):
    if color_map is None:
        steps = np.linspace(0,1,5)
        color_map = np.array([[0, 0, 0, 1],[1, 0, 0, 1],[1, 1, 0, 1],[1, 0, 0, 1],[0, 0, 0, 1]],
                             dtype = np.float64)
    else:
        steps = np.linspace(0, 1, color_map.shape[0])
    return pg.ColorMap(steps, color_map).getLookupTable(0.0, 1.0, colors)


# GraphicsLayoutWidget class with controls & fractal data
class FractalWidget(pg.GraphicsLayoutWidget):
    def __init__(self):
        super(FractalWidget, self).__init__()
        
        self.xsize, self.ysize = 1024, 1024
        self.xmin, self.xmax = -2, 1
        self.ymin, self.ymax =  -1.5, 1.5
        self.maxit, self.col = 200, 200
        
        self.moveSpeed = 6
        self.zoomSpeed = 1.06667
        
        # Array to hold iteration count for each pixel
        self.data = np.zeros(self.xsize*self.ysize, dtype = np.int32)
        
        # Add view box
        view = self.addViewBox(lockAspect = True, enableMouse = False, enableMenu = False, invertY = True)
        
        # Create image item
        self.ip = pg.ImageItem(border = 'w')
        lut = generate_lut(color_map=get_color_map('viridis'))
        self.ip.setLookupTable(lut, update = False)
        self.createFractal()
        view.addItem(self.ip)
        
        # Create TextItem to display fps and coordinates
        self.ti = pg.TextItem()
        self.ti.setPos(10,self.ysize)
        view.addItem(self.ti)
        
        # Connect mouse click event to function mouseEvent
        self.scene().sigMouseClicked.connect(self.mouseEvent)
        
        # Dictionary with functions to call at keypress
        self.staticKeyList = {
                              QtCore.Qt.Key_R: self.createFractal
                             }
        # Functions which get continuously called at keypress
        self.movementKeyList = {
                                QtCore.Qt.Key_E: self.zoomIn,
                                QtCore.Qt.Key_Q: self.zoomOut,
                                QtCore.Qt.Key_A: self.moveL,
                                QtCore.Qt.Key_D: self.moveR,
                                QtCore.Qt.Key_S: self.moveD,
                                QtCore.Qt.Key_W: self.moveU
                               }
        # A set of currently pressed keys
        self.pressedKeys = set()
        
        # Timer which calls update function at const framerate
        self.tickRate = 1000 / 30
        self.timer = QtCore.QTimer()
        self.timer.start(self.tickRate)
        self.timer.timeout.connect(self.move)
        self.timer.timeout.connect(self.renderText)
        
        # Init fps counter
        self.fps = 1000 / self.tickRate
        self.lastTime = time()
        self.timer.timeout.connect(self.fpsCounter)
    
    # Renders text to display
    def renderText(self):
        self.ti.setText('Fps: %.0f\tRange: (%.15f, %.15f; %.15f, %.15f)'
                        %(self.fps, self.fractal.xmin, self.fractal.xmax,
                          self.fractal.ymin, self.fractal.ymax))
    
    # Calculates current fps
    def fpsCounter(self):
        self.now = time()
        dt = self.now - self.lastTime
        self.lastTime = self.now
        s = np.clip(dt*2., 0, 1)
        self.fps = self.fps * (1-s) + (1.0/dt) * s
    
    # Calls moveX functions according to which key is pressed
    def move(self):
        for key in self.pressedKeys:
            self.movementKeyList.get(key, self.doNothing)()
    
    # Empty function to call if any other key is pressed
    def doNothing(self):
        pass
    
    # Appends key to list when pressed
    def keyPressEvent(self, e):
        if e.isAutoRepeat():
            pass
        else:
            self.pressedKeys.add(e.key())
            self.staticKeyList.get(e.key(), self.doNothing)()
    
    # Removes key from list when released
    def keyReleaseEvent(self, e):
        if e.isAutoRepeat():
            pass
        else:
            try:
                self.pressedKeys.remove(e.key())
            except KeyError:
                pass
    
    # Takes mouse click and zooms in or out at position
    def mouseEvent(self, e):
        pos = self.ip.mapFromScene(e.scenePos())
        if not (0 < pos.x() < self.xsize) or not (0 < pos.y() < self.ysize):
            return
        bts = {1:self.zoomIn, 2:self.zoomOut}
        if e.button() in bts:
            self.fractal.setExtent(pos.x(), pos.y())
            bts.get(e.button())()
    
    def updateImage(self):
        self.ip.setImage(self.data.reshape((self.ysize,self.xsize)).transpose(),
                         levels = (0,self.col))
    
    def createFractal(self):
        args = (self.xsize, self.ysize, self.xmin, self.xmax, self.ymin,
                self.ymax, self.maxit, self.col, self.data)
        self.fractal = Mandel(*args)
        self.updateImage()
    
    def zoomIn(self):
        self.fractal.zoom(1.0/self.zoomSpeed)
        self.updateImage()
    
    def zoomOut(self):
        self.fractal.zoom(self.zoomSpeed)
        self.updateImage()
        
    def moveL(self):
        self.fractal.moveL(self.moveSpeed)
        self.updateImage()
    
    def moveR(self):
        self.fractal.moveR(self.moveSpeed)
        self.updateImage()
    
    def moveD(self):
        self.fractal.moveD(self.moveSpeed)
        self.updateImage()
    
    def moveU(self):
        self.fractal.moveU(self.moveSpeed)
        self.updateImage()
    
    def setMaxIt(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Iterations', 'Set number of iterations')
        if ok:
            try:
                self.fractal.setMaxIt(int(text))
                self.updateImage()
            except ValueError:
                pass
    
    def setCol(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Colors', 'Set number of colors')
        if ok:
            try:
                self.fractal.setCol(int(text))
                self.col = int(text)
                self.updateImage()
            except ValueError:
                pass


# Main window, to have file menu & statusbar
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init()
        self.show()
        
    def init(self):
        self.resize(1024, 1024)
        self.setWindowTitle('Mandelbrot')
        
        self.window = FractalWidget()
#        self.keyPressEvent = self.window.keyPressEvent
        self.setCentralWidget(self.window)
#        self.statusBar()
        # Menubar entries
        closeApp = QtGui.QAction(QtGui.QIcon('quit.png'), 'Quit', self)
        closeApp.setShortcut('Escape')
        closeApp.setStatusTip('Exit application')
        closeApp.triggered.connect(pg.exit)
        setIter = QtGui.QAction(QtGui.QIcon('quit.png'), 'Iterations', self)
        setIter.setShortcut('I')
        setIter.setStatusTip('Set number of iterations to calculate')
        setIter.triggered.connect(self.window.setMaxIt)
        setCol = QtGui.QAction(QtGui.QIcon('quit.png'), 'Colors', self)
        setCol.setShortcut('C')
        setCol.setStatusTip('Set number of colors')
        setCol.triggered.connect(self.window.setCol)
        # Add menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(setIter)
        fileMenu.addAction(setCol)
        fileMenu.addAction(closeApp)


if __name__ == "__main__":
    # Start Qt applicatoin
    app = QtGui.QApplication([])
    # Create main window
    win = MainWindow()
    app.exec()
    pg.exit()