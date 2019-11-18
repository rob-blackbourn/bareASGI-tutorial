"""The server"""

import asyncio
import logging
import sys
from typing import Any, Dict, Optional

from bareasgi import Application
from hypercorn.asyncio import serve
from hypercorn.config import Config
import pkg_resources
import yaml

from bareasgi_blog.app import create_application


def load_config(filename: str) -> Dict[str, Any]:
    """Load the configuration from a yaml file.

    :param filename: The path of the yaml file.
    :type filename: str
    :return: A dictionary of the configuration.
    :rtype: Dict[str, Any]
    """
    with open(filename, 'rt') as file_ptr:
        return yaml.load(file_ptr, Loader=yaml.FullLoader)


def initialise_logging(config: Optional[Dict[str, Any]]) -> None:
    """Optionally initialise the logging.

    The logging section is optional, so check that it exists.

    :param config: The logging configuration.
    :type config: Optional[Dict[str, Any]]
    """
    if config is not None:
        logging.config.dictConfig(config)


def start_http_server(app: Application, config: Dict[str, Any]) -> None:
    """Start the HTTP server given the ASGI application and some config.

    :param app: The ASGI application.
    :type app: Application
    :param config: A dictionary of configuration.
    :type config: Dict[str, Any]
    """
    http_config = Config()
    http_config.bind = [f"{config['host']}:{config['port']}"]
    asyncio.run(serve(app, http_config))


def start_server() -> None:
    """Start the server.

    If this was started from the command line the path of the config file may
    be passed as the first parameter. Otherwise we take the default config file
    from the package.
    """
    filename = (
        sys.argv[1] if len(sys.argv) == 2 else
        pkg_resources.resource_filename(__name__, "config.yml")
    )
    config = load_config(filename)

    initialise_logging(config.get('logging'))
    app = create_application(config)
    start_http_server(app, config['app'])


if __name__ == '__main__':
    start_server()
