# -*- coding: utf-8 -*-

def start(core):
    monitor = core.kodi.xbmc.Monitor()
    has_done_subs_check = False

    while not monitor.abortRequested():
        if monitor.waitForAbort(1):
            break

        if not core.kodi.get_bool_setting('general', 'auto_search'):
            continue

        has_video = core.kodi.xbmc.getCondVisibility('Player.HasVideo')
        if not has_video and has_done_subs_check:
            has_done_subs_check = False

        if not has_video or has_done_subs_check:
            continue

        has_done_subs_check = True

        has_subtitles_enabled = core.kodi.xbmc.getCondVisibility('VideoPlayer.SubtitlesEnabled')
        has_subtitles = core.kodi.xbmc.getCondVisibility('VideoPlayer.HasSubtitles') and has_subtitles_enabled

        if not has_subtitles:
            core.time.sleep(0.5)
            core.kodi.xbmc.executebuiltin('ActivateWindow(SubtitleSearch)')
            continue
