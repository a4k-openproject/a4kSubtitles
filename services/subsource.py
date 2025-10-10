import requests

API_URL = "https://api.subsource.net/api/v1"
SEARCH_URL = f"{API_URL}/movies/search"
GET_SUB_URL = f"{API_URL}/subtitles"

def search(api_key, query, search_type, year):
    if not api_key:
        raise ValueError("SubSource API Key is required.")

    headers = {"X-API-Key": api_key}
    params = {
        "searchType": "text",
        "q": query,
        "year": year,
        "type": search_type,
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_subtitles(api_key, movie_id, languages):
    if not api_key:
        raise ValueError("SubSource API Key is required.")

    headers = {"X-API-Key": api_key}
    params = {
        "movieId": movie_id,
        "language": ",".join(languages).lower(),
    }

    response = requests.get(GET_SUB_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def download_subtitle(api_key, subtitle_id):
    if not api_key:
        raise ValueError("SubSource API Key is required.")

    headers = {"X-API-Key": api_key}
    url = f"{GET_SUB_URL}/{subtitle_id}/download"

    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    return response.content