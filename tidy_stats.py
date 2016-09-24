#!/home/emc/anaconda3/envs/astroconda/bin/python

# ============================================================================ #
# Takes files with pixel statistics and extracts the sky values and sigmas.
# Eryn Cangi
# 31 August 2016
# ============================================================================ #


def tidy_list_skyvals(mypath):
    """
    :param mypath: a variable that contains the full path to a directory
    containing analysis files which have pixel statistics found via imexam
    for each image. It should have just the txt files and no subdirectories.

    output: a single tidy file summarizing the values for each image,
    with path name attached for ease of navigation.
    """

    from os import walk
    import re

    # Collect a list of files which contain pixel statistics
    for (dirpath, dirnames, file) in walk(mypath):
        filenames = file

    if mypath[-1] != '/':
        mypath += '/'

    print('Using these files: {}'.format(filenames))

    # Establish the output file for finalizing the sky values
    output = open('files_and_params.txt', 'w')
    output.write('# IMAGE \t SKY MEAN \t SIGMA \t EXPOSURE \t PATH\n')

    # Main loop: Deals with the messy files by extracting the filenames,
    # gathering all the acquired data (doesn't matter how many datapoints),
    # finding the min mean value and associated standard deviation and writing
    # out to the output file.
    for name in filenames:
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

        # iterates through all the data in the current file...
        for line in lines:
            # recognize lines with filenames. They just happen to start with C.
            if line[0] == 'C':
                # PROCESS IMAGE DATA BEFORE MOVING ON TO NEXT ONE...
                if means and stds:
                    mmin = means[0]
                    mmin_index = means.index(means[0])
                    # Finds the minimum value in means and associated std index
                    for m in means:
                        if m < mmin:
                            mmin = m
                            mmin_index = means.index(m)

                    std = stds[mmin_index]

                    # remove filename at end of path - makes life easier later
                    imgpath = thepath.replace(image, '')

                    # writes to the output file
                    output.write('{}\t{}\t{}\t{}\t{}\n'.format(image, mmin,
                                                               std, exp,
                                                               imgpath))

                # NOW START WORKING ON IMAGE DESIGNATED BY THIS LINE...

                # identify path name for the new image
                thepath = line[14:]

                # Extract the image name
                image = re.search(fnameexp, line).group(0)

                # extract the exposure time
                e = re.search('\d+\D{0,5}sec', thepath).group(0)
                val = int(re.search('\d+', e).group(0))
                unit = re.search('\D+', e).group(0)
                unit_key = {'sec': 1, 'millisec': 1*10**(-3),
                            'microsec': 1*10**(-6), 'nanosec': 1*10**(-9),
                            'picosec': 1*10**(-12), 'femtosec': 1*10**(-15)}
                exp = round(val * unit_key[unit], 6)

                # reset means and std lists
                means = []
                stds = []

            # if not a header line, line contains pixel stats. grab them.
            else:
                data = line.strip('\n').split()
                means.append(data[2])
                stds.append(data[3])

    output.close()
