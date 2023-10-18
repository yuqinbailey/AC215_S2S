import os
import io
import pandas as pd
from moviepy.editor import VideoFileClip
from google.cloud import storage
import concurrent.futures
import shutil
import argparse
import random

# make local directories
def makedirs(input_videos, output_videos):
    os.makedirs(input_videos, exist_ok=True)
    os.makedirs(output_videos, exist_ok=True)
    os.makedirs(output_audios, exist_ok=True)

def clean_up(input_videos, output_videos):
    shutil.rmtree(input_videos, ignore_errors=True)
    shutil.rmtree(output_videos, ignore_errors=True)
    shutil.rmtree(output_audios, ignore_errors=True)

def get_all_videos(client, bucket_name, input_videos):
    blobs = client.get_bucket(bucket_name).list_blobs(prefix=f'{input_videos}/')
    all_videos = set(blob.name.split('/')[-1].split('.')[0] for blob in blobs if blob.name.endswith('.mp4'))
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
    success = True
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
            #     '-r', f'{fps}', '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
            #     '-b:a', '98k', '-y', output_video_path
            # ]
            # os.system(cmd_video)

            # # Use ffmpeg to change audio sample rate
            # cmd_audio = [
            #     'ffmpeg', '-i', output_video_path, '-ar', str(sr), '-ac', '1', '-c:a', 'aac', '-strict', 'experimental',
            #     '-ab', '16k', '-y', output_audio_path
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

def preprocess(bucket_name, input_videos, output_videos, output_audios, progress_file,n,w,sr,fps):
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


def get_all_clips(client, output_videos, bucket_name):
    blobs = client.list_blobs(bucket_name, prefix= output_videos)
    clips = []
    for blob in blobs:
        clips.append(blob.name.split('/')[-1].split('.')[0])
    return clips

def update_train_test_split(output_videos, p, filelists, test_ratio):

    client = storage.Client()
    clips = get_all_clips(client, output_videos, bucket_name)
    random.shuffle(clips)
    
    if test_ratio < 0 or test_ratio > 1:
        raise Exception("Invalid test_ratio")

    total_num = len(clips)
    test_num = int(total_num * test_ratio)
    train_clips = clips[test_num:]
    test_clips = clips[:test_num]

    # Create string content for train and test filelists
    train_content = "\n".join(train_clips)
    test_content = "\n".join(test_clips)

    # Upload train and test filelists to GCP bucket as strings, overwriting existing files
    bucket = client.get_bucket(bucket_name)

    # Delete existing blobs if they exist
    train_blob = bucket.blob(os.path.join(filelists, f"{p}_train.txt"))
    if train_blob.exists():
        train_blob.delete()

    test_blob = bucket.blob(os.path.join(filelists, f"{p}_test.txt"))
    if test_blob.exists():
        test_blob.delete()

    # Upload the new content
    train_blob.upload_from_string(train_content, content_type="text/plain")
    test_blob.upload_from_string(test_content, content_type="text/plain")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-n", '--num_videos', default='100', type=int)
    parser.add_argument("-a", '--audio_sample_rate', default='22050', type=int)
    parser.add_argument("-v", '--video_fps', default='21.5', type=float)
    parser.add_argument("-w", '--num_workers', type=int, default=8)
    parser.add_argument("-p", "--prefix", required=True, choices=["test_prefix", "oboe", "bongo", "badminton"])
    parser.add_argument("-t", '--test_ratio', type=float, default=0.1)

    args = parser.parse_args()

    n = args.num_videos
    w = args.num_workers
    sr = args.audio_sample_rate
    fps = args.video_fps
    p = args.prefix
    t = args.test_ratio

    # Configurations
    gcp_project = "ac215-project"
    bucket_name = "s2s_data"

    raw_dir = "raw_data"
    processed_dir = "processed_data"

    input_videos = f"{raw_dir}/{p}"
    output_videos= f"{processed_dir}/{p}/video_10s_{fps}fps"
    output_audios= f"{processed_dir}/{p}/audio_10s_{sr}hz"
    
    progress_file = f"{processed_dir}/{p}/progress.txt"
    filelists_dir = f"filelists"

    preprocess(bucket_name, input_videos, output_videos, output_audios, progress_file, n, w, sr, fps)
    update_train_test_split(output_videos, p, filelists_dir, test_ratio=t)


