# -*- coding: utf-8 -*-

import requests
import re
import time
from .kodi import get_int_setting
from . import logger

def execute(request):
    request.setdefault('timeout', get_int_setting('general.timeout'))

    validate_response = request.get('validate_response', None)
    request.pop('validate_response', None)

    logger.debug('%s ^ - %s' % (request['method'], request['url']))
    try:
        response = requests.request(**request)
    except:
        response = lambda: None
        response.text = ''
        response.status_code = 500
    logger.debug('%s $ - %s - %s' % (request['method'], request['url'], response.status_code))

    if validate_response:
        alternative_request = validate_response(response)
        if alternative_request:
            return execute(alternative_request)

    return response
