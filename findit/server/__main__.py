from findit.server.router import app
from findit.logger import logger
from findit.server import config

import argparse
import os


def start_server():
    logger.info(f'server port: {config.SERVER_PORT}')
    logger.info(f'pic root dir path: {config.PIC_DIR_PATH}')

    # check existed
    assert os.path.exists(config.PIC_DIR_PATH), f'dir path not existed: {config.PIC_DIR_PATH}'

    from gevent import monkey, pywsgi
    monkey.patch_all()
    server = pywsgi.WSGIServer(
        ('0.0.0.0', int(config.SERVER_PORT)),
        app,
    )
    server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help="port number")
    parser.add_argument('-d', '--dir', help="pictures root directory")
    args = parser.parse_args()

    config.SERVER_PORT = args.port or config.SERVER_PORT
    config.PIC_DIR_PATH = args.dir or config.PIC_DIR_PATH

    # should not be empty
    assert config.SERVER_PORT, 'no port configured, eg: --port 9410'
    assert config.PIC_DIR_PATH, 'no path root configured, eg: --dir path/to/your/pic/dir'

    # start server
    start_server()
