import dataclasses
import enum

import boto3


@dataclasses.dataclass
class Context:
    env: str
    aws_region: str
    sensor_registry_table: str
    sns_topic_arn: str
    sqs_url: str
    dynamo_db_client: "boto3.client.dynamodb"
    sqs_client: "boto3.client.sqs"

    @classmethod
    def from_dict(cls, env: dict):
        aws_profile = env["AWS_PROFILE_NAME"]
        aws_region = env["AWS_REGION"]
        session = boto3.Session(profile_name=aws_profile, region_name=aws_region)

        return cls(
            env=env["ENV"],
            aws_region=aws_region,
            sensor_registry_table=env["SENSOR_REGISTRY_TABLE"],
            sns_topic_arn=env["SNS_TOPIC_ARN"],
            sqs_url=env["SQS_URL"],
            dynamo_db_client=session.client("dynamodb", region_name=aws_region),
            sqs_client=session.client("sqs", region_name=aws_region),
        )


class SensorStatus(enum.Enum):
    OK: str = "OK"
    TEMPERATURE_TOO_LOW: str = "TEMPERATURE_TOO_LOW"
    TEMPERATURE_TOO_HIGH: str = "TEMPERATURE_TOO_HIGH"
    TEMPERATURE_CRITICAL: str = "TEMPERATURE_CRITICAL"
