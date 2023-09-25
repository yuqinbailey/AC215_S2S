import pandas as pd
from pytube import YouTube
import time
import os
import io
import argparse
import shutil
from google.cloud import storage
import requests

# Generate the inputs arguments parser
parser = argparse.ArgumentParser(description="Command description.")

# TODO: some the variables are not used
# noqa
YOUTUBE_BASE_URL = "https://www.youtube.com/watch?v="
gcp_project = "ac215-project"
bucket_name = "s2s_data"
raw_data = "raw_data"
output_videos = "processed_data"
vggsound_file = 'vggsound.csv'
progress_file = 'progress.txt'


def makedirs():
    os.makedirs(raw_data, exist_ok=True)
    os.makedirs(output_videos, exist_ok=True)


def download_from_youtube(args):
    print("Download the videos from YouTube")

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    blob = bucket.blob(vggsound_file)
    blob.download_to_filename(blob.name)

    blob = bucket.blob(raw_data + "/"+ progress_file)
    blob.download_to_filename(progress_file)

    vggsound = pd.read_csv(vggsound_file, header=None)
    vggsound.columns = ['video_id', 'start_time', 'topic', "dataset"]
    ids = vggsound["video_id"].values.tolist()

    # get the index of the files that we have NOT downloaded yet
    with open(progress_file, 'r') as file:
        progress_id = int(file.readlines()[0].split()[0])

    start_index = progress_id
    end_index = min(len(ids), start_index + args.nums_to_download)

    for i in range(start_index, end_index):
        id = ids[i]
        link = YOUTUBE_BASE_URL + id
        yt = YouTube(link)
        is_success = False
        try:
            video_stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
            video_url = video_stream.url
            response = requests.get(video_url)
            video_bytes = response.content
            print(f"Finished downloading the video with id {id}.")
            is_success = True
        except:
            print(f"[WARNING] Invalid Video. Give up the video with id {id}")

        if is_success:
            # push it to bucket
            blob = bucket.blob(os.path.join(raw_data, str(id) + ".mp4"))
            with blob.open('wb') as f:
                f.write(video_bytes)
            print(f"\t Pushed {id} with counter {i}.")

        progress_id += 1

        # save the progress
        with open(progress_file, 'w') as file:
            file.write(str(progress_id))

    # sync the whole progress id to bucket
    blob = bucket.blob(os.path.join(raw_data, progress_file))
    with blob.open('w') as f:
        f.write(str(progress_id))


def main(args=None):
    print("Args:", args)
    download_from_youtube(args)


if __name__ == "__main__":
    # Generate the inputs arguments parser
    parser = argparse.ArgumentParser(description="Transcribe audio file to text")

    parser.add_argument('--nums_to_download', default=5, type=int,
                    help="The number of videos to download from YouTube")

    args = parser.parse_args()
    main(args)
