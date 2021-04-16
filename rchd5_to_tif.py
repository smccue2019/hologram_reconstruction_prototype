#!/usr/bin/env python3

import matplotlib.pyplot as plt
import holopy as hp
from holopy.core.io import load
from pathlib import Path
import glob, time
from configparser import SafeConfigParser

# Be sure to set matplotlib qt if using Jupyter Qt Console.

# Use loop_counter_upper_limit to control how many files are processed
# Remnant from development. It should be removed for production but it has
# some value, so make large such that it's effectively removed.
loop_counter_upper_limit = 1000000

# To make changes in behavior edit the config file.
config_path_n_name = '/media/jhowland/47f712eb-df76-4093-bd1f-57bf84e4215c/SJM/holo_rc.ini'

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

    my_params["my_spacing"]=num(ini.get('Optics','Spacing'))
    my_params["my_illum_wavelength"]=num(ini.get('Optics','Illum_wavelength'))
    my_params["my_medium_index"]=num(ini.get('Optics','Medium_index'))

    my_params["my_imagedir"]=ini.get('File','Imagedir')
    my_params["my_outdir"]=ini.get('File','Outdir')

    check_read = True
    if check_read == True:
        print ('sort_flag:%s' % (my_params["my_sort_flag"]))
        print ('max_count:%s' % (my_params["max_count"]))
        print ('my_spacing:%s' % (my_params["my_spacing"]))
        print ('my_illum_wavelength:%s' % (my_params["my_illum_wavelength"]))
        print ('my_medium_index:%s' % (my_params["my_medium_index"]))
        print ('my_imagedir:%s' % (my_params["my_imagedir"]))
        print ('my_outdir:%s' % (my_params["my_outdir"]))
        
    return(my_params)

mp=read_config(config_path_n_name)

# Presumably the hd5 files are in the previous step's output directory.
files_glob = '%s/H*.hd5' % (mp["my_outdir"])
if mp["my_sort_flag"] == True:
    files_list = sorted(glob.glob(files_glob))
else:
    files_list = glob.glob(files_glob)


start = time.time()
loop_counter=0

plt.ion()

for in_recon in files_list:
    loop_counter = loop_counter + 1
    print ('File counter: %d\n' % (loop_counter))
    if loop_counter == loop_counter_upper_limit + 1:
        break
    else:
        infullpath = Path(in_recon)
        infilebasename = infullpath.name
        outfile = infilebasename.replace('hd5','png')
        outfullpath = ('./%s' % (outfile))
        outexistence = Path(outfullpath)
        if outexistence.is_file():
            print('Skipping processing of %s cause an outfile exists' % (outfullpath))
        else:

            print('%s\n' % (in_recon))
            stack = hp.load(in_recon)
            fig = hp.show(stack)
            plt.savefig(outfullpath)
            plt.close(fig)
            stack = []
            
            now = time.time()
            elapsed = now-start
            print('Elapsed time is %d seconds' % (elapsed))

plt.ioff()
