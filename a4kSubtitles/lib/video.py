# -*- coding: utf-8 -*-

import os
import json
import struct
import hashlib
import re
import threading

from .kodi import xbmc, xbmcvfs, get_bool_setting
from . import logger, utils, request

__64k = 65536
__longlong_format_char = 'q'
__byte_size = struct.calcsize(__longlong_format_char)

def __sum_64k_bytes(file, result):
    for _ in range(__64k / __byte_size):
        chunk = file.read(__byte_size)
        (value,) = struct.unpack(__longlong_format_char, chunk)
        result.filehash += value
        result.filehash &= 0xFFFFFFFFFFFFFFFF

def __set_size_and_hash(meta, filepath):
    f = xbmcvfs.File(filepath)
    try:
        filesize = meta['filesize'] = f.size()

        # used for mocking
        try:
            meta['filehash'] = f.hash()
            return
        except: pass

        if filesize < __64k * 2:
            return

        # ref: https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
        # filehash = filesize + 64bit sum of the first and last 64k of the file
        result = lambda: None
        result.filehash = filesize

        __sum_64k_bytes(f, result)
        f.seek(filesize - __64k, os.SEEK_SET)
        __sum_64k_bytes(f, result)

        meta['filehash'] = "%016x" % result.filehash
    finally:
        f.close()

def __set_subdb_hash(meta, filepath):
    f = xbmcvfs.File(filepath)
    try:
        # used for mocking
        try:
            meta['subdb_hash'] = f.subdb_hash()
            return
        except: pass

        data = f.read(__64k)
        f.seek(-__64k, os.SEEK_END)
        data += f.read(__64k)

        meta['subdb_hash'] = hashlib.md5(data).hexdigest()
    finally:
        f.close()

def __scrape_tvshow_year(meta):
    imdb_response = request.execute({'method': 'GET', 'url': 'https://www.imdb.com/title/' + meta.imdb_id})
    if imdb_response.status_code == 200:
        show_year_match = re.search(r' %s \((.*?)\)"' % meta.tvshow, imdb_response.text)
        if show_year_match:
            meta.tvshow_year = show_year_match.group(1)

def get_meta():
    meta = {}
    meta['year'] = xbmc.getInfoLabel('VideoPlayer.Year')
    meta['season'] = xbmc.getInfoLabel('VideoPlayer.Season')
    meta['episode'] = xbmc.getInfoLabel('VideoPlayer.Episode')
    meta['tvshow'] = xbmc.getInfoLabel('VideoPlayer.TVShowTitle')
    meta['title'] = xbmc.getInfoLabel('VideoPlayer.OriginalTitle')
    if meta['title'] == '':
        meta['title'] = xbmc.getInfoLabel('VideoPlayer.Title')
    meta['imdb_id'] = xbmc.getInfoLabel('VideoPlayer.IMDBNumber')

    meta['filename'] = meta['title']
    meta['filesize'] = ''
    meta['filehash'] = ''

    try:
        filepath = xbmc.Player().getPlayingFile()
        meta['filename'] = filepath.split('/')[-1]
        __set_size_and_hash(meta, filepath)
        __set_subdb_hash(meta, filepath)
    except:
        import traceback
        traceback.print_exc()

    try:
        meta['filename'] = utils.unquote(meta['filename'])
        meta['filename_without_ext'] = os.path.splitext(meta['filename'])[0]
    except: pass

    meta_json = json.dumps(meta, indent=2)
    logger.debug(meta_json)
    meta = json.loads(meta_json)

    meta = utils.DictAsObject(meta)

    for key in meta.keys():
        value = utils.strip_non_ascii_and_unprintable(meta[key])
        meta[key] = str(value).strip()

    meta.is_tvshow = meta.tvshow != ''
    meta.is_movie = not meta.is_tvshow

    if meta.is_tvshow and meta.imdb_id != '' and get_bool_setting('podnadpisi', 'enabled'):
        meta.tvshow_year_thread = threading.Thread(target=__scrape_tvshow_year, args=(meta,))
        meta.tvshow_year_thread.start()

    return meta
