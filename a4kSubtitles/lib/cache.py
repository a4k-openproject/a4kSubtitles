# -*- coding: utf-8 -*-

import os
import json
import hashlib
from . import kodi
from . import utils

__meta_cache_filepath = os.path.join(kodi.addon_profile, 'last_meta.json')
__tvshow_years_cache_filepath = os.path.join(kodi.addon_profile, 'tvshow_years_cache.json')
__imdb_id_cache_filepath = os.path.join(kodi.addon_profile, 'imdb_id_cache.json')
__tokens_cache_filepath = os.path.join(kodi.addon_profile, 'tokens_cache.json')
results_filepath = os.path.join(kodi.addon_profile, 'last_results.json')

def __get_cache(filepath):
    try:
        with utils.open_file_wrapper(filepath)() as f:
            data = json.loads(f.read())
            return utils.DictAsObject(data)
    except:
        return utils.DictAsObject({})

def __save_cache(filepath, cache):
    try:
        json_data = json.dumps(cache, indent=2)
        with utils.open_file_wrapper(filepath, mode='w')() as f:
            f.write(json_data)
    except: pass

def hash_data(data):
    json_data = json.dumps(data).encode(utils.default_encoding)
    return hashlib.sha256(json_data).hexdigest()

def get_meta_hash(meta):
    return hash_data({
        'imdb_id': meta.imdb_id,
        'filename': meta.filename,
        'languages': meta.languages,
        'preferredlanguage': meta.preferredlanguage
    })

def get_meta_cache():
    meta_cache = __get_cache(__meta_cache_filepath)
    meta_cache.setdefault('imdb_id', '')
    meta_cache.setdefault('tvshow_year', '')
    return meta_cache

def save_meta_cache(meta_cache):
    return __save_cache(__meta_cache_filepath, meta_cache)

def get_tvshow_years_cache():
    return __get_cache(__tvshow_years_cache_filepath)

def save_tvshow_years_cache(data):
    return __save_cache(__tvshow_years_cache_filepath, data)

def get_imdb_id_cache():
    return __get_cache(__imdb_id_cache_filepath)

def save_imdb_id_cache(data):
    return __save_cache(__imdb_id_cache_filepath, data)

def get_tokens_cache():
    return __get_cache(__tokens_cache_filepath)

def save_tokens_cache(data):
    return __save_cache(__tokens_cache_filepath, data)
