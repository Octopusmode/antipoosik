from time import time

class Alarm():
    def __init__(self, timeout=10):
        self.alarm_timer = .0
        self.alarm_timeout = timeout
        self.alarm_triggered = False
        self.alarm_status = False
        
        self.time_elasped = .0
        
        self.input_list = []
        self.input_list_previous = []
    
    def process_inputs(self, input_list :list):
        self.input_list = input_list
        self.alarm_triggered = all(self.input_list) is True
        if self.alarm_triggered:
            self.alarm_timer = time()
        else:
            self.timeout_reset()
        if self.input_list != self.input_list_previous:
            self.input_list_previous = self.input_list
            self.alarm_status = True
        else:
            self.alarm_status = False
        return self.alarm_triggered
    
    def timeout_reset(self):
        self.alarm_timer = .0

    def is_triggered(self):
        self.time_elasped = time() - self.alarm_timer
        return self.time_elasped > self.alarm_timeout
    
    def is_state_changed(self):
        self.process_inputs(self.input_list)
        return self.alarm_status
    
    def get_time_elapsed(self):
        self.is_triggered()
        return self.time_elasped
