#!/home/emc/anaconda3/envs/astroconda/bin/python
# -*- coding: utf-8 -*-

def make_grid(nx, ny, size, vertices=False):
    """
    Generate grid coordinates for an image as well as coordinates of polygon
    centers. Originally by Dr. Elsa Johnson. Modified by Eryn Cangi May 2016.
    ---INPUTS---
        nx: number of boxes in x direction
        ny: " " " " y "
        size: image size given as tuple: (x, y) i.e. (width, height)
        vertices: boolean value determining whether to make a file of vertices
    ---OUTPUTS---
        <name>vertices.txt: file containing polygon vertices in relative lengths
        <name>centers.txt: file containing polygon centers
    """

    import numpy as np

    x_beg = 0             # x and y start pixels
    y_beg = 0
    x_end = size[0]       # x and y end pixels
    y_end = size[1]
    dx = x_end // nx     # set x-dimension of rectangles
    dy = y_end // ny     # " y-dimension " "

    # file saving information
    path = '/home/emc/GoogleDrive/Phys/Research/BothunLab/AnalysisFiles' \
           '/gridfiles/'
    name = '{}x{}grid_{}x{}image'.format(nx, ny, size[0], size[1])
    fpath = path + name

    print('Creating files for grid with cell size {}x{} px\n'
          'Grid size: {}x{}'.format(dx, dy, nx, ny))

    if vertices:
        # Creates list showing actual grid vertices. Not required for polyphot
        # --used for vertification with plotting
        xx = np.tile(np.arange(x_beg, x_end+dx, dx), ny+1)
        yy = np.repeat(np.arange(y_beg, y_end + dy, dy), nx + 1)
        try:
            big = np.column_stack((xx, yy))
        except:
            raise ValueError('It is required to choose a grid size such that '
                             'the number of rectangles in each direction '
                             'exactly divides the image dimensions!')
        np.savetxt(fpath+"_real_vertices.txt", big, fmt=('%4.0f', '%4.0f'))

    # Create list of polygon centers
    cx = np.tile(np.arange(x_beg + dx/2, x_end + dx/2, dx), ny)
    cy = np.repeat(np.arange(y_beg + dy / 2, y_end + dy / 2, dy), nx)
    try:
        bigc = np.column_stack((cx, cy))
    except:
        raise ValueError('Bad grid size: you must choose a grid size such that'
                         ' the number of rectangles in each direction exactly '
                         'divides the image dimensions.')
    np.savetxt(fpath+"_centers.txt", bigc, fmt=('%4.0f', '%4.0f'))
               #newline='\n;\n')

    # Create polyphot's required file 'polygons'. Given in format of 4
    # vertices RELATIVE to the centers.
    f = open(fpath+'_polygons.txt', 'w')
    f.write('0 0\n')
    f.write('{} 0\n'.format(dx))
    f.write('{} {}\n'.format(dx, dy))
    f.write('0 {}\n'.format(dy))
    f.write(';\n')
    f.close()

    print('...Files created sucessfully!')




