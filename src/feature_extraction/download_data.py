import os
from google.cloud import storage
import argparse
import shutil

# only in this container, DO NOT PUSH TO GIT HUB

from google.oauth2 import service_account
import json
SERVICE_ACCOUNT = json.loads(r"""{
  "type": "service_account",
  "project_id": "ac215project-398818",
  "private_key_id": "9a258746e23557c6e8e36af37ab4a8b4183a54f5",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCn2luUmPGZZJUc\nrwBlhKt0caxCUBdoo7ocGt444hjhmjQAqPNGxKTy9eTgmNZBj6XQPYeIjgQ3PnkC\nTkYr8PFiWTuSH83Yy2a3+3XFcSGSfU9f/lwF9h5Peyxq8AMvNJPyaIRn2X9kpiw4\nh3AC2vR+tJun+5emW9btutRp+dvJyhIgnLLoukJE/WrDojHJaCZtJanNqCUMLUDy\nXBiiWnv2VifgN5CTTlpsUPNVj69s39THCGKRWWNgZ4MO0N5FX9Txoh0h/LJCIcY3\n6GSop1grBVQ7LbCiFGIkNVEgFtY9dqlCHvdm05kataDx48C4b2/K7WEKH0K37Qj5\n+KPcTqUbAgMBAAECggEAFHtbo3VKPdp9K4PbO4gF1+6rA2h8gsM/yYApz60fNiA3\n6kCzdtY1/oOsyw87TcK2jAOGD06tCwSvhW2BuIjtG4Ah+cGxv5uKTDb99vrICvUJ\ng4ApQHz40+AG2oGxEciLqQ/B4F404lY4nSlBrMeFABUPzV6w8ZbRUi7zDn9zp1qz\nSrHyt2yzGCqfuyBfPjYgJfONzQCblxiA+bzgYNMZiMg6rw18bLrg9n8YIL6TDsh8\n26fDZZWdeKFHE3InzizU5SRO0Kh80rx1zcvGvY04bBkCVC9XA8i4lAmq0f28563S\nfOJGYN1vg/YSiWgrc9IsmqAVGfFNdbeWhGSkxQFuWQKBgQDdXA2RP6oXqckeGMb/\nXL7UJfOwa+AoTS4vHQB8pFlL6GHyEgtwut+Y/GBHrMXrQ7OezcYwBLpTTEzBy46Q\nZTTXYABcpzrqdovVRfke+5HQ8YG7yqSw2iw5ETwqHEQZhTkRbIUpxf4C2fDGGlth\njpzJBUrjeepjrEWOb6+zic8nfwKBgQDCHsLhuHKWM/FNODfLvke8v2C4OD+hEryc\nRxG40AUlTWCWgS2U6At21lg9zJ5+CwgtQwa/3wUVUhZ5iF2SBMTvGa0mR141LFEh\nTpdBBhxY/Ti83PA7QVY89hcvKCvEEbDc7Pompi+wRByFEQDu9irc6SVldRyHffex\neS9ztfPwZQKBgDkBFKlb+MSBP76VaOGoE6h0YY4EKcSXI5aUZGS0uh43KMn65aFR\nLnWqQG0UzB8q3x29JhWFkioTUwzxC7SZq4LvQQibNCve/WGd1GqrJEDngJ5IsCKu\n/IZxrsm1X8Ams6yOArjgOOqpDz0k2nWEEVIfH8r2wWqLmZn1nwygJ42nAoGAcTab\nliWKvstAejbFY9Bv6kb7U7WKdpiE4+gXD+BSf/Tm1iA0w1mqBf7wq+pArWYluLAU\nqaaaQlsDvJGpcNXTPVeOQnrxGLXmAzTgxg2YTtYwVwXMHeL3NsqXrusQy2M98TtM\nkWnu+jBfKcRG9Rcg3IIlS0zH/MWcxibVY/jEcnkCgYA3UHlSJngK5O/g7c779PRd\n9elwlt+Es7Iw0mu9WTS3S0qUAwJZAa5k31iDf8fFaLZ6LtuXYPVlF/H5I9V5NLZG\nGNf8zgpUUWkUCK7MiNLyKI1/Iz3yFI51RDq2SNR5TSNFzY3IpnSHXHs2pGLC5Lrq\nacWHw5DXuOBPQ3Yzpwq5gg==\n-----END PRIVATE KEY-----\n",
  "client_email": "data-service-account@ac215project-398818.iam.gserviceaccount.com",
  "client_id": "108806359890677372500",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/data-service-account%40ac215project-398818.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}""")
BUCKET = "s2s_data"

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

def get_progress(bucket_name, progress_file_path):

    #client = storage.Client()

    client = storage.Client(
    credentials=credentials,
    project=credentials.project_id,)

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

    # client = storage.Client()
    client = storage.Client(
    credentials=credentials,
    project=credentials.project_id,)
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

    progress = get_progress('s2s_data', f'features/{p}/progress.txt')
    downloaded = download('s2s_data', p , n, progress=progress)
    

