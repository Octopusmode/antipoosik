import cv2
import numpy as np
import time

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
        self.threshold = len(self.events) * self.threshold_percentage
        print(f'debug: {self.threshold=}')
        event_count = sum([value for _, value in self.events]) 
        return event_count >= self.threshold

    def get_events(self):
        return self.events

    def clear_events(self):
        self.events = []

    def __call__(self, *args, **kwargs):
        self.cleanup(time.time())
        return self.check_event()