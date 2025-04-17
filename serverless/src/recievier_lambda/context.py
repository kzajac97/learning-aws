import dataclasses
from typing import Any, Self

import boto3


@dataclasses.dataclass
class Context:
    sqs_url: str
    input_bucket: str
    payload_bucket: str

    aws_profile: str
    aws_region: str

    sqs_client: Any
    s3_client: Any

    @classmethod
    def from_dict(cls, env: dict) -> Self:
        aws_profile = env["AWS_PROFILE_NAME"]
        aws_region = env["AWS_REGION"]
        session = boto3.Session(profile_name=aws_profile, region_name=aws_region)

        return cls(
            sqs_url=env["SQS_URL"],
            input_bucket=env["INPUT_BUCKET"],
            payload_bucket=env["PAYLOAD_BUCKET"],
            aws_profile=aws_profile,
            aws_region=aws_region,
            sqs_client=session.client("sqs"),
            s3_client=session.client("s3"),
        )
