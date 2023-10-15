import os
import io
import pandas as pd
from moviepy.editor import VideoFileClip
from google.cloud import storage
import concurrent.futures
import shutil
import argparse

# make local directories
def makedirs(input_videos, output_videos):
    os.makedirs(input_videos, exist_ok=True)
    os.makedirs(output_videos, exist_ok=True)
    os.makedirs(output_audios, exist_ok=True)

def clean_up(input_videos, output_videos):
    shutil.rmtree(input_videos, ignore_errors=True)
    shutil.rmtree(output_videos, ignore_errors=True)

def get_all_videos(client, bucket_name, input_videos):
    blobs = client.get_bucket(bucket_name).list_blobs(prefix=f'{input_videos}/')
    all_videos = set(blob.name.split('/')[-1].split('.')[0] for blob in blobs)
    return all_videos

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
    progress_blob = bucket.blob(progress_file)
    if progress_blob.exists():
        progress = set(progress_blob.download_as_text().splitlines())
    else:
        progress = set()
    return progress

def handle_video(bucket_name, video_id, input_videos, output_videos, output_audios, trim_info, sr, fps):
    client = storage.Client() 
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
            output_video_path = os.path.join(output_videos, f'{clip_id}.mp4')
            output_audio_path = os.path.join(output_audios, f'{clip_id}.wav')

            trimmed_clip = clip.subclip(t, min(t + 10, clip.duration))

            trimmed_clip.write_videofile(output_video_path, fps = fps, threads = 8, logger = None, codec = "libx264", audio_codec="aac",ffmpeg_params=['-b:a','98k'])
            trimmed_clip.audio.write_audiofile(output_audio_path, fps = sr, logger = None, codec="aac", ffmpeg_params = ['-ac', '1','-ab', '16k'])

            # # Use ffmpeg to trim video and change video FPS
            # cmd_video = [
            #     'ffmpeg', '-ss', str(t), '-i', input_video_path, '-t', '10', '-vf',
            #     f'fps={fps}', '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
            #     '-b:a', '98k', '-y', output_video_path
            # ]
            # os.system(cmd_video)

            # # Use ffmpeg to change audio sample rate
            # cmd_audio = [
            #     'ffmpeg', '-i', output_video_path, '-ar', str(sr), '-ac', '1', '-c:a', 'aac', '-strict', 'experimental',
            #     '-b:a', '98k', '-y', output_audio_path
            # ]
            # os.system(cmd_audio)

            # Upload video and audio to storage
            blob_video = bucket.blob(f'{output_videos}/{clip_id}.mp4')
            blob_video.upload_from_filename(output_video_path)

            blob_audio = bucket.blob(f'{output_audios}/{clip_id}.wav')
            blob_audio.upload_from_filename(output_audio_path)

        except Exception as e:
            success = False
            print(f"Failed to process video/audio clip {clip_id}.mp4: {e}")

    if success:
        processed_video_ids.append(video_id)
    return processed_video_ids


def update_progress(client, bucket_name, progress_file, processed_videos):
    bucket = client.get_bucket(bucket_name)
    progress_blob = bucket.blob(progress_file)
    new_progress = '\n'.join(processed_videos)
    progress_blob.upload_from_string(f'{new_progress}\n', content_type='text/plain', client=client)

def download_cut_upload(bucket_name, input_videos, output_videos, output_audios, progress_file,n,w,sr,fps):
    clean_up(input_videos, output_videos)
    client = storage.Client()
    trim_info = get_trim_info(client, bucket_name)  # Get trim_info using the new function
    makedirs(input_videos, output_videos)
    
    processed_videos = get_processed_videos(client, bucket_name, progress_file)
    all_videos = get_all_videos(client, bucket_name, input_videos)
    remaining = all_videos - processed_videos
    remaining = list(remaining)[:min(len(remaining),n)]
    
    processed = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=w) as executor:
        futures = [executor.submit(
            handle_video, bucket_name, video_id, input_videos, output_videos, output_audios, trim_info, sr, fps
        ) for video_id in remaining]
        for future in concurrent.futures.as_completed(futures):
            processed.extend(future.result())
    
    # Update progress after all videos have been processed
    update_progress(client, bucket_name, progress_file, processed)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-n", '--num_videos', default='100', type=int)
    parser.add_argument("-a", '--audio_sample_rate', default='22050', type=int)
    parser.add_argument("-v", '--video_fps', default='21.5', type=float)
    parser.add_argument("-w", '--num_workers', type=int, default=8)

    args = parser.parse_args()

    n = args.num_videos
    w = args.num_workers
    sr = args.audio_sample_rate
    fps = args.video_fps

    # Configurations
    gcp_project = "ac215-project"
    bucket_name = "s2s_data"
    input_videos = "raw_data"
    output_videos= f"processed_data/video_10s_{fps}fps"
    output_audios= f"processed_data/audio_10s_{sr}hz"
    progress_file = 'processed_data/progress.txt'

    download_cut_upload(bucket_name, input_videos, output_videos, output_audios, progress_file, n, w, sr, fps)
