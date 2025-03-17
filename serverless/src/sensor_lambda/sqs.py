import json
from datetime import datetime as dt

from context import Context

from serverless.src.sensor_lambda.context import SensorStatus


def send_message(context: Context, sensor_id: str, temperature: float, status: SensorStatus):
    message = {
        "sensor_id": sensor_id,
        "temperature": temperature,
        "status": status.value,
        "timestamp": dt.now().isoformat(),
    }

    context.sqs_client.send_message(QueueUrl=context.sqs_queue_url, MessageBody=json.dumps(message))
