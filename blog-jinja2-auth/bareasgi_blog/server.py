"""The server"""

import asyncio
import logging
import os.path
from typing import Any, Dict

from hypercorn.asyncio import serve
from hypercorn.config import Config
import pkg_resources
import yaml

from bareasgi_blog.app import create_application

def _load_config(filename: str) -> Dict[str, Any]:
    with open(filename, 'rt') as file_ptr:
        return yaml.load(file_ptr, Loader=yaml.FullLoader)

def _initialise_logging(config: Dict[str, Any]) -> None:
    if 'logging' in config:
        logging.config.dictConfig(config['logging'])

def start_server() -> None:
    """Start the server"""
    config = _load_config(pkg_resources.resource_filename(__name__, "config.yml"))

    app_config = config['app']
    host = app_config['host']
    port = app_config['port']
    certfile = os.path.expanduser(app_config['certfile'])
    keyfile = os.path.expanduser(app_config['keyfile'])

    _initialise_logging(config)
    app = create_application(config)
    http_config = Config()
    http_config.bind = [f"{host}:{port}"]
    http_config.certfile = certfile
    http_config.keyfile = keyfile

    asyncio.run(serve(app, http_config))


if __name__ == '__main__':
    start_server()
