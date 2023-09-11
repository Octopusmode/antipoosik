import logging
from logging import Logger
import asyncio
import multiprocessing as mp
from GstreamerStream import Stream

import numpy as np
import cv2

# import rtsp_grabber as vs
from fb_renderer import FramebufferRenderer as FBR
from tools import resize_image

from time import time

### Init

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

lcd_resolution = (1088, 1920)
render = FBR(device_id='/dev/fb0', resolution=lcd_resolution)

blanc_image = np.zeros(shape=(1200, 1600, 3), dtype=np.uint8)

#RTSP Params
queue = mp.Queue()
event = mp.Event()
camlink = 'rtsp://192.168.0.120/snl/live/1/1'
framerate = 10

source = Stream(camlink, event, queue, framerate=framerate)
source.start()

vcap = cv2.VideoCapture(filename="rtsp://192.168.0.120/snl/live/1/1")

### Func
async def render_async(image, metrics):
    await asyncio.sleep(delay= 0.01)
    render.render_image(image=image, metrics=metrics)
    
async def main():
    render_time: float = .0
    cycle_time: float = .0
    frame = None
    
    while 1:
        if not queue.empty():
            cstatus, frame = queue.get()

        if frame is None:
            frame = blanc_image
        
        ret, frame = vcap.read()
            
        cycle_start: float = time()
        grabbed_image = frame
        
        if grabbed_image is None:
            grabbed_image = blanc_image
        
        render_start: float = time()
        await render_async(image=grabbed_image, metrics=None)
        render_time = time() - render_start
        cycle_time: float = time() - cycle_start
    
    render.close()
    
asyncio.run(main())