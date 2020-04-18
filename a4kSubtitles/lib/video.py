# -*- coding: utf-8 -*-

import json

from .kodi import xbmc
from . import logger

def get_meta():
    meta = {}
    meta['year'] = xbmc.getInfoLabel("VideoPlayer.Year")
    meta['season'] = xbmc.getInfoLabel("VideoPlayer.Season")
    meta['episode'] = xbmc.getInfoLabel("VideoPlayer.Episode")
    meta['tvshow'] = xbmc.getInfoLabel("VideoPlayer.TVShowTitle")
    meta['title'] = xbmc.getInfoLabel("VideoPlayer.OriginalTitle")
    if meta['title'] == '':
        meta['title'] = xbmc.getInfoLabel("VideoPlayer.Title")
    meta['imdb_id'] = xbmc.getInfoLabel("VideoPlayer.IMDBNumber")

    try:
        meta['filename'] = xbmc.Player().getPlayingFile().split('/')[-1]
    except:
        pass

    meta_json = json.dumps(meta, indent=2)
    logger.debug(meta_json)
    meta = json.loads(meta_json)

    item = lambda: None
    for key in meta.keys():
        value = meta[key]
        setattr(item, key, value.strip())

    return item
