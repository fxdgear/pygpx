This library is designed for parsing and manipulating gpx files in python.

This project originally started: http://www.benno.id.au/code/pygpx/ by Ben Leslie.

I've picked up this project to update it to v1.1 of GPX so I can use this project with some of my personal work.
Prerequisites
-------------

Required by pygpx:

    * lxml


pygpx has now been converted to v0.3.
	* v0.3 now supports the GPX schema v1.1. All files using pygpx should validate against v1.1
	* pygpx now ships with the schema v1.1 and will run a validation test before running.
	* Garmin supports exporting files to GPX valid against v1.1 so you shouldn't have any problems if you're using garmin software.
	
API example:
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
                print trkpnt.time
        
        print track.full_duration
        print track.distance
