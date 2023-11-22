import os
import json
import numpy as np
from google.cloud import aiplatform
import base64
import os
import requests
import zipfile
import tarfile
import argparse
from glob import glob
import numpy as np
import base64
import torch
from tqdm import tqdm
import sys
from io import BytesIO
import os
from moviepy.editor import VideoFileClip, AudioFileClip

fps = 21.5
prefix = "playing_bongo"
t = 0  # trimming from the beginning
sr = 22050  # Sample rate for audio

PROCESSED_VIDEO_DIR = f"./processed_data/{prefix}/video_10s_{fps}fps"
PROCESSED_AUDIO_DIR = f"./processed_data/{prefix}/audio_10s_{sr}hz"
FEATURE_DIR = f"./features/{prefix}"

def preprocess(test):
        input_video_path = test + ".mp4"

        # start to do the preprocess and feature extraction
        os.makedirs(PROCESSED_VIDEO_DIR, exist_ok=True)
        os.makedirs(PROCESSED_AUDIO_DIR, exist_ok=True)
        os.makedirs(FEATURE_DIR, exist_ok=True)

        print("-" * 50)
        print("CHECKPOINT 2")
        print("-" * 50)

        # preprocess
        clip = VideoFileClip(input_video_path)

        output_video_path = os.path.join(PROCESSED_VIDEO_DIR, f'{test}.mp4')
        output_audio_path = os.path.join(PROCESSED_AUDIO_DIR, f'{test}.wav')

        print("-" * 50)
        print("CHECKPOINT 3")
        print("-" * 50)

        trimmed_clip = clip.subclip(t, min(t + 10, clip.duration))
        audio_clip = trimmed_clip.audio

        trimmed_clip.write_videofile(output_video_path, fps=fps, threads=8, logger=None, codec="libx264", audio_codec="aac", ffmpeg_params=['-b:a', '98k'])
        audio_clip.write_audiofile(output_audio_path, fps=sr, logger=None, ffmpeg_params=['-ac', '1', '-ab', '16k'])

        print("-" * 50)
        print("CHECKPOINT 4")
        print("-" * 50)
        
        # feature extractions
        os.system(f"python ./api/extract_rgb_flow.py -i {PROCESSED_VIDEO_DIR} -o {os.path.join(FEATURE_DIR, f'OF_10s_{fps}fps')}")
        print("*" * 50)
        print("Finished extract_rgb_flow")
        print("*" * 50)
        
        os.system(f"python ./api/extract_mel_spectrogram.py -i {PROCESSED_AUDIO_DIR} -o {os.path.join(FEATURE_DIR, f'melspec_10s_{sr}hz')}")
        print("*" * 50)
        print("Finished extract_mel_spectrogram")
        print("*" * 50)

        # Extract RGB features
        os.system(f"CUDA_VISIBLE_DEVICES=0 python ./api/extract_feature.py  -f {test} -m RGB -i {os.path.join(FEATURE_DIR, f'OF_10s_{fps}fps')} -o {os.path.join(FEATURE_DIR, f'feature_rgb_bninception_dim1024_{fps}fps')}")
        print("*" * 50)
        print("Finished extract_feature RGB")
        print("*" * 50)

        # Extract Flow features
        os.system(f"CUDA_VISIBLE_DEVICES=0 python ./api/extract_feature.py  -f {test} -m Flow -i {os.path.join(FEATURE_DIR, f'OF_10s_{fps}fps')} -o {os.path.join(FEATURE_DIR, f'feature_flow_bninception_dim1024_{fps}fps')}")
        print("*" * 50)
        print("Finished extract_feature flow")
        print("*" * 50)


def make_prediction(test):
      
    preprocess(test)

    os.system(f"CUDA_VISIBLE_DEVICES=0 python ./api/test.py --test_name {test}")

    # Load the video clip
    video_clip = VideoFileClip(os.path.join(PROCESSED_VIDEO_DIR, f'{test}.mp4'))

    # Load the audio clip
    audio_clip = AudioFileClip(os.path.join('./results', f'{test}.wav'))

    # Set the audio of the video clip to your audio clip
    video_clip = video_clip.set_audio(audio_clip)

    # Write the result to a new file
    video_clip.write_videofile(os.path.join('./results', f'{test}.mp4'), codec='libx264', audio_codec='aac')
    

# def make_prediction_vertexai(image_path):
#     print("Predict using Vertex AI endpoint")

#     # Get the endpoint
#     # Endpoint format: endpoint_name="projects/{PROJECT_NUMBER}/locations/us-central1/endpoints/{ENDPOINT_ID}"
#     endpoint = aiplatform.Endpoint(
#         "projects/129349313346/locations/us-central1/endpoints/8600804363952193536"
#     )

#     with open(image_path, "rb") as f:
#         data = f.read()
#     b64str = base64.b64encode(data).decode("utf-8")
#     # The format of each instance should conform to the deployed model's prediction input schema.
#     instances = [{"bytes_inputs": {"b64": b64str}}]

#     result = endpoint.predict(instances=instances)

#     print("Result:", result)
#     prediction = result.predictions[0]
#     print(prediction, prediction.index(max(prediction)))

#     index2label = {0: "oyster", 1: "crimini", 2: "amanita"}

#     prediction_label = index2label[prediction.index(max(prediction))]

#     poisonous = False
#     if prediction_label == "amanita":
#         poisonous = True

#     return {
#         "prediction_label": prediction_label,
#         "prediction": prediction,
#         "accuracy": round(np.max(prediction) * 100, 2),
#         "poisonous": poisonous,
#     }