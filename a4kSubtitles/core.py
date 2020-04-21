# -*- coding: utf-8 -*-

import json
import os
import sys
import threading
import copy
import shutil
import gzip
import difflib
from base64 import b64encode

from .lib import (
    utils,
    logger,
    kodi,
    video,
    request,
)
from .services import services
from .search import search
from .download import download

core = sys.modules[__name__]
api_mode_enabled = os.getenv('A4KSUBTITLES_API_MODE') is not None

handle = None
if not api_mode_enabled:
    handle = int(sys.argv[1])

def main(paramstring):
    params = dict(utils.parse_qsl(paramstring))
    if params['action'] in ('search', 'manualsearch'):
        search(core, params)
    elif params['action'] == 'download':
        params['action_args'] = json.loads(params['action_args'])
        download(core, params)
    kodi.xbmcplugin.endOfDirectory(handle)
