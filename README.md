# 🎵 T-Music Shuffle Selector

<div align="center">

## An AI-powered music shuffle system that learns how to create better playlists.

T-Music Shuffle Selector replaces traditional random shuffle with an intelligent system that generates playlist orders, evaluates them using a neural network, and improves through user feedback.

</div>

---

## ✨ Features

* 🧠 AI-based shuffle quality prediction
* 🎲 Intelligent playlist shuffle generation
* 🔄 Automatic regeneration of bad shuffles
* 🎵 Song embedding based playlist representation
* 🤖 3-layer neural network classifier
* 📈 Continuous learning from user feedback
* 🎧 YouTube Music integration using `ytmusicapi`
* ▶️ Automatic playlist creation and playback
* ⌨️ Custom keyboard media controls
* ⚡ FastAPI local backend
* 🌐 Browser extension with JavaScript playback control
* ➕ Automatic new song detection and retraining

---

# 📌 Motivation

Traditional shuffle algorithms treat every song order as equally valid.

But a good playlist is not just a random collection of songs. The transition between songs, placement, and overall flow affects the listening experience.

T-Music Shuffle Selector attempts to learn what makes a playlist order feel better by using machine learning and continuous user feedback.

---

# 🏗️ System Architecture

```text
                    Local Playlist
                          |
                          ▼
              Song Metadata Collection
                          |
                          ▼
                    ytmusicapi
                          |
                          ▼
             YouTube Music Track Mapping
                          |
                          ▼
              Generate Candidate Shuffle
                          |
                          ▼
              Generate Song Embeddings
                          |
                          ▼
              3-Layer Neural Network
                          |
              ┌───────────┴───────────┐
              ▼                       ▼
          Prediction 0            Prediction 1
          Bad Shuffle             Good Shuffle
              |                       |
              ▼                       ▼
       Generate Again          Show Playlist
                                      |
                                      ▼
                              User Feedback
                                      |
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
                Positive                              Negative
                Label = 1                             Label = 0
                    |
                    ▼
              Retrain Model
```

---

# 🚀 How It Works

## 1. Playlist Loading

Songs are stored locally with their metadata.

The system connects song information with YouTube Music using `ytmusicapi`.

Stored information includes:

* Song name
* Artist
* Playlist information
* YouTube Music video ID

---

## 2. Shuffle Generation

The system creates a random candidate shuffle from the playlist.

Unlike normal shuffle algorithms, this shuffle is evaluated before being shown to the user.

---

## 3. Song Embeddings

Each song is converted into an embedding representation.

The complete playlist order is transformed into numerical data that can be processed by the neural network.

---

## 4. Neural Network Evaluation

A 3-layer neural network predicts the quality of the generated shuffle.

Output:

```
1 → Good shuffle
0 → Bad shuffle
```

If the model predicts `0`, the shuffle is discarded and regenerated.

This continues until a suitable shuffle is found.

---

# 🎧 YouTube Music Integration

The project uses `ytmusicapi` to communicate with YouTube Music.

It handles:

* Searching songs
* Fetching track information
* Mapping songs to YouTube Music IDs
* Creating playlists
* Connecting local playlists with online playback

After a shuffle is accepted:

1. Songs are converted into YouTube Music tracks.
2. A playlist is generated.
3. Playback begins.

---

# 🎮 Playback Control System

The project uses a FastAPI backend and a browser extension to control playback.

Architecture:

```text
Keyboard Input
       |
       ▼
 FastAPI Backend
       |
       ▼
 Browser Extension
       |
       ▼
 JavaScript Injection
       |
       ▼
 YouTube Music Player
```

The browser extension injects JavaScript into the YouTube Music page and controls the player directly.

---

# ⌨️ Media Controls

A dedicated keyboard key is used for playback control.

| Input        | Action        |
| ------------ | ------------- |
| Single Press | Play / Pause  |
| Double Press | Next Song     |
| Triple Press | Previous Song |

---

# 📚 Learning System

The model improves using user feedback.

If a generated playlist is good:

```
Playlist → Label 1
```

If the generated playlist is bad:

```
Playlist → Label 0
```

These examples are added to the dataset and used for future training.

---

# ➕ Adding New Songs

When new songs are added to the playlist, run:

```bash
python add_new_songs.py
```

The script:

* Detects songs not present in the stored dataset
* Asks the user where the song belongs:

  * Top
  * Middle
  * Bottom
* Generates new training examples
* Updates the dataset
* Retrains the classifier

---

# 📊 Dataset Generation

The project contains a template dataset containing **50 playlists**.

Each playlist has a label:

```
1 → Correct playlist ordering
0 → Incorrect playlist ordering
```

For negative examples:

* Songs are randomly placed into incorrect positions.

For positive examples:

* Songs are placed according to their preferred position.

When multiple songs are added:

1. Songs are grouped in batches.
2. Candidate playlists are generated.
3. Labels are assigned.
4. The model is retrained.

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
│   ├── neural_network.py
│   ├── train.py
│   └── weights/
│
├── dataset/
│   ├── playlists.json
│   └── labels.json
│
├── music/
│   ├── song metadata
│   └── YouTube Music IDs
│
├── add_new_songs.py
├── shuffle.py
└── README.md
```

---

# 🛠️ Tech Stack

| Component            | Technology         |
| -------------------- | ------------------ |
| Language             | Python             |
| Backend              | FastAPI            |
| Machine Learning     | Neural Network     |
| Numerical Processing | NumPy              |
| Music API            | ytmusicapi         |
| Browser Extension    | JavaScript         |
| Playback             | YouTube Music      |
| Storage              | JSON / Local Files |

---

# 🔮 Future Improvements

* Replace binary classification with playlist ranking
* Use reinforcement learning from listening behaviour
* Add multiple user profiles
* Improve song transition modelling
* Add playlist quality scoring
* Create a web dashboard
* Visualize why a shuffle was accepted or rejected

---

# 📜 License

MIT License

---

# ⭐ Project Goal

T-Music Shuffle Selector explores whether a machine learning model can learn the difference between a random playlist and a playlist that feels naturally enjoyable.

Instead of asking:

> "Can we shuffle songs randomly?"

This project asks:

> "Can a model learn how humans prefer songs to flow?"
