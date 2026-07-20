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

not_found = []

for song in all_songs:
    if song not in song_data["names"]:
        not_found.append(song)

not_found_song_priority =[]

for song in not_found:
    while True:
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

                    not_found_song_priority.append({"name":song,"position":position})                
                    break
        break

new_songs_split = [not_found_song_priority[i:i + 3] for i in range(0, len(not_found_song_priority), 3)] 

len_split = len(template_dataset) // len(new_songs_split)

template_split = [template_dataset[i:i+len_split] for i in range(0,len(template_dataset),len_split)]

top = [0,1,2]
middle = [3,4,5]
bottom = [6,7,8,9]

to_add = []

for song_split,template in zip(new_songs_split,template_split):
    for playlist in template:
        if playlist["clf"] == 0:
            random_place = 0

            for song in song_split:
                if song["position"] == 1:
                    random_place = random.randint(middle+bottom)
                elif song['position'] == 2:
                    random_place = random.choice(top + bottom)
                else:
                    random_place = random.choice(top + middle)
                
                playlist["playlist"][random_place] = song["name"]

        else:
            random_place = 0
            for song in song_split:
                if song["position"] == 1:
                    random_place = random.choice(top)
                elif song['position'] == 2:
                    random_place = random.choice(middle)
                else:
                    random_place= random.choice(bottom)
                
                playlist["playlist"][random_place] = song['name']
        
        to_add.append({"playlist":playlist,"clf":playlist["clf"]})

random.shuffle(to_add)

good_count = 10
bad_count = 10

dataset_extension = {}

for addd in to_add:
    if addd["clf"] == 0:
        if bad_count >0:
            bad_count -=1
        else:
            continue
    
    else:
        if good_count > 0:
            good_count -=1
        else:
            continue

    dataset_extension["playlist"].append(addd["playlist"])
    dataset_extension["clf"].append(addd["clf"])

with open("Data/dataset.json",'r') as f:
    loaded = json.load(f)

loaded["playlist"].extend(dataset_extension["playlist"])
loaded["clf"].extend(dataset_extension["clf"])

with open("Data/dataset.json",'w') as f:
    json.dump(loaded,f,indent=4)

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