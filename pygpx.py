"""
A module for parsing GPX files.
"""

import math
from xml.dom.minidom import parse
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
        self.lat = float(node.getAttribute("lat"))
        self.lon = float(node.getAttribute("lon"))
        self.elevation = None
        self.time = None
        for node in node.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            if node.nodeName == "time":
                self.time = datetime_iso(node.firstChild.data)
            elif node.nodeName == "ele":
                self.elevation = float(node.firstChild.data)
            else:
                raise ValueError, "Can't handle node", node.nodeName

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
        for node in node.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            elif node.nodeName == "trkpt":
                self.trkpts.append(GPXTrackPt(node, self.version))
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
        for node in node.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            if node.nodeName == "name":
                self.name = node.firstChild.data                
            elif node.nodeName == "trkseg":
                self.trksegs.append(GPXTrackSeg(node, self.version))
            elif node.nodeName == "number":
                self.name = node.firstChild.data                
            else:
                raise ValueError, "Can't handle node <%s>" % node.nodeName

    def distance(self):
        """Return the distance for this track."""
        return sum([trkseg.distance() for trkseg in self.trksegs])
        
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
        """Given a file descriptor, create GPX."""
        self.dom = parse(fd)
        self.creator = None
        self.time = None
        self.tracks = []
        self.gpx_hdr = self.dom.firstChild
        self.version = self.gpx_hdr.getAttribute("version")
        if self.version == "1.1":
            self._init_version_1_1()
        else:
            raise ValueError, "Can't handle version", None

    def _init_version_1_1(self):
        """Initialise a version 1.1 GPX instance."""
        self.creator = self.gpx_hdr.getAttribute("creator")
        for node in self.gpx_hdr.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            if node.nodeName == "time":
                self.time = node.firstChild.data
            elif node.nodeName == "trk":
                self.tracks.append(GPXTrack(node, self.version))
            else:
                raise ValueError, "Can't handle node", node.nodeName
