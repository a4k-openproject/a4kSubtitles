# -*- coding: utf-8 -*-

def start(api):
    core = api.core
    monitor = core.kodi.xbmc.Monitor()
    has_done_subs_check = False

    while not monitor.abortRequested():
        if monitor.waitForAbort(1):
            break

        if not core.kodi.get_bool_setting('general', 'auto_search'):
            continue

        has_video = (core.kodi.xbmc.getCondVisibility('VideoPlayer.Content(movies)')
                   or core.kodi.xbmc.getCondVisibility('VideoPlayer.Content(episodes)'))
        if not has_video and has_done_subs_check:
            has_done_subs_check = False

        has_video_duration = core.kodi.xbmc.getCondVisibility('Player.HasDuration')

        if not has_video or not has_video_duration or has_done_subs_check:
            continue

        has_done_subs_check = True
        has_subtitles = False

        preferredlang = core.kodi.get_kodi_setting('locale.subtitlelanguage')

        try:
            preferredlang_code = core.kodi.xbmc.convertLanguage(preferredlang, core.kodi.xbmc.ISO_639_2)
            sub_lang_codes = [core.kodi.xbmc.convertLanguage(s, core.kodi.xbmc.ISO_639_2) for s in core.kodi.xbmc.Player().getAvailableSubtitleStreams()]
            core.kodi.xbmc.Player().setSubtitleStream(sub_lang_codes.index(preferredlang_code))
            has_subtitles = True
        except: pass

        if has_subtitles:
            continue

        if not core.kodi.get_bool_setting('general', 'auto_download'):
            core.kodi.xbmc.executebuiltin('ActivateWindow(SubtitleSearch)')
            continue

        languages = core.kodi.get_kodi_setting('subtitles.languages')
        params = {
            'action': 'search',
            'languages': ','.join(languages),
            'preferredlanguage': preferredlang
        }

        results = api.search(params)
        for result in results:
            try:
                subfile = api.download(result)
                core.kodi.xbmc.Player().setSubtitles(subfile)
                break
            except: pass
