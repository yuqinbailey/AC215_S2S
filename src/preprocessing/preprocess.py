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
input_videos = "raw_data"
output_videos = "processed_data"


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

    blob = bucket.blob('vggsound.csv')
    blob.download_to_filename(blob.name)

def cut_video():
    print("cut")
    makedirs()

    file = open('vggsound.csv',"r")
    lines = list(reader(file))
    start_times = {}
    for line in lines:
        video_id = line[0]
        if video_id not in start_times.keys():
            start_times[video_id] = [int(line[1])]
        else:
            start_times[video_id].append(int(line[1]))

    video_files = os.listdir(input_videos)
    for video_file in video_files:
        if video_file.endswith('mp4'):
            try:
                clip = VideoFileClip(os.path.join(input_videos,video_file))
            except:
                print("!!!! Exception when reading video input: ", video_file)
            else:
                video_id = video_file.split('.')[0]
                for j, t in enumerate(start_times[video_id]):
                    trimmed_clip = clip.subclip(t,min(t+10,clip.duration))
                    trimmed_clip.write_videofile(os.path.join(output_videos,f'c_{video_id}_{j+1}.mp4'), audio_codec="aac")
            finally:
                clip.close()




def upload():
    print("upload")
    makedirs()

    # Upload to bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Get the list of video file
    video_files = os.listdir(output_videos)

    for video_file in video_files:
        file_path = os.path.join(output_videos, video_file)

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
        "--cut_video",
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
