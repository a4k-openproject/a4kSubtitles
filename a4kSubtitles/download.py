# -*- coding: utf-8 -*-

def __download(core, filepath, request):
    request['stream'] = True
    with core.request.execute(request) as r:
        with open(filepath, 'wb') as f:
            core.shutil.copyfileobj(r.raw, f)

def __extract(core, archivepath, filename, language):
    path = core.utils.quote_plus(archivepath)
    ext = core.os.path.splitext(filename)[1].lower()
    (dirs, files) = core.kodi.xbmcvfs.listdir('archive://%s' % path)

    subfile = filename
    for file in files:
        if file.lower().endswith(ext):
            subfile = file
            break

    src = 'archive://' + path + '/' + subfile
    subfile = __insert_language_code_in_filename(core, filename, language)
    dest = core.os.path.join(core.utils.temp_dir, subfile)
    core.kodi.xbmcvfs.copy(src, dest)
    return dest

def __insert_language_code_in_filename(core, filename, language_name):
    filename_chunks = filename.split('.')
    lang_code = core.kodi.xbmc.convertLanguage(language_name,
                                               core.kodi.xbmc.ISO_639_1)
    filename_chunks.insert(-1, lang_code)
    return '.'.join(filename_chunks)

def download(core, params):
    core.logger.debug(lambda: core.json.dumps(params, indent=2))

    core.shutil.rmtree(core.utils.temp_dir, ignore_errors=True)
    core.kodi.xbmcvfs.mkdirs(core.utils.temp_dir)

    actions_args = params['action_args']
    filename = actions_args['filename']
    language = actions_args['lang']
    archivepath = core.os.path.join(core.utils.temp_dir, 'sub.zip')

    service_name = params['service_name']
    service = core.services[service_name]
    request = service.build_download_request(core, service_name, actions_args)

    __download(core, archivepath, request)
    filepath = __extract(core, archivepath, filename, language)

    if core.api_mode_enabled:
        return filepath
    listitem = core.kodi.xbmcgui.ListItem(label=filepath)
    core.kodi.xbmcplugin.addDirectoryItem(handle=core.handle, url=filepath, listitem=listitem, isFolder=False)
