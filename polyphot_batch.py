#!/home/emc/anaconda3/envs/astroconda/bin/python
# -*- coding: utf-8 -*-

# ============================================================================ #
# Eryn Cangi
# 1 September 2016
# Script #3a of 5 to run
# Uses files_and_params.txt (a summary of various images and their sky
# values, etc) to calculate photometry for many images at once. Photometry
# files are stored in the same folder as their parent image. This is the
# script to run if you want to do automatic photometry using a grid. If you
# want to do manual photometry, run script #3b (generate_manual_cmds.py).
# To use this script, run in the terminal.
# ============================================================================ #

import ast

def prepare_params():
    """
    Grabs the parameters for each image out of a storage file and puts them
    into a list. Also generates a list of logfile names.

    Format of storage file must be:
    IMAGE   SKYVAL   SIGMA   SKYVAL ERR   EXPOSURE   FILTER 1   FILTER 2   PATH

    The 'PATH' is the path to the image file, not including the image file
    itself, and will be user- or computer- dependent.
    """

    # Identify the files_and_params file to use
    default = '/home/{}/GoogleDrive/Phys/Research/BothunLab/SkyPhotos' \
              '/NewCamera/{}/'
    un = raw_input('Please specify username of this computer account (enter to '
                   'use default of "emc"): ')
    folder = raw_input('Enter the working directory name (e.g. 2June2017): ')

    if un == '':
        un = 'emc'
    else:
        pass

    default = default.format(un, folder)
    param_file = default + 'files_and_params.txt'

    # Read in the param_file and put values in a list. value order is:
    # IMAGE  SKYVAL  SIGMA  SKYVAL ERR  EXPOSURE  FILTER 1  FILTER 2  PATH
    # RESOLUTION
    image_data = []

    with open(param_file, 'r') as f:
        throwaway = f.readline()  # skip the first line which is a comment
        for line in f:
            ln = line.strip().split('\t')
            if ln:
                image_data.append([ln[0], ln[1], ln[2], ln[3], ln[4], ln[5],
                                   ln[6], ln[7], ln[8]])

    # Generate some logfile names for photometry output
    logs = ['{}_photometry'.format(x[0][:-4]) for x in image_data]

    return image_data, logs


def do_photometry():
    """
    Do photometry in batch mode.
    Script will prompt for the locations of the grid files and the location
    of the parameter file.

    Output:
    Files for each image with extension '_photometry' and data inside,
    which are placed in the same directory as their parent image.
    """

    from pyraf import iraf
    from os import walk
    import re

    # Retrieves image parameters from a stored file ----------------------------
    image_data, lognames = prepare_params()

    # Identify the grid files --------------------------------------------------
    path = '/home/emc/GoogleDrive/Phys/Research/BothunLab/AnalysisFiles' \
              '/gridfiles/'

    # print('Available grid files: ')
    #
    # for (dirpath, dirnames, gfile) in walk(path):
    #     print(gfile)

    gsize = raw_input('Enter the grid size to use (ex: 10x10): ')
    # dim1 = re.search('[0-9]+(?=x)', gsize).group(0)
    # dim2 = re.search('(?<=x)[0-9]+', gsize).group(0)
    #area = int(dim1) * int(dim2)

    # adjust lognames if grid size is not 10x10 to avoid overwriting files
    # lognames = [i+'_'+gsize for i in lognames]

    # Loops through images and call polyphot for each --------------------------
    print('\nNow doing photometry. Please wait...\n')

    for image, logname in zip(image_data, lognames):
        filename = image[0]
        sky = image[1]
        sig = image[2]
        err = image[3]
        exp = image[4]
        filter1 = image[5]
        filter2 = image[6]
        im_path = image[7]
        res = ast.literal_eval(image[8])  # stores this as a tuple

        # TODO specify resolution for ease and explicitness
        xdim = res[0]
        ydim = res[1]

        # TODO handle 1024x768
        if xdim == 1024 and ydim == 768:
            gsize = '8x8'

        # TODO update logname
        logn = '_'.join([logname, gsize])

        # TODO fix
        # specify names of grid files to use
        coordfile = gsize + 'grid_{}x{}image_centers.txt'.format(xdim, ydim)
        polygonfile = gsize + 'grid_{}x{}image_polygons.txt'.format(xdim, ydim)

        print('Processing image {}'.format(filename))
        # call the task, then write the error to the logfile at the end.
        iraf.polyphot(im_path+filename, coords=path+coordfile,
                      output=im_path+logn, polygons=path+polygonfile,
                      interactive='no', skyvalue=sky, sigma=sig, itime=exp,
                      ifilter=', '.join([filter1, filter2]),
                      verify='no')

        gsize = '10x10'

    print('Photometry complete!')

    return None

do_photometry()