"""
Module that contains the command line app.

Typical usage example from command line:
        python cli.py --upload
        python cli.py --deploy
        python cli.py --predict
"""

import os
import requests
import zipfile
import tarfile
import argparse
from glob import glob
import numpy as np
import base64
from google.cloud import storage
from google.cloud import aiplatform
import torch
from torch.jit import trace
from tqdm import tqdm

from model import Regnet
from config import _C as config
from wavenet_vocoder import builder

from torchvision import transforms
from PIL import Image
from io import BytesIO

from google.api_core.future.polling import DEFAULT_POLLING

### Set the default timeoutto 3600 seconds
DEFAULT_POLLING._timeout = 3600

# # W&B
# import wandb
# GCP_PROJECT = os.environ["GCP_PROJECT"]
# GCS_MODELS_BUCKET_NAME = os.environ["GCS_MODELS_BUCKET_NAME"]
BEST_MODEL = "traced_regnet_model_test.pth"
GCP_PROJECT = "ac215project-398818"
GCS_MODELS_BUCKET_NAME = "s2s_data_new"
ARTIFACT_URI = f"gs://{GCS_MODELS_BUCKET_NAME}/model/RegNet/"
SERVICE_ACCOUNT = ""

class CombinedModel(torch.nn.Module):
    def __init__(self, regnet_model, wavenet_model):
        super(CombinedModel, self).__init__()
        self.regnet = regnet_model
        self.wavenet = wavenet_model

    def forward(self, *args):
        with torch.no_grad():
            inputs, real_B = args
            fake_B, _ = self.regnet.netG(inputs, real_B)
            fake_B = fake_B[0].data.cpu().numpy()
            save_path = os.path.join(config.save_dir, "demo.wav")
            waveform = gen_waveform(self.wavenet, save_path, fake_B, 'cuda:0')
            return waveform

def build_wavenet(checkpoint_path=None, device='cuda:0'):
    model = builder.wavenet(
        out_channels=30,
        layers=24,
        stacks=4,
        residual_channels=512,
        gate_channels=512,
        skip_out_channels=256,
        cin_channels=80,
        gin_channels=-1,
        weight_normalization=True,
        n_speakers=None,
        dropout=0.05,
        kernel_size=3,
        upsample_conditional_features=True,
        upsample_scales=[4, 4, 4, 4],
        freq_axis_kernel_size=3,
        scalar_input=True,
    )

    model = model.to(device)
    if checkpoint_path:
        print("Load WaveNet checkpoint from {}".format(checkpoint_path))
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    model.make_generation_fast_()

    return model


def gen_waveform(model, save_path, c, device):
    initial_input = torch.zeros(1, 1, 1).to(device)
    if c.shape[1] != config.n_mel_channels:
        c = np.swapaxes(c, 0, 1)
    length = c.shape[0] * 256
    c = torch.FloatTensor(c.T).unsqueeze(0).to(device)
    with torch.no_grad():
        y_hat = model.incremental_forward(
            initial_input, c=c, g=None, T=length, tqdm=tqdm, softmax=True, quantize=True,
            log_scale_min=np.log(1e-14))
    waveform = y_hat.view(-1).cpu().data.numpy()
    # np.save('waveform.npy', waveform)
    #librosa.output.write_wav(save_path, waveform, sr=22050)
    # sf.write(save_path, waveform, samplerate=22050)
    return waveform

class RegnetWrapper(Regnet):
    def __init__(self, *args, **kwargs):
        super(RegnetWrapper, self).__init__(*args, **kwargs)

    def forward(self, input, mel):
        self.parse_batch((input, mel, None))
        super(RegnetWrapper, self).forward()
        return self.fake_B, self.fake_B_postnet

def main(args=None):
    if args.upload:
        print("Upload model to GCS")
        storage_client = storage.Client(credentials=credentials, project=GCP_PROJECT)
        bucket = storage_client.get_bucket(GCS_MODELS_BUCKET_NAME)
        
        # Download the Regnet and Wavenet weights from GCS
        if not os.path.exists("./ckpt/bongo/demo"):
            os.makedirs("./ckpt/bongo/demo")

        prefix = 'checkpoint_001320'
        blob = bucket.blob(f"ckpt/bongo/demo/{prefix}_netG")
        blob.download_to_filename(f"./ckpt/bongo/demo/{prefix}_netG")
        blob = bucket.blob(f"ckpt/bongo/demo/{prefix}_netD")
        blob.download_to_filename(f"./ckpt/bongo/demo/{prefix}_netD")
        
        # Load the models using the weights
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        regnet_model = RegnetWrapper()
        regnet_model.load_checkpoint(f"ckpt/bongo/demo/{prefix}")
        regnet_model.to(device).eval()
        print('successfully loaded regnet model')

        # Convert the PyTorch model to TorchScript format

        # Save the model in TorchScript format
        batch_size = 4
        sequence_length = 215  # number of sequences or frames
        feature_dimension = 2048  # feature dimension per sequence
        mel_features = 80  
        time_steps = 860
        dummy_input = torch.rand(1, sequence_length, feature_dimension)
        dummy_realB = torch.rand(1, mel_features, time_steps)

        # traced_model = torch.jit.script(regnet_model)
        # traced_model = torch.jit.script(regnet_model, example_inputs={regnet_model:[dummy_input, dummy_realB]})
        traced_model = torch.jit.trace(regnet_model, (dummy_input, dummy_realB))
        


        print("succesfully constructed the model")
        traced_model.save("model/RegNet/traced_regnet_model_test.pth")
        print('successfully saved')

        # Upload the model file to the GCS bucket
        model_gcs_path = "model/RegNet/traced_regnet_model_test.pth" 
        blob = bucket.blob(model_gcs_path)
        blob.upload_from_filename(model_gcs_path)

        print(f"Regnet model uploaded to {model_gcs_path} in the GCS bucket {GCS_MODELS_BUCKET_NAME}")

    elif args.deploy:
        print("Deploy model")

        # List of prebuilt containers for prediction
        # https://cloud.google.com/vertex-ai/docs/predictions/pre-built-containers
        # serving_container_image_uri = (
        #     "us-docker.pkg.dev/vertex-ai/prediction/pytorch/torchserve:latest-gpu"
        # )
        # serving_container_image_uri = (
        #     "us-central1-docker.pkg.dev/ac215project-398818/gcf-artifacts/pytorch_predict_regnet"
        # )
        # # Upload and Deploy model to Vertex AI
        # # Reference: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.Model#google_cloud_aiplatform_Model_upload
        # deployed_model = aiplatform.Model.upload(
        #     display_name=BEST_MODEL,
        #     artifact_uri=ARTIFACT_URI,
        #     serving_container_image_uri=serving_container_image_uri,
        # )
        # print("deployed_model:", deployed_model)
        # # Reference: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.Model#google_cloud_aiplatform_Model_deploy
        # endpoint = deployed_model.deploy(
        #     deployed_model_display_name=BEST_MODEL,
        #     traffic_split={"0": 100},
        #     machine_type="n1-standard-4",
        #     accelerator_count=1,
        #     min_replica_count=2,
        #     max_replica_count=5,
        #     sync=False,
        # )
        # print("endpoint:", endpoint)

        VERSION = 1
        CUSTOM_PREDICTOR_IMAGE_URI = "us-central1-docker.pkg.dev/ac215project-398818/gcf-artifacts/pytorch_predict_regnet:cc"
        # CUSTOM_PREDICTOR_IMAGE_URI = "us-central1-docker.pkg.dev/ac215project-398818/gcf-artifacts/pytorch_predict_regnet:latest"

        APP_NAME = "regnet"
        model_display_name = f"{APP_NAME}-v{VERSION}"
        model_description = "PyTorch based regnet with custom container"

        MODEL_NAME = APP_NAME
        health_route = "/ping"
        predict_route = f"/predictions/{MODEL_NAME}"
        serving_container_ports = [7080]

        model = aiplatform.Model.upload(
            display_name=model_display_name,
            description=model_description,
            serving_container_image_uri=CUSTOM_PREDICTOR_IMAGE_URI,
            serving_container_predict_route=predict_route,
            serving_container_health_route=health_route,
            serving_container_ports=serving_container_ports,
        )

        model.wait()

        print("Successfully uploaded the model")
        print(model.display_name)
        print(model.resource_name)

        endpoint_display_name = f"{APP_NAME}-endpoint"
        endpoint = aiplatform.Endpoint.create(display_name=endpoint_display_name)

        traffic_percentage = 100
        machine_type = "n1-standard-2"
        deployed_model_display_name = model_display_name
        min_replica_count = 1
        max_replica_count = 1
        accelerator_type = "NVIDIA_TESLA_T4"  # Example accelerator type
        accelerator_count = 1  # Number of accelerators per machine
        sync = True

        model.deploy(
            endpoint=endpoint,
            deployed_model_display_name=deployed_model_display_name,
            machine_type=machine_type,
            traffic_percentage=traffic_percentage,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            sync=sync,
            deploy_request_timeout=100000000,
            enable_access_logging=True,
        )

        print("Successfully deployed the model")
        model.wait()

    elif args.predict:
        print("Predict using endpoint")

        # Get the endpoint
        # Endpoint format: endpoint_name="projects/{PROJECT_NUMBER}/locations/us-central1/endpoints/{ENDPOINT_ID}"
        endpoint = aiplatform.Endpoint(
            "projects/634116577723/locations/us-central1/endpoints/5891115131902885888"
        )


        with open('input_payload.json', 'r') as file:
            # Parse JSON content from file
            json_dict = json.load(file)

        # instance = [{
        #     "data": {
        #         "b64": str(b64_encoded.decode('utf-8'))
        #     }
        # }]
        instance = json_dict["instances"]
        # print(instance)

        print(f"Start the prediction...")
        print(f"Waiting for the response...")
        prediction = endpoint.predict(instances=instance, timeout=100000000)
        print(f"Prediction response: \n\t{prediction}")


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Data Collector CLI")

    parser.add_argument(
        "-u",
        "--upload",
        action="store_true",
        help="Upload saved model to GCS Bucket",
    )
    parser.add_argument(
        "-d",
        "--deploy",
        action="store_true",
        help="Deploy saved model to Vertex AI",
    )
    parser.add_argument(
        "-p",
        "--predict",
        action="store_true",
        help="Make prediction using the endpoint from Vertex AI",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Test deployment to Vertex AI",
    )

    args = parser.parse_args()

    main(args)
