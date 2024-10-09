# -*- coding: utf-8 -*-

__api = "https://api.subsource.net/api/"

__getMovie = __api + "getMovie"
__getSub = __api + "getSub"
__search = __api + "searchMovie"
__download = __api + "downloadSub/"

def build_search_requests(core, service_name, meta):
    def get_movie(response):
        results = response.json()
        found = results.get("found", [])
        movie_name = ""
        seasons = []

        for res in found:
            incorrect_type = res.get("type", "Movie") == "Movie" and meta.is_tvshow
            incorrect_movie = meta.is_movie and meta.imdb_id and res.get("imdb") and res["imdb"] != meta.imdb_id
            if incorrect_type or incorrect_movie:
                continue
            movie_name = res["linkName"]
            seasons = res.get("seasons")
            break

        params = {"movieName": movie_name, "langs": meta.languages}
        if meta.is_tvshow:
            season = seasons[0].get("number") if len(seasons) == 1 else meta.season
            params["season"] = "season-" + str(season)
        return {"method": "POST", "url": __getMovie, "data": params}

    name = (meta.title if meta.is_movie else meta.tvshow)
    year = meta.tvshow_year if meta.is_tvshow else meta.year

    params = {"query": name + " " + year}
    request = {
        "method": "POST",
        "url": __search,
        "data": params,
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

    if "subs" not in results:
        return []

    def map_result(result):
        name = result.get("releaseName", "")
        lang = result.get("lang")

        if lang not in meta.languages:
            return None

        rating = result.get("rating", 0)
        lang_code = core.utils.get_lang_id(lang, core.kodi.xbmc.ISO_639_1)
        return {
            "service_name": service_name,
            "service": service.display_name,
            "lang": lang,
            "name": name,
            "rating": rating,
            "lang_code": lang_code,
            "sync": "true" if meta.filename_without_ext in result["releaseName"] else "false",
            "impaired": "true" if result.get("hi", 0) != 0 else "false",
            "color": "teal",
            "action_args": {
                "url": "{}#{}".format(result["subId"], name),
                "lang": lang,
                "filename": name,
                "full_link": result["fullLink"],
            },
        }

    return list(map(map_result, results["subs"]))


def build_download_request(core, service_name, args):
    *_, movie, lang, sub_id = args["full_link"].split("/")
    params = {"movie": movie, "lang": lang, "id": sub_id}

    def downloadsub(response):
        result = response.json()
        download_token = result["sub"]["downloadToken"]
        return {"method": "GET", "url": __download + download_token, "stream": True}

    request = {
        "method": "POST",
        "url": __getSub,
        "data": params,
        "next": lambda dw: downloadsub(dw)
    }

    return request
