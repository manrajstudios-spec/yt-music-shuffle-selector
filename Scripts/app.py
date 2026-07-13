from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://music.youtube.com"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    while True:
        user_input = input("Enter What Yu Wanna Do --> ")

        if user_input in ["pause_play","prev","next"]:
            return {"message":user_input}