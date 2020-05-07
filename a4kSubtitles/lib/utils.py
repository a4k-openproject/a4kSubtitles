# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import hashlib
import string
from . import kodi
from . import logger

try:  # pragma: no cover
    from urlparse import unquote, parse_qsl
    from urllib import quote_plus
    from StringIO import StringIO
    import Queue as queue
except ImportError:
    from urllib.parse import quote_plus, unquote, parse_qsl
    from io import StringIO
    import queue
    unicode = None

__url_regex = r'(([a-z0-9][a-z0-9-]{1,5}[a-z0-9]\.[a-z0-9]{2,20})|(opensubtitles))\.[a-z]{2,5}'
__credit_part_regex = r'(sync|synced|fix|fixed|corrected|corrections)'
__credit_regex = __credit_part_regex + r' ?&? ?' + __credit_part_regex + r'? by'

PY2 = sys.version_info[0] == 2
PY3 = not PY2

temp_dir = os.path.join(kodi.addon_profile, 'temp')
results_filepath = os.path.join(kodi.addon_profile, 'last_results.json')

class DictAsObject(dict):
    def __getattr__(self, name):
        return self.get(name, None)

    def __setattr__(self, name, value):
        self[name] = value

def get_all_relative_py_files(file):
    files = os.listdir(os.path.dirname(file))
    return [filename[:-3] for filename in files if not filename.startswith('__') and filename.endswith('.py')]

def strip_non_ascii_and_unprintable(text):
    if not isinstance(text, str):
        return str(text)

    if PY2 and not isinstance(text, unicode):
        return str(text)

    result = ''.join(char for char in text if char in string.printable)
    return result.encode('ascii', errors='ignore').decode('ascii', errors='ignore')

def get_lang_ids(languages, lang_format=kodi.xbmc.ISO_639_2):
    lang_ids = []
    for language in languages:
        if language == "Portuguese (Brazil)":
            lang_id = "pob"
        elif language == "Greek":
            lang_id = "ell"
        else:
            lang_id = kodi.xbmc.convertLanguage(language, lang_format)
        lang_ids.append(lang_id)
    return lang_ids

def wait_threads(threads):
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

def get_hash(obj):
    json_data = json.dumps(obj).encode('utf-8')
    return hashlib.sha256(json_data).hexdigest()

def cleanup_subtitles(sub_contents):
    all_lines = sub_contents.split('\n')
    cleaned_lines = []
    buffer = []
    garbage = False

    if all_lines[0].strip() != '':
        all_lines.insert(0, '')

    if all_lines[-1].strip() != '':
        all_lines.append('')

    for line in all_lines:
        line = line.strip()

        if garbage and line != '':
            continue

        garbage = False

        if line == '':
            if len(buffer) > 0:
                buffer.insert(0, '')
                cleaned_lines.extend(buffer)
                buffer = []
            continue

        if re.search(__url_regex, line, re.IGNORECASE) or re.search(__credit_regex, line, re.IGNORECASE):
            logger.notice('(detected ad) %s' % line)
            if not re.match(r'^\{\d+\}\{\d+\}', line):
                garbage = True
                buffer = []
            continue

        buffer.append(line)

    if cleaned_lines[0] == '':
        cleaned_lines.pop(0)

    return '\n'.join(cleaned_lines)
