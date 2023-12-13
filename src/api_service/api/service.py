from fastapi import FastAPI, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from aiohttp import ClientTimeout
import aiohttp
import os
import uuid
import base64

class VideoProcessingManager:
    def __init__(self):
        self.statuses = {}

    def set_status(self, filename, status):
        self.statuses[filename] = status

    def get_status(self, filename):
        return self.statuses.get(filename, "not_started")

video_manager = VideoProcessingManager()

app = FastAPI(title="API Server", description="API Server", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}.mp4"

    video_manager.set_status(unique_filename, "processing")

    file_content = await file.read()
    base64_encoded_file = base64.b64encode(file_content).decode()
    timeout = ClientTimeout(total=3600)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post("http://34.106.213.117:8080/predictions/s2s", 
                                json={"file": base64_encoded_file}) as response:
            if response.status == 200:
                response_data = await response.json()
                base64_encoded_video = response_data['video']
                video_data = base64.b64decode(base64_encoded_video)
                with open(f'./results/{unique_filename}', 'wb') as f:
                    f.write(video_data)
                video_manager.set_status(unique_filename, "completed")
            else:
                video_manager.set_status(unique_filename, "error")
                print("Error processing video:", await response.text())

    return {"message": "Video processing started", "filename": unique_filename}

@app.get("/status/{filename}")
def get_status(filename: str):
    return {"status": video_manager.get_status(filename)}

@app.get("/get_video/{filename}")
def get_video(filename: str):
    video_path = f'./results/{filename}'
    if os.path.exists(video_path):
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'video/mp4'
        }
        return FileResponse(video_path, headers=headers)
    return {"message": "File does not exist"}, 404
