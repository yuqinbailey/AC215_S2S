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


CUDA_VISIBLE_DEVICES=0 python extract_feature_ceci.py \
    -t filelists/processed_train.txt \
    -m RGB \
    -i data/features/processed_data/OF_10s_21.5fps \
-o data/features/processed_data/feature_rgb_bninception_dim1024_21.5fps

CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
    -t filelists/processed_test.txt \
    -m RGB \
    -i data/features/processed_data/OF_10s_21.5fps \
    -o data/features/processed_data/feature_rgb_bninception_dim1024_21.5fps


CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
    -t filelists/processed_train.txt \
    -m Flow \
    -i data/features/processed_data/OF_10s_21.5fps \
    -o data/features/processed_data/feature_flow_bninception_dim1024_21.5fps

CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
    -t filelists/processed_test.txt \
    -m Flow \
    -i data/features/processed_data/OF_10s_21.5fps \
    -o data/features/processed_data/feature_flow_bninception_dim1024_21.5fps