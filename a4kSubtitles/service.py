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

        # Check if there is an IMDB number for this video
        # If not then this is most probably not a video played from an addon that provides the IMDB number
        # It could also be a local video file of from youtube, a tv station or...
        # In that case don't set the subtitle stream
        # Maybe an option should be added to the settings of a4kSubtitles if this is wanted or not
        IMDBNumber = core.kodi.xbmc.getInfoLabel('VideoPlayer.IMDBNumber')
        if IMDBNumber is None or IMDBNumber == '':
            continue

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
