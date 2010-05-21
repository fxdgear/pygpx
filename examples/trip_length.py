from pygpx import GPX
import sys

def main():
    """A simple example application"""
    if len(sys.argv) != 2:
        print "Usage: %s filename" % sys.argv[0]
        return
    gpx = GPX(open(sys.argv[1]))
    for trk in gpx.tracks:
        print trk.distance() / 1000.0, trk.duration(), \
              trk.full_duration(), trk.start_time(), trk.end_time()

if __name__ == "__main__":
    main()
