"""
BuffelMapper module is the top level controller that runs the MapPhotographer
and runs the webserver.

Run this from run.py using the droneapi in MavProxy.
"""

__author__ = "Alex Warren"
__copyright__ = "Copyright 2015, Autonomous Mapping Project"
__credits__ = ["Alex Warren", "Rachel Powers", "Thomas Schuker",
                    "Travis Kibler", "Jesse Odle", "Jeremy Hibbs"]
__license__ = "BSD 2"



import time
import sys, os
#
from droneapi.lib import VehicleMode
from pymavlink import mavutil

from pprint import pprint

from Settings import settings
from MapPhotographer import MapPhotographer

from BuffelWeb.BuffelWeb import BuffelWebServer

class BuffelMapper:
    def __init__(self, api, log_dir):

        # First get an instance of the API endpoint (the connect via web case will be similar)
        self.api = api

        # Our vehicle (we assume the user is trying to control the virst vehicle attached to the GCS)
        self.vehicle = self.api.get_vehicles()[0]

        self.log_dir = log_dir

        self.map_picture_dir = os.path.join(log_dir, "map_pics")
        if not os.path.exists(self.map_picture_dir):
            os.makedirs(self.map_picture_dir)

        self.web_static_dir = os.path.join(settings["buffel_root"], "BuffelWeb", "static")
        self.web_static_picture = os.path.join(self.web_static_dir, "map_pic.jpg")

        self.last_update = time.time()

        self.vehicle.set_mavlink_callback(self.getTimeDifference)

        self.map_photographer = MapPhotographer(self.map_picture_dir)

        self.web_server = BuffelWebServer(self.vehicle, self)

        self.running = False


    def getTimeDifference(self, m):
        if (m.get_type() == "SYSTEM_TIME"):
            local_t = time.time()
            del self.vehicle.mavrx_callback
            autopilot_t = m.time_unix_usec / 1000000.
            self.time_diff = local_t - autopilot_t
            time_file = sys.join(self.log_dir, "time_diff.txt")
            with open(time_file, 'w') as f:
                f.write(time_diff)

    def run(self):
        while not self.api.exit:
            if self.running:
                self.start()
                self.loop()
                self.pause()
            else:
                self.paused()

        self.finish()

    def start(self):
        self.map_photographer.startBackground()

    def pause(self):
        self.map_photographer.pauseBackground()
        

    def paused(self):
        while not self.api.exit:
            time.sleep(1)
            if self.vehicle.armed:
                self.running = True
                break

    def loop(self):
        while not self.api.exit:
            time.sleep(1)
            self.map_photographer.updatePhotographList()
            if self.map_photographer.photograph_list:
                recent_pic = self.map_photographer.photograph_list[-1]
                if os.path.exists(self.web_static_picture):
                    os.remove(self.web_static_picture)
                os.symlink(recent_pic, self.web_static_picture)

            if not self.vehicle.armed:
                self.running = False
                break

    def finish(self):
        self.map_photographer.stopBackground()
        self.web_server.close()
