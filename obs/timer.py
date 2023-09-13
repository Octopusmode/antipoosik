class Timer():
    """
    Timer class
    """
    def __init__(self):
        from time import time
        self.starting_time = time()
        self.timeout = .0
        self.elapsed_time = .0
        self.triggered = False
        
    def start(self):
        self.triggered = False
        self.starting_time = time()
        
    def stop(self):
        self.triggered = False
        
    def set_timeout(self, timeout):
        self.timeout = timeout
        
    def is_triggered(self):
        self.elapsed_time = time() - self.starting_time
        if self.elapsed_time > self.timeout:
            self.triggered = True
            return True
        return False
    
    def get_elapsed_time(self):
        return self.elapsed_time
    
"""Usage example"""
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