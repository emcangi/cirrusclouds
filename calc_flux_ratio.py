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
from itertools import permutations as perm


def make_dataframe(phot_file, img_file):
    """
    For a given image and its photometry file, this function analyzes the
    photometry file to create a tidy Pandas data frame.

    :param phot_file: a file containing photometry for img_file
    :param img_file: the path to a particular image file
    :return: a Pandas dataframe of photometry data
    """

    # Copy polyphot data to new file without headers --------------------------
    out_file = phot_file + '_data'

    # TODO: fix this so the number of lines is determined from file, not a const
    lines = 83
    os.system("tail -n +{} {} > {}".format(lines, phot_file, out_file))

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
    headers = big_table[0]
    df = DataFrame(big_table[1:], columns=headers)
    return df, img_metadata


def get_flux_ratio(imgs, photfiles):
    """
    Generates flux ratio dataframes given a pair of images and their
    photometry files.

    :param imgs: A list of tuples, each storing a pair of image file paths
    :param photfiles: Photometry files associated with imgs
    :return:
    """

    # ==========================================================================
    # GET IMAGE FILES TO WORK ON
    # ==========================================================================
    # default = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera'
    # print('Current default base path is {}\n'.format(default))
    #
    # dir_extV = raw_input('Please enter the directory(ies) housing the first image '
    #                      'and photometry file (e.g. '
    #                      '28October2016/15-11/260microsec): ')
    # dir_extB = raw_input('Please enter the directory(ies) housing the second image '
    #                      'and photometry file (e.g. '
    #                      '28October2016/15-11/260microsec): ')
    #
    # imgV = raw_input('First image file name: ')
    # imgB = raw_input('Second image file name: ')
    # size = '64x64'#raw_input('Please input the photometry grid size (e.g. 64x64): ')
    # pathV = '/'.join([default, dir_extV])
    # pathB = '/'.join([default, dir_extB])
    # pathV += '/'
    # pathB += '/'
    #
    # # Identify the image files and associated photometry files
    # img_fileV = pathV + imgV if imgV[-4:] == '.FIT' else pathV + imgV + '.FIT'
    # img_fileB = pathB + imgB if imgB[-4:] == '.FIT' else pathB + imgB + '.FIT'
    # phot_fileV = img_fileV[:-4] + '_photometry_' + size
    # phot_fileB = img_fileB[:-4] + '_photometry_' + size
    #
    # print('Comparing images: {} \n and \n {}(#2)'.format(img_fileV, img_fileB))
    img_fileB = imgs[0]
    img_fileV = imgs[1]
    phot_fileB = photfiles[0]
    phot_fileV = photfiles[1]

    dfV, img_metadataV = make_dataframe(phot_fileV, img_fileV)
    dfB, img_metadataB = make_dataframe(phot_fileB, img_fileB)

    # ==============================================================================
    # CALCULATE THE FLUX RATIOS
    # ==============================================================================

    # Calculate flux ratio of images. Vertices from either dataframe since they
    # are the same
    FRatio_VtoB_df = DataFrame({'F Ratio': np.array((dfV['Flux'] / dfB['Flux']),
                                                    dtype='float32'),
                                'v1': dfV['v1'], 'v2': dfV['v2'],
                                'v3': dfV['v3'], 'v4': dfV['v4']})

    B_V_df = DataFrame({'B-V': -2.5 * np.log10(np.array((dfV['Flux'] / dfB['Flux']),
                        dtype='float32')), 'v1': dfV['v1'], 'v2': dfV['v2'],
                        'v3': dfV['v3'], 'v4': dfV['v4']})

    return B_V_df, img_metadataV, img_metadataB


# BATCH PROCESSING =============================================================

# Get the main folder to operate on. Should be a folder containing
# filter-titled folders
folder = raw_input('Please input the main folder to operate on, '
                   'e.g. 11February2017_MOON/set1. Should contain folders each '
                   'named for a filter: ')
default = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera' \
          '/{}/'
mypath = default.format(folder)
print(mypath)

# Make folders
paths = []
img_paths = []
phot_paths = []

# Collect a list of folders containing images, image paths and photometry paths
for (dirpath, dirnames, files) in os.walk(mypath):
    for file in files:
        if file.endswith('.FIT'):     # store image path
            img_paths.append(dirpath + '/' + file)
        elif file.endswith('64x64'):  #store path to photometry file
            phot_paths.append(dirpath + '/' + file)

# Generate combinations of filters
img_pairs = []   # img pairs, list of tuples: [(img1, img2), (img1, img3)...]
phot_pairs = []  # associated photometry files in same format

# Finds pairs of images and stores that pair along with the associated
# photometry files.
for s1, s2 in zip(perm(img_paths, 2), perm(phot_paths, 2)):
    img_pairs.append(s1)
    phot_pairs.append(s2)

print('Total pairs: {}'.format(len(img_pairs)))
count = 0
for p1, p2 in zip(img_pairs, phot_pairs):
    print('Pair {}'.format(count))
    print(img_pairs)
    print(phot_pairs)
    FRdf, metadataV, metadataB = get_flux_ratio(p1, p2)

    # Write dataframe to CSV
    fname = '{}FR_B-V_{}-{}.txt'.format(mypath, metadataB['filter1'],
                                    metadataV['filter1'])
    FRdf.to_csv(path_or_buf=fname, encoding='utf-8', na_rep='-9999')
    count += 1
