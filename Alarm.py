from time import time

class Alarm():
    # Debug variables
    def __init__(self):
        self.afk_status_old = False
        self.chair_status_old = False
        self.afk_alarm = False
        self.afk_alarm_old = False
        self.afk_timer = .0
        self.alarm_timeout = 10
        self.afk_timer_status = False
        self.afk_timer_status_old = False
        self.afk_alarm_status = False
        self.afk_alarm_status_old = False
    