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
