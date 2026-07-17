import json
import math
import torch
import random
import webbrowser
from param import Param
from ytmusicapi import YTMusic

class Classifier:
    def __init__(self):
        self.w1 = Param(shape=(384,128),random=True)
        self.b1 = Param(shape=(1,128),random=False)

        self.w2 = Param(shape=(20*128,64),random=True)
        self.b2 = Param(shape=(1,64),random=False)

        self.w3 = Param(shape=(64,2),random=True)
        self.b3 = Param(shape=(1,2),random=False)

        self.params = [self.w1,self.b1,self.w2,self.b2,self.w3,self.b3]

        self.z1=None
        self.z2=None
        self.z3=None
        self.a1=None
        self.a2=None
        self.flat=None

        self.epochs = 20
        self.targets = []
        self.train_embeds = []

        self.probs = None

        self.song_data = torch.load("Data/song_data.pt",weights_only=False)

    def get_data(self):
        try:
            with open("Data/dataset.json", "r") as f:
                dataset = json.load(f)
        except FileNotFoundError as e:
            print(e)
            dataset = []

        for good, bad in zip(dataset[0], dataset[1]):
            good_embeds = []
            bad_embeds = []

            for g, b in zip(good["songs"], bad["songs"]):
                try:
                    g_id = self.song_data["names"].index(g)
                except ValueError:
                    print(g)

                try:
                    b_id = self.song_data["names"].index(b)
                except ValueError:
                    print(b)
                good_embeds.append(self.song_data["embeddings"][g_id])
                bad_embeds.append(self.song_data["embeddings"][b_id])

            self.train_embeds.append(good_embeds)
            self.train_embeds.append(bad_embeds)

            self.targets.append(good["clf"])
            self.targets.append(bad["clf"])

    @staticmethod
    def gelu(x):
        c = math.sqrt(2.0 / math.pi)
        return 0.5 * x * (1.0 + torch.tanh(c * (x + 0.044715 * x ** 3)))

    @staticmethod
    def gelu_backward(z, grad_out):
        c = math.sqrt(2.0 / math.pi)
        a = 0.044715
        u = c * (z + a * z ** 3)
        tanh_u = torch.tanh(u)
        du_dx = c * (1.0 + 3.0 * a * z ** 2)
        gelu_grad = 0.5 * (1.0 + tanh_u) + 0.5 * z * (1.0 - tanh_u ** 2) * du_dx

        return grad_out * gelu_grad

    @staticmethod
    def softmax(x):
        e = torch.exp(x - x.max(dim=-1, keepdim=True).values)
        return e / e.sum(dim=-1, keepdim=True)

    @staticmethod
    def cross_entropy_loss(probs, target):
        return -torch.log(probs[0, target].clamp_min(1e-8))

    def forward(self,x):
        z1 = x @ self.w1.value + self.b1.value
        a1 = self.gelu(z1)

        flat = a1.reshape(1,-1)

        z2 = flat @ self.w2.value + self.b2.value
        a2 = self.gelu(z2)

        z3 = a2 @ self.w3.value + self.b3.value

        probs = self.softmax(z3)

        self.z1=z1
        self.a1=a1
        self.flat=flat
        self.z2=z2
        self.a2=a2
        self.z3=z3
        self.probs = probs

    def backward(self,x,y):
        d_z3 = self.probs.clone()
        d_z3[0, y] -= 1

        d_w3 = self.a2.T @ d_z3
        d_b3 = d_z3.sum(dim=0, keepdim=True)

        d_a2 = d_z3 @ self.w3.value.T

        d_z2 = self.gelu_backward(self.z2, d_a2)

        d_w2 = self.flat.T @ d_z2
        d_b2 = d_z2.sum(dim=0, keepdim=True)

        d_flat = d_z2 @ self.w2.value.T

        d_a1 = d_flat.reshape(self.a1.shape)

        d_z1 = self.gelu_backward(self.z1, d_a1)
        d_w1 = x.T @ d_z1
        d_b1 = d_z1.sum(dim=0, keepdim=True)

        self.w3.grad = d_w3
        self.w2.grad = d_w2
        self.w1.grad = d_w1

        self.b3.grad = d_b3
        self.b2.grad = d_b2
        self.b1.grad = d_b1

    def train(self):
        min_loss = float("inf")
        self.get_data()

        for epoch in range(self.epochs):
            epoch_loss = 0.0

            combined = list(zip(self.train_embeds, self.targets))
            random.shuffle(combined)

            for X, y in combined:
                X = torch.stack(X)

                self.forward(X)
                cur_loss = self.cross_entropy_loss(self.probs, y)

                epoch_loss += cur_loss.item()

                self.backward(X, y)
                self.step()
                self.zero_grad()

            avg_loss = epoch_loss / len(combined)

            if avg_loss < min_loss:
                min_loss = avg_loss
                self.save_model()
                print(f"epoch: {epoch}, loss: {avg_loss}")

    def step(self):
        for param in self.params:
            param.step()

    def zero_grad(self):
        for param in self.params:
            param.zero_grad()

    def save_model(self):
        to_save = {"w1":self.w1.value,"w2":self.w2.value,"w3":self.w3.value,"b1":self.b1.value,"b2":self.b2.value,"b3":self.b3.value}

        torch.save(to_save,"Models/classfier_model.pt")

    def predict(self, X):
        song_embeds = []

        for x in X:
            s_id = self.song_data["names"].index(x)
            song_embeds.append(self.song_data["embeddings"][s_id])

        X = torch.stack(song_embeds)

        self.forward(X)

        prediction = self.probs[0].argmax(dim=0).item()

        return prediction

    def return_good_shuffle(self,all_songs,max_tries=10000):
        all_songs = all_songs.copy()

        for i in range (max_tries):
            random.shuffle(all_songs)
            cur_playlist = all_songs
            impact_songs = cur_playlist[:20]
            prediction = self.predict(impact_songs)

            print(f"try: {i+1}; probs: {self.probs} ; prediction: {prediction}")

            if not prediction or self.probs[0,prediction] < 0.75:
                continue

            video_ids = []

            for song in cur_playlist:
                s_id = self.song_data["names"].index(song)

                video_ids.append(self.song_data["video_ids"][s_id])

            return video_ids,all_songs


if __name__=="__main__":
    try:
        playlist_classifier = Classifier()

        model_config = torch.load("Models/classfier_model.pt",weights_only=True)

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

