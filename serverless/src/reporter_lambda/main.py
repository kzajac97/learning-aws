import enum
import logging

import awswrangler as wr
import pandas as pd
from logger import setup_logging

setup_logging()


def event_to_message(event: dict) -> dict:
    """Make event readable in logs (remove the very long values under batch key)"""
    return {k: v for k, v in event.items() if k != "batch"}


class Source(enum.Enum):
    s3: str = "S3"
    event: str = "EVENT"


def handler(event: dict, _):
    logging.info(f"Received event from {event_to_message(event)}")

    if event["source"] == Source.s3.value:
        data = wr.s3.read_csv(event["batch"])
    elif event["source"] == Source.event.value:
        data = pd.DataFrame(event["batch"])
    else:
        raise ValueError(f"Can't parse from event {event_to_message(event)}!")

    data["timestamp"] = data["timestamp"].apply(pd.Timestamp)
    minutes = data.groupby(data["timestamp"].dt.floor("min"))["temperature"].mean()

    start_time = minutes.index.min()
    end_time = minutes.index.max()

    full_range = pd.date_range(start=start_time, end=end_time, freq="min")
    minutes = minutes.reindex(full_range, fill_value=0)

    minutes.index = minutes.index.map(lambda timestamp: timestamp.isoformat())
    minutes = minutes.apply(lambda temperature: round(temperature, 2))

    return minutes.to_dict()
