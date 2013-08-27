This library is designed for parsing and manipulating gpx files in Python.

This project originally started: http://www.benno.id.au/code/pygpx/ by Ben Leslie.
Modified by Nick Lang to work with GPX v1.1: https://github.com/fxdgear/pygpx

I am modifying it further. Changes are in CHANGE-LOG.

Prerequisites
-------------

Required by pygpx:

    * lxml


pygpx has now been converted to v0.3.
	* v0.3 now supports the GPX schema v1.1. All files using pygpx should validate against v1.1
	* pygpx now ships with the schema v1.1 and will run a validation test before running.
	* Garmin supports exporting files to GPX valid against v1.1 so you shouldn't have any problems if you're using garmin software.

Tests
-------

::

    nosetests
	
API example:
--------------

::

    from pygpx import GPX
    gpx = GPX("some_data.gpx")
    tracks = gpx.tracks
    for track in tracks:
        print track.name
        for trkseg in track.trksegs:
            for trkpnt in trkseg.trkpts:
                print trkpnt.lat
                print trkpnt.lon
                print trkpnt.elevation
                print trkpnt.hr
                print trkpnt.time
        
        print track.full_duration()
        print track.distance()
