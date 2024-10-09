# -*- coding: utf-8 -*-
subtitles_exts = ['.srt', '.sub']
subtitles_exts_secondary = ['.smi', '.ssa', '.aqt', '.jss', '.ass', '.rt', '.txt']
subtitles_exts_all = subtitles_exts + subtitles_exts_secondary

def __download(core, filepath, request):
    request['stream'] = True
    with core.request.execute(core, request) as r:
        with open(filepath, 'wb') as f:
            core.shutil.copyfileobj(r.raw, f)

def __extract_gzip(core, archivepath, filename):
    if not any(filename.lower().endswith(ext) for ext in subtitles_exts_all):
        # For now, we will use 'srt' to mark unknown file extensions as subtitles.
        filename = filename + ".srt"

    filepath = core.os.path.join(core.utils.temp_dir, filename)

    if core.utils.py2:
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
    sub_exts = subtitles_exts
    sub_exts_secondary = subtitles_exts_secondary

    try:
        using_libvfs = False
        with open(archivepath, 'rb') as f:
            zipfile = core.zipfile.ZipFile(core.BytesIO(f.read()))
        namelist = core.utils.get_zipfile_namelist(zipfile)
    except:
        using_libvfs = True
        archivepath_ = core.utils.quote_plus(archivepath)
        (dirs, files) = core.kodi.xbmcvfs.listdir('archive://%s' % archivepath_)
        namelist = [file.decode(core.utils.default_encoding) if core.utils.py2 else file for file in files]

    subfile = core.utils.find_file_in_archive(core, namelist, sub_exts + sub_exts_secondary, episodeid)

    if subfile:
        # Add the subtitle file extension.
        subfilename_and_ext = subfile.rsplit(".", 1)
        if len(subfilename_and_ext) > 1:
            filename = filename + "." + subfilename_and_ext[-1]

    dest = core.os.path.join(core.utils.temp_dir, filename)
    if not subfile:
        try:
            return __extract_gzip(core, archivepath, filename)
        except:
            try: core.os.remove(dest)
            except: pass
            try: core.os.rename(archivepath, dest)
            except: pass
            return dest

    if not using_libvfs:
        src = core.utils.extract_zipfile_member(zipfile, subfile, core.utils.temp_dir)
        try: core.os.remove(dest)
        except: pass
        try: core.os.rename(src, dest)
        except: pass
    else:
        src = 'archive://' + archivepath_ + '/' + subfile
        core.kodi.xbmcvfs.copy(src, dest)

    return dest

def __insert_lang_code_in_filename(core, filename, lang_code):
    name = core.utils.strip_non_ascii_and_unprintable(filename)
    nameparts = name.rsplit(".", 1)

    # Because this can be called via "raw" subtitles where sub ext exists we will ensure it ends with the subtitle ext.
    # Otherwise we will use "filename.lang_code" later the ext will be added on unzip process.
    if len(nameparts) > 1 and ("." + nameparts[1] in subtitles_exts_all):
        return ".".join([nameparts[0], lang_code, nameparts[1]])

    return "{0}.{1}".format(name, lang_code)

def __postprocess(core, filepath, lang_code):
    try:
        with open(filepath, 'rb', encoding=core.utils.default_encoding) as f:
            text_bytes = f.read()

        if core.kodi.get_bool_setting('general.use_chardet'):
            encoding = ''
            if core.utils.py3:
                detection = core.utils.chardet.detect(text_bytes)
                detected_lang_code = core.utils.get_lang_id(detection['language'], core.kodi.xbmc.ISO_639_2)
                if detection['confidence'] == 1.0 or detected_lang_code == lang_code:
                    encoding = detection['encoding']

            if not encoding:
                encoding = core.utils.code_pages.get(lang_code, core.utils.default_encoding)

            text = text_bytes.decode(encoding)
        else:
            text = text_bytes.decode(core.utils.default_encoding)

        try:
            if all(ch in text for ch in core.utils.cp1251_garbled):
                text = text.encode(core.utils.base_encoding).decode('cp1251')
            elif all(ch in text for ch in core.utils.koi8r_garbled):
                try:
                    text = text.encode(core.utils.base_encoding).decode('koi8-r')
                except:
                    text = text.encode(core.utils.base_encoding).decode('koi8-u')
        except: pass

        try:
            clean_text = core.utils.cleanup_subtitles(core, text)
            if len(clean_text) > len(text) / 2:
                text = clean_text
        except: pass

        with open(filepath, 'wb') as f:
            f.write(text.encode(core.utils.default_encoding))
    except: pass

def __copy_sub_local(core, subfile):
    # Copy the subfile to local.
    if core.os.getenv('A4KSUBTITLES_TESTRUN') == 'true':
        return

    media_name = core.os.path.splitext(core.os.path.basename(core.kodi.xbmc.getInfoLabel('Player.Filename')))[0]
    sub_name, lang_code, extension = core.os.path.basename(subfile).rsplit(".", 2)
    file_dest, folder_dest = None, None
    if core.kodi.get_kodi_setting("subtitles.storagemode") == 0:
        folder_dest = core.kodi.xbmc.getInfoLabel('Player.Folderpath')
        file_dest = core.os.path.join(folder_dest, ".".join([media_name, lang_code, extension]))
    elif core.kodi.get_kodi_setting("subtitles.storagemode") == 1:
        folder_dest = core.kodi.get_kodi_setting("subtitles.custompath")
        file_dest = core.os.path.join(folder_dest, ".".join([media_name, lang_code, extension]))

    if file_dest and core.kodi.xbmcvfs.exists(folder_dest):
        core.kodi.xbmcvfs.copy(subfile, file_dest)

def download(core, params):
    core.logger.debug(lambda: core.json.dumps(params, indent=2))

    core.shutil.rmtree(core.utils.temp_dir, ignore_errors=True)
    core.kodi.xbmcvfs.mkdirs(core.utils.temp_dir)

    actions_args = params['action_args']
    lang_code = core.utils.get_lang_id(actions_args['lang'], core.kodi.xbmc.ISO_639_2)
    filename = __insert_lang_code_in_filename(core, actions_args['filename'], lang_code)
    filename = core.utils.slugify_filename(filename)
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

    __postprocess(core, filepath, lang_code)

    if core.api_mode_enabled:
        __copy_sub_local(core, filepath)
        return filepath

    listitem = core.kodi.xbmcgui.ListItem(label=filepath, offscreen=True)
    core.kodi.xbmcplugin.addDirectoryItem(handle=core.handle, url=filepath, listitem=listitem, isFolder=False)
