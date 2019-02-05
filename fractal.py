from __future__ import division

from numba import vectorize

import numpy as np
import matplotlib
matplotlib.use('qt4agg')
import matplotlib.pyplot as plt

from matplotlib import colors

from math import log

from scipy.misc import imresize

mandel_sig = 'float32(float32, float32, float32, float32, float32, uint32, uint32, uint32)'
julia_sig = 'float32(float32,float32,float32,float32,float32,uint32,uint32,uint32,float32,float32)'

@vectorize([mandel_sig], target='cuda')
def mandel(tid,min_x,max_x,min_y,max_y,width,height,iters):
    pixel_size_x = (max_x - min_x) / width
    pixel_size_y = (max_y  - min_y) / height
    
    x = tid % width
    y = tid / width
    real = min_x + x*pixel_size_x
    imag = min_y + y*pixel_size_y
    c = complex(real,imag)
    z = 0.0j
    h = 2.0 ** 40
    log_h = log(log(h))/log(2.0)
    for i in range(iters):
        z = z*z + c
        az = (z.real*z.real + z.imag*z.imag)
        if az >= h:
            return float(i) - log(log(az))/log(2.0) + log_h
    return 0.0


@vectorize([julia_sig], target='cuda')
def julia(tid,min_x,max_x,min_y,max_y,width,height,iters,real_c,imag_c):
    pixel_size_x = (max_x - min_x) / width
    pixel_size_y = (max_y  - min_y) / height
    
    x = tid % width
    y = tid / width
    real = min_x + x*pixel_size_x
    imag = min_y + y*pixel_size_y
    z = complex(real,imag)
    c = complex(real_c,imag_c)
    h = 2.0 ** 40
    log_h = log(log(h))/log(2.0)
    for i in range(iters):
        z = z*z + c
        az = (z.real*z.real + z.imag*z.imag)
        if az >= h:
            return float(i) - log(log(az))/log(2.0) + log_h
    return 0.0

def lighting(M,upsample,cmap='gnuplot2'):
    light = colors.LightSource(180,10)
    M = light.shade(M, cmap=plt.cm.get_cmap(cmap), vert_exag=1.25,
            norm=colors.PowerNorm(0.3), blend_mode='hsv', 
            dx=int(upsample), dy=int(upsample))
    return M

def create_fractal(min_x,max_x,min_y,max_y,width,height,iters,
                   real_c=None,imag_c=None,upsample=1,fancy=True,
                   cmap='gnuplot2',debug=False):
    
    min_x, max_x, min_y, max_y = float(min_x), float(max_x), float(min_y), float(max_y)
    try:
        real_c, imag_c = float(real_c), float(imag_c)
    except:
        pass
    upsample = float(upsample)
    ogwidth,ogheight = width,height
    width,height = int(upsample*width),int(upsample*height)
    cmap = str(cmap).strip()
    tids = np.arange(width*height, dtype=np.float32)
    
    
    if real_c is not None and imag_c is not None:
        M = julia(tids,np.float32(min_x),np.float32(max_x),np.float32(min_y),
                     np.float32(max_y),np.uint32(width),np.uint32(height),
                     np.uint32(iters),np.float32(real_c),
                     np.float32(imag_c)).reshape((height,width))        
    else:
        M = mandel(tids,np.float32(min_x),np.float32(max_x),np.float32(min_y),
                     np.float32(max_y),np.uint32(width),np.uint32(height),
                     np.uint32(iters)).reshape((height,width))
    if fancy == 0:
        M = lighting(M,upsample,cmap)
    else:
        cmap = plt.cm.ScalarMappable(cmap=cmap)

        M = cmap.to_rgba(M)

    if upsample != 1:
        M = imresize(M,(ogheight,ogwidth),interp='bicubic')
    
    if debug:
        plt.imsave('debug.png', M)

    return M

def calculate_new_coords(old_coords,roi_coords,width,height):
    min_x, max_x, min_y, max_y = old_coords
    min_x, max_x, min_y, max_y = float(min_x), float(max_x), float(min_y), float(max_y)
    pixel_size_x = (max_x - min_x) / width
    pixel_size_y = (max_y  - min_y) / height
    return [min_x + pixel_size_x*roi_coords[0], min_x + pixel_size_x*roi_coords[1],
            max_y - pixel_size_y*roi_coords[3], max_y - pixel_size_y*roi_coords[2]]

def test_frac():
    center_x = -0.761574
    center_y = -0.0847596
    zoom_val = 1/625.
    x_min = center_x - zoom_val
    x_max = center_x + zoom_val
    y_min = center_y - zoom_val
    y_max = center_y + zoom_val

    
    print x_min, x_max, y_min, y_max
    
    
    width = 1920        
    height = 1080
    


    M = create_fractal(x_min,x_max,y_min,y_max,width,height,500,
                       fancy=False,upsample=2.5,cmap='jet')
    
    
    
    
    plt.imsave('testnormal.png', M)

#test_frac()