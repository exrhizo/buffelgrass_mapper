#!/usr/bin/python

import sys, os
sys.path.insert(0, os.getcwd())
from BuffelMapper.MapPhotographer import main

log_dir = "./mavproxy_buffelmapper/logs"
all_date_dirs = [os.path.join(log_dir,d) for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
latest_date_dir = max(all_date_dirs, key=os.path.getmtime)
all_flight_dirs = [os.path.join(latest_date_dir,d) for d in os.listdir(latest_date_dir) if os.path.isdir(os.path.join(latest_date_dir, d))]
latest_flight_dir = max(all_flight_dirs, key=os.path.getmtime)
map_picture_dir = os.path.join(latest_flight_dir, "map_pics")
if not os.path.exists(map_picture_dir):
    os.makedirs(map_picture_dir)

# First get an instance of the API endpoint
api = local_connect()

main(api, output_dir=map_picture_dir, frequency=2, width=640, height=480)

# from BuffelMapper.BuffelMapper import BuffelMapper
# bm = BuffelMapper(api)
# bm.run()