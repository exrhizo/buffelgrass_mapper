#!/usr/bin/python

import sys, os
sys.path.insert(0, os.getcwd())
from BuffelMapper.MapPhotographer import main

# First get an instance of the API endpoint
api = local_connect()

main(api, output_file="test.gpx", frequency=2, width=640, height=480)
