#!/home/emc/anaconda3/envs/astroconda/bin/python
# -*- coding: utf-8 -*-

# ============================================================================ #
# Eryn Cangi
# 31 August 2016
# Updated 12 February 2017
# Script #2 of 5 to run
# Takes files with pixel statistics gathered by imexam and extracts the
# median sky background values and sigmas.
# Produces a text file called files_and_params.txt which summarizes all the
# images in the set.
# To use, call at the terminal.
# ============================================================================ #


def get_bg(means, stds, image):
    """
    :param means: a list of the mean sky values in 25 px boxes of the
                  background sky (or closest to it we can get)
    :param stds:  the sigmas associated with the above means. order matters
    :param image: image name

    :returns median value of means; the associated standard deviation (sigma)
             for that median value; the error in that value (sigma/sqrt(N))
             and the image path name for convenience.

    note that if the median of the sky value means appears more than once,
    this will just find the first appearance and take the sigma of that line.
    This is fine because there shouldn't be very much deviation between
    different data.
    """

    from math import sqrt
    from numpy import median

    # convert to numbers
    means = [float(x) for x in means]
    stds = [float(y) for y in stds]

    # find sky value, associated sigma and error in the sky value.
    skyval = median(means)
    # toggle the following line if dealing with camera bias files only!
    # skyval = max(means)
    try:
        sigma = stds[means.index(skyval)]
    except ValueError:
        print('Image {} probably has an even number of sky background data '
              'points in its imexam results file. Please re-run '
              'collect_skystats.py on this file, use results to replace the '
              'content of its imexam results file, delete any partially '
              'damaged files_and_params from the working directory and re-run '
              'this script.')
    bgerr = sigma/sqrt(25)

    return skyval, sigma, bgerr


def summarize_set(mypath):
    """
    :param mypath: Path to the dated folder containing image sets (only works
    for data where the sky value statistics were calculated after the logging
    fix by @sosey).

    output: a single tidy file named files_and_params.txt summarizing the
    values for each image, with path name attached for ease of navigation.
    file has column headers:
    IMAGE   SKYVAL   SIGMA   SKYVAL ERR   EXPOSURE   FILTER 1   FILTER 2   PATH
    """

    from os import walk
    import re

    full_file_paths = []    # makes dealing with opening images easy
    file_parent_dirs = []   # makes keeping track of parent directories easy

    # Collect a list of files which contain pixel statistics -------------------
    for (dirpath, dirnames, files) in walk(mypath):
        for file in files:
            if file.endswith('_sky') or file.endswith('_sky.txt'):
                full_file_paths.append(dirpath + '/' + file)
                file_parent_dirs.append(dirpath + '/')

    # print('Using these files: {}'.format(full_file_paths))

    # Establish the output file for finalizing the sky values ------------------
    output = open(mypath+'/files_and_params.txt', 'w')
    output.write('# IMAGE \t SKY VAL \t SIGMA \t SKYVAL ERR \t EXPOSURE \t '
                 'FILTER 1 \t FILTER 2 \t PATH\n')
    wstr = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'

    # MAIN LOOP OVER SKYSTAT FILES ---------------------------------------------
    # Extracts the filenames, pares down all datapoints (no matter how many),
    # finds the sky value, sigma and error and writes to output file

    for fpath, fdir in zip(full_file_paths, file_parent_dirs):
        print('Processing file: {}'.format(fpath))

        # PARSE FILENAME FOR IMAGE METADATA ------------------------------------
        # example path: /home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/
        # NewCamera/11February2017-MOON/set1/82a/0.9millisec/20-48-17-979_sky

        # Extract the image name
        fnameexp = '[0-2][0-9]\-[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{1,3}'
        image = re.search(fnameexp, fpath).group(0)
        image += '.FIT'

        # Extract the filter combination
        possfilters = ['11', '15', '47', '82a', 'None', 'LRGBred', 'LRGBgreen',
                       'LRGBblue', 'LRGBluminance']

        # print('Now finding the filters')
        # print('file path: {}'.format(fpath))
        for fil in possfilters:
            try:
                searchstr = '((?<=\/){}(?=\/))'.format(fil)
                bpfilter = re.search(searchstr, fpath,
                                     re.IGNORECASE).group(0)
                break
            except AttributeError:
                continue

        second_filter = 'None'  # TODO: maybe add support for 2 filters.
        # print('Done with filters')

        # print('Now finding the exposure time')
        # Extract the exposure time:
        # regex 1st expression: devil magic I found on stackexchange to
        # match floating point numbers that also could sometimes be integers
        # regex 2nd expr: matches any & all chars up until the first letter
        # third regex: Finds all the letters in the item
        e = re.search(r'[-+]?\d*\.*\d+\D{0,5}sec', fpath).group(0)
        val = re.search('(.+?)(?=[A-Za-z])', e).group(0)
        try:                                        # and it better be a number
            val = int(val)
        except ValueError:
            val = float(val)
        unit = re.search('[A-Za-z]+', e).group(0)
        unit_key = {'sec': 1, 'millisec': 1 * 10 ** (-3),
                    'microsec': 1 * 10 ** (-6), 'nanosec': 1 * 10 ** (-9),
                    'picosec' : 1 * 10 ** (-12), 'femtosec': 1 * 10 ** (-15)}
        exp = round(val * unit_key[unit], 6)
        # print('Done with exposure time')

        # print('Now get the stats')
        # START WORKING ON STATISTICS IN FILE ----------------------------------
        with open(fpath, 'r') as f:
            lines = f.readlines()

        # Get rid of extraneous lines created by pyRAF that we don't need
        # for L in ['_run_imexam \n', '\n', 'all_m_stats \n', 'real_m_stats \n',
        #           'SLICE   NPIX   MEAN   STD   MEDIAN   MIN   MAX\n']:
        #     while L in lines:
        #         lines.remove(L)

        means = []
        stds = []

        # ITERATE THROUGH STATISTICS -------------------------------------------
        for line in lines:
            # if line.startswith('Current'):
            #     continue
            if line.startswith('['):
                data = line.strip('\n').split()  # Clean up the line
                means.append(data[2])            # Get the mean sky value
                stds.append(data[3])             # And its associated st dev
            else:
                continue

        # print('Done with stats')
        # print('Now write the stuff out')
        # summarize the stats and write to the output file
        skybg, sigma, bgerr = get_bg(means, stds, image)
        output.write(wstr.format(image, skybg, sigma, bgerr, exp, bpfilter,
                                 second_filter, fdir))
        # print('Done writing, next file...')
        # print

    output.close()

path = raw_input('Enter the path to the dated image folder: ')

summarize_set(path)
