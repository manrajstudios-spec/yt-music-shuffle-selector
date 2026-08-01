# 🎵 T-Music Shuffle Selector

<div align="center">

**An AI-powered music shuffle system that learns what makes a playlist sound good.**

Instead of returning a completely random shuffle, T-Music Shuffle Selector generates multiple candidate playlists, evaluates them using a neural network, and only presents shuffles predicted to provide a better listening experience.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![NumPy](https://img.shields.io/badge/NumPy-Scientific_Computing-blue?logo=numpy)
![JavaScript](https://img.shields.io/badge/JavaScript-Browser_Extension-yellow?logo=javascript)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## ✨ Features

* 🧠 AI-powered playlist quality prediction
* 🎲 Intelligent shuffle generation
* 🔄 Automatic shuffle regeneration
* 📈 Continuous learning from user feedback
* 🎵 Local playlist support
* ▶️ Automatic YouTube playlist playback
* ⌨️ Global keyboard media controls
* 🌐 Browser extension for YouTube control
* ⚡ FastAPI backend
* 🎯 Automatic dataset generation for new songs

---

# 📸 Demo

> **Coming Soon**

| Shuffle Generation | Playback | Dataset Builder |
| ------------------ | -------- | --------------- |
| *(GIF)*            | *(GIF)*  | *(GIF)*         |

---

# 🏗️ Architecture

```text
                  Local Playlist
                        │
                        ▼
               Generate Random Shuffle
                        │
                        ▼
               Generate Song Embeddings
                        │
                        ▼
              3-Layer Neural Network
                        │
          ┌─────────────┴─────────────┐
          │                           │
      Prediction = 0             Prediction = 1
      (Bad Shuffle)             (Good Shuffle)
          │                           │
          ▼                           ▼
  Generate New Shuffle         Show To User
                                      │
                                      ▼
                            User Feedback (👍 / 👎)
                                      │
                                      ▼
                              Update Dataset
                                      │
                                      ▼
                              Retrain Model
```

---

# 🚀 How It Works

## Step 1 — Load Playlist

The application reads every song from a locally stored playlist.

Each song stores metadata including its corresponding YouTube video ID.

---

## Step 2 — Generate Candidate Shuffle

A random ordering of the playlist is created.

Unlike a traditional music player, this shuffle is **not immediately shown** to the user.

---

## Step 3 — Embed the Playlist

Every song is converted into an embedding representation.

The embeddings are combined to represent the entire playlist before being passed into the neural network.

---

## Step 4 — Evaluate the Shuffle

A custom **3-layer neural network** predicts whether the generated shuffle is likely to sound good.

Output:

```
1 → Good Playlist
0 → Bad Playlist
```

If the prediction is **0**, the shuffle is discarded and another candidate is generated.

This continues until the model predicts a high-quality shuffle.

---

## Step 5 — Play the Playlist

Once accepted:

* Video IDs are collected
* The YouTube playlist is opened
* Playback starts

---

# 🎮 Playback System

The playback pipeline consists of three independent components.

```text
Keyboard
    │
    ▼
FastAPI Backend
    │
    ▼
Browser Extension
    │
    ▼
Injected JavaScript
    │
    ▼
YouTube Player
```

The browser extension injects JavaScript into YouTube pages.

Whenever FastAPI receives a media command, it forwards the request to the extension, which directly controls the YouTube player.

---

# ⌨️ Keyboard Controls

| Input        | Action          |
| ------------ | --------------- |
| Single Press | ⏯ Play / Pause  |
| Double Press | ⏭ Next Song     |
| Triple Press | ⏮ Previous Song |

---

# 📚 Learning From Feedback

Every accepted playlist becomes training data.

If the user enjoys the playlist:

```
Label = 1
```

If the playlist feels poor:

```
Label = 0
```

The dataset grows over time, allowing the classifier to improve with real user preferences.

---

# ➕ Adding New Songs

Whenever songs are added to the local playlist, simply run

```bash
python add_new_songs.py
```

The script automatically:

* detects new songs
* asks whether they belong near the **Top**, **Middle**, or **Bottom** of a playlist
* updates the dataset
* generates additional training playlists
* retrains the classifier

If multiple songs are added simultaneously, they are grouped together before playlist generation.

---

# 📊 Dataset Generation

The project contains a template dataset consisting of **50 playlists**.

Each playlist is labelled as:

```
1 = Good Playlist

0 = Bad Playlist
```

Negative playlists intentionally place songs in poor positions.

Positive playlists arrange songs according to their preferred ranking.

This creates balanced supervised training data.

---

# 📂 Project Structure

```text
T-Music-Shuffle-Selector/

├── backend/
│   ├── FastAPI server
│   └── Keyboard listener
│
├── extension/
│   ├── manifest.json
│   ├── content.js
│   └── background.js
│
├── model/
│   ├── network.py
│   ├── train.py
│   └── weights/
│
├── dataset/
│   ├── playlists.json
│   └── labels.json
│
├── embeddings/
│
├── add_new_songs.py
├── shuffle.py
└── README.md
```

---

# 🛠️ Tech Stack

| Category           | Technology               |
| ------------------ | ------------------------ |
| Language           | Python                   |
| Backend            | FastAPI                  |
| Machine Learning   | NumPy                    |
| Browser Automation | JavaScript               |
| Extension          | Chrome/Firefox Extension |
| Playback           | YouTube                  |
| Dataset            | Local JSON / NumPy       |
| Music Source       | Local Playlist           |

---

# 🔮 Future Work

* Transformer-based playlist ranking
* Reinforcement learning from user feedback
* Personalized embeddings
* Genre-aware shuffling
* Playlist similarity search
* Web dashboard
* Explainable AI predictions
* Playlist quality score instead of binary classification

---

# 💡 Motivation

Traditional shuffle algorithms assume every ordering is equally good.

In reality, the transition between songs affects the listening experience.

This project explores whether a machine learning model can learn those transitions and generate playlist orders that feel more natural than a purely random shuffle.

---

# 📄 License

This project is licensed under the MIT License.
