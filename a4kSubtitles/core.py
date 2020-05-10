# -*- coding: utf-8 -*-

import json
import os
import sys
import threading
import copy
import shutil
import gzip
import difflib
import time
import hashlib
import re
from datetime import datetime
from base64 import b64encode
from xml.etree import ElementTree

from .lib import (
    utils,
    logger,
    kodi,
    video,
    request,
    num2ordinal,
)
from .services import services
from .search import search
from .download import download
from .data import data

core = sys.modules[__name__]
api_mode_enabled = True
handle = None

progress_dialog = None
progress_text = ''

def main(handle, paramstring):  # pragma: no cover
    core.api_mode_enabled = False
    core.handle = handle

    params = dict(utils.parse_qsl(paramstring))
    if params['action'] == 'manualsearch':
        kodi.notification('Manual search is not supported')
    elif params['action'] == 'search':
        core.progress_text = ''
        core.progress_dialog = kodi.get_progress_dialog()

        try:
            search(core, params)
        finally:
            core.progress_dialog.close()
            core.progress_dialog = None

    elif params['action'] == 'download':
        params['action_args'] = json.loads(params['action_args'])
        download(core, params)

    kodi.xbmcplugin.endOfDirectory(handle)
