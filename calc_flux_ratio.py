#!/home/emc/anaconda3/envs/astroconda/bin/python
# -*- coding: utf-8 -*-

# ============================================================================ #
# Eryn Cangi
# Created 15 January 2017
# Script #4a of 5 to run
# Calculate the flux ratio of two images given their respective photometry
# files. Returns the flux ratios by grid cell which can then be plotted as
# required. This is a batch operation.
# This script should be called from the command prompt and run interactively.
# ============================================================================ #

import os
from pandas import DataFrame
import numpy as np
import itertools
import re
from math import log10, log, sqrt

# Camera bias: Determined empirically. Faulty counts per pixel.
BIAS = 0.1875  # Orion StarShoot All-in-one camera

# Zero points - Calculated in separate script find_zero_points.py
ZP_DICT = {'11': -1.24, '15': -1.67, '47': -3.77, '82a': 0.13, 'LRGBred': -2.48,
           'LRGBgreen': -1.89, 'LRGBblue': -1.45, 'LRGBluminance': 0.14}

def make_dataframe(phot_file, pt):
    """
    Analyzes the photometry file of a single image to create a tidy Pandas data
    frame that displays the B-V index, count error per cell, and error in B-V
    index.

    CALLED BY: get_flux_ratio()

    :param phot_file: a file containing photometry for img_file
    :param pt: photometry type. 'm' = manual, 'g' = gridded
    :return: a Pandas dataframe displaying B-V, count error/cell and B-V error
    """

    # Copy polyphot data to new file without headers --------------------------
    out_file = phot_file + '_data'

    # TODO: fix this so the number of lines is determined from file, not a const
    lines = 83
    os.system("tail -n +{} {} > {}".format(lines, phot_file, out_file))

    # Construct initial lists of information from the photometry file ----------
    ln_cnt = 1  # we have to keep track since Python doesn't
    data = []   # stores lines that contain photometry counts
    grid = []   # stores cell vertices for a particular counts datum
    cell = 0    # keeps track of which cell we are on; order is how the cells
                # appear in the photometry file.

    # TODO: Make next block a heckin lot more elegant...
    # Loops through the photometry file lines and collects data ================
    with open(out_file, 'r') as f:
        for line in f:

            # First grab sky background, filters and grid size -- only need
            # to do this once but there's not really a more elegant way.
            if ln_cnt == 3:
                msky = float(line.split()[0])
                sigma = float(line.split()[1])
            if ln_cnt == 4:
                filter1 = line.split()[2].split(',')[0]
                filter2 = line.split()[2].split(',')[1]
            if ln_cnt == 6:
                gridsize = line.split()[0]
                img_metadata = {'msky': msky, 'sigma': sigma, 'filter1':
                                filter1, 'filter2': filter2, 'gridsize':
                                gridsize}

            if pt == 'g':
                # check what the last digit of the line number is
                last_digit = ln_cnt % 10

                # Lines ending in 5 are the ones with data
                if ln_cnt % 5 == 0 and last_digit != 0:
                    data.append(line)

                # The following lines list the vertices of the grid cell
                if last_digit in [7, 8, 9, 0]:
                    # start a new sublist if it is a new cell
                    if last_digit == 7:
                        grid.append([])
                    # append the items to the sublist
                    grid[cell].append(line)

                    # this tells us we have finished logging the cell vertices
                    if last_digit == 0:
                        cell += 1

            elif pt == 'm':  #TODO: fix this so it can use more than 1 region
                # there will only be data on line 5 if photometry is manual
                if ln_cnt == 5:
                    data.append(line)

                # vertices are in some irregular shape, maybe more than 4
                if ln_cnt >= 7:
                    grid.append([])
                    grid[cell].append(line)

            ln_cnt += 1

    # Construct data display table =============================================

    # Headers of the table/dataframe
    if pt == 'g':
        big_table = [['Counts', 'Area(pixels)', 'Flux', 'CellErr',
                      'Err', 'v1', 'v2', 'v3', 'v4']]
    elif pt == 'm':
        big_table = [['Counts', 'Area(pixels)', 'Flux', 'CellErr', 'Err',
                      'vertices']]

    # build data to add to dataframe
    for e1, e2 in zip(data, grid):
        datum = e1.split()
        del datum[-1]  # gets rid of junk characters added to the line
        datum = datum[:3]   # extract useful info only (counts, area, flux)
        datum = [float(i) for i in datum]
        datum.append((sigma/5) * datum[1])  # append Cell Count Error
        datum.append(-99)  # field for the magnitude error. placeholder value.

        # appends vertices in neat ordered-pair format
        if pt == 'g':
            for el in e2:
                # witchcraft to append a list of floats for the coordinates
                datum.append([float(i) for i in el.strip().split()[:2]])
        elif pt == 'm':
            datum.append(e2)

        # Subtract off the camera bias ((bias counts per px) * area) from the
        # flux, which is datum[2]
        datum[2] -= BIAS * datum[1]
        # print('flux after subtracting bias: {}'.format(datum[2]))

        # add data and vertices to a big table
        big_table.append(datum)
    # Make a Pandas dataframe ==================================================
    headers = big_table[0]
    df = DataFrame(big_table[1:], columns=headers)
    return df, img_metadata


def get_flux_ratio(photfiles, zp_pair, pt):
    """
    Generates flux ratio dataframes given a pair of images and their
    photometry files.

    CALLED BY: main logic

    :param photfiles: Photometry files associated with imgs
    :param zp_pair: zero points for the filters being examined in these images
    :param pt: photometry type. 'm' = manual, 'g' = gridded

    two possible returns, one for success, one for failure when flux < 0:
    :return (success): status indicator, the dataframe, two metadata dicts
    :return (failure): status indicator, None, problem filter name, flux value
    """

    phot_fileB = photfiles[0]
    phot_fileV = photfiles[1]
    zp_b = zp_pair[0]
    zp_v = zp_pair[1]

    # print('Sending in: \n {} and \n {}'.format(phot_fileB, phot_fileV))

    # Get the tidy flux counts for the B and V filters--these are not yet B
    # or V magnitudes, they are still fluxes!
    # print('trying to run make_dataframe')
    dfB, img_metadataB = make_dataframe(phot_fileB, pt)
    # print('B ok')
    dfV, img_metadataV = make_dataframe(phot_fileV, pt)
    # print('V ok')
    # print('successfully ran make_dataframe')

    # ==========================================================================
    # CALCULATE THE FLUX RATIOS AND B-V INDICES
    # ==========================================================================

    # Convert the dataframe information to magnitudes in B and V
    to_mag_b = lambda x: -2.5 * log10(x) + zp_b
    to_mag_v = lambda x: -2.5 * log10(x) + zp_v

    # calculate the error of the B-V index. Error is function of flux. Thus
    # this must be done before we convert the flux to magnitudes.
    # calculation: mag = -2.5 * log10(f) + zp, so
    # dm = sqrt[((del_m/del_f)*df)^2] = |del_m/del_f| * df
    dfB['Err'] = (2.5 * (dfB['CellErr'])) / (dfB['Flux'] * log(10))
    dfV['Err'] = (2.5 * (dfV['CellErr'])) / (dfV['Flux'] * log(10))

    # these only needed for when doing gridded photometry.
    # dfB = dfB[dfB['Flux'] != 0]
    # dfV = dfV[dfV['Flux'] != 0]

    # dfB = dfB[dfB['Flux'] >= 0]
    # dfV = dfV[dfV['Flux'] >= 0]

    failed = False
    # Convert the flux values to magnitudes
    try:
        dfB['Flux'] = dfB['Flux'].apply(to_mag_b)
    except ValueError:
        probflux = dfB.at[0, 'Flux']
        failed = True
        problemfilter = img_metadataB['filter1']

    try:
        dfV['Flux'] = dfV['Flux'].apply(to_mag_v)
    except ValueError:
        probflux = dfV.at[0, 'Flux']
        failed = True
        problemfilter = img_metadataV['filter1']

    # Make the B-V dataframe. Maintain vertex columns without knowing how
    # many there are or what they are called.
    if not failed:
        status = 'OK'
        B_V_df = dfB.copy(deep=True)  # make copy of one of the dfs to get cols
        del B_V_df['Counts']          # delete unnecessary cols
        del B_V_df['Area(pixels)']
        B_V_df.rename(columns={'Flux': 'B-V'}, inplace=True)
        B_V_df.rename(columns={'Err': 'BVErr'}, inplace=True)
        B_V_df['B-V'] = dfB['Flux'] - dfV['Flux']
        B_V_df['BVErr'] = sqrt(dfB['Err']**2 + dfV['Err']**2) # TODO: check
        return status, B_V_df, img_metadataV, img_metadataB
    elif failed:
        status = 'Fail'
        return status, None, problemfilter, probflux


# BATCH PROCESSING =============================================================

# Get the main folder to operate on. Should be a folder containing
# filter-titled folders
folder = raw_input('Please raw_input the main folder to operate on, '
                   'e.g. 11February2017_MOON/set01. Should contain folders '
                   'each '
                   'named for a filter: ')
un = raw_input('Enter the user account name of this computer: ')
default = '/home/{}/GoogleDrive/Phys/Research/BothunLab/SkyPhotos' \
          '/NewCamera/{}/'
mypath = default.format(un, folder)

# Make folders
paths = []
img_paths = []
phot_paths = []

# manual or gridded photometry; use info to construct string to search for to
#  find photometry files
photometry_type = raw_input('Is photometry [m]anual or [g]ridded?: ')
pt = photometry_type.lower()

if pt == 'm':
    phot_str_end = 'manual$'
elif pt == 'g':
    phot_str_end = '([0-9]){1,3}[x]([0-9]){1,3}$'
else:
    while pt not in ['m', 'g']:
        photometry_type = raw_input('Is photometry [m]anual or [g]ridded?: ')
        pt = photometry_type.lower()

# Collect a list of folders containing images, image paths and photometry paths

for (dirpath, dirnames, files) in os.walk(mypath):
    for f in files:
        if f.endswith('.FIT'):     # store image path
            img_paths.append(dirpath + '/' + f)
        else:
            regex_result = re.search(phot_str_end, f)
            if regex_result is not None:
                phot_paths.append(dirpath + '/' + f)
# print(img_paths)
# print(len(img_paths))
# print(phot_paths)
# print(len(phot_paths))

# Generate pairs of the form [blue, visual]; total is len(blues) * len(visuals)
blues = ['47', '82a', 'LRGBblue', 'LRGBluminance']
visuals = ['11', '15', 'LRGBred', 'LRGBgreen']
combos = list(itertools.product(blues, visuals))

# Collect the zero points in the same format for when we make the dataframe
zps = [list(i) for i in combos]

for combo in zps:
    combo[0] = ZP_DICT[combo[0]]
    combo[1] = ZP_DICT[combo[1]]

# make empty lists to store pairs of image or photometry paths. format:
# [[blue1, visual1], [blue1, visual2]...]
img_pairs = [['', ''] for i in range(len(combos))]
phot_pairs = [['', ''] for i in range(len(combos))]

# Step through the empty pair lists and populate them
counter = 0
for combo in combos:
    for i, p in zip(img_paths, phot_paths):
        # print('looking for {} or {} in \n {}'.format(combo[0], combo[1], i))
        # looks in image path and photometry file path for the blue filter
        b_match_img = re.search('((?<=/){}(?=/))'.format(combo[0]), i)
        b_match_phot = re.search('((?<=/){}(?=/))'.format(combo[0]), p)

        # looks in image path and photometry file path for the visual filter
        v_match_img = re.search('((?<=/){}(?=/))'.format(combo[1]), i)
        v_match_phot = re.search('((?<=/){}(?=/))'.format(combo[1]), p)

        # populates lists with pairs of image paths and photometry paths in
        # format [blue, visual]
        if (b_match_img is not None) and (b_match_phot is not None):
            img_pairs[counter][0] = i
            phot_pairs[counter][0] = p
        if (v_match_img is not None) and (v_match_phot is not None):
            img_pairs[counter][1] = i
            phot_pairs[counter][1] = p
        else:
            continue
    counter += 1

counter = 0

# Iterate through pairs and retrieve B-V dataframes.
errlog = open(mypath+'errorlog.txt', 'w')

for imgs, phots, zp in zip(img_pairs, phot_pairs, zps):
    print('Processing pair {}/{}'.format(counter, len(zps)))
    status, BVdf, m1, m2 = get_flux_ratio(phots, zp, pt)

    if status == 'Fail':
        bfilt = re.search('(?<=set[0-9]{2}/).+(?=/.+?sec)', imgs[0]).group(0)
        vfilt = re.search('(?<=set[0-9]{2}/).+(?=/.+?sec)', imgs[1]).group(0)
        report = 'Filter {} had flux < 0: {} \n Could not complete ' \
                 'combo {}-{} \n'.format(m1, m2, bfilt, vfilt)
        print(report)
        errlog.write(report)
        errlog.write('\n')
    elif status == 'OK':
        BVdf.replace([np.inf, -np.inf], np.nan)    # set any "inf" values to NaN
        # Write dataframe to CSV. NaN is represented as -9999
        fname = '{}B-V_{}-{}.csv'.format(mypath, m2['filter1'],
                                         m1['filter1'])
        BVdf.to_csv(path_or_buf=fname, encoding='utf-8', na_rep='-9999')
    counter += 1

errlog.close()
