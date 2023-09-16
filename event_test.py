import cv2
import numpy as np
from time import time

from tools import EventContainer as Event

blank_image = np.zeros(shape=(600, 800, 3), dtype=np.uint8)

AFK = Event(threshold_percentage=0.3, timeout=5)

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
        print(f'{AFK.check_event(100)=}')
        
    AFK.cleanup(time())
        
    events = AFK.get_events()
    if events != events_old:
        print(f'{len(events)=}')
    events_old = events
    
    events_len = len(events)
    if events_len != events_len_old:
        print(f'{events_len=} {[value for _, value in AFK.get_events()]}')
    events_len_old = events_len