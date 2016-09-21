#!/home/emc/anaconda3/envs/astroconda/bin/python

# ============================================================================ #
# Do photometry in batch mode!
# Eryn Cangi
# 1 September 2016
# ============================================================================ #

from pyraf import iraf

def prepare_params():
    """
    Grabs the parameters for each image out of a storage file and puts them
    into a list. Also generates a list of logfile names.

    Format of storage file is:
    IMAGENAME    SKYVALUE    SIGMA    EXPOSURE    FULLPATH (user dependent)
    """

    choice = raw_input('Enter option to select image & parameter file '
                           'path.\n'
                           '[1]: Enter full path to the file\n'
                           '[2]: Enter just the working directory name (use '
                           'the default base path)\n\n')

    if choice == '1':
        param_file = raw_input('Please input path: ')
    elif choice == '2':
        d = raw_input('Please input directory name with spaces, no slashes: ')
        param_file = '/home/emc/GoogleDrive/Phys/Research/BothunLab' \
                     '/AnalysisFiles/{}/files_and_params.txt'.format(d)
    else:
        while choice != 1 or choice != 2:
            choice = raw_input('Please enter either 1 or 2:\n'
                               '[1]: Enter full path to the file\n'
                               '[2]: Enter just the working directory name ('
                               'use the default base path)\n\n')


    # Read in the param_file and put values in lists
    image_data = []

    with open(param_file, 'r') as f:
        for line in f:
            ln = line.split()
            if ln:
                image_data.append([ln[0], ln[1], ln[2], ln[3], ln[4]])

    # Generate some logfile names for photometry output
    logs = ['{}_photometry'.format(x[0][:-4]) for x in image_data]

    return image_data, logs


def do_photometry(coordfile, polygonfile):
    """
    Do photometry in batch mode.
    :param coordfile: a text file of grid centers, as required by polyphot
    :param polygonfile: a text file of polygon sizes, as required by polyphot

    Output:
    Files for each image with extension '_photometry' and data inside.
    """

    # This just retrieves all parameters for all images from a stored file
    # that I made
    image_data, lognames = prepare_params()

    # Loops through images and calls polyphot for each. REQUIRED:
    # Manually set interactive mode = no, validate = no in epar polyphot at
    # pyraf prompt.
    for image, logname in zip(image_data, lognames):
        filename = image[0]
        sky = image[1]
        sig = image[2]
        exp = image[3]

        # call the task
        iraf.polyphot(filename, coords=coordfile, output=logname,
                      polygons=polygonfile, skyvalue=sky, sigma=sig, itime=exp)
    print('Photometry complete!')
    return None
