import os

from sensor import Context


def notify(context: Context, message: str):
    context.sns.publish(
        TopicArn=os.getenv("SNS_TOPIC_ARN"),
        Message=message,
        Subject="AWS Lab Error Alert",
    )
