# hologram_reconstruction_prototype
Hologram reconstruction prototype using HoloPy, applied to a collection of captures from a bona fide research cruise.

The following content is a copy of a README file that accompanies the code.

README for first development set, ITZ hologram processing.
----------------------------------------------------------
SJM
smccue@whoi.edu
21Mar19


Describes initial efforts at developing batch procedures for the processing
of holgrams. The images captured at sea are interference patterns reflected
off of materials and animals as they float in a parcel of water. Many inages
were captured. This document describes the processing of these images from
interference pattern to image of the material or animal.


1. Background

Core processing uses the HoloPy library from a Harvard Project. HoloPy routines
are used to build an image of animal or material by the process called
"reconstruction". The routines "propagate" the interference pattern through
a series of slices (these slice intervals are defined in code by the user) in
conjunction with the known optical characteristics of the system to create the
image. The demand that reconstruction places on computing resources is not
trivial.

Batch processing consists of invoking the steps over a collection of
images while managing the demands on computational resources. Development
was performed on a highly resourced laptop computer, but a laptop computer
nonetheless. The computational limits of the laptop were assessed and
processing was implemented within those limits. It is expected that batch
processing will be transferred to much more capable computers and invoked
on large collections of images. The scripts described below offer some
levels of adaptability to accommodate computers with different levels of
resources- some adaptation is through user definition and some is
programmatic.

2. Processing steps

   1. Generate background image.
      HoloPy developers recommend the generation of a background image for
      later use in reconstruction. A background is an average of images,
      and is presumed to capture systematic noise (such as a permanent
      distortion of the image field).

   2. Perform reconstruction
      Reconstruction computes from interference pattern back to the shape
      of the object that caused that pattern. Computation is performed on
      a stack of discrete slices that is defined by the user. The definition
      of this stack is the user's main way of adapting the process to
      available computing processes, primarily through definition of the
      number of intervals over which to propagate the reconstruction.

   3. Generate images of the reconstructions.
      Too much of the development computer's resources were demanded when
      trying to both reconstruct and image the reconstruction in the same
      step. So these were separated into sequential steps. For each
      reconstruction file, produce an image that users can review (for
      presence of anaimals of interest).
      
3. Routines

   Developed started under Anaconda/Spyder but I judged that these were
   using resources best devoted to the processing of holograms. In the
   end they were turned into unix shell/command line programs. Success on
   other computers will depend on how python3, numpy, and HoloPy are installed.

   The routines obtain some user-defined information through a DOS-style
   config file, such as optics and path information. Other user-defined
   information is passed as command line arguments.

    1. gen_bg2.py
       Averages as many images as computing resources allows. This limit
       is determined by how many images the HoloPy routine 'load_average'
       can process without resources issues. On the development laptop
       this limit was at least 18 example images, less than 25 images.

       This script creates an "average of averages". For the final result to
       be a legitimate average, each of the initial averages must be computed
       from the same number of elements (images). Then, these can also be
       averaged.

       Because of this averaging rule, the maximum count of images to make up
       a background image is the square of the experimentally determined
       max count for 'load_average'.

       The user can define a file glob to invoke sub-selection of file names
       to be used in the background image. This glob is passed as a command
       line argument to 'gen_bg2.py'.

     2. rc_loop.py & rc_loop_control.py
        Perform reconstruction on a collection of files.
        'rc_loop.py': Loops though a list of files that is given in a text
        file. Saves the reconstructions in files of HDF v5 format. 
        'rc_loop_control.py': Given a collection of images in a directory and
        a count of the number of CPUs that a system can devote to processing,
        'rc_loop_control.py'
           - divides the full list of files into sublists and generates a
           collection of text files for the sublists,
           - invokes CPU_count instances of 'rc_loop.py' and tells
           each instance which sublist it is to process.

      3. rc_hd5_to_tif.py
         Now that reconstructions have been built, create images of them.
         Performed by looping over a glob 


