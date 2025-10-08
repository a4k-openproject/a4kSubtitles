# -*- coding: utf-8 -*-

__api = "https://api.subsource.net/api/v1"

__search = __api + "/movies/search"
__getSub = __api + "/subtitles"

ss_to_code = {
    "Big 5 code": "zh",
    "Brazilian Portuguese": "pt-BR",
    "Bulgarian": "bg",
    "Chinese BG code": "zh",
    "Farsi/Persian": "fa",
    "Chinese(Simplified)": "zh-Hans",
    "Chinese(Traditional)": "zh-Hant",
    "French(France)": "fr-FR",
    "Icelandic": "is",
    "Spanish(Latin America)": "es-419",
    "Spanish(Spain)": "es-ES"
}

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

        params = {"movieId": movie_id or first_season_id, "language": ",".join(meta.languages).lower()}

        return {"method": "GET", "url": __getSub, "params": params, "headers": headers}

    name = (meta.title if meta.is_movie else meta.tvshow)
    year = meta.tvshow_year if meta.is_tvshow else meta.year

    params = {"searchType": "text", "q": name, "year": year, "type": "tvseries" if meta.is_tvshow else "movie"}
    request = {
        "method": "GET",
        "url": __search,
        "params": params,
        "headers": headers,
        "next": lambda gm: get_movie(gm)
    }
    return [request]


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
        lang = result.get("language", "").capitalize()

        if lang in ss_to_code:
            lang = core.kodi.xbmc.convertLanguage(ss_to_code[lang], core.kodi.xbmc.ENGLISH_NAME)

        if lang not in meta.languages:
            return None

        rating = result.get("rating", {}).get("total", 0)

        lang_code = core.utils.get_lang_id(lang, core.kodi.xbmc.ISO_639_1)
        return {
            "service_name": service_name,
            "service": service.display_name,
            "lang": lang,
            "name": name,
            "rating": rating,
            "lang_code": lang_code,
            "sync": "true" if meta.filename_without_ext in name else "false",
            "impaired": "true" if result.get("hearingImpaired") else "false",
            "color": "teal",
            "action_args": {
                "url": "{}#{}".format(result["subtitleId"], name),
                "lang": lang,
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
