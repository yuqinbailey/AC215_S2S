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


def get_relevant_videos(target_topic, vggsound):
    # YONG: here we doing an exact for the target topic
    # semantics-based matching to be continued
    filtered_vggsound = vggsound[vggsound["topic"] == target_topic]
    return filtered_vggsound['video_id'].tolist()


def download_and_upload_video(target_topic, index, id):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    link = YOUTUBE_BASE_URL + id
    is_success = False
    base_path = raw_data + "/" + target_topic + "/"
    try:
        yt = YouTube(link)
        video_stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
        video_url = video_stream.url
        response = requests.get(video_url)
        video_bytes = response.content
        is_success = True

        if is_success:
            # push it to bucket
            blob = bucket.blob(os.path.join(base_path, str(id) + ".mp4"))
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

    target_topic = args.target_topic

    vggsound = pd.read_csv(vggsound_file, header=None)
    vggsound.columns = ['video_id', 'start_time', 'topic', "dataset"]

    relevant_ids = get_relevant_videos(target_topic, vggsound)
    target_topic = target_topic.replace(" ", "_")
    print(f"[INFO] The num of videos for topic {target_topic} is {len(relevant_ids)} ")
    
    # # Use ThreadPoolExecutor to download videos concurrently
    num_workers = args.num_workers
    print(f"The number of workers: {num_workers}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(download_and_upload_video, target_topic, index, relevant_ids[index]) : index \
        for index in range(len(relevant_ids))}

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result(timeout=150)
                index = futures[future]
            except Exception as e:
                print(f"[ERROR] Video {index} generated an exception: {e}")


if __name__ == "__main__":
    # Generate the inputs arguments parser
    parser = argparse.ArgumentParser(description="Download the YouTube videos")

    parser.add_argument('--num_workers', default=cpu_count(), type=int, 
                    help="The number of workers")
    
    # nargs="+",
    parser.add_argument('--target_topic', default="playing bongo", type=str, 
                    help="The targe topic")

    args = parser.parse_args()
    main(args)