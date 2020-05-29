# -*- coding: utf-8 -*-

import os
import importlib
from a4kSubtitles import api, service

if __name__ == '__main__':
    os.environ.pop(api.api_mode_env_name, '')
    core = importlib.import_module('a4kSubtitles.core')
    service.start(core)
