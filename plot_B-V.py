#!/home/emc/anaconda3/envs/astroconda/bin/python
# -*- coding: utf-8 -*-

# ============================================================================ #
# Eryn Cangi
# Created 15 January 2017
# Script #5 of 5 to run
# Plot the B-V values of two images given a dataframe containing those
# numbers. Default behavior is to plot blueish values. Option to choose which
#  B-V values within certain ranges to plot.
# This script should be called from the command prompt and run interactively.
# ============================================================================ #

import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
import math

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

# Gather the dataframe
dffile = raw_input('Please input the full path of the CSV file containing '
                   'dataframe info: ')
B_V_df = pd.read_csv('dffile')

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
