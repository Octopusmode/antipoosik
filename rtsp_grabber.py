import cv2
import asyncio
import time
import logging
import numpy as np

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

class RTSP():
    def __init__(self, camlink: str, framerate: int, size_wh: tuple, max_missed_frames: int = 10):
        self.camlink = camlink
        self.framerate = framerate
        self.frame = None
        self.max_missed_frames = max_missed_frames
        self.cap = cv2.VideoCapture(self.camlink)
        self.cap.set(cv2.CAP_PROP_FPS, self.framerate)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, size_wh[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size_wh[1])
        self.blank_image = cv2.putText(img=np.zeros(shape=(size_wh[1], size_wh[0], 3), dtype=np.uint8), text='No image', org=(50, 150), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(255, 255, 255), thickness=2)
        self.is_grabbing = False
        self.last_frame_time = .0

        
    async def start(self):
        if not self.is_grabbing:
            logger.info(f'RTSP: Starting {self.camlink}')
            self.is_grabbing, self.frame = self.cap.read()
            asyncio.sleep(1)
            
            
            