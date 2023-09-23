import cv2
import numpy as np

import subprocess as sp

import time
from datetime import datetime

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

class SubprocessGrabber():
    def __init__(self, in_stream, width, height, timeout=10, max_dublicates=None):
        self.in_stream = in_stream
        self.width = width
        self.height = height
        self.grab_time = .0
        self.prev_frame = None
        self.dublicate_count = 0
        self.max_dublicates = max_dublicates
        ret = False
        self.width, self.height = 0, 0
        
        # Getting resolution of input video
        cap = cv2.VideoCapture(in_stream)
        start_time = time.time()
        while not ret and not width or not height:
            ret, _ = cap.read()
            # Get resolution of input video
            self.width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
            # Release VideoCapture - it was used just for getting video resolution
            cap.release()
            if time.time() - start_time > timeout:
                raise Exception('Timeout while getting video resolution')
        
    def start(self, framerate=10, timeout=30):
        self.framerate = framerate
        self.ffmpeg_cmd = ['ffmpeg',
                           '-discard', 'nokey',
                           '-rtsp_transport', 'tcp',
                           '-max_delay', str(timeout*1000000),
                           '-i', self.in_stream,
                           '-f', 'rawvideo',
                           '-pix_fmt', 'bgr24',
                           '-vcodec', 'rawvideo', '-an', 'pipe:']
        
        # Open sub-process that gets in_stream as input and uses stdout as an output PIPE.
        self.process = sp.Popen(self.ffmpeg_cmd, stdout=sp.PIPE)
        
    def get_frame(self):
        start_time = time.time()
        raw_frame = self.process.stdout.read(self.width*self.height*3)
        if len(raw_frame) != (self.width*self.height*3):
            logger.error('Error reading frame!')
            return None
        else:
            if self.prev_frame is not None:
                if np.array_equal(self.prev_frame, raw_frame):
                    self.dublicate_count += 1
                    if self.max_dublicates is not None and self.dublicate_count >= self.max_dublicates:
                        logger.debug(f'Dublicate frame series detected! Count: {self.dublicate_count}')
                    return None
                else:
                    self.dublicate_count = 0
            frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((self.height, self.width, 3))
            self.prev_frame = frame
            self.grab_time = time.time() - start_time
            return frame
        
    def get_returncode(self):
        if self.process.poll() is not None:
            return self.process.returncode
        else:
            return None


        
