# -*- coding: utf-8 -*-

from .common import api


def __utils():
    return api.A4kSubtitlesApi({'kodi': True}).core.utils


def test_shorten_filename_season_pack():
    utils = __utils()
    releases = ['Lost.S02E%02d.720p.BluRay.x264-SiNNERS' % e for e in range(1, 7)]
    name = utils.slugify_filename(' / '.join(releases) + '.eng')
    assert len(name) > 200
    short = utils.shorten_filename(name, 'eng')
    assert len(short) <= 100
    assert short.startswith('Lost.S02E01.720p.BluRay.x264-SiNNERS')
    assert short.endswith('.eng')


def test_shorten_filename_keeps_extension_and_short_names():
    utils = __utils()
    name = 'x' * 150 + '.spa.srt'
    short = utils.shorten_filename(name, 'spa')
    assert len(short) <= 100
    assert short.endswith('.spa.srt')
    assert utils.shorten_filename('Lost.S02E04.720p.eng.srt', 'eng') == 'Lost.S02E04.720p.eng.srt'
