from collections import namedtuple

import boto3
import pytest
from moto import mock_aws

from tests import settings


@pytest.fixture(scope="function")
def mocked_aws():
    with mock_aws():
        yield


@pytest.fixture(scope="function")
def mocked_s3(mocked_aws):
    s3 = boto3.client("s3", region_name=settings.TEST_AWS_REGION)

    s3.create_bucket(Bucket=settings.INPUT_BUCKET_NAME)
    s3.create_bucket(Bucket=settings.PAYLOAD_BUCKET_NAME)

    yield s3


@pytest.fixture(scope="function")
def mocked_sqs(mocked_aws):
    sqs = boto3.client("sqs", region_name=settings.TEST_AWS_REGION)

    queue_url = sqs.create_queue(QueueName=settings.QUEUE_NAME)["QueueUrl"]
    yield sqs, queue_url


@pytest.fixture
def lambda_context():
    context_data = {
        "function_name": "test_function",
        "memory_limit_in_mb": 128,
        "invoked_function_arn": "arn:aws:lambda:region:account:function:test_function",
        "aws_request_id": "12345678-1234-1234-1234-123456789012",
    }
    LambdaContext = namedtuple("LambdaContext", context_data.keys())
    return LambdaContext(*context_data.values())
