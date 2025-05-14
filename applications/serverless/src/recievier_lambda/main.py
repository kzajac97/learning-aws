import enum
import json
import logging
import os

import awswrangler as wr
import pandas as pd
from context import Context
from logger import setup_logging

setup_logging()
context = Context.from_dict(os.environ)

MAX_PAYLOAD_SIZE = 262144  # 256 KB -> hard limit from Step Functions
BUFFER = int(0.1 * MAX_PAYLOAD_SIZE)  # 10% buffer to be safe


class Source(enum.Enum):
    s3: str = "S3"
    sqs: str = "SQS"
    event: str = "EVENT"


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
            messages.append(json.loads(message["Body"]))
            context.sqs_client.delete_message(QueueUrl=context.sqs_url, ReceiptHandle=message["ReceiptHandle"])
        if len(response["Messages"]) < 10:
            break

    return messages


def handler(event, _):
    if event["source"] == Source.s3.value:
        logging.info("Received event from S3")
        data = wr.s3.read_csv(f"s3://{context.input_bucket}/{event['key']}")

    elif event["source"] == Source.sqs.value:
        messages = receive_message(context)
        logging.info(f"Received {len(messages)} messages from SQS")
        data = pd.DataFrame(messages)
    else:
        logging.error(f"Unknown source: {event['source']}")
        raise RuntimeError(f"Unknown source: {event['source']}")

    if data.empty:
        logging.warning(f"Did not receive any data from {event['source']}")
        return {"status_code": 204}

    grouped = data.groupby("location_id")

    batches = [group[["temperature", "timestamp"]] for _, group in grouped]
    logging.info(f"Created {len(batches)} batches")

    json_batches = [batch.to_dict("records") for batch in batches]
    payload = {
        "status_code": 200,
        "source": Source.event.value,
        "batches": json_batches,
    }
    payload_size = len(json.dumps(payload).encode("utf-8"))

    if payload_size > (MAX_PAYLOAD_SIZE - BUFFER):
        s3_keys = []
        for index, batch in enumerate(batches):  # write batches to S3, each as CSV file
            path = f"s3://{context.payload_bucket}/batch-{index}.csv"
            wr.s3.to_csv(batch, path)
            s3_keys.append(path)

        payload = {"status_code": 200, "batches": s3_keys, "source": Source.s3.value}

    return payload
