# -*- coding: utf-8 -*-

__url = 'https://subscene.com'

def __match_title(core, title, year, response):
    title_with_year = '%s (%s)' % (title, year)
    href_regex = r'<a href="(.*?)">' + core.re.escape(title_with_year) + r'</a>'
    return core.re.search(href_regex, response.text, core.re.IGNORECASE)

def __find_title_result(core, service_name, meta, title, response):
    result = __match_title(core, title, meta.year, response)
    if not result:
        prev_year = int(meta.year) - 1
        result = __match_title(core, title, prev_year, response)

    if not result:
        return None

    title_href = result.group(1)
    core.services[service_name].context.title_href = title_href

    request = {
        'cfscrape': True,
        'method': 'GET',
        'url': __url + title_href
    }

    return request

def build_search_requests(core, service_name, meta):
    title = meta.title

    if meta.is_tvshow:
        ordinal_season = core.num2ordinal.convert(meta.season).strip()
        title = '%s - %s Season' % (meta.tvshow, ordinal_season)

    request = {
        'cfscrape': True,
        'method': 'GET',
        'url': __url + ('/subtitles/searchbytitle?query=' + core.utils.quote_plus(title)),
        'next': lambda r: __find_title_result(core, service_name, meta, title, r),
    }

    return [request]

def parse_search_response(core, service_name, meta, response):
    service = core.services[service_name]
    title_href = service.context.title_href
    any_regex = r'.*?'

    results_regex = (
            r'<a href="' + core.re.escape(title_href) + r'(.*?)">' +
                any_regex + r'</span>' + any_regex +
                r'<span>(.*?)</span>' + any_regex +
            r'</a>' + any_regex +
            r'(<td class="a41">)?' + any_regex +
        r'</tr>'
    )

    results = core.re.findall(results_regex, response.text, core.re.DOTALL)
    if not results:
        return None

    episodeid = 's%se%s' % (meta.season.zfill(2), meta.episode.zfill(2))
    if meta.is_tvshow:
        identifier = r'(\.s%s\.|%s)' % (meta.season.zfill(2), episodeid)
        results = list(filter(lambda x: core.re.search(identifier, x[1], core.re.IGNORECASE), results))

    def map_result(result):
        download_href = '%s%s%s' % (__url, title_href, result[0])
        lang_original = result[0].split('/')[1]
        lang = core.utils.get_lang_id(lang_original.split('_')[-1].capitalize(), core.kodi.xbmc.ENGLISH_NAME)
        lang_code = core.utils.get_lang_id(lang, core.kodi.xbmc.ISO_639_1)
        name = result[1].strip()
        name_with_ext = '%s.srt' % name
        impaired = result[2] != ''

        return {
            'service_name': service_name,
            'service': service.display_name,
            'lang': lang,
            'name': name_with_ext,
            'rating': 0,
            'lang_code': lang_code,
            'sync': 'true' if meta.filename_without_ext == name else 'false',
            'impaired': 'true' if impaired else 'false',
            'color': 'dodgerblue',
            'action_args': {
                'url': download_href,
                'lang': lang_original,
                'filename': name_with_ext,
                'episodeid': '' if meta.is_movie else episodeid
            }
        }

    return list(map(map_result, results))

def build_download_request(core, service_name, args):
    download_url = '/subtitles/%s-text/' % args['lang'].lower()
    href_regex = r'<a href="(' + core.re.escape(download_url) + r'.*?)"'

    def find_download_href(response):
        result = core.re.search(href_regex, response.text)
        if not result:
            return None

        return {
            'cfscrape': True,
            'method': 'GET',
            'url': '%s%s' % (__url, result.group(1)),
            'stream': True
        }

    request = {
        'cfscrape': True,
        'method': 'GET',
        'url': args['url'],
        'next': lambda r: find_download_href(r)
    }

    return request
