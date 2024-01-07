<img align="left" width="115px" height="115px" src="icon.png">

# a4kSubtitles
[![Kodi version](https://img.shields.io/badge/kodi%20versions-19--20-blue)](https://kodi.tv/) [![Coverage Status](https://coveralls.io/repos/github/a4k-openproject/a4kSubtitles/badge.svg?branch=master)](https://coveralls.io/github/a4k-openproject/a4kSubtitles?branch=master)

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
[![Subscene](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-subscene.yml/badge.svg)](https://github.com/a4k-openproject/a4kSubtitles/actions/workflows/cron-tests-subscene.yml)

## Description

Subtitle addon for KODI with support for multiple subtitle services:
* Addic7ed
* BSPlayer
* OpenSubtitles
* Podnadpisi.NET
* Subscene

## Configuration
![configuration](https://media.giphy.com/media/kewuE4BgfOnFin0vEC/source.gif)

## Installation

Steps to install a4kSubtitles:
1. Go to the KODI **File manager**.
2. Click on **Add source**.
3. The path for the source is https://a4k-openproject.github.io/a4kSubtitles/packages/
4. (Optional) Name it **a4kSubtitles-repo**.
5. Head to **Addons**.
6. Select **Install from zip file**.
7. When it asks for the location select **a4kSubtitles-repo** and install `a4kSubtitles-repository.zip`.
8. Go back to **Addons** and select **Install from repository**
9. Select the **a4kSubtitles** menu item

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
