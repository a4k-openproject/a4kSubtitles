# -*- coding: utf-8 -*-

import importlib
import json
import types

from .common import api

__search = importlib.import_module('a4kSubtitles.search')

def __core():  # built lazily: test_api needs the first core import to happen inside it
    return api.A4kSubtitlesApi({'kodi': True}).core

def __service():
    return __core().services['opensubtitles_quick']


def __api_url():
    return 'https://' + getattr(__service(), '__host')

def __file_url(id, scheme='https'):
    return '%s://files.%s/file/%s' % (scheme, getattr(__service(), '__host').split('.', 1)[1], id)

def __meta(**kwargs):
    from a4kSubtitles.lib.utils import DictAsObject
    meta = DictAsObject({
        'imdb_id': 'tt3183660',
        'tv_show_imdb_id': 'tt3183660',
        'season': '',
        'episode': '',
        'is_tvshow': False,
        'languages': ['English'],
    })
    meta.update(kwargs)
    return meta

def __item(id, lang, name='Fantastic.Beasts.2016.1080p.BluRay.x264-JYK.srt', url=None):
    return {'id': id, 'lang': lang, 'url': url or __file_url(id), 'subtitleFileName': name}

def __parse(items, languages):
    response = types.SimpleNamespace(status_code=200, text=json.dumps({'subtitles': items}))
    return __service().parse_search_response(__core(), 'opensubtitles_quick', __meta(languages=languages), response)

def test_movie_url():
    [request] = __service().build_search_requests(__core(), 'opensubtitles_quick', __meta())
    assert request['url'] == __api_url() + '/subtitles/movie/tt3183660.json'
    assert request['timeout'] <= 5

def test_episode_url_uses_show_id_and_unpadded_numbers():
    meta = __meta(imdb_id='tt8358332', tv_show_imdb_id='tt0475784', season='03', episode='1', is_tvshow=True)
    [request] = __service().build_search_requests(__core(), 'opensubtitles_quick', meta)
    assert request['url'] == __api_url() + '/subtitles/series/tt0475784:3:1.json'

def test_episode_falls_back_to_imdb_id_without_show_id():
    meta = __meta(imdb_id='tt0475784', tv_show_imdb_id='', season='3', episode='1', is_tvshow=True)
    [request] = __service().build_search_requests(__core(), 'opensubtitles_quick', meta)
    assert request['url'] == __api_url() + '/subtitles/series/tt0475784:3:1.json'

def test_no_request_without_usable_ids():
    assert __service().build_search_requests(__core(), 'opensubtitles_quick', __meta(imdb_id='12345')) == []
    assert __service().build_search_requests(__core(), 'opensubtitles_quick', __meta(is_tvshow=True, season='3', episode='')) == []

def test_retries_once_on_server_error():
    [request] = __service().build_search_requests(__core(), 'opensubtitles_quick', __meta())
    calls = []

    def session_request(**kwargs):
        calls.append(kwargs['url'])
        return types.SimpleNamespace(status_code=502, text='', content='')
    session = types.SimpleNamespace(mount=lambda *args: None, request=session_request)
    core = __core()
    original = core.request.requests
    core.request.requests = types.SimpleNamespace(session=lambda: session)
    try:
        response = core.request.execute(core, request)
    finally:
        core.request.requests = original

    assert response.status_code == 502
    assert len(calls) == 2

def test_language_mapping_keeps_requested_languages_only():
    items = [
        __item('1', 'eng'), __item('2', 'spa'), __item('3', 'fre'), __item('4', 'ger'),
        __item('5', 'por'), __item('6', 'pob'), __item('7', 'ita'), __item('8', 'xyz'),
    ]
    languages = ['English', 'Spanish', 'French', 'German', 'Portuguese', 'Portuguese (Brazil)']
    results = __parse(items, languages)
    assert [(r['action_args']['url'][-1], r['lang'], r['lang_code']) for r in results] == [
        ('1', 'English', 'en'), ('2', 'Spanish', 'es'), ('3', 'French', 'fr'),
        ('4', 'German', 'de'), ('5', 'Portuguese', 'pt'), ('6', 'Portuguese (Brazil)', 'pt-br'),
    ]
    assert all(r['service'] == 'OpenSubtitles' and r['action_args']['raw'] for r in results)

def test_rows_from_other_hosts_are_dropped():
    items = [__item('1', 'eng', url='https://example.com/file/1'), __item('2', 'eng', url=__file_url('2', scheme='http'))]
    assert __parse(items, ['English']) == []

def test_download_is_a_plain_get_of_the_row_url():
    url = __file_url('1')
    assert __service().build_download_request(__core(), 'opensubtitles_quick', {'url': url}) == {'method': 'GET', 'url': url, 'stream': True}

def __row(service_name, dedup_key, sync='false', url=None):
    return {
        'service_name': service_name, 'service': 'OpenSubtitles', 'lang': 'English', 'lang_code': 'en',
        'name': 'Fantastic.Beasts.2016.1080p.BluRay.x264-JYK', 'rating': 0, 'sync': sync, 'impaired': 'false',
        'dedup_key': dedup_key, 'action_args': {'url': url or '%s-%s' % (service_name, dedup_key)},
    }

def test_dedup_keeps_one_row_per_opensubtitles_file():
    meta = __meta()
    rows = [
        __row('opensubtitles', 'opensubtitles:1'), __row('opensubtitles_quick', 'opensubtitles:1'),
        __row('opensubtitles_quick', 'opensubtitles:2'), __row('opensubtitles', 'opensubtitles:2'),
        __row('opensubtitles', 'opensubtitles:3', sync='true'), __row('opensubtitles_quick', 'opensubtitles:3'),
        __row('opensubtitles', None, url='4'), __row('opensubtitles_quick', None, url='5'),
    ]
    kept = sorted((r['dedup_key'] or '', r['service_name']) for r in __search.__sanitize_results(__core(), meta, rows))
    assert kept == [
        ('', 'opensubtitles'), ('', 'opensubtitles_quick'),
        ('opensubtitles:1', 'opensubtitles_quick'),
        ('opensubtitles:2', 'opensubtitles_quick'),
        ('opensubtitles:3', 'opensubtitles'),
    ]

def test_credentialed_rows_carry_the_shared_dedup_key():
    body = {'data': [{'attributes': {
        'legacy_subtitle_id': 6897823, 'language': 'en', 'ratings': 0, 'hearing_impaired': False,
        'feature_details': {}, 'files': [{'file_id': 1, 'file_name': 'Fantastic.Beasts.2016'}],
    }}]}
    response = types.SimpleNamespace(status_code=200, text=json.dumps(body))
    [row] = __core().services['opensubtitles'].parse_search_response(__core(), 'opensubtitles', __meta(), response)
    [quick] = __parse([__item('6897823', 'eng')], ['English'])
    assert row['dedup_key'] == quick['dedup_key'] == 'opensubtitles:6897823'
