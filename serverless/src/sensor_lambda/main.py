import json
import os
from datetime import datetime as dt

import dynamodb
import sensor
import sns
import sqs
from context import Context
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.idempotency import DynamoDBPersistenceLayer, idempotent


logger = Logger("sensor_lambda")
context = Context.from_dict(dict(os.environ))
persistence_store = DynamoDBPersistenceLayer(table_name=context.idempotency_table)


@logger.inject_lambda_context(log_event=True)
@idempotent(persistence_store=persistence_store)
def handler(event, _):
    main(event)


def main(event: dict):
    """
    Main logic of the Lambda handler, unwrapped from the AWS Lambda specific settings (idempotency, logger etc.)
    `context` is initialized on module initialization, to be reused between execution environments.
    """
    logger.info(f"Received event: {event}")
    sensor_registry = dynamodb.SensorRegistryClient(context.dynamo_db_client, table_name=context.sensor_registry_table)

    sensor_id = str(event["sensor_id"])
    location_id = str(event["location_id"])
    r = float(event["value"])

    if not sensor_registry.exists(sensor_id):
        # assume the sensor is working ok, when it is first registered
        sensor_registry.put_item(sensor_id, working_ok=True)

    if not sensor_registry.get_item(sensor_id).get("working_ok"):
        return {"status_code": 204}  # sensor is not working, ignore the event

    if not sensor.is_in_range(r):  # the current reading is out of range
        sensor_registry.update_item(sensor_id, working_ok=False)  # mark the sensor as not working
        return {"status_code": 204}

    temperature = sensor.compute_temperature(r)
    status = sensor.get_status(temperature)

    logger.info(f"Sensor {sensor_id} has temperature {temperature} and status {status.value} at {location_id}")
    logger.info("Forwarding message to SQS")
    sqs.send_message(context, sensor_id, location_id, temperature, status)

    if status == sensor.SensorStatus.TEMPERATURE_CRITICAL:
        alert = f"Sensor {sensor_id} is in critical state with temperature {temperature} at {location_id}!"
        sns.notify(message=alert)

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
