import os
import io
import pandas as pd
from moviepy.editor import VideoFileClip
from google.cloud import storage
import concurrent.futures
import shutil

# Configurations
gcp_project = "ac215-project"
bucket_name = "s2s_data"
input_videos = "raw_data"
output_videos = "processed_data"
progress_file = 'progress.txt'

# def check_processed(bucket_name, output_videos, video_id, trim_info):
#     client = storage.Client()
#     bucket = client.get_bucket(bucket_name)
#     for t in trim_info.get(video_id, []):
#         clip_id = f'c_{video_id}_{t}.mp4'
#         blob = bucket.blob(f'{output_videos}/{clip_id}')
#         if not blob.exists():
#             return False  # if any of the trimmed clips don't exist, it means this video hasn't been fully processed
#     return True

def makedirs(input_videos, output_videos):
    os.makedirs(input_videos, exist_ok=True)
    os.makedirs(output_videos, exist_ok=True)

def get_trim_info(client, bucket_name):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob('vggsound.csv')
    data = pd.read_csv(io.BytesIO(blob.download_as_bytes()), header=None)
    data.columns = ['video_id', 'start_time', 'topic', "dataset"]
    start_times = {}
    for i in range(len(data)):
        video_id = data.loc[i,'video_id']
        if video_id not in start_times.keys():
            start_times[video_id] = [int(data.loc[i,'start_time'])]
        else:
            start_times[video_id].append(int(data.loc[i,'start_time']))
    return start_times

def get_processed_videos(client, bucket_name, progress_file):
    bucket = client.get_bucket(bucket_name)
    progress_blob = bucket.blob(f'{output_videos}/{progress_file}')
    if progress_blob.exists():
        progress = set(progress_blob.download_as_text().splitlines())
    else:
        progress = set()
    return progress

def clean_up(input_videos, output_videos):
    shutil.rmtree(input_videos, ignore_errors=True)
    shutil.rmtree(output_videos, ignore_errors=True)

def get_all_videos(client, bucket_name, input_videos):
    blobs = client.get_bucket(bucket_name).list_blobs(prefix=f'{input_videos}/')
    all_videos = set(blob.name.split('/')[-1].split('.')[0] for blob in blobs)
    return all_videos

def handle_video(bucket_name, video_id, input_videos, output_videos, trim_info):
    # if check_processed(bucket_name, output_videos, video_id, trim_info):
    #     return []
            
    client = storage.Client()  # Moved client instantiation here
    video_file = video_id + '.mp4'
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(f'{input_videos}/{video_file}')
    try:
        blob.download_to_filename(os.path.join(input_videos, video_file))
        clip = VideoFileClip(os.path.join(input_videos, video_file))
    except Exception as e:
        print(f"Failed to download or read video {video_file}: {e}")
        return []

    processed_video_ids = []
    for t in trim_info.get(video_id, []):
        clip_id = f'c_{video_id}_{t}'
        try:
            trimmed_clip = clip.subclip(t, min(t + 10, clip.duration))
            trimmed_clip.write_videofile(os.path.join(output_videos, f'{clip_id}.mp4'), audio_codec="aac")
            destination_blob_name = f'{output_videos}/{clip_id}.mp4'
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(os.path.join(output_videos, f'{clip_id}.mp4'))
        except Exception as e:
            print(f"Failed to process video clip {clip_id}.mp4: {e}")
        else:
            processed_video_ids.append(video_id)
    clip.close()
    return processed_video_ids

def update_progress(client, bucket_name, progress_file, processed_videos):
    bucket = client.get_bucket(bucket_name)
    progress_blob = bucket.blob(f'{output_videos}/{progress_file}')
    new_progress = '\n'.join(processed_videos)
    progress_blob.upload_from_string(f'{new_progress}\n', content_type='text/plain', client=client)

def download_cut_upload(bucket_name, input_videos, output_videos, progress_file):
    clean_up(input_videos, output_videos)
    client = storage.Client()
    trim_info = get_trim_info(client, bucket_name)  # Get trim_info using the new function
    makedirs(input_videos, output_videos)
    
    processed_videos = get_processed_videos(client, bucket_name, progress_file)
    all_videos = get_all_videos(client, bucket_name, input_videos)
    remaining = all_videos - processed_videos
    
    processed = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(
            handle_video, bucket_name, video_id, input_videos, output_videos, trim_info
        ) for video_id in remaining]
        for future in concurrent.futures.as_completed(futures):
            processed.extend(future.result())
    
    # Update progress after all videos have been processed
    update_progress(client, bucket_name, progress_file, processed)

if __name__ == "__main__":
    download_cut_upload(bucket_name, input_videos, output_videos, progress_file)
