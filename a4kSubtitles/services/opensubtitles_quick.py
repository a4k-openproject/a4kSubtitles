# -*- coding: utf-8 -*-

# OpenSubtitles results with no account: one fast GET per search.
__host = 'opensubtitles-v3.strem.io'  # public OpenSubtitles mirror API
__download_domain = '.' + __host.split('.', 1)[1]
__timeout = 5
quick = True  # runs in quick searches (search params['quick'], A4kSubtitlesApi.quick_search)

def __retry_once(request):
    def validate(response):
        if response.status_code >= 500 or response.status_code == 429:
            return dict(request, validate=lambda _: None)
    return validate

def __is_download_url(core, url):
    return url.startswith('https://') and (core.request.host(url) or '').endswith(__download_domain)

def build_search_requests(core, service_name, meta):
    if meta.is_tvshow:
        imdb_id = meta.tv_show_imdb_id or meta.imdb_id
        if not meta.season.isdigit() or not meta.episode.isdigit():
            return []
        path = 'series/%s:%d:%d' % (imdb_id, int(meta.season), int(meta.episode))
    else:
        imdb_id = meta.imdb_id
        path = 'movie/%s' % imdb_id

    if not imdb_id.startswith('tt'):
        return []

    request = {
        'method': 'GET',
        'url': 'https://%s/subtitles/%s.json' % (__host, path),
        'timeout': __timeout,
    }
    request['validate'] = __retry_once(request)

    return [request]

def parse_search_response(core, service_name, meta, response):
    try:
        subtitles = core.json.loads(response.text).get('subtitles', [])
    except Exception as exc:
        core.logger.error('%s - %s' % (service_name, exc))
        return []

    service = core.services[service_name]
    lang_format = core.kodi.xbmc.ISO_639_2
    # The API sends ISO 639-2 codes (B or T form, plus 'pob'); match them against the requested languages.
    languages = {core.utils.get_lang_id(lang, lang_format): lang for lang in meta.languages}
    languages.pop('', None)

    results = []
    for item in subtitles:
        lang = languages.get(core.utils.get_lang_id(item.get('lang', ''), lang_format))
        url = item.get('url', '')
        if not lang or not __is_download_url(core, url):
            continue

        filename = item.get('subtitleFileName') or item.get('movieReleaseName') or 'OpenSubtitles %s' % item.get('id', '')
        results.append({
            'service_name': service_name,
            'service': service.display_name,
            'lang': lang,
            'name': filename,
            'rating': 0,
            'lang_code': core.utils.get_lang_id(lang, core.kodi.xbmc.ISO_639_1),
            'sync': 'false',
            'impaired': 'false',
            'color': 'springgreen',
            # Same id as the opensubtitles service's legacy_subtitle_id: search keeps one row per file.
            'dedup_key': 'opensubtitles:%s' % item['id'] if item.get('id') else None,
            'action_args': {
                'url': url,
                'lang': lang,
                'filename': filename,
                'raw': True
            }
        })

    return results

def build_download_request(core, service_name, args):
    if not __is_download_url(core, args['url']):
        raise Exception('Failed to download subtitle (unexpected host)')

    return {
        'method': 'GET',
        'url': args['url'],
        'stream': True
    }
