# -*- coding: utf-8 -*-

def __auth_service(core, service_name, request):
    service = core.services[service_name]
    response = core.request.execute(request)
    if response.status_code == 200 and response.text:
        service.parse_auth_response(core, service_name, response.text)

def __query_service(core, service_name, meta, request, results):
    service = core.services[service_name]
    response = core.request.execute(request)
    if response and response.status_code == 200 and response.text:
        service_results = service.parse_search_response(core, service_name, meta, response)
    else:
        service_results = []

    results.extend(service_results)

    core.logger.debug(lambda: core.json.dumps({
        'url': request['url'],
        'count': len(service_results),
        'status_code': response.status_code
    }, indent=2))

def __add_results(core, results):
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

def __save_results(core, meta, results):
    try:
        if len(results) == 0:
            return
        meta_hash = core.utils.get_hash(meta)
        json_data = core.json.dumps({'hash': meta_hash, 'results': results}, indent=2)
        with open(core.utils.results_filepath, 'w') as f:
            f.write(json_data)
    except:
        import traceback
        traceback.print_exc()

def __get_last_results(core, meta):
    try:
        with open(core.utils.results_filepath, 'r') as f:
            last_results = core.json.loads(f.read())

        meta_hash = core.utils.get_hash(meta)
        if last_results['hash'] == meta_hash:
            return last_results['results']
    except: pass

    return []

def __sanitize_results(core, meta, results):
    temp_dict = {}

    for result in results:
        temp_dict[result['action_args']['url']] = result

        try:
            if result['sync'] == 'true':
                ext = core.os.path.splitext(result['name'])[1]
                result['name'] = '%s%s' % (meta.filename_without_ext, ext)
        except: pass

        result['name'] = core.utils.unquote(result['name'])

    return list(temp_dict.values())

def __apply_language_filter(meta, results):
    return list(filter(lambda x: x['lang'] in meta.languages, results))

def __apply_limit(core, all_results, meta):
    limit = core.kodi.get_int_setting('general.results_limit')
    lang_limit = int(limit / len(meta.languages))
    if lang_limit * len(meta.languages) < limit:
        lang_limit += 1

    results = []
    for lang in meta.languages:
        lang_results = list(filter(lambda x: x['lang'] == lang, all_results))
        if len(lang_results) < lang_limit:
            lang_limit += lang_limit - len(lang_results)
        results.extend(lang_results[:lang_limit])

    return results[:limit]

def __parse_languages(core, languages):
    return list({language for language in (__parse_language(core, x) for x in languages) if language is not None})

def __parse_language(core, language):
    if language == 'original':
        audio_streams = core.kodi.xbmc.Player().getAvailableAudioStreams()
        if len(audio_streams) == 0:
            return None
        return core.kodi.xbmc.convertLanguage(
            audio_streams[0],
            core.kodi.xbmc.ENGLISH_NAME
        )
    elif language == 'default':
        return core.kodi.xbmc.getLanguage()
    elif language == 'none':
        return None
    elif language == 'forced_only':
        return __parse_language(core, core.kodi.get_kodi_setting("locale.audiolanguage"))
    else:
        return language

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

def __complete_search(core, results):
    if core.api_mode_enabled:
        return results
    __add_results(core, results)

def __search(core, service_name, meta, results):
    service = core.services[service_name]
    requests = service.build_search_requests(core, service_name, meta)
    core.logger.debug(lambda: '%s - %s' % (service_name, core.json.dumps(requests, default=lambda o: '', indent=2)))

    threads = []
    for request in requests:
        thread = core.threading.Thread(target=__query_service, args=(core, service_name, meta, request, results))
        threads.append(thread)

    core.utils.wait_threads(threads)

def search(core, params):
    core.logger.debug(lambda: core.json.dumps(params, indent=2))
    meta = core.video.get_meta()
    meta.languages = __parse_languages(core, core.utils.unquote(params['languages']).split(','))
    meta.preferredlanguage = __parse_language(core, params['preferredlanguage'])

    if meta.imdb_id == '':
        core.logger.error('missing imdb id!')
        return

    threads = []
    results = []
    last_query_results = __get_last_results(core, meta)
    for service_name in core.services:
        if not core.kodi.get_bool_setting(service_name, 'enabled'):
            continue

        last_results = list(filter(lambda r: r['service_name'] == service_name, last_query_results))
        if len(last_results) > 0:
            core.logger.notice('%s using cached results' % service_name)
            results.extend(last_results)
            continue

        service = core.services[service_name]
        auth_thread = None

        auth_request = service.build_auth_request(core, service_name)
        if auth_request:
            auth_thread = core.threading.Thread(target=__auth_service, args=(core, service_name, auth_request))

        search_thread = core.threading.Thread(target=__search, args=(core, service_name, meta, results))

        threads.append((auth_thread, search_thread))

    if len(threads) == 0:
        return __complete_search(core, last_query_results)

    __wait_threads(core, threads)
    results = __apply_language_filter(meta, results)
    results = __sanitize_results(core, meta, results)

    sorter = lambda x: (
        not x['lang'] == meta.preferredlanguage,
        meta.languages.index(x['lang']),
        not x['sync'] == 'true',
        -core.difflib.SequenceMatcher(None, x['name'], meta.filename).ratio(),
        -x['rating'],
        not x['impaired'] == 'true',
        x['service'],
    )

    results = sorted(results, key=sorter)
    results = __apply_limit(core, results, meta)
    results = sorted(results, key=sorter)
    __save_results(core, meta, results)

    return __complete_search(core, results)
