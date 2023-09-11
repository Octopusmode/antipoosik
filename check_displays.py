import sys

if sys.platform.startswith('win'):
    # Код для Windows
    from screeninfo import get_monitors
    monitors = get_monitors()
    print("Количество графических дисплеев:", len(monitors))
elif sys.platform.startswith('linux'):
    # Код для Linux
    from Xlib import display
    data = display.Display().screen()
    print("Количество графических дисплеев:", data.root.nb_outputs)
else:
    print("Операционная система не поддерживается")