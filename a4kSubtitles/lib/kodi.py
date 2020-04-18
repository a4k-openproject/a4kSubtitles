# -*- coding: utf-8 -*-

import os

try:
    import xbmc
    import xbmcaddon
    import xbmcplugin
    import xbmcgui
    import xbmcvfs
except:
    pass

addon = xbmcaddon.Addon()
addon_id   = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_profile = xbmc.translatePath(addon.getAddonInfo('profile'))

def create_listitem(item):
    if item['lang'] == 'Brazilian':
        item['lang'] = 'Portuguese (Brazil)'

    (item_name, item_ext) = os.path.splitext(item['name'])
    item_name = item_name.replace('.', '')
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

def get_setting(service_name, id):
    return addon.getSetting('%s.%s' % (service_name, id)).strip()
