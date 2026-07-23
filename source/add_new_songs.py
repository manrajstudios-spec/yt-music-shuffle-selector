import json
import torch
import shutil
import random
from pathlib import Path
from classifier import Classifier
from save_song_embeddings import load_songs,save_song_data

all_songs,video_ids = load_songs()

with open("Data/template_dataset.json",'r') as f:
    template_dataset = json.load(f)


song_data = torch.load("Data/song_data.pt",weights_only=False)

new_songs = []

for song in all_songs:
    if song not in song_data["names"]:
        new_songs.append(song)

new_songs_priority =[]

for song in new_songs:
    while True:
        print(f"{song}: song")
        ask_user = input("would yu like this song in top 10: Press (1 to reject OR Press Enter For Yes): ")

        if not ask_user:
            while True:
                ask_user_position = input("Where Would Yu Like This Song To Be Placed In Top 10 Songs (1 top: 2 middle: 3 bottom:)--> ")

                if ask_user_position:
                    position = 0

                    if ask_user_position == "1":position=1
                    elif ask_user_position == "2":position=2
                    elif ask_user_position == "3":position=3
                    else:
                        break

                    new_songs_priority.append({"name":song,"position":position})                
                    break
        break

new_song_splits = []
cur_split = []
k = 0

for i,song in enumerate(new_songs_priority):
    k+=1
    cur_split.append(song)
    
    if k == 3 or i == len(new_songs_priority) - 1:
        new_song_splits.append(cur_split)
        cur_split = []
        k=0

template_divided = []

sample_per_split = 20

for split in new_song_splits:
    ids = list(range(len(template_dataset["playlist"])))
    random.shuffle(ids)
    
    template_dataset["playlist"] = [template_dataset["playlist"][i] for i in ids]
    template_dataset["clf"] = [template_dataset["clf"][i] for i in ids]
    to_add = {"playlist":[],"clf":[]}
    
    good_count,bad_count = 10,10
    
    print(f"Template: {len(template_dataset["clf"])}")
    
    for template_playlist,clf in zip(template_dataset["playlist"],template_dataset["clf"]):
        if clf == 0:
            if bad_count <=0 : continue
            bad_count -= 1
            to_add["playlist"].append(template_playlist)
            to_add["clf"].append(0)
         
        else:
            if good_count <= 0: continue
            good_count -= 1
            to_add["playlist"].append(template_playlist)
            to_add["clf"].append(1)
            
        if good_count and bad_count <=0: break
    
    
    print(len(to_add["clf"]))
    template_divided.append(to_add) 
                    
top = [0,1,2]
middle = [3,4,5]
bottom = [6,7,8,9]

extended = {"playlist":[],"clf":[]}

for song_split,template_split in zip(new_song_splits,template_divided):
    ids = list(range(len(template_split["clf"])))
    random.shuffle(ids)
    template_split["playlist"] = [template_split["playlist"][i] for i in ids]
    template_split["clf"] = [template_split["clf"][i] for i in ids]
    
    for playlist,clf in zip(template_split["playlist"],template_split["clf"]):
        if clf == 0:
            for song in song_split:
                position = 0
                
                if song['position'] == 1:
                    position = random.choice(middle + bottom)
                elif song["position"] == 2:
                    position = random.choice(top + bottom)
                else:
                    position = random.choice(top + middle)
                    
                playlist[position] = song 
        else:
            for song in song_split:
                position = 0
                if song["position"] == 1:
                    position = random.choice(top)
                elif song["position"] == 2:
                    position = random.choice(middle)
                else:
                    position = random.choice(bottom)
                
                playlist[position] = song
        
        extended["playlist"].append(playlist)
        extended["clf"].append(clf)

good_count = 15
bad_count = 15

dataset_extension = {"playlist":[],"clf":[]}

ids = list(range(len(extended["clf"])))
random.shuffle(ids)

extended["playlist"] = [extended["playlist"][i] for i in ids]    
extended["clf"] = [extended["clf"][i] for i in ids]    

for playlist,clf in zip(extended["playlist"],extended["clf"]):
    if clf == 1:
        if good_count > 0:
            good_count -=1
            dataset_extension["playlist"].append(playlist)
            dataset_extension["clf"].append(1)
    else:
        if bad_count > 0:
            bad_count -= 1
            dataset_extension["playlist"].append(playlist)
            dataset_extension["clf"].append(1)
            
if new_songs_priority:
    with open("Data/dataset.json",'r') as f:
        loaded = json.load(f)

    loaded["playlist"].extend(dataset_extension["playlist"])
    loaded["clf"].extend(dataset_extension["clf"])

    with open("Data/dataset.json",'w') as f:
        json.dump(loaded,f,indent=4)

    save_song_data(all_songs,video_ids=video_ids)
    
    model_path = Path("Models/classifier_model.pt")
    old_folder = Path("Models/old")

    old_folder.mkdir(parents=True,exist_ok=True)

    if model_path.exists():
        shutil.move(str(model_path),str(old_folder/model_path.name))

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