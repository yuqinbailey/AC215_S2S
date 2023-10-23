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

        # Define a Container Component for data processor
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

        # Define a Container Component for data processor
        @dsl.container_component
        def data_processor():
            container_spec = dsl.ContainerSpec(
                image=DATA_PROCESSOR_IMAGE,
                command=[],
                args=[
                    "cli.py",
                    #"-p playing_bongo",
                    #"-n 10",
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

    if args.sample1:
        print("Sample Pipeline 1")

        # Define Component
        @dsl.component
        def square(x: float) -> float:
            return x**2

        # Define Component
        @dsl.component
        def add(x: float, y: float) -> float:
            return x + y

        # Define Component
        @dsl.component
        def square_root(x: float) -> float:
            return x**0.5

        # Define a Pipeline
        @dsl.pipeline
        def sample_pipeline(a: float = 3.0, b: float = 4.0) -> float:
            a_sq_task = square(x=a)
            b_sq_task = square(x=b)
            sum_task = add(x=a_sq_task.output, y=b_sq_task.output)
            return square_root(x=sum_task.output).output

        # Build yaml file for pipeline
        compiler.Compiler().compile(
            sample_pipeline, package_path="sample-pipeline1.yaml"
        )

        # Submit job to Vertex AI
        aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

        job_id = generate_uuid()
        DISPLAY_NAME = "sample-pipeline-" + job_id
        job = aip.PipelineJob(
            display_name=DISPLAY_NAME,
            template_path="sample-pipeline1.yaml",
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
        "-t",
        "--model_training",
        action="store_true",
        help="Run just Model Training",
    )
    parser.add_argument(
        "-d",
        "--model_deploy",
        action="store_true",
        help="Run just Model Deployment",
    )
    parser.add_argument(
        "-w",
        "--pipeline",
        action="store_true",
        help="Mushroom App Pipeline",
    )
    parser.add_argument(
        "-s1",
        "--sample1",
        action="store_true",
        help="Sample Pipeline 1",
    )

    args = parser.parse_args()

    main(args)
