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
import matplotlib.patches as mpatches
from astropy.io import fits
from ast import literal_eval
import numpy as np
import re
import os
import sys

# COLLECT INFORMATION ON IMAGES TO USE =========================================
# we want to plot on top of images taken with no filter because they're
# easiest to see.

default = '/home/{}/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera'
un = sys.argv[1]
default = default.format(un)

dir_extN = sys.argv[2]

# dir_extN = raw_input('Please enter the directory(ies) housing the image '
#                      'taken with no filter (ex. '
#                      '28October2016/set01/None/260microsec): ')

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
header = hdu_list.info(output=False)
image_data = hdu_list[0].data

dim = header[0][4]  # collect image dimensions so we know the plot limits
xmax = dim[0]
ymax = dim[1]

hdu_list.close()

# set up the save location for created plots
saveloc = '/home/{}/GoogleDrive/Phys/Research/BothunLab/DATA/'.format(un) \
          + date + '/' + theset + '/cloudfields/'
if not os.path.exists(saveloc):
    os.makedirs(saveloc)

# average cloud colors and stds
# updated on 12 June 2017
avgs = {'47-11'                  : 0.94, '47-15': 0.73, '47-LRGBgreen': 0.91,
        '47-LRGBred'             : 0.67,
        '82a-11'                 : 0.98, '82a-15': 0.78, '82a-LRGBgreen': 0.90,
        '82a-LRGBred'            : 0.71, 'LRGBblue-11': 0.89,
        'LRGBblue-15'            : 0.69,
        'LRGBblue-LRGBgreen'     : 0.81, 'LRGBblue-LRGBred': 0.62,
        'LRGBluminance-11'       : 0.92, 'LRGBluminance-15': 0.72,
        'LRGBluminance-LRGBgreen': 0.84, 'LRGBluminance-LRGBred': 0.65}

stds = {'47-11'                  : 0.30, '47-15': 0.35, '47-LRGBgreen': 0.27,
        '47-LRGBred'             : 0.37,
        '82a-11'                 : 0.12, '82a-15': 0.20, '82a-LRGBgreen': 0.28,
        '82a-LRGBred'            : 0.26, 'LRGBblue-11': 0.39,
        'LRGBblue-15'            : 0.49,
        'LRGBblue-LRGBgreen'     : 0.20, 'LRGBblue-LRGBred': 0.45,
        'LRGBluminance-11'       : 0.30, 'LRGBluminance-15': 0.35,
        'LRGBluminance-LRGBgreen': 0.19, 'LRGBluminance-LRGBred': 0.29}

filters = sorted(avgs.keys())

# LOOP THROUGH CSVs ===========================================================
csvloc = '/'.join([default, date, theset, 'BVGrid'])

for combo in filters:
    csvfile = 'B-V_{}.csv'.format(combo)
    B_V_df = pd.read_csv('/'.join([csvloc, csvfile]))

    # ignore bad values --------------------------------------------------------
    good = B_V_df.loc[B_V_df['B-V'] != -9999]

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
    color = 'cornflowerblue'
    for index, row in good.iterrows():
        if lowBV < row['B-V'] < highBV:
            # collect the vertices for the boxes
            r1 = literal_eval(row['v1'])
            r2 = literal_eval(row['v2'])
            r3 = literal_eval(row['v3'])
            r4 = literal_eval(row['v4'])

            p = mpatches.Polygon(np.array([r1, r2, r3, r4]), closed=True,
                                 color='#6495ED', alpha=0.15)  #TODO: New
            ax.add_patch(p)
            # Create the boxes
            #  including the 1st point at the end allows the boxes to be closed
            x = np.array([r1[0], r2[0], r3[0], r4[0], r1[0]])
            y = np.array([r1[1], r2[1], r3[1], r4[1], r1[1]])

            # ax.scatter(x, y, c='lime')  # toggle to turn on plotting vertices
            ax.plot(x, y, c=color)

    ax.autoscale(enable=True, axis='both', tight=True)
    ax.set_xlim([0, xmax])
    ax.set_ylim([0, ymax])

    titlestr = u'B-V values: {}±{} for filters {} (B), {} (V)'
    ax.set_title(titlestr.format(av, sig, filter1, filter2), fontsize=20)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # save figure --------------------------------------------------------------
    fname = 'cloudfield_{}-{}.png'.format(filter1, filter2)
    plt.savefig(saveloc+fname, bbox_inches='tight')
    plt.close()
