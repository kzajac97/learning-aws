import sys
import awswrangler as wr
import pandas as pd
import pytest

from src.reporter_lambda.main import handler


@pytest.fixture(scope="function")
def source_root():
    sys.path.append("src/reporter_lambda")
    yield
    sys.path.remove("src/reporter_lambda")


@pytest.mark.parametrize(
    ["event", "expected"],
    (
        # test case with 1 record
        (
            {
                "batch": [
                    {"temperature": 100, "timestamp": "2025-01-01 00:12:00"},
                ],
                "source": "EVENT",
            },
            {"2025-01-01T00:12:00": 100},
        ),
        # test case with 3 records
        (
            {
                "batch": [
                    {"temperature": 100, "timestamp": "2025-01-01 00:12:00"},
                    {"temperature": 50, "timestamp": "2025-01-01 00:12:00"},
                    {"temperature": 150, "timestamp": "2025-01-01 00:12:00"},
                ],
                "source": "EVENT",
            },
            {"2025-01-01T00:12:00": 100},
        ),
        # test case with 2 records in different minutes
        (
            {
                "batch": [
                    {"temperature": 100, "timestamp": "2025-01-01 00:12:00"},
                    {"temperature": 50, "timestamp": "2025-01-01 00:13:00"},
                ],
                "source": "EVENT",
            },
            {"2025-01-01T00:12:00": 100, "2025-01-01T00:13:00": 50},
        ),
    ),
)
def test_reporter_lambda_handler_from_event(event: dict, expected: dict, lambda_context):
    response = handler(event, lambda_context)
    assert response == expected


@pytest.mark.parametrize(
    ["event", "key", "expected"],
    (
        # test case with 1 record
        (
            {
                "batch": [
                    {"temperature": 100, "timestamp": "2025-01-01 00:12:00"},
                ],
                "source": "S3",
            },
            "s3://test-sfn-payload-bucket/test.csv",
            {"2025-01-01T00:12:00": 100},
        ),
        # test case with 3 records
        (
            {
                "batch": [
                    {"temperature": 100, "timestamp": "2025-01-01 00:12:00"},
                    {"temperature": 50, "timestamp": "2025-01-01 00:12:00"},
                    {"temperature": 150, "timestamp": "2025-01-01 00:12:00"},
                ],
                "source": "S3",
            },
            "s3://test-sfn-payload-bucket/test.csv",
            {"2025-01-01T00:12:00": 100},
        ),
        # test case with 2 records in different minutes
        (
            {
                "batch": [
                    {"temperature": 100, "timestamp": "2025-01-01 00:12:00"},
                    {"temperature": 50, "timestamp": "2025-01-01 00:13:00"},
                ],
                "source": "S3",
            },
            "s3://test-sfn-payload-bucket/test.csv",
            {"2025-01-01T00:12:00": 100, "2025-01-01T00:13:00": 50},
        ),
    ),
)
def test_reporter_lambda_handler_from_s3(event: dict, key: str, expected: dict, lambda_context, mocked_s3, source_root):
    data = event.pop("batch")
    event["batch"] = key
    wr.s3.to_csv(pd.DataFrame(data), key, index=False)

    response = handler(event, lambda_context)
    assert response == expected
