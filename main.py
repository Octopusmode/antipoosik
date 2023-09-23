import os
import logging
import asyncio
import multiprocessing as mp
from inference import Darknet as Net

from dotenv import load_dotenv

import numpy as np
import cv2

from tools import resize_image, EventContainer as Event

from time import time
from datetime import datetime

from telebot import Telebot

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

WORKING_RESOLUTION_HWC = (720, 1280, 3)

# Detector initialization
detector = Net(weights_path='model/chairman.weights',
               config_path='model/chairman.cfg',
               class_path='model/classes.txt',
               conf_threshold=0.5,
               nms_threshold=0.4,
               input_width=416,
               input_height=416)

# Generating No signal image
blanc_image = np.zeros(shape=WORKING_RESOLUTION_HWC, dtype=np.uint8)
blank_image = cv2.putText(img=blanc_image, text='No image', org=(50, 150), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(255, 255, 255), thickness=2)

# RTSP Params
camlink = os.getenv('RTSP_LINK')
framerate = 10


# Bot init
load_dotenv()

bot = Telebot(os.getenv('BOT_TOKEN'))

async def main():
    cycle_time: float = .0
    frame=None
    bot.send_hello()
    person_count: int = 0    
    afk = Event(threshold_percentage=.2, timeout=5)
    chait_exist = Event(threshold_percentage=0.05, timeout=5)
    
    # Debug variables
    afk_status_old = False
    chair_status_old = False
    alarm_status = False
    alarm_status_old = False
    afk_alarm = False
    afk_alarm_old = False
    afk_timer = .0
    alarm_timeout = 10
    afk_timer_status = False
    afk_timer_status_old = True
    
    # Chair ROI
    x1, y1,x2, y2 = 660, 250, 815, 350
    
    while True:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cycle_time = time()
        if not queue.empty():
            frame = queue.get()
            logger.warning(f'{current_time} Image grabbed')
        else:
            frame = blank_image
            logger.warning(f'{current_time} No image')
            await asyncio.sleep(delay=1)
            continue
        
asyncio.run(main())
        
        
        
        
        
        
        
        
    
        
        
    