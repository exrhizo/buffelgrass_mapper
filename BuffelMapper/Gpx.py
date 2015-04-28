import cPickle as pickle

class Gpx:
    """
    Class for managing the GPS Exchange format.
    Use to create a gpx file with track points.
    Currently limited to saving files.
    """
    GPX_BEGIN = """<?xml version="1.0" encoding="UTF-8"?>
<gpx
  version="1.0"
  creator="pymavlink"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/0"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
<trk>
<trkseg>
"""
    GPX_END = """</trkseg>
</trk>
</gpx>
""" 

    def __init__(self, gpx_file, load=False):
        if load:
            print "ERROR: loading from a file has not been implemented."
        self.gpx_file = gpx_file
        self.pkl_file = gpx_file+".pkl"
        self.track_points = []
        self.has_new_points = False

    def addTrackPoint(self, point):
        self.has_new_points = True
        self.track_points.append(point)

    def save(self):
        if self.has_new_points:            
            with open(self.gpx_file, 'w') as f:
                f.write(str(self))
            with open(self.pkl_file, 'wb') as f:
                f.write(pickle.dumps(self))
            self.has_new_points = False

    def __str__(self):
        return self.GPX_BEGIN + \
                ''.join([str(p) for p in self.track_points]) + \
                self.GPX_END


class TrackPoint:
    """
    A simple GPX track point. Used for recording a path taken.
    """
    GPX_TRACK_POINT = """<trkpt lat="{lat}" lon="{lon}">
  <ele>{ele}</ele>
  <time>{time}</time>
  <compass>{compass}</compass>
  <speed>{speed}</speed>
  <fix>3d</fix>
</trkpt>
"""
    def __init__(self, args):
        self.lon = args["lon"]
        self.lat = args["lat"]
        self.ele = args["ele"]
        self.time = args["time"]
        self.compass = args["compass"]
        self.speed = args["speed"]

    def __str__(self):
        return self.GPX_TRACK_POINT.format(**self.__dict__)