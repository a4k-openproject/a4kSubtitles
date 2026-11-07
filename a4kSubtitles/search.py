# -*- coding: utf-8 -*-

def __auth_service(core, service_name, request):
    service = core.services[service_name]
    response = core.request.execute(core, request)
    service.parse_auth_response(core, service_name, response)

__results_ttl = 4 * 60 * 60  # seconds a saved last_results.json may be replayed
__quick_timeout = 5  # seconds a quick search may take before it returns no rows

def __is_transport_error(response):
    # None is not an error here: request chains return None for "nothing found".
    return response is not None and (response.status_code >= 500 or response.status_code == 429)

def __query_service(core, service_name, meta, request, results, failed):
    try:
        service = core.services[service_name]
        response = core.request.execute(core, request)

        if __is_transport_error(response):
            failed.append(service_name)
            core.logger.warning('%s - search failed: %s (HTTP %s)' % (service_name, core.request.host(request['url']), response.status_code))

        if response and response.status_code == 200 and response.text:
            service_results = service.parse_search_response(core, service_name, meta, response)
        else:
            service_results = []

        results.extend(service_results)

        core.logger.debug(lambda: core.json.dumps({
            'url': request['url'],
            'count': len(service_results),
            'status_code': response.status_code if response else 'N/A'
        }, indent=2))
    finally:
        core.progress_text = core.progress_text.replace(service.display_name, '', 1)  # two services share 'OpenSubtitles'
        core.kodi.update_progress(core)

def __add_results(core, results, meta):  # pragma: no cover
    for item in results:
        listitem = core.kodi.create_listitem(item)

        action_args = core.utils.quote_plus(core.json.dumps(item['action_args']))

        core.kodi.xbmcplugin.addDirectoryItem(
            handle=core.handle,
            listitem=listitem,
            isFolder=False,
            url='plugin://%s/?action=download&service_name=%s&action_args=%s'
                % (core.kodi.addon_id, item['service_name'], action_args)
        )

def __has_results(service_name, results):
    return any(map(lambda r: r['service_name'] == service_name, results))

def __log_summary(core, searched, failed, results, cached_count):
    rows = ['%s: %s' % (name, 'failed' if name in failed else sum(1 for r in results if r and r['service_name'] == name)) for name in searched]
    core.logger.info('search - %s; %d rows from cache' % (', '.join(rows) or 'no service searched', cached_count))

def __save_results(core, meta, results, created):
    try:
        if len(results) == 0:
            return
        meta_hash = core.cache.get_meta_hash(meta)
        json_data = core.json.dumps({
            'hash': meta_hash,
            'timestamp': core.time.time(),
            # When the full search ran; a replay that refreshes bsplayer keeps it, so the TTL still ends.
            'created': created or core.time.time(),
            'results': results
        }, indent=2)
        with open(core.cache.results_filepath, 'w') as f:
            f.write(json_data)
    except:
        import traceback
        traceback.print_exc()

def __get_last_results(core, meta):
    force_search = []

    try:
        with open(core.cache.results_filepath, 'r') as f:
            last_results = core.json.loads(f.read())

        meta_hash = core.cache.get_meta_hash(meta)
        if last_results['hash'] != meta_hash:
            return ([], [], None)

        created = last_results.get('created', last_results['timestamp'])
        if core.time.time() - created > __results_ttl:
            return ([], [], None)

        has_bsplayer_results = __has_results('bsplayer', last_results['results'])
        has_bsplayer_results_expired = core.time.time() - last_results['timestamp'] > 3 * 60
        if has_bsplayer_results and has_bsplayer_results_expired:
            last_results['results'] = list(filter(lambda r: r['service_name'] != 'bsplayer', last_results['results']))
            force_search.append('bsplayer')

        return (last_results['results'], force_search, created)
    except: pass

    return ([], [], None)

def __sanitize_results(core, meta, results):
    temp_dict = {}

    for result in results:
        result['name'] = core.utils.unquote(result['name'])
        # Rows of one file from two services share a dedup_key (both OpenSubtitles services do).
        key = result.get('dedup_key') or result['action_args']['url']
        kept = temp_dict.get(key)
        if kept is None or __dedup_rank(result) > __dedup_rank(kept):
            temp_dict[key] = result

    return list(temp_dict.values())

def __dedup_rank(result):
    # Keep the synced row; else the one whose download spends no OpenSubtitles account quota.
    return (result.get('sync') == 'true', result['service_name'] != 'opensubtitles')

def __apply_language_filter(meta, results):
    return list(filter(lambda x: x and x['lang'] in meta.languages, results))

def __apply_limit(core, all_results, meta):
    # `all_results` is already in priority order: __prepare_results sorts it
    # with `sorter`, whose first key is `not x['lang'] == meta.preferredlanguage`
    # and whose second is `meta.languages.index(x['lang'])`, so the preferred
    # language leads, the other requested languages follow in request order,
    # and within a language the quality keys rank the rows. The preferred
    # language keeps the bulk of the cap, but up to min(5, limit // 4) seats
    # go to the best-ranked rows of the other requested languages so they
    # never vanish entirely. Both halves are taken in sorted order and the
    # preferred half goes first, so the sorter's order is kept.
    limit = core.kodi.get_int_setting('general.results_limit')
    preferred = [r for r in all_results if r['lang'] == meta.preferredlanguage]
    others = [r for r in all_results if r['lang'] != meta.preferredlanguage]
    if not preferred or not others:
        return all_results[:limit]

    reserved = min(5, limit // 4, len(others))
    preferred = preferred[:limit - reserved]
    return preferred + others[:limit - len(preferred)]

def __prepare_results(core, meta, results):
    results = __apply_language_filter(meta, results)
    results = __sanitize_results(core, meta, results)

    release_groups = [
        ['bluray', 'bd', 'bdrip', 'brrip', 'bdmv', 'bdscr', 'remux', 'bdremux', 'uhdremux', 'uhdbdremux', 'uhdbluray'],
        ['web', 'webdl', 'webrip', 'webr', 'webdlrip', 'webcap'],
        ['dvd', 'dvd5', 'dvd9', 'dvdr', 'dvdrip', 'dvdscr'],
        ['scr', 'screener', 'r5', 'r6']
    ]
    release = []
    for group in release_groups:
        release.extend(group)
    media_exts = ['avi', 'mp4', 'mkv', 'ts', 'm2ts', 'mts', 'mpeg', 'mpg', 'mov', 'wmv', 'flv', 'vob']
    release.extend(media_exts)

    quality_groups = [
        ['4k', '2160p', '2160', '4kuhd', '4kultrahd', 'ultrahd', 'uhd'],
        ['1080p', '1080'],
        ['720p', '720'],
        ['480p'],
        ['360p', '240p', '144p'],
    ]
    quality = []
    for group in quality_groups:
        quality.extend(group)

    service_groups = [
        ['netflix', 'nflx', 'nf'],
        ['amazon', 'amzn', 'primevideo'],
        ['hulu', 'hlu'],
        ['crunchyroll', 'cr'],
        ['disney', 'disneyplus'],
        ['hbo', 'hbonow', 'hbogo', 'hbomax', 'hmax'],
        ['bbc'],
        ['sky', 'skyq'],
        ['syfy'],
        ['atvp', 'atvplus'],
        ['pcok', 'peacock'],
    ]
    service = []
    for group in service_groups:
        service.extend(group)

    codec_groups = [
        ['x264', 'h264', '264', 'avc'],
        ['x265', 'h265', '265', 'hevc'],
        ['av1', 'vp9', 'vp8', 'divx', 'xvid'],
    ]
    codec = []
    for group in codec_groups:
        codec.extend(group)

    audio_groups = [
        ['dts', 'dtshd', 'atmos', 'truehd'],
        ['aac', 'ac'],
        ['dd', 'ddp', 'ddp5', 'dd5', 'dd2', 'dd1', 'dd7', 'ddp7'],
    ]
    audio = []
    for group in audio_groups:
        audio.extend(group)

    color_groups = [
        ['hdr', '10bit', '12bit', 'hdr10', 'hdr10plus', 'dolbyvision', 'dolby', 'vision'],
        ['sdr', '8bit'],
    ]
    color = []
    for group in color_groups:
        color.extend(group)

    extra = ['extended', 'cut', 'remastered', 'proper']

    filename = core.utils.unquote(meta.filename_without_ext).lower()
    regexsplitwords = r'[\s\.\:\;\(\)\[\]\{\}\\\/\&\€\'\`\#\@\=\$\?\!\%\+\-\_\*\^]'
    meta_nameparts = core.re.split(regexsplitwords, filename)

    release_list = [i for i in meta_nameparts if i in release]
    quality_list = [i for i in meta_nameparts if i in quality]
    service_list = [i for i in meta_nameparts if i in service]
    codec_list = [i for i in meta_nameparts if i in codec]
    audio_list = [i for i in meta_nameparts if i in audio]
    color_list = [i for i in meta_nameparts if i in color]
    extra_list = [i for i in meta_nameparts if i in extra]

    for item in release_list:
        for group in release_groups:
            if item in group:
                release_list = group
                break

    for item in quality_list:
        for group in quality_groups:
            if item in group:
                quality_list = group
                break

    for item in service_list:
        for group in service_groups:
            if item in group:
                service_list = group
                break

    for item in codec_list:
        for group in codec_groups:
            if item in group:
                codec_list = group
                break

    for item in audio_list:
        for group in audio_groups:
            if item in group:
                audio_list = group
                break

    for item in color_list:
        for group in color_groups:
            if item in group:
                color_list = group
                break

    def _filter_name(x):
        name_diff_ignore = media_exts + quality + codec + audio + color
        name_diff_ignore += ["multi", 'multiple', 'sub', 'subs', 'subtitle']

        if x.isdigit():
            x = str(int(x)).zfill(3)
        elif x.lower() in name_diff_ignore:
            x = ''
        return x.lower()

    def _match_numbers(a, b):
        offset = 0
        for s in b:
            s = core.re.sub(r'v[1-4]', "", s)
            if not s.isdigit():
                continue
            elif meta.episode and s.zfill(3) == meta.episode.zfill(3):
                offset += 0.4
            elif s in a:
                offset += 0.2

        return offset

    def sorter(x):
        name = x['name'].lower()
        nameparts = core.re.split(regexsplitwords, name)

        # Add episode number to action_args to detect the desired episode later during sub extraction.
        x['action_args'].setdefault("episodeid", meta.episode.zfill(3) if meta.episode else "")

        cleaned_nameparts = list(filter(len, map(_filter_name, nameparts)))
        cleaned_file_nameparts = list(filter(len, map(_filter_name, meta_nameparts)))
        matching_offset = 0

        if meta.is_tvshow:
            sub_info = core.utils.extract_season_episode(name)

            is_season = sub_info.season and sub_info.season == meta.season.zfill(3)
            is_episode = sub_info.episode and sub_info.episode == meta.episode.zfill(3)

            # Handle the parsed season and episode.
            if is_season and not sub_info.episode:
                matching_offset += 0.6
            if is_season and is_episode:
                matching_offset += 0.4
            elif meta.episode and int(meta.episode) in sub_info.episodes_range:
                matching_offset += 0.3
            elif sub_info.season and sub_info.episode:
                matching_offset -= 0.5

            if matching_offset == 0:
                matching_offset = _match_numbers(cleaned_file_nameparts, cleaned_nameparts)

        return (
            not x['lang'] == meta.preferredlanguage,
            meta.languages.index(x['lang']),
            not x['sync'] == 'true',
            -(core.difflib.SequenceMatcher(None, cleaned_file_nameparts, cleaned_nameparts).ratio() + matching_offset),
            -sum(i in nameparts for i in release_list) * 10,
            -sum(i in nameparts for i in quality_list) * 10,
            -sum(i in nameparts for i in codec_list) * 10,
            -sum(i in nameparts for i in service_list) * 10,
            -sum(i in nameparts for i in audio_list),
            -sum(i in nameparts for i in color_list),
            -sum(i in nameparts for i in extra_list),
            -core.difflib.SequenceMatcher(None, filename, name).ratio(),
            -x['rating'],
            not x['impaired'] == 'true',
            x['service'],
        )

    results = sorted(results, key=sorter)
    results = __apply_limit(core, results, meta)
    results = sorted(results, key=sorter)

    return results

def __parse_languages(core, languages):
    # dict.fromkeys, not a set: de-duplicated but in REQUEST order, so
    # `meta.languages.index` (the sorter's second key) is deterministic
    # instead of per-process hash order.
    return list(dict.fromkeys(language for language in (core.kodi.parse_language(x) for x in languages) if language is not None))

def __chain_auth_and_search_threads(core, auth_thread, search_thread):
    auth_thread.start()
    auth_thread.join()
    search_thread.start()
    search_thread.join()

def __wait_threads(core, request_threads):
    threads = []

    for (auth_thread, search_thread) in request_threads:
        if not auth_thread:
            threads.append(search_thread)
        else:
            thread = core.threading.Thread(target=__chain_auth_and_search_threads, args=(core, auth_thread, search_thread))
            threads.append(thread)

    core.utils.wait_threads(threads)

def __complete_search(core, results, meta):
    if core.api_mode_enabled:
        return results

    __add_results(core, results, meta)  # pragma: no cover

def __search(core, service_name, meta, results, failed):
    service = core.services[service_name]
    requests = service.build_search_requests(core, service_name, meta)
    core.logger.debug(lambda: '%s - %s' % (service_name, core.json.dumps(requests, default=lambda o: '', indent=2)))

    threads = []
    for request in requests:
        thread = core.threading.Thread(target=__query_service, args=(core, service_name, meta, request, results, failed))
        threads.append(thread)

    core.utils.wait_threads(threads)

def search(core, params):
    # params['quick']: only services with `quick = True` run, the last_results cache is neither read nor written
    # (a saved quick-only set would be replayed for the next full search), and the search gives up after __quick_timeout.
    quick = params.get('quick', False)
    meta = core.video.get_meta(core)
    core.last_meta = meta

    meta.languages = __parse_languages(core, core.utils.unquote(params['languages']).split(','))
    meta.preferredlanguage = core.kodi.parse_language(params['preferredlanguage'])
    core.logger.debug(lambda: core.json.dumps(meta, default=lambda o: '', indent=2))

    if meta.imdb_id == '':
        core.logger.error('missing imdb id!')
        core.kodi.notification('IMDB ID is not provided')
        return

    threads = []
    searched = []
    failed = []
    (results, force_search, created) = ([], [], None) if quick else __get_last_results(core, meta)
    cached_count = len(results)
    for service_name in core.services:
        if quick and not getattr(core.services[service_name], 'quick', False):
            continue

        if len(results) > 0 and (__has_results(service_name, results) or service_name not in force_search):
            continue

        if not core.kodi.get_bool_setting(service_name, 'enabled'):
            continue

        service = core.services[service_name]
        core.progress_text += service.display_name + '|'

        auth_thread = None
        auth_request = service.build_auth_request(core, service_name)
        if auth_request:
            auth_thread = core.threading.Thread(target=__auth_service, args=(core, service_name, auth_request))

        search_thread = core.threading.Thread(target=__search, args=(core, service_name, meta, results, failed))
        searched.append(service_name)

        threads.append((auth_thread, search_thread))

    if len(threads) == 0:
        __log_summary(core, searched, failed, results, cached_count)
        return __complete_search(core, results, meta)

    core.progress_text = core.progress_text[:-1]
    core.kodi.update_progress(core)

    ready_queue = core.utils.queue.Queue()
    cancellation_token = lambda: None
    cancellation_token.iscanceled = False

    def check_cancellation():  # pragma: no cover
        dialog = core.progress_dialog
        while (core.progress_dialog is not None and not cancellation_token.iscanceled):
            if not dialog.iscanceled():
                core.time.sleep(1)
                continue

            cancellation_token.iscanceled = True
            final_results = __prepare_results(core, meta, results)
            ready_queue.put(__complete_search(core, final_results, meta))
            break

    def wait_all_results():
        __wait_threads(core, threads)
        __log_summary(core, searched, failed, results, cached_count)
        if cancellation_token.iscanceled:
            return
        final_results = __prepare_results(core, meta, results)
        if not failed and not quick:  # a cached set missing a service that failed would hide it until the TTL ends
            __save_results(core, meta, final_results, created)
        ready_queue.put(__complete_search(core, final_results, meta))

    core.threading.Thread(target=check_cancellation).start()
    core.threading.Thread(target=wait_all_results).start()

    try:
        return ready_queue.get(timeout=__quick_timeout if quick else None)
    except core.utils.queue.Empty:
        core.logger.warning('quick search - no answer in %s s' % __quick_timeout)
        return []
