import json
import math
import os
import random
import time

import boto3
import click
import pandas as pd
import yaml


def invoke_lambda(payload: dict, client) -> dict:
    try:
        raw_response = client.invoke(
            FunctionName="sensor-lambda",
            InvocationType="RequestResponse",
            Payload=json.dumps(payload).encode("utf-8"),
        )

        response_payload = raw_response["Payload"].read().decode("utf-8")
        response = json.loads(response_payload)

        status_code = response.get("status_code")
        if status_code in (200, 204):
            return response["body"]

        print(f"Got unexpected status: {status_code}!")
        raise RuntimeError(response)

    except Exception as e:
        print(f"Error invoking Lambda: {e}")
        raise e


@click.command()
@click.option(
    "--config",
    required=True,
    help="Number of locations to trigger",
    type=click.Path(exists=True),
)
@click.option(
    "--dump",
    required=False,
    type=click.Path(),
    default=None,
    help="Path to CSV with data dump",
)
def main(config: str, dump: bool):
    session = boto3.Session(profile_name=os.environ["AWS_PROFILE_NAME"], region_name="us-east-1")
    client = session.client("lambda")

    with open(config, "r") as f:
        config = yaml.safe_load(f)

    max_requests = math.ceil(config["timer"]["total_runtime_seconds"] / config["timer"]["min_delay_seconds"])
    data_dump = []

    start = time.time()
    for n in range(max_requests):
        elapsed = time.time() - start
        if elapsed > config["timer"]["total_runtime_seconds"]:
            print(f"Exit loop after {config['timer']['total_runtime_seconds']} seconds")
            break

        location_id = random.choice(list(range(config["meta"]["locations"])))
        sensor_id = random.choice(list(range(config["meta"]["sensors"])))
        payload = {
            "sensor_id": location_id * config["meta"]["sensors"] + sensor_id,  # unique sensor for each location
            "location_id": location_id,
            "value": random.uniform(20, 250),
        }

        response = invoke_lambda(payload, client=client)
        print(response)
        if dump:
            response.update({"n": n})
            data_dump.append(response)

        interval = random.uniform(config["timer"]["min_delay_seconds"], config["timer"]["min_delay_seconds"])
        time.sleep(interval)
    else:
        print(f"Exiting after {max_requests} triggers")

    if dump:
        pd.DataFrame(data_dump).to_csv(dump)


if __name__ == "__main__":
    main()
