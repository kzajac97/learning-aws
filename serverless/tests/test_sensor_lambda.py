import os
import json
from typing import Any

import freezegun
import pytest

from tests import settings


@pytest.fixture(scope="function")
def mock_env(mocked_dynamodb, mocked_sns, mocked_sqs):
    _, queue_url = mocked_sqs
    _, topic_arn = mocked_sns

    return {
        "ENV": "test",
        "SENSOR_REGISTRY_TABLE": settings.SENSOR_REGISTRY_TABLE,
        "AWS_REGION": settings.TEST_AWS_REGION,
        "AWS_PROFILE_NAME": settings.TEST_AWS_PROFILE_NAME,
        "LAMBDA_IDEMPOTENCY_TABLE": settings.IDEMPOTENCY_TABLE,
        "SNS_TOPIC_ARN": topic_arn,
        "SQS_URL": queue_url,
    }


@pytest.mark.parametrize(
    [
        "event",
        "dynamodb_content",
        "expected_status_code",
        "expected_response",
        "expected_dynamodb_content",
        "expected_sns_messages",
        "expected_sqs_messages",
    ],
    (
        (
            {"sensor_id": "1", "location_id": "A", "value": 2000},  # event
            {},  # empty dynamodb_content
            200,
            {"sensor_id": "1", "location_id": "A", "status": "OK", "timestamp": settings.TIME},
            {},  # expected_dynamodb_content
            [],  # expected_sns_messages
            [],  # expected_sqs_messages
        ),
    ),
)
@freezegun.freeze_time(settings.TIME)
def test_sensor_lambda(
    event: dict,
    dynamodb_content: list[dict],
    expected_status_code: int,
    expected_response: dict[str, Any],
    expected_dynamodb_content: list[dict],
    expected_sns_messages,
    expected_sqs_messages,
    mock_env,
    lambda_context,
    mocked_s3,
    mocked_dynamodb,
    mocked_sns,
    mocked_sqs,
    mocker,
):
    mocker.patch.dict(os.environ, mock_env, clear=True)  # patch environment variables before importing handler
    from src.sensor_lambda.main import main

    response = main(event)
    body = json.loads(response.get("body"))
    temperature = body.pop("temperature")  # do not assert exact quality on temperature  # noqa

    assert response["status_code"] == expected_status_code
    assert body == expected_response
