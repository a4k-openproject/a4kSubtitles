# -*- coding: utf-8 -*-

__user_agent = 'TemporaryUserAgent'

def __set_auth_header(core, service_name, request):
    username = core.kodi.get_setting(service_name, 'username')
    password = core.kodi.get_setting(service_name, 'password')

    if username == '' or password == '':
        return

    token = '%s:%s' % (username, password)
    if core.utils.PY3:
        token = token.encode('ascii')

    request['headers']['Authorization'] = 'Basic %s' % core.b64encode(token).decode('ascii')

def build_search_requests(core, service_name, meta):
    params = [
        'imdbid-%s' % meta.imdb_id[2:]
    ]

    if core.kodi.get_bool_setting(service_name, 'use_filehash'):
        if meta.filesize:
            params.append('moviebytesize-%s' % meta.filesize)

        if meta.filehash:
            params.append('moviehash-%s' % meta.filehash)

    request = {
        'method': 'GET',
        'url': 'https://rest.opensubtitles.org/search/%s' % '/'.join(params),
        'headers': {
            'X-User-Agent': __user_agent
        }
    }

    __set_auth_header(core, service_name, request)

    lang_ids = core.utils.get_lang_ids(meta.languages)
    if len(lang_ids) > 2:
        return [request]

    requests = []
    for lang_id in lang_ids:
        request_copy = request.copy()
        request_copy['url'] = request_copy['url'] + ('/sublanguageid-%s' % lang_id)
        requests.append(request_copy)

    return requests

def parse_search_response(core, service_name, meta, response):
    try:
        results = core.json.loads(response)
    except Exception as exc:
        core.logger.error('%s - %s' % (service_name, exc))
        return []

    def map_result(result):
        return {
            'service_name': service_name,
            'service': 'OpenSubtitles',
            'lang': result['LanguageName'],
            'name': result['SubFileName'],
            'icon': str(int(round(float(result['SubRating']) / 2))),
            'thumbnail': result['ISO639'],
            'sync': 'true' if result['MovieHash'] == meta.filehash else 'false',
            'impaired': 'false' if result['SubHearingImpaired'] == '0' else 'true',
            'action_args': {
                'url': result['ZipDownloadLink'].replace('/subad/', '/sub/'),
                'lang': result['LanguageName'],
                'filename': result['SubFileName']
            }
        }

    return list(map(map_result, results))

def build_download_request(core, service_name, args):
    request = {
        'method': 'GET',
        'url': args['url'],
        'headers': {
            'X-User-Agent': __user_agent
        }
    }

    __set_auth_header(core, service_name, request)

    return request
