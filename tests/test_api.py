# -*- coding: utf-8 -*-

from .common import pytest, api

def test_api_mocking():
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
