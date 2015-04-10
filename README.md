#Buffelgrass Mapper
===

University of Arizona
Engineering Senior Capstone

===

## Overview

The buffelgrass mapper is a senior design project with the goal of creating an autonomous quadcopter capable of mapping a given region defined in GPS coordinates.

The code is based on [ardupilot-balloon-finder](ardupilot-balloon-finder)

## Setup

The ballon-finder folks have a [good tutorial](http://dev.ardupilot.com/wiki/companion-computers/odroid-via-mavlink).

### On another computer connect to the pixhawk for configuration.

First set-up connection using [apm-planner](https://github.com/diydrones/apm_planner).

We are going to use [Drone API](http://dev.ardupilot.com/wiki/droneapi-tutorial/) - has instructions for setting up.

### Odroid Setup

Now we need to get [MAVLink](http://dev.ardupilot.com/wiki/companion-computers/raspberry-pi-via-mavlink/#Install_the_required_packages_on_the_Raspberry_Pi) set up.

   > sudo apt-get install screen python-wxgtk2.8 python-matplotlib python-opencv python-pip python-numpy

   > sudo pip install mavproxy

   