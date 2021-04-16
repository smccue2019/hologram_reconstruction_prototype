#!/usr/bin/env python3
import numpy as np
import holopy as hp
from holopy.core.io import load, load_average, save, save_image
from holopy.core.process.img_proc import bg_correct
import sys
import glob
import time
import os
import shutil
from configparser import SafeConfigParser

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

# Create background image by processing specified tiff images. If the
# number of images exceeds 'experimentally_determined_max_count', the
# tiff image list is split into sublists of 'image_count_to_average',
# a value calculated by the program. The sublists are averaged into temporary
# averages, and then in turn they are averaged  into a background image
# as final result.

# Because an "average of averages" is only legitimate if each of the
# first round of averages results from the same number of tiff images,
# it is likely that there will be some images at the end of the glob list
# that are not used in computing the final average. The user can adjust
# the wildcards in the file glob (to choose images from the same dive for
# instance), or <somewhat> the of elements that go into  the round one
# averages. This is done by making 'sort_flag' (above) 'True' or 'False'.
# 'True' forces the list to be sorted, whereas 'False' means the list
# returns from the glob call in the "random" order of the glob routine.

# Earlier I found that the largest count of images that were successfully
# averaged was 18, on the laptop I used and from the image set I had. I
# expect that max count will change according to image characteristics and
# computing platform.

# Handle command line arguments
# No arg, make a background averaged from all tiff files in directory.
# One arg, use the arg as the glob for which files in directory to use.
# 'sort_flag', above, defines whether the list returned by the glob is
# sorted by name, or returns in the random? order the 'glob' call offers.

# SJM smccue@whoi.edu
# WHOI
# March 2019

if len(sys.argv) == 1:
    my_glob=mp["my_imagedir"] + '/*.tif'

elif len(sys.argv) == 2:
    my_glob = mp["my_imagedir"] + '/' + sys.argv[1]

print('file glob to generate a background average is %s' % (my_glob))

# Choose whether to impose sorting on list so that the user can predict
# which images are used and which are not.
if mp["my_sort_flag"] == True:
    files_list = sorted(glob.glob(my_glob))
else:
    files_list = glob.glob(my_glob)

# Determine params to divide full files list into sublists, and process each.
files_count = len(files_list)
experimentally_determined_max_count = mp["max_count"]

if files_count > (experimentally_determined_max_count * experimentally_determined_max_count):
    print('File selection count exceeds resource capabilities\n')
    print('Will process %d of %d files into a background image, performing average of averages\n' % (experimentally_determined_max_count * experimentally_determined_max_count, files_count))
    image_count_to_average = experimentally_determined_max_count
    files_list_orig = files_list
    files_list = files_list_orig[0:(experimentally_determined_max_count * experimentally_determined_max_count)] 

image_count_to_average = int(round(np.sqrt(files_count)))


start = time.time()
tmp_avg_filelist = []
for index in range(1, files_count,  image_count_to_average):
    tmp_avg_filename = '%s/bg_temp_idx%s-%s.tif' % (mp["my_outdir"], str(index).zfill(2), str(index+image_count_to_average-1).zfill(2))

    my_loop_count=0
    for file in files_list[index-1:index+image_count_to_average-1]:
        my_loop_count = my_loop_count + 1
        tmp_filename = '/tmp/holo_%s.tif' % (str(my_loop_count).zfill(2))
        print('Copying %s to %s' % (file, tmp_filename))
        shutil.copy2(file, tmp_filename)

# Round one, average individual images into averages.
    try:
        print('Averaging above files into intermediate background file %s' % (tmp_avg_filename))
        bg = load_average('/tmp', image_glob='/tmp/holo_*.tif',spacing=mp["my_spacing"],illum_wavelen=mp["my_illum_wavelength"],medium_index=mp["my_medium_index"],channel='all')
        save_image(tmp_avg_filename,bg)
        tmp_avg_filelist.append(tmp_avg_filename)
    except BadImage:
        print('BadImage exception raised by bg_correct. Failed average of this group\n')
        continue
    except LoadError:
        print('LoadError exception raised by bg_correct. Failed average of this group\n')
        continue
    
    tmp_files = glob.glob('/tmp/holo_*.tif')
    for tmp_file in sorted(tmp_files):
        print('Deleting %s' % (tmp_file))
        os.remove(tmp_file)


# Round two, average the averages to get final product
try:
    outfile = '%stest_bg.hd5' % (mp["my_outdir"])
    print('Averaging the averages into final background file %s' % (outfile))
    bg = load_average(mp["my_outdir"], image_glob='bg_temp_idx*.tif',spacing=mp["my_spacing"],illum_wavelen=mp["my_illum_wavelength"],medium_index=mp["my_medium_index"],channel='all')
    save((mp["my_outdir"] + '/' + 'test_bg.hd5'),bg)
except BadImage:
    print('BadImage exception raised by bg_correct. Failed average of this group\n')
except LoadError:
    print('LoadError exception raised by bg_correct. Failed average of this group\n')
    
now = time.time()
print('Elapsed time is %d' % (now-start))


