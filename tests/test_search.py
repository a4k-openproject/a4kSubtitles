# -*- coding: utf-8 -*-

import sys
import os

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

sys.argv = ['_', '1']

from a4kSubtitles import api
from tests import utils

def test_search_missing_imdb_id():
    a4kSubtitlesApi = api.a4kSubtitlesApi({ 'kodi': True })
    log_error_spy = utils.spy_fn(a4kSubtitlesApi.core.logger, 'error')

    params = {
        'languages': 'English',
        'preferredlanguage': '',
    }
    a4kSubtitlesApi.search(params)

    log_error_spy.called_with('Missing imdb id!')

def test_search_opensubtitles():
    a4kSubtitlesApi = api.a4kSubtitlesApi({ 'kodi': True })

    params = {
        'languages': 'English',
        'preferredlanguage': '',
    }
    settings = {
        'general.timeout': '15',
        'general.results_limit': '20',
        'opensubtitles.enabled': 'true'
    }
    video_meta = {
        'year': '2016',
        'title': 'Fantastic Beasts and Where to Find Them',
        'imdb_id': 'tt3183660',
        'filename': 'Fantastic.Beasts.and.Where.to.Find.Them.2016.1080p.BluRay.x264.DTS-FGT.srt'
    }

    results = a4kSubtitlesApi.search(params, settings, video_meta)

    assert len(results) == 20
    assert results[0]['name'] == video_meta['filename']
