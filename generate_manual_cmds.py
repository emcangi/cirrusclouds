# ============================================================================ #
# Eryn Cangi
# 26 May 2017
# Script #3b of 5 to run
# Simple script to build terminal commands for running polyphot manually based
# on a certain files_and_params.txt file.
# Use any way you like. Can easily be run as-is in Sublime.
# ============================================================================ #

# Change these as needed
thepath = '/home/emc/GoogleDrive/Phys/Research/BothunLab/SkyPhotos/NewCamera/' \
         '{}'
setkey = '/{}/'   # key to use to find the right set of stuff
exposurekey = ''  # only fill in if there is more than one exposure

dated_folder = raw_input('Enter the dated image folder: ')
theset = raw_input('Enter the name of the set folder to generate commnads '
                   'for: ')
expkey = raw_input('Enter the exposure to look for (press enter if none): ')

thefile = thepath.format(dated_folder) + '/files_and_params.txt'
setkey = setkey.format(theset)
exposurekey = exposurekey.format(expkey)

if '_' in dated_folder:
    date = dated_folder.split('_')[0]

# do not change the below
BASE = 'polyphot {} coords="" polygons="" output="{}" sigma={} itime={} ' \
       'ifilter={} skyvalue={} interactive=yes'
CMDS_UNSORT = []  # list of commands, used to sort before printing
cmds_sort = ['']*8

with open(thefile, 'r') as f:
    junk = f.readline()
    for line in f:
        data = line.split()
        if data:
            if setkey in data[7] and exposurekey in data[7]:
                fn = data[0]
                outputfn = fn[:-4] + '_photometry_manual'
                sig = data[2]
                sky = data[1]
                e = data[4]
                filt = data[5] + ',' + data[6]
                CMDS_UNSORT.append(BASE.format(fn, outputfn, sig, e, filt, sky))

# This is the ugliest shit I've ever written and it sure isn't Pythonic but
# gosh darn it, it works.

for cmd in CMDS_UNSORT:
    if "ifilter=11" in cmd:
        cmds_sort[0] = cmd
    elif "ifilter=15" in cmd:
        cmds_sort[1] = cmd
    elif "ifilter=47" in cmd:
        cmds_sort[2] = cmd
    elif "ifilter=82a" in cmd:
        cmds_sort[3] = cmd
    elif "ifilter=LRGBred" in cmd:
        cmds_sort[4] = cmd
    elif "ifilter=LRGBgreen" in cmd:
        cmds_sort[5] = cmd
    elif "ifilter=LRGBblue" in cmd:
        cmds_sort[6] = cmd
    elif "ifilter=LRGBluminance" in cmd:
        cmds_sort[7] = cmd
    else:
        pass

fn = 'man_polyphot_cmds_{}_{}.txt'

writepath = thepath+setkey+fn

with open(writepath.format(dated_folder, date, theset), 'w') as f:
    for cmd in cmds_sort:
        f.write(cmd + '\n')



