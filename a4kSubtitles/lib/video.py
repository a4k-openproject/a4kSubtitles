# -*- coding: utf-8 -*-

import os
import json
import struct
import hashlib
import re
import threading

from .kodi import xbmc, xbmcvfs, get_bool_setting
from . import logger, cache, utils, request

__64k = 65536
__longlong_format_char = 'q'
__byte_size = struct.calcsize(__longlong_format_char)
__imdb_id_prefix = 'tt'

def __sum_64k_bytes(file, result):
    range_value = __64k / __byte_size
    if utils.py3:
        range_value = round(range_value)

    for _ in range(range_value):
        try: chunk = file.readBytes(__byte_size)
        except: chunk = file.read(__byte_size)
        (value,) = struct.unpack(__longlong_format_char, chunk)
        result.filehash += value
        result.filehash &= 0xFFFFFFFFFFFFFFFF

def __set_size_and_hash(core, meta, filepath):
    if core.progress_dialog and not core.progress_dialog.dialog:
        core.progress_dialog.open()

    f = xbmcvfs.File(filepath)
    try:
        filesize = meta.filesize = f.size()

        # used for mocking
        try:
            meta.filehash = f.hash()
            return
        except: pass

        if filesize < __64k * 2:
            return

        # ref: https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
        # filehash = filesize + 64bit sum of the first and last 64k of the file
        result = lambda: None
        result.filehash = filesize

        __sum_64k_bytes(f, result)
        f.seek(filesize - __64k, os.SEEK_SET)
        __sum_64k_bytes(f, result)

        meta.filehash = "%016x" % result.filehash
    finally:
        f.close()

def __get_filename(title):
    filename = title
    video_exts = ['mkv', 'mp4', 'avi', 'mov', 'mpeg', 'flv', 'wmv']

    try:
        filepath = xbmc.Player().getPlayingFile()
        filename = filepath.split('/')[-1]
        filename = utils.unquote(filename)

        for ext in video_exts:
            if ext in filename:
                filename = filename[:filename.index(ext) + len(ext)]
                break
    except: pass

    return filename

def __scrape_tvshow_year(core, meta):
    imdb_response = request.execute(core, {
        'method': 'GET',
        'url': 'https://www.imdb.com/title/' + meta.imdb_id,
        'timeout': 10,
    })

    if imdb_response.status_code != 200:
        return

    show_year_match = re.search(r' %s \((.*?)\)"' % meta.tvshow, imdb_response.text)
    if not show_year_match:
        show_year_match = re.search(r'<title>.*?\(TV (?:Mini-)?Series (\d\d\d\d).*?</title>', imdb_response.text)
    if not show_year_match:
        show_year_match = re.search(r'<span class="parentDate">\((\d\d\d\d).*?\)</span>', imdb_response.text)

    if show_year_match:
        meta.tvshow_year = show_year_match.group(1).strip()

        tvshow_years_cache = cache.get_tvshow_years_cache()
        tvshow_years_cache[meta.imdb_id] = meta.tvshow_year
        cache.save_tvshow_years_cache(tvshow_years_cache)

def __scrape_imdb_id(core, meta):
    if meta.title == '' or meta.year == '':
        return

    is_movie = meta.season == '' and meta.episode == ''

    title = (meta.title if is_movie else meta.tvshow).lower()
    year = '_%s' % meta.year if is_movie else ''
    query = '%s%s' % (title.lower().replace(' ', '_'), year)
    query = query[:20]

    request = {
        'method': 'GET',
        'url': 'https://v2.sg.media-imdb.com/suggestion/%s/%s.json' % (query[:1], query),
        'timeout': 10
    }

    response = core.request.execute(core, request)
    if response.status_code != 200:
        return

    results = core.json.loads(response.text)
    if len(results['d']) == 0:
        return

    def filter_movie_results(result):
        year_start = result.get('y', None)
        result_type = result.get('q', None)
        return (
            result_type is not None and result_type in ['feature', 'TV movie'] and
            result['l'].lower() == title and
            (year_start is not None and year_start == year)
        )

    if is_movie:
        year = int(meta.year)
        results = list(filter(filter_movie_results, results['d']))
        if len(results) > 0:
            meta.imdb_id = results[0]['id']
        return

    show_title = title.lower()
    episode_title = meta.title.lower()
    episode_year = int(meta.year)

    def filter_tvshow_results(result):
        year_start = result.get('y', None)
        year_end = result.get('yr', '-').split('-')[1]
        result_type = result.get('q', None)
        return (
            result_type is not None and result_type in ['TV series', 'TV mini-series'] and
            result['l'].lower() == show_title and
            (year_start is not None and year_start <= episode_year) and
            (year_end == '' or int(year_end) >= episode_year)
        )

    results = list(filter(filter_tvshow_results, results['d']))
    if len(results) == 0:
        return

    if len(results) == 1:
        meta.tvshow_year = str(results[0]['y'])
        meta.imdb_id = results[0]['id']
        return

    episode_title_pattern = r'title=\"' + re.escape(episode_title) + r'\"'
    for result in results:
        episodes_response = core.request.execute(core, {
            'method': 'GET',
            'url': 'https://www.imdb.com/title/%s/episodes/_ajax?season=%s' % (result['id'], meta.season),
            'timeout': 10
        })

        if episodes_response.status_code != 200:
            continue

        if re.search(episode_title_pattern, episodes_response.text, re.IGNORECASE):
            meta.tvshow_year = str(result['y'])
            meta.imdb_id = result['id']
            return

def __update_info_from_imdb(core, meta, pagination_token=''):
    request = {
        'method': 'POST',
        'url': 'https://graphql.imdb.com',
        'data': core.json.dumps({
            'query': '''
                query TitlesList($idArray: [ID!]!, $paginationToken: ID) {
                    titles(ids: $idArray) {
                        id
                        titleText {
                            text
                        }
                        releaseDate {
                            year
                        }
                        releaseDates(first: 5) {
                            edges {
                                node {
                                    country { text }
                                    year
                                }
                            }
                        }
                        series {
                            series {
                                id,
                                titleText {
                                    text
                                }
                                releaseDate {
                                    year
                                }
                            }
                            episodeNumber {
                                episodeNumber
                                seasonNumber
                            }
                        }
                        episodes {
                            ...TMD_Episodes_EpisodesCardContainer
                        }
                    }
                }

                fragment TMD_Episodes_EpisodesCardContainer on Episodes {
                    result: episodes(first: 250, after: $paginationToken) {
                        edges {
                            node {
                                ...TMD_Episodes_EpisodeCard
                            }
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }

                fragment TMD_Episodes_EpisodeCard on Title {
                    id
                    titleText {
                        text
                    }
                    releaseDate {
                        year
                    }
                    series {
                        episodeNumber {
                            episodeNumber
                            seasonNumber
                        }
                    }
                }
            ''',
            'operationName': 'TitlesList',
            'variables': {
                'idArray': [meta.imdb_id],
                'paginationToken': pagination_token
            },
        }),
        'headers': {
            'content-type': 'application/json',
        },
        'timeout': 10
    }

    response = core.request.execute(core, request)
    if response.status_code != 200:
        return

    try:
        result = json.loads(response.text)
        result = result['data']['titles'][0]

        if result['series'] is not None:
            meta.tv_show_imdb_id = result['series']['series']['id']

        if result['episodes'] is None:
            meta.title = result['titleText']['text']
            meta.year = str(result['releaseDate']['year'])
            if result['series'] is not None:
                meta.tvshow = result['series']['series']['titleText']['text']
                meta.tvshow_year = str(result['series']['series']['releaseDate']['year'])
                meta.season = str(result['series']['episodeNumber']['seasonNumber'])
                meta.episode = str(result['series']['episodeNumber']['episodeNumber'])
        else:
            meta.tvshow = result['titleText']['text']
            if meta.tvshow_year == '':
                releasesDates = result['releaseDates']
                if releasesDates is not None and len(releasesDates['edges']) > 0:
                    meta.tvshow_year = str(releasesDates['edges'][0]['node']['year'])
                else:
                    meta.tvshow_year = str(result['releaseDate']['year'])

            episodes = result['episodes']['result']['edges']
            s_number = int(meta.season)
            ep_number = int(meta.episode)
            found = False
            for episode in episodes:
                ep = episode['node']
                series = ep['series']['episodeNumber']
                if series['episodeNumber'] == ep_number and series['seasonNumber'] == s_number:
                    meta.title = ep['titleText']['text']
                    meta.year = str(ep['releaseDate']['year'])
                    meta.imdb_id = ep['id']
                    found = True
            if not found and result['episodes']['result']['pageInfo']['hasNextPage']:
                return __update_info_from_imdb(core, meta, result['episodes']['result']['pageInfo']['endCursor'])
    except:
        return

def __get_basic_info(core):
    meta = utils.DictAsObject({})
    filename_and_path = ''

    if core.kodi.get_version_major() >= 20:  # The InfoTagVideo API was added in kodi v20
        video_info = xbmc.Player().getVideoInfoTag()

        meta.year = video_info.getYear()
        meta.season = video_info.getSeason()
        meta.episode = video_info.getEpisode()
        meta.tvshow = video_info.getTVShowTitle()

        meta.title = video_info.getOriginalTitle()
        if meta.title == '':
            meta.title = video_info.getTitle()

        meta.imdb_id = video_info.getUniqueID('imdb')
        filename_and_path = video_info.getFilenameAndPath()

    if not meta.year:
        meta.year = xbmc.getInfoLabel('VideoPlayer.Year')
    if not meta.season:
        meta.season = xbmc.getInfoLabel('VideoPlayer.Season')
    if not meta.episode:
        meta.episode = xbmc.getInfoLabel('VideoPlayer.Episode')
    if not meta.tvshow:
        meta.tvshow = xbmc.getInfoLabel('VideoPlayer.TVShowTitle')

    if not meta.title:
        meta.title = xbmc.getInfoLabel('VideoPlayer.OriginalTitle')
        if meta.title == '':
            meta.title = xbmc.getInfoLabel('VideoPlayer.Title')

    if not meta.imdb_id:
        meta.imdb_id = xbmc.getInfoLabel('VideoPlayer.IMDBNumber')
    if not filename_and_path:
        filename_and_path = xbmc.getInfoLabel('Player.FilenameAndPath')

    meta.tvshow_year = ''
    meta.filename = __get_filename(meta.title)
    meta.filename_without_ext = meta.filename

    if meta.imdb_id == '':
        regex_result = re.search(r'.*(tt\d{7,}).*', filename_and_path, re.IGNORECASE)
        if regex_result:
            meta.imdb_id = regex_result.group(1)

    if meta.season == '' or meta.episode == '':
        filename_info = utils.extract_season_episode(meta.filename, zfill=0)
        filename_path_info = utils.extract_season_episode(filename_and_path, zfill=0)
        meta.season = meta.season or filename_path_info.season or filename_info.season
        meta.episode = meta.episode or filename_path_info.episode or filename_info.episode

    meta.tv_show_imdb_id = meta.imdb_id

    return meta

def __is_imdb_id(id: str) -> bool:
    return id.startswith(__imdb_id_prefix)

def get_meta(core):
    meta = __get_basic_info(core)

    # Depending on the used scraper, the imdb_id returned by Kodi might not actually be an IMDB ID.
    if meta.imdb_id == '' or not __is_imdb_id(meta.imdb_id):
        cache_key = cache.hash_data(meta)
        imdb_id_cache = cache.get_imdb_id_cache()
        meta.imdb_id = imdb_id_cache.get(cache_key, '')

        if meta.imdb_id == '':
            __scrape_imdb_id(core, meta)

            if meta.imdb_id != '':
                imdb_id_cache[cache_key] = meta.imdb_id
                cache.save_imdb_id_cache(imdb_id_cache)

            if meta.tvshow_year != '':
                tvshow_years_cache = cache.get_tvshow_years_cache()
                tvshow_years_cache[meta.imdb_id] = meta.tvshow_year
                cache.save_tvshow_years_cache(tvshow_years_cache)

    if meta.imdb_id != '':
        __update_info_from_imdb(core, meta)

    meta_cache = cache.get_meta_cache()
    if meta.imdb_id != '' and meta_cache.imdb_id == meta.imdb_id and meta_cache.filename == meta.filename:
        meta = meta_cache
    else:
        meta.filesize = ''
        meta.filehash = ''

        try:
            filepath = xbmc.Player().getPlayingFile()
            __set_size_and_hash(core, meta, filepath)
        except:
            import traceback
            traceback.print_exc()

        try:
            meta.filename_without_ext = os.path.splitext(meta.filename)[0]
        except: pass

        meta_json = json.dumps(meta, indent=2)
        logger.debug(meta_json)

        meta = json.loads(meta_json)
        meta = utils.DictAsObject(meta)

        for key in meta.keys():
            value = utils.strip_non_ascii_and_unprintable(meta[key])
            meta[key] = str(value).strip()

        cache.save_meta_cache(meta)

    meta.is_tvshow = meta.tvshow != ''
    meta.is_movie = not meta.is_tvshow

    tvshow_year_requiring_service_enabled = (
        get_bool_setting('podnadpisi', 'enabled') or
        get_bool_setting('addic7ed', 'enabled')
    )

    if meta.is_tvshow and meta.imdb_id != '' and meta.tvshow_year == '' and tvshow_year_requiring_service_enabled:
        tvshow_years_cache = cache.get_tvshow_years_cache()
        tvshow_year = tvshow_years_cache.get(meta.imdb_id, '')

        if tvshow_year != '':
            meta.tvshow_year = tvshow_year
        else:
            meta.tvshow_year_thread = threading.Thread(target=__scrape_tvshow_year, args=(core, meta))
            meta.tvshow_year_thread.start()

    try:
        if len(meta.imdb_id) > 2:
            meta.imdb_id_as_int = int(meta.imdb_id[2:].lstrip('0'))
    except: pass

    return meta
