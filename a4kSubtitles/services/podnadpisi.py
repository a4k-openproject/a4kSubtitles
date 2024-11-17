# -*- coding: utf-8 -*-

__url = 'https://www.podnapisi.net'

def build_search_requests(core, service_name, meta):
    params = {
        'keywords': meta.title if meta.is_movie else meta.tvshow,
        'language': core.utils.get_lang_ids(meta.languages, core.kodi.xbmc.ISO_639_1),
    }

    if meta.is_tvshow:
        params['seasons'] = meta.season
        params['episodes'] = meta.episode
        params['movie_type'] = ['tv-series', 'mini-series']

        if meta.tvshow_year_thread:
            meta.tvshow_year_thread.join()
        if meta.tvshow_year:
            params['year'] = meta.tvshow_year
    else:
        params['movie_type'] = 'movie'
        params['year'] = meta.year

    request = {
        'method': 'GET',
        'url': '%s/subtitles/search/advanced' % __url,
        'headers': {
            'Accept': 'application/json'
        },
        'params': params
    }

    return [request]

def parse_search_response(core, service_name, meta, response):
    try:
        results = core.json.loads(response.text)
    except Exception as exc:
        core.logger.error('%s - %s' % (service_name, exc))
        return []

    service = core.services[service_name]
    lang_ids = core.utils.get_lang_ids(meta.languages, core.kodi.xbmc.ISO_639_1)

    def map_result(result):
        name = ''
        last_similarity = -1

        for release_name in result['custom_releases']:
            similarity = core.difflib.SequenceMatcher(None, release_name, meta.filename_without_ext).ratio()
            if similarity > last_similarity:
                last_similarity = similarity
                name = release_name

        if name == '':
            name = '%s %s' % (meta.title, meta.year)
            if meta.is_tvshow:
                name = '%s S%sE%s' % (meta.tvshow, meta.season.zfill(2), meta.episode.zfill(2))

        name = '%s.srt' % name
        lang_code = result['language']
        lang = meta.languages[lang_ids.index(lang_code)]

        return {
            'service_name': service_name,
            'service': service.display_name,
            'lang': lang,
            'name': name,
            'rating': 0,
            'lang_code': lang_code,
            'sync': 'true' if meta.filename_without_ext in result['custom_releases'] else 'false',
            'impaired': 'true' if 'hearing_impaired' in result['flags'] else 'false',
            'color': 'orange',
            'action_args': {
                'url': '%s%s' % (__url, result['download']),
                'lang': lang,
                'filename': name,
            }
        }

    return list(map(map_result, results['data']))

def build_download_request(core, service_name, args):
    def retry_download(response):
        if response.status_code >= 500:
            return {
                'method': 'GET',
                'url': args['url']
            }

    request = {
        'method': 'GET',
        'url': args['url'],
        'error': lambda r: retry_download(r),
    }

    return request
