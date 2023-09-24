import os
import io
import argparse
import shutil
from google.cloud import storage
from csv import reader
from moviepy.editor import VideoFileClip

# Generate the inputs arguments parser
parser = argparse.ArgumentParser(description="Command description.")

gcp_project = "ac215-project"
bucket_name = "s2s_data"
input_videos = "input_videos"
output_videos = "output_videos"


def makedirs():
    os.makedirs(input_videos, exist_ok=True)
    os.makedirs(output_videos, exist_ok=True)


def download():
    print("download")

    # Clear
    shutil.rmtree(input_videos, ignore_errors=True, onerror=None)
    makedirs()

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=input_videos + "/")
    for blob in blobs:
        print(blob.name)
        if not blob.name.endswith("/"):
            blob.download_to_filename(blob.name)


def cut_video():
    print("cut")
    makedirs()


    video_files = os.listdir(input_videos)

    file = open('vggsound.csv',"r")
    lines = list(reader(file))
    start_times = {x[0]:int(x[1]) for x in lines}

    for video_file in video_files:
        clip = VideoFileClip(os.path.join(input_videos,video_file))
        video_id = video_file.split('.')[0]
        trimmed_clip = clip.subclip(start_times[video_id],start_times[video_id]+10)
        trimmed_clip.write_videofile(os.path.join(output_videos,video_file))


def upload():
    print("upload")
    makedirs()

    # Upload to bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Get the list of video file
    text_files = os.listdir(output_videos)

    for text_file in text_files:
        file_path = os.path.join(output_videos, text_file)

        destination_blob_name = file_path
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(file_path)


def main(args=None):
    print("Args:", args)

    if args.download:
        download()
    if args.cut_video:
        cut_video()
    if args.upload:
        upload()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Transcribe audio file to text")

    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="Download video files from GCS bucket",
    )

    parser.add_argument(
        "-c",
        "--cut",
        action="store_true",
        help="Cut video files from GCS bucket",
    )

    parser.add_argument(
        "-u",
        "--upload",
        action="store_true",
        help="Upload video files to GCS bucket",
    )

    args = parser.parse_args()

    main(args)