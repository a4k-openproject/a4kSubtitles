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
            def update_sub_stream():
                if not core.kodi.get_bool_setting('general', 'auto_select'):
                    return

                player_props = core.kodi.get_kodi_player_subtitles()
                prefer_sdh = core.kodi.get_bool_setting('general', 'prefer_sdh')
                prefer_forced = not prefer_sdh and core.kodi.get_bool_setting('general', 'prefer_forced')

                preferredlang_code = core.utils.get_lang_id(preferredlang, core.kodi.xbmc.ISO_639_2)
                sub_langs = [core.utils.get_lang_id(s, core.kodi.xbmc.ISO_639_2) for s in core.kodi.xbmc.Player().getAvailableSubtitleStreams()]

                preferedlang_sub_indexes = [i for i, s in enumerate(sub_langs) if preferredlang_code == s]
                if len(preferedlang_sub_indexes) == 0:
                    return

                select_index = -1
                def find_sub_index():
                    if 'subtitles' in player_props:
                        for sub in player_props['subtitles']:
                            subname = sub['name'].lower()
                            if sub['language'] != preferredlang_code:
                                continue
                            if prefer_sdh and (sub['isimpaired'] or 'sdh' in subname or 'honorific' in subname):
                                select_index = sub['index']
                                break
                            if prefer_forced and (sub['isforced'] or 'forced' in subname):
                                select_index = sub['index']
                                break

                        if select_index == -1:
                            for sub in player_props['subtitles']:
                                subname = sub['name'].lower()
                                if sub['isdefault'] or ('forced' not in subname and 'songs' not in subname):
                                    select_index = sub['index']
                                    break

                find_sub_index()
                if select_index == -1 and preferredlang_code == 'pob':
                    preferredlang_code = 'por'
                    find_sub_index()

                if select_index == -1:
                    if prefer_sdh:
                        select_index = preferedlang_sub_indexes[-1]
                    if select_index == -1 and not prefer_forced and len(preferedlang_sub_indexes) > 1:
                        select_index = preferedlang_sub_indexes[1]
                    if select_index == -1:
                        select_index = preferedlang_sub_indexes[0]

                core.kodi.xbmc.Player().setSubtitleStream(select_index)
                return True

            has_subtitles = update_sub_stream()
        except:
            pass

        if has_subtitles:
            continue

        has_imdb = core.kodi.xbmc.getInfoLabel('VideoPlayer.IMDBNumber')
        if not has_imdb:
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
