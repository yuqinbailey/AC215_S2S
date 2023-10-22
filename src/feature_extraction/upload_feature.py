from google.cloud import storage
import os
import glob

BUCKET = "s2s_data"

# only in this container, DO NOT PUSH TO GIT HUB

from google.oauth2 import service_account
import json
SERVICE_ACCOUNT = json.loads()
BUCKET = "s2s_data"

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

def upload_features(local_path, gcs_path):

   print("uploading")
   os.makedirs(local_path, exist_ok=True)
   
   # Upload to bucket
   # storage_client = storage.Client()
   storage_client = client = storage.Client(
   credentials=credentials,
   project=credentials.project_id,)
   bucket = storage_client.bucket(BUCKET)

   for local_file in glob.glob(local_path + '/**'):
      if not os.path.isfile(local_file):
         print(os.path.basename(local_file))
         if "OF_10s_21.5fps" == os.path.basename(local_file):
            continue
         upload_features(local_file, gcs_path + "/" + os.path.basename(local_file))
      else:
         remote_path = os.path.join(gcs_path, local_file[1 + len(local_path):])
         blob = bucket.blob(remote_path)
         blob.upload_from_filename(local_file)

if __name__ == "__main__":
   parser.add_argument("-p", "--prefix", required=True, choices=["test_prefix", "oboe", "playing_bongo", "badminton"])
   args = parser.parse_args()
   p = args.prefix
   upload_features('features','features')