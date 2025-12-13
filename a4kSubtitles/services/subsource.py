# -*- coding: utf-8 -*-

__api = "https://api.subsource.net/api/v1"

__search = __api + "/movies/search"
__getSub = __api + "/subtitles"

code_langs = {
    'ar': ('arabic',),
    'en': ('english',),
    'bn': ('bengali',),
    'id': ('indonesian',),
    'ab': ('abkhazian',),
    'af': ('afrikaans',),
    'sq': ('albanian',),
    'am': ('amharic',),
    'an': ('aragonese',),
    'hy': ('armenian',),
    'as': ('assamese',),
    'fa': ('farsi_persian',),
    'ast': ('asturian',),
    'az': ('azerbaijani',),
    'eu': ('basque',),
    'be': ('belarusian',),
    'zh': ('big_5_code', 'chinese', 'chinese_cantonese', 'chinese_simplified', 'chinese_traditional', 'chinese_bg_code', 'chinese_bilingual'),
    'bs': ('bosnian',),
    'pt': ('brazilian_portuguese', 'portuguese'),
    'br': ('breton',),
    'bg': ('bulgarian',),
    'my': ('burmese',),
    'ca': ('catalan',),
    'hr': ('croatian',),
    'cs': ('czech',),
    'da': ('danish',),
    'prs': ('dari',),
    'nl': ('dutch',),
    'eo': ('espranto',),
    'et': ('estonian',),
    'ext': ('extremaduran',),
    'fil': ('filipino',),
    'fi': ('finnish',),
    'fr': ('french', 'french_canada', 'french_france'),
    'gd': ('gaelic',),
    'gl': ('gaelician',),
    'ka': ('georgian',),
    'de': ('german',),
    'el': ('greek',),
    'kl': ('greenlandic',),
    'he': ('hebrew',),
    'hi': ('hindi',),
    'hu': ('hungarian',),
    'is': ('icelandic',),
    'ig': ('igbo',),
    'ia': ('interlingua',),
    'ga': ('irish',),
    'it': ('italian',),
    'ja': ('japanese',),
    'kn': ('kannada',),
    'kk': ('kazakh',),
    'km': ('khmer',),
    'ko': ('korean',),
    'ku': ('kurdish',),
    'ky': ('kyrgyz',),
    'lv': ('latvian',),
    'lt': ('lithuanian',),
    'lb': ('luxembourgish',),
    'mk': ('macedonian',),
    'ml': ('malayalam',),
    'mni': ('manipuri',),
    'mr': ('marathi',),
    'ms': ('malay',),
    'mn': ('mongolian',),
    'cnr': ('montenegrin',),
    'nv': ('navajo',),
    'ne': ('nepali',),
    'se': ('northen_sami',),
    'no': ('norwegian',),
    'oc': ('occitan',),
    'ps': ('pashto', 'pushto'),
    'or': ('odia',),
    'pl': ('polish',),
    'ro': ('romanian',),
    'ru': ('russian',),
    'sat': ('santli',),
    'sr': ('serbian',),
    'sd': ('sindhi',),
    'si': ('sinhala', 'sinhalese'),
    'sk': ('slovak',),
    'sl': ('slovenian',),
    'so': ('somali',),
    'wen': ('sorbian',),
    'es': ('spanish', 'spanish_latin_america', 'spanish_spain'),
    'sw': ('swahili',),
    'sv': ('swedish',),
    'syl': ('sylheti',),
    'syr': ('syriac',),
    'tl': ('tagalog',),
    'ta': ('tamil',),
    'tt': ('tatar',),
    'te': ('telugu',),
    'tet': ('tetum',),
    'th': ('thai',),
    'tok': ('toki_pona',),
    'tr': ('turkish',),
    'tk': ('turkmen',),
    'uk': ('ukrainian',),
    'ur': ('urdu',),
    'uz': ('uzbek',),
    'vi': ('vietnamese',),
    'cy': ('welsh',)
}
ss_to_code = {v: k for k, vals in code_langs.items() for v in vals}

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


        required_languages = [
            code_langs.get(core.utils.get_lang_id(kodi_lang, core.kodi.xbmc.ISO_639_1), (kodi_lang.lower(),))
            for kodi_lang in meta.languages
        ]
        languages = ",".join(sum(required_languages, ()))

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
            lang_code = ss_to_code[lang]
            lang = core.kodi.xbmc.convertLanguage(ss_to_code[lang], core.kodi.xbmc.ENGLISH_NAME)
        else:
            lang_code = core.utils.get_lang_id(lang.capitalize(), core.kodi.xbmc.ISO_639_1)

        if lang not in meta.languages:
            return None

        rating = result.get("rating", {}).get("total", 0)

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
