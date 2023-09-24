import cv2
import numpy as np
from time import time

from modules.events import EventContainer as Event
from modules.tools import Timer

blank_image = np.zeros(shape=(600, 800, 3), dtype=np.uint8)

AFK = Event(threshold_percentage=0.3, timeout=5)
TON1 = Timer('TON1', timeout=3)

events_old = []
events_len_old = 0

while 1:
    key = cv2.waitKey(1)
    
    if key == ord('q'):
        break
    
    cv2.imshow('frame', blank_image)
    
    if key != -1:
        print(f'{key=}')
        AFK.add_event(key)
        print(f'{AFK.check_event(100)=} / {TON1.get_elapsed_time()=}')
        print(f'{TON1.is_running()=} {TON1.is_triggered()=} / {TON1.timeout=}')
        
    AFK.cleanup(time())
        
    events = AFK.get_events()
    if events != events_old:
        print(f'{len(events)=}')
    events_old = events
    
    events_len = len(events)
    if events_len != events_len_old:
        print(f'{events_len=} {[value for _, value in AFK.get_events()]}')
    events_len_old = events_len
    
    if AFK.check_event(100):
        if not TON1.is_running:
            TON1.start()
    else:
        TON1.stop()