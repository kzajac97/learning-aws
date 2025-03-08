import json
import logging
import math
from typing import Final

from sns import notify

# constants for the Steinhart-Hart equation
A: Final[float] = 0.001129148
B: Final[float] = 0.000234125
C: Final[float] = 0.0000000876741
MIN_R: Final[float] = float(1)
MAX_R: Final[float] = float(20_000)

logging.basicConfig(level=logging.INFO)


def to_celcius(temperature_in_kelvin: float) -> float:
    return temperature_in_kelvin - 273.15


def compute_temperature(r: float) -> float:
    """
    Compute the temperature in Kelvin using the Steinhart-Hart equation.
    For reference, see: https://en.wikipedia.org/wiki/Steinhart%E2%80%93Hart_equation
    """
    log_r = math.log(r)
    return 1 / (A + B * math.log(r) + C * math.pow(log_r, 3))


def compose_response(sensor_id: str, temperature: float, status: str) -> dict:
    return {
        "status_code": 200,
        "body": json.dumps({"sensor_id": sensor_id, "temperature": temperature, "status": status}),
    }


def lambda_handler(event, _):
    logging.info(f"Received event: {event}")
    try:
        sensor_id = str(event["sensor_id"])
        r = float(event["value"])

        if MIN_R > r or r > MAX_R:
            # TODO: Store sensor as broken and notify the user
            ...

        temperature = compute_temperature(r)
        temperature = to_celcius(temperature)

        if temperature < 20:
            return compose_response(sensor_id, temperature, status="TEMPERATURE_TOO_LOW")
        elif temperature < 100:
            return compose_response(sensor_id, temperature, status="OK")
        elif temperature < 250:
            return compose_response(sensor_id, temperature, status="TEMPERATURE_TOO_HIGH")

        return compose_response(sensor_id, temperature, status="TEMPERATURE_CRITICAL")

    except (KeyError, TypeError) as e:
        notify(message=f"Error processing event: {e}!")

        logging.error(f"Error processing event: {e}!")
        return {"status_code": 400, "body": json.dumps({"error": "INVALID_REQUEST"})}
