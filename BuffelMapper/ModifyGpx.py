#!/usr/bin/python

import sys, os
import cPickle as pickle
#from MapPhotographer import Gpx

sys.path.insert(0, os.path.split(os.getcwd())[0])
import BuffelMapper

GPX_FILE = sys.argv[1]

print("Using Gpx pickle: {}".format(GPX_FILE))

with open(GPX_FILE, 'rb') as f:
	gpx = pickle.load(f)

gpx.fixPoints()

print "write to: {}/flight.gpx".format(os.path.split(GPX_FILE)[0])

#print str(gpx)
with open("{}/flight.gpx".format(os.path.split(GPX_FILE)[0]), 'w') as f:
	f.write(str(gpx))