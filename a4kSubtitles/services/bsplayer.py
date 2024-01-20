# -*- coding: utf-8 -*-

__soap_format = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" '
                       'xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" '
                       'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                       'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
                       'xmlns:ns1="{url}">'
        '<SOAP-ENV:Body SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            '<ns1:{action}>{params}</ns1:{action}>'
        '</SOAP-ENV:Body>'
    '</SOAP-ENV:Envelope>'
)

__headers = {
    'User-Agent': 'BSPlayer/2.x (1022.12362)',
    'Content-Type': 'text/xml; charset=utf-8',
    'Connection': 'close',
}

__subdomains = [1, 2, 3, 4, 5, 6, 7, 8, 101, 102, 103, 104, 105, 106, 107, 108, 109]

def __get_url(core, service_name):
    context = core.services[service_name].context
    if not context.subdomain:
        time_seconds = core.datetime.now().second
        context.subdomain = __subdomains[time_seconds % len(__subdomains)]

    return "http://s%s.api.bsplayer-subtitles.com/v1.php" % context.subdomain

def __validate_response(core, service_name, request, response, retry=True):
    if not retry:
        return None

    def get_retry_request():
        core.time.sleep(2)
        request['validate'] = lambda response: __validate_response(core, service_name, request, response, retry=False)
        return request

    if response is None:
        return get_retry_request()

    if response.status_code != 200:
        return get_retry_request()

    response = __parse_response(core, service_name, response.text)
    if response is None:
        return None

    status_code = response.find('result/result')
    if status_code is None:
        status_code = response.find('result')

    if status_code.text != '200' and status_code.text != '402':
        return get_retry_request()

    results = response.findall('data/item')
    if not results:
        return get_retry_request()

    if len(results) == 0:
        return get_retry_request()

    return None

def __get_request(core, service_name, action, params):
    url = __get_url(core, service_name)
    headers = __headers.copy()
    headers['SOAPAction'] = '"%s#%s"' % (url, action)
    request = {
        'method': 'POST',
        'url': url,
        'data': __soap_format.format(url=url, action=action, params=params),
        'headers': headers,
        'validate': lambda response: __validate_response(core, service_name, request, response)
    }
    return request

def __parse_response(core, service_name, response):
    try:
        tree = core.ElementTree.fromstring(response.strip())
        return tree.find('.//return')
    except Exception as exc:
        core.logger.error('%s - %s' % (service_name, exc))
        return None

def __logout(core, service_name):
    context = core.services[service_name].context
    if not context.token:
        return

    action = 'logOut'
    params = '<handle>%s</handle>' % context.token
    request = __get_request(core, service_name, action, params)

    def logout():
        core.request.execute(core, request)

    context.token = None
    thread = core.threading.Thread(target=logout)
    thread.start()

def build_auth_request(core, service_name):
    action = 'logIn'
    params = (
        '<username></username>'
        '<password></password>'
        '<AppID>BSPlayer v2.72</AppID>'
    )
    return __get_request(core, service_name, action, params)

def parse_auth_response(core, service_name, response):
    if response.status_code != 200 or not response.text:
        return

    response = __parse_response(core, service_name, response.text)
    if response is None:
        return

    if response.find('result').text == '200':
        token = response.find('data').text
        core.services[service_name].context.token = token

def build_search_requests(core, service_name, meta):
    token = core.services[service_name].context.token
    if not token:
        return []

    action = 'searchSubtitles'

    lang_ids = core.utils.get_lang_ids(meta.languages)
    core.services[service_name].context.lang_ids = lang_ids

    params = (
        '<handle>{token}</handle>'
        '<movieHash>{filehash}</movieHash>'
        '<movieSize>{filesize}</movieSize>'
        '<languageId>{lang_ids}</languageId>'
        '<imdbId>{imdb_id}</imdbId>'
    ).format(
        token=token,
        filesize=meta.filesize if meta.filesize else '0',
        filehash=meta.filehash if meta.filehash else '0',
        lang_ids=','.join(lang_ids),
        imdb_id=meta.imdb_id[2:]
    )

    return [__get_request(core, service_name, action, params)]

def parse_search_response(core, service_name, meta, response):
    __logout(core, service_name)

    service = core.services[service_name]
    response = __parse_response(core, service_name, response.text)
    if response is None:
        return []

    if response.find('result/result').text != '200':
        return []

    results = response.findall('data/item')
    if not results:
        return []

    lang_ids = core.services[service_name].context.lang_ids

    def map_result(result):
        name = result.find('subName').text
        lang_id = result.find('subLang').text
        rating = result.find('subRating').text

        try:
            lang = meta.languages[lang_ids.index(lang_id)]
        except:
            lang = lang_id

        return {
            'service_name': service_name,
            'service': service.display_name,
            'lang': lang,
            'name': name,
            'rating': int(round(float(rating) / 2)) if rating else 0,
            'lang_code': core.utils.get_lang_id(lang, core.kodi.xbmc.ISO_639_1),
            'sync': 'true' if meta.filehash else 'false',
            'impaired': 'false',
            'color': 'gold',
            'action_args': {
                'url': result.find('subDownloadLink').text,
                'lang': lang,
                'filename': name,
                'gzip': True
            }
        }

    return list(map(map_result, results))

def build_download_request(core, service_name, args):
    request = {
        'method': 'GET',
        'url': args['url']
    }

    return request
