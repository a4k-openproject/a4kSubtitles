# -*- coding: utf-8 -*-

import os
import sys
import json
import re
import importlib

kodi = sys.modules[__name__]
api_mode = os.getenv('A4KSUBTITLES_API_MODE')

if api_mode:
    try: api_mode = json.loads(api_mode)
    except: api_mode = None

if api_mode:
    if api_mode.get('kodi', False):
        from .kodi_mock import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
    else:
        from . import kodi_mock

        for target in ['xbmc', 'xbmcaddon', 'xbmcplugin', 'xbmcgui', 'xbmcvfs']:
            if target == 'kodi':
                continue
            elif api_mode.get(target, False):
                mod = getattr(kodi_mock, target)
            else:
                mod = importlib.import_module(target)
            setattr(kodi, target, mod)

else:  # pragma: no cover
    import xbmc
    import xbmcaddon
    import xbmcplugin
    import xbmcgui
    import xbmcvfs

addon = xbmcaddon.Addon('service.subtitles.a4ksubtitles')
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')
addon_icon = addon.getAddonInfo('icon')
try:
    addon_profile = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
except:
    addon_profile = xbmc.translatePath(addon.getAddonInfo('profile'))

def json_rpc(method, params, log_error=True):  # pragma: no cover
    try:
        result = xbmc.executeJSONRPC(
            json.dumps({
                'jsonrpc': '2.0',
                'method': method,
                'id': 1,
                'params': params or {}
            })
        )
        if 'error' in result and log_error:
            from . import logger
            logger.error(result)
        return json.loads(result)['result']['value']
    except KeyError:
        return None

def get_kodi_setting(setting, log_error=True):  # pragma: no cover
    return json_rpc('Settings.GetSettingValue', {"setting": setting}, log_error)

def notification(text, time=3000):  # pragma: no cover
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (addon_name, text, time, addon_icon))

def get_progress_dialog():  # pragma: no cover
    wrapper = lambda: None
    wrapper.dialog = None
    wrapper.latest_update = None
    def open():
        wrapper.dialog = xbmcgui.DialogProgress()
        wrapper.dialog.create(addon_name, 'Searching...')
        if wrapper.latest_update:
            (progress, text) = wrapper.latest_update
            wrapper.dialog.update(progress, text)
    def close():
        if wrapper.dialog:
            wrapper.dialog.close()
            wrapper.dialog = None
    def iscanceled():
        return wrapper.dialog.iscanceled() if wrapper.dialog else False
    def update(progress, text):
        if wrapper.dialog:
            wrapper.dialog.update(progress, text)
        else:
            wrapper.latest_update = (progress, text)
    wrapper.open = open
    wrapper.close = close
    wrapper.iscanceled = iscanceled
    wrapper.update = update
    return wrapper

def update_progress(core):  # pragma: no cover
    if core.progress_dialog is None or core.progress_dialog.iscanceled():
        return

    text = re.sub(r'\|+', '|', core.progress_text).strip('|')
    total = core.progress_text.count('|') + 1
    count = text.count('|') + 1 if text != '' else 0
    progress = int(float(total - count) / total * 100)
    core.progress_dialog.update(progress, text.replace('|', ' | '))

def parse_language(language):  # pragma: no cover
    if language == 'original':
        audio_streams = xbmc.Player().getAvailableAudioStreams()
        if len(audio_streams) == 0:
            return None
        return xbmc.convertLanguage(
            audio_streams[0],
            xbmc.ENGLISH_NAME
        )
    elif language == 'default':
        return xbmc.getLanguage()
    elif language == 'none':
        return None
    elif language == 'forced_only':
        return parse_language(get_kodi_setting("locale.audiolanguage"))
    else:
        return language

def create_listitem(item):  # pragma: no cover
    if item['lang'] == 'Brazilian':
        item['lang'] = 'Portuguese (Brazil)'

    (item_name, item_ext) = os.path.splitext(item['name'])
    item_name = item_name.replace('.', ' ')
    item_ext = item_ext.upper()[1:]
    item_service = item['service']
    item_color = item.get('color', 'white')

    args = {
        'label': item['lang'],
        'label2': '%s ([B]%s[/B]) ([B][COLOR %s]%s[/COLOR][/B])' % (item_name, item_ext, item_color, item_service),
        'offscreen': True,
    }

    listitem = xbmcgui.ListItem(**args)
    listitem.setArt({
        'icon': str(item['rating']),
        'thumb': item['lang_code'],
    })
    listitem.setProperty('sync', item['sync'])
    listitem.setProperty('hearing_imp', item['impaired'])

    return listitem

def get_setting(group, id=None):
    key = '%s.%s' % (group, id) if id else group
    return addon.getSetting(key).strip()

def get_int_setting(group, id=None):
    return int(get_setting(group, id))

def get_bool_setting(group, id=None):
    return get_setting(group, id).lower() == 'true'
