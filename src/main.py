#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 11:03:55 2015

@author: yboetz
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from qtwindow import MainWindow


if __name__ == "__main__":
    # Start Qt applicatoin
    app = QtGui.QApplication([])
    # Create main window
    win = MainWindow()
    app.exec()
    pg.exit()
