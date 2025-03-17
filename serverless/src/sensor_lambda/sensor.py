import math
from typing import Final

from context import SensorStatus

# constants for the Steinhart-Hart equation
A: Final[float] = 0.001129148
B: Final[float] = 0.000234125
C: Final[float] = 0.0000000876741
MIN_R: Final[float] = float(1)
MAX_R: Final[float] = float(20_000)


def compute_temperature(r: float) -> float:
    """
    Compute the temperature in Kelvin using the Steinhart-Hart equation.
    For reference, see: https://en.wikipedia.org/wiki/Steinhart%E2%80%93Hart_equation
    """
    log_r = math.log(r)
    kelvins = 1 / (A + B * math.log(r) + C * math.pow(log_r, 3))
    return kelvins - 273.15


def is_in_range(r: float) -> bool:
    return MIN_R <= r <= MAX_R


def get_status(temperature: float) -> SensorStatus:
    if temperature < 20:
        return SensorStatus.TEMPERATURE_TOO_LOW
    elif temperature < 100:
        return SensorStatus.OK
    elif temperature < 250:
        return SensorStatus.TEMPERATURE_TOO_HIGH

    return SensorStatus.TEMPERATURE_CRITICAL
