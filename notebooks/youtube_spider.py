import pandas as pd
from pytube import YouTube
import time
import os

YOUTUBE_BASE_URL = "https://www.youtube.com/watch?v="

'''
###############################
Users should change the file path
###############################
'''
vggsound_file_path = "/Users/leocheung/Desktop/vggsound.csv"
SAVED_FOLDER_PATH = "/Users/leocheung/Desktop/raw_data"
FILES_TO_DOWNLOAD = 10

PROGRESS_FILE_NAME = "progress.txt"
PROGRESS_FILE_PATH = os.path.join(SAVED_FOLDER_PATH, PROGRESS_FILE_NAME)

downloaded_pointer = 0
vggsound = pd.read_csv(vggsound_file_path, header=None)
vggsound.columns = ['video_id', 'start_time', 'topic', "dataset"]

ids = vggsound["video_id"].values.tolist()


# sanity check for the progress file existence
if not os.path.exists(PROGRESS_FILE_PATH):
    with open(PROGRESS_FILE_PATH, 'w') as file:
        file.write("0")

# get the index of the files that we have NOT downloaded yet
with open(PROGRESS_FILE_PATH, 'r') as file:
    progress_id = int(file.readlines()[0].split()[0])


start_index = progress_id
end_index = min(len(ids), start_index + FILES_TO_DOWNLOAD)

for i in range(start_index, end_index):
    id = ids[i]
    link = YOUTUBE_BASE_URL + id
    yt = YouTube(link)
    try:
        yt.streams.filter(progressive=True, file_extension="mp4").\
            first().\
            download(output_path=SAVED_FOLDER_PATH, filename=id + ".mp4")
        print(f"Finished downloading the video with id {id}")
    except:
        print(f"[WARNING] Invalid Video. Give up the video with id {id}")

    progress_id += 1

    # save the progress
    with open(PROGRESS_FILE_PATH, 'w') as file:
        file.write(str(progress_id))

print('Finished downloaded specified video')


