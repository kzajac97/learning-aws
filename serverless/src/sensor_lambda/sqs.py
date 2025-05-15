import json
from datetime import datetime as dt

from context import Context, SensorStatus


def send_message(
    context: Context,
    sensor_id: str,
    location_id: str,
    temperature: float,
    status: SensorStatus,
):
    message = {
        "sensor_id": sensor_id,
        "location_id": location_id,
        "temperature": temperature,
        "status": status.value,
        "timestamp": dt.now().isoformat(),
    }

    context.sqs_client.send_message(QueueUrl=context.sqs_url, MessageBody=json.dumps(message))
