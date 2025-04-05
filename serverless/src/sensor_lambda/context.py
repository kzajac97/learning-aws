import dataclasses
import enum

import boto3


@dataclasses.dataclass
class Context:
    env: str
    region: str
    sensor_registry_table: str
    sns_topic_arn: str
    sqs_url: str
    dynamo_db_client: "boto3.client.dynamodb"
    sqs_client: "boto3.client.sqs"

    @classmethod
    def from_dict(cls, env: dict):
        region = env["AWS_REGION"]

        return cls(
            env=env["ENV"],
            region=region,
            sensor_registry_table=env["SENSOR_REGISTRY_TABLE"],
            sns_topic_arn=env["SNS_TOPIC_ARN"],
            sqs_url=env["SQS_URL"],
            dynamo_db_client=boto3.client("dynamodb", region_name=region),
            sqs_client=boto3.client("sqs", region_name=region),
        )


class SensorStatus(enum.Enum):
    OK: str = "OK"
    TEMPERATURE_TOO_LOW: str = "TEMPERATURE_TOO_LOW"
    TEMPERATURE_TOO_HIGH: str = "TEMPERATURE_TOO_HIGH"
    TEMPERATURE_CRITICAL: str = "TEMPERATURE_CRITICAL"
