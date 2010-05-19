#!/usr/bin/env python

from distutils.core import setup

version = "0.2"

"""Setup script for pygpx"""

setup (
    name = "pygpx",
    version = version,
    description = "A module for parsing GPX files.",
    long_description = "This module allows you to parse and extract data from GPX files.",
    author = "Ben Leslie",
    author_email = "benno@benno.id.au",
    url = "http://www.benno.id.au/code/pygpx/",
    download_url = "http://www.benno.id.au/code/pygpx/pygpx-%s.tar.gz" % version,
    license = "http://www.opensource.org/licenses/mit-license.php",
    py_modules = ["pygpx"],
    platforms = ["any"],
    classifiers = ["Development Status :: 4 - Alpha",
                   "Intended Audience :: Developers",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "License :: OSI Approved :: MIT License"
                   ]
    )
    
    
