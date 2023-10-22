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

from model import Regnet
from config import _C as config
from wavenet_vocoder import builder

# # W&B
# import wandb
# GCP_PROJECT = os.environ["GCP_PROJECT"]
# GCS_MODELS_BUCKET_NAME = os.environ["GCS_MODELS_BUCKET_NAME"]
# BEST_MODEL = "model-mobilenetv2_train_base_True.v74"
# ARTIFACT_URI = f"gs://{GCS_MODELS_BUCKET_NAME}/{BEST_MODEL}"
GCP_PROJECT = "ac215project-398818"
GCS_MODELS_BUCKET_NAME = "s2s_data"


data_details = {
    "image_width": 224,
    "image_height": 224,
    "num_channels": 3,
    "num_classes": 3,
    "labels": ["oyster", "crimini", "amanita"],
    "label2index": {"oyster": 0, "crimini": 1, "amanita": 2},
    "index2label": {0: "oyster", 1: "crimini", 2: "amanita"},
}

class CombinedModel(torch.nn.Module):
    def __init__(self, regnet_model, wavenet_model):
        super(CombinedModel, self).__init__()
        self.regnet = regnet_model
        self.wavenet = wavenet_model

    def forward(self, x):
        regnet_output = self.regnet(x)
        wavenet_output = self.wavenet(regnet_output)
        
        return wavenet_output
    
def download_file(packet_url, base_path="", extract=False, headers=None):
    if base_path != "":
        if not os.path.exists(base_path):
            os.mkdir(base_path)
    packet_file = os.path.basename(packet_url)
    with requests.get(packet_url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(os.path.join(base_path, packet_file), "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    if extract:
        if packet_file.endswith(".zip"):
            with zipfile.ZipFile(os.path.join(base_path, packet_file)) as zfile:
                zfile.extractall(base_path)
        else:
            packet_name = packet_file.split(".")[0]
            with tarfile.open(os.path.join(base_path, packet_file)) as tfile:
                tfile.extractall(base_path)

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


def main(args=None):
    if args.upload:
        print("Upload model to GCS")
        
        # Configure GCS client
        storage_client = storage.Client(project=GCP_PROJECT)
        bucket = storage_client.get_bucket(GCS_MODELS_BUCKET_NAME)
        
        # Download the Regnet and Wavenet weights from GCS
        prefix = 'checkpoint_001320'
        blob = bucket.blob(f"ckpt/bongo/demo/{prefix}_netG")
        blob.download_to_filename(f"./ckpt/bongo/demo/{prefix}_netG")
        blob = bucket.blob(f"ckpt/bongo/demo/{prefix}_netD")
        blob.download_to_filename(f"./ckpt/bongo/demo/{prefix}_netD")

        blob = bucket.blob('ckpt/drum_wavenet/drum_checkpoint_step000160000_ema.pth')
        blob.download_to_filename('ckpt/drum_wavenet/drum_checkpoint_step000160000_ema.pth')
        
        # Load the models using the weights
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        regnet_model = Regnet()
        regnet_model.load_checkpoint(f"ckpt/bongo/demo/{prefix}")
        regnet_model.to(device).eval()
        wavenet_model = build_wavenet('ckpt/drum_wavenet/drum_checkpoint_step000160000_ema.pth', device)
        
        combined_model = CombinedModel(regnet_model, wavenet_model).to(device).eval()
        
        # Save the model in TorchScript format
        batch_size = 4
        sequence_length = 215  # number of sequences or frames
        feature_dimension = 2048  # feature dimension per sequence
        dummy_input = torch.rand(batch_size, sequence_length, feature_dimension)

        traced_model = trace(combined_model, dummy_input)
        traced_model.save("model/traced_model.pth")
        
        # Upload the TorchScript model back to GCS
        blob = bucket.blob('model/traced_model.pth')
        blob.upload_from_filename('model/traced_model.pth')
    
        # Similarly, save and upload the Wavenet model if needed...
        # mel_features = 80  
        # time_steps = 860
        # dummy_input_wavenet = torch.rand(1, time_steps, mel_features)

        # traced_wavenet = trace(wavenet_model, dummy_input_wavenet)
        # traced_wavenet.save("model/wavenet/wavenet_traced_model.pth")

        # blob = bucket.blob('model/wavenet/wavenet_traced_model.pth')
        # blob.upload_from_filename('model/wavenet/wavenet_traced_model.pth')
       

        # # Preprocess Image
        # def preprocess_image(bytes_input):
        #     decoded = tf.io.decode_jpeg(bytes_input, channels=3)
        #     decoded = tf.image.convert_image_dtype(decoded, tf.float32)
        #     resized = tf.image.resize(decoded, size=(224, 224))
        #     return resized

        # @tf.function(input_signature=[tf.TensorSpec([None], tf.string)])
        # def preprocess_function(bytes_inputs):
        #     decoded_images = tf.map_fn(
        #         preprocess_image, bytes_inputs, dtype=tf.float32, back_prop=False
        #     )
        #     return {"model_input": decoded_images}

        # @tf.function(input_signature=[tf.TensorSpec([None], tf.string)])
        # def serving_function(bytes_inputs):
        #     images = preprocess_function(bytes_inputs)
        #     results = model_call(**images)
        #     return results

        # model_call = tf.function(prediction_model.call).get_concrete_function(
        #     [
        #         tf.TensorSpec(
        #             shape=[None, 224, 224, 3], dtype=tf.float32, name="model_input"
        #         )
        #     ]
        # )

        # # Save updated model to GCS
        # tf.saved_model.save(
        #     prediction_model,
        #     ARTIFACT_URI,
        #     signatures={"serving_default": serving_function},
        # )

    elif args.deploy:
        print("Deploy model")

        # List of prebuilt containers for prediction
        # https://cloud.google.com/vertex-ai/docs/predictions/pre-built-containers
        serving_container_image_uri = (
            "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-12:latest"
        )

        # Upload and Deploy model to Vertex AI
        # Reference: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.Model#google_cloud_aiplatform_Model_upload
        deployed_model = aiplatform.Model.upload(
            display_name=BEST_MODEL,
            artifact_uri=ARTIFACT_URI,
            serving_container_image_uri=serving_container_image_uri,
        )
        print("deployed_model:", deployed_model)
        # Reference: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.Model#google_cloud_aiplatform_Model_deploy
        endpoint = deployed_model.deploy(
            deployed_model_display_name=BEST_MODEL,
            traffic_split={"0": 100},
            machine_type="n1-standard-4",
            accelerator_count=0,
            min_replica_count=1,
            max_replica_count=1,
            sync=False,
        )
        print("endpoint:", endpoint)

    elif args.predict:
        print("Predict using endpoint")

        # Get the endpoint
        # Endpoint format: endpoint_name="projects/{PROJECT_NUMBER}/locations/us-central1/endpoints/{ENDPOINT_ID}"
        endpoint = aiplatform.Endpoint(
            "projects/129349313346/locations/us-central1/endpoints/5072058134046965760"
        )

        # Get a sample image to predict
        image_files = glob(os.path.join("data", "*.jpg"))
        print("image_files:", image_files[:5])

        image_samples = np.random.randint(0, high=len(image_files) - 1, size=5)
        for img_idx in image_samples:
            print("Image:", image_files[img_idx])

            with open(image_files[img_idx], "rb") as f:
                data = f.read()
            b64str = base64.b64encode(data).decode("utf-8")
            # The format of each instance should conform to the deployed model's prediction input schema.
            instances = [{"bytes_inputs": {"b64": b64str}}]

            result = endpoint.predict(instances=instances)

            print("Result:", result)
            prediction = result.predictions[0]
            print(prediction, prediction.index(max(prediction)))
            print(
                "Label:   ",
                data_details["index2label"][prediction.index(max(prediction))],
                "\n",
            )


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
