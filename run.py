#!/usr/bin/python

import sys, os
sys.path.insert(0, os.getcwd())
from BuffelMapper.MapPhotographer import main

OUTPUT_DIR="flight_a"

# First get an instance of the API endpoint
api = local_connect()

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

main(api, output_dir=OUTPUT_DIR, frequency=2, width=640, height=480)
