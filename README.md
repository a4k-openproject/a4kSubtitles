<img align="left" width="115px" height="115px" src="icon.png">

# AI Kodi Subtitle Translator
---
**Note:** This project is a fork of the original [a4kSubtitles](https://github.com/a4k-openproject/a4kSubtitles) by the a4k-openproject team. This version is modified to focus on AI-powered subtitle translation to any language, while retaining the core functionalities of the original addon. Many thanks to the original creators for their excellent work!
---
[![Kodi version](https://img.shields.io/badge/kodi%20versions-20--21-blue)](https://kodi.tv/)

### General Status
[![Background Service](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-service.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-service.yml)
[![API](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-api.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-api.yml)
[![Search](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-search.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-search.yml)
[![TVShows](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-tvshow.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-tvshow.yml)

### Providers Status
[![Addic7ed](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-addic7ed.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-addic7ed.yml)
[![BSPlayer](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-bsplayer.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-bsplayer.yml)
[![OpenSubtitles](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-opensubtitles.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-opensubtitles.yml)
[![Podnadpisi.NET](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-podnadpisi.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-podnadpisi.yml)
<!-- [![SubDL](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-subdl.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-subdl.yml) -->

## Description

AI-powered subtitle addon for KODI. This addon allows you to find subtitles from various services and translate them to virtually any language using AI.
It builds upon the robust features of a4kSubtitles and supports multiple subtitle services including:
* Addic7ed
* BSPlayer
* OpenSubtitles
* Podnadpisi.NET
* SubDL
* SubSource
* And your own Subtitlecat implementation for AI translations!

## Configuration
![configuration](https://media.giphy.com/media/kewuE4BgfOnFin0vEC/source.gif)

## Installation

Steps to install a4kSubtitles:
1. Go to the KODI **File manager**.
2. Click on **Add source**.
3. The path for the source is https://a4k-openproject.github.io/a4kSubtitles/packages/
4. (Optional) Name it **ai-kodi-subtitle-translator-repo**.
5. Head to **Addons**.
6. Select **Install from zip file**.
7. When it asks for the location select **ai-kodi-subtitle-translator-repo** (or the name you chose in step 4) and install `ai-kodi-subtitle-translator-repository.zip` (Note: The exact ZIP name will depend on the updated packaging).
8. Go back to **Addons** and select **Install from repository**
9. Select the **AI Kodi Subtitle Translator** menu item (or similar, based on the new addon name).

## Preview
![usage](https://media.giphy.com/media/QTmhgEJTpTPTPxByfj/source.gif)

## Contribution

Configure hooks for auto update of `addons.xml`:
```sh
git config core.hooksPath .githooks
```
## License

MIT

## Icon

Logo `quill` by Ramy Wafaa ([RoundIcons](https://roundicons.com))
