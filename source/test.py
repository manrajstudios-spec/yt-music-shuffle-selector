from evdev import list_devices,InputDevice

for device in list_devices():
    print(InputDevice(device).name == "input-remapper keyboard")