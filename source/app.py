import user_input
from fastapi import FastAPI
from classifier import get_classifier,get_shuffle
from fastapi.middleware.cors import CORSMiddleware
from user_input import start_recording

get_shuffle()
start_recording()
playlist_classifier = get_classifier()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://music.youtube.com"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/action")
def root():
    user_input.user_action_event.wait()
    return {"message":user_input.user_action}


@app.get("/action_done")
def action_done():
    user_input.set_user_input_null()
    user_input.user_action_event.clear()
    return {"message":"done"}

