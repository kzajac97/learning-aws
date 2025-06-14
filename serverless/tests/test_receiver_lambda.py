import json
import sys
import os
import random
from datetime import datetime, timedelta

import awswrangler as wr
import boto3
import pandas as pd
import pytest

from tests import settings


@pytest.fixture(scope="function")
def source_root():
    sys.path.append("src/receiver_lambda")
    yield
    sys.path.remove("src/receiver_lambda")


def random_date():
    """Generate a random datetime between 2020-01-01 and now."""
    delta = datetime.now() - datetime.min
    delta_seconds = delta.total_seconds()
    random_seconds = random.uniform(0, delta_seconds)
    return datetime.min + timedelta(seconds=random_seconds)


def prepare_s3_input(num_locations: int, num_csv_rows: int):
    df = pd.DataFrame(
        {
            "sensor_id": [random.choice(range(1, num_locations + 1)) for _ in range(num_csv_rows)],
            "location_id": [random.choice(range(1, num_locations + 1)) for _ in range(num_csv_rows)],
            "temperature": [random.uniform(20, 250) for _ in range(num_csv_rows)],
            "timestamp": [random_date().isoformat() for _ in range(num_csv_rows)],
        }
    )

    wr.s3.to_csv(df=df, path=f"s3://{settings.INPUT_BUCKET_NAME}/test.csv", index=False)
    return df


def prepare_sqs_input(num_locations: int, num_csv_rows: int):
    sqs = boto3.client("sqs", region_name=settings.TEST_AWS_REGION)
    queue_url = os.getenv("SQS_URL")  # executed after mock_env

    for _ in range(num_csv_rows):
        message = json.dumps(
            {
                "sensor_id": random.choice(range(1, num_locations + 1)),
                "location_id": random.choice(range(1, num_locations + 1)),
                "temperature": random.uniform(20, 250),
                "timestamp": random_date().isoformat(),
            }
        )

        sqs.send_message(QueueUrl=queue_url, MessageBody=message)


@pytest.fixture
def mock_env(mocked_sqs):
    _, queue_url = mocked_sqs
    return {
        "ENV": "test",
        "SQS_URL": queue_url,
        "INPUT_BUCKET": settings.INPUT_BUCKET_NAME,
        "PAYLOAD_BUCKET": settings.PAYLOAD_BUCKET_NAME,
        "AWS_REGION": settings.TEST_AWS_REGION,
        "AWS_PROFILE_NAME": settings.TEST_AWS_PROFILE_NAME,
    }


@pytest.mark.parametrize(
    ["num_rows", "num_locations"],
    (
        (10, 2),
        (20, 5),
        (50, 10),
        (100, 10),
        (100, 20),
    ),
)
def test_receiver_lambda_handler_s3(
    num_rows: int, num_locations: int, mock_env, mocked_s3, lambda_context, source_root, mocker
):
    mocker.patch.dict(os.environ, mock_env, clear=True)  # patch environment variables before importing handler
    prepare_s3_input(num_locations, num_rows)

    from src.receiver_lambda.main import handler

    event = {"source": "S3", "key": "test.csv"}
    response = handler(event, lambda_context)

    assert response["status_code"] == 200
    assert len(response["batches"]) <= num_locations  # some locations may not have data


@pytest.mark.parametrize(
    ["num_rows", "num_locations"],
    (
        (10, 2),
        (100, 5),
        (500, 10),
        (1000, 20),
        (1000, 100),
    ),
)
def test_receiver_lambda_handler_sqs(
    num_rows: int, num_locations: int, mock_env, mocked_sqs, lambda_context, source_root, mocker
):
    mocker.patch.dict(os.environ, mock_env, clear=True)  # patch environment variables before importing handler
    prepare_sqs_input(num_locations, num_rows)

    from src.receiver_lambda.main import handler

    event = {"source": "SQS"}
    response = handler(event, lambda_context)

    assert response["status_code"] == 200
    assert len(response["batches"]) <= num_locations  # some locations may not have data
