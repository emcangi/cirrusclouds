#!/home/emc/anaconda3/envs/astroconda/bin/python

# ============================================================================ #
# Summarize photometry outputs for an image file
# Eryn Cangi
# 4 October 2016
# ============================================================================ #

import os
from pandas import DataFrame

# Gather the image filename ----------------------------------------------------

default = '/home/emc/GoogleDrive/Phys/Research/BothunLab' \
          '/WorkingArea/{}'

print('Current default path to the photometry file is {}, where curly '
          'braces represent the working directory\n'.format(default))

    choice = raw_input('How do you want to identify the photometry file?\n'
                       '[1]: Enter full path to the file\n'
                       '[2]: Enter just the file name (use the default path)\n'
                       'Your choice: ')

    if choice == '1':
        phot_file = raw_input('Please input path: ')
    elif choice == '2':
        d = raw_input('Please input file name: ')
        phot_file = default.format(d)
    else:
        while choice != 1 or choice != 2:
            choice = raw_input('Please enter either 1 or 2:\n'
                               '[1]: Enter full path to the file\n'
                               '[2]: Enter just the file name ('
                               	'use the default path)\n\n')

output_file = phot_file + "_data"

os.system("tail -n +83 {} > {}".format(phot_file, output_file))

# Construct initial lists of information from the photometry file --------------
ln_cnt = 1
data = []
grids = []
grids_sublist = 0

with open(output_file, 'r') as f:
    for line in f:
        # finds lines that end in 5 only--these are the ones with data
        if ln_cnt % 5 == 0 and ln_cnt % 10 != 0:
            data.append(line)
        # check what the last digit of the line number is    
        last_digit = ln_cnt % 10 
        # these lines will hold vertices of the cell 
        if last_digit in [7, 8, 9, 0]:
            if last_digit == 7:
                grids.append([])  # start a new sublist if it is a new cell
            grids[grids_sublist].append(line)
            if last_digit == 0:
                grids_sublist += 1
        ln_cnt += 1  # we have to keep track since Python doesn't

# Construct data display table -------------------------------------------------
             
big_table = [['Counts', 'Area(pixels)', 'Flux counts', 'Mag', 'MERR', 'PIER', 
			  'PERROR', 'v1', 'v2', 'v3', 'v4']]

for e1, e2 in zip(data, grids):
    datum = e1.split()  # extract useful info
    del datum[-1]  # gets rid of some garbage characters trailing on the line

    # appends vertices in neat ordered-pair format
    for el in e2:
        datum.append(el.strip().split()[:2])

    # add data and vertices to a big table
    big_table.append(datum)

# Make a Pandas dataframe
headers = big_table[0]
df = DataFrame(big_table[1:], columns=headers)

# Get the average counts for the whole image
counts = pd.to_numeric(df['Counts'])
mean_counts = counts.mean()

print('Mean counts: '.format(mean_counts))