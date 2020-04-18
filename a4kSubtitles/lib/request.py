# -*- coding: utf-8 -*-

import requests
from . import logger

def execute(request):
    logger.debug('%s ^ - %s' % (request['method'], request['url']))
    response = requests.request(timeout=15, **request)
    logger.debug('%s $ - %s' % (request['method'], request['url']))
    return response
