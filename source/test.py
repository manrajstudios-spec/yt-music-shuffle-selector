import torch

song_data = torch.load("Data/song_data.pt",weights_only=False)

for name in song_data["names"]:
    print(name)