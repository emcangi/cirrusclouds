#!/home/emc/anaconda3/envs/astroconda/bin/python

# ============================================================================ #
# Summarize photometry outputs for an image file. Creates a nice pandas table
# and then utilizes the data in it to create an image with detection grid
# drawn on to it. Also outputs the highest SNR above the detection threshold.
# Eryn Cangi
# 4 October 2016
# TODO: FIX ME, 7 November
# ============================================================================ #

import os
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import re


# Get directory, image name and create path to image, photometry file ==========

default = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera'

print('Current default path to the photometry file is {}\n'.format(default))

pathext = '9October2016/set7/15-none/225microsec'
    #raw_input('Please enter the directory(ies) housing the photometry '
                    #'file (e.g. 28October2016/15-11/260microsec): ')

filename = '13-41-23-838' #raw_input('Please input the filename EXCLUDING file
# extension: ')

size = '64x64'#raw_input('Please input the gridsize of the photometry grid (
# e.g. 64x64): ')

full_path = '/'.join([default, pathext, filename])
img_file = full_path + '.FIT'

if size != '10x10':
    phot_file = full_path + '_photometry_' + size
else:
    phot_file = full_path + '_photometry'

print('Using image: {}'.format(img_file))
print('Using photometry file: {}'.format(phot_file))

# Create shorter polyphoy results file (no comment lines) ======================
output_file = phot_file + "_data"

# TODO: fix this so the number of lines is determined from file, not a const
lines = 83
os.system("tail -n +{} {} > {}".format(lines, phot_file, output_file))

# Get FITS data and save for using in matplotlib ===============================
hdu_list = fits.open(img_file)
hdu_list.info()
image_data = hdu_list[0].data
hdu_list.close()

# Construct initial lists of information from the photometry file ==============
ln_cnt = 1
data = []
grids = []
grids_sublist = 0

with open(output_file, 'r') as f:
    for line in f:
        # First grab the magnitude of the sky background and the filters
        if ln_cnt == 3:
            msky = float(line.split()[0])  # gets magnitude of sky
            sigma = float(line.split()[1])  # gets sigma
        if ln_cnt == 4:
            filter1 = line.split()[2].split(',')[0]
            filter2 = line.split()[2].split(',')[1]
        if ln_cnt == 6:
            gridsize = line.split()[0]
        # finds lines that end in 5 only--these are the ones with data
        if ln_cnt % 5 == 0 and ln_cnt % 10 != 0:
            data.append(line)
        # check what the last digit of the line number is
        last_digit = ln_cnt % 10
        # these lines will hold vertices of the cell
        if last_digit in [7, 8, 9, 0]:
            if last_digit == 7:
                grids.append([])  # start a new sublist if it is a new cell
            grids[grids_sublist].append(line)
            if last_digit == 0:
                grids_sublist += 1
        ln_cnt += 1  # we have to keep track since Python doesn't

# Construct data display table =================================================

big_table = [['Counts', 'Area(pixels)', 'Flux', 'v1', 'v2', 'v3', 'v4']]

for e1, e2 in zip(data, grids):
    datum = e1.split()  # extract useful info
    del datum[-1]  # gets rid of some garbage characters trailing on the line
    datum = datum[:3]  # get rid of magg, merr, pier, perror which we don't need
    datum = [float(i) for i in datum]

    # appends vertices in neat ordered-pair format
    for el in e2:
        # witchcraft to append a list of floats for the coordinates
        datum.append([float(i) for i in el.strip().split()[:2]])

    # add data and vertices to a big table
    big_table.append(datum)

# Make a Pandas dataframe ======================================================
headers = big_table[0]
df = DataFrame(big_table[1:], columns=headers)
print(df['Counts'])

# EVERYTHING AFTER HERE IS OUTDATED AND NEEDS FIXED ============================





# Calculate the background per cell, error and threshold of detection ==========
# note that 300 is the area of a cell sized 20x15. later I should set this
# dynamically
bg_per_cell = msky * 300
bg_err_per_px = sigma / 25
bg_err_per_cell = bg_err_per_px * 300

# Calculate detection threshold
threshold = bg_per_cell + 3 * bg_err_per_cell
print('Threshold: {}'.format(threshold))

# Make the images ==============================================================

# min and max ratio of counts to sky background -------------
m = df['Counts'].min()
M = df['Counts'].max()
print('Min counts: {}'.format(m))
print('Max counts: {}'.format(M))

cirrus_detected = df.loc[df['Counts'] >= threshold]

# create plot with image as background
fig = plt.figure(figsize=(16, 12))
ax3 = fig.add_subplot(111)
plt.imshow(image_data, cmap='gray')
ax3.set_autoscale_on(False)

for index, row in cirrus_detected.iterrows():  # iterate over the rows
    # collect and tidy up
    r1 = row['v1']
    r2 = row['v2']
    r3 = row['v3']
    r4 = row['v4']

    # including the 1st point at the end again allows the boxes to be closed
    x = np.array([r1[0], r2[0], r3[0], r4[0], r1[0]])
    y = np.array([r1[1], r2[1], r3[1], r4[1], r1[1]])

    # ax1.scatter(x, y, c='lime') # toggle to turn on plotting vertices
    ax3.plot(x, y, c='purple')
    ax3.set_title('{}.FIT'.format(filename), fontsize=20)
    ax3.get_xaxis().set_visible(False)
    ax3.get_yaxis().set_visible(False)

plt.show()
#plt.savefig(full_path + '.png')

with open('{} SNR stats.txt'.format(filename), 'w') as f:
    f.write('Min counts: {}\n'.format(m))
    f.write('Max counts: {}\n'.format(M))
    f.write('Detection threshold: {}\n'.format(threshold))
    f.write('Largest SNR (max - threshold): {}\n'.format(M - threshold))
    f.write('Largest SNR is {} multiples of threshold\n'.format(M/threshold))
    f.write('\n')
