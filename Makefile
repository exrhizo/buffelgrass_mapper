#simple makefile for initializing everything
BUFFEL_HOME=/home/odroid/buffel
STAMP_DIR=$BUFFEL_HOME/stamps

setup: mavlink.py
	echo "Done."

mavlink.py:
	echo "Get mavlink.py"


stamps:
	mkdir -p STAMP_DIR