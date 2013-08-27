"""
A module for parsing GPX files.
"""
from lxml import etree
import os
import math
import datetime
from dateutil.parser import parse


def deg2rad(deg):
    """Convert degrees to radians"""
    return deg / (180 / math.pi)


class GPXTrackPt:
    """A track point."""

    def __init__(self, node, version):
        """Construct a trackpint given an XML node."""
        self.version = version
        self.lat = float(node.get("lat"))
        self.lon = float(node.get("lon"))
        self.elevation = None
        self.time = None
        self.hr = None
        for child in node:
            if child.tag == "{http://www.topografix.com/GPX/1/1}time":
                self.time = parse(child.text)
            elif child.tag == "{http://www.topografix.com/GPX/1/1}ele":
                self.elevation = float(child.text)
            elif child.tag == "{http://www.topografix.com/GPX/1/1}extensions":
                for child1 in child:
                	if child1.tag == "{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension":
                		for child2 in child1:
                			if child2.tag == "{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr":
                				self.hr = int(child2.text)
            else:
                raise ValueError("Can't handle node: '%s'" % child.tag)

    def distance(self, other):
        """Compute the distance from this point to another."""
        try:
            # http://www.platoscave.net/blog/2009/oct/5/calculate-distance-latitude-longitude-python/

            radius = 6378700.0 # meters

            lat1, lon1 = self.lat, self.lon
            lat2, lon2 = other.lat, other.lon

            dlat = math.radians(lat2-lat1)
            dlon = math.radians(lon2-lon1)
            a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
                * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            d = radius * c

        except ValueError, e:
            raise ValueError(e)
        return d

    def duration(self, other):
        """Return the time difference between two nodes."""
        return other.time - self.time


class GPXTrackSeg:
    """One segment of a GPX track."""

    def __init__(self, node, version):
        self.version = version
        self.trkpts = []
        self.elevation_gain = 0.0
        self.elevation_loss = 0.0
        for child in node:
            if child.tag == "{http://www.topografix.com/GPX/1/1}trkpt":
                self.trkpts.append(GPXTrackPt(child, self.version))
            else:
                raise ValueError("Can't handle node <%s>" % node.nodeName)
        self._get_elevation()

    def _get_elevation(self):
        try:
            gain = 0.0
            loss = 0.0
            last_pt = self.trkpts[0]
            last_elevation = last_pt.elevation
            for pt in self.trkpts[1:]:
                if pt.elevation > last_elevation:
                    gain += pt.elevation - last_elevation
                else:
                    loss += last_elevation - pt.elevation
                last_elevation = pt.elevation
            self.elevation_gain = gain
            self.elevation_loss = loss
        except AttributeError:
            self.elevation_gain = None
            self.elevation_loss = None

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
            elif child.tag == "{http://www.topografix.com/GPX/1/1}desc":
                self.desc = child.text

    def elevation_gain(self):
        try:
            return sum([trkseg.elevation_gain for trkseg in self.trksegs])
        except TypeError:
            return None

    def elevation_loss(self):
        try:
            return sum([trkseg.elevation_loss for trkseg in self.trksegs])
        except TypeError:
            return None

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
        try:
            return self.trksegs[0].trkpts[0]
        except IndexError:
            return None

    def end(self):
        """Return the final track point of this track."""
        try:
            return self.trksegs[-1].trkpts[-1]
        except IndexError:
            return None

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
        SCHEMA = os.path.join(PATH, "schema", "gpx-1_1.xsd")
        self.creator = None
        self.time = None
        self.tracks = []
        self.version = ""
        self.metadata = None
        gpx_schema_doc = etree.parse(SCHEMA)
        gpx_schema = etree.XMLSchema(gpx_schema_doc)
        self.gpx_doc = etree.parse(fd)
        self.root = self.gpx_doc.getroot()

        # Test if this is a GPX file or not and if it's version 1.1
        if self.root.tag != "{http://www.topografix.com/GPX/1/1}gpx":
            raise ValueError("Not a gpx file: '%s'" % fd)
        elif self.root.get("version") != "1.1":
            raise ValueError("Verion %s is not supported. Must use GPX v1.1" % self.root.get("version"))
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

    def elevation_gain(self):
        try:
            return sum([track.elevation_gain() for track in self.tracks])
        except TypeError:
            return None

    def elevation_loss(self):
        try:
            return sum([track.elevation_loss() for track in self.tracks])
        except TypeError:
            return None

    def distance(self):
        """Return the distance for this gpx file."""
        try:
            return sum([track.distance() for track in self.tracks])
        except IndexError:
            print "emtpy GPX file"

    def duration(self):
        """Return the duration for this track. The sum of the duration
        of all track segments."""
        dur = datetime.timedelta(0)
        for track in self.tracks:
            dur += track.duration()
        return dur

    def full_duration(self):
        """Return the full duration of the track. This does not include
        break time."""
        if hasattr(self.start(), 'duration'):
            return self.start().duration(self.end())
        else:
            return None

    def start(self):
        """Return the starting track point."""
        return self.tracks[0].start()

    def end(self):
        """Return the final track point of this track."""
        return self.tracks[-1].end()

    def start_time(self):
        """Return the start time of the track."""
        if self.start():
            return self.start().time
        else:
            return None

    def end_time(self):
        """Return the end time of te track."""
        return self.end().time

