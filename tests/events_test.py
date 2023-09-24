import unittest
from events import EventContainer
import time

class EventContainerTest(unittest.TestCase):
    def setUp(self):
        self.container = EventContainer()

    def test_add_event(self):
        self.container.add_event(5)
        self.assertEqual(len(self.container.get_events()), 1)

    def test_cleanup(self):
        self.container.add_event(5)
        self.container.cleanup(time.time() + 10)
        self.assertEqual(len(self.container.get_events()), 0)

    def test_check_event(self):
        self.container.add_event(5)
        self.container.add_event(5)
        self.container.add_event(10)
        self.assertTrue(self.container.check_event(5))
        self.assertFalse(self.container.check_event(10))

    def test_clear_events(self):
        self.container.add_event(5)
        self.container.clear_events()
        self.assertEqual(len(self.container.get_events()), 0)

    def test_threshold_percentage(self):
        self.container.add_event(5)
        self.container.add_event(5)
        self.container.add_event(10)
        self.container.add_event(10)
        self.container.add_event(10)
        self.container.threshold_percentage = 0.6
        self.assertFalse(self.container.check_event(5))
        self.assertTrue(self.container.check_event(10))

    def test_timeout(self):
        self.container.add_event(5)
        time.sleep(6)
        self.assertEqual(len(self.container.get_events()), 0)

if __name__ == '__main__':
    unittest.main()