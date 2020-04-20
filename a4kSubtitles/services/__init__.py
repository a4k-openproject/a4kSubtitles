# -*- coding: utf-8 -*-

import importlib
from a4kSubtitles.lib import utils

__all__ = utils.get_all_relative_py_files(__file__)

services = {}
for service in __all__:
    services[service] = importlib.import_module('a4kSubtitles.services.%s' % service)
