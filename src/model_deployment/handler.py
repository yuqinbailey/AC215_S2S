import os
import requests
import zipfile
import tarfile
import argparse
from glob import glob
import numpy as np
import base64
import torch
from tqdm import tqdm

from model import Regnet
from config import _C as config
# from wavenet_vocoder import builder
from ts.torch_handler.base_handler import BaseHandler
from io import BytesIO
import os


TARGET_MODEL_NAME = "traced_regnet_model_test.pth"

class RegNetHandler(BaseHandler):
    """
    The handler takes an input string and returns the classification text 
    based on the serialized transformers checkpoint.
    """
    def __init__(self):
        super(RegNetHandler, self).__init__()
        self.initialized = False

    def initialize(self, ctx):
        """ Loads the model.pt file and initializes the model object.
        Instantiates Tokenizer for preprocessor to use
        Loads labels to name mapping file for post-processing inference response
        """
        self.manifest = ctx.manifest

        properties = ctx.system_properties
        model_dir = properties.get("model_dir")
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")

        # Read model serialize/pt file
        serialized_file = self.manifest["model"]["serializedFile"]
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError("Missing the model.pt or pytorch_model.bin file")
        
        # Load model
        self.model = torch.jit.load(f"/home/model-server/model/RegNet/{TARGET_MODEL_NAME}", map_location=self.device)
        self.model.eval()
        self.initialized = True


    def preprocess(self, data):
        # read the video data
        base64_video = data[0].get("data")
        print(f"input data video bytes: {base64_video}")
        video_buffer = BytesIO(base64_video)

        # save it as a temporary mp4 file
        temp_video_file = '/home/model-server/temp_video.mp4'
        with open(temp_video_file, 'wb') as f:
            f.write(video_buffer.getbuffer())

        # TODO: start to do the preprocess and feature extraction





        # the rest of this part is yet to be deleted
        sequence_length = 215  # number of sequences or frames
        feature_dimension = 2048  # feature dimension per sequence
        mel_features = 80  
        time_steps = 860
        dummy_input = torch.rand(1, sequence_length, feature_dimension)
        dummy_realB = torch.rand(1, mel_features, time_steps)
        
        # inputs = torch.tensor(data[0]['data']).reshape(1, 215, 2048).to(self.device)
        # real_B = torch.tensor(data[1]['data']).reshape(1, 80, 860).to(self.device)
        inputs = dummy_input
        real_B = dummy_realB
        # print(f"preprocess input {inputs}")
        # print(f"preprocess real_B {real_B}")
        return inputs, real_B


    def inference(self, inputs):
        # """ Predict the class of a text using a trained transformer model.
        # """
        inputs, real_B = inputs
        # print(f"inference input {inputs}")
        # print(f"inference real_B {real_B}")
        # with torch.no_grad():
        #     fake_B, _ = self.model(inputs, real_B)
        # return [fake_B.cpu().numpy()]
        return ["Testing the inference side - Leo"]

    def postprocess(self, inference_output):
        return inference_output