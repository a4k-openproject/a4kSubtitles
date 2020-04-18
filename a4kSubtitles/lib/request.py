# -*- coding: utf-8 -*-

import requests
from .kodi import get_int_setting
from . import logger

def execute(request):
    logger.debug('%s ^ - %s' % (request['method'], request['url']))
    response = requests.request(timeout=get_int_setting('general.timeout'), **request)
    logger.debug('%s $ - %s' % (request['method'], request['url']))
    return response
