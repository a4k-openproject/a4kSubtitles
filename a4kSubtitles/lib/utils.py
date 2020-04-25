# -*- coding: utf-8 -*-

import os
import sys
import re
from . import kodi
from . import logger

try:
    from urlparse import unquote, parse_qsl
    from urllib import quote_plus
    from StringIO import StringIO
except ImportError:
    from urllib.parse import quote_plus, unquote, parse_qsl
    from io import StringIO

__url_regex = r'(([a-zA-Z0-9][a-zA-Z0-9-]{1,5}[a-zA-Z0-9]\.[a-zA-Z]{2,20})|(opensubtitles))\.[a-zA-Z]{2,5}'
__credit_part_regex = r'(sync|synced|fix|fixed|corrected|corrections)'
__credit_regex = __credit_part_regex + r' ?&? ?' + __credit_part_regex + r'? by'

PY2 = sys.version_info[0] == 2
PY3 = not PY2

temp_dir = os.path.join(kodi.addon_profile, 'temp')

def get_all_relative_py_files(file):
    files = os.listdir(os.path.dirname(file))
    return [filename[:-3] for filename in files if not filename.startswith('__') and filename.endswith('.py')]

def get_lang_ids(languages):
    lang_ids = []
    for language in languages:
        if language == "Portuguese (Brazil)":
            lang_id = "pob"
        elif language == "Greek":
            lang_id = "ell"
        else:
            lang_id = kodi.xbmc.convertLanguage(language, kodi.xbmc.ISO_639_2)
        lang_ids.append(lang_id)
    return lang_ids

def wait_threads(threads):
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

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
