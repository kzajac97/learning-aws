import os
import logging
import itertools

import pandas as pd

from context import Context
from logger import setup_logging

setup_logging()
context = Context.from_dict(os.environ)


def batched(iterable, n: int):
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            break
        yield batch


def receive_message(context: Context) -> list:
    messages = []
    while True:
        response = context.sqs_client.receive_message(
            QueueUrl=context.sqs_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=0,
        )

        if "Messages" not in response:
            break
        for message in response["Messages"]:
            messages.append(message)
            context.sqs_client.delete_message(QueueUrl=context.sqs_url, ReceiptHandle=message["ReceiptHandle"])
        if len(response["Messages"]) < 10:
            break

    return messages


def lambda_handler(event, _):
    messages = receive_message(context)
    logging.info(f"Received {len(messages)} messages from SQS")

    data = pd.DataFrame(messages)
    grouped = data.groupby("location_id")

    batches = []
    for location_id, group in grouped:
        group = group[["temperature", "timestamp"]].to_dict("records")
        batches.extend(batched(group, n=context.max_batch_size))

    logging.info(f"Created {len(batches)} batches")
    return {"status_code": 200, "batches": batches}
