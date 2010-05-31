"""
A module for parsing GPX files.
"""
from lxml import etree
import os
import math
import datetime

def deg2rad(deg):
    """Convert degrees to radians"""
    return deg / (180 / math.pi)

def datetime_iso(string):
    """Parse an ISO formatted string. E.g:
    2006-01-08T06:45:07Z

    Return a datetime object.
    """
    yr = int(string[0:4])
    mn = int(string[5:7])
    da = int(string[8:10])
    hr = int(string[11:13])
    mi = int(string[14:16])
    se = int(string[17:19])
    #tz = string[19:]
    dt = datetime.datetime(yr, mn, da, hr, mi, se, )
    return dt

class GPXTrackPt:
    """A track point."""

    def __init__(self, node, version):
        """Construct a trackpint given an XML node."""
        self.version = version
        self.lat = float(node.get("lat"))
        self.lon = float(node.get("lon"))
        self.elevation = None
        self.time = None
        for child in node:
            if child.tag == "{http://www.topografix.com/GPX/1/1}time":
                self.time = datetime_iso(child.text)
            elif child.tag == "{http://www.topografix.com/GPX/1/1}ele":
                self.elevation = float(child.text)
            elif child.tag == "{http://www.topografix.com/GPX/1/1}extensions":
                pass
            else:
                raise ValueError("Can't handle node: '%s'" % child.tag)

    def distance(self, other):
        """Compute the distance from this point to another."""
        r = 6378700
        dist = r * math.acos(math.sin(deg2rad(self.lat)) *
                             math.sin(deg2rad(other.lat)) + 
                             math.cos(deg2rad(self.lat)) *
                             math.cos(deg2rad(other.lat)) * 
                             math.cos(deg2rad(self.lon - other.lon)))
        return dist

    def duration(self, other):
        """Return the time difference between two nodes."""
        return other.time - self.time

class GPXTrackSeg:
    """One segment of a GPX track."""
    
    def __init__(self, node, version):
        self.version = version
        self.trkpts = []
        for child in node:
            if child.tag == "{http://www.topografix.com/GPX/1/1}trkpt":
                self.trkpts.append(GPXTrackPt(child, self.version))
            else:
                raise ValueError, "Can't handle node <%s>" % node.nodeName

    def distance(self):
        """Return the distance along the track segment."""
        _length = 0.0
        last_pt = self.trkpts[0]
        for pt in self.trkpts[1:]:
            _length += last_pt.distance(pt)
            last_pt = pt
        return _length

    def duration(self):
        """Return the duration of this track segment."""
        return self.trkpts[0].duration(self.trkpts[-1])

class GPXTrack:
    """A GPX Track, made up of individual segments."""
    
    def __init__(self, node, version):
        """Create a GPX track, give an XML DOM node and the document version."""
        
        self.version = version
        self.trksegs = []
        for child in node:
            if child.tag == "{http://www.topografix.com/GPX/1/1}name":
                self.name = child.text              
            elif child.tag == "{http://www.topografix.com/GPX/1/1}trkseg":
                if len(child) > 0:
                    self.trksegs.append(GPXTrackSeg(child, self.version))
            elif child.tag == "{http://www.topografix.com/GPX/1/1}number":
                self.name = child.text               
            else:
                raise ValueError, "Can't handle node <%s>" % node.nodeName

    def distance(self):
        """Return the distance for this track."""
        try:
            return sum([trkseg.distance() for trkseg in self.trksegs])
        except IndexError:
            print "emtpy track segment"
        
    def duration(self):
        """Return the duration for this track. The sum of the duration
        of all track segments."""
        dur = datetime.timedelta(0)
        for trkseg in self.trksegs:
            dur += trkseg.duration()
        return dur
    
    def full_duration(self):
        """Return the full duration of the track. This does not include
        break time."""
        return self.start().duration(self.end())

    def start(self):
        """Return the starting track point."""
        return self.trksegs[0].trkpts[0]

    def end(self):
        """Return the final track point of this track."""
        return self.trksegs[-1].trkpts[-1]

    def start_time(self):
        """Return the start time of the track."""
        return self.start().time

    def end_time(self):
        """Return the end time of te track."""
        return self.end().time


class GPX:
    """This class allows the manipulation of a GPX document."""
    
    def __init__(self, fd):
        """
        Create a GPX object based on the given file descriptor.
        """
        PATH = os.path.dirname(__file__)
        schema = os.path.join(PATH, "pygpx", "lib","gpx-1_1.xsd")
        print schema
        self.creator = None
        self.time = None
        self.tracks = []
        self.version = ""
        self.metadata = None
        gpx_schema_doc = etree.parse("lib/gpx-1_1.xsd")
        gpx_schema = etree.XMLSchema(gpx_schema_doc)
        self.gpx_doc = etree.parse(fd)
        self.root = self.gpx_doc.getroot()
        
        # Test if this is a GPX file or not and if it's version 1.1
        if self.root.tag != "{http://www.topografix.com/GPX/1/1}gpx":
            raise ValueError("Not a gpx file: '%s'" % fd)
        elif self.root.get("version") != "1.1":
            raise ValueError("Verion %s is not supported. Must use GPX v1.1" % root.get("version"))
        else:
            self.version = self.root.get("version")
        # attempt to validate the xml file against the schema
        try:
            gpx_schema.validate(self.gpx_doc)
        except:
            raise Exception("GPX does not validate: '%s'" % fd) 
        
        # initalize the GPX document for parsing.
        self._init_version()
        
    def _init_version(self):
        """
        Initialize a GPX instance
        """
        self.creator = self.root.get("creator")
        for child in self.root:
            if child.tag == "{http://www.topografix.com/GPX/1/1}time":
                self.time = child[0]
            elif child.tag == "{http://www.topografix.com/GPX/1/1}trk":
                self.tracks.append(GPXTrack(child, self.version))
            elif child.tag == "{http://www.topografix.com/GPX/1/1}metadata":
                self.metadata = child
        