import dataclasses
from typing import Any, Self

import boto3


@dataclasses.dataclass
class Context:
    sqs_url: str
    input_bucket: str
    payload_bucket: str

    sqs_client: Any
    s3_client: Any

    @classmethod
    def from_dict(cls, env: dict) -> Self:
        return cls(
            sqs_url=env["SQS_URL"],
            input_bucket=env["INPUT_BUCKET"],
            payload_bucket=env["PAYLOAD_BUCKET"],
            sqs_client=boto3.client("sqs"),
            s3_client=boto3.client("s3"),
        )
