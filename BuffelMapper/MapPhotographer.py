"""
MapPhotographer

Module for capturing images and saving them in a seperate process.
"""
import time
import sys, os
from multiprocessing import Process, Pipe
import subprocess

from droneapi.lib import VehicleMode
from pymavlink import mavutil

import cv2
import numpy as np

from Settings import settings
import logging

################################################################################

class MapPhotographer:
    BACKGROUND_RUN = 1
    BACKGROUND_PAUSE = 0
    BACKGROUND_STOP = -1

    def __init__(self, picture_dir):
        self.time_step = 1.0 / settings["map_cam_freq"]

        self.picture_dir = picture_dir
        
        self.background_started = False

        self.photograph_list = []

        logging.debug("Using MapPhotographer time_step: %f", self.time_step)

    def startBackground(self, paused=False):
        if self.background_started:
            self.parent_conn.send(self.BACKGROUND_RUN) #tell the subprocess to run
        else:
            self.background_started = True
            self.parent_conn, background_conn = Pipe()

            self.proc = Process(target=self.backround_start, args=(background_conn, paused))
            self.proc.start()

    def pauseBackground(self):
        if self.background_started:
            self.parent_conn.send(self.BACKGROUND_PAUSE) #tell the subprocess to pause
        else:
            logging.error("Unable to pause background photographer, process does not exist.")

    def stopBackground(self):
        if self.background_started:
            self.parent_conn.send(self.BACKGROUND_STOP) #tell the subprocess to stop
            self.background_started = False
        else:
            logging.error("Unable to pause background photographer, process does not exist.")

    def updatePhotographList(self):
        while self.parent_conn.poll():
            m = self.parent_conn.recv()
            logging.info("Recieved photo path: %s", str(m))
            self.photograph_list.append(m)

    def backround_start(self, background_conn, paused):
        self.background_conn = background_conn
        self.last_update = time.time() - self.time_step

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, settings["map_cam_width"])
        self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, settings["map_cam_height"])

        self.background_running = not paused

        self.background_loop()
        self.background_stop()

    def background_stop(self):
        self.cap.release()

    def background_loop(self):
        ended = False
        while True:
            # Read through all the messages.
            while self.background_conn.poll():
                m = self.background_conn.recv()
                if m == self.BACKGROUND_STOP:
                    ended = True
                elif m == self.BACKGROUND_PAUSE:
                    self.background_running = False
                elif m == self.BACKGROUND_RUN:
                    self.background_running = True
                else:
                    logging.debug("Unknown message sent to background: %s", str(m))

            if not self.background_running:
                time.sleep(1)
                continue

            if ended:
                break

            now = time.time()

            time_diff = now - self.last_update
            if time_diff < self.time_step:
                time.sleep(self.time_step - time_diff)
                now = time.time()
            elif time_diff > 1.5 * self.time_step:
                logging.error("CANNOT MEET FREQUENCY REQUESTED")
                logging.error("REQUESTED TIMESTEP: %f", self.time_step)
                logging.error("ACTUAL STEP:        %f", time_diff)


            #Files are saved with this format:
            #YYYY:MM:DD HH:MM:SS-0-0.jpg
            date_time = time.strftime("%Y:%m:%d %H:%M:%S")
            pic_file_path = os.path.join(self.picture_dir, "{}-0-0.jpg".format(date_time))
            ret, frame = self.cap.read()
            cv2.imwrite(pic_file_path, frame);
            logging.info("Picture taken. %s", pic_file_path)

            self.fixExif(pic_file_path, date_time)
            logging.info("Exif modified. %s", pic_file_path)
            
            self.background_conn.send(pic_file_path)

            self.last_update = now
        
    def fixExif(self, file_path, date_time):
        command = ['exiftool',
                   '-overwrite_original',
                   '-focallength=%s' % str(settings["map_cam_focal_length"]),
                   '-DateTimeOriginal=%s' % date_time,
                   '-CreateDate=%s' % date_time,
                   file_path
                   ]
        exif_proc = subprocess.Popen(command, 
                            stdin = subprocess.PIPE,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE)
        out, err = exif_proc.communicate()
        
        logging.info(out)
        if err:
            logging.error(err)
