
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 10:30:16 2018

@author: yboetz
"""

import numpy as np
import pyqtgraph as pg


#xmin, xmax = -0.7436438870576386, -0.7436438870166787
#ymin, ymax = 0.1318259041848326, 0.1318259042257926

def get_color_map(filename):
    try:
        x = np.fromfile(filename, dtype=np.float64, sep=' ')
    except FileNotFoundError:
        return None
    x = x.reshape((x.size//3, 3))
    x = np.append(x, x[::-1], axis=0)
    colmap = np.ones((len(x), 4), dtype=np.float64)
    colmap[:,:3] = x
    return colmap

def generate_lut(color_map=None, colors=2000):
    if color_map is None:
        steps = np.linspace(0, 1, 5)
        color_map = np.array([[0, 0, 0, 1], [1, 0, 0, 1], [1, 1, 0, 1], [1, 0, 0, 1], [0, 0, 0, 1]],
                             dtype=np.float64)
    else:
        steps = np.linspace(0, 1, color_map.shape[0])
    return pg.ColorMap(steps, color_map).getLookupTable(0.0, 1.0, colors)
