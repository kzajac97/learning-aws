import logging


def setup_logging():
    if logging.getLogger().hasHandlers():
        # AWS Lambda by default hasHandlers -> override it with simple INFO logger
        logging.getLogger().setLevel(logging.INFO)
    else:
        # locally, set to DEBUG
        logging.basicConfig(level=logging.DEBUG)
