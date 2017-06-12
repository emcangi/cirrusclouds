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
from ast import literal_eval
import numpy as np
import re
import os
import sys

# COLLECT INFORMATION ON IMAGES TO USE =========================================
# we want to plot on top of images taken with no filter because they're
# easiest to see.

default = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera'

if sys.argv:
    dir_extN = sys.argv[1]
else:
    dir_extN = raw_input('Please enter the directory(ies) housing the image taken '
                         'with no filter (ex. '
                          '28October2016/set01/None/260microsec): ')
# automatically find the FIT image since there should be only one
nonepath = '/'.join([default, dir_extN])
for f in os.listdir(nonepath):
    if f.endswith(".FIT"):
        img_fileN = os.path.join(nonepath, f)
        break

# need these for finding the CSV files
date = re.search('\d{1,2}\D+\d{4}', dir_extN).group(0)
theset = re.search('set\d{2}', dir_extN).group(0)
if not theset:
    theset = ''
else:
    pass

# PREPARATION TO LOOP-CREATE PLOTS =============================================
# Load the FITS data for the no-filter image -----------------------------------
hdu_list = fits.open(img_fileN)
hdu_list.info()
image_data = hdu_list[0].data
hdu_list.close()

# set up the save location for created plots
saveloc = '/home/emc/GoogleDrive/Phys/Research/BothunLab/DATA/' + date + '/' \
          + theset + '/cloudfields/'
if not os.path.exists(saveloc):
    os.makedirs(saveloc)

# average cloud colors and stds
avgs = {'47-11'                  : 0.93, '47-15': 0.70, '47-LRGBgreen': 0.97,
        '47-LRGBred'             : 0.63,
        '82a-11'                 : 1.02, '82a-15': 0.79, '82a-LRGBgreen': 1.04,
        '82a-LRGBred'            : 0.71, 'LRGBblue-11': 0.87,
        'LRGBblue-15'            : 0.65,
        'LRGBblue-LRGBgreen'     : 0.89, 'LRGBblue-LRGBred': 0.57,
        'LRGBluminance-11'       : 0.92, 'LRGBluminance-15': 0.69,
        'LRGBluminance-LRGBgreen': 0.94, 'LRGBluminance-LRGBred': 0.61}

stds = {'47-11'                  : 0.27, '47-15': 0.28, '47-LRGBgreen': 0.29,
        '47-LRGBred'             : 0.27,
        '82a-11'                 : 0.06, '82a-15': 0.09, '82a-LRGBgreen': 0.21,
        '82a-LRGBred'            : 0.10, 'LRGBblue-11': 0.33,
        'LRGBblue-15'            : 0.35,
        'LRGBblue-LRGBgreen'     : 0.19, 'LRGBblue-LRGBred': 0.31,
        'LRGBluminance-11'       : 0.22, 'LRGBluminance-15': 0.24,
        'LRGBluminance-LRGBgreen': 0.13, 'LRGBluminance-LRGBred': 0.21}

filters = sorted(avgs.keys())

# LOOP THROUGH CSVs ===========================================================
csvloc = '/'.join([default, date, theset, 'BVGrid'])

for combo in filters:
    csvfile = 'B-V_{}.csv'.format(combo)
    B_V_df = pd.read_csv('/'.join([csvloc, csvfile]))

    # ignore bad values --------------------------------------------------------
    good = B_V_df.loc[B_V_df['B-V'] != -9999]
    # max_bv = math.ceil(good.max(numeric_only=True)['B-V'])
    # min_bv = math.floor(good.min(numeric_only=True)['B-V'])

    # CREATE PLOTS =============================================================

    # collect filter names for metadata etc ------------------------------------
    filter1 = combo.split('-')[0]
    filter2 = combo.split('-')[1]

    # Create figure, plot no-filter FITS image as background -------------------
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111)
    plt.imshow(image_data, cmap='gray')
    ax.set_autoscale_on(False)

    # get the cloud color and std for this particular filter combo
    av = avgs[combo]
    sig = stds[combo]
    lowBV = av - sig
    highBV = av + sig

    # iterate over the rows in the dataframe, plotting boxes -------------------
    color = 'cornflowerblue'  # np.random.rand(3, 1)
    for index, row in good.iterrows():
        if lowBV < row['B-V'] < highBV:
            # collect the vertices for the boxes
            r1 = literal_eval(row['v1'])
            r2 = literal_eval(row['v2'])
            r3 = literal_eval(row['v3'])
            r4 = literal_eval(row['v4'])

            # Create the boxes
            #  including the 1st point at the end allows the boxes to be closed
            x = np.array([r1[0], r2[0], r3[0], r4[0], r1[0]])
            y = np.array([r1[1], r2[1], r3[1], r4[1], r1[1]])

            # ax.scatter(x, y, c='lime')  # toggle to turn on plotting vertices
            ax.plot(x, y, c=color)

    titlestr = u'B-V values: {}±{} for filters {} (B), {} (V)'
    ax.set_title(titlestr.format(av, sig, filter1, filter2), fontsize=20)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # save figure --------------------------------------------------------------
    fname = 'cloudfield_{}-{}.png'.format(filter1, filter2)
    plt.savefig(saveloc+fname, bbox_inches='tight')
    plt.close()
