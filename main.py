import logging
from logging import Logger
import asyncio
import multiprocessing as mp
from inference import Darknet as Net

# Check available OS
import platform
if platform.system() == 'Linux':
    use_framebuffer = True
    from key_grabber import get_current_key
    from evdev import InputDevice
    device = InputDevice('/dev/input/event6')
else:
    use_framebuffer = False

import numpy as np
import cv2

from fb_renderer import FramebufferRenderer as FBR
from tools import resize_image

from time import time

### Init

detector = Net(weights_path='chairman.weights',
               config_path='chairman.cfg',
               class_path='model/classes.txt',
               conf_threshold=0.5,
               nms_threshold=0.4,
               input_width=416,
               input_height=416)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

lcd_resolution = (1088, 1920)
render = FBR(device_id='/dev/fb0', resolution=lcd_resolution)

blanc_image = np.zeros(shape=(1200, 1600, 3), dtype=np.uint8)

#RTSP Params
# queue = mp.Queue()
# event = mp.Event()
camlink = 'rtsp://192.168.0.120/snl/live/1/1'
framerate = 10

# source = Stream(camlink, event, queue, framerate=framerate)
# source.start()

vcap = cv2.VideoCapture(filename=camlink)

### Func
async def render_async(image, metrics):
    await asyncio.sleep(delay= 0.01)
    render.render_image(image=image, metrics=metrics)
    
async def main():
    render_time: float = .0
    cycle_time: float = .0
    frame = None
    
    while 1:
        # if not queue.empty():
        #     cstatus, frame = queue.get()

        if frame is None:
            frame = blanc_image
        
        ret, frame = vcap.read()
        
        detector.inference(frame=frame)
        
        frame = detector.render_prediction(frame=frame)
            
        cycle_start: float = time()
        grabbed_image = frame
        
        if grabbed_image is None:
            grabbed_image = blanc_image
        
        render_start: float = time()
        if use_framebuffer:
            await render_async(image=grabbed_image, metrics=None)
            if get_current_key(device) == 'KEY_KP0':
                break
        else:
            grabbed_image = resize_image(grabbed_image, lcd_resolution)
            cv2.imshow('frame', grabbed_image)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            
        render_time = time() - render_start
        cycle_time: float = time() - cycle_start
    
    render.close()
    
asyncio.run(main())