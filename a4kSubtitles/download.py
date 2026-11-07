# -*- coding: utf-8 -*-
subtitles_exts = ['.srt', '.sub']
subtitles_exts_secondary = ['.smi', '.ssa', '.aqt', '.jss', '.ass', '.rt']
subtitles_exts_all = subtitles_exts + subtitles_exts_secondary
raw_exts = subtitles_exts_all + ['.vtt']  # raw downloads only: archives are searched for subtitles_exts_all
archive_magics = (b'PK\x03\x04', b'PK\x05\x06', b'Rar!\x1a\x07', b'7z\xbc\xaf\x27\x1c')  # zip, empty zip, rar, 7z

def __download(core, filepath, request):
    request['stream'] = True
    response = core.request.execute(core, request)
    if response.status_code >= 400:
        raise Exception('Failed to download subtitle (HTTP: %s)' % response.status_code)

    with response as r:
        with open(filepath, 'wb') as f:
            r.raw.decode_content = True
            core.shutil.copyfileobj(r.raw, f)

    return response

def __detect_raw_ext(core, response, filepath):
    # The name had no subtitle extension: try the URL path, then Content-Type, then a WEBVTT sniff.
    path_ext = core.os.path.splitext(core.request.urlparse(response.url).path)[1].lower()
    if path_ext in raw_exts:
        return path_ext
    if 'vtt' in response.headers.get('Content-Type', '').lower():
        return '.vtt'
    with open(filepath, 'rb') as f:
        if f.read(64).lstrip(b'\xef\xbb\xbf').startswith(b'WEBVTT'):
            return '.vtt'
    return '.srt'

def __extract_gzip(core, archivepath, filename):
    if not any(filename.lower().endswith(ext) for ext in subtitles_exts_all):
        # For now, we will use 'srt' to mark unknown file extensions as subtitles.
        filename = filename + ".srt"

    filepath = core.os.path.join(core.os.path.dirname(archivepath), filename)

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
            # A name that already ends in a subtitle extension (podnadpisi sends name.srt) takes the member's instead.
            (name, ext) = core.os.path.splitext(filename)
            if ext.lower() in subtitles_exts_all:
                filename = name
            filename = filename + "." + subfilename_and_ext[-1]

    dest = core.os.path.join(core.os.path.dirname(archivepath), filename)
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
        src = core.utils.extract_zipfile_member(zipfile, subfile, core.os.path.dirname(archivepath))
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
    if len(nameparts) > 1 and ("." + nameparts[1].lower() in raw_exts):
        return ".".join([nameparts[0], lang_code, nameparts[1]])

    return "{0}.{1}".format(name, lang_code)

def __postprocess(core, filepath, lang_code):
    try:
        with open(filepath, 'rb') as f:
            text_bytes = f.read()

        if core.kodi.get_bool_setting('general.use_chardet'):
            encoding = ''
            try:
                # Text that decodes as UTF-8 is UTF-8: chardet often rates it below 1.0, and the code page
                # fallback below then turned UTF-8 Arabic into cp1256 mojibake.
                text_bytes.decode('utf-8-sig')
                encoding = 'utf-8-sig'
            except UnicodeDecodeError: pass

            if not encoding and core.utils.py3:
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

def __check_subfile(core, filepath):
    if not core.os.path.isfile(filepath) or core.os.path.getsize(filepath) == 0:
        raise Exception('Failed to download subtitle (missing or empty file)')
    with open(filepath, 'rb') as f:
        if f.read(6).startswith(archive_magics):
            raise Exception('Failed to download subtitle (got an archive with no subtitle in it)')

def __prune_temp_dirs(core):
    # Each download works in its own subdir; drop old ones but never one another download may still be writing.
    cutoff = core.time.time() - 10 * 60
    for name in core.os.listdir(core.utils.temp_dir):
        path = core.os.path.join(core.utils.temp_dir, name)
        try:
            if core.os.path.getmtime(path) < cutoff:
                core.shutil.rmtree(path, ignore_errors=True)
        except OSError: pass

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

def __download_to(core, params, work_dir):
    actions_args = params['action_args']
    lang_code = core.utils.get_lang_id(actions_args['lang'], core.kodi.xbmc.ISO_639_2)
    filename = actions_args['filename']
    # Raw downloads keep this name; one with no subtitle extension gets it after the download.
    # Zip and gzip extraction add the extension themselves.
    raw_needs_ext = actions_args.get('raw', False) and not any(filename.lower().endswith(ext) for ext in raw_exts)
    filename = __insert_lang_code_in_filename(core, filename, lang_code)
    filename = core.utils.slugify_filename(filename)
    filename = filename.strip()
    filename = core.utils.shorten_filename(filename, lang_code)
    archivepath = core.os.path.join(work_dir, 'sub.zip')

    service_name = params['service_name']
    service = core.services[service_name]
    request = service.build_download_request(core, service_name, actions_args)

    if actions_args.get('raw', False):
        filepath = core.os.path.join(work_dir, filename)
        response = __download(core, filepath, request)
        if raw_needs_ext:
            filepath_with_ext = filepath + __detect_raw_ext(core, response, filepath)
            core.os.rename(filepath, filepath_with_ext)
            filepath = filepath_with_ext
    else:
        __download(core, archivepath, request)
        if actions_args.get('gzip', False):
            filepath = __extract_gzip(core, archivepath, filename)
        else:
            episodeid = actions_args.get('episodeid', '')
            filepath = __extract_zip(core, archivepath, filename, episodeid)

    __check_subfile(core, filepath)
    __postprocess(core, filepath, lang_code)
    return filepath

def download(core, params):
    core.logger.debug(lambda: core.json.dumps(params, indent=2))

    core.kodi.xbmcvfs.File(core.utils.suspend_service_file, 'w').close()
    try:
        core.kodi.xbmcvfs.mkdirs(core.utils.temp_dir)
        __prune_temp_dirs(core)
        work_dir = core.tempfile.mkdtemp(dir=core.utils.temp_dir)
        try:
            filepath = __download_to(core, params, work_dir)
        except:
            core.shutil.rmtree(work_dir, ignore_errors=True)
            raise
    finally:
        core.kodi.xbmcvfs.delete(core.utils.suspend_service_file)

    if core.api_mode_enabled:
        __copy_sub_local(core, filepath)
        return filepath

    listitem = core.kodi.xbmcgui.ListItem(label=filepath, offscreen=True)
    core.kodi.xbmcplugin.addDirectoryItem(handle=core.handle, url=filepath, listitem=listitem, isFolder=False)
