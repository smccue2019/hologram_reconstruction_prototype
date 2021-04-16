#!/usr/bin/env python3

import numpy as np
import holopy as hp
from holopy.core.io import load,save
from holopy.core.process.img_proc import bg_correct
from holopy.core.errors import BadImage
import glob, time, sys
from pathlib import Path
from configparser import SafeConfigParser

# Perform reconstruction under the control of a higher level script that
# determines the images to be processed and the background image that
# normalizes the images.
#
# That means that the controlling script MUST pass into this one the
# glob that builds the image list, plus the path + name of the background
# file (a .hd5 format file). At the moment these will be command line
# arguments.

if not len(sys.argv) == 4:
    print('Must pass three command line arg. Passed %d args. Quitting\n' % \
          (len(sys.argv)-1))
    print('Usage %s in_list_filename background_image_full_path loopID' % (sys.argv[0]))
    exit

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def read_config(config_path):
    ini=SafeConfigParser()
    ini.read(config_path)

    my_params={}
    my_params["my_sort_flag"]=ini.getboolean('Proc','Sort_flag')
    my_params["max_count"]=num(ini.getint('Proc','Max_avg_cnt'))
    my_params["stack_length"]=num(ini.getint('Proc','Stack_count'))
    my_params["my_cfsp_cnt"]=num(ini.getint('Proc','Cfsp_count'))

    my_params["my_spacing"]=num(ini.get('Optics','Spacing'))
    my_params["my_illum_wavelength"]=num(ini.get('Optics','Illum_wavelength'))
    my_params["my_medium_index"]=num(ini.get('Optics','Medium_index'))

    my_params["my_imagedir"]=ini.get('File','Imagedir')
    my_params["my_outdir"]=ini.get('File','Outdir')

    check_read = True
    if check_read == True:
        print ('sort_flag:%s' % (my_params["my_sort_flag"]))
        print ('max_count:%s' % (my_params["max_count"]))
        print ('stack length:%d' % (my_params["stack_length"]))
        print ('my_spacing:%s' % (my_params["my_spacing"]))
        print ('my_illum_wavelength:%s' % (my_params["my_illum_wavelength"]))
        print ('my_medium_index:%s' % (my_params["my_medium_index"]))
        print ('my_imagedir:%s' % (my_params["my_imagedir"]))
        print ('my_outdir:%s' % (my_params["my_outdir"]))
        print ('my_cfsp_cnt:%s' % (my_params["my_cfsp_cnt"]))
        
    return(my_params)

mp = read_config('/media/jhowland/47f712eb-df76-4093-bd1f-57bf84e4215c/SJM/holo_rc.ini')

file_counter = 0

bg=load(sys.argv[2])
loopID = sys.argv[3]

zstack = np.linspace(0, 1000000, mp["stack_length"])

start = time.time()
print('Starting loop %s\n' % (loopID))

with open(sys.argv[1]) as list_in_file:
    for file in list_in_file:
        file = file.rstrip()
        
        file_counter = file_counter+1

        print('----------------------------------')
        print('file number: %d: %s' % (file_counter, file))
        print('----------------------------------')
        infullpath = Path(file)
        infilebasename = infullpath.name
        outfilehd5 = infilebasename.replace('tif','hd5')
        outfullpathhd5 = ('%s/%s' % (mp["my_outdir"], outfilehd5))
        outexistence = Path(outfullpathhd5)
        if outexistence.is_file():
            print('Skipping processing of %s cause an outfile exists' % (outfullpathhd5))
        else:
            print('Processing to yield %s' % (outfullpathhd5))
            orig_tif = hp.load_image(file,spacing=mp["my_spacing"],illum_wavelen=mp["my_illum_wavelength"],medium_index=mp["my_medium_index"], channel='all')

            try:
                holo = bg_correct(orig_tif, bg)
                rec_vol = hp.propagate(holo, zstack, cfsp=mp["my_cfsp_cnt"])
                save(outfullpathhd5, rec_vol)
 
            except BadImage as e:
                print('Exception raised by bg_correct %s' % (e))
                continue
            
end = time.time()
elapsed = end - start
print('Elapsed time for loopID %s is %d' % (loopID, elapsed))
