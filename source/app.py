import torch
import webbrowser
from fastapi import FastAPI
from classifier import Classifier
from key_press_detection import get_input
from threading import Thread
from gesture_handler import recognize_gesture
from fastapi.middleware.cors import CORSMiddleware

playlist_classifier = None

try:
    with open("Models/classfier_model.pt", "rb") as f:
        playlist_classifier = torch.load(f, weights_only=False)
except FileNotFoundError:
    playlist_classifier = Classifier()
    playlist_classifier.train()

good_playlist, good_playlist_id = playlist_classifier.return_good_shuffle()

url = "https://music.youtube.com/playlist"f"?list={good_playlist_id}"

firefox = webbrowser.get("firefox")
firefox.open(url)

print(good_playlist[:20])

open_palm = False
key_press = ""

gesture_thread = None
key_press_thread = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://music.youtube.com"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    while True:
        user_input = input("Enter What Yu Wanna Do --> ")

        if user_input in ["pause_play","prev","next"]:
            return {"message":user_input}

def get_action():
    global gesture_thread, key_press_thread

    def keyboard_thread():
        global key_press

        while True:
            key_press = get_input()
            if key_press:
                break

    def gesture_thread_func():
        global open_palm

        while True:
            open_palm = recognize_gesture()
            if open_palm:
                break

    while True:
        if gesture_thread is None:
            gesture_thread = Thread(target=keyboard_thread)
            gesture_thread.start()
        if key_press_thread is None:
            key_press_thread = Thread(target=gesture_thread_func)
            key_press_thread.start()


        while not open_palm and not key_press:
            continue


        if open_palm:
            open_palm = False
            gesture_thread = None
        else:
            key_press = ""
            key_press_thread = None

        print(f"{open_palm if open_palm else key_press}")

if __name__ == "__main__":
    get_action()