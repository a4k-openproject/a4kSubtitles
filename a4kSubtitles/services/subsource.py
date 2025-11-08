# -*- coding: utf-8 -*-

__api = "https://api.subsource.net/api/v1"

__search = __api + "/movies/search"
__getSub = __api + "/subtitles"

ss_to_code = {
    "arabic": "ar",
    "english": "en",
    "bengali": "bn",
    "indonesian": "id",
    "abkhazian": "ab",
    "afrikaans": "af",
    "albanian": "sq",
    "amharic": "am",
    "aragonese": "an",
    "armenian": "hy",
    "assamese": "as",
    "farsi_persian": "fa",
    "asturian": "ast",
    "azerbaijani": "az",
    "basque": "eu",
    "belarusian": "be",
    "big_5_code": "zh",
    "bosnian": "bs",
    "brazilian_portuguese": "pt",
    "breton": "br",
    "bulgarian": "bg",
    "burmese": "my",
    "catalan": "ca",
    "chinese": "zh",
    "chinese_cantonese": "zh",
    "chinese_simplified": "zh",
    "chinese_traditional": "zh",
    "chinese_bg_code": "zh",
    "chinese_bilingual": "zh",
    "croatian": "hr",
    "czech": "cs",
    "danish": "da",
    "dari": "prs",
    "dutch": "nl",
    "espranto": "eo",
    "estonian": "et",
    "extremaduran": "ext",
    "filipino": "fil",
    "finnish": "fi",
    "french": "fr",
    "french_canada": "fr",
    "french_france": "fr",
    "gaelic": "gd",
    "gaelician": "gl",
    "georgian": "ka",
    "german": "de",
    "greek": "el",
    "greenlandic": "kl",
    "hebrew": "he",
    "hindi": "hi",
    "hungarian": "hu",
    "icelandic": "is",
    "igbo": "ig",
    "interlingua": "ia",
    "irish": "ga",
    "italian": "it",
    "japanese": "ja",
    "kannada": "kn",
    "kazakh": "kk",
    "khmer": "km",
    "korean": "ko",
    "kurdish": "ku",
    "kyrgyz": "ky",
    "latvian": "lv",
    "lithuanian": "lt",
    "luxembourgish": "lb",
    "macedonian": "mk",
    "malayalam": "ml",
    "manipuri": "mni",
    "marathi": "mr",
    "malay": "ms",
    "mongolian": "mn",
    "montenegrin": "cnr",
    "navajo": "nv",
    "nepali": "ne",
    "northen_sami": "se",
    "norwegian": "no",
    "occitan": "oc",
    "pashto": "ps",
    "odia": "or",
    "polish": "pl",
    "portuguese": "pt",
    "pushto": "ps",
    "romanian": "ro",
    "russian": "ru",
    "santli": "sat",
    "serbian": "sr",
    "sindhi": "sd",
    "sinhala": "si",
    "sinhalese": "si",
    "slovak": "sk",
    "slovenian": "sl",
    "somali": "so",
    "sorbian": "wen",
    "spanish": "es",
    "spanish_latin_america": "es",
    "spanish_spain": "es",
    "swahili": "sw",
    "swedish": "sv",
    "sylheti": "syl",
    "syriac": "syr",
    "tagalog": "tl",
    "tamil": "ta",
    "tatar": "tt",
    "telugu": "te",
    "tetum": "tet",
    "thai": "th",
    "toki_pona": "tok",
    "turkish": "tr",
    "turkmen": "tk",
    "ukrainian": "uk",
    "urdu": "ur",
    "uzbek": "uz",
    "vietnamese": "vi",
    "welsh": "cy"
}

code_to_ss = {v: k for k, v in ss_to_code.items()}

def build_search_requests(core, service_name, meta):
    apikey = core.kodi.get_setting(service_name, 'apikey')

    if not apikey:
        core.kodi.notification('Subsource requires API Key! Insert it in the addon Settings->Accounts or disable the service.')
        core.logger.error('%s - API Key is missing' % service_name)
        return []

    headers = {"X-API-Key": apikey}

    def get_movie(response):
        results = response.json()

        if "error" in results:
            return core.logger.error("%s - %s" % (service_name, results["message"]))

        found = results.get("data", [])
        first_season_id = None
        movie_id = None

        for res in found:
            if meta.is_movie and meta.imdb_id and "imdbId" in res and res["imdbId"] != meta.imdb_id:
                continue

            if res.get("season") == 1:
                first_season_id = res["movieId"]
            if meta.is_tvshow and meta.season != str(res.get("season")):
                continue

            movie_id = res["movieId"]
            break

        languages = ",".join(
            [
                code_to_ss.get(
                    core.utils.get_lang_id(k, core.kodi.xbmc.ISO_639_1), k.lower()
                )
                for k in meta.languages
            ]
        )

        params = {"movieId": movie_id or first_season_id, "language": languages}

        return {"method": "GET", "url": __getSub, "params": params, "headers": headers}

    name = (meta.title if meta.is_movie else meta.tvshow)
    year = meta.tvshow_year if meta.is_tvshow else meta.year

    text_search = {"searchType": "text", "q": name, "year": year, "type": "tvseries" if meta.is_tvshow else "movie"}
    imdb_search = {"searchType": "imdb", "imdb": meta.tv_show_imdb_id if meta.is_tvshow else meta.imdb_id}

    request = lambda params: {
        "method": "GET",
        "url": __search,
        "params": params,
        "headers": headers,
        "next": lambda gm: get_movie(gm)
    }
    return [request(text_search), request(imdb_search)]


def parse_search_response(core, service_name, meta, response):
    try:
        results = response.json()
    except Exception as exc:
        core.logger.error("%s - %s" % (service_name, exc))
        return []

    service = core.services[service_name]

    if "success" not in results or not results["success"]:
        return []

    def map_result(result):
        name = result.get("releaseInfo", [""])[0]
        lang = result.get("language", "")

        if lang in ss_to_code:
            lang = core.kodi.xbmc.convertLanguage(ss_to_code[lang], core.kodi.xbmc.ENGLISH_NAME)

        if lang not in meta.languages:
            return None

        rating = result.get("rating", {}).get("total", 0)

        lang_code = core.utils.get_lang_id(lang, core.kodi.xbmc.ISO_639_1)
        return {
            "service_name": service_name,
            "service": service.display_name,
            "lang": lang.capitalize(),
            "name": name,
            "rating": rating,
            "lang_code": lang_code,
            "sync": "true" if meta.filename_without_ext in name else "false",
            "impaired": "true" if result.get("hearingImpaired") else "false",
            "color": "teal",
            "action_args": {
                "url": "{}#{}".format(result["subtitleId"], name),
                "lang": lang.capitalize(),
                "filename": name,
                "full_link": result["link"],
            },
        }

    return list(map(map_result, results["data"]))


def build_download_request(core, service_name, args):
    subtitle_id = args["full_link"].split("/")[-1]
    request = {
        "method": "GET",
        "headers": {"X-API-Key": core.kodi.get_setting(service_name, 'apikey')},
        "url": "/".join([__getSub, subtitle_id, "download"]),
        "stream": True
    }

    return request
