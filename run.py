import logging
from config import read_config
from pir import pir_detector

def setup_logger(debug_mode=False):
    level = logging.INFO
    formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s")
    if debug_mode:
        level = logging.DEBUG
        formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] [%(module)s.py] %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log = logging.getLogger('root')
    log.setLevel(level)
    log.addHandler(handler)
    return log

def main():
    """
    Application entrypoint.
    """
    config = read_config()
    log = setup_logger(debug_mode=config['debug_mode'])
    log.info("Starting application, press Ctrl+C to interrupt.")
    pir_detector(config)
    log.info('Terminated.')

if __name__ == '__main__':
    main()
