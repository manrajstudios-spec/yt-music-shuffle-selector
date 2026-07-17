import torch
import threading
import webbrowser
import tkinter as tk

import uvicorn as uv

from app import app
from ytmusicapi import YTMusic
from classifier import Classifier
from user_input import start_recording


yt_music = YTMusic("Data/browser.json")
source_playlist_id = "PLmVrfZmSPBK1kYEWdgbB9dlB1L7AB8hbB"

video_ids = []
shuffle = []


def start_uvicorn_server():
    uv.run(
        app,
        host="127.0.0.1",
        port=8000
    )


def get_classifier():
    try:
        playlist_classifier = Classifier()

        model_config = torch.load(
            "Models/classfier_model.pt",
            weights_only=True
        )

        playlist_classifier.w1.value = model_config["w1"]
        playlist_classifier.w2.value = model_config["w2"]
        playlist_classifier.w3.value = model_config["w3"]

        playlist_classifier.b1.value = model_config["b1"]
        playlist_classifier.b2.value = model_config["b2"]
        playlist_classifier.b3.value = model_config["b3"]

    except FileNotFoundError:
        playlist_classifier = Classifier()
        playlist_classifier.train()
        playlist_classifier.save_model()

    return playlist_classifier


def get_all_songs():
    try:
        with open("Data/last_playlist_id.txt", "r") as file:
            last_playlist_id = file.read().strip()

    except FileNotFoundError:
        last_playlist_id = ""

    if last_playlist_id:
        yt_music.delete_playlist(
            playlistId=last_playlist_id
        )

    playlist_data = yt_music.get_watch_playlist(
        playlistId=source_playlist_id,
        limit=200,
        shuffle=True
    )

    all_songs = [
        song["title"]
        for song in playlist_data["tracks"]
    ]

    return all_songs


def get_shuffle():
    global video_ids, shuffle

    classifier = get_classifier()
    all_songs = get_all_songs()

    video_ids, shuffle = classifier.return_good_shuffle(
        all_songs
    )

    return shuffle, video_ids


def open_shuffle():
    created_playlist_id = yt_music.create_playlist(
        title="temp",
        description="auto generated",
        privacy_status="PRIVATE"
    )

    if not isinstance(created_playlist_id, str):
        print(
            "Playlist creation failed:",
            created_playlist_id
        )
        return

    yt_music.add_playlist_items(
        created_playlist_id,
        videoIds=video_ids
    )

    with open("Data/last_playlist_id.txt", "w") as file:
        file.write(created_playlist_id)

    firefox = webbrowser.get("firefox")

    url = (
        "https://music.youtube.com/playlist"
        f"?list={created_playlist_id}"
    )

    firefox.open(url)


def record_input():
    start_recording()


class ShuffleWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("YT Music Shuffle Selector")
        self.geometry("520x520")
        self.minsize(440, 420)

        self.configure(bg="#121212")

        self.title_label = tk.Label(
            self,
            text="YT Music Shuffle Selector",
            bg="#121212",
            fg="white",
            font=("Arial", 22, "bold"),
            pady=18
        )

        self.title_label.pack()

        self.status = tk.Label(
            self,
            text="Generate a shuffle to begin",
            bg="#121212",
            fg="#dddddd",
            font=("Arial", 12),
            pady=8
        )

        self.status.pack()

        self.song_list = tk.Listbox(
            self,
            bg="#202020",
            fg="white",
            selectbackground="#1db954",
            selectforeground="black",
            highlightbackground="#333333",
            highlightcolor="#333333",
            relief="flat",
            borderwidth=0,
            font=("Arial", 11)
        )

        self.generate_button = tk.Button(
            self,
            text="Generate Shuffle",
            command=self.generate,
            bg="#1db954",
            fg="black",
            activebackground="#26d865",
            activeforeground="black",
            relief="flat",
            borderwidth=0,
            font=("Arial", 12, "bold"),
            padx=20,
            pady=12,
            cursor="hand2"
        )

        self.generate_button.pack(
            fill="x",
            padx=30,
            pady=20
        )

        self.decision_frame = tk.Frame(
            self,
            bg="#121212"
        )

        self.reshuffle_button = tk.Button(
            self.decision_frame,
            text="Reshuffle",
            command=self.generate,
            bg="#333333",
            fg="white",
            activebackground="#444444",
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            font=("Arial", 11, "bold"),
            padx=15,
            pady=12,
            cursor="hand2"
        )

        self.reshuffle_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 6)
        )

        self.play_button = tk.Button(
            self.decision_frame,
            text="Play This Shuffle",
            command=self.play_shuffle,
            bg="#1db954",
            fg="black",
            activebackground="#26d865",
            activeforeground="black",
            relief="flat",
            borderwidth=0,
            font=("Arial", 11, "bold"),
            padx=15,
            pady=12,
            cursor="hand2"
        )

        self.play_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(6, 0)
        )

    def generate(self):
        self.status.config(
            text="Generating a good shuffle..."
        )

        self.generate_button.config(
            state="disabled"
        )

        self.reshuffle_button.config(
            state="disabled"
        )

        self.play_button.config(
            state="disabled"
        )

        # Draw the changed status before get_shuffle blocks.
        self.update_idletasks()

        try:
            get_shuffle()

        except Exception as error:
            self.status.config(
                text=f"Shuffle failed: {error}"
            )

            self.generate_button.config(
                state="normal"
            )

            self.reshuffle_button.config(
                state="normal"
            )

            return

        self.show_shuffle()

    def show_shuffle(self):
        self.song_list.delete(0, tk.END)

        for index, song in enumerate(
            shuffle[:15],
            start=1
        ):
            self.song_list.insert(
                tk.END,
                f"{index}. {song}"
            )

        self.status.config(
            text="Keep this shuffle?"
        )

        if not self.song_list.winfo_ismapped():
            self.song_list.pack(
                fill="both",
                expand=True,
                padx=30,
                pady=12
            )

        self.generate_button.pack_forget()

        if not self.decision_frame.winfo_ismapped():
            self.decision_frame.pack(
                fill="x",
                padx=30,
                pady=20
            )

        self.reshuffle_button.config(
            state="normal"
        )

        self.play_button.config(
            state="normal"
        )

    def play_shuffle(self):
        self.status.config(
            text="Creating and opening playlist..."
        )

        self.reshuffle_button.config(
            state="disabled"
        )

        self.play_button.config(
            state="disabled"
        )

        self.update_idletasks()

        try:
            open_shuffle()
            record_input()

            self.status.config(
                text=(
                    "Playlist opened • gesture and "
                    "keyboard detection running"
                )
            )

            self.decision_frame.pack_forget()

        except Exception as error:
            self.status.config(
                text=f"Could not start: {error}"
            )

            self.reshuffle_button.config(
                state="normal"
            )

            self.play_button.config(
                state="normal"
            )


if __name__ == "__main__":
    server_thread = threading.Thread( 
        target=start_uvicorn_server,
        daemon=True,
        name="UvicornThread"
    )

    server_thread.start()

    window = ShuffleWindow()
    window.mainloop()