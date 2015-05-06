"""
Classes for use with genshi, these are the basic datastructres that are used to create
populate the values of the templaes.
"""


__author__ = "Alex Warren"
__copyright__ = "Copyright 2015, Autonomous Mapping Project"
__credits__ = ["Alex Warren", "Rachel Powers", "Thomas Schuker",
                    "Travis Kibler", "Jesse Odle", "Jeremy Hibbs"]
__license__ = "BSD 2"

import os

from BuffelMapper.Settings import settings
from droneapi.lib import VehicleMode, Vehicle

class Photograph(object):
	def __init__(self, file_path, date_time):
		self.file_path = file_path
		self.date_time = date_time

	def __repr__(self):
		return '<%s %r>' % (type(self).__name__, self.date_time)

class Flight(object):
	def __init__(self, path, date, flight_title, idx):
		self.path = path
		self.date = date
		self.flight_title = flight_title
		self.name = "%s_%s" %(date, flight_title)
		self.idx = idx

	def __str__(self):
		return self.flight_title


class Flights(object):
	def __init__(self):
		self.flights = []
		log_dir = settings["log_dir"]
		self.log_dir = log_dir
		all_date_dirs = [d for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
		for date_dir in os.listdir(log_dir):
			full_date_dir = os.path.join(log_dir, date_dir)
			if not os.path.isdir(full_date_dir):
				continue
			for flight_dir in os.listdir(full_date_dir):
				full_flight_dir = os.path.join(full_date_dir, flight_dir)
				if not os.path.isdir(full_flight_dir):
					continue
				self.flights.append(Flight(full_flight_dir, date_dir, flight_dir, len(self.flights)))
	
