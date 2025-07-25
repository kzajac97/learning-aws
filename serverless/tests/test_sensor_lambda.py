import os
import json
from typing import Any

import freezegun
import pytest

from tests import settings


def prepare_dynamodb(dynamodb, table_name: str, content: list[dict]):
    """Prepare the mocked sensor_registry DynamoDB table with the given content."""
    if not content:
        return  # empty DynamoDB table

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


def assert_sqs(sqs, expected_messages: list[dict] | None):
    """Assert that the mocked SQS queue contains the expected messages."""
    if not expected_messages:
        return  # no messages expected

    client, queue_url = sqs
    messages = client.receive_message(QueueUrl=queue_url)

    for message, expected in zip(messages["Messages"], expected_messages):
        message_body = json.loads(message.get("Body", "{}"))
        message_body.pop("temperature")  # do not assert exact quality on temperature
        assert message_body == expected  # check message content one by one


@pytest.fixture(scope="function")
def mock_env(mocked_dynamodb, mocked_sns, mocked_sqs):
    _, queue_url = mocked_sqs
    _, topic_arn = mocked_sns

    return {
        "ENV": "test",
        "SENSOR_REGISTRY_TABLE": settings.SENSOR_REGISTRY_TABLE,
        "AWS_REGION": settings.TEST_AWS_REGION,
        "AWS_DEFAULT_REGION": settings.TEST_AWS_REGION,  # for boto3 compatibility
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
        "expected_sqs_messages",
    ],
    (
        # test case 1: temperature in range with new sensor
        (
            {"sensor_id": "1", "location_id": "A", "value": 2000},  # event
            None,  # empty dynamodb_content
            200,
            {"sensor_id": "1", "location_id": "A", "status": "OK", "timestamp": settings.TIME},
            [{"sensor_id": {"S": "1"}, "working_ok": {"BOOL": True}}],  # expected_dynamodb_content
            [{"sensor_id": "1", "location_id": "A", "status": "OK", "timestamp": "2025-01-01T00:00:00"}],  # sqs
        ),
        # test case 2: temperature in range with existing sensor
        (
            {"sensor_id": "2", "location_id": "A", "value": 1500},  # event
            [{"sensor_id": "2", "working_ok": True}],  # dynamodb_content
            200,
            {"sensor_id": "2", "location_id": "A", "status": "OK", "timestamp": settings.TIME},
            [{"sensor_id": {"S": "2"}, "working_ok": {"BOOL": True}}],  # expected_dynamodb_content
            [{"sensor_id": "2", "location_id": "A", "status": "OK", "timestamp": "2025-01-01T00:00:00"}],  # sqs
        ),
        # test case 3: temperature in range with broken sensor
        (
            {"sensor_id": "3", "location_id": "A", "value": 1800},  # event
            [{"sensor_id": "3", "working_ok": False}],  # dynamodb_content
            204,
            {},  # no response body
            [{"sensor_id": {"S": "3"}, "working_ok": {"BOOL": False}}],  # expected_dynamodb_content
            None,  # nothing in SQS -> sensor is broken
        ),
        # test case 4: temperature out of range with new sensor
        (
            {"sensor_id": "4", "location_id": "A", "value": 25_000},  # event
            None,  # empty dynamodb
            204,
            {},  # no response body
            [{"sensor_id": {"S": "4"}, "working_ok": {"BOOL": False}}],  # expected_dynamodb_content
            None,  # nothing is SQS -> sensor is broken
        ),
        # test case 5: temperature out of range with existing sensor
        (
            {"sensor_id": "5", "location_id": "A", "value": 25_000},  # event
            [{"sensor_id": "5", "working_ok": True}],  # dynamodb_content with existing sensor - initially working
            204,
            {},  # no response body
            # expected_dynamodb_content -> sensor is now marked as broken
            [{"sensor_id": {"S": "5"}, "working_ok": {"BOOL": False}}],
            None,  # nothing in SQS -> sensor is broken
        ),
        # test case 6: temperature too low with new sensor
        (
            {"sensor_id": "6", "location_id": "A", "value": 15_000},  # event
            None,  # empty dynamodb_content
            200,
            {"sensor_id": "6", "location_id": "A", "status": "TEMPERATURE_TOO_LOW", "timestamp": settings.TIME},
            [{"sensor_id": {"S": "6"}, "working_ok": {"BOOL": True}}],  # expected_dynamodb_content
            # sqs message
            [
                {
                    "sensor_id": "6",
                    "location_id": "A",
                    "status": "TEMPERATURE_TOO_LOW",
                    "timestamp": settings.TIME,
                }
            ],
        ),
        # test case 7: temperature too high with new sensor
        (
            {"sensor_id": "7", "location_id": "A", "value": 500},  # event
            None,  # empty dynamodb_content
            200,
            {
                "sensor_id": "7",
                "location_id": "A",
                "status": "TEMPERATURE_TOO_HIGH",
                "timestamp": settings.TIME,
            },
            [{"sensor_id": {"S": "7"}, "working_ok": {"BOOL": True}}],  # expected_dynamodb_content
            # sqs message
            [
                {
                    "sensor_id": "7",
                    "location_id": "A",
                    "status": "TEMPERATURE_TOO_HIGH",
                    "timestamp": settings.TIME,
                }
            ],
        ),
        # test case 8: temperature critical with new sensor
        (
            {"sensor_id": "8", "location_id": "A", "value": 10},  # event
            None,  # empty dynamodb_content
            200,
            {
                "sensor_id": "8",
                "location_id": "A",
                "status": "TEMPERATURE_CRITICAL",
                "timestamp": settings.TIME,
            },
            [{"sensor_id": {"S": "8"}, "working_ok": {"BOOL": True}}],  # expected_dynamodb_content
            # sqs message
            [
                {
                    "sensor_id": "8",
                    "location_id": "A",
                    "status": "TEMPERATURE_CRITICAL",
                    "timestamp": settings.TIME,
                }
            ],
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
    expected_sqs_messages: list[dict] | None,
    mock_env,
    mocked_s3,
    mocked_dynamodb,
    mocked_sns,
    mocked_sqs,
    mocker,
):
    mocker.patch.dict(os.environ, mock_env)  # patch environment variables before importing handler
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
    assert_sqs(mocked_sqs, expected_sqs_messages)
