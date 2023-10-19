import os
from google.cloud import storage
import argparse

def get_exclusion_list(bucket_name, progress_file_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(progress_file_path)

    if blob.exists():
        # Temporarily download the progress.txt file
        tmp_progress = 'tmp_progress.txt'
        blob.download_to_filename(tmp_progress)

        # Read the exclusion list from the file
        with open(tmp_progress, 'r') as f:
            excluded_files = [line.strip() for line in f]

        os.remove(tmp_progress)
        return excluded_files
    else:
        print(f"The file {progress_file_path} does not exist in the {bucket_name} bucket.")
        return []

def download(bucket_name, target_dir, exclusion_list=None):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=target_dir)

    for blob in blobs:
        blob_folder_structure = os.path.dirname(blob.name)
        if not os.path.exists(blob_folder_structure):
            os.makedirs(blob_folder_structure, exist_ok=True)
        # Only download if basename is not in the exclusion list
        if os.path.basename(blob.name) not in (exclusion_list or []):
            try:
                blob.download_to_filename(blob.name)
            except Exception as e:
                print(f"Error downloading {blob.name}: {e}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prefix", required=True, choices=["test_prefix", "oboe", "playing_bongo", "badminton"])
    args = parser.parse_args()
    p = args.prefix

    exclusion_list = get_exclusion_list('s2s_data', f'features/{p}/progress.txt')

    # Download audios and videos, excluding those in the exclusion list
    download('s2s_data', f'processed_data/{p}', exclusion_list=exclusion_list)
    download('s2s_data', f'filelists')
