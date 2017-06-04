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
    :return: a list of format ['filtercombo', b-v, b-v error]
    """
    thelist = []

    for fname in bv_file_list:
        pair = re.search('(?<=V_).+-.+(?=.csv)', fname).group(0)
        sublist = []
        sublist.append(pair)

        with open(fname, 'r') as f:
            f.readline()  # the column names--we don't need these
            data_line = f.readline().split(',')
            b_v = round(float(data_line[1]), 3)
            err = round(float(data_line[3]), 3)
            sublist.append(b_v)
            sublist.append(err)
        thelist.append(sublist)

    return thelist


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
    files = sorted(files)
    return files


def autolabel(rects, vals):
    """
    Attach a text label above each bar displaying its height. For vertical
    bar plots.

    :param rects: the bars in the given bar plot
    :param vals: actual values used to plot the bars, needed to display
    negative labels
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

def autolabelh(rects, vals):
    """
    Attach a text label next to each bar displaying its width. For horizontal
    bar plots.

    :param rects: the bars in the given bar plot
    :param vals: actual values used to plot the bars, needed to display
    negative labels
    """
    # get the sign of each value
    signs = [i / abs(i) for i in vals]

    for r, s in zip(rects, signs):
        width = r.get_width()
        adj = max(vals) / 15
        ax.text(s * (width + adj), r.get_y() + r.get_height() / 2.,
                '{}'.format(round(s * width, 3)),
                ha='center', va='center', fontsize=12)


# IDENTIFY CLOUD AND MOON SETS TO COMPARE ======================================

# collect path information to files
basepath = '/home/{}/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera/'
un = raw_input('Please specify username of this computer account: ')
basepath = basepath.format(un)
cloudpath = raw_input('Please enter the cloud set folder, '
                      'i.e. 3January2017/set01/: ')
moonpath = raw_input('Please enter the moon set folder, '
                     'i.e. 10April2017_MOON/set01/: ')

full_cloud_path = basepath + cloudpath
full_moon_path = basepath + moonpath

# get the dates only--used for putting labels in the plots
clouddate = re.search('([0-9]+[A-Za-z]+[0-9]+)', cloudpath).group(0)
moondate = re.search('([0-9]+[A-Za-z]+[0-9]+)', moonpath).group(0)

# GET ALL THE B-V FILES IN CLOUD AND MOON FOLDERS ==============================
cloud_files = find_bv_files_in(full_cloud_path)
moon_files = find_bv_files_in(full_moon_path)

# COLLECT B-V AND ERROR DATA FOR CLOUDS AND MOON ===============================

clouddata = extract_bv_data(cloud_files)
moondata = extract_bv_data(moon_files)

# this may seem excessive and unpythonic, but it deals with the fact that
# sometimes there isn't a B-V value for two given images of clouds because
# one of them may have had a negative flux.
filters = []
cloudbv = []
clouderr = []
moonbv = []
moonerr = []

for c in clouddata:
    for m in moondata:
        if c[0] == m[0]:
            filters.append(c[0])
            cloudbv.append(c[1])
            clouderr.append(c[2])
            moonbv.append(m[1])
            moonerr.append(m[2])


# CALCULATE RAW B-V DIFFERENCES BETWEEN CLOUD AND MOON DATASETS ================

diffs = []
for a, b in zip(cloudbv, moonbv):
    diffs.append(a - b)

# PLOTTING =====================================================================

# create and save plots in DATA, so they aren't buried in the photo folders
ind = np.arange(len(filters))
saveloc = '/home/{}/GoogleDrive/Phys/Research/BothunLab/DATA/'.format(un) + \
          cloudpath

if not os.path.exists(saveloc):
    os.makedirs(saveloc)

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
h = 0.8
fig, ax = plt.subplots(figsize=(12, 10))
bars = ax.barh(ind, diffs, h, align='center', color=colors, alpha=1)
autolabelh(bars, diffs)
lg = ax.legend(handles=[gold], fontsize=18)
xlbl = ax.set_xlabel('(B-V)$_{cloud}$ - (B-V)$_{moon}$', fontsize=18)
yt = ax.set_yticks(ind)
ytl = ax.set_yticklabels(filters)
plt.tick_params(axis='both', which='major', labelsize=16)
titl = ax.set_title(
    'Difference in measured B-V index of cirrus clouds and the moon \n'
    'Clouds: {}, Moon: {}'.format(clouddate, moondate), y=1,
    fontsize=22)

# adjust margins slightly
margin = max(diffs) * 0.15
x0, x1, y0, y1 = plt.axis()
plt.axis((x0 - margin,
          x1 + margin,
          y0 + margin,
          y1 - margin))

plt.savefig(saveloc + '/B-Vdiff.png', bbox_inches='tight')

# Plot B-V for cloud next to B-V for moon with error bars ----------------------
h = 0.4

fig2, ax2 = plt.subplots(figsize=(20, 10))
rects1 = ax2.barh(ind, cloudbv, h, color='cyan', align='center', alpha=0.7,
                  xerr=clouderr, error_kw=dict(ecolor='black'))
rects2 = ax2.barh(ind+h, moonbv, h, color='gray', align='center', alpha=0.8,
                  xerr=moonerr, error_kw=dict(ecolor='black'))
lg2 = ax2.legend((rects1[0], rects2[0]), ('Clouds', 'Moon'), fontsize=18)
xlbl2 = ax2.set_xlabel('B-V', fontsize=18)
yt2 = ax2.set_yticks(ind + h/4)
ytl2 = ax2.set_yticklabels(filters)
plt.tick_params(axis='both', which='major', labelsize=16)
titl2 = ax2.set_title('B-V of clouds compared to moon \n'
                      'Clouds: {}, Moon: {}'.format(clouddate, moondate),
                      fontsize=22)
autolabelh(rects1, cloudbv)
autolabelh(rects2, moonbv)
plt.savefig(saveloc + '/cloudsvsmoon.png', bbox_inches='tight')

# Lastly, save a file specifying which moon set we compare to
f = open(saveloc + '/moon_comparison_set_{}.txt'.format(moondate), 'w')
f.write('Compared to {}'.format(moondate))

f.close()