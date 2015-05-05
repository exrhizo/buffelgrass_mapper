#!/usr/bin/python

import sys, os
# sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from BuffelMapper.BuffelMapper import BuffelMapper

import logging

log_dir = "./mavproxy_buffelmapper/logs"

all_date_dirs = [os.path.join(log_dir,d) for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
latest_date_dir = max(all_date_dirs, key=os.path.getmtime)
all_flight_dirs = [os.path.join(latest_date_dir,d) for d in os.listdir(latest_date_dir) if os.path.isdir(os.path.join(latest_date_dir, d))]
latest_flight_dir = max(all_flight_dirs, key=os.path.getmtime)
map_picture_dir = os.path.join(latest_flight_dir, "map_pics")
if not os.path.exists(map_picture_dir):
    os.makedirs(map_picture_dir)

log_file = os.path.join(latest_flight_dir, "BuffelMapper.log")
logging.basicConfig(format='%(asctime)s %(message)s')
logging.basicConfig(filename=log_file,level=logging.DEBUG)

# First get an instance of the API endpoint
api = local_connect()

v = api.get_vehicles()[0]

bm = BuffelMapper(api, latest_flight_dir)
bm.run()