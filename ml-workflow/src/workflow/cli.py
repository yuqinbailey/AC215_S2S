"""
Module that contains the command line app.

Typical usage example from command line:
        python cli.py
"""

import os
import argparse
import random
import string
from kfp import dsl
from kfp import compiler
import google.cloud.aiplatform as aip
from model import model_training, model_deploy


GCP_PROJECT = os.environ["GCP_PROJECT"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
BUCKET_URI = f"gs://{GCS_BUCKET_NAME}"
PIPELINE_ROOT = f"{BUCKET_URI}/pipeline_root/root"
GCS_SERVICE_ACCOUNT = os.environ["GCS_SERVICE_ACCOUNT"]
#GCS_PACKAGE_URI = os.environ["GCS_PACKAGE_URI"]
#GCP_REGION = os.environ["GCP_REGION"]

# DATA_COLLECTOR_IMAGE = "gcr.io/ac215-project/mushroom-app-data-collector"
DATA_COLLECTOR_IMAGE = "lildanni/data-collection"
DATA_PROCESSOR_IMAGE = "lildanni/data-preprocessing"
FEATURE_EXTRACTION_IMAGE = "lildanni/feature-extraction"

def generate_uuid(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def main(args=None):
    print("CLI Arguments:", args)

    if args.data_collector:
        # Define a Container Component
        @dsl.container_component
        def data_collector():
            container_spec = dsl.ContainerSpec(
                image=DATA_COLLECTOR_IMAGE,
                command=[],
                args=[
                    "cli.py",
                    "--num_workers 4",
                                    ],
            )
            return container_spec

        # Define a Pipeline
        @dsl.pipeline
        def data_collector_pipeline():
            data_collector()

        # Build yaml file for pipeline
        compiler.Compiler().compile(
            data_collector_pipeline, package_path="data_collector.yaml"
        )

        # Submit job to Vertex AI
        aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

        job_id = generate_uuid()
        DISPLAY_NAME = "s2s-data-collector-" + job_id
        job = aip.PipelineJob(
            display_name=DISPLAY_NAME,
            template_path="data_collector.yaml",
            pipeline_root=PIPELINE_ROOT,
            enable_caching=False,
        )

        job.run(service_account=GCS_SERVICE_ACCOUNT)

    if args.data_preprocessor:
        print("Data Preprocessor")

        # Define a Container Component for data preprocessor
        @dsl.container_component
        def data_preprocessor():
            container_spec = dsl.ContainerSpec(
                image=DATA_PROCESSOR_IMAGE,
                command=[],
                args=[
                    "cli.py",
                    "-p playing_bongo",
                    "-n 10",
                ],
            )
            return container_spec

        # Define a Pipeline
        @dsl.pipeline
        def data_preprocessor_pipeline():
            data_preprocessor()

        # Build yaml file for pipeline
        compiler.Compiler().compile(
            data_preprocessor_pipeline, package_path="data_preprocessor.yaml"
        )

        # Submit job to Vertex AI
        aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

        job_id = generate_uuid()
        DISPLAY_NAME = "s2s-data-preprocessor-" + job_id
        job = aip.PipelineJob(
            display_name=DISPLAY_NAME,
            template_path="data_preprocessor.yaml",
            pipeline_root=PIPELINE_ROOT,
            enable_caching=False,
        )

        job.run(service_account=GCS_SERVICE_ACCOUNT)

    # In progress
    if args.feature_extractor:
        print("Feature Extractor")

        # Define a Container Component for feature extractor
        @dsl.container_component
        def feature_extractor():
            container_spec = dsl.ContainerSpec(
                image=FEATURE_EXTRACTION_IMAGE,
                command=[],
                args=[
                    "./feature_extract.sh",
                    "-p",
                    "playing_bongo",
                    "-n 1",
                ],
            )
            return container_spec

        # Define a Pipeline
        @dsl.pipeline
        def feature_extractor_pipeline():
            feature_extractor()

        # Build yaml file for pipeline
        compiler.Compiler().compile(
            feature_extractor_pipeline, package_path="feature_extractor.yaml"
        )

        # Submit job to Vertex AI
        aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

        job_id = generate_uuid()
        DISPLAY_NAME = "s2s-feature_extractor-" + job_id
        job = aip.PipelineJob(
            display_name=DISPLAY_NAME,
            template_path="feature_extractor.yaml",
            pipeline_root=PIPELINE_ROOT,
            enable_caching=False,
        )

        job.run(service_account=GCS_SERVICE_ACCOUNT)

    if args.model_deploy:
        print("Model Deploy")

        # Define a Pipeline
        @dsl.pipeline
        def model_deploy_pipeline():
            model_deploy(
                bucket_name=GCS_BUCKET_NAME,
            )

        # Build yaml file for pipeline
        compiler.Compiler().compile(
            model_deploy_pipeline, package_path="model_deploy.yaml"
        )

        # Submit job to Vertex AI
        aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

        job_id = generate_uuid()
        DISPLAY_NAME = "s2s-model-deploy-" + job_id
        job = aip.PipelineJob(
            display_name=DISPLAY_NAME,
            template_path="model_deploy.yaml",
            pipeline_root=PIPELINE_ROOT,
            enable_caching=False,
        )

        job.run(service_account=GCS_SERVICE_ACCOUNT)

    if args.pipeline:
        # Define a Container Component for data collector
        @dsl.container_component
        def data_collector():
            container_spec = dsl.ContainerSpec(
                image=DATA_COLLECTOR_IMAGE,
                command=[],
                args=[
                    "cli.py",
                    "--num_workers 4",
                                    ],
            )
            return container_spec

        # Define a Container Component for data preprocessor
        @dsl.container_component
        def data_preprocessor():
            container_spec = dsl.ContainerSpec(
                image=DATA_PROCESSOR_IMAGE,
                command=[],
                args=[
                    "cli.py",
                    "-p playing_bongo",
                    "-n 10",
                ],
            )
            return container_spec

        # Define a Container Component for feature extractor
        @dsl.container_component
        def feature_extractor():
            container_spec = dsl.ContainerSpec(
                image=FEATURE_EXTRACTION_IMAGE,
                command=[],
                args=[
                    "./feature_extract.sh",
                    "-p",
                    "playing_bongo",
                    "-n 1",
                ],
            )
            return container_spec

        # Define a Pipeline
        @dsl.pipeline
        def ml_pipeline():
            # Data Collector
            data_collector_task = data_collector().set_display_name("Data Collector")
            # Data Processor
            data_preprocessor_task = (
                data_preprocessor()
                .set_display_name("Data Processor")
                .after(data_collector_task)
            )
            # Feature Extractor
            feature_extractor_task = (
                feature_extractor()
                .set_display_name("Feature Extractor")
                .after(data_preprocessor_task)
            )
            # # Model Training
            # model_training_task = (
            #     model_training(
            #         project=GCP_PROJECT,
            #         location=GCP_REGION,
            #         staging_bucket=GCS_PACKAGE_URI,
            #         bucket_name=GCS_BUCKET_NAME,
            #         epochs=15,
            #         batch_size=16,
            #         model_name="mobilenetv2",
            #         train_base=False,
            #     )
            #     .set_display_name("Model Training")
            #     .after(feature_extractor_task)
            # )
            # Model Deployment
            model_deploy_task = (
                model_deploy(
                    bucket_name=GCS_BUCKET_NAME,
                )
                .set_display_name("Model Deploy")
                .after(feature_extractor_task)
            )

        # Build yaml file for pipeline
        compiler.Compiler().compile(ml_pipeline, package_path="pipeline.yaml")

        # Submit job to Vertex AI
        aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

        job_id = generate_uuid()
        DISPLAY_NAME = "mushroom-app-pipeline-" + job_id
        job = aip.PipelineJob(
            display_name=DISPLAY_NAME,
            template_path="pipeline.yaml",
            pipeline_root=PIPELINE_ROOT,
            enable_caching=False,
        )

        job.run(service_account=GCS_SERVICE_ACCOUNT)

    


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Workflow CLI")

    parser.add_argument(
        "-c",
        "--data_collector",
        action="store_true",
        help="Run just the Data Collector",
    )
    parser.add_argument(
        "-p",
        "--data_preprocessor",
        action="store_true",
        help="Run just the Data Processor",
    )
    parser.add_argument(
        "-e",
        "--feature_extractor",
        action="store_true",
        help="Run just the Feature Extractor",
    )

    parser.add_argument(
        "-d",
        "--model_deploy",
        action="store_true",
        help="Run just Model Deploy",
    )
    parser.add_argument(
        "-w",
        "--pipeline",
        action="store_true",
        help="S2S Pipeline",
    )

    args = parser.parse_args()

    main(args)
