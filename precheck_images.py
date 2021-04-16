#!/usr/bin/env python3

import holopy as hp
from holopy.core.io import load,save
from holopy.core.errors import BadImage, LoadError
import glob, time
from configparser import SafeConfigParser


def read_config(config_path):
    ini=SafeConfigParser()
    ini.read(config_path)

    my_params={}
    my_params["my_spacing"]=int(ini.get('Optics','Spacing'))
    my_params["my_illum_wavelength"]=int(ini.get('Optics','Illum_wavelength'))
    my_params["my_medium_index"]=ini.get('Optics','Medium_index')
    my_params["my_imagedir"]=ini.get('File','Imagedir')

    check_read = True
    if check_read == True:
        print ('my_spacing:%s' % (my_params["my_spacing"]))
        print ('my_illum_wavelength:%s' % (my_params["my_illum_wavelength"]))
        print ('my_medium_index:%s' % (my_params["my_medium_index"]))
        print ('my_imagedir:%s' % (my_params["my_imagedir"]))
        

    return(my_params)

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

mp=read_config('/media/jhowland/47f712eb-df76-4093-bd1f-57bf84e4215c/SJM/holo_rc.ini')

my_glob=mp["my_imagedir"] + '/*.tif'
files_list = sorted(glob.glob(my_glob))
file_counter = 0

start = time.time()

for file in files_list:
    file_counter = file_counter+1
    
    print('----------------------------------')
    print('Checking file number: %d: %s' % (file_counter, file))
    print('----------------------------------')

    try:
        orig_tif = hp.load_image(file,spacing=num(mp["my_spacing"]),illum_wavelen=num(mp["my_illum_wavelength"]),medium_index=num(mp["my_medium_index"]),channel='all')
        #        orig_tif = hp.load_image(file,spacing=7400,illum_wavelen=658,medium_index=1.33,channel=[0,1,2])
        #        orig_tif = hp.load_image(file,spacing=num(mp["my_spacing"]),illum_wavelen=num(mp["my_illum_wavelength"]),medium_index=num(mp["my_medium_index"]),channel=[0,1,2])
    except LoadError:
        print('********* io.py LoadError **************')
        print('Error loading %s' % (file))
        continue
    except BadImage:
        print('********* io.py BadImage **************')
        print('Error loading %s' % (file))
        continue

    orig_tif = []

    end = time.time()

    elapsed = end - start
    print('Ongoing elapsed time is %d' % (elapsed))
