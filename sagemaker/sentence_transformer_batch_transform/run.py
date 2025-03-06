import boto3
import sagemaker
from sagemaker.huggingface import HuggingFaceModel


S3_MODEL_NAME = "microsoft/MiniLM-L12-H384-uncased"  # Can be replaced
SAGE_MAKER_MODEL_NAME = None  # Can be replaced
# Useful defaults for embedding generation
HF_ENV = {
    "HF_TASK": "feature-extraction",
    "TS_MAX_RESPONSE_SIZE": "13107000",
    "TS_MAX_REQUEST_SIZE": "13107000",
    "MMS_MAX_RESPONSE_SIZE": "13107000",
    "MMS_MAX_REQUEST_SIZE": "13107000",
    "MMS_WORKERS_PER_MODEL": "4",
    "SAGEMAKER_CONTAINER_LOG_LEVEL": 20,  # 20 is INFO
}


if __name__ == "__main__":
    boto3_session = boto3.Session()
    sagemaker_session = sagemaker.Session(boto_session=boto3_session)
    role = sagemaker.get_execution_role()

    # create model from S3 containing parameters and overloaded script
    model = HuggingFaceModel(
        name=f"test-v1",
        model_data=f"s3://some-bucket/models/{S3_MODEL_NAME}.tar.gz",
        transformers_version="4.17.0",
        pytorch_version="1.10.2",
        py_version="py38",
        env=HF_ENV,  # for overwriting defaults to allow large payloads (with embeddings)
        role=role,
        sagemaker_session=sagemaker_session,
    )

    # creates docker container with batch transform multi-model-server and stores it as model in SageMaker
    transformer = model.transformer(
        instance_count=1,
        instance_type="ml.m4.xlarge",
        output_path="s3://some-bucket/outputs/",
        strategy="SingleRecord",
        assemble_with="Line",
        max_payload=100,
    )
    # runs batch transform job
    transformer.transform(
        data="s3://some-bucket/inputs/",
        data_type="S3Prefix",
        content_type="application/json",
        split_type="Line",
    )
