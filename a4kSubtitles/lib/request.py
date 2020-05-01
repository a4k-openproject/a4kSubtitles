# -*- coding: utf-8 -*-

import requests
import re
import time
from .kodi import get_int_setting
from . import logger

def execute(request):
    request.setdefault('timeout', get_int_setting('general.timeout'))

    validate = request.pop('validate', None)
    next = request.pop('next', None)

    if next:
        request.pop('stream', None)

    logger.debug('%s ^ - %s' % (request['method'], request['url']))
    try:
        response = requests.request(verify=False, **request)
    except:
        response = lambda: None
        response.text = ''
        response.status_code = 500
    logger.debug('%s $ - %s - %s' % (request['method'], request['url'], response.status_code))

    if validate:
        alt_request = validate(response)
        if alt_request:
            return execute(alt_request)

    if next and response.status_code == 200:
        next_request = next(response)
        if next_request:
            return execute(next_request)
        else:
            return None

    return response
