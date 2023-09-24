import logging
from logging import Logger
import asyncio
import multiprocessing as mp
from inference import Darknet as Net
from GstreamerStream import Stream

import numpy as np
import cv2

import os

# Token for bot
# from dotenv import load_dotenv
# load_dotenv()

# bot = TelegramBot(token=os.getenv('TOKEN'))

from modules.tools import resize_image, EventContainer as Event
from modules.tools import Timer

from time import time
from datetime import datetime

### Init

detector = Net(weights_path='model/chairman.weights',
               config_path='model/chairman.cfg',
               class_path='model/classes.txt',
               conf_threshold=0.5,
               nms_threshold=0.4,
               input_width=416,
               input_height=416)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)



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
    await asyncio.sleep(delay= 1 / 15)
    render.render_image(image=image, metrics=metrics)
    
async def main():

    
    render_time: float = .0
    cycle_time: float = .0
    frame = None
    old_count = 0
    person_count = 0
    
    afk = Event(threshold_percentage=0.20, timeout=5)
    chait_exist = Event(threshold_percentage=0.05, timeout=5)
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
    
    while 1:    
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # if not queue.empty():
        #     cstatus, frame = queue.get()
        # else:
        #     logger.warning('Queue missing!')
        
        ret, frame = vcap.read()

        if frame is None:
            frame = blanc_image
        
        person_count = len(detector.inference(frame=frame)[0])
        afk.add_event(person_count)
        # logger.debug(f'{afk.get_events()}, {afk.check_event()}')
        
        ### Chair

        x1, y1, x2, y2 = 660, 250, 815, 350 # ROI
        
        chair_image = frame[y1:y2, x1:x2]
        chair_image = cv2.cvtColor(chair_image, cv2.COLOR_BGR2GRAY)
        chair_image = cv2.medianBlur(chair_image, ksize=5)
        _, chair_image = cv2.threshold(chair_image, 50, 255, cv2.THRESH_BINARY)
        circles = cv2.HoughCircles(chair_image, method=cv2.HOUGH_GRADIENT, dp=1.0, minRadius=23, maxRadius=26, minDist=1000, param1=27, param2=8)
        

        
        ### Render 
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(frame, (x+x1, y+y1), r, (0, 255, 0), 1)
                cv2.line(frame, 
                         ((x+x1)- r, y+y1), 
                         ((x+x1)+ r, y+y1),
                         (255, 0, 0), 2)
                cv2.line(frame, 
                         (x+x1, (y+y1)-r), 
                         (x+x1, (y+y1)+r),
                         (255, 0, 0), 2)

            chait_exist.add_event(1)
        else:
            chait_exist.add_event(0)
                

        
        frame = detector.render_prediction(frame=frame)
        
        ### Logic
        
        afk_status = afk.check_event(0)
        chair_status = chait_exist.check_event(1)
        if afk_status != afk_status_old:
            logger.debug(f'{current_time} {afk_status=}')
        if chair_status != chair_status_old:
            logger.debug(f'{current_time} {chair_status=}')
        afk_status_old = afk_status
        chair_status_old = chair_status
        
        if afk_status and not chair_status:
            afk_alarm = True
        else:
            afk_alarm = False
            afk_timer = .0
        
        if afk_alarm and not afk_timer:  # int(afk_timer) > 0
            afk_timer = time()
            
        if time() - afk_timer > alarm_timeout:
            afk_alarm = True
        else:
            afk_alarm = False
              
        if afk_alarm != afk_alarm_old:
            logging.info(f'{current_time} {afk_alarm=}')
        afk_alarm_old = afk_alarm
        
        afk_timer_status = int(afk_timer) > 0
        
        # if afk_timer_status:
        #     logging.info(f'round{afk_timer=} / round{time()=} / {time()-afk_timer=}')
        
        if afk_timer_status != afk_timer_status_old:
            logging.info(f'ALARM {afk_timer_status=}')
        afk_timer_status_old = afk_timer_status
        
        ### Displaying
            
        cycle_start: float = time()
        grabbed_image = frame
        
        if grabbed_image is None:
            grabbed_image = blanc_image
        
        render_start: float = time()

        key = get_current_key(device)
        if  key == 'KEY_KP0':
            break

            
        render_time = time() - render_start
        cycle_time: float = time() - cycle_start
        
    vcap.release()
    
asyncio.run(main())