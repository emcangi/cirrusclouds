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


# IDENTIFY CLOUD AND MOON/SUN SETS TO COMPARE ==================================

# collect path information to files
basepath = '/home/{}/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera/'
un = raw_input('Please specify username of this computer account (enter to '
               'use default of "emc"): ')
if un == '':
    un = 'emc'
else:
    pass
basepath = basepath.format(un)

cloudpath = raw_input('Please enter the cloud set folder, '
                      'i.e. 3January2017/set01: ')
full_cloud_path = basepath + cloudpath

full_compared_path = ''
while full_compared_path == '':
    selectCompare = raw_input('Available comparison sets: \n '
                              '[1] 10April2017_MOON/set01 \n'
                              '[2] 26May2017_SUN/set01 \n '
                              '\nSelect 1 or 2: ')
    if selectCompare == '1':
        comparedpath = '10April2017_MOON/set01'
    elif selectCompare == '2':
        comparedpath = '26May2017_SUN/set01'
    else:
        pass
    full_compared_path = basepath + comparedpath

# get the dates only--used for putting labels in the plots
clouddate = re.search('([0-9]+[A-Za-z]+[0-9]+)', cloudpath).group(0)
cloudset = re.search('set\d{2}', cloudpath).group(0)
comparedate = re.search('([0-9]+[A-Za-z]+[0-9]+)', comparedpath).group(0)
comparetype = re.search('(?<=_)\w+', comparedpath).group(0).lower()

# GET ALL THE B-V FILES IN CLOUD AND MOON FOLDERS ==============================
cloud_files = find_bv_files_in(full_cloud_path)
compared_files = find_bv_files_in(full_compared_path)

# COLLECT B-V AND ERROR DATA FOR CLOUDS AND MOON ===============================

clouddata = extract_bv_data(cloud_files)
comparedata = extract_bv_data(compared_files)

# this may seem excessive and unpythonic, but it deals with the fact that
# sometimes there isn't a B-V value for two given images of clouds because
# one of them may have had a negative flux.
filters = []
cloudbv = []
clouderr = []
comparebv = []
compareErr = []

for c in clouddata:
    for m in comparedata:
        if c[0] == m[0]:
            filters.append(c[0])
            cloudbv.append(c[1])
            clouderr.append(c[2])
            comparebv.append(m[1])
            compareErr.append(m[2])


# CALCULATE RAW B-V DIFFERENCES BETWEEN CLOUD AND MOON DATASETS ================

diffs = []
for a, b in zip(cloudbv, comparebv):
    diffs.append(a - b)

# PLOTTING =====================================================================

# create and save plots in DATA, so they aren't buried in the photo folders
ind = np.arange(len(filters))
saveloc = '/home/{}/GoogleDrive/Phys/Research/BothunLab/DATA/'.format(un) + \
          cloudpath

if not os.path.exists(saveloc):
    os.makedirs(saveloc)

# Plot difference of cloud B-V and moon B-V ------------------------------------
# Make the plot
h = 0.8
fig, ax = plt.subplots(figsize=(14, 10))

# Determines whether to color a bar gold or blue depending on the value,
# makes a legend
colors = []
for d in diffs:
    if abs(d) <= 0.05:
        colors.append('gold')
    elif 0.05 <= abs(d) <= 0.1:
        colors.append('silver')
    else:
        colors.append('cornflowerblue')

gold = mpatches.Patch(color='gold', label='Diff <= 0.05')
silver = mpatches.Patch(color='silver', label='Diff <= 0.1')
ax.legend(handles=[gold, silver], fontsize=18, loc='lower right')

# plot
bars = ax.barh(ind, diffs, h, align='center', color=colors, alpha=1)
autolabelh(bars, diffs)

# this next bit of madness is because i'm using both latex and string
# formatting in the same line
xlbl_str = '(B-V)$_{' + 'cloud' + '}$ - (B-V)$_{' + comparetype + '}$'
ax.set_xlabel(xlbl_str, fontsize=18)
ax.set_yticks(ind)
ax.set_yticklabels(filters)
plt.tick_params(axis='both', which='major', labelsize=16)
titl = ax.set_title(
    'Difference in measured B-V index of cirrus clouds and the {} \n'
    'Clouds: {} {}, {}: {}'.format(comparetype, clouddate, cloudset,
                                   comparetype, comparedate), y=1,
    fontsize=22)

# adjust margins slightly
margin = max(diffs) * 0.15
x0, x1, y0, y1 = plt.axis()
plt.axis((x0 - margin,
          x1 + margin,
          y0 + margin,
          y1 - margin))

plt.savefig(saveloc + '/B-Vdiff_{}.png'.format(comparetype),
            bbox_inches='tight')

# Plot B-V for cloud next to B-V for moon with error bars ----------------------
h = 0.4
comparecolor = 'black' if comparetype == 'moon' else 'orangered'
compareErrColor = 'gray' if comparetype == 'moon' else 'orange'

fig2, ax2 = plt.subplots(figsize=(22, 10))

# plot the actual B-V data points
ax2.errorbar(ind, cloudbv, yerr=clouderr, fmt='o', color='blue', label='Clouds',
             ms=7, marker='D')
ax2.errorbar(ind, comparebv, yerr=compareErr, fmt='o', color=comparecolor,
             label='{}'.format(comparetype), ms=7, marker='x')

# print B-V values next to their markers and collect the locations
cloudbv_pts = []
comparebv_pts = []
for i, v in enumerate(cloudbv):
    cloudbv_pts.append([i, v])
    ax2.text(i+0.1, v, str(round(v, 2)), color='blue', fontsize=12)
for i, v in enumerate(comparebv):
    comparebv_pts.append([i, v])
    ax2.text(i-0.4, v, str(round(v, 2)), color=comparecolor, fontsize=12)

# graph partially transparent bars representing the error
for pt, err in zip(cloudbv_pts, clouderr):
    ax2.plot([pt[0], pt[0]], [pt[1]-err, pt[1]+err], lw=10, color="skyblue",
             solid_capstyle="butt", alpha=0.4)
for pt, err in zip(comparebv_pts, compareErr):
    ax2.plot([pt[0], pt[0]], [pt[1]-err, pt[1]+err], lw=10,
             color=compareErrColor, solid_capstyle="butt", alpha=0.3)

# ticks and titles etc
ax2.legend(fontsize=18)
ax2.set_xticks(ind)
ax2.set_xticklabels(filters, rotation="45", ha='right')
ax2.set_xlabel('Blue-visual Filter combinations', fontsize=20)
ax2.set_ylabel('B-V index', fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=16)
titl2 = ax2.set_title('B-V of clouds compared to {} \n'
                      'Clouds: {} {}, {}: {}'.format(comparetype, clouddate,
                                                     cloudset, comparetype,
                                                     comparedate), fontsize=24)

plt.savefig(saveloc + '/cloudsvs{}.png'.format(comparetype),
            bbox_inches='tight')

# Lastly, save a file specifying which moon set we compare to
f = open(saveloc + '/{}_comparison_set_{}.txt'.format(comparetype,
                                                      comparedate), 'w')
f.write('Compared to {}'.format(comparedate))

f.close()
