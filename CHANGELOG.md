* [v2.2.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-2.2.0):
  * Fix KODI 19 Matrix support

* [v2.1.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-2.1.0):
  * Fix Persian search in Subscene

* [v2.0.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-2.0.0):
  * Use IMDb as main source for all meta.
  * Retry on 503 (Service Unavailable). OpenSubtitles and Subscene seems to return it occasionally.

* [v1.8.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.8.0):
  * Remove SubDb (Site is down)
  * Make lib vfs optional since there are fallbacks and it is used as last case scenario. Thus making the addon installable on platforms which are not supported by lib vfs.

* [v1.7.2](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.7.2):
  * Improve results sort based on title match

* [v1.7.1](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.7.1):
  * Drop python meta as it prevents installations on pre Kodi 19 versions

* [v1.7.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.7.0):
  * Update python meta to enable Kodi 19 installations

* [v1.6.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.6.0):
  * Add option to auto download first subtitle result silently

* [v1.5.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.5.0):
  * Auto open search dialog only on movie and tvshow videos

* [v1.4.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.4.0):
  * Add option to auto open the search dialog when the video does not have subtitles

* [v1.3.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.3.0):
  * Improve tvshow year scraping

* [v1.2.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.2.0):
  * Use internal ZipFile for extraction with a fallback to vfs.libarchive

* [v1.1.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.1.0):
  * Improve imdb id scraping

* [v1.0.1](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.0.1):
  * Add screenshots

* [v1.0.0](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-1.0.0):
  * Invalidate BSPlayer results cache when download links expire
  * Extraction fallback: zip -> gzip -> raw

* [v0.0.30](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.30):
  * Add service names in ad detection
  * Removed the option to disable cleaning of ads
  * Add remote fetching of addic7ed data

* [v0.0.29](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.29):
  * Fix Podnadpisi download of results missing filename meta
  * Fix last results cache not invalidated on language preferences change

* [v0.0.28](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.28):
  * Attempt scrape of imdb id when missing
  * Improve filename parsing
  * Fix SubDB lang code
  * Fix Podnadpisi not returning release name

* [v0.0.27](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.27):
  * Attempt to auto-fix a garbled cyrillic encoded subtitles
  * Fix more encoding issues
  * Ensure progress dialog close even if the addon crashes
  * Apply color to service name in results and bold tags
  * Show notification if imdb id is missing

* [v0.0.26](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.26):
  * Support for Addic7ed
  * Improve cache of the last results
  * Don't show progress when showing results from cache

* [v0.0.25](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.25):
  * Fix cancellation thread exit

* [v0.0.24](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.24):
  * Show progress dialog only for search

* [v0.0.23](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.23):
  * Add progress dialog
  * Support cancellation

* [v0.0.22](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.22):
  * Fix meta string conversion issue

* [v0.0.21](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.21):
  * TVShow year scrape from imdb when necessary

* [v0.0.20](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.20):
  * Improve Subscene tvshow matching
  * Extract first sub file from zips when none is matched
  * Fix Podnadpisi not working properly for tvshows
  * Fix non-ascii video file title issues
  * Add tvshow tests

* [v0.0.19](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.19):
  * Update settings
  * Fix language code suffix format in the subtitle file name
  * Support for Subscene

* [v0.0.18](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.18):
  * Support for Podnadpisi.NET
  * Support for SubDB

* [v0.0.17](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.17):
  * Reuse KODI's Python language invoker
    * Improves performance on low-end devices when switching subtitles for best match
  * Url decode subtitle names

* [v0.0.16](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.16):
  * Cache last result
  * OpenSubtitles always queries:
    * by imdb id and title
    * by video file hash
  * Improve results ordering:
    * preferred lang
    * lang
    * synced
    * name match
    * rating
    * hearing impaired
    * subtitle service
  * Fix url with numbers matching in ads detection

* [v0.0.15](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.15):
  * Remove ads by default
  * Support for BSPlayer
  * Additional option for OpenSubtitles to use file hash (Limits results to exact matches)

* [v0.0.14](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.14):
  * Fix API and normal usage at the same time

* [v0.0.13](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.13):
  * Exclude development files from release

* [v0.0.12](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.12):
  * Removal of ads (Experimental)
  * Fix extract issue when file contains unicode symbols

* [v0.0.11](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.11):
  * Changelog in KODI

* [v0.0.10](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.10):
  * Inserted language code in sub filename

* [v0.0.9](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.9):
  * Implemented (orginal, default, none, forced_only) as KODI language setting
  * Fixed minor bugs in API implementation
  * Added .idea folder to .gitignore

* [v0.0.8](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.8):
  * opensubtitles should make max 2 requests for separate languages
  * lint updates
  * add tests for download

* [v0.0.7](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.7):
  * API class rename

* [v0.0.6](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.6):
  * fix core requiring handle even with API usage

* [v0.0.5](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.5):
  * expose API for usage without KODI
  * add tests for search

* [v0.0.4](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.4):
  * distribution process:
    * KODI repository with updates based on github releases
    * addons.xml and addons.xml.crc auto generation via git hooks
    * release automation on merge to master via Github Actions

* [v0.0.3](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.3):
  * general settings for configuring requests timeout and results limit
  * additional ordering of the results depending on the similarity ratio of the video file name and the subtitle file name

* [v0.0.2](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.2):
  * improve archive extraction support
  * limit the results and add requests timeout
  * fix OpenSubtitles authentication
  * handle debug logging detection issues

* [v0.0.1](https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles-0.0.1):
  * initial working version (search and download subtitles)
  * OpenSubtitles support with optional authentication
  * results ordering with preferred language ordered first
