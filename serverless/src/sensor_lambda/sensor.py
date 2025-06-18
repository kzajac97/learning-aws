import math
from typing import Final

import dataclasses
import enum

import boto3

# constants for the Steinhart-Hart equation
A: Final[float] = 0.001129148
B: Final[float] = 0.000234125
C: Final[float] = 0.0000000876741
MIN_R: Final[float] = float(1)
MAX_R: Final[float] = float(20_000)


class SensorStatus(enum.Enum):
    OK = "OK"
    TEMPERATURE_TOO_LOW = "TEMPERATURE_TOO_LOW"
    TEMPERATURE_TOO_HIGH = "TEMPERATURE_TOO_HIGH"
    TEMPERATURE_CRITICAL = "TEMPERATURE_CRITICAL"


def compute_temperature(r: float) -> float:
    """
    Compute the temperature in Kelvin using the Steinhart-Hart equation.
    For reference, see: https://en.wikipedia.org/wiki/Steinhart%E2%80%93Hart_equation
    """
    log_r = math.log(r)
    kelvins = 1 / (A + B * math.log(r) + C * math.pow(log_r, 3))
    return kelvins - 273.15


def is_in_range(r: float) -> bool:
    return MIN_R <= r <= MAX_R


def get_status(temperature: float) -> SensorStatus:
    if temperature < 20:
        return SensorStatus.TEMPERATURE_TOO_LOW
    elif temperature < 100:
        return SensorStatus.OK
    elif temperature < 250:
        return SensorStatus.TEMPERATURE_TOO_HIGH

    return SensorStatus.TEMPERATURE_CRITICAL


@dataclasses.dataclass
class Context:
    env: str
    aws_region: str
    sensor_registry_table: str
    sns_topic_arn: str
    sqs_url: str
    idempotency_table: str
    dynamodb: "boto3.client.dynamodb"
    sns: "boto3.client.sns"
    sqs: "boto3.client.sqs"

    @classmethod
    def from_dict(cls, env: dict):
        aws_region = env["AWS_REGION"]

        return cls(
            env=env["ENV"],
            aws_region=aws_region,
            sensor_registry_table=env["SENSOR_REGISTRY_TABLE"],
            sns_topic_arn=env["SNS_TOPIC_ARN"],
            sqs_url=env["SQS_URL"],
            idempotency_table=env["LAMBDA_IDEMPOTENCY_TABLE"],
            dynamodb=boto3.client("dynamodb", region_name=aws_region),
            sns=boto3.client("sns", region_name=aws_region),
            sqs=boto3.client("sqs", region_name=aws_region),
        )
