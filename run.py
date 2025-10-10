from flask import Flask, render_template, jsonify, request
from services import subsource
import os
from imdb import IMDb

app = Flask(__name__)

SUBSOURCE_API_KEY = os.environ.get("SUBSOURCE_API_KEY")
ia = IMDb()

# Stremio uses 3-letter ISO 639-2 codes, SubSource uses full names
LANG_MAP = {
    'eng': 'English',
    'spa': 'Spanish (Spain)',
    'fre': 'French (France)',
    'ger': 'German',
    'ita': 'Italian',
    'por': 'Portuguese',
    'pob': 'Brazilian Portuguese',
    'dut': 'Dutch',
    'rus': 'Russian',
    'bul': 'Bulgarian',
    'chi': 'Chinese(Simplified)',
    'per': 'Farsi/Persian',
    'ice': 'Icelandic',
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "id": "community.stremio.subsource",
        "version": "1.0.0",
        "name": "SubSource Subtitles",
        "description": "Provides subtitles from SubSource.",
        "types": ["movie", "series"],
        "resources": ["subtitles"],
        "catalogs": [],
        "idPrefixes": ["tt"]
    })

@app.route('/subtitles/<type>/<id>/<lang>.json')
def get_subtitles_for(type, id, lang):
    if not SUBSOURCE_API_KEY:
        return jsonify({"subtitles": []})

    try:
        parts = id.split(':')
        imdb_id = parts[0]
        season = None
        episode = None
        if type == 'series' and len(parts) == 3:
            season = parts[1]
            episode = parts[2]

        movie = ia.get_movie(imdb_id.replace('tt', ''))

        if not movie:
            return jsonify({"subtitles": []})

        title = movie.get('title')
        year = movie.get('year')

        search_type = "movie" if type == "movie" else "tvseries"

        search_results = subsource.search(SUBSOURCE_API_KEY, title, search_type, year)

        if not search_results.get("data"):
            return jsonify({"subtitles": []})

        movie_id = None
        for result in search_results.get("data", []):
            if result.get("imdbId") == imdb_id:
                if type == 'series':
                    if str(result.get("season")) == season:
                        movie_id = result.get("movieId")
                        break
                else:
                    movie_id = result.get("movieId")
                    break

        if not movie_id:
            return jsonify({"subtitles": []})

        subsource_lang = LANG_MAP.get(lang)
        if not subsource_lang:
            return jsonify({"subtitles": []})

        subtitle_results = subsource.get_subtitles(SUBSOURCE_API_KEY, movie_id, [subsource_lang])

        subtitles = []
        for sub in subtitle_results.get("data", []):
            if type == 'series':
                # Assuming the subtitle object from SubSource has an 'episode' field.
                if 'episode' in sub and str(sub.get("episode")) != episode:
                    continue

            subtitles.append({
                "id": sub.get("subtitleId"),
                "url": f"{request.url_root}download/{sub.get('subtitleId')}",
                "lang": lang,
                "releaseName": sub.get("releaseInfo")[0] if sub.get("releaseInfo") else "N/A"
            })

        return jsonify({"subtitles": subtitles})

    except Exception as e:
        app.logger.error(f"Error fetching subtitles: {e}", exc_info=True)
        return jsonify({"subtitles": []})

@app.route('/download/<subtitle_id>')
def download(subtitle_id):
    if not SUBSOURCE_API_KEY:
        return "API Key not configured", 400

    try:
        subtitle_content = subsource.download_subtitle(SUBSOURCE_API_KEY, subtitle_id)
        return subtitle_content
    except Exception as e:
        app.logger.error(f"Error downloading subtitle: {e}", exc_info=True)
        return "Error downloading subtitle", 500

if __name__ == '__main__':
    app.run(debug=True)