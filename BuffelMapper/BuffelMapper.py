import time
import sys
#
from droneapi.lib import VehicleMode
from pymavlink import mavutil

from pprint import pprint

from MapPhotographer import MapPhotographer

class BuffelMapper:
    def __init__(self, api, log_dir):

        # First get an instance of the API endpoint (the connect via web case will be similar)
        self.api = api

        # Our vehicle (we assume the user is trying to control the virst vehicle attached to the GCS)
        self.vehicle = self.api.get_vehicles()[0]

        self.log_dir = log_dir

        self.last_update = time.time()

        self.vehicle.set_mavlink_callback(self.getTimeDifference)

        self.map_photographer = MapPhotographer()


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
            if not self.vehicle.armed:
                self.running = False
                break

    def finish(self):
        self.map_photographer.stopBackground()
