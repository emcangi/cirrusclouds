#!/home/emc/anaconda3/envs/astroconda/bin/python

# ============================================================================ #
# Helper script to iterate through the images and allow interaction with DS9 to
# get the sky values
# ============================================================================ #

import sys
from os import walk
import imexam
from box_stats import real_m_stats

mypath = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera'

#Collect the address for the current DS9 window
ds9data = imexam.list_active_ds9()
ds9data = ds9data.split()
XPA_METHOD = ds9data[3]

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
v.zoom(0.5)
print('DS9 successfully connected\n')

mydic = {"i": (real_m_stats, "Modified stat display function, displays all the "
         "same stats that are normally displayed in imexamine's 'm' task")}
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

    # NOT WORKING-------------------
    # # Now the first list in imgdirlists should be new working directory and files
    # imgnamelist = imgdirlists_copy[0][1]  # alias to deal with long variable
    # #imgnamelist = sorted(imgnamelist)   # sort to avoid deleting not-done images
    # #print('Sorted:')
    # print(imgnamelist)
    # loc = imgnamelist.index(start)  # get start index
    # print('Found {} at index {}'.format(start, loc))
    # imgdirlists_copy[0][1] = imgnamelist[loc:]  # remove imgs before start
    imgdirlists = list(imgdirlists_copy)   # Replace originals with updated copies
else:
    pass

print('Starting imexam loop...')

# loop through images. Code will automatically pause to allow interaction. q to
# continue to next image.
completed = []

for sublist in imgdirlists:
    imgnames = sublist[1]
    curdir = sublist[0]
    if sublist[1]:
        for image in imgnames:
            #print('Using directory {}, image {}'.format(imgdir, image))
            path = "{}/{}".format(curdir, image)
            v.load_fits(path)
            v.setlog(filename="{}_sky".format(image[:-4]), on=True)
            v.imexam()
            v.setlog(filename="{}_sky".format(image[:-4]), on=False)
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



