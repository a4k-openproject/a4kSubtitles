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

def __mock_is_playingvideo(api, mock_playing_state):
    default = api.core.kodi.xbmc.Player().isPlayingVideo
    api.core.kodi.xbmc.Player().isPlayingVideo = lambda: mock_playing_state
    def restore():
        api.core.kodi.xbmc.Player().isPlayingVideo = default
    return restore

def __mock_get_cond_visibility(api, mock_data):
    default = api.core.kodi.xbmc.getCondVisibility
    api.core.kodi.xbmc.getCondVisibility = lambda v: mock_data.get(v, False)
    def restore():
        api.core.kodi.xbmc.getCondVisibility = default
    return restore

def __mock_get_info_label(api, mock_data):
    default = api.core.kodi.xbmc.getInfoLabel
    api.core.kodi.xbmc.getInfoLabel = lambda v: mock_data.get(v, False)
    def restore():
        api.core.kodi.xbmc.getInfoLabel = default
    return restore

def __mock_api_search(api):
    default = api.search
    api.search = lambda p: [{}]
    def restore():
        api.search = default
    return restore

def __mock_api_download(api, result=None):
    default = api.download
    api.download = lambda p: result
    def restore():
        api.download = default
    return restore

def __mock(api, settings):
    restore_monitor = __mock_monitor(api)
    restore_settings = api.mock_settings(settings)

    def restore():
        restore_monitor()
        restore_settings()
    return restore

def test_service_start_when_video_playing():
    def test_playing_video(state):
        a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

        restore = __mock(a4ksubtitles_api, {
            'general.auto_search': 'True',
        })
        get_infolabel_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'getInfoLabel')
        restore_isplayingvideo = __mock_is_playingvideo(a4ksubtitles_api, state)

        service.start(a4ksubtitles_api)

        restore()
        restore_isplayingvideo()
        get_infolabel_spy.restore()

        return get_infolabel_spy.call_count

    assert test_playing_video(True) != 0
    assert test_playing_video(False) == 0

def test_service_start_when_disabled():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'false',
    })
    get_cond_visibility_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'getCondVisibility')
    restore_isplayingvideo = __mock_is_playingvideo(a4ksubtitles_api, True)

    service.start(a4ksubtitles_api)

    restore()
    restore_isplayingvideo()
    get_cond_visibility_spy.restore()

    assert get_cond_visibility_spy.call_count == 0

def test_service_start_when_enabled():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
    })
    get_cond_visibility_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'getCondVisibility')
    restore_isplayingvideo = __mock_is_playingvideo(a4ksubtitles_api, True)

    service.start(a4ksubtitles_api)

    restore()
    restore_isplayingvideo()
    get_cond_visibility_spy.restore()

    assert get_cond_visibility_spy.call_count > 0

def test_service_when_video_does_not_have_subtitles():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
    })
    restore_get_cond_visibility = __mock_get_cond_visibility(a4ksubtitles_api, {
        'Player.HasDuration': True,
        'VideoPlayer.HasSubtitles': False,
        'VideoPlayer.SubtitlesEnabled': False,
    })
    restore_get_info_label = __mock_get_info_label(a4ksubtitles_api, {
        'VideoPlayer.IMDBNumber': 'tt1234567',
    })
    restore_isplayingvideo = __mock_is_playingvideo(a4ksubtitles_api, True)

    executebuiltin_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'executebuiltin')

    service.start(a4ksubtitles_api)

    restore()
    restore_isplayingvideo()
    restore_get_cond_visibility()
    restore_get_info_label()
    executebuiltin_spy.restore()

    assert executebuiltin_spy.call_count == 1

def test_service_when_video_has_disabled_subtitles():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
    })
    restore_get_cond_visibility = __mock_get_cond_visibility(a4ksubtitles_api, {
        'Player.HasDuration': True,
        'VideoPlayer.HasSubtitles': True,
        'VideoPlayer.SubtitlesEnabled': False,
    })
    restore_get_info_label = __mock_get_info_label(a4ksubtitles_api, {
        'VideoPlayer.IMDBNumber': 'tt1234567',
    })
    restore_isplayingvideo = __mock_is_playingvideo(a4ksubtitles_api, True)

    executebuiltin_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'executebuiltin')

    service.start(a4ksubtitles_api)

    restore()
    restore_isplayingvideo()
    restore_get_cond_visibility()
    restore_get_info_label()
    executebuiltin_spy.restore()

    assert executebuiltin_spy.call_count == 1

def test_service_when_does_not_have_video_duration():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
    })
    restore_get_cond_visibility = __mock_get_cond_visibility(a4ksubtitles_api, {
        'Player.HasDuration': False,
        'VideoPlayer.HasSubtitles': False,
        'VideoPlayer.SubtitlesEnabled': False,
    })
    restore_get_info_label = __mock_get_info_label(a4ksubtitles_api, {
        'VideoPlayer.IMDBNumber': 'tt1234567',
    })
    restore_isplayingvideo = __mock_is_playingvideo(a4ksubtitles_api, True)

    executebuiltin_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'executebuiltin')

    service.start(a4ksubtitles_api)

    restore()
    restore_isplayingvideo()
    restore_get_cond_visibility()
    restore_get_info_label()
    executebuiltin_spy.restore()

    assert executebuiltin_spy.call_count == 0

def test_service_auto_download():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})

    restore = __mock(a4ksubtitles_api, {
        'general.auto_search': 'true',
        'general.auto_download': 'true',
    })
    restore_get_cond_visibility = __mock_get_cond_visibility(a4ksubtitles_api, {
        'Player.HasDuration': True,
        'VideoPlayer.HasSubtitles': False,
        'VideoPlayer.SubtitlesEnabled': False,
    })
    restore_get_info_label = __mock_get_info_label(a4ksubtitles_api, {
        'VideoPlayer.IMDBNumber': 'tt1234567',
    })
    restore_isplayingvideo = __mock_is_playingvideo(a4ksubtitles_api, True)
    restore_api_search = __mock_api_search(a4ksubtitles_api)
    expected_download_result = 'test_download_result'
    restore_api_download = __mock_api_download(a4ksubtitles_api, expected_download_result)

    executebuiltin_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc, 'executebuiltin')
    setsubtitles_spy = utils.spy_fn(a4ksubtitles_api.core.kodi.xbmc.Player(), 'setSubtitles')

    service.start(a4ksubtitles_api)

    restore()
    restore_isplayingvideo()
    restore_get_cond_visibility()
    restore_get_info_label()
    restore_api_search()
    restore_api_download()
    executebuiltin_spy.restore()

    assert executebuiltin_spy.call_count == 0
    assert setsubtitles_spy.call_count == 1
    setsubtitles_spy.called_with(expected_download_result)
