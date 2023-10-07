python extract_audio_and_video.py \
    -i data/processed_data/ \
    -o data/features/processed_data

python extract_rgb_flow.py \
    -i data/features/processed_data/videos_10s_21.5fps \
    -o data/features/processed_data/OF_10s_21.5fps

python gen_list.py \
    -i data/processed_data/ \
    -o filelists --prefix processed

python extract_mel_spectrogram.py \
    -i data/features/processed_data/audio_10s_22050hz \
    -o data/features/processed_data/melspec_10s_22050hz
