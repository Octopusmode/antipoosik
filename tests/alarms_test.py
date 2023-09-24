import unittest
from alarms import Alarm
from time import time
    
class AlarmTest(unittest.TestCase):
    def setUp(self):
        self.alarm = Alarm()

    def test_process_inputs_alarm_triggered(self):
        input_list = [True, True, True]
        self.assertTrue(self.alarm.process_inputs(input_list))

    def test_process_inputs_alarm_not_triggered(self):
        input_list = [True, False, True]
        self.assertFalse(self.alarm.process_inputs(input_list))

    def test_timeout_reset(self):
        self.alarm.timeout_reset()
        self.assertEqual(self.alarm.alarm_timer, 0.0)

    def test_is_triggered_true(self):
        self.alarm.alarm_timer = 0.0
        self.alarm.alarm_timeout = 10
        self.assertTrue(self.alarm.is_triggered())

    def test_is_triggered_false(self):
        self.alarm.alarm_timer = time() - 5  # less than timeout
        self.alarm.alarm_timeout = 10
        self.assertFalse(self.alarm.is_triggered())

    def test_is_state_changed_true(self):
        self.alarm.input_list = [True, False, True]
        self.alarm.input_list_previous = [False, False, True]
        self.assertTrue(self.alarm.is_state_changed())

    def test_is_state_changed_false(self):
        self.alarm.input_list = [True, False, True]
        self.alarm.input_list_previous = [True, False, True]
        self.assertFalse(self.alarm.is_state_changed())

    def test_get_time_elapsed(self):
        self.alarm.alarm_timer = time() - 5  # less than timeout
        self.alarm.alarm_timeout = 10
        self.assertEqual(round(self.alarm.get_time_elapsed(), 2), 5.0)

if __name__ == '__main__':
    unittest.main()