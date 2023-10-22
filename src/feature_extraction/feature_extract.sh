#!/bin/bash

# Default values
PREFIX="playing_bongo"
FPS="21.5"
N="10"

# Parse command-line arguments
while getopts "p:f:n:" opt; do
  case $opt in
    p)
      PREFIX="$OPTARG"
      ;;
    f)
      FPS="$OPTARG"
      ;;
    n)
      N="$OPTARG"
      ;;
    \?)
      echo "Usage: $0 [-p PREFIX] [-f FPS] [-n N]" >&2
      exit 1
      ;;
  esac
done

# download data
python download_data.py -p "$PREFIX" -n "$N"

# Define input and output directories
INPUT_VIDEO_DIR="processed_data/$PREFIX/video_10s_${FPS}fps"
OUTPUT_VIDEO_DIR="features/$PREFIX/OF_10s_${FPS}fps"
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

# Extract RGB features
CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
  -t "features/filelists/${PREFIX}_train_new.txt" \
  -m RGB \
  -i "$OUTPUT_VIDEO_DIR" \
  -o "features/$PREFIX/feature_rgb_bninception_dim1024_${FPS}fps"

CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
  -t "features/filelists/${PREFIX}_test_new.txt" \
  -m RGB \
  -i "$OUTPUT_VIDEO_DIR" \
  -o "features/$PREFIX/feature_rgb_bninception_dim1024_${FPS}fps"

# Extract Flow features
CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
  -t "features/filelists/${PREFIX}_train_new.txt" \
  -m Flow \
  -i "$OUTPUT_VIDEO_DIR" \
  -o "features/$PREFIX/feature_flow_bninception_dim1024_${FPS}fps"

CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
  -t "features/filelists/${PREFIX}_test_new.txt" \
  -m Flow \
  -i "$OUTPUT_VIDEO_DIR" \
  -o "features/$PREFIX/feature_flow_bninception_dim1024_${FPS}fps"

FEATURES_DIR="features/$PREFIX/feature_flow_bninception_dim1024_${FPS}fps/"

for file in "$FEATURES_DIR"/*; do
  if [ -f "$file" ]; then  # Check if it's a regular file (not a directory)
    base_name=$(basename "${file%.*}") # This gets the full filename including extension.
    echo "$base_name" >> "$PROGRESS_FILE"
  fi
done

TRAIN_NEW="features/filelists/${PREFIX}_train_new.txt"
TEST_NEW="features/filelists/${PREFIX}_test_new.txt"

new_files=("${TRAIN_NEW}" "${TEST_NEW}")

for new_file in  "${new_files[@]}"; do
    # Extract the base name without "_new"
    orig_file="${new_file%_new.txt}.txt"

    # Append contents of new_file to orig_file
    cat "$new_file" >> "$orig_file"

    # Delete the _new.txt file
    rm "$new_file"
done

# upload feature
python upload_feature.py 
