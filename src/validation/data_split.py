"""
Module that contains the command line app.
"""
import os
import shutil
import argparse
from random import shuffle
from google.cloud import storage

# Generate the inputs arguments parser
parser = argparse.ArgumentParser(description="Command description.")

GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
input_videos = "processed_data"
output_videos = "s2s_dataset"

def makedirs():
    os.makedirs(input_videos, exist_ok=True)
    os.makedirs(output_videos, exist_ok=True)

def download():
    print("download")

    # Clear
    shutil.rmtree(input_videos, ignore_errors=True, onerror=None)
    makedirs()

    client = storage.Client()
    bucket = client.get_bucket(GCS_BUCKET_NAME)

    blobs = bucket.list_blobs(prefix=input_videos + "/")
    for blob in blobs:
        print(blob.name)
        if not blob.name.endswith("/"):
            blob.download_to_filename(blob.name)

def train_val_test_split(source_folder, train_percent, val_percent):

    # Lists to hold filenames
    all_files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    # Randomly shuffle the list
    shuffle(all_files)  

    num_files = len(all_files)
    num_train = int(train_percent * num_files)
    num_val = int(val_percent * num_files)

    train_files = all_files[:num_train]
    val_files = all_files[num_train:num_train + num_val]
    test_files = all_files[num_train + num_val:]

    # Create train, val, test directories under s2s_dataset
    os.makedirs(os.path.join(output_videos, 'train'), exist_ok=True)
    os.makedirs(os.path.join(output_videos, 'val'), exist_ok=True)
    os.makedirs(os.path.join(output_videos, 'test'), exist_ok=True)

    # Copy files to respective directories
    def move_files(file_list, target_dir):
        for f in file_list:
            shutil.copy(os.path.join(source_folder, f), os.path.join(output_videos, target_dir, f))

    move_files(train_files, 'train')
    move_files(val_files, 'val')
    move_files(test_files, 'test')

    print("Files split into train, val, and test directories under s2s_dataset.")


def main(args=None):
    download()
    train_val_test_split(input_videos, args.train_percent, args.val_percent)



if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python data_split.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Data Spliting CLI...")

    parser.add_argument(
        "-t",
        "--train_percent",
        default=0.7,
        help="Percentage of data to be used for training. Should be a float value between 0 and 1. Default is 0.7."
    )

    parser.add_argument(
        "-v",
        "--val_percent",
        default=0.2,
        help="Percentage of data to be used for validation. Should be a float value between 0 and 1. Default is 0.2."
    )

    args = parser.parse_args()

    main(args)
