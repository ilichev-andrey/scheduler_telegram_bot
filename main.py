import json
import logging
import os
import sys

from wrappers import logger

from bot import configs
from bot.application import Application

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


def main():
    if not os.path.isfile(CONFIG_FILE):
        sys.stderr.write(f'File "{CONFIG_FILE}" - missing')
        exit(1)

    with open(CONFIG_FILE) as fin:
        config = json.load(fin)

    try:
        config = configs.load_config(config)
    except KeyError as e:
        sys.stderr.write(f'Parameter {str(e)} is missing in the file, see "default_config.json"')
        exit(1)

    logger.create(config.log_file, logging.INFO)

    app = Application(config, os.getenv('TELEGRAM_API_TOKEN'))
    app.init()
    app.run()


if __name__ == '__main__':
    main()
