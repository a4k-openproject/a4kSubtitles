# -*- coding: utf-8 -*-

import sys
import os
import json
import re
import pytest

dir_name = os.path.dirname(__file__)
main = os.path.join(dir_name, '..')
a4kSubtitles = os.path.join(main, '..', 'a4kSubtitles')
lib = os.path.join(a4kSubtitles, 'lib')
services = os.path.join(a4kSubtitles, 'services')

sys.path.append(dir_name)
sys.path.append(main)
sys.path.append(a4kSubtitles)
sys.path.append(lib)
sys.path.append(services)

from a4kSubtitles import api
from tests import utils

def __search(a4ksubtitles_api, creds=None):
    search = lambda: None
    search.params = {
        'languages': 'English',
        'preferredlanguage': '',
    }
    search.settings = {
        'general.timeout': '15',
        'general.results_limit': '20',
        'general.remove_ads': 'false',
        'opensubtitles.enabled': 'true',
        'opensubtitles.username': creds.username,
        'opensubtitles.password': creds.password,
    }
    search.video_meta = {
        'year': '2016',
        'title': 'Fantastic Beasts and Where to Find Them',
        'imdb_id': 'tt3183660',
        'filename': 'Fantastic.Beasts.and.Where.to.Find.Them.2016.1080p.BluRay.x264.DTS-FGT.srt'
    }

    search.results = a4ksubtitles_api.search(search.params, search.settings, search.video_meta)

    return search

def test_api():
    def get_error_msg(e):
        return str(e.value).replace('\'', '')

    with pytest.raises(ImportError) as e:
        api.A4kSubtitlesApi()
    assert get_error_msg(e) == "No module named xbmc"

    with pytest.raises(ImportError) as e:
        api.A4kSubtitlesApi({'xbmc': True})
    assert get_error_msg(e) == "No module named xbmcaddon"

    with pytest.raises(ImportError) as e:
        api.A4kSubtitlesApi({'xbmc': True, 'xbmcaddon': True})
    assert get_error_msg(e) == "No module named xbmcplugin"

    with pytest.raises(ImportError) as e:
        api.A4kSubtitlesApi({'xbmc': True, 'xbmcaddon': True, 'xbmcplugin': True})
    assert get_error_msg(e) == "No module named xbmcgui"

    with pytest.raises(ImportError) as e:
        api.A4kSubtitlesApi({'xbmc': True, 'xbmcaddon': True, 'xbmcplugin': True, 'xbmcgui': True})
    assert get_error_msg(e) == "No module named xbmcvfs"

    api.A4kSubtitlesApi({'xbmc': True, 'xbmcaddon': True, 'xbmcplugin': True, 'xbmcgui': True, 'xbmcvfs': True})
    api.A4kSubtitlesApi({'kodi': True})

def test_search_missing_imdb_id():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    log_error_spy = utils.spy_fn(a4ksubtitles_api.core.logger, 'error')

    params = {
        'languages': 'English',
        'preferredlanguage': '',
    }
    a4ksubtitles_api.search(params)

    log_error_spy.called_with('Missing imdb id!')

def test_opensubtitles():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    # search
    creds = lambda: None
    creds.username = os.getenv('A4KSUBTITLES_OPENSUBTITLES_USERNAME', '')
    creds.password = os.getenv('A4KSUBTITLES_OPENSUBTITLES_PASSWORD', '')
    search = __search(a4ksubtitles_api, creds)

    assert len(search.results) == 20
    assert search.results[0]['name'] == search.video_meta['filename']

    # download
    item = search.results[0]
    item['action_args']['filename'] = item['name']

    params = {
        'action': 'download',
        'service_name': 'opensubtitles',
        'action_args': item['action_args']
    }

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

    # remove_ads
    with open(filepath, 'r') as f:
        sub_contents = f.read()

    assert re.match(r'.*OpenSubtitles.*', sub_contents, re.DOTALL) is not None

    search.settings['general.remove_ads'] = 'true'
    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

    with open(filepath, 'r') as f:
        sub_contents = f.read()

    assert re.match(r'.*OpenSubtitles.*', sub_contents, re.DOTALL) is None
