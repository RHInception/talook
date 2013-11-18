import sys
import os

sys.path.insert(0, '/path/to/talook/server/file/')

os.environ['TALOOK_CONFIG_FILE'] = '/path/to/talook/config.json'

from server import make_app

application = make_app()
