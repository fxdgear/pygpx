#!/usr/bin/env python

from distutils.core import setup

version = "0.3.1"

"""Setup script for pygpx"""

setup (
    name = "pygpx",
    version = version,
    description = "A module for parsing GPX files.",
    long_description = "This module allows you to parse and extract data from GPX files.",
    author = "Ben Leslie, Nick Lang, Artem Dudarev",
    author_email = "benno@benno.id.au, nick.lang@gmail.com, dudarev@gmail.com",
    url = "http://www.github.com/dudarev/pygpx",
    download_url = "http://github.com/dudarev/pygpx/zipball/master",
    license = "http://www.opensource.org/licenses/mit-license.php",
    packages = ["pygpx"],
    package_dir =  {"pygpx": 'pygpx'},
    package_data = {'pygpx': ['schema/gpx-1_1.xsd']},
    platforms = ["any"],
    classifiers = ["Development Status :: 4 - Alpha",
                   "Intended Audience :: Developers",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "License :: OSI Approved :: MIT License"
                   ]
    )
    
    
