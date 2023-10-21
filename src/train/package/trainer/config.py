from yacs.config import CfgNode as CN



_C  =  CN()
_C.BASE_DATA_PATH = "/gcs/s2s_data/"
# _C.epochs = 1000
_C.epochs = 50
_C.num_epoch_save = 10
_C.seed = 123
_C.dynamic_loss_scaling = True
_C.dist_backend = "nccl"
_C.dist_url = "tcp://localhost:54321"
_C.cudnn_enabled = True
_C.cudnn_benchmark = False
_C.save_dir = _C.BASE_DATA_PATH + 'ckpt/processed_data/'
_C.checkpoint_path = ''
# _C.checkpoint_path = 'ckpt/processed_data/checkpoint_041000'
_C.epoch_count = 0
_C.exclude_dirs = ['ckpt', 'data']
_C.training_files = _C.BASE_DATA_PATH + 'filelists/playing_bongo_train.txt'
_C.test_files = _C.BASE_DATA_PATH + 'filelists/playing_bongo_test.txt'
# _C.rgb_feature_dir = "data/features/dog/feature_rgb_bninception_dim1024_21.5fps"
# _C.flow_feature_dir = "data/features/dog/feature_flow_bninception_dim1024_21.5fps"
# _C.mel_dir = "data/features/dog/melspec_10s_22050hz"
# _C.rgb_feature_dir = BASE_TRAINER_PATH + "data/features/processed_data/feature_rgb_bninception_dim1024_21.5fps"
# _C.flow_feature_dir = BASE_TRAINER_PATH + "data/features/processed_data/feature_flow_bninception_dim1024_21.5fps"
# _C.mel_dir =BASE_TRAINER_PATH + "data/features/processed_data/melspec_10s_22050hz"
_C.rgb_feature_dir = _C.BASE_DATA_PATH + "features/playing_bongo/feature_rgb_bninception_dim1024_21.5fps"
_C.flow_feature_dir = _C.BASE_DATA_PATH + "features/playing_bongo/feature_flow_bninception_dim1024_21.5fps"
_C.mel_dir =_C.BASE_DATA_PATH + "features/playing_bongo/melspec_10s_22050hz"
_C.video_samples = 215
_C.audio_samples = 10
_C.mel_samples = 860
_C.visual_dim = 2048
_C.n_mel_channels = 80
_C.wandb_api_key = "f41e521531bde36451c2adc9a1e7b2de8f2064fa"

# Encoder parameters
_C.random_z_dim = 512
_C.encoder_n_lstm = 2
_C.encoder_embedding_dim = 2048
_C.encoder_kernel_size = 5
_C.encoder_n_convolutions = 3

# Auxiliary parameters
_C.auxiliary_type = "lstm_last"
_C.auxiliary_dim = 32
_C.auxiliary_sample_rate = 32
_C.mode_input = ""
_C.aux_zero = False

# Decoder parameters
_C.decoder_conv_dim = 1024

# Mel-post processing network parameters
_C.postnet_embedding_dim = 512
_C.postnet_kernel_size = 5
_C.postnet_n_convolutions = 5

_C.loss_type = "MSE"
_C.weight_decay = 1e-6
_C.grad_clip_thresh = 1.0
# _C.batch_size = 64
_C.batch_size = 4
_C.lr = 0.0002
_C.beta1 = 0.5
_C.continue_train = False
_C.lambda_Oriloss = 10000.0
_C.lambda_Silenceloss = 0
_C.niter = 100
_C.D_interval = 1
_C.wo_G_GAN = False
_C.wavenet_path = _C.BASE_DATA_PATH + 'ckpt/drum_wavenet/drum_checkpoint_step000160000_ema.pth'
