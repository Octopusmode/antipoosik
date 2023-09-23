from dotenv import load_dotenv
load_dotenv()

import os
import logging
import asyncio
import multiprocessing as mp
from inference import Darknet as Net

import numpy as np
import cv2

from tools import resize_image, EventContainer as Event

import time
from datetime import datetime

from rtsp_grabber import SubprocessGrabber as Grabber

from aiogram import Bot, Dispatcher
from telebot import Telebot

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

bot = Bot(os.getenv('BOT_TOKEN'))
chat_id = os.getenv('CHAT_ID')
dp = Dispatcher(bot)
telebot = Telebot(bot, dp, chat_id)

dp.register_message_handler(telebot.handle_message)
dp.register_message_handler(telebot.start, commands=['start'])

WORKING_RESOLUTION_HWC = (720, 1280, 3)

# Detector initialization
detector = Net(weights_path='model/chairman.weights',
               config_path='model/chairman.cfg',
               class_path='model/classes.txt',
               conf_threshold=0.5,
               nms_threshold=0.4,
               input_width=416,
               input_height=416)

# Chair detection params
x1, y1,x2, y2 = 660, 250, 815, 350
median_ksize = 5
min_threshold = 50
max_threshold = 255
# Marker params
min_radius = 23
max_radius = 25
param1 = 27
param2 = 8


# Generating No signal image
blanc_image = np.zeros(shape=WORKING_RESOLUTION_HWC, dtype=np.uint8)
blank_image = cv2.putText(img=blanc_image, text='No image', org=(50, 150), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(255, 255, 255), thickness=2)

# RTSP Params
camlink = os.getenv('RTSP_LINK')
framerate = 10

camlink = os.getenv('RTSP_LINK')

stream = Grabber(in_stream=camlink, timeout=10)

async def main():  
    cycle_time: float = .0
    frame=None
    # telebot.bot.send_hello('290302339')
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
    stream.start(framerate=framerate, timeout=30)
    
    while True:
        await dp.start_polling()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cycle_start = time.time()
        
        frame = stream.get_frame().copy()
        
        if frame is None:
            frame = blank_image
            logger.warning(f'{current_time} No image')
            await asyncio.sleep(delay=1)
            continue
        
        # Person detection
        person_count = len(detector.inference(frame=frame)[0])
        afk.add_event(person_count)
        
        # Chair image processing
        chair_image = frame[y1:y2, x1:x2]
        chair_image = cv2.cvtColor(chair_image, cv2.COLOR_BGR2GRAY)
        chair_image = cv2.medianBlur(chair_image, median_ksize)
        _, chair_image = cv2.threshold(chair_image, min_threshold, max_threshold, cv2.THRESH_BINARY)
        circles = cv2.HoughCircles(chair_image, cv2.HOUGH_GRADIENT, dp=1, param1=param1, param2=param2, minRadius=min_radius, maxRadius=max_radius, minDist=1000)
        
        # Chair detection
        if circles is not None:
            chait_exist.add_event(1)
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles[:1]:
                cv2.circle(frame, (x+x1, y+y1), r, (0, 255, 0), 1)
                cv2.line(frame, 
                         ((x+x1)- r, y+y1), 
                         ((x+x1)+ r, y+y1),
                         (255, 0, 0), 2)
                cv2.line(frame, 
                         (x+x1, (y+y1)-r), 
                         (x+x1, (y+y1)+r),
                         (255, 0, 0), 2)
        else:
            chait_exist.add_event(0)
            
        if frame.shape != WORKING_RESOLUTION_HWC:
            frame = resize_image(frame, WORKING_RESOLUTION_HWC, interpolation=cv2.INTER_NEAREST)
            
        frame = detector.render_prediction(frame=frame)
        
        # Alarm logic
        afk_status = afk.check_event(0)
        chair_status = chait_exist.check_event(1)
        if afk_status != afk_status_old or chair_status != chair_status_old:
            logger.debug(f'{current_time} Some thing changed: Person leave={afk_status} Chair in place={chair_status}\n')
        afk_status_old = afk_status
        chair_status_old = chair_status
        
        if afk_status and not chair_status:
            afk_alarm = True
        else:
            afk_alarm = False
            afk_timer = .0
        
        if afk_alarm and not int(afk_timer) > 0:
            afk_timer = time.time()
            
        if time.time() - afk_timer > alarm_timeout:
            afk_alarm = True
        else:
            afk_alarm = False
            
        if afk_alarm != afk_alarm_old:
            logging.info(f'{current_time} {afk_alarm=}')
            success, encoded_image = cv2.imencode('.jpg', frame)
            if success:
                img_data = encoded_image.tobytes()
                msg = 'Опасность проникновения пупсика!'
                user_id='290302339'
                # await telebot.send_msg(msg, user_id, img_data) 
        afk_alarm_old = afk_alarm
        
        afk_timer_status = int(afk_timer) > 0
        
        # if afk_timer_status:
        #     logging.info(f'round{afk_timer=} / round{time()=} / {time()-afk_timer=}')
        
        if afk_timer_status != afk_timer_status_old:
            logging.info(f'ALARM {afk_timer_status=}\n')
        afk_timer_status_old = afk_timer_status
        
        # Rendering
        render_start = time.time()
        frame = cv2.putText(frame, f'{current_time}', (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        frame = cv2.putText(frame, f'{person_count} people', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        frame = cv2.putText(frame, f'{afk_alarm=}', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        frame = cv2.putText(frame, f'{afk_timer_status=}', (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        frame = cv2.putText(frame, f'{afk_timer=}', (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        render_time = time.time() - render_start
        cycle_time = time.time() - cycle_start


asyncio.run(main())