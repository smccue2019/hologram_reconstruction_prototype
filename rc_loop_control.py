#!/usr/bin/env python

import glob
from configparser import SafeConfigParser
from numpy import floor
#from pathlib import Path

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def read_config(config_path):
    ini=SafeConfigParser()
    ini.read(config_path)

    my_params={}
    my_params["CPU_count"]=ini.getint('Proc','CPU_count')
    my_params["my_imagedir"]=ini.get('File','Imagedir')
    my_params["my_outdir"]=ini.get('File','Outdir')
    my_params["my_bindir"]=ini.get('File','Bindir')

    check_read = True
    if check_read == True:
        print ('CPU_count:%s' % (my_params["CPU_count"]))
        print ('my_imagedir:%s' % (my_params["my_imagedir"]))
        print ('my_outdir:%s' % (my_params["my_outdir"]))
        print ('my_bindir:%s' % (my_params["my_bindir"]))
        
    return(my_params)

mp = read_config('/media/jhowland/47f712eb-df76-4093-bd1f-57bf84e4215c/SJM/holo_rc.ini')
# Initial assumption: all tiff images in a directory are to be
# reconstructed.

image_glob = mp["my_imagedir"] + '/*.tif'

files_list = sorted(glob.glob(image_glob))
files_count = len(files_list)
loop_counter = 0

# Compute how many image files to be allotted to each loop.
# There will be a short list of files made up of the remainder
# of the full list, could be as short as 0 files.
# Divide the full image list into CPU_count-1 equal blocklengths
# setting aside one for the last, short block 
files_per_instance = int(floor(files_count/(mp["CPU_count"]-1)))

files_remain_cnt = files_count - ((mp["CPU_count"]-1) * files_per_instance)

# Loop over the sublists that are fully populated by "files_per_instance"
# files.
for ctr in range(mp["CPU_count"]-1):
    start = ctr*files_per_instance
    end=start+files_per_instance-1
    sublist = files_list[start:end]
    outfile = '%s/loop%s_filelist.txt'  % (mp["my_outdir"], str(loop_counter).zfill(2))
    outfh = open(outfile, 'w')
    for fname in sublist:
        fname = fname + '\n'
        outfh.write(fname)
    outfh.close()

    # Construct the command that invokes the reconstruction script on each
    # of the CPUs provided for the job.
    cmd = '%s/rc_loop.py %s /media/jhowland/Data/Holograms/bg_2018081704-6.hd5 %d' % (mp["my_bindir"],outfile,loop_counter)
    print('%s' % (cmd))

    loop_counter = loop_counter + 1
    
print('Invoked %d instances of reconstruction scripts of %d images each' % (loop_counter, files_per_instance))

print('Invoking one more instance of reconstruction script of %d images' % (files_remain_cnt))


