#!/usr/bin/env python

import distutils.command.install_lib
import distutils.command.build
from distutils.core import setup
import os
import shutil

class MyInstallLib(distutils.command.install_lib.install_lib):
    def run(self):
        distutils.command.install_lib.install_lib.run(self)
        for fn in self.get_outputs():
            if fn.endswith("/qapgen") or fn.endswith("/qapgenf") \
                    or fn.endswith("/qapinput") or fn.endswith("/qapprove") \
                    or fn.endswith("/qapver"):
                # copied from distutils source - make the binaries executable
                mode = ((os.stat(fn).st_mode) | 0555) & 07777
                distutils.log.info("changing mode of %s to %o", fn, mode)
                os.chmod(fn, mode)

apps = ['qapgen', 'qapgenf', 'qapinput', 'qapcoeffcache', 'qapprove', 'qapver']
exefix = '.exe' if os.name == 'nt' else ''

class MyBuildLib(distutils.command.build.build):
    def run(self):
        for app in apps:
            fl = 'qaptools/' + app + exefix
            tr = os.path.join("pysnark", fl)
            if not os.path.isfile('qaptools/' + app + exefix):
                raise RuntimeError("*** Missing qaptools executable " + fl + ", please compile first")
            self.announce("Copying qaptools executable " + fl + " info pysnark source directory", level=distutils.log.INFO)
            shutil.copyfile(fl, tr)
            mode = ((os.stat(tr).st_mode) | 0555) & 07777
            distutils.log.info("changing mode of %s to %o", tr, mode)
            os.chmod(tr, mode)

        distutils.command.build.build.run(self)

setup(name='PySNARK',
      version='0.1',
      description='Python zk-SNARK execution environment',
      author='Meilof Veeningen',
      author_email='meilof@gmail.com',
      url='https://github.com/meilof/pysnark',
      packages=['pysnark', 'pysnark.lib', 'pysnark.qaptools'],
      package_data={'pysnark': ['lib/gghkey.txt', 'contracts/*.sol'],
                    'pysnark.qaptools': [ app+exefix for app in apps ]},
      cmdclass={'build': MyBuildLib, 'install_lib': MyInstallLib},
      )
