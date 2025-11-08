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
    from .third_party import iso639
    from .third_party import gptsubtrans
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
suspend_service_file = os.path.join(kodi.addon_profile, 'suspend_service')

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

def slugify_filename(text):
    return re.sub(r'[\\/*?:"<>|]', '_', text)

def get_lang_id(language, lang_format):
    try:
        return get_lang_ids([language], lang_format)[0]
    except:
        return ''

def get_lang_ids(languages, lang_format=kodi.xbmc.ISO_639_2):
    try:
        lang_ids = []
        for language in languages:
            lang = language.lower()
            if lang in ['pb', 'pob', 'pt-br'] or 'brazil' in lang:
                if lang_format == kodi.xbmc.ISO_639_1:
                    lang_ids.append('pt-br')
                elif lang_format == kodi.xbmc.ISO_639_2:
                    lang_ids.append('pob')
                elif lang_format == kodi.xbmc.ENGLISH_NAME:
                    lang_ids.append('Portuguese (Brazil)')
                continue

            lang = iso639.Lang(language)

            lang_id = None
            if lang_format == kodi.xbmc.ISO_639_1:
                lang_id = lang.pt1
            elif lang_format == kodi.xbmc.ISO_639_2:
                lang_id = lang.pt3
            elif lang_format == kodi.xbmc.ENGLISH_NAME:
                lang_id = lang.name

            if lang_id is not None:
                lang_ids.append(lang_id)

        return lang_ids
    except:
        return []

def get_subfile_from_temp_dir():
    if not os.path.exists(temp_dir):
        return None
    for file in os.listdir(temp_dir):
        if file != 'sub.zip' and not file.endswith('.translated'):
            return os.path.join(temp_dir, file.strip())
    return None

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
            logger.debug('(detected ad) %s' % line.encode('ascii', errors='ignore'))
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

def find_file_in_archive(core, namelist, exts, episode_number=''):
    first_ext_match = None
    exact_file = None
    for file in namelist:
        file_lower = file.lower()
        if any(file_lower.endswith(ext) for ext in exts):
            sub_meta = extract_season_episode(file_lower, True)
            if not first_ext_match:
                first_ext_match = file
            if (episode_number == '' or sub_meta.episode == episode_number):
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

def extract_season_episode(filename, episode_fallback=False, zfill=3):
    episode_pattern = r'(?:e|ep.?|episode.?)(\d{1,5})(?:v\d?)?'
    season_pattern = r'(?:s|season.?)(\d{1,5})'
    combined_pattern = r'\b(?:s|season)(\d{1,5})\s?[x|\-|\_|\s]\s?[a-z]?(\d{1,5})(?:v\d?)?\b'
    range_episodes_pattern = r'\b(?:.{1,4}e|ep|eps|episodes|\s)?(\d{1,5}?)(?:v.?)?\s?[\-|\~]\s?(\d{1,5})(?:v.?)?\b'
    date_pattern = r'\b(\d{2,4}-\d{1,2}-\d{2,4})\b'

    filename = re.sub(date_pattern, "", filename)
    season_match = re.search(season_pattern, filename, re.IGNORECASE)
    episode_match = re.search(episode_pattern, filename, re.IGNORECASE)
    combined_match = re.search(combined_pattern, filename, re.IGNORECASE)
    range_episodes_match = re.findall(range_episodes_pattern, filename, re.IGNORECASE)

    season = season_match.group(1) if season_match else None
    episode = episode_match.group(1) if episode_match else None
    episodes_range = range(0)

    if combined_match:
        season = season if season else combined_match.group(1)
        episode = episode if episode else combined_match.group(2)

    if range_episodes_match:
        range_start, range_end = map(int, range_episodes_match[-1])
        episodes_range = range(range_start, range_end)

    if episode_fallback and not episode:
        # If no matches found, attempt to capture episode-like sequences
        fallback_pattern = re.compile(r'\bE?P?(\d{1,5})v?\d?\b', re.IGNORECASE)
        filename = re.sub(r'[\s\.\:\;\(\)\[\]\{\}\\\/\&\€\'\`\#\@\=\$\?\!\%\+\-\_\*\^]', " ", filename)
        fallback_matches = fallback_pattern.findall(filename)

        if fallback_matches:
            # Assuming the last number in the fallback matches is the episode number
            episode = fallback_matches[-1].lstrip("0").zfill(zfill)

    return DictAsObject(
        {
            "season": season.lstrip("0").zfill(zfill) if season else "",
            "episode": episode.lstrip("0").zfill(zfill) if episode else "",
            "episodes_range": episodes_range
        }
    )
