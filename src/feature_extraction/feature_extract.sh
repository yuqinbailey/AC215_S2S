CUDA_VISIBLE_DEVICES=0 python extract_feature.py \
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