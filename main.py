from dotenv import load_dotenv
load_dotenv()

import os
import logging
import asyncio
import multiprocessing as mp
from inference import Darknet as Net

import numpy as np
import cv2

from modules.tools import resize_image
from modules.alarms import Alarm
from modules.events import EventContainer as Event

import time
from datetime import datetime

from rtsp_grabber import SubprocessGrabber as Grabber

from aiogram import Bot, Dispatcher
from aiogram.utils import exceptions
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

def start_polling():
    dp.start_polling()
    
async def alarm(frame, msg):
    try:
        # await send_alarm(frame, msg)
        pass
    except exceptions.NetworkError as e:
        logger.error("Telebot connection troubles: {e}")
        pass

async def send_alarm(frame, msg='!', user_id=os.getenv('CHAT_ID')):
    success, encoded_image = cv2.imencode('.jpg', frame)
    if success and dp.is_polling:
        img_data = encoded_image.tobytes()
        await telebot.send_msg(msg, user_id, img_data)
    if not dp.is_polling:
        logger.warning('{time}')

async def main():
    # pooling = mp.Process(target=start_polling)
    # pooling.start()
    cycle_time: float = .0
    frame=None
    # telebot.bot.send_hello('290302339')
    person_count: int = 0    
    afk = Event(threshold_percentage=.2, timeout=5)
    chait_exist = Event(threshold_percentage=0.05, timeout=5)
    render=None
    render_time: float = .0
    frame_count = 0
    heating_frame_count = 40

    alarm_timeout = 10
    
    afk_status, afk_status_old = False, False
    chair_status, chair_status_old = False, False
    alarm_status, alarm_status_old = False, False

    stream.start(framerate=framerate, timeout=30)
    
    while True:        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cycle_start = time.time()
        
        grabbed_frame = stream.get_frame(blank_image)
        
        # Heating
    
        # TODO починить пустой тип кадра
        if frame is not None:
            frame = grabbed_frame.copy()
        else:
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
        
        # Rendering
        render_start = time.time()
        render = cv2.putText(frame, f'{current_time}', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        render = cv2.putText(render, f'{person_count} people', (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # render = cv2.putText(render, f'{afk_alarm=}', (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        render = cv2.putText(render, f'{afk_timer_status=}', (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # render = cv2.putText(render, f'{afk_timer=}', (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        render = cv2.putText(render, f'{afk_status=}', (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        render = cv2.putText(render, f'{chair_status=}', (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        render = cv2.putText(render, f'{alarm_status=}', (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        render = cv2.putText(render, f'{cycle_time=}', (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        render = cv2.putText(render, f'{render_time=}', (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        render_time = time.time() - render_start
        
        if frame_count > heating_frame_count:
            # Alarm logic
            afk_status, chair_status = afk.check_event(0), chait_exist.check_event(1)
            
            if afk_status != afk_status_old or chair_status != chair_status_old:
                msg = f'{current_time} Some thing changed: Person leave={afk_status} Chair in place={chair_status}\n'
                logger.debug(msg)
                if render is not None:
                    await alarm(render, msg)
            afk_status_old, chair_status_old = afk_status, chair_status
            

                
            if afk_alarm != afk_alarm_old:
                msg = f'{current_time} {afk_alarm=} Сработал тревожный таймер\n'
                logging.info(msg)
            afk_alarm_old = afk_alarm
            
            afk_timer_status = int(afk_timer) > 0
            
            if afk_timer_status != afk_timer_status_old:
                msg = f'{current_time} TIMER {afk_timer_status=}\n'
            afk_timer_status_old = afk_timer_status
            
            if alarm_status != alarm_status_old:
                msg = f'{current_time} ALARM {afk_alarm_status=}\n'
                logger.debug(msg)
                if render is not None:
                    await alarm(render, msg)
            alarm_status_old = afk_alarm_status
    
        cycle_time = time.time() - cycle_start
        
        frame_count += 1
        
        # pooling.join


asyncio.run(main())