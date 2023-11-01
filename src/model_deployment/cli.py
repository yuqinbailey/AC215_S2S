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

# # W&B
# import wandb
# GCP_PROJECT = os.environ["GCP_PROJECT"]
# GCS_MODELS_BUCKET_NAME = os.environ["GCS_MODELS_BUCKET_NAME"]
BEST_MODEL = "RegWaveNet"
GCP_PROJECT = "ac215project-398818"
GCS_MODELS_BUCKET_NAME = "s2s_data"
ARTIFACT_URI = f"gs://{GCS_MODELS_BUCKET_NAME}/{BEST_MODEL}"

########### only in this container, DO NOT PUSH TO GIT HUB ###########

from google.oauth2 import service_account
import json
SERVICE_ACCOUNT = json.loads(r"""{
    "type": "service_account",
    "project_id": "ac215project-398818",
    "private_key_id": "30a1b85791b1178f16bd1546f40b2c6131ca7a47",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC10F9XtSBx7z0A\nwcqZcGv9GdVyQfRIby9XAQc+KStmyroZQEoWk0akFHxBoVScgaoYTw9nXvfF9yGF\nCmvByCzrbfwAtEPVubWbhUMjEqQtldDQoLhSlWII0psAQBTeNyrxESiaEaimf7dh\niD1r7+Bv0aSj/zhjDcu903v7ed9TI906gxUIdOXm44SHwbouFlS+t5awr/Ep0Irn\nSKGSGm5x521hiBT/WdpY9Lr2bT+NsBVi1K9oKVN/JiJv2vh3mRtMVJMk0iGHqkLl\nMCHZsKI5xcGCkqEvnybLt38qh5Ea4uWf9RejFJiLUPMPwLossB5cYczJIYX4Su7t\nlFsunDoTAgMBAAECggEAESN/K/470eb/70zVTikt/NINGrQDP5AU5yoxJm0XasgB\nyp89UgB4axTam7iGCH95QHO0xi/1F65n9KnFUPiPh3KQNqQc4Djyg3ezRaCcZQcC\nLqXKik+2SeefII2/NIKrI8X+zPs3fy57ORCbMva4nOx8Yns3XlsEEYpYiHL2GC5D\nSjC/8gssQXeUYF/WRUI5T7FXUJijSREIwu1Fx7mchmzgykI6vjasvevgCqAUZfc2\nw/3VYzFHkzHE9BGI9hL8KaK07RRihVil5dqdmB29FYSVyD9YvgQuaN1KpZfSsCqK\nkrB6meqRfq4D79o6TkbXXdjzIaOlEBZ+yUVyFZTgfQKBgQDsTEPZL2NyU4uYng/0\nUiScy3ihlsEVx/Dq9BdTQD3tct4EH0KgSUaIVrXAKJHtq0avR4/O6YxqGYKYql6T\n5rpmsFssWJg+EfVqpafPQxjnr2pf6sVdfXuuHFfVk9wWT8+AdiplG0C9n+NUpD1s\nTuwoa7Ev7haRd75xIfnhlTFqNQKBgQDE+ShRz90qF6nPeWMmtC1k2w2ovVyHXwPN\nAk8wNTmVxq834tvA0LsQrVHl3SY/HilN/p/Bq5EXNVW8+3eHjJxk5bnvm9yHxkUG\n1PPCy0ZbHiPpCOALHEI+GJdpGeupwd+yminz0HgWH/xOsN/Ef16TViAFXBr0rdFj\nWLZpF4JcJwKBgHcVqEvX+gIv4HY1kkzK6PCsCktFMmHLtbpy8R5fjdYQwZrKNkWZ\nKBalvErvJzvjyWekZPEd+kmuOYa+tZNMADyoPAqJS5BcdJYejgeCBRcd7DoSkwye\npKoGVq2oKo6EAkr3Qj5aEbJ+1Y5ehyYCUDm+rDk/f9gnxK43NTteeNzRAoGACq6A\nUz90fO3flZK9n8GxnICMkxQByo2KhTmU1cZtIwQtSFiTFje7jUH46QA/LLkUAFjI\njRYiviF0TtVMPBuR957FoIrRQMOtxpsRxQSFAjf2NpL2o2Oa7AclXtu6/e+3k9Xs\nZH5vpLODWTkaSWum01KeVewSwiYS7tJGwhg2R40CgYAMvuGXH3BbUTP+KlL7Weh/\nEOhYO1lxQW41YSq6CPDmQOUJaf9tK512d/Fd9u7nZCQhXSiZHj9zUav6YTSZ+Wp/\n9Xz3tESvVYB8dvYI2F21J7iBvpF7Ludft7LqWx+X8Uelg1HKXmxkgWRHiRpfCKoG\nPBQM2JjpgdMgWaD1Y/rXqA==\n-----END PRIVATE KEY-----\n",
    "client_email": "model-deployment@ac215project-398818.iam.gserviceaccount.com",
    "client_id": "104802719843929809393",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/model-deployment%40ac215project-398818.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
  }""")

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
########################################################################

class CombinedModel(torch.nn.Module):
    def __init__(self, regnet_model, wavenet_model):
        super(CombinedModel, self).__init__()
        self.regnet = regnet_model
        self.wavenet = wavenet_model

    def forward(self, *args):
        with torch.no_grad():
            inputs, real_B = args
            fake_B, _ = self.regnet.netG(inputs, real_B)
            # fake_B = fake_B[0].data.cpu().numpy()
            fake_B = fake_B[0].data
            # save_path = os.path.join(config.save_dir, "demo.wav")
            # waveform = gen_waveform(self.wavenet, save_path, fake_B, 'cuda:0')
            return fake_B


class RegnetWrapper(Regnet):
    def __init__(self, *args, **kwargs):
        super(RegnetWrapper, self).__init__(*args, **kwargs)

    def forward(self, input, mel):
        self.parse_batch((input, mel, None))
        super(RegnetWrapper, self).forward()
        return self.fake_B, self.fake_B_postnet


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


def main(args=None):
    if args.trace:
        print("Trace model")

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        prefix = 'checkpoint_001320'
        regnet_model = RegnetWrapper()
        regnet_model.load_checkpoint(f"ckpt/bongo/demo/{prefix}")
        regnet_model.to(device).eval()
        example_input_tensor_1 = torch.randn(1, 215, 2048)
        example_input_tensor_2 = torch.randn(1, 80, 860)
        traced_model = trace(regnet_model, (example_input_tensor_1, example_input_tensor_2))
        traced_model.save("model/traced_regnet_model.pth")

    elif args.upload:
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

        if not os.path.exists("./ckpt/drum_wavenet"):
            os.makedirs("./ckpt/drum_wavenet")
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
        mel_features = 80  
        time_steps = 860
        dummy_input = torch.rand(1, sequence_length, feature_dimension)
        dummy_realB = torch.rand(1, mel_features, time_steps)

        for module in combined_model.modules():
            module._backward_hooks = {}
        traced_model = trace(combined_model, (dummy_input,dummy_realB))
        print("check progress")
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
    parser.add_argument(
        "-z",
        "--trace",
        action="store_true",
        help="Make prediction using the endpoint from Vertex AI",
    )

    args = parser.parse_args()

    main(args)
