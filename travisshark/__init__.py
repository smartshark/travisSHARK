import logging
import logging.config
import os
import json


def setup_logging(default_path=os.path.dirname(os.path.realpath(__file__)) + "/../loggerConfiguration.json",
                  default_level=logging.INFO):
    """
    Setup logging configuration

    :param default_path: path to the logger configuration
    :param default_level: defines the default logging level if configuration file is not found (default: logging.INFO)
    """
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

setup_logging()
