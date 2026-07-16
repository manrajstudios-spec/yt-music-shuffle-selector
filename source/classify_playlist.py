import json
from ytmusicapi import YTMusic

yt_music = YTMusic("browser.json")

playlist_id = "PLmVrfZmSPBK1kYEWdgbB9dlB1L7AB8hbB"

i = 0
good_or_data = []

while i < 10:
    print("---------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------")
    i+=1
    songs = yt_music.get_watch_playlist(playlistId=playlist_id,limit=200,shuffle=True)


    all_songs = []

    for song in songs["tracks"]:
        print(song["title"])
        all_songs.append(song["title"])

    user_action = input("Do Yu Like The Playlist? y/n --> ")

    if user_action == "y":
        good_or_data.append({"songs":all_songs[:20],"good_bad":1})
    else:
        good_or_data.append({"songs":all_songs[:20],"good_bad":0})

try:
    with open("clf_data.json","r") as f:
        good_or_data.extend(json.load(f))
except:
    pass

with open("clf_data.json","w") as f:
    json.dump(good_or_data,f,indent=4)
