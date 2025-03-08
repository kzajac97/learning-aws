import os

import boto3


def notify(message: str):
    client = boto3.client("sns")
    client.publish(
        TopicArn=os.getenv("SNS_ARN"),
        Message=message,
        Subject="AWS Lab Error Alert",
    )
