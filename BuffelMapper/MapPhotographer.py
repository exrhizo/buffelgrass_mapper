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

import cv2
import numpy as np

from Gpx import Gpx, TrackPoint

################################################################################

def main(api, output_dir=".", frequency=1,
            width=640, height=480):
    # get our vehicle - when running with mavproxy it only knows about one vehicle (for now)
    print "RUNNING MapPhotographer.py"
    v = api.get_vehicles()[0]

    gpx = Gpx(output_dir+"/flight.gpx")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)

    time_step = 1.0 / frequency
    last_update = time.time() - time_step #don't trigger warning
    count = 0
    print "Using timestep %f" % time_step

    while not api.exit:
        if not v.armed:
            gpx.save()
            time.sleep(1)
            continue
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

        #Files are saved with this format:
        #YYYY:MM:DD HH:MM:SS-elevation-speed.jpg

        pic_name = "{}-{:.3f}-{:.3f}.jpg".format(
            time.strftime("%Y:%m:%d %H:%M:%S"),
            v.location.alt,
            v.groundspeed)

        print "{}: about to read frame".format(time.time())
        ret, frame = cap.read()
        print "{}: frame read. About to write image {}".format(time.time(), pic_name)
        cv2.imwrite("{}/{}".format(output_dir, pic_name), frame);
        print "{}: image writen. about to create TrackPoint".format(time.time())

        gpx.addTrackPoint(TrackPoint({
            'lon':v.location.lon, #Decimal degrees
            'lat':v.location.lat, #Decimal degrees
            'ele':v.location.alt, #Meters
            'time':time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'compass':v.attitude.yaw * 57.2957795, #degrees
            'speed':v.groundspeed})) # m/s

        print "{}: TrackPoint created".format(time.time())

        #End of Loop time and count
        count += 1
        if count%10:
            gpx.save()
        last_update = now

    print "api.exit is true"
    cap.release()
    gpx.save()
