# -*- coding: utf-8 -*-

__api = "https://api.subsource.net/v1"

__search = __api + "/movie/search"
__getSub = __api + "/subtitle/"
__download = __getSub + "download/"

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
    def get_movie(response):
        results = response.json()
        found = results.get("results", [])
        movie_url = ""
        seasons = []

        for res in found:
            incorrect_type = res.get("type", "movie").lower() == "movie" and meta.is_tvshow
            incorrect_movie = meta.is_movie and str(res.get("releaseYear")) != str(meta.year)
            incorrect_tvshow = meta.is_tvshow and str(res.get("releaseYear")) != str(meta.tvshow_year)
            if incorrect_type or incorrect_movie or incorrect_tvshow:
                continue
            movie_url = res["link"]
            seasons = res.get("seasons", [])
            break

        params = {"language": ",".join(meta.languages).lower()}
        if meta.is_tvshow:
            season = seasons[0] if len(seasons) == 1 else seasons[max(0, int(meta.season) - 1)]
            movie_url = season["link"].replace("season=", "season-")

        return {"method": "GET", "url": __api + movie_url, "params": params}

    name = (meta.title if meta.is_movie else meta.tvshow)
    year = meta.tvshow_year if meta.is_tvshow else meta.year

    params = {"query": name + " " + year, "includeSeasons": True}
    request = {
        "method": "POST",
        "url": __search,
        "json": params,
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

    if "subtitles" not in results:
        return []

    def map_result(result):
        name = result.get("release_info", "")
        lang = result.get("language", "").capitalize()

        if lang in ss_to_code:
            lang = core.kodi.xbmc.convertLanguage(ss_to_code[lang], core.kodi.xbmc.ENGLISH_NAME)

        if lang not in meta.languages:
            return None

        rating = 10 if result.get("rating") == "good" else 0 

        lang_code = core.utils.get_lang_id(lang, core.kodi.xbmc.ISO_639_1)
        return {
            "service_name": service_name,
            "service": service.display_name,
            "lang": lang,
            "name": name,
            "rating": rating,
            "lang_code": lang_code,
            "sync": "true" if meta.filename_without_ext in result["release_info"] else "false",
            "impaired": "true" if result.get("hearing_impaired", 0) != 0 else "false",
            "color": "teal",
            "action_args": {
                "url": "{}#{}".format(result["id"], name),
                "lang": lang,
                "filename": name,
                "full_link": result["link"],
            },
        }

    return list(map(map_result, results["subtitles"]))


def build_download_request(core, service_name, args):

    def downloadsub(response):
        result = response.json()
        download_token = result["subtitle"]["download_token"]
        return {"method": "GET", "url": __download + download_token, "stream": True}

    request = {
        "method": "GET",
        "url": __getSub + args["full_link"],
        "next": lambda dw: downloadsub(dw)
    }

    return request
