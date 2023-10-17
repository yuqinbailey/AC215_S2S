import os
import argparse
import random
from google.cloud import storage

def get_processed_clips(client, output_videos, bucket_name):
    blobs = client.list_blobs(bucket_name, prefix= output_videos)
    clips = []
    for blob in blobs:
        clips.append(blob.name.split('/')[-1].split('.')[0])
    return clips

def train_test_split(output_videos, filelists, test_ratio):

    client = storage.Client()
    clips = get_processed_clips(client, output_videos, bucket_name)
    random.shuffle(clips)
    
    if test_ratio < 0 or test_ratio > 1:
        raise Exception("Invalid test_ratio")

    total_num = len(clips)
    test_num = int(total_num * test_ratio)
    train_clips = clips[:-test_num]
    test_clips = clips[-test_num:]

    # Create string content for train and test filelists
    train_content = "\n".join(train_clips)
    test_content = "\n".join(test_clips)

    # Upload train and test filelists to GCP bucket as strings, overwriting existing files
    bucket = client.get_bucket(bucket_name)

    # Delete existing blobs if they exist
    train_blob = bucket.blob(os.path.join(filelists, "train.txt"))
    if train_blob.exists():
        train_blob.delete()

    test_blob = bucket.blob(os.path.join(filelists, "test.txt"))
    if test_blob.exists():
        test_blob.delete()

    # Upload the new content
    train_blob.upload_from_string(train_content, content_type="text/plain")
    test_blob.upload_from_string(test_content, content_type="text/plain")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", '--video_dir', default='processed_data/video_10s_21.5fps')
    parser.add_argument("-t", '--test_ratio', type=float, default=0.1)

    args = parser.parse_args()

    video_dir = args.video_dir
    t = args.test_ratio

    # Configurations
    filelists = 'processed_data/filelists'
    gcp_project = "ac215-project"
    bucket_name = "s2s_data"

    
    train_test_split(video_dir, filelists, test_ratio=t)
