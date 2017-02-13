#!/home/emc/anaconda3/envs/astroconda/bin/python

# ============================================================================ #
# Helper script to iterate through the images and allow interaction with DS9 to
# get the sky values
# Script 1 of 3 to run
# Output: Individual output files for each image, tailored with the image name.
# ============================================================================ #

from os import walk
import imexam
from box_stats import all_m_stats

mypath = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera'

#Collect the address for the current DS9 window
ds9data = imexam.list_active_ds9()
XPA_METHOD = ds9data.keys()[0]

print('Current default path is {}'.format(mypath))
use_default = raw_input('Use default path? (y/n) ')

if use_default == 'n':
    mypath = raw_input('Enter full path of top level directory containing '
                        'images: ')
elif use_default == 'y':
    img_directory = raw_input('Enter top level dated image directory: ')
    mypath = mypath + '/' + img_directory


# Connect to DS9 and register a new task with imexam to gather stats
v = imexam.connect(XPA_METHOD)
print('DS9 successfully connected\n')

mydic = {"i": (all_m_stats, "Modified stat display function, simultaneously "
                             "displays all the stats that can be displayed with"
                             " imexamine's 'm' task")}
v.exam.register(mydic)
print('New task successfully registered\n')

# Collect sets of corresponding paths and lists of image names =================
imgdirlists = []                  # store images within a directory

print('Building list of filenames and directories...')

for (dirpath, dirnames, filenames) in walk(mypath):
    if filenames:  # Only proceed if filenames has values (we have found images)
        temp = []
        temp.append(dirpath)
        fitsonly = [f for f in filenames if f[-4:] == '.FIT']  # Only use FITS
        temp.append(fitsonly)
        imgdirlists.append(temp)

imgdirlists = sorted(imgdirlists)

print('File list completed\n')


# Allow starting at a certain directory ========================================

# Create working copies
imgdirlists_copy = list(imgdirlists)

start = raw_input('Directory to start on (enter = start from beginning. You may'
                  ' type two directories like so: Parent/Child): ')
if start != '':
    # Go through lists of directories and images
    for imglist in imgdirlists:
        if start not in imglist[0]:
            imgdirlists_copy.remove(imglist)
            print('Skipping directory {}'.format(imglist[0]))
        else:
            # Break out of the loop once we've found the list with start
            break

    imgdirlists = list(imgdirlists_copy)  # Replace originals w/ updated copies
else:
    pass

one_only = raw_input('Are you trying to load individual images manually? (y/n)')

if one_only == 'y':
    load_another = 'y'
    while load_another != 'n':
        extradir = raw_input('Enter any additional parent folders without '
                             'initial and trailing slashes (e.g. '
                             'folder1/folder2): ')
        imgname = raw_input('Enter the image name with extension: ')
        single_image_path = mypath+'/'+extradir+'/'+imgname
        print('PATH::: {}'.format(single_image_path))
        v.load_fits(single_image_path, extver=0)
        v.setlog(filename="{}/{}/{}_sky".format(mypath, extradir, imgname[:-4]))
        v.zoom(0.5)
        v.imexam()
        v.setlog(on=False)
        print('Finished with image {}'.format(imgname))
        load_another = raw_input('Load another single image? (y/n) ')
else:

    print('Starting imexam loop...')

    # loop through images. Code will automatically pause to allow interaction.
    # q to continue to next image.
    completed = []

    for sublist in imgdirlists:
        imgnames = sublist[1]
        curdir = sublist[0]
        if sublist[1]:
            for image in imgnames:
                print('Using directory {}, image {}'.format(curdir, image))
                path = "{}/{}".format(curdir, image)
                print('PATH::: {}'.format(path))
                v.load_fits(path, extver=0)
                v.setlog(filename="{}_sky".format(path[:-4]))
                v.zoom(0.5)
                v.imexam()
                v.setlog(on=False)
        else:
            pass

        completed.append(sublist[0])
        quit = raw_input('Finished with directory. Continue to next directory?'
                         '(y/n): ')
        if quit == 'n':
            print('Exiting imexam loop process')
            break
        else:
            pass

    print('Completed these directories:')
    for directory in completed:
        print(directory)

    print('Still undone: ')
    for todoitem in imgdirlists:
        if todoitem[0] not in completed:
            print(todoitem[0])

print('Shutting down. Goodbye!')



