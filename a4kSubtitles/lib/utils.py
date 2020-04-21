# -*- coding: utf-8 -*-

import os
import sys
from .kodi import addon_profile

try:
    from urlparse import unquote, parse_qsl
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus, unquote, parse_qsl

PY2 = sys.version_info[0] == 2
PY3 = not PY2
temp_dir = os.path.join(addon_profile, 'temp')

def get_all_relative_py_files(file):
    files = os.listdir(os.path.dirname(file))
    return [filename[:-3] for filename in files if not filename.startswith('__') and filename.endswith('.py')]
