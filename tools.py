import cv2
import numpy as np
import time
from math import ceil
import logging
from logging import Logger

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

def resize_image(image: np.ndarray, target_resolution: tuple) -> np.ndarray:
    height, width = image.shape[:2]
    
    target_width, target_height = target_resolution

    scale_x = target_width / width
    scale_y = target_height / height
    scale = min(scale_x, scale_y)

    new_width = int(width * scale)
    new_height = int(height * scale)

    resized_image: np.ndarray = cv2.resize(src=image, 
                                           dsize=(new_width, new_height), 
                                           interpolation=cv2.INTER_AREA)
    
    top, left = 0, 0
    bottom = target_height - new_height
    right = target_width - new_width
    
    image = cv2.copyMakeBorder(src=resized_image, 
                               top=top, bottom=bottom, left=left, right=right,
                               borderType=cv2.BORDER_CONSTANT)

    return image
      
        
class EventContainer:
    def __init__(self, threshold_percentage=.5, timeout=5):
        self.events = []
        self.threshold_percentage = threshold_percentage
        self.timeout = timeout
        self.threshold = 0

    def add_event(self, value=0):
        current_time = time.time()
        self.events.append((current_time, value))
        self.cleanup(current_time)

    def cleanup(self, current_time):
        self.events = [(event_time, value) for event_time, value in self.events if current_time - event_time <= self.timeout]

    def check_event(self, value=0):
        self.cleanup(time.time())
        self.threshold = ceil(len(self.events) * self.threshold_percentage)
        event_count = len([val for _, val in self.events if val == value])
        return event_count >= self.threshold

    def get_events(self):
        return self.events

    def clear_events(self):
        self.events = []

    def __call__(self, *args, **kwargs):
        self.cleanup(time.time())
        return self.check_event()
    
    
    """
    events = EventContaiber(threshold_percentage=.5, timeout=5)
    
    while 1:
        if some_action:
            events.add_event(value)
        
        if some_checks:
            if events.check_event(value):
                do_something()
        
    """
    
class Timer():
    """
    Timer class
    """
    def __init__(self, name, timeout=5):
        self.starting_time = time.time()
        self._timeout = float(timeout)
        self.elapsed_time = .0
        self.triggered = False
        self.running = False
        self.name = name
    
    def check_timer_running(func):
        def wrapper(self, *args, **kwargs):
            if func.__name__ == 'start' and self.running:
                logger.info(f'Timer {self.name} is already running')
            elif func.__name__ == 'stop' and not self.running:
                pass
                # logger.info(f'Timer {self.name} is nor running')
            else:
                return func(self, *args, **kwargs)
        return wrapper
    
    @check_timer_running        
    def start(self):
        self.triggered = False
        self.running = True
        self.starting_time = time.time()
        logger.info(f'{self.starting_time=}' + 'Timer {self.name} started')
    
    @check_timer_running
    def stop(self):
        self.running = False
        self.triggered = False
        logger.info(f'{self.starting_time=}' + 'Timer {self.name} stopped')
    
    @property
    def timeout(self):
        return self._timeout
    
    @timeout.setter
    def timeout(self, value):
        self._timeout = value
    
    @check_timer_running
    def is_triggered(self):
        self.elapsed_time = time.time() - self.starting_time
        if self.elapsed_time > self.timeout:
            self.triggered = True
        return self.triggered
    
    def is_running(self):
        return self.running
    
    @check_timer_running
    def get_elapsed_time(self):
        return self.elapsed_time
    
"""
from time import time, sleep

if __name__ == '__main__':
    timer = Timer()
    timer.set_timeout(5)
    timer.start()
    while 1:
        if timer.is_triggered():
            print('Timer triggered')
            timer.stop()
            timer.start()
        print(timer.get_elapsed_time())
        sleep(1)
"""