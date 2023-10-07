from google.cloud import storage
import os

BUCKET = "s2s_data"

def download_data(num, target_local_dir):
    print("downloading")
    os.makedirs('data/processed_data', exist_ok=True)
    client = storage.Client()
    bucket = client.get_bucket(BUCKET)
    blobs = bucket.list_blobs(prefix= "processed_data/")
    counter = 0
    for blob in blobs:
        print(blob.name)
        if blob.name.endswith("mp4"):
            blob.download_to_filename(f'{target_local_dir}/{blob.name}')
            counter +=1
        if counter>=num:
          break

if __name__ == "__main__":
    download_data(5, 'data')