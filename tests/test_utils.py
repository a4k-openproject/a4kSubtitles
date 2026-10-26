# -*- coding: utf-8 -*-

from .common import api


def __utils():
    return api.A4kSubtitlesApi({'kodi': True}).core.utils


def test_extract_season_episode_numbered_names():
    utils = __utils()
    for name in ['2x04.srt', '02x04.srt', 'Lost.2x04.srt', 'Lost - 2x04 - The Hunting Party.srt', 'Lost S02/2x04.srt']:
        meta = utils.extract_season_episode(name.lower(), True)
        assert (meta.season, meta.episode) == ('002', '004'), name


def test_extract_season_episode_keeps_other_names():
    utils = __utils()
    meta = utils.extract_season_episode('lost.s02e04.1920x1080.web.x264.srt', True)
    assert (meta.season, meta.episode) == ('002', '004')
    meta = utils.extract_season_episode('movie.2005.1920x1080.x264.srt')
    assert (meta.season, meta.episode) == ('', '')


def test_find_file_in_archive_season_pack():
    utils = __utils()
    namelist = ['Lost S02/2x01.srt', 'Lost S02/2x02.srt', 'Lost S02/2x04.srt', 'Lost S02/2x05.srt']
    assert utils.find_file_in_archive(None, namelist, ['.srt'], '004') == 'Lost S02/2x04.srt'
