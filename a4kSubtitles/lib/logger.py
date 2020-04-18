# -*- coding: utf-8 -*-

import json
from .kodi import xbmc, addon_id

__debug_logenabled_jsonrpc = json.dumps({
    'jsonrpc': '2.0',
    'id': '1',
    'method': 'Settings.GetSettingValue',
    'params': {
        "setting": "debug.showloginfo"
    },
})

__get_debug_logenabled_err = False
def __get_debug_logenabled():
    global __get_debug_logenabled_err
    if __get_debug_logenabled_err:
        return False

    try:
        response = xbmc.executeJSONRPC(__debug_logenabled_jsonrpc)
        return json.loads(response)['result']['value']
    except:
        __get_debug_logenabled_err = True
        return False

def __log(message, level=xbmc.LOGDEBUG):
    is_lazy_msg = callable(message)
    if is_lazy_msg and level == xbmc.LOGDEBUG and not __get_debug_logenabled():
        return

    if is_lazy_msg:
        message = message()

    xbmc.log('{0}: {1}'.format(addon_id, message), level)

def notice(message):
    __log(message, xbmc.LOGNOTICE)

def info(message):
    __log(message, xbmc.LOGINFO)

def error(message):
    __log(message, xbmc.LOGERROR)

def debug(message):
    __log(message, xbmc.LOGDEBUG)
