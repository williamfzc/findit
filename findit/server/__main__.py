from findit.server.server import app
import findit.server.config as config


if __name__ == '__main__':
    import argparse
    import os

    # TODO load from env?
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help="port number")
    parser.add_argument('-d', '--dir', help="pictures root directory", required=True)
    args = parser.parse_args()

    # init pic dir
    config.PIC_DIR_PATH = args.dir
    assert os.path.exists(config.PIC_DIR_PATH), 'dir path not existed'

    # save port
    config.SERVER_PORT = int(args.port or 9410)

    app.run(
        host='0.0.0.0',
        port=config.SERVER_PORT,
    )
