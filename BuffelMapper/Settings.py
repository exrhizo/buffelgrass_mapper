"""
Simple module for storing all the settings in one place.
"""

import os

settings = {
	"map_cam_width":640,
	"map_cam_height":480,
	"map_cam_freq":1,
	"map_cam_focal_length":3.67,
	"buffel_root":"/home/alex/buffel/buffelgrass_mapper"}


settings["log_dir"] = os.path.join(settings["buffel_root"], "mavproxy_buffelmapper", "logs")
