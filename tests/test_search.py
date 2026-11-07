# -*- coding: utf-8 -*-

import importlib
import os
import types

from .common import api

__search = importlib.import_module('a4kSubtitles.search')

def __row(service_name):
    return {
        'service_name': service_name,
        'service': service_name,
        'lang': 'English',
        'lang_code': 'en',
        'name': 'The.Matrix.1999.1080p.BluRay.x264-%s' % service_name,
        'rating': 0,
        'sync': 'false',
        'impaired': 'false',
        'action_args': {'url': 'https://%s.example/download/1' % service_name},
    }

def __service(service_name):
    return types.SimpleNamespace(
        display_name=service_name.upper(),
        build_auth_request=lambda core, name: None,
        build_search_requests=lambda core, name, meta: [{'method': 'GET', 'url': 'https://%s.example/search?apikey=secret' % name}],
        parse_search_response=lambda core, name, meta, response: [__row(name)],
    )

def __meta():
    from a4kSubtitles.lib.utils import DictAsObject
    return DictAsObject({
        'imdb_id': 'tt0133093',
        'title': 'The Matrix',
        'year': '1999',
        'filename': 'The.Matrix.1999.1080p.BluRay.x264.mkv',
        'filename_without_ext': 'The.Matrix.1999.1080p.BluRay.x264',
        'season': '',
        'episode': '',
        'is_tvshow': False,
        'is_movie': True,
    })

def __setup(monkeypatch, tmp_path, failing_hosts=()):
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    core = a4ksubtitles_api.core
    meta = __meta()

    def execute(core_, request):
        host = request['url'].split('/')[2]
        if host in failing_hosts:
            return types.SimpleNamespace(status_code=500, text='', content='')
        return types.SimpleNamespace(status_code=200, text='ok', content='ok')

    monkeypatch.setattr(core, 'services', {'svca': __service('svca'), 'svcb': __service('svcb')})
    monkeypatch.setattr(core.video, 'get_meta', lambda core_: meta)
    monkeypatch.setattr(core.request, 'execute', execute)
    monkeypatch.setattr(core.cache, 'results_filepath', str(tmp_path / 'last_results.json'))
    monkeypatch.setattr(core, 'progress_text', '')
    restore = a4ksubtitles_api.mock_settings({'svca.enabled': 'true', 'svcb.enabled': 'true', 'general.results_limit': '20'})

    def search():
        try:
            return core.search(core, {'languages': 'English', 'preferredlanguage': 'English'})
        finally:
            restore()

    return core, meta, search

def test_last_results_replay_expires_after_ttl(monkeypatch, tmp_path):
    core, meta, _ = __setup(monkeypatch, tmp_path)
    meta.languages = ['English']
    meta.preferredlanguage = 'English'

    def write_cache(age):
        with open(core.cache.results_filepath, 'w') as f:
            f.write(core.json.dumps({
                'hash': core.cache.get_meta_hash(meta),
                'timestamp': core.time.time() - age,
                'results': [__row('svca')],
            }))

    write_cache(age=60)
    assert __search.__get_last_results(core, meta)[0] == [__row('svca')]

    write_cache(age=24 * 60 * 60)
    assert __search.__get_last_results(core, meta)[0] == []

def test_last_results_not_saved_when_a_service_fails(monkeypatch, tmp_path):
    core, _, search = __setup(monkeypatch, tmp_path, failing_hosts=('svcb.example',))
    results = search()
    assert [r['service_name'] for r in results] == ['svca']
    assert not os.path.exists(core.cache.results_filepath)

def test_last_results_saved_when_every_service_answers(monkeypatch, tmp_path):
    core, _, search = __setup(monkeypatch, tmp_path)
    results = search()
    assert sorted(r['service_name'] for r in results) == ['svca', 'svcb']
    assert os.path.exists(core.cache.results_filepath)

def __capture_logs(monkeypatch, core):
    records = []
    monkeypatch.setattr(core.kodi.xbmc, 'log', lambda message, level: records.append((level, message)))
    return records

def test_request_exception_logs_warning_with_host_only(monkeypatch):
    import requests
    core = api.A4kSubtitlesApi({'kodi': True}).core
    records = __capture_logs(monkeypatch, core)

    def raise_connection_error(**kwargs):
        raise requests.exceptions.ConnectionError("HTTPSConnectionPool(host='api.example.com', port=443): Max retries exceeded with url: /search?apikey=secret")
    session = types.SimpleNamespace(mount=lambda *args: None, request=raise_connection_error)
    monkeypatch.setattr(core.request, 'requests', types.SimpleNamespace(session=lambda: session))

    response = core.request.execute(core, {'method': 'GET', 'url': 'https://api.example.com/search?apikey=secret'})

    assert response.status_code == 500
    warnings = [m for (level, m) in records if level == core.kodi.xbmc.LOGWARNING]
    assert len(warnings) == 1 and 'api.example.com' in warnings[0] and 'ConnectionError' in warnings[0], records
    assert not any('secret' in m or '/search' in m for (_, m) in records), records

def test_search_logs_one_info_line_with_rows_per_service(monkeypatch, tmp_path):
    core, _, search = __setup(monkeypatch, tmp_path, failing_hosts=('svcb.example',))
    records = __capture_logs(monkeypatch, core)
    search()

    summaries = [m for (level, m) in records if level == core.logger.notice_type and 'search - ' in m]
    assert len(summaries) == 1, records
    assert 'svca: 1' in summaries[0] and 'svcb: failed' in summaries[0], summaries
    warnings = [m for (level, m) in records if level == core.kodi.xbmc.LOGWARNING]
    assert any('svcb' in m and 'svcb.example' in m for m in warnings), records
    assert not any('secret' in m for (_, m) in records), records

def test_search_summary_skips_empty_rows(monkeypatch):
    # Services return None for rows they drop (opensubtitles does); the summary runs before the language filter.
    core = api.A4kSubtitlesApi({'kodi': True}).core
    records = __capture_logs(monkeypatch, core)
    __search.__log_summary(core, ['svca'], [], [__row('svca'), None], 0)
    assert any('svca: 1' in m for (_, m) in records), records
