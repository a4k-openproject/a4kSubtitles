# -*- coding: utf-8 -*-

import io
import os
import zipfile

from .common import api, pytest

__srt = b'1\n00:00:01,000 --> 00:00:02,000\nHello\n'
__name = 'Fantastic.Beasts.2016.1080p.BluRay.x264-JYK'

class __Response(object):
    status_code = 200

    def __init__(self, data):
        self.raw = io.BytesIO(data)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

def __zip(member, data=__srt):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        z.writestr(member, data)
    return buffer.getvalue()

@pytest.fixture
def download(monkeypatch, tmp_path):
    core = api.A4kSubtitlesApi({'kodi': True}).core
    monkeypatch.setattr(core.utils, 'temp_dir', str(tmp_path / 'temp'))
    monkeypatch.setattr(core, 'api_mode_enabled', True)

    def run(service_name, action_args, payload):
        monkeypatch.setattr(core.request, 'execute', lambda core_, request: __Response(payload))
        args = dict({'lang': 'English', 'url': 'https://example.com/download/1'}, **action_args)
        return core.download(core, {'service_name': service_name, 'action_args': args})

    run.core = core
    return run

def test_download_refuses_empty_file(download):
    with pytest.raises(Exception, match='empty'):
        download('opensubtitles', {'filename': __name, 'raw': True}, b'')
    # Nothing is left behind for the service to pick up as the current subtitle.
    assert download.core.utils.get_subfile_from_temp_dir() is None

def test_download_does_not_delete_an_earlier_download(download):
    first = download('opensubtitles', {'filename': __name + '-A', 'raw': True}, __srt)
    second = download('opensubtitles', {'filename': __name + '-B', 'raw': True}, __srt)
    assert os.path.isfile(first) and os.path.isfile(second)
    assert os.path.dirname(first) != os.path.dirname(second)
    assert download.core.utils.get_subfile_from_temp_dir() == second

def test_download_prunes_only_old_download_dirs(download):
    temp_dir = download.core.utils.temp_dir
    old, recent = os.path.join(temp_dir, 'old'), os.path.join(temp_dir, 'recent')
    os.makedirs(old)
    os.makedirs(recent)
    an_hour_ago = download.core.time.time() - 60 * 60
    os.utime(old, (an_hour_ago, an_hour_ago))

    download('opensubtitles', {'filename': __name, 'raw': True}, __srt)
    assert not os.path.exists(old)
    assert os.path.exists(recent)

@pytest.mark.parametrize('payload', [
    __zip('Fantastic.Beasts.srt'),
    b'Rar!\x1a\x07\x01\x00' + b'\x00' * 32,
    b'7z\xbc\xaf\x27\x1c\x00\x04' + b'\x00' * 32,
], ids=['zip', 'rar', '7z'])
def test_download_refuses_raw_archive(download, payload):
    with pytest.raises(Exception, match='archive'):
        download('opensubtitles', {'filename': __name, 'raw': True}, payload)

def test_download_refuses_zip_without_subtitle(download):
    # No subtitle member and not gzip: the archive itself used to be renamed to the subtitle name.
    with pytest.raises(Exception, match='archive'):
        download('subdl', {'filename': __name}, __zip('readme.txt', b'not a subtitle'))

@pytest.mark.parametrize('service_name, filename, member, expected', [
    ('podnadpisi', __name + '.srt', 'a.srt', __name + '.eng.srt'),
    ('podnadpisi', __name + '.srt', 'a.ass', __name + '.eng.ass'),
    ('subdl', __name, 'a.srt', __name + '.eng.srt'),
    ('subdl', __name, 'a.ass', __name + '.eng.ass'),
])
def test_download_zip_name_has_one_subtitle_extension(download, service_name, filename, member, expected):
    filepath = download(service_name, {'filename': filename}, __zip(member))
    assert os.path.basename(filepath) == expected
