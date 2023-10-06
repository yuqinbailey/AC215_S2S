import cv2
from glob import glob
import os
import os.path as P
import argparse
from tqdm import tqdm
import torch
import torchvision.transforms as transforms
from flownet2.models import FlowNet2
from PIL import Image

def cal_for_frames(video_path, output_dir, width, height, model):
    save_dir = P.join(output_dir, P.basename(video_path).split('.')[0])
    os.makedirs(save_dir, exist_ok=True)
    video = cv2.VideoCapture(video_path)
    video.read()
    _, prev = video.read()
    num = 1
    prev = cv2.resize(prev, (width, height))
    cv2.imwrite(P.join(save_dir, f"img_{num:05d}.jpg"), prev)
    prev_tensor = transforms.ToTensor()(Image.fromarray(prev)).unsqueeze(0).cuda()
    while video.isOpened():
        ret, curr = video.read()
        if not ret:
            break
        curr = cv2.resize(curr, (width, height))
        cv2.imwrite(P.join(save_dir, f"img_{num:05d}.jpg"), curr)
        curr_tensor = transforms.ToTensor()(Image.fromarray(curr)).unsqueeze(0).cuda()

        # Compute Optical Flow using FlowNet2
        flow = model(prev_tensor, curr_tensor).squeeze().cpu().numpy().transpose([1,2,0])

        # Save optical flow
        cv2.imwrite(P.join(save_dir, f"flow_x_{num:05d}.jpg"), flow[:, :, 0])
        cv2.imwrite(P.join(save_dir, f"flow_y_{num:05d}.jpg"), flow[:, :, 1])
        prev_tensor = curr_tensor
        num += 1
    if num < 215:
        print(video_path)

if __name__ == '__main__':
    paser = argparse.ArgumentParser()
    paser.add_argument("-i", "--input_dir", default="data/features/dog/videos_10s_21.5fps")
    paser.add_argument("-o", "--output_dir", default="data/features/dog/OF_10s_21.5fps")
    paser.add_argument("-w", "--width", type=int, default=340)
    paser.add_argument("-g", "--height", type=int, default=256)
    args = paser.parse_args()
    
    input_dir = args.input_dir
    output_dir = args.output_dir
    width = args.width
    height = args.height

    video_paths = glob(P.join(input_dir, "*.mp4"))
    video_paths.sort()

    for video_path in tqdm(video_paths, desc="Processing videos"):
        cal_for_frames(video_path, output_dir, width, height)