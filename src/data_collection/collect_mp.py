import concurrent.futures
import pandas as pd
from pytube import YouTube
from google.cloud import storage
import requests
import os
import argparse
import io
from multiprocessing import cpu_count

YOUTUBE_BASE_URL = "https://www.youtube.com/watch?v="
gcp_project = "ac215-project"
bucket_name = "s2s_data"
raw_data = "raw_data"
vggsound_file = 'vggsound.csv'
progress_file = 'progress.txt'


def download_and_upload_video(index, id, progress_data):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    link = YOUTUBE_BASE_URL + id
    is_success = False
    try:
        yt = YouTube(link)
        video_stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
        video_url = video_stream.url
        response = requests.get(video_url)
        video_bytes = response.content

        is_success = True
        progress_data["last_id"] = id

        if is_success:
            # push it to bucket
            blob = bucket.blob(os.path.join(raw_data, str(id) + ".mp4"))
            with blob.open('wb') as f:
                f.write(video_bytes)
            print(f"[SUCCESS] Video ID {id} with counter {index}.")

    except Exception as e:
        print(f"\t [WARNING] Failed Video ID {id} with counter {index}: {e}")


def main(args):

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    blob = bucket.blob(vggsound_file)
    blob.download_to_filename(blob.name)

    blob = bucket.blob(raw_data + "/"+ progress_file)
    blob.download_to_filename(progress_file)

    vggsound = pd.read_csv(vggsound_file, header=None)
    vggsound.columns = ['video_id', 'start_time', 'topic', "dataset"]

    # get the index of the files that we have NOT downloaded yet
    with open(progress_file, 'r') as file:
        progress_id = int(file.readlines()[0].split()[0])

    print(f"Resuming from index {progress_id}.")

    video_ids = vggsound['video_id'].tolist()
    start_index = progress_id
    end_index = min(len(video_ids), start_index + args.nums_to_download)

    progress_data = {'index': progress_id, 'last_id': None}

    # Use ThreadPoolExecutor to download videos concurrently
    num_workers = args.num_workers
    print(f"The number of workers: {num_workers}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(download_and_upload_video, index, video_ids[index], progress_data) : index \
        for index in range(start_index, end_index)}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result(timeout=150)
                progress_data['index'] += 1
                index = futures[future]
            except Exception as e:
                print(f"[ERROR] Video {index} generated an exception: {e}")

    print(f"Updated progress to {progress_data['index']}.")

    # sync the whole progress id to bucket
    blob = bucket.blob(os.path.join(raw_data, progress_file))
    with blob.open('w') as f:
        f.write(str(progress_data['index']))
    print(f"Finished syncing with progress ID {progress_data['index']}.")

if __name__ == "__main__":
    # Generate the inputs arguments parser
    parser = argparse.ArgumentParser(description="Download the YouTube videos")

    parser.add_argument('--nums_to_download', default=30, type=int,
                    help="The number of videos to download from YouTube")

    parser.add_argument('--num_workers', default=cpu_count(), type=int,
                    help="The number of workers")
    args = parser.parse_args()
    main(args)