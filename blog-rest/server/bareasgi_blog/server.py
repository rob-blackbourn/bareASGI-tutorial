"""The server"""

import asyncio
import logging
import signal
from typing import Any, Dict

from hypercorn.asyncio import serve
from hypercorn.config import Config
import pkg_resources
import yaml

from bareasgi import Application

from bareasgi_blog.app import create_application

def _load_config(filename: str) -> Dict[str, Any]:
    with open(filename, 'rt') as file_ptr:
        return yaml.load(file_ptr, Loader=yaml.FullLoader)

def _initialise_logging(config: Dict[str, Any]) -> None:
    if 'logging' in config:
        logging.config.dictConfig(config['logging'])

def start_hypercorn(app: Application, app_config: Dict[str, Any]) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    shutdown_event = asyncio.Event()

    def _signal_handler(*_):
        shutdown_event.set()
    loop.add_signal_handler(signal.SIGTERM, _signal_handler)
    loop.add_signal_handler(signal.SIGINT, _signal_handler)

    host = app_config['host']
    port = app_config['port']

    config = Config()
    config.bind = [f"{host}:{port}"]
    config.loglevel = 'debug'
    # config.certfile = os.path.expanduser(f"~/.keys/server.crt") if USE_SSL else None
    # config.keyfile = os.path.expanduser(f"~/.keys/server.key") if USE_SSL else None

    loop.run_until_complete(
        serve(
            app,
            config,
            shutdown_trigger=shutdown_event.wait  # type: ignore
        )
    )

def start_server() -> None:
    """Start the server"""
    config = _load_config(pkg_resources.resource_filename(__name__, "config.yml"))

    app_config = config['app']
    path_prefix = app_config['path_prefix']
    _initialise_logging(config)
    app = create_application(path_prefix)
    start_hypercorn(app, app_config)


if __name__ == '__main__':
    start_server()
