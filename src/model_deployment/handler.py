# handler.py
import os
import uuid
import base64
import torch
from io import BytesIO
from ts.torch_handler.base_handler import BaseHandler
from moviepy.editor import VideoFileClip, AudioFileClip

# Constants from your api_model.py
fps = 21.5
prefix = "playing_bongo"
t = 0  # trimming from the beginning
sr = 22050  # Sample rate for audio

# We use /workspace as a writable directory for TorchServe
PROCESSED_VIDEO_DIR = f"/workspace/processed_data/{prefix}/video_10s_{fps}fps"
PROCESSED_AUDIO_DIR = f"/workspace/processed_data/{prefix}/audio_10s_{sr}hz"
FEATURE_DIR = f"/workspace/features/{prefix}"
RESULTS_DIR = "/workspace/results"
os.makedirs(PROCESSED_VIDEO_DIR, exist_ok=True)
os.makedirs(PROCESSED_AUDIO_DIR, exist_ok=True)
os.makedirs(FEATURE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

class MyModelHandler(BaseHandler):

    def initialize(self, context):

        print("*"*50,"Initializing","*"*50)

        self.initialized = False
        # Model initialization here, if needed
        self.model = None  # Replace with actual model loading if applicable
        self.initialized = True
        self.unique_id = str(uuid.uuid4())


    def preprocess(self, data):

        print("*"*50,"Preprocessing","*"*50)

        try:
            # Decode base64 data
            
            base64_video = data[0]['body']['file']
            # base64_video = data[0]['body']['instances'][0]['data']['b64']
            if base64_video is None:
                raise ValueError("No data provided")
            video_buffer = BytesIO(base64.b64decode(base64_video))
        except (KeyError, IndexError, TypeError, base64.binascii.Error) as e:
            raise ValueError("Invalid input format or base64 decode error") from e
        
        temp_video_path = f'/workspace/{self.unique_id}.mp4'
        with open(temp_video_path, "wb") as f:
            f.write(video_buffer.getbuffer())

        self._preprocess()
        return []

    def _preprocess(self):
        test = self.unique_id

        input_video_path = f'/workspace/{test}.mp4'
    
        if not os.path.exists(input_video_path) or os.path.getsize(input_video_path) == 0:
            raise ValueError("Video file not found or is empty")
    
        # Adapting preprocessing logic from api_model.py
        input_video_path = f'/workspace/{test}.mp4'
        os.makedirs(PROCESSED_VIDEO_DIR, exist_ok=True)
        os.makedirs(PROCESSED_AUDIO_DIR, exist_ok=True)
        os.makedirs(FEATURE_DIR, exist_ok=True)

        # Preprocess the video
        clip = VideoFileClip(input_video_path)
        output_video_path = os.path.join(PROCESSED_VIDEO_DIR, f'{test}.mp4')
        output_audio_path = os.path.join(PROCESSED_AUDIO_DIR, f'{test}.wav')

        trimmed_clip = clip.subclip(t, min(t + 10, clip.duration))
        audio_clip = trimmed_clip.audio

        # Write the processed video and audio to files
        trimmed_clip.write_videofile(output_video_path, fps=fps, threads=4, logger=None, codec="libx264", audio_codec="aac", ffmpeg_params=['-b:a', '98k'])
        audio_clip.write_audiofile(output_audio_path, fps=sr, logger=None, ffmpeg_params=['-ac', '1', '-ab', '16k'])

        # Feature extraction commands
        self._extract_features()

    def _extract_features(self):
        test = self.unique_id

        print("*"*50,"Extracting features","*"*50)

        # Run feature extraction scripts as system commands
        os.system(f"python /workspace/src/extract_rgb_flow.py -i {PROCESSED_VIDEO_DIR} -o {os.path.join(FEATURE_DIR, f'OF_10s_{fps}fps')}")
        os.system(f"python /workspace/src/extract_mel_spectrogram.py -i {PROCESSED_AUDIO_DIR} -o {os.path.join(FEATURE_DIR, f'melspec_10s_{sr}hz')}")
        
        # Extract RGB and Flow features
        os.system(f"CUDA_VISIBLE_DEVICES=0 python /workspace/src/extract_feature.py -f {test} -j 0 -m RGB -i {os.path.join(FEATURE_DIR, f'OF_10s_{fps}fps')} -o {os.path.join(FEATURE_DIR, f'feature_rgb_bninception_dim1024_{fps}fps')}")
        os.system(f"CUDA_VISIBLE_DEVICES=0 python /workspace/src/extract_feature.py -f {test}  -j 0 -m Flow -i {os.path.join(FEATURE_DIR, f'OF_10s_{fps}fps')} -o {os.path.join(FEATURE_DIR, f'feature_flow_bninception_dim1024_{fps}fps')}")

    def inference(self, data):
        # Since the prediction is done within the make_prediction function, we call it directly

        print("*"*50,"Inferencing","*"*50)
        self._make_prediction()
        return []

    def _make_prediction(self):
        test = self.unique_id

        # Inference logic from api_model.py
        os.system(f"CUDA_VISIBLE_DEVICES=0 python /workspace/src/test.py --test_name {test}")
        
        # Combine video and audio back to a single file
        video_clip = VideoFileClip(os.path.join(PROCESSED_VIDEO_DIR, f'{test}.mp4'))
        audio_clip = AudioFileClip(os.path.join(RESULTS_DIR, f'{test}.wav'))
        video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(os.path.join(RESULTS_DIR, f'{test}.mp4'), codec='libx264', audio_codec='aac')

    def postprocess(self, inference_output):
        # Path to the processed video file
        video_file_path = f'/workspace/results/{self.unique_id}.mp4'
        
        # Encode the video file in base64
        with open(video_file_path, 'rb') as f:
            video_data = f.read()
        base64_encoded_video = base64.b64encode(video_data).decode('utf-8')
        
        # Return a list of dictionaries with the base64 encoded video string
        return [{"video": base64_encoded_video, "status": "success"}]



