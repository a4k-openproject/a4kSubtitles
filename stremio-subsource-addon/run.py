from flask import Flask, render_template, jsonify, request, abort, Response, stream_with_context
import os
import requests
import json
import base64

app = Flask(__name__)

MANIFEST = {
    "id": "community.stremio.subsource",
    "version": "1.0.0",
    "name": "SubSource",
    "description": "Addon for SubSource subtitles.",
    "resources": ["subtitles"],
    "types": ["movie", "series"],
    "idPrefixes": ["tt"],
    "behaviorHints": {
        "configurable": True,
        "configurationRequired": True
    },
    "config": [
        {
            "key": "subsource_api_key",
            "title": "SubSource API Key",
            "type": "text",
            "required": True
        }
    ]
}

SUBSOURCE_API_URL = "https://api.subsource.net/api/v1"
CINEMETA_URL = "https://v3-cinemeta.strem.io"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
@app.route('/<config>/manifest.json')
def manifest(config=None):
    return jsonify(MANIFEST)

def get_api_key_from_config(config_str):
    if not config_str:
        return None
    try:
        # The config is a base64 encoded JSON object.
        # It might have URL-safe characters, so replace them.
        config_str = config_str.replace('-', '+').replace('_', '/')
        # Add padding if it's missing.
        padding = len(config_str) % 4
        if padding:
            config_str += '=' * (4 - padding)
        decoded_config = base64.b64decode(config_str).decode('utf-8')
        config_json = json.loads(decoded_config)
        return config_json.get('subsource_api_key')
    except Exception as e:
        print(f"Error decoding config: {e}")
        return None

@app.route('/subtitles/<type>/<id>.json')
@app.route('/<config>/subtitles/<type>/<id>.json')
def subtitles(type, id, config=None):
    api_key = get_api_key_from_config(config)
    if not api_key:
        return jsonify({"subtitles": []})

    headers = {"X-API-Key": api_key}

    imdb_id = id.split(':')[0]

    # 1. Get metadata from Cinemeta
    meta_url = f"{CINEMETA_URL}/meta/{type}/{imdb_id}.json"
    try:
        meta_resp = requests.get(meta_url)
        meta_resp.raise_for_status()
        metadata = meta_resp.json()['meta']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metadata from Cinemeta: {e}")
        return jsonify({"subtitles": []})

    name = metadata['name']
    year = metadata.get('year')
    season = None
    if type == 'series' and len(id.split(':')) > 1:
        season = id.split(':')[1]

    # 2. Search for movieId on SubSource
    search_url = f"{SUBSOURCE_API_URL}/movies/search"
    search_params = {
        "searchType": "text",
        "q": name,
        "year": year,
        "type": "tvseries" if type == 'series' else "movie"
    }
    try:
        search_resp = requests.get(search_url, headers=headers, params=search_params)
        search_resp.raise_for_status()
        search_data = search_resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching on SubSource: {e}")
        return jsonify({"subtitles": []})

    if not search_data.get('success') or not search_data.get('data'):
        return jsonify({"subtitles": []})

    movie_id = None
    first_season_id = None
    for res in search_data['data']:
        if type == 'movie' and imdb_id and res.get("imdbId") and res["imdbId"] != imdb_id:
            continue

        if res.get("season") == 1:
            first_season_id = res.get("movieId")

        if type == 'series':
            if season and str(res.get("season")) != season:
                continue

        movie_id = res.get("movieId")
        if movie_id:
            break

    movie_id = movie_id or first_season_id
    if not movie_id:
        return jsonify({"subtitles": []})

    # 3. Get subtitles from SubSource
    subtitles_url = f"{SUBSOURCE_API_URL}/subtitles"
    subtitles_params = {"movieId": movie_id}
    try:
        subtitles_resp = requests.get(subtitles_url, headers=headers, params=subtitles_params)
        subtitles_resp.raise_for_status()
        subtitles_data = subtitles_resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting subtitles from SubSource: {e}")
        return jsonify({"subtitles": []})

    if not subtitles_data.get('success') or not subtitles_data.get('data'):
        return jsonify({"subtitles": []})

    # 4. Format subtitles for Stremio
    subtitles_list = []
    for sub in subtitles_data['data']:
        sub_id = sub['subtitleId']
        download_url = f"{request.url_root}{config}/download/{sub_id}.srt"

        lang_name = sub.get("language", "unknown").capitalize()

        sub_entry = {
            "id": sub_id,
            "url": download_url,
            "lang": lang_name,
        }

        subtitles_list.append(sub_entry)

    return jsonify({"subtitles": subtitles_list})

@app.route('/download/<subtitle_id>.srt')
@app.route('/<config>/download/<subtitle_id>.srt')
def download_subtitle(subtitle_id, config=None):
    api_key = get_api_key_from_config(config)
    if not api_key:
        abort(401) # Unauthorized

    download_url = f"{SUBSOURCE_API_URL}/subtitles/{subtitle_id}/download"
    headers = {"X-API-Key": api_key}

    try:
        req = requests.get(download_url, headers=headers, stream=True)
        req.raise_for_status()
        return Response(stream_with_context(req.iter_content(chunk_size=1024)), content_type=req.headers['content-type'])
    except requests.exceptions.RequestException as e:
        print(f"Error downloading subtitle: {e}")
        abort(4e4)

if __name__ == '__main__':
    app.run(debug=True)