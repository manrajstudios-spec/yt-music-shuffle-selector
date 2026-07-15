from evdev import InputDevice, ecodes,list_devices
import time

def get_device():
    keyboard = None

    for path in list_devices():
        device = InputDevice(path)

        if device.name == "input-remapper keyboard":
            keyboard = device
            return keyboard


def get_input():
    keyboard = get_device()
    print(keyboard)

    single_press = False
    start_time = 0

    while True:
        event = keyboard.read_one()

        if event is None:
            if single_press and time.time()-start_time > 0.34:
                return "single_press"

            continue

        if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_F14 and event.value == 1:
            if not single_press:
                single_press = True
                start_time = time.time()
            else:
                if time.time() - start_time < 0.34:
                    return "double_press"
                else:
                    return "single_press"

if __name__ == "__main__":
    print(get_input())






