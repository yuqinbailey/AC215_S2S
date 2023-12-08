from fastapi import FastAPI, File, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from api import VideoProcessor
import uuid
from fastapi.responses import FileResponse

app = FastAPI(title="API Server", description="API Server", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

processors = {}

@app.post("/predict")
async def predict(background_tasks: BackgroundTasks, file: bytes = File(...)):
    video_id = str(uuid.uuid4())
    video_path = f"./{video_id}.mp4"

    with open(video_path, "wb") as output:
        output.write(file)

    processor = VideoProcessor(video_id)
    processors[video_id] = processor

    background_tasks.add_task(processor.make_prediction)

    return {"message": "Video processing started", "video_id": video_id}

@app.get("/status/{video_id}")
def get_status(video_id: str):
    if video_id in processors:
        return {"status": processors[video_id].get_status()}
    return {"status": "Video ID not found"}

@app.get("/get_video/{video_id}")
def get_video(video_id: str):
    video_path = f"./results/{video_id}.mp4"
    if os.path.exists(video_path):
        headers = {'Content-Disposition': f'attachment; filename="{video_id}.mp4"', 'Content-Type': 'video/mp4'}
        return FileResponse(video_path, headers=headers)
    else:
        return {"message": "File does not exist"}, 404
