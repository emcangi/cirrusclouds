# ============================================================================ #
# Calculate the flux ratio of two images given their respective photometry
# files. Returns the flux ratios by grid cell which can then be plotted as
# required.
#
# This script should be called from the command prompt and run interactively.
#
# Eryn Cangi
# Created 15 January 2017
# ============================================================================ #

import os
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits


def make_dataframe(phot_file, img_file):
    """
    For a given image and its photometry file, this function analyzes the
    photometry file to create a tidy Pandas data frame and also imports the
    image FITS data into an object that can be used with matplotlib to plot.

    :param phot_file: a file containing photometry for img_file
    :param img_file: the path to a particular image file
    :return: a Pandas dataframe of photometry data and an image data object
                for use with matplotlib
    """

    # Copy polyphot data to new file without headers --------------------------
    out_file = phot_file + '_data'
    print('I am using {}'.format(out_file))

    # TODO: fix this so the number of lines is determined from file, not a const
    lines = 83
    os.system("tail -n +{} {} > {}".format(lines, phot_file, out_file))

    # Get FITS data and save for using in matplotlib ===========================
    # hdu_list = fits.open(img_file)
    # hdu_list.info()
    # image_data = hdu_list[0].data
    # hdu_list.close()

    # Construct initial lists of information from the photometry file ==========
    ln_cnt = 1  # we have to keep track since Python doesn't
    data = []
    grid = []
    cell = 0  # keeps track of which cell we are on; order is how the cells
    # appear in the photometry file.

    with open(out_file, 'r') as f:
        for line in f:

            # First grab sky background, filters and grid size -- only need
            # to do this once but there's not really a more elegant way.
            if ln_cnt == 3:
                msky = float(line.split()[0])  # gets magnitude of sky
                sigma = float(line.split()[1])  # gets sigma
            if ln_cnt == 4:
                filter1 = line.split()[2].split(',')[0]
                filter2 = line.split()[2].split(',')[1]
            if ln_cnt == 6:
                gridsize = line.split()[0]
                img_metadata = {'msky': msky, 'sigma': sigma, 'filter1': filter1,
                                'filter2': filter2, 'gridsize': gridsize}

            # check what the last digit of the line number is
            last_digit = ln_cnt % 10

            # Lines ending in 5 are the ones with data
            if ln_cnt % 5 == 0 and last_digit != 0:
                data.append(line)

            # Lines ending in list the vertices of the grid cell
            if last_digit in [7, 8, 9, 0]:
                # start a new sublist if it is a new cell
                if last_digit == 7:
                    grid.append([])
                # append the items to the sublist
                grid[cell].append(line)
                # signify that we have finished logging the grid cell vertices
                if last_digit == 0:
                    cell += 1
            ln_cnt += 1

    # Construct data display table =============================================

    big_table = [['Counts', 'Area(pixels)', 'Flux', 'v1', 'v2', 'v3', 'v4']]

    for e1, e2 in zip(data, grid):
        datum = e1.split()  # extract useful info
        del datum[-1]  # gets rid of junk characters added to the line
        datum = datum[:3]  # get rid of magg, merr, pier, perror (unneeded)
        datum = [float(i) for i in datum]

        # appends vertices in neat ordered-pair format
        for el in e2:
            # witchcraft to append a list of floats for the coordinates
            datum.append([float(i) for i in el.strip().split()[:2]])

        # add data and vertices to a big table
        big_table.append(datum)

    # Make a Pandas dataframe ==================================================
    print(big_table[0:30])
    headers = big_table[0]
    df = DataFrame(big_table[1:], columns=headers)

    return df, 'trash', img_metadata#image_data, img_metadata


# ==============================================================================
# GET IMAGE FILES TO WORK ON
# ==============================================================================
default = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera'
print('Current default base path is {}\n'.format(default))

dir_ext1 = raw_input('Please enter the directory(ies) housing the first image '
                     'and photometry file (e.g. '
                     '28October2016/15-11/260microsec): ')
dir_ext2 = raw_input('Please enter the directory(ies) housing the second image '
                     'and photometry file (e.g. '
                     '28October2016/15-11/260microsec): ')

img1 = raw_input('First image file name: ')
img2 = raw_input('Second image file name: ')
size = '64x64'#raw_input('Please input the photometry grid size (e.g. 64x64): ')
path1 = '/'.join([default, dir_ext1])
path2 = '/'.join([default, dir_ext2])
path1 += '/'
path2 += '/'

# Identify the image files and associated photometry files
img_file1 = path1+img1 if img1[-4:] == '.FIT' else path1+img1+'.FIT'
img_file2 = path2+img2 if img2[-4:] == '.FIT' else path2+img2+'.FIT'
phot_file1 = img_file1[:-4] + '_photometry_' + size
phot_file2 = img_file2[:-4] + '_photometry_' + size

print('Comparing images: {} \n and \n (#2)'.format(img_file1, img_file2))
print('Using photometry files: {} \n and \n {}'.format(phot_file1, phot_file2))

df1, img_data1, img_metadata1 = make_dataframe(phot_file1, img_file1)
df2, img_data2, img_metadata2 = make_dataframe(phot_file2, img_file2)

print(df1['Flux'][0:30])
print(img_metadata1)
print(df2['Flux'][0:1000])
print(img_metadata2)
# ==============================================================================
# CALCULATE THE FLUX RATIOS
# ==============================================================================

# Calculate flux ratio of image #1 to #2 (#1 is in numerator). Using vertices
#  from either dataframe since they are the same
f_ratio_1to2_df = DataFrame({'F Ratio': np.array((df1['Flux'] / df2['Flux']),
                             dtype='float32'),
                                'v1': df1['v1'],
                                'v2': df1['v2'],
                                'v3': df1['v3'],
                                'v4': df1['v4']})

# Calculate the inverse, #2 to #1
f_ratio_2to1_df = DataFrame(1/f_ratio_1to2_df['F Ratio'])

print(f_ratio_1to2_df[0:30])
print()
print(f_ratio_2to1_df[0:30])


