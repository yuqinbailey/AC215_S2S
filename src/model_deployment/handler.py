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
        self.model = torch.jit.load(f"/home/model-server/model/RegNet/traced_regnet_model_test.pth", map_location=self.device)
        self.model.eval()
        self.initialized = True
        
        # Ensure to use the same tokenizer used during training
        # self.tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')

        # Read the mapping file, index to object name
        # mapping_file_path = os.path.join(model_dir, "index_to_name.json")

        # if os.path.isfile(mapping_file_path):
        #     with open(mapping_file_path) as f:
        #         self.mapping = json.load(f)
        # else:
        #     logger.warning('Missing the index_to_name.json file. Inference output will not include class name.')


    def preprocess(self, data):
        # """ Preprocessing input request by tokenizing
        #     Extend with your own preprocessing steps as needed
        # """
        # text = data[0].get("data")
        # if text is None:
        #     text = data[0].get("body")
        # sentences = text.decode('utf-8')
        # logger.info("Received text: '%s'", sentences)

        # # Tokenize the texts
        # tokenizer_args = ((sentences,))
        # inputs = self.tokenizer(*tokenizer_args,
        #                         padding='max_length',
        #                         max_length=128,
        #                         truncation=True,
        #                         return_tensors = "pt")
        
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
        print(f"preprocess input {inputs}")
        print(f"preprocess real_B {real_B}")
        return inputs, real_B


    def inference(self, inputs):
        # """ Predict the class of a text using a trained transformer model.
        # """
        inputs, real_B = inputs
        # with torch.no_grad():
        #     fake_B, _ = self.model(inputs, real_B)
        # return [fake_B.cpu().numpy()]
        print(f"inference input {inputs}")
        print(f"inference real_B {real_B}")
        return ["Testing the inference side - Leo"]

    def postprocess(self, inference_output):
        return inference_output