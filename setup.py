import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
# with open(os.path.join(here, 'README.rst')) as f:
#       long_description = f.read()

def get_version(string):
      """ Parse the version number variable __version__ from a script. """
      import re
      version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
      version_str = re.search(version_re, string, re.M).group(1)
      return version_str


setup(name='thex',
    #   version=get_version(open('src/svim_asm/svim-asm').read()),
      description='',
    #   long_description=long_description,
      url='https://github.com/harris-2374/conda-dash-app.git',
      author='Andrew Harris',
      author_email='ajharris.2374@gmail.com',
      license='GPLv3',
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Console',
      'Intended Audience :: Science/Research',
      'Topic :: Scientific/Engineering :: Bio-Informatics',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Programming Language :: Python :: 3.6'
      ],
      packages = find_packages("src"),
      package_dir = {"": "src"},
      scripts=['src/thex', 'src/app.py'],
)

