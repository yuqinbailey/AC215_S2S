from fastapi import FastAPI, File, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from api import api_model
import os
from fastapi.responses import FileResponse

app = FastAPI(title="API Server", description="API Server", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    print("Startup tasks")
    api_model.progress_status = "not_started"

@app.get("/")
async def get_index():
    return {"message": "Welcome to the API Service"}

@app.post("/predict")
async def predict(background_tasks: BackgroundTasks, file: bytes = File(...)):
    video_path = './test.mp4'
    with open(video_path, "wb") as output:
        output.write(file)
    
    background_tasks.add_task(api_model.make_prediction, 'test')

    return {"message": "Video processing started"}

@app.get("/status")
def get_status():
    return {"status": api_model.progress_status}

@app.get("/get_video")
def get_video():
    video_path = './results/test.mp4'
    if os.path.exists(video_path):
        headers = {
            'Content-Disposition': 'attachment; filename="test.mp4"',
            'Content-Type': 'video/mp4'
        }
        return FileResponse(video_path, headers=headers)
    else:
        return {"message": "File does not exist"}, 404
