import os
from csv import reader
from moviepy.editor import VideoFileClip

def cut_video():
    
    os.makedirs('processed_video', exist_ok=True)
    video_files = os.listdir('raw_video')

    file = open('vggsound.csv',"r")
    lines = list(reader(file))
    start_times = {x[0]:int(x[1]) for x in lines}

    for video_file in video_files:
        clip = VideoFileClip(os.path.join('raw_video',video_file))
        video_id = video_file.split('.')[0]
        trimmed_clip = clip.subclip(start_times[video_id],start_times[video_id]+10)
        trimmed_clip.write_videofile(os.path.join('processed_video',video_file))