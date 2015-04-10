#!/usr/bin/python

"""
This is the basic code to collect map photographs and create the GPX file.

Based on code: 
https://github.com/mavlink/mavlink/blob/master/pymavlink/tools/mavtogpx.py

"""

#from __future__ import division
import argparse
import time
#
from droneapi.lib import VehicleMode
from pymavlink import mavutil

PARSER = argparse.ArgumentParser(
    description='Collect photographs and create GPX file for stitching.')
PARSER.add_argument('output_file', help='Output directory for images and GPX.')
PARSER.add_argument('-f', '-frequency', dest='frequency', type=float, default=.5,
    help='Number of pictures saved per second.')
PARSER.add_argument('-width', dest='width', type=int, default=640,
    help='Width of the photographs.')
PARSER.add_argument('-height', dest='height', type=int, default=480,
    help='Height of the photographs.')



################################################################################


################################################################################
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
    class TrackPoint:
        """
        A simple GPX track point. Used for recording a path taken.
        """
        GPX_TRACK_POINT = """<trkpt lat="{lat}" lon="{lon}">
  <ele>{ele}</ele>
  <time>{time}</time>
  <course>{course}</course>
  <speed>{speed}</speed>
  <fix>3d</fix>
</trkpt>
"""
        def __init__(self, args):
            self.lon = args["lon"]
            self.lat = args["lat"]
            self.ele = args["ele"]
            self.time = args["time"]
            self.course = args["course"]
            self.speed = args["speed"]
        def __str__(self):
            return self.GPX_TRACK_POINT.format(**self.__dict__)
        

    def __init__(self, gpx_file, load=False):
        if load:
            print "ERROR: loading from a file has not been implemented."
        self.gpx_file = gpx_file
        self.track_points = []

    def addTrackPoint(self, point):
        self.track_points.append(point)

    def save(self):
        with open(self.gpx_file, 'w') as f:
            f.write(str(self))

    def __str__(self):
        return self.GPX_BEGIN + \
                ''.join([str(p) for p in self.track_points]) + \
                self.GPX_END




def main(api, output_file="test.gpx", frequency=1,
            width=640, height=480):
    # get our vehicle - when running with mavproxy it only knows about one vehicle (for now)
    print "RUNNING MAP PHOTOGRAPHER"
    v = api.get_vehicles()[0]

    gpx = Gpx(output_file)
    # gpx.addTrackPoint(Gpx.TrackPoint(0,6,7,1,2,3))
    # gpx.addTrackPoint(Gpx.TrackPoint(0,6,7,1,2,3))
    # print str(gpx)
    # gpx.save()
    time_step = 1.0 / frequency
    last_update = time.time() - time_step #don't trigger warning
    count = 0
    print "Using timestep %f" % time_step
    while True:
        #Give the correct update rate
        now = time.time()
        time_diff = now - last_update
        if time_diff < time_step:
            time.sleep(time_step - time_diff)
            now = time.time()
        elif time_diff > 1.5 * time_step:
            print "CANNOT MEET FREQUENCY REQUESTED"
            print "REQUESTED TIMESTEP: %f" % time_step
            print "ACTUAL STEP:        %f" % time_diff


        gpx.addTrackPoint(Gpx.TrackPoint({
            'lon':v.location.lon,
            'lat':v.location.lat,
            'ele':v.location.alt,
            'time':time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'course':v.attitude.yaw,
            'speed':v.groundspeed}))


        #End of Loop time and count
        count += 1
        if count > 10:
            break
        last_update = now
    gpx.save()


print __name__
if __name__ == '__main__':
    args = PARSER.parse_args()

    # First get an instance of the API endpoint
    api = local_connect()

    main(api, vehicle, **vars(args))