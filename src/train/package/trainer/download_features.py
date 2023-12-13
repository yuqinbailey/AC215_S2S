import os
from google.cloud import storage


def download_features_from_gcs(bucket_name, prefix, destination_dir):

    print("Downloading extracted fearures from bucket")
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir, exist_ok=True)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)

    for blob in blobs:
        

        blob_folder_structure = os.path.dirname(blob.name)
        local_folder = os.path.join(destination_dir, blob_folder_structure)
    

        if not os.path.exists(local_folder):
            os.makedirs(local_folder, exist_ok=True)

        # Define the local file path
        local_file_path = os.path.join(destination_dir, blob.name)
        
        # Download the blob to the local file
        blob.download_to_filename(local_file_path)
        print(f"Downloaded {blob.name} to {local_file_path}")

def download_filelists_from_gcs(bucket_name, prefix, destination_dir):

    print("Downloading filelists from bucket")
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir, exist_ok=True)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)

    for blob in blobs:
        destination_file_name = os.path.join(destination_dir, blob.name.split("/")[-1])
        blob.download_to_filename(destination_file_name)
        print(f"Downloaded {blob.name} to {destination_file_name}")


if __name__ == "__main__":
    download_features_from_gcs('s2s_data', 'features/processed_data/', 'data')
    download_filelists_from_gcs('s2s_data', 'filelists/', 'filelists')

