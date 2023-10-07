from google.cloud import storagefrom 
#from google.oauth2 import service_account
import os
import glob
import json

BUCKET = "s2s_data"   

#SERVICE_ACCOUNT = json.loads(r"""{
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


def upload_features(local_path,gcs_path):

   print("uploading")
   os.makedirs(local_path, exist_ok=True)
   
   # Upload to bucket
   storage_client = storage.Client()
   bucket = storage_client.bucket(BUCKET)

   for local_file in glob.glob(local_path + '/**'):
      if not os.path.isfile(local_file):
         upload_features(local_file, gcs_path + "/" + os.path.basename(local_file))
      else:
         remote_path = os.path.join(gcs_path, local_file[1 + len(local_path):])
         blob = bucket.blob(remote_path)
         blob.upload_from_filename(local_file)
   

if __name__ == "__main__":
   upload_features('filelists','filelists2')
   upload_features('data/features','features2')