import numpy as np
cimport numpy as np
from libcpp cimport bool

cdef extern from "Mandelbrot.h":
    cdef cppclass Mandelbrot:
        Mandelbrot(int, int, double, double, double, double, int, int, int*) except +
        void setMaxIt(int)
        void setCol(int)
        void zoom(double)
        void moveL(int)
        void moveR(int)
        void moveD(int)
        void moveU(int)
        void setExtent(double,double)
        double xmin, xmax, ymin, ymax
   

cdef class Mandel:
    cdef Mandelbrot *thisptr
    
    def __cinit__(self, int xsize, int ysize, double xmin, double xmax, double ymin, double ymax, 
                  int maxiter, int color, np.ndarray[int, ndim=1, mode="c"] img):
        self.thisptr = new Mandelbrot(xsize, ysize, xmin, xmax, ymin, ymax, maxiter, color, &img[0])
        
    def __dealloc__(self):
        del self.thisptr
    
    def setMaxIt(self, int maxit):
        self.thisptr.setMaxIt(maxit)
    
    def setCol(self, int c):
        self.thisptr.setCol(c)
        
    def zoom(self, double factor):
        self.thisptr.zoom(factor)
    
    def moveL(self, int step):
        self.thisptr.moveL(step)
    
    def moveR(self, int step):
        self.thisptr.moveR(step)
    
    def moveD(self, int step):
        self.thisptr.moveD(step)
    
    def moveU(self, int step):
        self.thisptr.moveU(step)
    
    def setExtent(self, double x, double y):
        self.thisptr.setExtent(x,y)
    
    property xmin:
        def __get__(self): return self.thisptr.xmin
    
    property xmax:
        def __get__(self): return self.thisptr.xmax
    
    property ymin:
        def __get__(self): return self.thisptr.ymin
    
    property ymax:
        def __get__(self): return self.thisptr.ymax