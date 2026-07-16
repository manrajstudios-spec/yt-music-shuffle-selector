import time
import threading
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from evdev import InputDevice, ecodes,list_devices
from mediapipe.tasks.python.vision import GestureRecognizer,GestureRecognizerOptions,RunningMode

base_options = BaseOptions(model_asset_path="Models/gesture_recognizer.task")
options = GestureRecognizerOptions(base_options=base_options,num_hands=1,min_tracking_confidence=0.4,min_hand_detection_confidence=0.4,running_mode=RunningMode.VIDEO)
gesture_recognizer = GestureRecognizer.create_from_options(options=options)

user_input = ""

def record_gesture():
    global user_input

    cap = cv.VideoCapture(0)

    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv.CAP_PROP_FPS, 30)
    cap.set(cv.CAP_PROP_BRIGHTNESS, 110)
    cap.set(cv.CAP_PROP_CONTRAST, 60)

    while True:
        if user_input:
            continue

        ret, frame = cap.read()


        if not ret:
            break

        timestamp_ms = int(cap.get(cv.CAP_PROP_POS_MSEC))

        frame = cv.flip(frame, 1)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        mp_image = mp.Image(data=frame, image_format=mp.ImageFormat.SRGB)

        result = gesture_recognizer.recognize_for_video(mp_image, timestamp_ms)

        if result.gestures:
            hand_gestures = result.gestures[0]

            if hand_gestures:
                top_gesture = hand_gestures[0]
                gesture_name = top_gesture.category_name
                confidence = top_gesture.score

                if gesture_name == "Open_Palm" and confidence > 0.5:
                    user_input = "play_pause"

def record_keyboard():
    global user_input

    keyboard = None

    for device_path in list_devices():
        device = InputDevice(device_path)

        if device.name == "input-remapper keyboard":
            keyboard = device
            break

    single_press = False
    start_time = 0.0
    double_press_window = 0.35

    while True:
        if user_input:
            continue

        if single_press and time.time() - start_time > double_press_window:
            single_press = False
            user_input = "next"

        event = keyboard.read_one()

        if event:
            if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_F14 and event.value == 1:
                if single_press and time.time() - start_time < double_press_window:
                    single_press = False
                    user_input = "prev"
                elif not single_press:
                    single_press = True
                    start_time = time.monotonic()


if __name__ == "__main__":
    gesture_thread = threading.Thread(target=record_gesture,daemon=True)
    keyboard_thread = threading.Thread(target=record_keyboard,daemon=True)

    gesture_thread.start()
    keyboard_thread.start()
    window_started = False

    start_time = 0.0

    while True:
        if user_input and not window_started:
            start_time = time.monotonic()
            window_started = True
            print(user_input)

        if time.time() - start_time > 2 and user_input and window_started:
            user_input = ""
            window_started = False