#!/home/emc/anaconda3/envs/astroconda/bin/python

# ============================================================================ #
# Do photometry in batch mode!
# Eryn Cangi
# 1 September 2016
# Script 3 of 3 to run
# ============================================================================ #


def prepare_params():
    """
    Grabs the parameters for each image out of a storage file and puts them
    into a list. Also generates a list of logfile names.

    Format of storage file must be:
    IMAGENAME    SKYVALUE    SIGMA    EXPOSURE    PATH

    The 'PATH' is the path to the image file, not including the image file
    itself, and will be user- or computer- dependent.
    """

    default = '/home/emc/GoogleDrive/Phys/Research/BothunLab' \
                     '/AnalysisFiles/{}/files_and_params.txt'

    print('Current default path to the image parameter file is {}, where curly '
          'braces represent the working directory\n'.format(default))

    choice = raw_input('How do you want to identify the image & parameter '
                       'file?\n'
                       '[1]: Enter full path to the file\n'
                       '[2]: Enter just the working directory name (use '
                       'the default path)\n'
                       'Your choice: ')

    if choice == '1':
        param_file = raw_input('Please input path: ')
    elif choice == '2':
        d = raw_input('Please input directory name with spaces, no slashes: ')
        param_file = default.format(d)
    else:
        while choice != 1 or choice != 2:
            choice = raw_input('Please enter either 1 or 2:\n'
                               '[1]: Enter full path to the file\n'
                               '[2]: Enter just the working directory name ('
                               'use the default path)\n\n')

    # Read in the param_file and put values in lists
    image_data = []

    with open(param_file, 'r') as f:
        throwaway = f.readline() # skip the first line which is a comment
        for line in f:
            ln = line.split()
            if ln:
                image_data.append([ln[0], ln[1], ln[2], ln[3], ln[4]])

    # Generate some logfile names for photometry output
    logs = ['{}_photometry'.format(x[0][:-4]) for x in image_data]

    return image_data, logs


def do_photometry():
    """
    Do photometry in batch mode.
    Script will prompt for the locations of the grid files and the location
    of the parameter file.

    Output:
    Files for each image with extension '_photometry' and data inside,
    which are placed in the same directory as their parent image.
    """

    from pyraf import iraf
    from os import walk

    # Retrieves image parameters from a stored file ----------------------------
    image_data, lognames = prepare_params()

    # Identify the grid files --------------------------------------------------
    default = '/home/emc/GoogleDrive/Phys/Research/BothunLab/AnalysisFiles' \
              '/gridfiles/'

    print('Default path for coordinate and polygon files: \n{}'.format(default))
    use_default = raw_input('Use base path? (y/n): ')
    if use_default == 'n':
        path = raw_input('Enter new path to coordinate and polygon files: ')
    elif use_default == 'y':
        path = default
    else:
        while use_default != 'n' or use_default != 'y':
            use_default = raw_input('Please enter y or n: ')

    print('Available grid files: ')

    for (dirpath, dirnames, gfile) in walk(path):
        print(gfile)

    gsize = raw_input('Enter the grid size to use (ex: 10x10): ')

    coordfile = gsize + 'grid_centers.txt'
    polygonfile = gsize + 'grid_polygons.txt'

    print('\nNow doing photometry. Please wait...\n')

    # Loops through images and call polyphot for each --------------------------
    for image, logname in zip(image_data, lognames):
        filename = image[0]
        sky = image[1]
        sig = image[2]
        exp = image[3]
        im_path = image[4]

        # call the task
        iraf.polyphot(im_path+filename, coords=path+coordfile,
                      output=im_path+logname, polygons=path+polygonfile,
                      interactive='no', skyvalue=sky, sigma=sig, itime=exp,
                      verify='no')


    print('Photometry complete!')

    return None
