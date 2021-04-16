#!/usr/bin/env python3
import numpy as np
import holopy as hp
from holopy.core.io import load, load_average, save
from holopy.core.process.img_proc import bg_correct

# To create the background image and save it for future use.
# To date the successful glob was for 18 images, H.20180817.0[456].tif.
# More than that appears to exceed memory limtations. However, this
# should be revisited. I leter learned that the Anaconda kernel with
# Spyder does not practice parsimonipus memory management and it
# could be that prior experiments retained memory that could have
# been used to average more images.
# SJM Mar 4 2019
bg = load_average('..', image_glob='/home/jhowland/WHOI_holo_images/H.20180817.0[456]*.tif',spacing=7400,illum_wavelen=658,medium_index=1.33,channel='all')
save('bg_2018081704-6.hd5',bg)
