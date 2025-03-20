import json
import logging
import os
from datetime import datetime as dt

import dynamodb
import sensor
import sns
import sqs
from context import Context
from logger import setup_logging

setup_logging()
context = Context.from_dict(os.environ)


def lambda_handler(event, _):
    logging.info(f"Received event: {event}")
    sensor_registry = dynamodb.SensorRegistryClient(context.dynamo_db_client, table_name=context.sensor_registry_table)

    sensor_id = str(event["sensor_id"])
    location_id = str(event["location_id"])
    r = float(event["value"])

    if not sensor_registry.exists(sensor_id):
        # assume sensor is working ok, when it is first registered
        sensor_registry.put_item(sensor_id, working_ok=True)

    if not sensor_registry.get_item(sensor_id).get("working_ok"):
        return {"status_code": 204}  # sensor is not working, ignore the event

    if not sensor.is_in_range(r):  # current reading is out of range
        sensor_registry.update_item(sensor_id, working_ok=False)  # mark sensor as not working
        return {"status_code": 204}

    temperature = sensor.compute_temperature(r)
    status = sensor.get_status(temperature)

    logging.info(f"Sensor {sensor_id} has temperature {temperature} and status {status.value} at {location_id}")
    logging.info(f"Forwarding message to SQS")
    sqs.send_message(context, sensor_id, temperature, status)

    if status == sensor.SensorStatus.TEMPERATURE_CRITICAL:
        alert = f"Sensor {sensor_id} is in critical state with temperature {temperature} at {location_id}!"
        sns.notify(context, message=alert)

    return {
        "status_code": 200,
        "body": json.dumps(
            {
                "sensor_id": sensor_id,
                "location_id": location_id,
                "temperature": temperature,
                "status": status.value,
                "timestamp": dt.now().isoformat(),
            }
        ),
    }
