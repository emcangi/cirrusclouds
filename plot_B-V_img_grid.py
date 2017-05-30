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
import math
import os

# COLLECT INFORMATION ON IMAGES TO USE =========================================
default = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera'
dir_extN = raw_input('Please enter the directory(ies) housing the image taken '
                     'with no filter (ex. 28October2016/None/260microsec): ')
imgN = raw_input('No-filter image file name: ')
pathN = '/'.join([default, dir_extN, imgN])
img_fileN = pathN if pathN[-4:] == '.FIT' else pathN + '.FIT'

# OPEN FLUX RATIO DATAFRAME ====================================================
dffile = raw_input('Please input the full path of the CSV file containing '
                   'dataframe info: ')
csvonly = re.search(r'FR.+.csv$', dffile).group(0)   # collects csv file name
setpath = re.search(r'.+(?=FR.+.csv$)', dffile).group(0)  # where to save plots
B_V_df = pd.read_csv(dffile)

# find min, max B-V values -----------------------------------------------------
good = B_V_df.loc[B_V_df['B-V'] != -9999]
max_bv = math.ceil(good.max(numeric_only=True)['B-V'])
min_bv = math.floor(good.min(numeric_only=True)['B-V'])

# CREATE PLOTS =================================================================

# Load the FITS data for the no-filter image -----------------------------------
hdu_list = fits.open(img_fileN)
hdu_list.info()
image_data = hdu_list[0].data
hdu_list.close()

# set max, min of B-V and the window size for plotting -------------------------
resolution = 0.5
cutoffs = np.arange(min_bv, max_bv, resolution)

# collect filter names from CSV file name --------------------------------------
csvonly = re.sub('FR_B-V_', '', csvonly)
csvonly = re.sub('.csv', '', csvonly)
filter1 = re.search(r'.+(?=-)', csvonly).group(0)
filter2 = re.search(r'(?<=-).+', csvonly).group(0)

# create a directory for the plots to live -------------------------------------
imgpath = setpath + 'plots/' + '{}-{}/'.format(filter1, filter2)
if not os.path.exists(imgpath):
    os.makedirs(imgpath)

for i in range(len(cutoffs) - 1):
    # Create figure, plot no-filter FITS image as background -------------------
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111)
    plt.imshow(image_data, cmap='gray')
    ax.set_autoscale_on(False)

    # iterate over the rows in the dataframe, plotting boxes -------------------
    color = np.random.rand(3, 1)
    for index, row in good.iterrows():
        if cutoffs[i] < row['B-V'] < cutoffs[i+1]:
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

    ax.set_title('B-V values between {} and {} for filters {} (B) and {} ('
                 'V)'.format(cutoffs[i], cutoffs[i+1], filter1, filter2),
                 fontsize=20)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # save figure --------------------------------------------------------------
    fname = 'B-V_{}to{}_filters_{}_and_{}.png'.format(cutoffs[i], cutoffs[i+1],
                                                      filter1, filter2)
    plt.savefig(imgpath+fname, bbox_inches='tight')
    plt.close()
