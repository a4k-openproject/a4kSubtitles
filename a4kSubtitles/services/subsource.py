# -*- coding: utf-8 -*-

__api = "https://api.subsource.net/api/"

__getMovie = __api + "getMovie"
__getSub = __api + "getSub"
__search = __api + "searchMovie"
__download = __api + "downloadSub/"

def __extract_season_episode(core, text):
    pattern = core.re.compile(r'(?:S(\d+)|Season\s*(\d+))[^E]*?(?:E(\d+)|Episode\s*(\d+))', core.re.IGNORECASE)
    match = pattern.search(text)

    if match:
        # Extract season and episode numbers from groups
        season = match.group(1) or match.group(2)
        episode = match.group(3) or match.group(4)
        return (season, episode)

    # If no matches found, attempt to capture episode-like sequences
    fallback_pattern = core.re.compile(r'\bE?P?(\d{2,5})\b', core.re.IGNORECASE)
    fallback_matches = fallback_pattern.findall(text)

    if fallback_matches:
        # Assuming the last number in the fallback matches is the episode number
        episode_number = fallback_matches[-1]
        return (None, episode_number)

    return (None, None)

def build_search_requests(core, service_name, meta):
    def get_movie(response):
        results = response.json()
        found = results.get("found", [])
        movie_name = ""

        for res in found:
            if res.get("type", "Movie") == "Movie" and meta.is_tvshow:
                continue
            movie_name = res["linkName"]
            break

        params = {"movieName": movie_name, "langs": meta.languages}
        if meta.is_tvshow:
            params["season"] = "season-" + meta.season
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

    movie_details = results.get("movie", {})

    # altname = movie_details.get("altName")
    full_name = movie_details.get("fullName", "")

    def map_result(result):
        name = result.get("releaseName", "")
        lang = result.get("lang")

        if lang not in meta.languages:
            return None

        rating = result.get("rating", 0)
        lang_code = core.utils.get_lang_id(lang, core.kodi.xbmc.ISO_639_1)

        if meta.is_tvshow:
            subtitle_season = core.re.search(r'Season\s(\d+)', full_name)
            season, episode = __extract_season_episode(core, name)
            season = subtitle_season.group(1).zfill(2) if subtitle_season else season

            if season == meta.season.zfill(2) and episode == meta.episode.zfill(2):
                name = meta.filename
            elif not season and meta.season == "1" and episode == meta.episode.zfill(2):
                name = meta.filename

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
                "url": result["subId"],
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
