# -*- coding: utf-8 -*-

__url = 'http://api.thesubdb.com?action={action}&hash={hash}'
__user_agent = 'SubDB/1.0 (a4kSubtitles/{version}; https://github.com/a4k-openproject/a4kSubtitles)'

def build_search_requests(core, service_name, meta):
    if meta.subdb_hash == '':
        return []

    request = {
        'method': 'GET',
        'url': __url.format(action='search', hash=meta.subdb_hash),
        'headers': {
            'User-Agent': __user_agent.format(version=core.kodi.addon_version)
        }
    }

    return [request]

def parse_search_response(core, service_name, meta, response):
    service = core.services[service_name]

    lang_ids = core.utils.get_lang_ids(meta.languages, core.kodi.xbmc.ISO_639_1)
    name = '%s.srt' % meta.filename_without_ext
    results = []

    lang_codes = response.text.split(',')
    for lang_code in lang_codes:
        if lang_code in lang_ids:
            lang = meta.languages[lang_ids.index(lang_code)]

            results.append({
                'service_name': service_name,
                'service': service.display_name,
                'lang': lang,
                'name': name,
                'rating': 0,
                'lang_code': lang_code,
                'sync': 'true',
                'impaired': 'false',
                'color': 'cyan',
                'action_args': {
                    'url': '',
                    'hash': meta.subdb_hash,
                    'lang': lang,
                    'filename': name,
                    'raw': True
                }
            })

    return results

def build_download_request(core, service_name, args):
    lang_code = core.kodi.xbmc.convertLanguage(args['lang'], core.kodi.xbmc.ISO_639_1)
    request = {
        'method': 'GET',
        'url': __url.format(action='download', hash=args['hash']) + ('&language=%s' % lang_code),
        'headers': {
            'User-Agent': __user_agent.format(version=core.kodi.addon_version)
        }
    }

    return request
