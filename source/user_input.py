import time
import threading
import cv2 as cv
import mediapipe as mp
from contextlib import redirect_stderr
from mediapipe.tasks.python import BaseOptions
from evdev import InputDevice, ecodes,list_devices
from mediapipe.tasks.python.vision import GestureRecognizer,GestureRecognizerOptions,RunningMode

base_options = BaseOptions(model_asset_path="Models/gesture_recognizer.task")
options = GestureRecognizerOptions(base_options=base_options,num_hands=1,min_tracking_confidence=0.4,min_hand_detection_confidence=0.4,running_mode=RunningMode.VIDEO)
gesture_recognizer = GestureRecognizer.create_from_options(options)

user_action = ""
user_action_event = threading.Event()

def record_gesture():
    global user_action

    cap = cv.VideoCapture(0)

    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv.CAP_PROP_FPS, 30)
    cap.set(cv.CAP_PROP_BRIGHTNESS, 100)
    cap.set(cv.CAP_PROP_CONTRAST, 20)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        timestamp_ms = int(time.monotonic() * 1000)

        frame = cv.flip(frame, 1)

        if user_action:
            time.sleep(0.01)
            continue

        rgb_frame = cv.cvtColor(frame,cv.COLOR_BGR2RGB)

        mp_image = mp.Image(data=rgb_frame,image_format=mp.ImageFormat.SRGB)

        result = gesture_recognizer.recognize_for_video(mp_image,timestamp_ms)

        display_text = "Gesture: None"

        if result.gestures:
            hand_gestures = result.gestures[0]

            if hand_gestures:
                top_gesture = hand_gestures[0]

                gesture_name = top_gesture.category_name
                confidence = top_gesture.score

                display_text = f"Gesture: {gesture_name} | "f"Confidence: {confidence:.2f}"

                if gesture_name == "Open_Palm" and confidence > 0.5:
                    user_action = "play_pause"
                    user_action_event.set()

        cv.putText(frame,display_text,(20, 40),cv.FONT_HERSHEY_SIMPLEX,0.7,(0, 255, 0),2,cv.LINE_AA)

def record_keyboard():
    global user_action

    keyboard = None

    for device_path in list_devices():
        device = InputDevice(device_path)

        if device.name == "input-remapper keyboard":
            keyboard = device
            break

    single_press = False
    start_time = 0.0
    double_press_window = 0.37

    while True:
        if user_action:
            time.sleep(0.02)
            continue

        if single_press and time.monotonic() - start_time > double_press_window:
            single_press = False
            user_action = "next"
            user_action_event.set()

        event = keyboard.read_one()
        if not event:
            time.sleep(0.02)
            continue

        if event:
            if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_F14 and event.value == 1:
                if single_press and time.monotonic() - start_time < double_press_window:
                    single_press = False
                    user_action = "prev"
                    user_action_event.set()
                elif not single_press:
                    single_press = True
                    start_time = time.monotonic()


def set_user_input_null():
    global user_action
    user_action = ""

def start_recording():
    global user_action
    gesture_thread = threading.Thread(target=record_gesture,daemon=True)
    keyboard_thread = threading.Thread(target=record_keyboard,daemon=True)

    gesture_thread.start()
    keyboard_thread.start()

if __name__ == "__main__":
    gesture_thread = threading.Thread(target=record_gesture,daemon=True)
    keyboard_thread = threading.Thread(target=record_keyboard,daemon=True)

    gesture_thread.start()
    keyboard_thread.start()
    window_started = False

    start_time = 0.0

    while True:
        if user_action and not window_started:
            start_time = time.monotonic()
            window_started = True
            print(user_action)

        if time.monotonic() - start_time > 2 and user_action and window_started:
            user_action = ""
            window_started = False
