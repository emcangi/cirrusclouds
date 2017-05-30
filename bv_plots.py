#!/home/emc/anaconda3/envs/astroconda/bin/python
# -*- coding: utf-8 -*-

# ============================================================================ #
# Eryn Cangi
# Created 29 May 2017
# Script #4b of 5 to run
# Calculate the B-V index of two images given their respective photometry
# files. The photometry files should contain photometry for a hand-drawn
# region around a cloud, and for comparison, either the sun or moon.
# This script should be called from the command prompt and run interactively.
# ============================================================================ #

import os
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def extract_bv_data(bv_file_list):
    """

    :param bv_file_list:
    :return:
    """
    filters = []
    bvlist = []
    errlist = []

    for fname in bv_file_list:
        pair = re.search('(?<=V_).+-.+(?=.csv)', fname).group(0)
        filters.append(pair)

        with open(fname, 'r') as f:
            f.readline()  # the column names--we don't need these
            data_line = f.readline().split(',')
            b_v = round(float(data_line[1]), 3)
            err = round(float(data_line[3]), 3)
            bvlist.append(b_v)
            errlist.append(err)

    return filters, bvlist, errlist


def find_bv_files_in(path):
    """
    Identifies all the CSV files that contain B-V indices within a given
    image set and returns a list of the paths of those files.

    :param path: Path do a directory containing CSV files that store B-V
    information for images.
    :returns a list of paths to the CSV files
    """
    files = []
    for f in os.listdir(path):
        if f.endswith(".csv") and f.startswith('B-V'):
            files.append(os.path.join(path, f))
    return files


def autolabel(rects, vals):
    """
    Attach a text label above each bar displaying its height
    """

    # get the sign of each value
    signs = [i / abs(i) for i in vals]

    for r, s in zip(rects, signs):
        height = r.get_height()
        multiplier = 1.15 if s < 0 else 1.03    # lets us put labels under
                                                # negative-valued bars
        ax.text(r.get_x() + r.get_width() / 2., s * multiplier * height,
                '{}'.format(s * height),
                ha='center', va='bottom', fontsize=12)


# IDENTIFY CLOUD AND MOON SETS TO COMPARE ======================================

basepath = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera/'
cloudpath = raw_input('Please enter the cloud set folder, '
                      'i.e. 3January2017_1/set1/: ')
moonpath = raw_input('Please enter the moon set folder, '
                     'i.e. 10April2017_1/set1/: ')

full_cloud_path = basepath + cloudpath
full_moon_path = basepath + moonpath

# GET ALL THE B-V FILES IN CLOUD AND MOON FOLDERS ==============================
cloud_files = find_bv_files_in(full_cloud_path)
moon_files = find_bv_files_in(full_moon_path)

# COLLECT B-V AND ERROR DATA FOR CLOUDS AND MOON ===============================

filtersC, cloudbv, clouderr = extract_bv_data(cloud_files)
filtersM, moonbv, moonerr = extract_bv_data(moon_files)

if filtersC != filtersM:
    raise Exception('Filter list is not equal between cloud and moon sets. '
                    'Something has gone horribly wrong!')
else:
    pass

filters = filtersC

# CALCULATE RAW B-V DIFFERENCES BETWEEN CLOUD AND MOON DATASETS ================
diffs = []
for a, b in zip(cloudbv, moonbv):
    diffs.append(a - b)


# PLOTTING =====================================================================

ind = np.arange(len(filters))

# Plot difference of cloud B-V and moon B-V ------------------------------------
# Determines whether to color a bar gold or blue depending on the value
colors = []
for d in diffs:
    if abs(d) <= 0.05:
        colors.append('gold')
    else:
        colors.append('blue')

gold = mpatches.Patch(color='gold', label='Diff <= 0.05')

# Make the plot
width = 0.8
fig, ax = plt.subplots(figsize=(12, 10))
bars = ax.bar(ind, diffs, width, align='center', color=colors, alpha=1)
autolabel(bars, diffs)
lg = ax.legend(handles=[gold], fontsize=18)
xlbl = ax.set_xlabel('Filter combination (format: blue - visual)', fontsize=18)
ylbl = ax.set_ylabel('(B-V)$_{cloud}$ - (B-V)$_{moon}$', fontsize=18)
xt = ax.set_xticks(ind + width / 2)
xtl = ax.set_xticklabels(filters, rotation="vertical")
plt.tick_params(axis='both', which='major', labelsize=16)
titl = ax.set_title(
    'Difference in measured B-V index of cirrus clouds and the moon \n'
    'using flux, not sum', y=1,
    fontsize=22)

# adjust margins slightly
margin = max(diffs) * 0.1
x0, x1, y0, y1 = plt.axis()
plt.axis((x0 + margin,
          x1 - margin,
          y0 - margin,
          y1 + margin))

plt.show()

# Plot B-V for cloud next to B-V for moon with error bars ----------------------
width = 0.4       # the width of the bars

fig2, ax2 = plt.subplots(figsize=(20,10))
rects1 = ax2.bar(ind, cloudbv, width, color='blue', alpha=0.7, yerr=clouderr)
rects2 = ax2.bar(ind+width, moonbv, width, color='gray', alpha=0.8,
                 yerr=moonerr)
autolabel(rects1, cloudbv)
autolabel(rects2, moonbv)
lg2 = ax2.legend((rects1[0], rects2[0]), ('Clouds', 'Moon'), fontsize=18)
xlbl2 = ax2.set_xlabel('Filter combination (format: blue-visual)', fontsize=18)
ylbl2 = ax2.set_ylabel('B-V', fontsize=18)
xt2 = ax2.set_xticks(ind + width / 2)
xtl2 = ax2.set_xticklabels(filters, rotation="vertical")
plt.tick_params(axis='both', which='major', labelsize=16)
titl2 = ax2.set_title('B-V of clouds compared to moon', fontsize=22)
plt.show()