#!/home/emc/anaconda3/envs/astroconda/bin/python

# ============================================================================ #
# Takes files with pixel statistics and extracts the sky values and sigmas.
# Eryn Cangi
# 31 August 2016
# Script 2 of 3 to run
# ============================================================================ #


def get_bg(means, stds, image, thepath):
    """
    :param means: a list of the mean sky values in 25 px boxes of the
                  background sky (or closest to it we can get)
    :param stds:  the sigmas associated with the above means. order matters
    :param image: image name
    :param thepath: path to the image

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

    # remove filename at end of path - makes life easier later
    imgpath = thepath.replace(image, '')

    # because @#$% strings
    means = [float(x) for x in means]
    stds = [float(y) for y in stds]

    # find sky value, associated sigma and error in the sky value. NOTE: this
    #  will fail if there are an even number of data points for the sky
    # background. TODO: fix to handle even number of datums
    skyval = median(means)
    sigma = stds[means.index(skyval)]
    bgerr = sigma/sqrt(25)

    return skyval, sigma, bgerr, imgpath


def tidy_list_skyvals(mypath):
    """
    :param mypath: a variable that contains the full path to a directory
    containing analysis files which have pixel statistics found via imexam
    for each image. It should have just the txt files and no subdirectories.

    output: a single tidy file named files_and_params.txt summarizing the
    values for each image, with path name attached for ease of navigation.
    file has column headers:
    IMAGE   SKYVAL   SIGMA   SKYVAL ERR   EXPOSURE   FILTER 1   FILTER 2   PATH
    """

    from os import walk
    import re

    # Collect a list of files which contain pixel statistics -------------------
    for (dirpath, dirnames, file) in walk(mypath):
        print(file)
        filenames = file

    if mypath[-1] != '/':
        mypath += '/'

    print('Using these files: {}'.format(filenames))

    # Establish the output file for finalizing the sky values ------------------
    output = open('files_and_params.txt', 'w')
    output.write('# IMAGE \t SKY VAL \t SIGMA \t SKYVAL ERR \t EXPOSURE \t '
                 'FILTER 1 \t FILTER 2 \t PATH\n')
    wstr = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'

    # MAIN LOOP OVER TEXT FILES ------------------------------------------------
    # Extracts the filenames, pares down all datapoints (no matter how many),
    # finds the sky value, sigma and error and writes to output file
    for name in filenames:
        print('Processing file: {}'.format(name))
        with open(mypath+name, 'r') as f:
            lines = f.readlines()

        # Get rid of extraneous lines created by pyRAF that we don't need
        for L in ['\n', '_run_imexam \n', 'real_m_stats \n',
                  'SLICE   NPIX   MEAN   STD   MEDIAN   MIN   MAX\n']:
            while L in lines:
                lines.remove(L)

        # pattern to match for finding filenames
        fnameexp = '[0-2][0-9]\-[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{1,3}.FIT$'
        means = []
        stds = []

        # ITERATE THROUGH STATISTICS -------------------------------------------
        # warning: this section uses regular expression black magic
        for i in range(len(lines)):
            # recognize lines with filenames. They just happen to start with C.
            if lines[i][0] == 'C':
                # start working on image designated by the current line

                # identify path name for the new image
                thepath = lines[i][14:]

                # Extract the image name
                image = re.search(fnameexp, lines[i]).group(0)

                # Extract the filter combination
                first_filter = re.search('\w+(?=-)', name).group(0)
                second_filter = re.search('(?<=-)\w+', name).group(0)

                # extract the exposure time
                e = re.search('\d+\D{0,5}sec', thepath).group(0)
                val = int(re.search('\d+', e).group(0))
                unit = re.search('\D+', e).group(0)
                unit_key = {'sec': 1, 'millisec': 1*10**(-3),
                            'microsec': 1*10**(-6), 'nanosec': 1*10**(-9),
                            'picosec': 1*10**(-12), 'femtosec': 1*10**(-15)}
                exp = round(val * unit_key[unit], 6)

            else: #TODO: make this more concise
                # This block is to handle gathering statistics when we are
                # not at the end of the file yet.
                if i+1 < len(lines):
                    if lines[i][0] != 'C' and lines[i+1][0] != 'C':
                        # if not a header line AND the following line isn't a
                        # header line, we are in the block of data for image.
                        # grab the data.
                        data = lines[i].strip('\n').split()
                        means.append(data[2])
                        stds.append(data[3])
                    elif lines[i][0] != 'C' and lines[i+1][0] == 'C':
                        # we've reached the end of the pixel stats block

                        # gather data from this line
                        data = lines[i].strip('\n').split()
                        means.append(data[2])
                        stds.append(data[3])

                        # summarize the stats and write to the file
                        skybg, sigma, bgerr, imgpath = get_bg(means, stds,
                                                              image, thepath)
                        output.write(wstr.format(image, skybg, sigma, bgerr,
                                                 exp, first_filter,
                                                 second_filter, imgpath))

                        # reset means and std lists for next image
                        means = []
                        stds = []
                elif i+1 >= len(lines):
                    # end of file has been reached

                    # gather data from this line
                    data = lines[i].strip('\n').split()
                    means.append(data[2])
                    stds.append(data[3])

                    # summarize the stats and write to the file
                    skybg, sigma, bgerr, imgpath = get_bg(means, stds,
                                                          image, thepath)
                    output.write(wstr.format(image, skybg, sigma, bgerr,
                                             exp, first_filter,
                                             second_filter, imgpath))

    output.close()