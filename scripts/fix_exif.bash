#!/bin/bash

#Set the exif tags for a directory of jpg files
#uses the file name to generate pictures

FOCAL_LENGTH="3.67"

usage(){
cat << EOF
Set the exif tags for a directory of jpg files.

jpg files must use the format:
YYYY:MM:DD HH:MM:SS-elevation-anything.jpg

Usage:
./fix_exif.bash [path to directory]
EOF
}

if [ "$#" -ne 1 ]; then
	usage
    exit -1
fi

if [ ! -d "$1" ]; then
	echo "$1 is not a valid directory."
	exit -1
fi

echo "Fixing photos in $1"
echo "----------------------------"

for fullfile in $1/*.jpg; do
	filename=$(basename "$fullfile")
	# extension="${filename##*.}"
	filename="${filename%.*}"
	IFS='-' read -a array <<< "$filename"
	time_created="${array[0]}"
	elevation="${array[1]}"
	# echo $filename
	# echo $time_created
	# echo $elevation

	exiftool -focallength=$FOCAL_LENGTH "$fullfile"
	exiftool -DateTimeOriginal="$time_created" "$fullfile"
	exiftool -CreateDate="$time_created" "$fullfile"
done