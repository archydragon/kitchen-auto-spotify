import os
import yaml
from cerberus import Validator


CONFIG_ROOT = os.path.expanduser("~/.config/kitchen")
CONFIG = os.path.join(CONFIG_ROOT, "config.yml")

CONFIG_SCHEMA = {
    'pir_pin':          {'type': 'number', 'required': True},
    'client_id':        {'type': 'string', 'required': True},
    'client_secret':    {'type': 'string', 'required': True},
    'device_name':      {'type': 'string', 'required': True},
    'presence_delay':   {'type': 'number', 'default': 60},
    'inactivity_delay': {'type': 'number', 'default': 600},
    'country':          {'type': 'string', 'nullable': True, 'default': None},
    'shuffle':          {'type': 'boolean', 'default': False},
    'volume':           {'type': 'number', 'default': 100},
    'night_starts':     {'type': 'string', 'required': False, 'regex': '^[0-2]?\d:[0-5]\d$', 'nullable': True},
    'night_ends':       {'type': 'string', 'required': False, 'regex': '^[0-2]?\d:[0-5]\d$', 'nullable': True},
}


def read_config():
    """
    Parse YAML config from the file.
    """
    config = None
    # If the file is absent, FileNotFoundError exception will be thrown.
    with open(CONFIG, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    # Validate config.
    v = Validator(allow_unknown=True)
    if not v.validate(config, CONFIG_SCHEMA):
        raise Exception(f"Config validation failed: {v.errors}")
    return v.normalized(config)
