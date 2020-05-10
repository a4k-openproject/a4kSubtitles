# -*- coding: utf-8 -*-

__search_url = 'https://rest.opensubtitles.org/search/'
__user_agent = 'TemporaryUserAgent'

def __set_auth_header(core, service_name, request):
    username = core.kodi.get_setting(service_name, 'username')
    password = core.kodi.get_setting(service_name, 'password')

    if username == '' or password == '':
        return

    token = '%s:%s' % (username, password)
    if core.utils.py3:
        token = token.encode('ascii')

    request['headers']['Authorization'] = 'Basic %s' % core.b64encode(token).decode('ascii')

def build_search_requests(core, service_name, meta):
    if meta.is_tvshow:
        query = "%s S%.2dE%.2d" % (meta.tvshow, int(meta.season), int(meta.episode))
    else:
        query = '%s %s' % (meta.title, meta.year)

    params = [
        'imdbid-%s' % meta.imdb_id[2:],
        'query-%s' % core.utils.quote_plus(query)
    ]

    lang_id_params = []
    lang_ids = core.utils.get_lang_ids(meta.languages)
    for lang_id in lang_ids:
        lang_id_params.append('/sublanguageid-%s' % lang_id)

    if meta.is_tvshow:
        params.extend([
            'season-%s' % meta.season,
            'episode-%s' % meta.episode,
        ])

    params_with_hash = [
        'moviebytesize-%s' % meta.filesize,
        'moviehash-%s' % meta.filehash,
    ]
    params_with_hash.extend(params)

    request = {
        'method': 'GET',
        'url': __search_url + '/'.join(params),
        'headers': {
            'X-User-Agent': __user_agent
        }
    }

    __set_auth_header(core, service_name, request)

    requests = []
    if len(lang_ids) > 2:
        request_hash = request.copy()
        request_hash['url'] = __search_url + '/'.join(params_with_hash)
        requests = [request, request_hash]
    else:
        requests = []
        for lang_id_param in lang_id_params:
            request_lang = request.copy()
            request_lang['url'] = request_lang['url'] + lang_id_param
            requests.append(request_lang)

            if meta.filehash and meta.filesize:
                request_hash = request.copy()
                request_hash['url'] = __search_url + '/'.join(params_with_hash) + lang_id_param
                requests.append(request_hash)

    return requests

def parse_search_response(core, service_name, meta, response):
    try:
        results = core.json.loads(response.text)
    except Exception as exc:
        core.logger.error('%s - %s' % (service_name, exc))
        return []

    service = core.services[service_name]

    def map_result(result):
        return {
            'service_name': service_name,
            'service': service.display_name,
            'lang': result['LanguageName'],
            'name': result['SubFileName'],
            'rating': int(round(float(result['SubRating']) / 2)),
            'lang_code': result['ISO639'],
            'sync': 'true' if result['MovieHash'] == meta.filehash else 'false',
            'impaired': 'false' if result['SubHearingImpaired'] == '0' else 'true',
            'color': 'springgreen',
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
