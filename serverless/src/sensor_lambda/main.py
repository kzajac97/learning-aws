import json
import logging
import os
from datetime import datetime as dt

import dynamodb
import sensor
import sns
import sqs
from context import Context

logging.basicConfig(level=logging.INFO)
context = Context.from_dict(os.environ)


def lambda_handler(event, _):
    logging.info(f"Received event: {event}")
    sensor_registry = dynamodb.SensorRegistryClient(context.dynamo_db_client, table_name=context.sensor_registry_table)

    try:
        sensor_id = str(event["sensor_id"])
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
        sqs.send_message(context, sensor_id, temperature, status)

        return {
            "status_code": 200,
            "body": json.dumps(
                {
                    "sensor_id": sensor_id,
                    "temperature": temperature,
                    "status": status,
                    "timestamp": dt.now().isoformat(),
                }
            ),
        }

    except (KeyError, TypeError) as e:
        sns.notify(message=f"Error processing event: {e}!")

        logging.error(f"Error processing event: {e}!")
        return {"status_code": 400, "body": json.dumps({"error": "INVALID_REQUEST"})}
