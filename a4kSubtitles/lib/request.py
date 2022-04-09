# -*- coding: utf-8 -*-

import requests
import urllib3
import re
import time
import ssl
import traceback
from .kodi import get_int_setting
from . import logger
from requests import adapters
from .third_party.cloudscraper import cloudscraper

class TLSAdapter(adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = urllib3.poolmanager.PoolManager(num_pools=connections,
                                                           maxsize=maxsize,
                                                           block=block,
                                                           ssl_version=ssl.PROTOCOL_TLSv1_2,
                                                           ssl_context=ctx)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def __retry(core, request, response, next, cfscrape, retry=0):
    if retry > 5:
        return None

    if response.status_code in [503, 429, 403]:
        if response.status_code == 503:
            core.time.sleep(2)
            retry = 5
        if response.status_code == 429:
            core.time.sleep(3)

        retry += 1
        request['validate'] = lambda response: __retry(core, request, response, next, cfscrape, retry)
        request['next'] = next
        request['cfscrape'] = cfscrape
        return request

def execute(core, request, progress=True, session=None):
    try: default_timeout = get_int_setting('general.timeout')
    except: default_timeout = 10
    request.setdefault('timeout', default_timeout)

    if progress and core.progress_dialog and not core.progress_dialog.dialog:
        core.progress_dialog.open()

    next = request.pop('next', None)

    cfscrape = 'cfscrape' in request
    request.pop('cfscrape', None)

    validate = request.pop('validate', None)
    if not validate:
        validate = lambda response: __retry(core, request, response, next, cfscrape)

    if next:
        request.pop('stream', None)

    logger.debug('%s ^ - %s, %s' % (request['method'], request['url'], core.json.dumps(request.get('params', {}))))
    try:
        if cfscrape:
            request.pop('cfscrape', None)
            if not session:
                session = cloudscraper.create_scraper(interpreter='native')
            response = session.request(**request)
        else:
            session = requests.session()
            session.mount('https://', TLSAdapter())
            response = session.request(**request)
        exc = ''
    except:  # pragma: no cover
        try:
            if cfscrape:
                if not session:
                    session = cloudscraper.create_scraper(interpreter='native')
                response = session.request(verify=False, **request)
            else:
                response = requests.request(verify=False, **request)
            exc = ''
        except:  # pragma: no cover
            exc = traceback.format_exc()
            response = lambda: None
            response.text = ''
            response.content = ''
            response.status_code = 500
    logger.debug('%s $ - %s - %s, %s' % (request['method'], request['url'], response.status_code, exc))

    alt_request = validate(response)
    if alt_request:
        return execute(core, alt_request, progress)

    if next and response.status_code == 200:
        next_request = next(response)
        if next_request:
            return execute(core, next_request, progress, session)
        else:
            return None

    return response
