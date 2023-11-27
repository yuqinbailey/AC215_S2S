from fastapi import FastAPI, File, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
import asyncio
# from api.tracker import TrackerService
import pandas as pd
import os
from fastapi import File
from tempfile import TemporaryDirectory
from api import api_model
import uuid

# Initialize Tracker Service
# tracker_service = TrackerService()

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global variable to hold the status
video_processing_status = "not_started"


def process_video(video_path):
    global video_processing_status
    video_processing_status = "processing"
    api_model.make_prediction('test')
    video_processing_status = "finished"

@app.on_event("startup")
async def startup():
    print("Startup tasks")
    # Initialize video_processing_status
    global video_processing_status
    video_processing_status = "not_started"

@app.get("/")
async def get_index():
    return {"message": "Welcome to the API Service"}

@app.post("/predict")
async def predict(background_tasks: BackgroundTasks, file: bytes = File(...)):
    global video_processing_status

    video_path = './test.mp4'
    with open(video_path, "wb") as output:
        output.write(file)

    # Reset the status when a new video is uploaded
    video_processing_status = "not_started"

    # Start the video processing in a background task
    background_tasks.add_task(process_video, video_path)

    return {"message": "Video processing started"}

@app.get("/status")
def get_status():
    global video_processing_status
    return {"status": video_processing_status}
