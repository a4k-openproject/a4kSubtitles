# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import string
import shutil
from . import kodi
from . import logger

try:
    from .third_party import chardet
except: pass

try:  # pragma: no cover
    from urlparse import unquote, parse_qsl
    from urllib import quote_plus
    from StringIO import StringIO
    import Queue as queue
except ImportError:
    from urllib.parse import quote_plus, unquote, parse_qsl
    from io import StringIO
    import queue
    unicode = lambda v: v

__url_regex = r'[a-z0-9][a-z0-9-]{0,5}[a-z0-9]\.[a-z0-9]{2,20}\.[a-z]{2,5}'
__credit_part_regex = r'(sync|synced|fix|fixed|corrected|corrections)'
__credit_regex = __credit_part_regex + r' ?&? ?' + __credit_part_regex + r'? by'

default_encoding = 'utf-8'
base_encoding = 'raw_unicode_escape'
cp1251_garbled = u'аеио'.encode('cp1251').decode('raw_unicode_escape')
koi8r_garbled = u'аеио'.encode('koi8-r').decode('raw_unicode_escape')
code_pages = {'ara': 'cp1256', 'ar': 'cp1256', 'ell': 'cp1253', 'el': 'cp1253', 'heb': 'cp1255', 'he': 'cp1255', 'tur': 'cp1254', 'tr': 'cp1254', 'rus': 'cp1251', 'ru': 'cp1251', 'bg': 'cp1251'}

zip_utf8_flag = 0x800
py3_zip_missing_utf8_flag_fallback_encoding = 'cp437'

py2 = sys.version_info[0] == 2
py3 = not py2

temp_dir = os.path.join(kodi.addon_profile, 'temp')
data_dir = os.path.join(kodi.addon_profile, 'data')

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

def get_any_of_regex(array):
    regex = r'('
    for target in array:
        regex += re.escape(target) + r'|'
    return regex[:-1] + r')'

def cleanup_subtitles(core, sub_contents):
    service_names_regex = get_any_of_regex(core.services.keys())
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

        line_contains_ad = (
            re.search(service_names_regex, line, re.IGNORECASE) or
            re.search(__url_regex, line, re.IGNORECASE) or
            re.search(__credit_regex, line, re.IGNORECASE)
        )

        if line_contains_ad:
            logger.notice('(detected ad) %s' % line.encode('ascii', errors='ignore'))
            if not re.match(r'^\{\d+\}\{\d+\}', line):
                garbage = True
                buffer = []
            continue

        buffer.append(line)

    if cleaned_lines[0] == '':
        cleaned_lines.pop(0)

    return '\n'.join(cleaned_lines)

def open_file_wrapper(file, mode='r', encoding='utf-8'):
    if py2:
        return lambda: open(file, mode)
    return lambda: open(file, mode, encoding=encoding)

def get_json(path, filename):
    path = path if os.path.isdir(path) else os.path.dirname(path)
    if not filename.endswith('.json'):
        filename += '.json'

    json_path = os.path.join(path, filename)
    with open_file_wrapper(json_path)() as json_result:
        return json.load(json_result)

def find_file_in_archive(core, namelist, exts, part_of_filename=''):
    first_ext_match = None
    exact_file = None
    for file in namelist:
        file_lower = file.lower()
        if any(file_lower.endswith(ext) for ext in exts):
            if not first_ext_match:
                first_ext_match = file
            if (part_of_filename == '' or part_of_filename in file_lower):
                exact_file = file
                break

    return exact_file if exact_file is not None else first_ext_match

def get_zipfile_namelist(zipfile):
    infolist = zipfile.infolist()
    namelist = []

    if py2:
        for info in infolist:
            namelist.append(info.filename.decode(default_encoding))
    else:
        for info in infolist:
            filename = info.filename
            if not info.flag_bits & zip_utf8_flag:
                filename = info.filename.encode(py3_zip_missing_utf8_flag_fallback_encoding).decode(default_encoding)
            namelist.append(filename)

    return namelist

def extract_zipfile_member(zipfile, filename, dest):
    if py2:
        return zipfile.extract(filename.encode(default_encoding), dest)
    else:
        try:
            return zipfile.extract(filename, dest)
        except:
            filename = filename.encode(default_encoding).decode(py3_zip_missing_utf8_flag_fallback_encoding)
            return zipfile.extract(filename, dest)
