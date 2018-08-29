import os

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))
KLOYSTER_SALT = os.environ.get('KLOYSTER_SALT', 'YOU_SHOULD_CHANGE_THIS')

WEBS_DIR = 'webs'
