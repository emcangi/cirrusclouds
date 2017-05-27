# ============================================================================ #
# Eryn Cangi
# 26 May 2017
# Script #3b of 5 to run
# Simple script to build terminal commands for running polyphot manually based
# on a certain files_and_params.txt file.
# Use any way you like. Can easily be run as-is in Sublime.
# ============================================================================ #

thepath = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera/' \
         '{}'
setkey = '/{}/'   # key to use to find the right set of stuff
expkey = ''  # only fill in if there is more than one exposure

# Get input from user
dated_folder = raw_input('Enter the dated image folder: ')
set_input = raw_input('Enter the name of the set folder to generate commnads '
                   'for: ')
e_input = raw_input('Enter the exposure to look for (press enter if none): ')

# set up some more variables we will need
thefile = thepath.format(dated_folder) + '/files_and_params.txt'
setkey = setkey.format(set_input)
expkey = expkey.format(e_input)

# this chops off the _# extension to a folder, where _# is my system for
# prioritizing data sets.
if '_' in dated_folder:
    date = dated_folder.split('_')[0]
else:
    date = dated_folder

# for building the commands and lists of commands
BASE = 'polyphot {} coords="" polygons="" output="{}" sigma={} itime={} ' \
       'ifilter={} skyvalue={} interactive=yes'
cmds_unsort = []  # list of commands, used to sort before printing
cmds_sort = []

# Loop through lines in the file and extract necessary info, add commands to
# unsorted list
with open(thefile, 'r') as f:
    junk = f.readline()
    for line in f:
        data = line.split()
        if data:
            if setkey in data[7] and expkey in data[7]:
                fn = data[0]
                outputfn = fn[:-4] + '_photometry_manual'
                sig = data[2]
                sky = data[1]
                e = data[4]
                filt = data[5] + ',' + data[6]
                cmds_unsort.append(BASE.format(fn, outputfn, sig, e, filt, sky))

# this is used for sorting the commands
possfilters = ['11', '15', '47', '82a', 'LRGBred', 'LRGBgreen',
                       'LRGBblue', 'LRGBluminance', 'None']

# sort the commands based on the filter
for fil in possfilters:
    for c in cmds_unsort:
        if 'ifilter={}'.format(fil) in c:
            cmds_sort.append(c)

# write out the sorted commands to the file
fn = 'man_polyphot_cmds_{}_{}.txt'
writepath = thepath+setkey+fn
import pickle
with open(writepath.format(dated_folder, date, set_input), 'w') as f:
    for cmd in cmds_sort:
        f.write(cmd)

