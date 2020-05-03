# -*- coding: utf-8 -*-

def __download(core, filepath, request):
    request['stream'] = True
    with core.request.execute(request) as r:
        with open(filepath, 'wb') as f:
            core.shutil.copyfileobj(r.raw, f)

def __extract_gzip(core, archivepath, filename):
    filepath = core.os.path.join(core.utils.temp_dir, filename)

    if core.utils.PY2:
        with open(archivepath, 'rb') as f:
            gzip_file = f.read()

        with core.gzip.GzipFile(fileobj=core.utils.StringIO(gzip_file)) as gzip:
            with open(filepath, 'wb') as f:
                f.write(gzip.read())
                f.flush()
    else:
        with core.gzip.open(archivepath, 'rb') as f_in:
            with open(filepath, 'wb') as f_out:
                core.shutil.copyfileobj(f_in, f_out)

    return filepath

def __extract_zip(core, archivepath, filename, episodeid):
    path = core.utils.quote_plus(archivepath)
    ext = core.os.path.splitext(filename)[1].lower()
    (dirs, files) = core.kodi.xbmcvfs.listdir('archive://%s' % path)

    first_subfile = None
    subfile = None
    for file in files:
        if core.utils.PY2:
            file = file.decode('utf8')

        file_lower = file.lower()
        if file_lower.endswith(ext):
            if not first_subfile:
                first_subfile = file
            if (episodeid == '' or episodeid in file_lower):
                subfile = file
                break

    if not subfile:
        if first_subfile:
            subfile = first_subfile
        else:
            subfile = filename

    src = 'archive://' + path + '/' + subfile
    dest = core.os.path.join(core.utils.temp_dir, filename)
    core.kodi.xbmcvfs.copy(src, dest)
    return dest

def __insert_lang_code_in_filename(core, filename, lang):
    filename_chunks = filename.split('.')
    lang_code = core.kodi.xbmc.convertLanguage(lang, core.kodi.xbmc.ISO_639_2)
    filename_chunks.insert(-1, lang_code)
    return '.'.join(filename_chunks)

def __cleanup(core, filepath):
    with open(filepath, 'r') as f:
        sub_contents = f.read()

    try:
        cleaned_contents = core.utils.cleanup_subtitles(sub_contents)
        if len(cleaned_contents) < len(sub_contents) / 2:
            return

        with open(filepath, 'w') as f:
            f.write(cleaned_contents)
    except:
        pass

def download(core, params):
    core.logger.debug(lambda: core.json.dumps(params, indent=2))

    core.shutil.rmtree(core.utils.temp_dir, ignore_errors=True)
    core.kodi.xbmcvfs.mkdirs(core.utils.temp_dir)

    actions_args = params['action_args']
    filename = __insert_lang_code_in_filename(core, actions_args['filename'], actions_args['lang'])
    archivepath = core.os.path.join(core.utils.temp_dir, 'sub.zip')

    service_name = params['service_name']
    service = core.services[service_name]
    request = service.build_download_request(core, service_name, actions_args)

    if actions_args.get('raw', False):
        filepath = core.os.path.join(core.utils.temp_dir, filename)
        __download(core, filepath, request)
    else:
        __download(core, archivepath, request)
        if actions_args.get('gzip', False):
            filepath = __extract_gzip(core, archivepath, filename)
        else:
            episodeid = actions_args.get('episodeid', '')
            filepath = __extract_zip(core, archivepath, filename, episodeid)

    if core.kodi.get_bool_setting('general.remove_ads'):
        __cleanup(core, filepath)

    if core.api_mode_enabled:
        return filepath
    listitem = core.kodi.xbmcgui.ListItem(label=filepath)
    core.kodi.xbmcplugin.addDirectoryItem(handle=core.handle, url=filepath, listitem=listitem, isFolder=False)
