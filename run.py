from config import read_config
from pir import pir_detector

def main():
    """
    Application entrypoint.
    """
    config = read_config()
    pir_detector(config)

if __name__ == '__main__':
    main()
