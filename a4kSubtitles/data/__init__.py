# -*- coding: utf-8 -*-

import importlib
from a4kSubtitles.lib import utils, kodi

kodi.xbmcvfs.mkdirs(utils.data_dir)
__all = utils.get_all_relative_entries(__file__, ext='')

data = {}
for service_name in __all:
    data[service_name] = importlib.import_module('a4kSubtitles.data.%s' % service_name)
