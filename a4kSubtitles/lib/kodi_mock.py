# -*- coding: utf-8 -*-
# flake8: noqa

import os
import shutil

from zipfile import ZipFile
from xml.etree import ElementTree

try:  # pragma: no cover
    from urlparse import unquote
except ImportError:
    from urllib.parse import unquote

# xbmc
xbmc = lambda: None
xbmc.translatePath = lambda p: p
xbmc.getInfoLabel = lambda t: ''
xbmc.executeJSONRPC = lambda _: '{ "result": { "value": [] } }'
xbmc.executebuiltin = lambda _: None
xbmc.getCleanMovieTitle = lambda t: t
xbmc.getCondVisibility = lambda _: False

xbmc.convertLanguage = lambda l, f: l[:f].lower()
xbmc.ISO_639_1 = 2
xbmc.ISO_639_2 = 3

__player = lambda: None
__player.getPlayingFile = lambda: ''
__player.getAvailableSubtitleStreams = lambda: []
__player.setSubtitles = lambda s: None
__player.setSubtitleStream = lambda i: None
xbmc.Player = lambda: __player

__monitor = lambda: None
__monitor.abortRequested = lambda: False
__monitor.waitForAbort = lambda _: False
xbmc.Monitor = lambda: __monitor

def __log(msg, label):
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
    elif name == 'version':
        tree = ElementTree.parse(os.path.join(os.path.dirname(__file__), '..', '..', 'addon.xml'))
        root = tree.getroot()
        return root.get('version')
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
def __mkdirs(f):
    try: os.makedirs(f)
    except Exception: pass
xbmcvfs.mkdirs = __mkdirs

__archive_proto = 'archive://'
def __listdir(archive_uri):
    archive_path = unquote(archive_uri).replace(__archive_proto, '')
    with ZipFile(archive_path, 'r') as zip_obj:
        return ([], zip_obj.namelist())
xbmcvfs.listdir = __listdir

def __copy(src_uri, dest):
    archive_path = unquote(src_uri[:src_uri.find('.zip') + 4]).replace(__archive_proto, '')
    member = unquote(src_uri[src_uri.find('.zip') + 5:]).replace(__archive_proto, '')
    with ZipFile(archive_path, 'r') as zip_obj:
        dest_dir = os.path.dirname(dest)
        zip_obj.extract(member, dest_dir)
        os.rename(os.path.join(dest_dir, member), dest)
xbmcvfs.copy = __copy

def __File(_):
    return __File
__File.size = lambda: 0
__File.hash = lambda: 0
__File.close = lambda: None
xbmcvfs.File = __File
