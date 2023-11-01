import os
from google.cloud import storage
import argparse
import shutil

def get_progress(bucket_name, progress_file_path):

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(progress_file_path)

    if blob.exists():
        # Temporarily download the progress.txt file
        blob_folder_structure = os.path.dirname(blob.name)
        if not os.path.exists(blob_folder_structure):
            os.makedirs(blob_folder_structure, exist_ok=True)
        blob.download_to_filename(blob.name)
        with open(blob.name, 'r') as f:
            progress = [line.strip() for line in f]
        return progress
    else:
        print(f"The file {progress_file_path} does not exist in the {bucket_name} bucket.")
        return []


def download(bucket_name, target_prefix, num_clips, progress=None):

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    train_list_file = f'processed_data/filelists/{target_prefix}_train.txt'
    test_list_file = f'processed_data/filelists/{target_prefix}_test.txt'

    train_list_blob = bucket.blob(train_list_file)
    if  train_list_blob.exists():
        train_list = set(train_list_blob.download_as_text().splitlines())
    else:
        train_list = set()

    test_list_blob = bucket.blob(test_list_file)
    if  test_list_blob.exists():
        test_list = set(test_list_blob.download_as_text().splitlines())
    else:
        test_list = set()

    processed_data_dir =  f'processed_data/{target_prefix}'
    blobs = bucket.list_blobs(prefix=processed_data_dir)
    if os.path.exists(processed_data_dir):
        shutil.rmtree(processed_data_dir)
    os.makedirs(processed_data_dir)

    downloaded = set()

    for blob in blobs:
        blob_folder_structure = os.path.dirname(blob.name)
        if not os.path.exists(blob_folder_structure):
            os.makedirs(blob_folder_structure, exist_ok=True)
        basename = os.path.basename(blob.name).split(".")[0]
        if basename not in (progress or []) and basename != "progress" :
            if len(downloaded) < num_clips or basename in downloaded: 
                try:
                    blob.download_to_filename(blob.name)
                except Exception as e:
                    print(f"Error downloading {blob.name}: {e}")
                else:
                    downloaded.add(basename)
    
    if os.path.exists('features/filelists'):
        shutil.rmtree('features/filelists')
    os.makedirs('features/filelists')

    train_new = open(f'features/filelists/{p}_train_new.txt', 'w')
    train_original = open(f'features/filelists/{p}_train.txt', 'w')

    test_new = open(f'features/filelists/{p}_test_new.txt', 'w')
    test_original = open(f'features/filelists/{p}_test.txt', 'w')

    for file_name in train_list:
        if file_name in downloaded:
            train_new.write(file_name + '\n')
        elif file_name in progress:
            train_original.write(file_name + '\n')
    for file_name in test_list:
        if file_name in downloaded:
            test_new.write(file_name + '\n')
        elif file_name in progress:
            test_original.write(file_name + '\n')
    
    train_new.close()
    train_original.close()
    test_new.close()
    test_original.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prefix", required=True, choices=["test_prefix", "oboe", "playing_bongo", "badminton"])
    parser.add_argument("-n", '--num_clips', default='10', type=int)
    
    args = parser.parse_args()
    p = args.prefix
    n = args.num_clips

    progress = get_progress('s2s_data_new', f'features/{p}/progress.txt')
    downloaded = download('s2s_data_new', p , n, progress=progress)
    

