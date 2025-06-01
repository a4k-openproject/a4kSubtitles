# -*- coding: utf-8 -*-

def start(api):
    core = api.core
    monitor = core.kodi.xbmc.Monitor()
    has_done_subs_check = False
    prev_playing_filename = ''

    subfile = None
    subfile_translated = None
    ai_last_timestamp = 0
    ai_max_range = 60
    ai_step = ai_max_range / 2
    ai_provider = ''
    ai_api_key = ''
    ai_model = ''
    moviename = ''
    target_language = ''

    while not monitor.abortRequested():
        if monitor.waitForAbort(1):
            break

        if not core.kodi.get_bool_setting('general', 'auto_search'):
            continue

        has_video = core.kodi.xbmc.Player().isPlayingVideo()

        if not has_video and has_done_subs_check:
            prev_playing_filename = ''
            has_done_subs_check = False
            subfile = None

        has_video_duration = core.kodi.xbmc.getCondVisibility('Player.HasDuration')

        # In-case episode changed.
        if has_video:
            playing_filename = core.kodi.xbmc.getInfoLabel('Player.Filenameandpath')
            if prev_playing_filename != playing_filename:
                has_done_subs_check = False
                subfile = None
                prev_playing_filename = playing_filename

        if not has_video or not has_video_duration or has_done_subs_check:
            continue

        use_ai = core.kodi.get_bool_setting('general', 'use_ai')
        if use_ai and subfile:
            timestamp = core.kodi.xbmc.Player().getTime()
            if ai_last_timestamp + ai_step > timestamp and timestamp > ai_last_timestamp:
                continue

            ai_last_timestamp = timestamp

            core.logger.debug('Using AI to translate portion of subtitles between %s and %s seconds' % (ai_last_timestamp, ai_last_timestamp + ai_max_range))
            core.utils.gptsubtrans.translate(
                input_file=subfile,
                target_language=target_language,
                output_file=subfile_translated,
                moviename=moviename,
                provider=ai_provider,
                api_key=ai_api_key,
                model=ai_model,
                begin_seconds=ai_last_timestamp,
                end_seconds=ai_last_timestamp + ai_max_range,
                log=core.logger.debug
            )

            core.kodi.xbmc.Player().setSubtitles(subfile_translated)
            continue

        has_done_subs_check = True
        has_subtitles = False

        preferredlang = core.kodi.get_kodi_setting('locale.subtitlelanguage')
        prefer_sdh = core.kodi.get_bool_setting('general', 'prefer_sdh')
        prefer_forced = not prefer_sdh and (core.kodi.get_bool_setting('general', 'prefer_forced') or preferredlang == 'forced_only')
        preferredlang = core.kodi.parse_language(preferredlang)

        try:
            def update_sub_stream():
                if not core.kodi.get_bool_setting('general', 'auto_select'):
                    return
                if preferredlang is None:
                    core.logger.debug('no subtitle language found')
                    return

                player_props = core.kodi.get_kodi_player_subtitles()
                preferredlang_code = core.utils.get_lang_id(preferredlang, core.kodi.xbmc.ISO_639_2)
                sub_langs = [core.utils.get_lang_id(s, core.kodi.xbmc.ISO_639_2) for s in core.kodi.xbmc.Player().getAvailableSubtitleStreams()]

                preferedlang_sub_indexes = [i for i, s in enumerate(sub_langs) if preferredlang_code == s]
                core.logger.debug('player_props: %s' % player_props)
                core.logger.debug('prefer_sdh: %s' % prefer_sdh)
                core.logger.debug('prefer_forced: %s' % prefer_forced)
                core.logger.debug('preferredlang_code: %s' % preferredlang_code)
                core.logger.debug('sub_langs: %s' % sub_langs)
                core.logger.debug('preferedlang_sub_indexes: %s' % preferedlang_sub_indexes)

                if len(preferedlang_sub_indexes) == 0:
                    core.logger.debug('no subtitles found for %s' % preferredlang)
                    return

                def find_sub_index():
                    if 'subtitles' not in player_props:
                        return None

                    sub_index = None
                    for sub in player_props['subtitles']:
                        subname = sub['name'].lower()
                        if sub['language'] != preferredlang_code:
                            continue
                        if prefer_sdh and (sub['isimpaired'] or 'sdh' in subname or 'captions' in subname or 'honorific' in subname):
                            core.logger.debug('found SDH subtitles: %s' % subname)
                            sub_index = sub['index']
                            break
                        if prefer_forced and (sub['isforced'] or 'forced' in subname):
                            core.logger.debug('found forced subtitles: %s' % subname)
                            sub_index = sub['index']
                            break

                    if sub_index is None:
                        for sub in player_props['subtitles']:
                            subname = sub['name'].lower()
                            if sub['language'] != preferredlang_code:
                                continue
                            if not sub['isforced'] and all(s not in subname for s in ['forced', 'songs', 'commentary']):
                                core.logger.debug('found default subtitles: %s' % subname)
                                sub_index = sub['index']
                                break

                    return sub_index

                sub_index = find_sub_index()
                if sub_index is None and preferredlang_code == 'pob':
                    core.logger.debug('no subtitles found for %s, trying por' % preferredlang)
                    preferredlang_code = 'por'
                    sub_index = find_sub_index()

                if sub_index is None:
                    if prefer_sdh:
                        core.logger.debug('no SDH subtitles found for %s, fallback to last index from matched langs' % preferredlang)
                        sub_index = preferedlang_sub_indexes[-1]
                    elif not prefer_forced and len(preferedlang_sub_indexes) > 1:
                        core.logger.debug('no subtitles found for %s, fallback to second index from matched langs' % preferredlang)
                        sub_index = preferedlang_sub_indexes[1]
                    else:
                        core.logger.debug('no subtitles found for %s, fallback to first index from matched langs' % preferredlang)
                        sub_index = preferedlang_sub_indexes[0]

                if sub_index != player_props['currentsubtitle']['index']:
                    core.kodi.xbmc.Player().setSubtitleStream(sub_index)
                return True

            if not use_ai:
                has_subtitles = update_sub_stream()
        except Exception as e:
            core.logger.debug('Error on update_sub_stream: %s' % e)

        if has_subtitles:
            continue

        has_imdb = core.kodi.xbmc.getInfoLabel('VideoPlayer.IMDBNumber')
        if not has_imdb:
            continue

        if not core.kodi.get_bool_setting('general', 'auto_download'):
            core.kodi.xbmc.executebuiltin('ActivateWindow(SubtitleSearch)')
            continue

        languages = core.kodi.get_kodi_setting('subtitles.languages')
        preferredlang_preai = preferredlang

        if use_ai:
            languages = ['English']
            preferredlang = 'English'

        params = {
            'action': 'search',
            'languages': ','.join(languages),
            'preferredlanguage': preferredlang
        }

        results = api.search(params)
        for result in results:
            try:
                subfile = api.download(result)

                if not subfile:
                    core.logger.debug('No subtitle file found for %s' % result)
                    continue

                if not use_ai or preferredlang == preferredlang_preai:
                    core.logger.debug('Setting subtitles: %s' % subfile)
                    core.kodi.xbmc.Player().setSubtitles(subfile)
                else:
                    core.logger.debug('Using AI to translate subtitles: %s' % subfile)
                    subfile_translated = subfile + '.translated'

                    ai_provider = core.kodi.get_setting('general', 'ai_provider')
                    if ai_provider is None or ai_provider == '':
                        ai_provider = '0'

                    if ai_provider == '0':
                        ai_provider = 'OpenAI'
                    else:
                        ai_provider = 'NexosAI'

                    if ai_provider not in ['OpenAI', 'NexosAI']:
                        core.logger.error('Invalid AI provider: %s' % ai_provider)
                        continue

                    ai_api_key = core.kodi.get_setting('general', 'ai_api_key')
                    ai_model = core.kodi.get_setting('general', 'ai_model')
                    moviename = '%s (%s)' % (core.last_meta.title, core.last_meta.year) if core.last_meta else ''
                    target_language = core.utils.get_lang_id(preferredlang_preai, core.kodi.xbmc.ISO_639_2)

                    core.logger.debug('Translating subtitles with AI provider: %s, model: %s' % (ai_provider, ai_model))
                    core.logger.debug('Moviename: %s, target_language: %s' % (moviename, target_language))

                    ai_last_timestamp = core.kodi.xbmc.Player().getTime()

                    core.utils.gptsubtrans.translate(
                        input_file=subfile,
                        target_language=target_language,
                        output_file=subfile_translated,
                        moviename=moviename,
                        provider=ai_provider,
                        api_key=ai_api_key,
                        model=ai_model,
                        begin_seconds=ai_last_timestamp,
                        end_seconds=ai_last_timestamp + ai_max_range,
                        log=core.logger.debug
                    )

                    core.kodi.xbmc.Player().setSubtitles(subfile_translated)
                    has_done_subs_check = False

                break
            except:
                import traceback
                core.logger.error('Error downloading or setting subtitles: %s' % traceback.format_exc())
                continue
