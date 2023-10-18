from google.cloud import storage
import os
import glob

BUCKET = "s2s_data"   

def upload_features(local_path, gcs_path):

   print("uploading")
   os.makedirs(local_path, exist_ok=True)
   
   # Upload to bucket
   storage_client = storage.Client()
   bucket = storage_client.bucket(BUCKET)

   for local_file in glob.glob(local_path + '/**'):
      if not os.path.isfile(local_file):
         print(os.path.basename(local_file))
         upload_features(local_file, gcs_path + "/" + os.path.basename(local_file))
      else:
         remote_path = os.path.join(gcs_path, local_file[1 + len(local_path):])
         blob = bucket.blob(remote_path)
         blob.upload_from_filename(local_file)

if __name__ == "__main__":
   upload_features('features','features')