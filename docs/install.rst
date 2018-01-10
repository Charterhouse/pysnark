Installation guide
==================

Unix (Linux/MacOS/...)
----------------------

First, download the PySNARK dependencies, ``ate-pairing`` and ``xbyak``: ::


  git submodule init
  git submodule update


Build the ``ate-pairing`` library: ::

  cd qaptools/ate-pairing
  make SUPPORT_SNARK=1


Build the ``qaptools`` library: ::

  cd qaptools
  make

Build and install the `pysnark` library: ::

  python setup.py install


Windows
-------

PySNARK comes with precompiled Windows executables of ``qaptools``, meaning it is possible to build an install PySNARK by just running: ::

  python setup.py install


To recompiling ``qaptools`` from source, set up a Unix-like build environment such as Mingw with MSYS and use the Unix instructions above.

Using without installation
--------------------------

It is also possible to run PySNARK applications without installing PySNARK. For this, follow the above steps but run ``python setup.py build`` instead of ``python setup.py install``. This makes sure all files are compiled and put in their correct locations. Then, run the application with the ``PYTHONPATH`` environment variable set to the PySNARK library, e.g.: ::

  PYTHONPATH=/path/to/pysnark/sources python script.py
