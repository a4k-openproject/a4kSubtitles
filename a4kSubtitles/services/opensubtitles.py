# -*- coding: utf-8 -*-

__api_host = 'api.opensubtitles.com'
__api_url = 'https://%s/api/v1'
__api_key = '7IQ4FYAepMynq20VYYHyj5mVHtx3qvKa'
__user_agent = 'a4kSubtitles v3'
__content_type = 'application/json'
__date_format = '%Y-%m-%d %H:%M:%S'

def __set_api_headers(core, service_name, request, token_cache=None):
    if token_cache is None:
        cache = core.cache.get_tokens_cache()
        token_cache = cache.get(service_name, None)

    base_url = token_cache['base_url'] if token_cache else __api_host

    request['url'] = request['url'] % base_url
    request['headers'] = request.get('headers', {})
    request['headers'].update({
        'User-Agent': __user_agent,
        'Api-Key': __api_key,
        'Accept': __content_type,
        'Content-Type': __content_type,
    })

    if token_cache and 'token' in token_cache:
        request['headers']['Authorization'] = 'Bearer %s' % token_cache['token']

def build_auth_request(core, service_name):
    cache = core.cache.get_tokens_cache()
    token_cache = cache.get(service_name, None)
    if token_cache is not None and 'ttl' in token_cache:
        token_ttl = core.datetime.fromtimestamp(core.time.mktime(core.time.strptime(token_cache['ttl'], __date_format)))
        if token_ttl > core.datetime.now():
            return

    cache.pop(service_name, None)
    core.cache.save_tokens_cache(cache)

    username = core.kodi.get_setting(service_name, 'username')
    password = core.kodi.get_setting(service_name, 'password')

    if username == '' or password == '':
        core.kodi.notification('OpenSubtitles now requires authentication! Enter username/password in the addon Settings->Accounts or disable the service.')
        return

    request = {
        'method': 'POST',
        'url': __api_url + '/login',
        'data': core.json.dumps({
            'username': username,
            'password': password,
        }),
    }

    __set_api_headers(core, service_name, request, token_cache=False)

    return request

def parse_auth_response(core, service_name, response):
    response = core.json.loads(response)
    token = response.get('token', None)
    base_url = response.get('base_url', __api_host)
    allowed_downloads = response.get('user', {}).get('allowed_downloads', 0)

    if token is None:
        core.kodi.notification('OpenSubtitles authentication failed!')
        return

    if allowed_downloads == 0:
        core.kodi.notification('OpenSubtitles failed! No downloads left for today.')
        return

    token_cache = {
        'token': token,
        'base_url': base_url,
        'ttl': (core.datetime.now() + core.timedelta(days=7)).strftime(__date_format),
    }

    cache = core.cache.get_tokens_cache()
    cache[service_name] = token_cache
    core.cache.save_tokens_cache(cache)

def build_search_requests(core, service_name, meta):
    cache = core.cache.get_tokens_cache()
    token_cache = cache.get(service_name, None)
    if token_cache is None:
        return []

    if meta.is_tvshow:
        query = '%s S%.2dE%.2d' % (meta.tvshow, int(meta.season), int(meta.episode))
    else:
        query = '%s %s' % (meta.title, meta.year)

    lang_ids = core.utils.get_lang_ids(meta.languages, core.kodi.xbmc.ISO_639_1)

    params = {
        'query': query,
        'languages': ','.join(lang_ids),
        'type': 'movie' if not meta.is_tvshow else 'episode',
    }

    if meta.is_tvshow:
        params.update({
            'season_number': meta.season,
            'episode_number': meta.episode,
        })
    else:
        params.update({
            'imdb_id': meta.imdb_id[2:],
            'year': meta.year,
        })

    if meta.filehash:
        params.update({
            'moviehash': meta.filehash,
        })

    request = {
        'method': 'GET',
        'url': __api_url + '/subtitles',
        'params': params,
    }

    __set_api_headers(core, service_name, request, token_cache)

    return [request]

def parse_search_response(core, service_name, meta, response):
    try:
        results = core.json.loads(response.text)
    except Exception as exc:
        core.logger.error('%s - %s' % (service_name, exc))
        return []

    service = core.services[service_name]

    def map_result(result):
        result = result['attributes']
        imdb_id = result.get('feature_details', {}).get('imdb_id', None)
        if len(result['files']) == 0 or imdb_id is not None and imdb_id != meta.imdb_id_as_int:
            return None

        filename = result['files'][0]['file_name']
        language = core.utils.get_lang_id(result['language'], core.kodi.xbmc.ENGLISH_NAME)

        return {
            'service_name': service_name,
            'service': service.display_name,
            'lang': language,
            'name': filename,
            'rating': int(round(float(result['ratings']) / 2)),
            'lang_code': core.utils.get_lang_id(language, core.kodi.xbmc.ISO_639_1),
            'sync': 'true' if result.get('moviehash_match', False) else 'false',
            'impaired': 'true' if result['hearing_impaired'] else 'false',
            'color': 'springgreen',
            'action_args': {
                'url': result['files'][0]['file_id'],
                'lang': language,
                'filename': filename,
                'gzip': True,
            }
        }

    return list(map(map_result, results['data']))

def build_download_request(core, service_name, args):
    def download_request(response):
        result = core.json.loads(response.text)

        if not result.get('link', None) and result['remaining'] == 0:
            core.kodi.notification('OpenSubtitles failed! No downloads left for today.')
            return

        return {
            'method': 'GET',
            'url': result['link'],
            'stream': True
        }

    file_id = args['url']
    request = {
        'method': 'POST',
        'url': __api_url + '/download',
        'data': core.json.dumps({
            'file_id': file_id,
        }),
        'next': lambda r: download_request(r),
    }

    __set_api_headers(core, service_name, request)

    return request
