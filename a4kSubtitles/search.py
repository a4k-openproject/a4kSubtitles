# -*- coding: utf-8 -*-

def __query_service(core, service_name, request, results):
    service = core.services[service_name]
    response = core.request.execute(request)
    service_results = service.parse_response(core, service_name, response.text)
    core.logger.debug(lambda: core.json.dumps(service_results, indent=2))
    results.extend(service_results)

def __add_results(core, service_name, results):
    for item in results:
        listitem = core.kodi.create_listitem(item)

        action_args = item['action_args']
        action_args['filename'] = item['name']
        action_args = core.utils.quote_plus(core.json.dumps(item['action_args']))

        core.kodi.xbmcplugin.addDirectoryItem(
            handle=core.handle,
            listitem=listitem,
            isFolder=False,
            url='plugin://%s/?action=download&service=%s&action_args=%s' % (core.kodi.addon_id, service_name, action_args)
        )

def search(core, params):
    core.logger.debug(lambda: core.json.dumps(params, indent=2))
    meta = core.video.get_meta()
    meta.languages = core.utils.unquote(params['languages']).split(',')
    meta.preferredlanguage = params['preferredlanguage']

    if meta.imdb_id == '':
        core.logger.error('Missing imdb id!')
        return

    threads = []
    results = []
    for service_name in core.services:
        service = core.services[service_name]
        requests = service.build_search_requests(core, service_name, meta)
        core.logger.debug(lambda: '%s - %s' % (service_name, core.json.dumps(requests, indent=2)))

        for request in requests:
            thread = core.threading.Thread(target=__query_service, args=(core, service_name, request, results))
            threads.append(thread)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    sorter = lambda x: (
        not x['lang'] == meta.preferredlanguage,
        meta.languages.index(x['lang']),
        x['service']
    )
    results = sorted(results, key=sorter)
    results = results[:20]

    __add_results(core, service_name, results)
