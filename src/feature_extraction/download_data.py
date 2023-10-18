import os
from google.cloud import storage
import argparse

def download(bucket_name, target_dir):

    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=target_dir)

    for blob in blobs:
        blob_folder_structure = os.path.dirname(blob.name)
        if not os.path.exists(blob_folder_structure):
            os.makedirs(blob_folder_structure, exist_ok=True)
        if blob.name.endswith("progress.txt"):
            continue
        blob.download_to_filename(blob.name)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prefix", required=True, choices=["test_prefix", "oboe", "playing_bongo", "badminton"])
    args = parser.parse_args()
    p = args.prefix

    download('s2s_data', f'processed_data/{p}')
    download('s2s_data', f'filelists')
    download('s2s_data', f'features/{p}/progress.txt')
    

