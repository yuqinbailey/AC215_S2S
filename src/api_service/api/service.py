from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import aiohttp
import os
import uuid

app = FastAPI(title="API Server", description="API Server", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

video_processing_status = "not_started"

@app.on_event("startup")
async def startup():
    global video_processing_status
    video_processing_status = "not_started"

@app.get("/")
async def get_index():
    return {"message": "Welcome to the API Service"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    global video_processing_status
    video_processing_status = "processing"
    unique_filename = f"{uuid.uuid4()}.mp4"

    async with aiohttp.ClientSession() as session:
        file_content = await file.read()
        async with session.post("http://34.106.213.117:8080/predictions/s2s", data={"file": file_content}) as response:
            if response.status == 200:
                with open(f'./results/{unique_filename}', 'wb') as f:
                    f.write(await response.read())
                video_processing_status = "completed"
            else:
                video_processing_status = "error"
                print("Error processing video:", await response.text())

    return {"message": "Video processing started", "filename": unique_filename}

@app.get("/status")
def get_status():
    return {"status": video_processing_status}

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
