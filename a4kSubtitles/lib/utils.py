# -*- coding: utf-8 -*-

import os
import sys
import re
import json
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
    unicode = lambda v, e: v

__url_regex = r'(([a-z0-9][a-z0-9-]{1,5}[a-z0-9]\.[a-z0-9]{2,20})|(opensubtitles))\.[a-z]{2,5}'
__credit_part_regex = r'(sync|synced|fix|fixed|corrected|corrections)'
__credit_regex = __credit_part_regex + r' ?&? ?' + __credit_part_regex + r'? by'

default_encoding = 'utf-8'
base_encoding = 'raw_unicode_escape'
cp1251_garbled = u'аеио'.encode('cp1251').decode('raw_unicode_escape')
koi8r_garbled = u'аеио'.encode('koi8-r').decode('raw_unicode_escape')

py2 = sys.version_info[0] == 2
py3 = not py2

temp_dir = os.path.join(kodi.addon_profile, 'temp')

class DictAsObject(dict):
    def __getattr__(self, name):
        return self.get(name, None)

    def __setattr__(self, name, value):
        self[name] = value

def get_all_relative_entries(relative_file, ext='.py', ignore_private=True):
    entries = os.listdir(os.path.dirname(relative_file))
    return [os.path.splitext(name)[0] for name in entries if not ignore_private or not name.startswith('__') and name.endswith(ext)]

def strip_non_ascii_and_unprintable(text):
    if not isinstance(text, str) and (not py2 or not isinstance(text, unicode)):
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
            logger.notice('(detected ad) %s' % line.encode('ascii', errors='ignore'))
            if not re.match(r'^\{\d+\}\{\d+\}', line):
                garbage = True
                buffer = []
            continue

        buffer.append(line)

    if cleaned_lines[0] == '':
        cleaned_lines.pop(0)

    return '\n'.join(cleaned_lines)

def get_relative_json(relative_file, filename):
    json_path = os.path.join(os.path.dirname(relative_file), filename + '.json')
    with open(json_path) as json_result:
        return json.load(json_result)
