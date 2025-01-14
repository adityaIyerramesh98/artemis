.. _building-source:

Building/installing WarpX
=========================

WarpX can be built with various options. This page describes the most basic
build, and points to instructions for more advanced builds.

Even if you are interested in more advanced builds, we recommend reading this
page first.

Downloading the source code
---------------------------

Clone the source codes of WarpX, and its dependencies AMReX and PICSAR into one
single directory (e.g. ``warpx_directory``):

::

    mkdir warpx_directory
    cd warpx_directory
    git clone https://github.com/ECP-WarpX/WarpX.git
    git clone https://github.com/ECP-WarpX/picsar.git
    git clone https://github.com/AMReX-Codes/amrex.git

Basic compilation
-----------------

WarpX requires a C/C++ and Fortran compiler (e.g., GCC or Intel) and an
MPI implementation (e.g., OpenMPI or MPICH). Then ``cd`` into the directory
``WarpX`` and type

::

    make -j 4

This will generate an executable file in the ``Bin`` directory.

Compile-time vs. run-time options
---------------------------------

WarpX has multiple compile-time and run-time options. The compilation
options are set in the file ``GNUmakefile``. The default
options correspond to an optimized code for 3D geometry. The main compile-time
options are:

    * ``DIM=3`` or ``2``: Geometry of the simulation (note that running an executable compiled for 3D with a 2D input file will crash).
    * ``DEBUG=FALSE`` or ``TRUE``: Compiling in ``DEBUG`` mode can help tremendously during code development.
    * ``USE_PSATD=FALSE`` or ``TRUE``: Compile the Pseudo-Spectral Analytical Time Domain Maxwell solver. Requires an FFT library.
    * ``USE_RZ=FALSE`` or ``TRUE``: Compile for 2D axisymmetric geometry.
    * ``COMP=gcc`` or ``intel``: Compiler.
    * ``USE_MPI=TRUE`` or ``FALSE``: Whether to compile with MPI support.
    * ``USE_OMP=TRUE`` or ``FALSE``: Whether to compile with OpenMP support.
    * ``USE_GPU=TRUE`` or ``FALSE``: Whether to compile for Nvidia GPUs (requires CUDA).
    * ``USE_OPENPMD=TRUE`` or ``FALSE``: Whether to support openPMD for I/O (requires openPMD-api).
    * ``USE_LLG=TRUE`` or ``FALSE``: Whether to compile with Landau-Lifshitz-Gilbert (LLG) model to compute magnetization.
    * ``MPI_THREAD_MULTIPLE=TRUE`` or ``FALSE``: Whether to initialize MPI with thread multiple support. Required to use asynchronous IO with more than ``amrex.async_out_nfiles`` (by default, 64) MPI tasks. Please see :doc:`../visualization/visualization` for more information.
    * ``PRECISION=FLOAT USE_SINGLE_PRECISION_PARTICLES=TRUE``: Switch from default double precision to single precision (experimental).

For a description of these different options, see the `corresponding page <https://amrex-codes.github.io/amrex/docs_html/BuildingAMReX.html>`__ in the AMReX documentation.

Alternatively, instead of modifying the file ``GNUmakefile``, you can directly pass the options in command line ; for instance:

::

   make -j 4 USE_OMP=FALSE

In order to clean a previously compiled version (typically useful for troubleshooting, if you encounter unexpected compilation errors):

::

    make realclean

before re-attempting compilation.

Preview: CMake Build System
---------------------------

We are currently transitioning to support CMake as our primary build system.
Until we have transitioned our documentation and functionality completely, please read the following preview section for details.

.. toctree::
   :maxdepth: 1

   cmake

Advanced building instructions
------------------------------

.. toctree::
   :maxdepth: 1

   openpmd
   spectral
   rzgeometry
   gpu_local
   python
   spack

Building for specific platforms
-------------------------------

.. toctree::
   :maxdepth: 1

   cori
   summit
   juwels
   lassen
   quartz
