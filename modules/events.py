import time
from math import ceil

class EventContainer:
    def __init__(self, threshold_percentage=.5, timeout=5, min_events=0):
        self.events = []
        self.threshold_percentage = threshold_percentage
        self.timeout = timeout
        self.threshold = 0
        self.min_events = min_events

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
        return event_count >= self.threshold and len(self.get_events()) > self.min_events

    def get_events(self):
        return self.events

    def clear_events(self):
        self.events = []

    def __call__(self, value=1):
        self.cleanup(time.time())
        return self.check_event(value=value)
    

# Reatime demo
if __name__ == "__main__":
    import random
    
    def main():
        container = EventContainer()

        try:
            while True:
                print('---------------------------------')               

                value = random.choice([0, 1])
                container.add_event(value)

                print('Current events:')
                for event in container.get_events():
                    print(event)

                print(f'Event count: {len(container.get_events())}')
                
                if container(1):
                    print('Event triggered!')

                time.sleep(random.uniform(1, 2))

        except KeyboardInterrupt:
            print("Program stopped.")
            
    main()