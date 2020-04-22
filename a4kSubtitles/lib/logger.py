# -*- coding: utf-8 -*-

from .kodi import xbmc, addon_id, get_kodi_setting

__get_debug_logenabled_err = False
def __get_debug_logenabled():
    global __get_debug_logenabled_err
    if __get_debug_logenabled_err:
        return False

    try:
        return get_kodi_setting("debug.showloginfo", log_error=False)
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
