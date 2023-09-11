from typing import Any
from evdev import ecodes, categorize

def get_current_key(device) -> Any:
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event: Any = categorize(event=event)
            if key_event.keystate == key_event.key_down:
                return key_event.keycode

# Пример использования функции
# from evdev import InputDevice
# device = InputDevice('/dev/input/event6')