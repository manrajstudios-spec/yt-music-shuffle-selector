import torch
import json
from ytmusicapi import YTMusic
from sentence_transformers import SentenceTransformer

# print(torch.load("Data/song_data.pt",weights_only=False).keys())


yt_music = YTMusic("Data/browser.json")
source_playlist_id = "PLmVrfZmSPBK1kYEWdgbB9dlB1L7AB8hbB"



playlist_data = yt_music.get_watch_playlist(playlistId=source_playlist_id, limit=200, shuffle=False)

all_songs = [song["title"] for song in playlist_data["tracks"]]

with open("Data/songs.json","w") as file:
    json.dump(all_songs,file,indent=4)


video_ids = [song["videoId"] for song in playlist_data["tracks"]]

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

embeddings = model.encode(video_ids, convert_to_tensor=True,device="cuda")

song_data = {"names":all_songs,"video_ids":video_ids,"embeddings":embeddings}

torch.save(song_data,"Data/song_data.pt")