# -*- coding: utf-8 -*-

import os

# xbmc
xbmc = lambda: None
xbmc.translatePath = lambda p: p
xbmc.getInfoLabel = lambda t: ''
xbmc.executeJSONRPC = lambda _: '{ "result": { "value": true } }'

xbmc.convertLanguage = lambda l, f: l[:3].lower()
xbmc.ISO_639_2 = None

__player = lambda: None
__player.getPlayingFile = lambda: ''
xbmc.Player = lambda: __player

def __log(msg, lebel):
    print(msg)
xbmc.log = __log
xbmc.LOGDEBUG = 'debug'
xbmc.LOGINFO = 'info'
xbmc.LOGERROR = 'error'
xbmc.LOGNOTICE = 'notice'

# xbmcaddon
xbmcaddon = lambda: None
__addon = lambda: None
def __get_addon_info(name):
    if name == 'id':
        return 'service.subtitles.a4ksubtitles'
    elif name == 'name':
        return 'a4ksubtitles'
    elif name == 'profile':
        return os.path.join(os.path.dirname(__file__), '../../tmp')
__addon.getAddonInfo = __get_addon_info
__addon.getSetting = lambda _: ''
xbmcaddon.Addon = lambda _: __addon

# xbmcplugin
xbmcplugin = lambda: None
def __add_directory_item(*args, **kwargs): return None
xbmcplugin.addDirectoryItem = __add_directory_item

# xbmcgui
xbmcgui = lambda: None
__listitem = lambda: None
__listitem.setProperty = lambda _, __: None
def __create_listitem(*args, **kwargs): return __listitem
xbmcgui.ListItem = __create_listitem

# xbmcvfs
xbmcvfs = lambda: None
