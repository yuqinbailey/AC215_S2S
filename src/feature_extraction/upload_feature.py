from google.cloud import storage
import os
import glob

def upload_to_GCP(bucket_name, local_path, gcs_path):

   print("uploading")
   os.makedirs(local_path, exist_ok=True)
   
   # Upload to bucket
   storage_client = storage.Client()
   bucket = storage_client.bucket(bucket_name)

   for local_file in glob.glob(local_path + '/**'):
      if not os.path.isfile(local_file):
         print(os.path.basename(local_file))
         if "OF_10s_21.5fps" == os.path.basename(local_file):
            continue
         upload_to_GCP(bucket_name,local_file, gcs_path + "/" + os.path.basename(local_file))
      else:
         remote_path = os.path.join(gcs_path, local_file[1 + len(local_path):])
         blob = bucket.blob(remote_path)
         blob.upload_from_filename(local_file)

if __name__ == "__main__":
   upload_to_GCP("s2s_data_new",'features','features')