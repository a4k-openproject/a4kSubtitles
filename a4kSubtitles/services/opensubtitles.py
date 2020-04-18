# -*- coding: utf-8 -*-

class subtitles(object):
    @staticmethod
    def build_search_requests(core, service_name, meta):
        params = [
            'imdbid-%s' % meta.imdb_id[2:]
        ]

        lang_ids = []
        for language in meta.languages:
            if language == "Portuguese (Brazil)":
                lang_id = "pob"
            elif language == "Greek":
                lang_id = "ell"
            else:
                lang_id = core.kodi.xbmc.convertLanguage(language, core.kodi.xbmc.ISO_639_2)
            lang_ids.append(lang_id)

        request = {
            'method': 'GET',
            'url': 'https://rest.opensubtitles.org/search/%s' % '/'.join(params),
            'headers': {
                'X-User-Agent': 'TemporaryUserAgent'
            }
        }

        if len(lang_ids) > 2:
            [request]

        requests = []
        for lang_id in lang_ids:
            request_copy = request.copy()
            request_copy['url'] = request_copy['url'] + ('/sublanguageid-%s' % lang_id)
            requests.append(request_copy)

        return requests

    @staticmethod
    def parse_response(core, service_name, response):
        try:
            results = core.json.loads(response)
        except Exception as exc:
            core.logger.error('%s - %s' % (service_name, exc))
            return []

        def map_result(result):
            return {
                'service': 'OpenSubtitles',
                'lang': result['LanguageName'],
                'name': result['SubFileName'],
                'icon': str(int(round(float(result['SubRating'])/2))),
                'thumbnail': result['ISO639'],
                'sync': 'false',
                'impaired': 'false' if result['SubHearingImpaired'] == '0' else 'true',
                'action_args': {
                    'url': result['ZipDownloadLink']
                }
            }

        return map(map_result, results)

    @staticmethod
    def build_download_request(core, service_name, args):
        request = {
            'method': 'GET',
            'url': args['url'],
            'headers': {
                'X-User-Agent': 'TemporaryUserAgent'
            }
        }

        username = core.kodi.get_setting(service_name, 'username')
        password = core.kodi.get_setting(service_name, 'password')
        token = '%s:%s' % (username, password)

        if username != '' and password != '':
            request['headers']['Authorization'] = 'Basic %s' % core.b64encode(token).decode('ascii')

        return request
