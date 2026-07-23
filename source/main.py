import os
import json
import torch
import threading
import webbrowser
import uvicorn as uv
from app import app
from rich.panel import Panel
from rich.table import Table

from rich.prompt import Prompt
from ytmusicapi import YTMusic,OAuthCredentials
from rich.console import Console
from classifier import Classifier
from user_input import start_recording

console = Console()

with open("Data/auth_file.json",'r') as f:
    auth = json.load(f)
    CLIENT_ID = auth["ID"]
    CLIENT_SECRET = auth["KEY"] 


yt_music = YTMusic("Data/browser.json")

source_playlist_id = "PLmVrfZmSPBK1kYEWdgbB9dlB1L7AB8hbB"


def start_uvicorn_server():
    uv.run(app,host="127.0.0.1",port=8000,log_level="critical",access_log=False)

def get_classifier():
    try:
        playlist_classifier = Classifier()

        model_config = torch.load("Models/classifier_model.pt",weights_only=True)

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
        yt_music.delete_playlist(playlistId=last_playlist_id)

    all_songs = []

    with open("Data/songs.json","r") as f:
        all_songs = json.load(f)

    return all_songs


def get_shuffle():
    classifier = get_classifier()
    all_songs = get_all_songs()

    shuffle,video_ids = classifier.return_good_shuffle(all_songs)

    classifier = None

    return shuffle, video_ids


def open_shuffle(video_ids):
    created_playlist_id = yt_music.create_playlist(title="temp",description="auto generated",privacy_status="PRIVATE")

    if not isinstance(created_playlist_id, str):
        print("Playlist creation failed:",created_playlist_id)
        return

    yt_music.add_playlist_items(created_playlist_id,videoIds=video_ids)

    with open("Data/last_playlist_id.txt", "w") as file:
        file.write(created_playlist_id)

    url = webbrowser.open("https://music.youtube.com/playlist"f"?list={created_playlist_id}")



def record_input():
    start_recording()


def show_shuffle(shuffle):
    table = Table(title="Generated Shuffle",show_header=True,header_style="bold cyan")

    table.add_column("#", justify="right")
    table.add_column("Song")

    for index, song in enumerate(shuffle[:10], start=1):
        table.add_row(str(index), song)

    console.print(table)

if __name__ == "__main__":

    with open("Data/dataset.json",'r') as f:
        dataset = json.load(f)

    shuffle, video_ids = [], []
    threading.Thread(target=start_uvicorn_server,daemon=True).start()

    console.print(
        Panel.fit("[bold red]YT Music Shuffle Selector[/bold red]\n" "[dim yellow]Generate a playlist based on your classifier[/dim yellow]"))


    while True:
        if not shuffle:
            Prompt.ask("\n[bold green]Press Enter to generate a shuffle[/bold green]")

            try:
                with console.status("[bold cyan]Generating shuffle...[/bold cyan]",spinner="moon"):
                    shuffle, video_ids = get_shuffle()

            except Exception as error:
                console.print(f"[bold red]Failed to generate shuffle:[/bold red] {error}")
                shuffle, video_ids = [], []
                continue

        show_shuffle(shuffle)

        choice = Prompt.ask("\n[bold]Choose an action[/bold]",choices=["play", "regenerate", "quit","skip"],default="play")

        if choice == "play":
            try:                
                threading.Thread(target=start_recording,daemon=True).start()

                with console.status("[bold green]Creating YouTube Music playlist...[/bold green]",spinner="aesthetic"):
                    open_shuffle(video_ids)

                console.print("[bold green]Playlist opened successfully.[/bold green]")


                shuffle, video_ids = [], []

            except Exception as error:
                console.print(f"[bold red]Failed to open playlist:[/bold red] {error}")
            
        elif choice == "regenerate":
            console.print("[yellow]Discarding current shuffle...[/yellow]")
            dataset["playlist"].append(shuffle[:10])
            dataset["clf"].append(0)

            with open("Data/dataset.json",'w') as file:
                json.dump(dataset,file,indent=4)
            shuffle, video_ids = [], []

        elif choice == "quit":
            console.print("[bold cyan]Goodbye 🎵[/bold cyan]")
            break
        elif choice == "skip":
            console.print("[blue]skipping current shuffle...[/blue]")
            shuffle, video_ids = [], []

