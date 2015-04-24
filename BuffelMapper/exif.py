#! /usr/bin/python
"""
Simple script for formating the exif for a directory
of pictures so that they are compatible with palantir.
"""
#

import argparse
import glob
from os import path, stat, makedirs
import sys
import exifread
from gi.repository import GExiv2
#import gi.repository as repepep


def fixDirectory(picture_dir):
	glob_pattern = path.join(picture_dir, "*.jpg")
	pictures = glob.glob(glob_pattern)
	for picture in pictures:
		fixExif(picture)
		break #only do one

def printAllTags(tags):
	print "printing tags"
	for tag in tags.keys():
		print tag
		if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
			print "Key: %s, value %s" % (tag, tags[tag])

def fixExif(file_name, focal_length="3.7 mm"):
	print(file_name)
	meta = GExiv2.Metadata(file_name)
	f
	print dir(exif)

if __name__ == "__main__":
	fixDirectory(sys.argv[1])


# from gi.repository import GExiv2
# meta = GExiv2.Metadata("../../outputs/flight1/photo222.jpg")