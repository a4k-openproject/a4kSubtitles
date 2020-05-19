# -*- coding: utf-8 -*-

from a4kSubtitles.lib import utils, request, kodi

__languages_filename = 'languages.json'
__tvshows_filename = 'tvshows.json'
__etags_filename = 'etags.json'
__github_url = 'https://raw.githubusercontent.com/a4k-openproject/a4kSubtitles/master/a4kSubtitles/data/addic7ed/%s'
__github_tvshows_url = __github_url % __tvshows_filename

__dirname = utils.os.path.dirname(__file__)
__service_name = utils.os.path.basename(__dirname)
__remote_data_dir = utils.os.path.join(utils.data_dir, __service_name)
kodi.xbmcvfs.mkdirs(__remote_data_dir)

__embedded_tvshows_path = utils.os.path.join(__dirname, __tvshows_filename)
__embedded_tvshows_mtime = utils.os.path.getmtime(__embedded_tvshows_path)
__remote_tvshows_path = utils.os.path.join(__remote_data_dir, __tvshows_filename)
__remote_etags_path = utils.os.path.join(__remote_data_dir, __etags_filename)

if not utils.os.path.exists(__remote_tvshows_path) or utils.os.path.getmtime(__remote_tvshows_path) < __embedded_tvshows_mtime:
    utils.shutil.copyfile(__embedded_tvshows_path, __remote_tvshows_path)

languages = utils.get_json(__file__, __languages_filename)
try:
    tvshows = utils.get_json(__remote_data_dir, __tvshows_filename)
except:
    tvshows = utils.get_json(__file__, __tvshows_filename)

def __download_data(url, etag, destpath):
    response = request.execute(utils.core, {
        'method': 'GET',
        'url': url,
        'headers': {
            'If-None-Match': etag
        }
    }, progress=False)
    if response.status_code != 200:
        return

    with open(destpath, 'wb') as f_out:
        f_out.write(response.content)

    etags = {'tvshows': response.headers['etag']}
    with open(__remote_etags_path, 'w') as f_out:
        f_out.write(utils.json.dumps(etags, indent=2))

__tvshows_etag = ''
if utils.os.path.exists(__remote_etags_path):
    __etags = utils.get_json(__remote_data_dir, __etags_filename)
    __tvshows_etag = __etags.get('tvshows', '')

utils.core.threading.Thread(target=__download_data,
                            args=(__github_tvshows_url, __tvshows_etag, __remote_tvshows_path)).start()
