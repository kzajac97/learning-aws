import os
import json
import sys
from typing import Any

import freezegun
import pytest

from tests import settings


@pytest.fixture(scope="function")
def source_root():
    sys.path.append("src/sensor_lambda")
    yield
    sys.path.remove("src/sensor_lambda")


def prepare_dynamodb(dynamodb, table_name: str, content: list[dict]):
    """Prepare the mocked sensor_registry DynamoDB table with the given content."""
    for item in content:
        if content:
            pk = item.get("sensor_id")
            ok = item.get("working_ok")
            dynamodb.put_item(TableName=table_name, Item={"sensor_id": {"S": pk}, "working_ok": {"BOOL": ok}})


def assert_dynamodb(dynamodb, table_name: str, expected_content: list[dict]):
    """Assert that the mocked sensor_registry DynamoDB table contains the expected content."""
    items = []
    exclusive_start_key = None

    while True:
        scan_kwargs = {"TableName": table_name}
        if exclusive_start_key:
            scan_kwargs["ExclusiveStartKey"] = exclusive_start_key

        response = dynamodb.scan(**scan_kwargs)
        for item in response.get("Items", []):
            items.append(item)

        exclusive_start_key = response.get("LastEvaluatedKey")
        if not exclusive_start_key:
            break

    assert items == expected_content


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
        # test case 1: temperature in range with new sensor
        (
            {"sensor_id": "1", "location_id": "A", "value": 2000},  # event
            {},  # empty dynamodb_content
            200,
            {"sensor_id": "1", "location_id": "A", "status": "OK", "timestamp": settings.TIME},
            [{"sensor_id": {"S": "1"}, "working_ok": {"BOOL": True}}],  # expected_dynamodb_content
            [],  # expected_sns_messages
            [],  # expected_sqs_messages
        ),
        # test case 2: temperature in range with existing sensor
        (
            {"sensor_id": "2", "location_id": "A", "value": 1500},  # event
            [{"sensor_id": "2", "working_ok": True}],  # dynamodb_content
            200,
            {"sensor_id": "2", "location_id": "A", "status": "OK", "timestamp": settings.TIME},
            [{"sensor_id": {"S": "2"}, "working_ok": {"BOOL": True}}],  # expected_dynamodb_content
            [],  # expected_sns_messages
            [],  # expected_sqs_messages
        ),
        # test case 3: temperature in range with broken sensor
        (
            {"sensor_id": "3", "location_id": "A", "value": 1800},  # event
            [{"sensor_id": "3", "working_ok": False}],  # dynamodb_content
            204,
            {},  # no response body
            [{"sensor_id": {"S": "3"}, "working_ok": {"BOOL": False}}],  # expected_dynamodb_content
            [],  # expected_sns_messages
            [],  # expected_sqs_messages
        ),
        # test case 4: temperature out of range with new sensor
        (
            {"sensor_id": "4", "location_id": "A", "value": 25_000},  # event
            {},  # empty dynamodb
            204,
            {},  # no response body
            [{"sensor_id": {"S": "4"}, "working_ok": {"BOOL": False}}],  # expected_dynamodb_content
            [],  # expected_sns_messages
            [],  # expected_sqs_messages
        ),
        # test case 5: temperature out of range with existing sensor
        (
            {"sensor_id": "5", "location_id": "A", "value": 25_000},  # event
            [{"sensor_id": "5", "working_ok": True}],  # dynamodb_content with existing sensor - initially working
            204,
            {},  # no response body
            # expected_dynamodb_content -> sensor is now marked as broken
            [{"sensor_id": {"S": "5"}, "working_ok": {"BOOL": False}}],
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
    mocked_s3,
    mocked_dynamodb,
    mocked_sns,
    mocked_sqs,
    source_root,
    mocker,
):
    mocker.patch.dict(os.environ, mock_env, clear=True)  # patch environment variables before importing handler
    prepare_dynamodb(mocked_dynamodb, settings.SENSOR_REGISTRY_TABLE, dynamodb_content)

    from src.sensor_lambda.main import main

    response = main(event)

    body = json.loads(response.get("body", "{}"))

    if body:
        temperature = body.pop("temperature")  # do not assert exact quality on temperature  # noqa

    assert response["status_code"] == expected_status_code
    assert body == expected_response
    # assert AWS resources behave as expected
    assert_dynamodb(mocked_dynamodb, settings.SENSOR_REGISTRY_TABLE, expected_dynamodb_content)
