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
import math


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


# ==============================================================================
# GET IMAGE FILES TO WORK ON
# ==============================================================================
default = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera'
print('Current default base path is {}\n'.format(default))

dir_extV = raw_input('Please enter the directory(ies) housing the first image '
                     'and photometry file (e.g. '
                     '28October2016/15-11/260microsec): ')
dir_extB = raw_input('Please enter the directory(ies) housing the second image '
                     'and photometry file (e.g. '
                     '28October2016/15-11/260microsec): ')

imgV = raw_input('First image file name: ')
imgB = raw_input('Second image file name: ')
size = '64x64'#raw_input('Please input the photometry grid size (e.g. 64x64): ')
pathV = '/'.join([default, dir_extV])
pathB = '/'.join([default, dir_extB])
pathV += '/'
pathB += '/'

# Identify the image files and associated photometry files
img_fileV = pathV + imgV if imgV[-4:] == '.FIT' else pathV + imgV + '.FIT'
img_fileB = pathB + imgB if imgB[-4:] == '.FIT' else pathB + imgB + '.FIT'
phot_fileV = img_fileV[:-4] + '_photometry_' + size
phot_fileB = img_fileB[:-4] + '_photometry_' + size

print('Comparing images: {} \n and \n {}(#2)'.format(img_fileV, img_fileB))
#print('Using photometry files: {} \n and \n {}'.format(phot_fileV, phot_fileB))

dfV, img_metadataV = make_dataframe(phot_fileV, img_fileV)
dfB, img_metadataB = make_dataframe(phot_fileB, img_fileB)

# ==============================================================================
# CALCULATE THE FLUX RATIOS
# ==============================================================================

# Calculate flux ratio of image #1 to #2 (#1 is in numerator). Using vertices
#  from either dataframe since they are the same
print('Flux ratio F_v/F_b:')
FRatio_VtoB_df = DataFrame({'F Ratio': np.array((dfV['Flux'] / dfB['Flux']),
                                                dtype='float32'), 'v1': dfV['v1'],
                                'v2': dfV['v2'], 'v3': dfV['v3'],
                                'v4': dfV['v4']})

B_V_df = DataFrame({'B-V': -2.5 * np.log10(np.array((dfV['Flux'] / dfB['Flux']),
                    dtype='float32')), 'v1': dfV['v1'], 'v2': dfV['v2'],
                    'v3': dfV['v3'], 'v4': dfV['v4']})


print(B_V_df[0:13])
print()

print(B_V_df.iloc[4]['B-V'])
print(math.isnan(B_V_df.iloc[4]['B-V']))

# ==============================================================================
# PLOT STUFF (may move this later)
# ==============================================================================

# Get FITS data and save for using in matplotlib ===========================
dir_extN = raw_input('Please enter the directory(ies) housing the image taken '
                     'with no filter (ex. 28October2016/None/260microsec): ')
imgN = raw_input('No-filter image file name: ')
pathN = '/'.join([default, dir_extN, imgN])
img_fileN = pathN if pathN[-4:] == '.FIT' else pathN + '.FIT'
hdu_list = fits.open(img_fileN)
hdu_list.info()
image_data = hdu_list[0].data
hdu_list.close()

# create plot with image as background
fig1 = plt.figure(figsize=(16, 12))
ax1 = fig1.add_subplot(111)
plt.imshow(image_data, cmap='gray')
ax1.set_autoscale_on(False)

# Draw boxes on the image where there is a valid B-V value
for index, row in B_V_df.iterrows():  # iterate over the rows
    if math.isnan(row['B-V']):
        continue
    else:
        # collect the vertices for the boxes
        r1 = row['v1']
        r2 = row['v2']
        r3 = row['v3']
        r4 = row['v4']

        # including the 1st point at the end again allows the boxes to be closed
        x = np.array([r1[0], r2[0], r3[0], r4[0], r1[0]])
        y = np.array([r1[1], r2[1], r3[1], r4[1], r1[1]])

        # ax.scatter(x, y, c='lime') # toggle to turn on plotting vertices
        ax1.plot(x, y, c='lime')
        ax1.set_title('{}'.format(imgN), fontsize=20)
        ax1.get_xaxis().set_visible(False)
        ax1.get_yaxis().set_visible(False)

plt.show()

# create plot with image as background
fig2 = plt.figure(figsize=(16, 12))
ax2 = fig2.add_subplot(111)
plt.imshow(image_data, cmap='gray')
ax2.set_autoscale_on(False)

# Draw boxes on the image where B-V value is < 0, i.e. rather blue
for index, row in B_V_df.iterrows():  # iterate over the rows
    if row['B-V'] > 0:
        continue
    elif row['B-V'] < 0:
        # collect the vertices for the boxes
        r1 = row['v1']
        r2 = row['v2']
        r3 = row['v3']
        r4 = row['v4']

        # including the 1st point at the end again allows the boxes to be closed
        x = np.array([r1[0], r2[0], r3[0], r4[0], r1[0]])
        y = np.array([r1[1], r2[1], r3[1], r4[1], r1[1]])

        # ax.scatter(x, y, c='lime') # toggle to turn on plotting vertices
        ax2.plot(x, y, c='lime')
        ax2.set_title('{}'.format(imgN), fontsize=20)
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
    else:
        continue


plt.show()