import dataclasses
from typing import Any, Self

import boto3


@dataclasses.dataclass
class Context:
    sqs_url: str
    bucket_name: str
    max_batch_size: int

    sqs_client: Any

    @classmethod
    def from_dict(cls, env: dict) -> Self:
        return cls(
            sqs_url=env["SQS_URL"],
            bucket_name=env["BUCKET_NAME"],
            max_batch_size=int(env["MAX_BATCH_SIZE"]),
            sqs_client=boto3.client("sqs"),
        )
