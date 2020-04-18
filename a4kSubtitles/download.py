# -*- coding: utf-8 -*-

def __download_file(core, filepath, request):
    request['stream'] = True
    with core.request.execute(request) as r:
        with open(filepath, 'wb') as f:
            core.shutil.copyfileobj(r.raw, f)

def __extract(core, archivepath, filepath):
    with core.gzip.open(archivepath, 'rb') as f_in:
        with open(filepath, 'wb') as f_out:
            core.shutil.copyfileobj(f_in, f_out)

def download(core, params):
    core.logger.debug(lambda: core.json.dumps(params, indent=2))

    core.shutil.rmtree(core.utils.temp_dir, ignore_errors=True)
    core.kodi.xbmcvfs.mkdirs(core.utils.temp_dir)

    actions_args = params['action_args']
    filename = actions_args['filename']
    filepath = core.os.path.join(core.utils.temp_dir, filename)
    archivepath = core.os.path.join(core.utils.temp_dir, 'archive.gz')
    core.logger.debug(filepath)

    service_name = params['service']
    service = core.services[service_name]
    request = service.build_download_request(core, service_name, actions_args)

    __download_file(core, archivepath, request)
    __extract(core, archivepath, filepath)

    listitem = core.kodi.xbmcgui.ListItem(label=filepath)
    core.kodi.xbmcplugin.addDirectoryItem(handle=core.handle, url=filepath, listitem=listitem, isFolder=False)
