# -*- coding: utf-8 -*-

import os
import sys
import json
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

        for target in api_mode.keys():
            if target == 'kodi':
                continue
            elif api_mode[target]:
                mod = getattr(kodi_mock, target)
            else:
                mod = importlib.import_module(target)
            setattr(kodi, target, mod)

else:
    import xbmc
    import xbmcaddon
    import xbmcplugin
    import xbmcgui
    import xbmcvfs

addon = xbmcaddon.Addon('service.subtitles.a4ksubtitles')
addon_id   = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_profile = xbmc.translatePath(addon.getAddonInfo('profile'))

def create_listitem(item):
    if item['lang'] == 'Brazilian':
        item['lang'] = 'Portuguese (Brazil)'

    (item_name, item_ext) = os.path.splitext(item['name'])
    item_name = item_name.replace('.', ' ')
    item_ext = item_ext.upper()[1:]

    listitem = xbmcgui.ListItem(
        label          = item['lang'],
        label2         = '%s (%s) (%s)' % (item_name, item_ext, item['service']),
        iconImage      = item['icon'],
        thumbnailImage = item['thumbnail']
    )

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
