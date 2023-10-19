#!/bin/bash

# Default PREFIX value
PREFIX="test_prefix"

# Parse command-line arguments
while getopts "p:" opt; do
  case $opt in
    p)
      PREFIX="$OPTARG"
      ;;
    \?)
      echo "Usage: $0 [-p PREFIX]" >&2
      exit 1
      ;;
  esac
done

# Define input and output directories
INPUT_VIDEO_DIR="processed_data/$PREFIX/video_10s_21.5fps"
OUTPUT_VIDEO_DIR="features/$PREFIX/OF_10s_21.5fps"
INPUT_AUDIO_DIR="processed_data/$PREFIX/audio_10s_22050hz"
OUTPUT_AUDIO_DIR="features/$PREFIX/melspec_10s_22050hz"
PROGRESS_FILE="features/$PREFIX/progress.txt"

# Check if progress.txt exists, if not, create it
[ ! -f "$PROGRESS_FILE" ] && touch "$PROGRESS_FILE"

# Extract RGB and Flow features
python extract_rgb_flow.py \
  -i "$INPUT_VIDEO_DIR" \
  -o "$OUTPUT_VIDEO_DIR"

python extract_mel_spectrogram.py \
  -i "$INPUT_AUDIO_DIR" \
  -o "$OUTPUT_AUDIO_DIR"

# Install necessary Python packages
pip install torch==1.4.0 torchvision==0.5.0 -f https://download.pytorch.org/whl/cu100/torch_stable.html
pip install torchvision
conda install pytorch torchvision cudatoolkit=10.0 -c pytorch
conda install python=3.7.2
pip install chardet

# Extract RGB features
CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
  -t "filelists/${PREFIX}_train.txt" \
  -m RGB \
  -i "$OUTPUT_VIDEO_DIR" \
  -o "features/$PREFIX/feature_rgb_bninception_dim1024_21.5fps"

CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
  -t "filelists/${PREFIX}_test.txt" \
  -m RGB \
  -i "$OUTPUT_VIDEO_DIR" \
  -o "features/$PREFIX/feature_rgb_bninception_dim1024_21.5fps"

# Extract Flow features
CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
  -t "filelists/${PREFIX}_train.txt" \
  -m Flow \
  -i "$OUTPUT_VIDEO_DIR" \
  -o "features/$PREFIX/feature_flow_bninception_dim1024_21.5fps"

CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
  -t "filelists/${PREFIX}_test.txt" \
  -m Flow \
  -i "$OUTPUT_VIDEO_DIR" \
  -o "features/$PREFIX/feature_flow_bninception_dim1024_21.5fps"

FEATURES_DIR="features/$PREFIX/feature_flow_bninception_dim1024_21.5fps"

for file in "$FEATURES_DIR"/*; do
  base_name=$(basename "${file%.*}") # This gets the full filename including extension. Modify if you need just the name without the extension.
  echo "$base_name" >> "$PROGRESS_FILE"
done