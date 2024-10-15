# -*- coding: utf-8 -*-

from .common import (
    sys,
    os,
    json,
    re,
    time,
    api,
    utils,
    pytest,
)

__movie_video_meta = {
    'year': '2016',
    'title': 'Fantastic Beasts and Where to Find Them',
    'imdb_id': 'tt3183660',
    'filename': 'Fantastic.Beasts.and.Where.to.Find.Them.2016.1080p.BluRay.x264.DTS-JYK.mkv',
    'filesize': '3592482379',
    'filehash': '4985126cbf92fe60',
}

__tvshow_video_meta = {
    "year": "2020",
    "title": "Parce Domine",
    "tvshow": "Westworld",
    "imdb_id": "tt8358332",
    "season": "3",
    "episode": "1",
    "filename": "westworld.s03e01.1080p.web.h264-xlf.mkv",
    "filesize": "3280755286",
    "filehash": "ec26d882048dde98",
}
__tvshow_expected_year = '2016'

__tvshow_unicode_video_meta = {
    "year": "2019",
    "title": "In the Dark Night of the Soul It's Always 3:30 in the Morning",
    "tvshow": "The Morning Show",
    "imdb_id": "tt7203552",
    "season": "1",
    "episode": "1",
    "filename": "The Morning Show (2019) S01E01 In the Dark Night of the Soul it's Always 330 in the Morning.mkv",
    "filesize": 2135679767,
    "filehash": "631fb55f3db5709c",
}

__tvshow_with_show_imdb_id_video_meta = __tvshow_video_meta.copy()
__tvshow_with_show_imdb_id_video_meta['imdb_id'] = 'tt0475784'
__tvshow_with_show_imdb_id_expected_year = '2016'

__tvshow_with_show_imdb_id_missing_year_meta = __tvshow_video_meta.copy()
__tvshow_with_show_imdb_id_missing_year_meta['imdb_id'] = 'tt0475784'
__tvshow_with_show_imdb_id_missing_year_meta['year'] = ''
__tvshow_with_show_imdb_id_missing_year_meta_expected_imdb_id = 'tt8358332'
__tvshow_with_show_imdb_id_missing_year_meta_expected_year = '2016'
__tvshow_with_show_imdb_id_missing_year_meta_expected_ep_year = '2020'

__tvshow_alt_title_video_meta = {
    "year": "2016",
    "title": "Episode 1",
    "tvshow": "Midnight Diner: Tokyo Stories",
    "imdb_id": "tt6190484",
    "season": "1",
    "episode": "1",
    "filename": "Midnight.Diner.Tokyo.Stories.S01E01.1080p.NF.WEB-DL.DDP2.0.x264-Monkee.mkv",
    "filesize": "808387637",
    "filehash": "b3b923134834beee",
}
__tvshow_alt_title_expected_year = '2016'

__tvshow_with_show_imdb_id_alt_title_video_meta = __tvshow_alt_title_video_meta.copy()
__tvshow_with_show_imdb_id_alt_title_video_meta['imdb_id'] = 'tt6150576'
__tvshow_with_show_imdb_id_alt_title_expected_year = '2016'

os.environ.setdefault('A4KSUBTITLES_TESTRUN', 'true')

def __remove_meta_cache(a4ksubtitles_api):
    try:
        os.remove(a4ksubtitles_api.core.cache.__meta_cache_filepath)
    except: pass

def __remove_imdb_id_cache(a4ksubtitles_api):
    try:
        os.remove(a4ksubtitles_api.core.cache.__imdb_id_cache_filepath)
    except: pass

def __remove_tvshow_years_cache(a4ksubtitles_api):
    try:
        os.remove(a4ksubtitles_api.core.cache.__tvshow_years_cache_filepath)
    except: pass

def __remove_last_results(a4ksubtitles_api):
    try:
        os.remove(a4ksubtitles_api.core.cache.results_filepath)
    except: pass

def __remove_all_cache(a4ksubtitles_api):
    __remove_imdb_id_cache(a4ksubtitles_api)
    __remove_meta_cache(a4ksubtitles_api)
    __remove_tvshow_years_cache(a4ksubtitles_api)
    __remove_last_results(a4ksubtitles_api)

def __search(a4ksubtitles_api, settings={}, video_meta={}, languages='English'):
    search = lambda: None
    search.params = {
        'languages': languages,
        'preferredlanguage': '',
    }

    search.settings = {
        'general.timeout': '30',
        'general.results_limit': '20',
        'opensubtitles.enabled': 'false',
        'opensubtitles.username': '',
        'opensubtitles.password': '',
        'bsplayer.enabled': 'false',
        'podnadpisi.enabled': 'false',
        'subdl.enabled': 'false',
        'addic7ed.enabled': 'false',
        'subsource.enabled': 'false',
    }
    search.settings.update(settings)

    search.video_meta = {}
    search.video_meta.update(video_meta)

    search.results = a4ksubtitles_api.search(search.params, search.settings, search.video_meta)

    return search

def __search_movie(a4ksubtitles_api, settings={}, video_meta={}, languages='English'):
    movie_video_meta = __movie_video_meta.copy()
    movie_video_meta.update(video_meta)
    return __search(a4ksubtitles_api, settings, movie_video_meta, languages)

def __search_tvshow(a4ksubtitles_api, settings={}, video_meta={}, languages='English'):
    tvshow_video_meta = __tvshow_video_meta.copy()
    tvshow_video_meta.update(video_meta)
    return __search(a4ksubtitles_api, settings, tvshow_video_meta, languages)

def __search_tvshow_alt_title(a4ksubtitles_api, settings={}, video_meta={}):
    tvshow_video_meta = __tvshow_alt_title_video_meta.copy()
    tvshow_video_meta.update(video_meta)
    return __search(a4ksubtitles_api, settings, tvshow_video_meta)

def __search_unicode_tvshow(a4ksubtitles_api, settings={}, video_meta={}):
    tvshow_video_meta = __tvshow_unicode_video_meta.copy()
    tvshow_video_meta.update(video_meta)
    return __search(a4ksubtitles_api, settings, tvshow_video_meta)

def __search_tvshow_with_show_imdb_id(a4ksubtitles_api, settings={}, video_meta={}):
    tvshow_video_meta = __tvshow_with_show_imdb_id_video_meta.copy()
    tvshow_video_meta.update(video_meta)
    return __search(a4ksubtitles_api, settings, tvshow_video_meta)

def __search_tvshow_with_show_imdb_id_alt_title(a4ksubtitles_api, settings={}, video_meta={}):
    tvshow_video_meta = __tvshow_with_show_imdb_id_alt_title_video_meta.copy()
    tvshow_video_meta.update(video_meta)
    return __search(a4ksubtitles_api, settings, tvshow_video_meta)

def __search_tvshow_with_show_imdb_id_missing_year(a4ksubtitles_api, settings={}, video_meta={}):
    tvshow_video_meta = __tvshow_with_show_imdb_id_missing_year_meta.copy()
    tvshow_video_meta.update(video_meta)
    return __search(a4ksubtitles_api, settings, tvshow_video_meta)

def test_search_missing_imdb_id():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    log_error_spy = utils.spy_fn(a4ksubtitles_api.core.logger, 'error')

    params = {
        'languages': 'English',
        'preferredlanguage': '',
    }
    a4ksubtitles_api.search(params, {}, {})

    log_error_spy.restore()
    log_error_spy.called_with('missing imdb id!')

def test_tvshow_year_scraping_with_episode_imdb_id():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    get_meta_spy = utils.spy_fn(a4ksubtitles_api.core.video, 'get_meta', return_result=False)

    try: __search_tvshow(a4ksubtitles_api, {'podnadpisi.enabled': 'true'})
    except: pass

    get_meta_spy.restore()
    assert get_meta_spy.result[0].tvshow_year == __tvshow_expected_year

def test_tvshow_year_scraping_with_episode_imdb_id_alt_title():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    get_meta_spy = utils.spy_fn(a4ksubtitles_api.core.video, 'get_meta', return_result=False)

    try: __search_tvshow_alt_title(a4ksubtitles_api, {'podnadpisi.enabled': 'true'})
    except: pass

    get_meta_spy.restore()
    assert get_meta_spy.result[0].tvshow_year == __tvshow_alt_title_expected_year

def test_tvshow_year_scraping_with_show_imdb_id():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    get_meta_spy = utils.spy_fn(a4ksubtitles_api.core.video, 'get_meta', return_result=False)

    try: __search_tvshow_with_show_imdb_id(a4ksubtitles_api, {'podnadpisi.enabled': 'true'})
    except: pass

    get_meta_spy.restore()
    assert get_meta_spy.result[0].tvshow_year == __tvshow_with_show_imdb_id_expected_year

def test_tvshow_year_scraping_with_show_imdb_id_alt_title():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    get_meta_spy = utils.spy_fn(a4ksubtitles_api.core.video, 'get_meta', return_result=False)

    try: __search_tvshow_with_show_imdb_id_alt_title(a4ksubtitles_api, {'podnadpisi.enabled': 'true'})
    except: pass

    get_meta_spy.restore()
    assert get_meta_spy.result[0].tvshow_year == __tvshow_with_show_imdb_id_alt_title_expected_year

def test_tvshow_year_scraping_with_show_imdb_id_missing_year():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    get_meta_spy = utils.spy_fn(a4ksubtitles_api.core.video, 'get_meta', return_result=False)

    try: __search_tvshow_with_show_imdb_id_missing_year(a4ksubtitles_api, {'podnadpisi.enabled': 'true'})
    except: pass

    get_meta_spy.restore()
    assert get_meta_spy.result[0].tvshow_year == __tvshow_with_show_imdb_id_missing_year_meta_expected_year
    assert get_meta_spy.result[0].year == __tvshow_with_show_imdb_id_missing_year_meta_expected_ep_year
    assert get_meta_spy.result[0].imdb_id == __tvshow_with_show_imdb_id_missing_year_meta_expected_imdb_id

def test_opensubtitles():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'opensubtitles.enabled': 'true',
    }
    search = __search_movie(a4ksubtitles_api, settings)

    assert len(search.results) == 20

    expected_result_name = 'Fantastic.Beasts.and.Where.to.Find.Them.2016.1080p.BluRay.x264.DTS-JYK'
    expected_result_name2 = 'Fantastic.Beasts.and.Where.to.Find.Them.2016.1080p.BluRay.x264.DTS-FGT'
    assert search.results[0]['name'] == expected_result_name or search.results[0]['name'] == expected_result_name2

    __remove_all_cache(a4ksubtitles_api)

    # search (imdb only)
    video_meta = {
        'filesize': '',
        'filehash': '',
    }
    search = __search_movie(a4ksubtitles_api, settings, video_meta)

    assert len(search.results) == 20

    # download
    item = search.results[0]

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

    assert re.match(r'.*OpenSubtitles.*', sub_contents, re.DOTALL) is None

def test_opensubtitles_tvshow():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'opensubtitles.enabled': 'true',
    }
    search = __search_tvshow(a4ksubtitles_api, settings)

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'opensubtitles',
        'action_args': item['action_args']
    }

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

def test_opensubtitles_unicode_tvshow():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'opensubtitles.enabled': 'true',
    }
    search = __search_unicode_tvshow(a4ksubtitles_api, settings)

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'opensubtitles',
        'action_args': item['action_args']
    }

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

def test_opensubtitles_missing_imdb_id():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'opensubtitles.enabled': 'true',
    }
    video_meta = {
        'imdb_id': '',
    }
    search = __search_movie(a4ksubtitles_api, settings, video_meta)

    assert len(search.results) > 0

def test_opensubtitles_missing_imdb_id_but_in_url():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'opensubtitles.enabled': 'true',
    }
    video_meta = {
        'imdb_id': '',
        'url': 'https://example.com/example.mkv?imdb_id=tt3183660'
    }
    search = __search_movie(a4ksubtitles_api, settings, video_meta)

    assert len(search.results) > 0

def test_opensubtitles_tvshow_missing_imdb_id():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'opensubtitles.enabled': 'true',
    }
    video_meta = {
        'imdb_id': '',
    }
    search = __search_tvshow(a4ksubtitles_api, settings, video_meta)

    assert len(search.results) > 0

def test_opensubtitles_tvshow_missing_imdb_id_but_in_url():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'opensubtitles.enabled': 'true',
    }
    video_meta = {
        'imdb_id': '',
        'season': '',
        'episode': '',
        'url': 'https://example.com/example.mkv?imdb_id=tt11610548'
    }
    search = __search_tvshow(a4ksubtitles_api, settings, video_meta)

    assert len(search.results) > 0

def test_opensubtitles_tvshow_missing_imdb_id_but_in_url_with_show_id_and_meta_for_ep_and_season():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'opensubtitles.enabled': 'true',
    }
    video_meta = {
        'imdb_id': '',
        'season': '',
        'episode': '',
        'url': 'https://example.com/example.mkv?imdb_id=tt10155688&season=1&episode=2'
    }
    search = __search_tvshow(a4ksubtitles_api, settings, video_meta)

    assert len(search.results) > 0

def test_bsplayer():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)
    request_execute_spy = utils.spy_fn(a4ksubtitles_api.core.request, 'execute')

    # search
    settings = {
        'bsplayer.enabled': 'true',
    }
    search = __search_movie(a4ksubtitles_api, settings)

    assert request_execute_spy.call_count > 1
    request_execute_spy.restore()

    assert len(search.results) == 16

    expected_result_name = os.path.splitext(search.video_meta['filename'])[0]
    result_name = os.path.splitext(search.results[0]['name'])[0]
    assert expected_result_name == result_name

    # cache
    request_execute_spy = utils.spy_fn(a4ksubtitles_api.core.request, 'execute')
    __search_movie(a4ksubtitles_api, settings)

    assert request_execute_spy.call_count == 1

    request_execute_spy.restore()

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'bsplayer',
        'action_args': item['action_args']
    }

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

def test_bsplayer_tvshow():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'bsplayer.enabled': 'true',
    }
    search = __search_tvshow(a4ksubtitles_api, settings)

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'bsplayer',
        'action_args': item['action_args']
    }

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

def test_podnadpisi():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'podnadpisi.enabled': 'true',
    }
    search = __search_movie(a4ksubtitles_api, settings)

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'podnadpisi',
        'action_args': item['action_args']
    }

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

def test_podnadpisi_tvshow():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'podnadpisi.enabled': 'true',
    }
    search = __search_tvshow(a4ksubtitles_api, settings)

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'podnadpisi',
        'action_args': item['action_args']
    }

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

def test_podnadpisi_tvshow_missing_imdb_id_but_in_url_with_show_id_and_meta_for_ep_and_season_with_paging():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'podnadpisi.enabled': 'true',
    }
    video_meta = {
        'imdb_id': '',
        'season': '',
        'episode': '',
        'url': 'https://example.com/example.mkv?imdb_id=tt0239195&season=20&episode=2'
    }
    search = __search_tvshow(a4ksubtitles_api, settings, video_meta)

    assert len(search.results) > 0

# def test_subdl():
#     a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
#     __remove_all_cache(a4ksubtitles_api)

#     # search
#     settings = {
#         'subdl.enabled': 'true',
#         'subdl.apikey': os.getenv('A4KSUBTITLES_SUBDL_APIKEY', ''),
#     }
#     search = __search_movie(a4ksubtitles_api, settings)

#     # download
#     item = search.results[0]

#     params = {
#         'action': 'download',
#         'service_name': 'subdl',
#         'action_args': item['action_args']
#     }

#     if os.getenv('CI', None) is not None:
#         time.sleep(4)

#     filepath = a4ksubtitles_api.download(params, search.settings)

#     assert filepath != ''

# def test_subdl_tvshow():
#     a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
#     __remove_all_cache(a4ksubtitles_api)

#     # search
#     settings = {
#         'subdl.enabled': 'true',
#         'subdl.apikey': os.getenv('A4KSUBTITLES_SUBDL_APIKEY', ''),
#     }

#     if os.getenv('CI', None) is not None:
#         time.sleep(4)

#     search = __search_tvshow(a4ksubtitles_api, settings)

#     # download
#     item = search.results[0]

#     params = {
#         'action': 'download',
#         'service_name': 'subdl',
#         'action_args': item['action_args']
#     }

#     if os.getenv('CI', None) is not None:
#         time.sleep(4)

#     filepath = a4ksubtitles_api.download(params, search.settings)

#     assert filepath != ''

# def test_subdl_tvshow_persian():
#     a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
#     __remove_all_cache(a4ksubtitles_api)

#     # search
#     settings = {
#         'subdl.enabled': 'true',
#         'subdl.apikey': os.getenv('A4KSUBTITLES_SUBDL_APIKEY', ''),
#     }

#     if os.getenv('CI', None) is not None:
#         time.sleep(4)

#     search = __search_tvshow(a4ksubtitles_api, settings, {}, 'Persian')

#     # download
#     item = search.results[0]

#     params = {
#         'action': 'download',
#         'service_name': 'subdl',
#         'action_args': item['action_args']
#     }

#     if os.getenv('CI', None) is not None:
#         time.sleep(4)

#     filepath = a4ksubtitles_api.download(params, search.settings)

#     assert filepath != ''

# def test_subdl_arabic():
#     a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
#     __remove_all_cache(a4ksubtitles_api)

#     # search
#     settings = {
#         'subdl.enabled': 'true',
#         'subdl.apikey': os.getenv('A4KSUBTITLES_SUBDL_APIKEY', ''),
#     }

#     if os.getenv('CI', None) is not None:
#         time.sleep(4)

#     search = __search_movie(a4ksubtitles_api, settings, {}, 'Arabic')

#     # download
#     item = search.results[0]

#     params = {
#         'action': 'download',
#         'service_name': 'subdl',
#         'action_args': item['action_args']
#     }

#     if os.getenv('CI', None) is not None:
#         time.sleep(4)

#     filepath = a4ksubtitles_api.download(params, search.settings)

#     assert filepath != ''

def test_addic7ed_tvshow():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'addic7ed.enabled': 'true',
    }
    search = __search_tvshow(a4ksubtitles_api, settings)

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'addic7ed',
        'action_args': item['action_args']
    }

    try:
        filepath = a4ksubtitles_api.download(params, search.settings)
    except Exception as e:
        if 'object does not support the context manager protocol' in str(e):
            print('Skipping test_addic7ed_tvshow')
            return

    assert filepath != ''

def test_subsource():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'subsource.enabled': 'true',
    }
    search = __search_movie(a4ksubtitles_api, settings)

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'subsource',
        'action_args': item['action_args']
    }

    if os.getenv('CI', None) is not None:
        time.sleep(4)

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

def test_subsource_tvshow():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'subsource.enabled': 'true',
    }

    if os.getenv('CI', None) is not None:
        time.sleep(4)

    search = __search_tvshow(a4ksubtitles_api, settings)

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'subsource',
        'action_args': item['action_args']
    }

    if os.getenv('CI', None) is not None:
        time.sleep(4)

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''

def test_subsource_arabic():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    __remove_all_cache(a4ksubtitles_api)

    # search
    settings = {
        'subsource.enabled': 'true',
    }

    if os.getenv('CI', None) is not None:
        time.sleep(4)

    search = __search_movie(a4ksubtitles_api, settings, {}, 'Arabic')

    # download
    item = search.results[0]

    params = {
        'action': 'download',
        'service_name': 'subsource',
        'action_args': item['action_args']
    }

    if os.getenv('CI', None) is not None:
        time.sleep(4)

    filepath = a4ksubtitles_api.download(params, search.settings)

    assert filepath != ''
