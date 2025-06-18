import dataclasses
from typing import Any, Self

import boto3


@dataclasses.dataclass
class Context:
    sqs_url: str
    input_bucket: str
    payload_bucket: str

    aws_region: str

    sqs_client: Any
    s3_client: Any

    @classmethod
    def from_dict(cls, env: dict) -> Self:
        aws_region = env["AWS_REGION"]

        return cls(
            sqs_url=env["SQS_URL"],
            input_bucket=env["INPUT_BUCKET"],
            payload_bucket=env["PAYLOAD_BUCKET"],
            aws_region=aws_region,
            sqs_client=boto3.client("sqs", region_name=aws_region),
            s3_client=boto3.client("s3", region_name=aws_region),
        )
