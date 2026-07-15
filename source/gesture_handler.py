import cv2
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions,RunningMode

def recognize_gesture():
    base_options = BaseOptions(model_asset_path="Models/gesture_recognizer.task")
    options = GestureRecognizerOptions(base_options=base_options,num_hands=1,min_tracking_confidence=0.4,min_hand_detection_confidence=0.4,running_mode=RunningMode.VIDEO)
    gesture_recognizer = GestureRecognizer.create_from_options(options=options)

    cap = cv.VideoCapture(0)

    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv.CAP_PROP_FPS, 30)
    cap.set(cv.CAP_PROP_BRIGHTNESS,110)
    cap.set(cv.CAP_PROP_CONTRAST,60)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        cv2.flip(frame,1)

        mp_image = mp.Image(data=frame,image_format=mp.ImageFormat.SRGB)

        result = gesture_recognizer.recognize_for_video(mp_image, timestamp_ms)

        if result.gestures:
            hand_gestures = result.gestures[0]

            if hand_gestures:
                top_gesture = hand_gestures[0]
                gesture_name = top_gesture.category_name
                confidence = top_gesture.score

                if gesture_name == "Open_Palm":
                    cv2.putText(frame,f"OPEN PALM DETECTED ({confidence:.2f})",(50, 80),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 0),2,cv2.LINE_AA)
                    return "open_palm"

if __name__ == "__main__":
    print(recognize_gesture())