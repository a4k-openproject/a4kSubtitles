# -*- coding: utf-8 -*-

from .common import api, service, utils

def __mock_monitor(api):
    monitor = lambda: None
    monitor.__check_num = 1
    def __monitor_is_at_least_third_check():
        if monitor.__check_num < 3:
            monitor.__check_num += 1
            return False
        return True
    monitor.abortRequested = lambda: __monitor_is_at_least_third_check()
    monitor.waitForAbort = lambda _: False

    default = api.core.kodi.xbmc.Monitor
    api.core.kodi.xbmc.Monitor = lambda: monitor
    def restore():
        api.core.kodi.xbmc.Monitor = default
    return restore

def __mock_get_cond_visibility(api, mock_data):
    default = api.core.kodi.xbmc.getCondVisibility
    api.core.kodi.xbmc.getCondVisibility = lambda v: mock_data.get(v, False)
    def restore():
        api.core.kodi.xbmc.getCondVisibility = default
    return restore

def __mock_time_sleep(api):
    default = api.core.time.sleep
    api.core.time.sleep = lambda _: None
    def restore():
        api.core.time.sleep = default
    return restore

def __mock(api, settings):
    restore_monitor = __mock_monitor(api)
    restore_time_sleep = __mock_time_sleep(api)
    restore_settings = api.mock_settings(settings)

    def restore():
        restore_monitor()
        restore_time_sleep()
        restore_settings()
    return restore

def test_service_start_when_disabled():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'false',
    })
    get_cond_visibility_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'getCondVisibility')

    service.start(a4ksubtitles_api.core)

    restore()
    get_cond_visibility_spy.restore()

    assert get_cond_visibility_spy.call_count == 0

def test_service_start_when_enabled():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
    })
    get_cond_visibility_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'getCondVisibility')

    service.start(a4ksubtitles_api.core)

    restore()
    get_cond_visibility_spy.restore()

    assert get_cond_visibility_spy.call_count > 0

def test_service_when_video_has_subtitles():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
    })
    restore_get_cond_visibility = __mock_get_cond_visibility(a4ksubtitles_api, {
        'Player.HasVideo': True,
        'VideoPlayer.HasSubtitles': True,
        'VideoPlayer.SubtitlesEnabled': True,
    })

    executebuiltin_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'executebuiltin')

    service.start(a4ksubtitles_api.core)

    restore()
    restore_get_cond_visibility()
    executebuiltin_spy.restore()

    assert executebuiltin_spy.call_count == 0

def test_service_when_video_does_not_have_subtitles():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
    })
    restore_get_cond_visibility = __mock_get_cond_visibility(a4ksubtitles_api, {
        'Player.HasVideo': True,
        'VideoPlayer.HasSubtitles': False,
        'VideoPlayer.SubtitlesEnabled': False,
    })

    executebuiltin_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'executebuiltin')

    service.start(a4ksubtitles_api.core)

    restore()
    restore_get_cond_visibility()
    executebuiltin_spy.restore()

    assert executebuiltin_spy.call_count == 1

def test_service_when_video_has_disabled_subtitles():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
    })
    restore_get_cond_visibility = __mock_get_cond_visibility(a4ksubtitles_api, {
        'Player.HasVideo': True,
        'VideoPlayer.HasSubtitles': True,
        'VideoPlayer.SubtitlesEnabled': False,
    })

    executebuiltin_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'executebuiltin')

    service.start(a4ksubtitles_api.core)

    restore()
    restore_get_cond_visibility()
    executebuiltin_spy.restore()

    assert executebuiltin_spy.call_count == 1

def test_service_when_subs_check_done():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
    })
    restore_get_cond_visibility = __mock_get_cond_visibility(a4ksubtitles_api, {
        'Player.HasVideo': True,
        'VideoPlayer.HasSubtitles': True,
        'VideoPlayer.SubtitlesEnabled': True,
    })

    executebuiltin_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'executebuiltin')

    service.start(a4ksubtitles_api.core)

    restore()
    restore_get_cond_visibility()
    executebuiltin_spy.restore()

    assert executebuiltin_spy.call_count == 0
