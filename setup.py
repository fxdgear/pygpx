#!/usr/bin/env python

from distutils.core import setup

version = "0.3"

"""Setup script for pygpx"""

setup (
    name = "pygpx",
    version = version,
    description = "A module for parsing GPX files.",
    long_description = "This module allows you to parse and extract data from GPX files.",
    author = "Ben Leslie, Nick Lang",
    author_email = "benno@benno.id.au, nick.lang@gmail.com",
    url = "http://www.github.com/fxdgear/pygpx",
    download_url = "http://github.com/fxdgear/pygpx/zipball/master",
    license = "http://www.opensource.org/licenses/mit-license.php",
    py_modules = ["pygpx.pygpx", "pygpx.lib"],
    platforms = ["any"],
    classifiers = ["Development Status :: 4 - Alpha",
                   "Intended Audience :: Developers",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "License :: OSI Approved :: MIT License"
                   ]
    )
    
    
