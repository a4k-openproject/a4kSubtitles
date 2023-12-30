# -*- coding: utf-8 -*-

__url = 'https://www.addic7ed.com'

def __get_show_id(core, service_name, meta):
    service = core.services[service_name]
    tvshows = core.data[service_name].tvshows

    title = '%s (%s)' % (meta.tvshow, meta.tvshow_year)
    tvshow_id = tvshows.get(title, '')
    if tvshow_id == '':
        title = meta.tvshow
        tvshow_id = tvshows.get(meta.tvshow, '')

    service.context.referer = '%s/serie/%s/%s/%s/%s' % (__url, title, meta.season, meta.episode, meta.title)
    service.context.referer = service.context.referer.replace(' ', '_')
    return tvshow_id

def __get_language_ids(core, service_name, meta):
    languages = core.data[service_name].languages

    lang_ids = []
    for lang in meta.languages:
        lang_id = languages.get(lang, '')
        if lang_id != '':
            lang_ids.append(lang_id)

    if len(lang_ids) == 0:
        lang_ids = '1'

    return '|'.join(lang_ids)

def build_search_requests(core, service_name, meta):
    if meta.is_movie:
        return []

    if meta.tvshow_year_thread:
        meta.tvshow_year_thread.join()
    if not meta.tvshow_year:
        return []

    tvshow_id = __get_show_id(core, service_name, meta)
    if tvshow_id == '':
        return []

    params = {
        'show': tvshow_id,
        'season': meta.season,
        'langs': '|%s|' % __get_language_ids(core, service_name, meta),
    }

    request = {
        'method': 'GET',
        'url': '%s/ajax_loadShow.php' % __url,
        'params': params
    }

    return [request]

def parse_search_response(core, service_name, meta, response):
    try:
        results = response.text.split('<tr')
    except:
        return []

    service = core.services[service_name]

    pattern = (
        r'<td>(.*?)</td>' +
        r'<td>(.*?)</td>' +
        r'<td>.*?</td>' +
        r'<td>(.*?)</td>' +
        r'<td.*?>(.*?)</td>' +
        r'\s*?<td.*?>.*?</td>' +
        r'<td.*?>(.*?)</td>' +
        r'<td.*?>.*?</td>' +
        r'<td.*?>.*?</td>' +
        r'<td.*?>.*?href=\"(.*?)\".*?</td>'
    )
    regex_pattern = core.re.compile(pattern)

    def map_result(result):
        match = core.re.search(regex_pattern, result)
        if not match:
            return None

        season = match.group(1)
        episode = match.group(2)

        if meta.season != season or meta.episode != episode:
            return None

        lang = core.utils.get_lang_id(match.group(3), core.kodi.xbmc.ENGLISH_NAME)
        if lang not in meta.languages:
            return None

        lang_code = core.utils.get_lang_id(lang, core.kodi.xbmc.ISO_639_1)

        release_id = match.group(4)
        name = '%s.S%sE%s.%s.srt' % (meta.tvshow, meta.season.zfill(2), meta.episode.zfill(2), release_id)
        hearing_impaired = match.group(5)
        url = __url + match.group(6)

        return {
            'service_name': service_name,
            'service': service.display_name,
            'lang': lang,
            'name': name,
            'rating': 0,
            'lang_code': lang_code,
            'sync': 'true' if release_id in meta.title else 'false',
            'impaired': 'true' if hearing_impaired != '' else 'false',
            'color': 'deepskyblue',
            'action_args': {
                'url': url,
                'lang': lang,
                'filename': name,
                'referer': service.context.referer,
                'raw': True
            }
        }

    return list(filter(lambda v: v, map(map_result, results)))

def build_download_request(core, service_name, args):
    request = {
        'method': 'GET',
        'url': args['url'],
        'headers': {
            'referer': args['referer']
        }
    }

    return request
