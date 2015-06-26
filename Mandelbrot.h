#include <iostream>
#include <immintrin.h>
#include <chrono>


inline __m128i modps_epi32(__m128 x, __m128 col)
    {
    __m128 div = _mm_div_ps(x,col);
    __m128 res = _mm_round_ps(div,_MM_FROUND_TO_ZERO);
    res = _mm_mul_ps(res,col);
    res = _mm_sub_ps(x,res);

    return _mm_cvtps_epi32(res);
    }

void iterate(double xmin, double xmax, double ymin, double ymax, int xsize, int ysize, int maxit, int col, int* image)
    {
    double dx = (xmax - xmin) / xsize;
    double dy = (ymax - ymin) / ysize;
    int width = xsize / 4;
    
    __m128 vcol = _mm_set1_ps((float)col);
    __m256d vdx = _mm256_set1_pd(dx);
    __m256d vdy = _mm256_set1_pd(-dy);
    __m256d vxmin = _mm256_set1_pd(xmin);
    __m256d vymax = _mm256_set1_pd(ymax);
    __m256d one = _mm256_set1_pd(1.0);
    __m256d two = _mm256_set1_pd(2.0);
    __m256d four = _mm256_set1_pd(4.0);
    
    #pragma omp parallel for schedule(dynamic)
    for(int j = 0; j < ysize; j++)
        {
        __m256d cim = _mm256_fmadd_pd(_mm256_set1_pd(j),vdy,vymax);
        __m256d incr = _mm256_setr_pd(0.0,1.0,2.0,3.0);
        int ywidth = j*xsize;
        
        for(int i = 0; i < width; i++)
            {
            __m256d cre = _mm256_fmadd_pd(incr,vdx,vxmin);
            incr = _mm256_add_pd(incr,four);
            
            __m256d re = _mm256_xor_pd(one,one); // Set to 0
            __m256d im = _mm256_xor_pd(one,one);
            __m256d re_2 = _mm256_xor_pd(one,one);
            __m256d im_2 = _mm256_xor_pd(one,one);
            
            __m256d counter = _mm256_xor_pd(one,one);

            int test;
            int k = 0;
            do
                {
                im = _mm256_mul_pd(im,re);
                im = _mm256_fmadd_pd(two,im,cim);
                re = _mm256_sub_pd(re_2,im_2);
                re = _mm256_add_pd(re,cre);
                re_2 = _mm256_mul_pd(re,re);
                im_2 = _mm256_mul_pd(im,im);
                
                __m256d which = _mm256_add_pd(re_2,im_2);
                which = _mm256_cmp_pd(which,four,_CMP_LT_OQ);
                test = _mm256_movemask_pd(which);
                
                which = _mm256_and_pd(which,one);
                counter = _mm256_add_pd(counter,which);
                }
            while((test != 0) && (++k < maxit));

            _mm_store_si128((__m128i*)(image + ywidth + 4*i),modps_epi32(_mm256_cvtpd_ps(counter),vcol));
            }
        }
    }


class Mandelbrot
    {
    public:
        int xsize, ysize;
        double xmin, xmax, ymin, ymax;
        int maxit, col;
        int* image;
        
        Mandelbrot(int, int, double, double, double, double, int, int, int*);
        void setMaxIt(int);
        void setCol(int);
        void zoom(double);
        void moveL(int);
        void moveR(int);
        void moveD(int);
        void moveU(int);
    };

Mandelbrot::Mandelbrot(int x, int y, double xmi, double xma, double ymi, double yma, int max, int c, int* img)
    {
    xsize = x;
    ysize = y;
    xmin = xmi;
    xmax = xma;
    ymin = ymi;
    ymax = yma;
    maxit = max;
    col = c;
    
    image = img;
    
    iterate(xmin, xmax, ymin, ymax, xsize, ysize, maxit, col, image);
    }

void Mandelbrot::setMaxIt(int it)
    {
    maxit = it;
    iterate(xmin, xmax, ymin, ymax, xsize, ysize, maxit, col, image);
    }

void Mandelbrot::setCol(int c)
    {
    col = c;
    iterate(xmin, xmax, ymin, ymax, xsize, ysize, maxit, col, image);
    }

void Mandelbrot::zoom(double factor)
    {
    double dx = 0.5 * (xmax - xmin) * (factor - 1.0);
    double dy = 0.5 * (ymax - ymin) * (factor - 1.0);
    xmin -= dx;
    xmax += dx;
    ymin -= dy;
    ymax += dy;
    
    iterate(xmin, xmax, ymin, ymax, xsize, ysize, maxit, col, image);
    }

void Mandelbrot::moveL(int step)
    {
    if(step == 0) return;
    
    int stepSize = 4*step;
//    if(stepSize > xsize) return;
    
    double dx = (xmax - xmin) / xsize * stepSize;
    xmin -= dx;
    xmax -= dx;
    
    int* tmp = new int[ysize * stepSize];
    
    iterate(xmin, xmin + dx, ymin, ymax, stepSize, ysize, maxit, col, tmp);
    
    int xstep = xsize/4 - step + 1;
    for(int j = 0; j < ysize; j++)
        {
        int ywidth = j*xsize;
        for(int i = 1; i < xstep; i++)
            {
            int _i = xsize - 4*i;
            _mm_store_si128((__m128i*)(image + ywidth + _i), _mm_load_si128((__m128i*)(image + ywidth + _i - stepSize)));
            }
        for(int i = 0; i < step; i++)
            {
            int _i = 4*i;
            _mm_store_si128((__m128i*)(image + ywidth + _i), _mm_load_si128((__m128i*)(tmp + j*stepSize + _i)));
            }
        }
    
    delete[] tmp;
    }

void Mandelbrot::moveR(int step)
    {
    if(step == 0) return;
    
    int stepSize = 4*step;
//    if(stepSize > xsize) return;
    
    double dx = (xmax - xmin) / xsize * stepSize;
    xmin += dx;
    xmax += dx;
    
    int* tmp = new int[ysize * stepSize];
    
    iterate(xmax - dx, xmax, ymin, ymax, stepSize, ysize, maxit, col, tmp);
    
    int xstep = xsize/4 - step;
    for(int j = 0; j < ysize; j++)
        {
        int _j = j*xsize;
        for(int i = 0; i < xstep; i++)
            {
            int _i = 4*i;
            _mm_store_si128((__m128i*)(image + _j + _i), _mm_load_si128((__m128i*)(image + _j + _i + stepSize)));
            }
        for(int i = xstep; i < xstep + step; i++)
            {
            int _i = 4*i;
            _mm_store_si128((__m128i*)(image + _j + _i), _mm_load_si128((__m128i*)(tmp + j*stepSize + _i - xsize + stepSize)));
            }
        }
    
    delete[] tmp;
    }

void Mandelbrot::moveD(int step)
    {
    if(step == 0) return;
    
    int stepSize = 4*step;
//    if(stepSize > xsize) return;
    
    double dy = (ymax - ymin) / ysize * stepSize;
    ymin -= dy;
    ymax -= dy;
    
    int* tmp = new int[xsize * stepSize];
    
    iterate(xmin, xmax, ymin, ymin + dy, xsize, stepSize, maxit, col, tmp);
    
    int xstep = xsize/4;
    int ystep = ysize - stepSize;
    int stepWidth = stepSize*xsize;
    int stepWidthtmp = ystep*xsize;
    for(int j = 0; j < ystep; j++)
        {
        int _j = j*xsize;
        for(int i = 0; i < xstep; i++)
            {
            int _i = 4*i;
            _mm_store_si128((__m128i*)(image + _j + _i), _mm_load_si128((__m128i*)(image + _j + _i + stepWidth)));
            }
        }
    for(int j = ystep; j < ysize; j++)
        {
        int _j = j*xsize; 
        for(int i = 0; i < xstep; i++)
            {
            int _i = 4*i;
            _mm_store_si128((__m128i*)(image + _j + _i), _mm_load_si128((__m128i*)(tmp + _j - stepWidthtmp + _i)));
            }
        }
    
    delete[] tmp;
    }

void Mandelbrot::moveU(int step)
    {
    if(step == 0) return;
    
    int stepSize = 4*step;
//    if(stepSize > xsize) return;
    
    double dy = (ymax - ymin) / ysize * stepSize;
    ymin += dy;
    ymax += dy;
    
    int* tmp = new int[xsize * stepSize];
    
    iterate(xmin, xmax, ymax - dy, ymax, xsize, stepSize, maxit, col, tmp);
    
    int xstep = xsize/4;
    int ystep = ysize - stepSize + 1;
    int stepWidth = stepSize*xsize;
    for(int j = 1; j < ystep; j++)
        {
        int _j = (ysize-j)*xsize;
        for(int i = 0; i < xstep; i++)
            {
            int _i = 4*i;
            _mm_store_si128((__m128i*)(image + _j + _i), _mm_load_si128((__m128i*)(image + _j + _i - stepWidth)));
            }
        }
    for(int j = 0; j < stepSize; j++)
        {
        int _j = j*xsize; 
        for(int i = 0; i < xstep; i++)
            {
            int _i = 4*i;
            _mm_store_si128((__m128i*)(image + _j + _i), _mm_load_si128((__m128i*)(tmp + _j + _i)));
            }
        }
    
    delete[] tmp;
    }
