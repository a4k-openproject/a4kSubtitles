# -*- coding: utf-8 -*-

import importlib

from .common import api

__search = importlib.import_module('a4kSubtitles.search')

__filename = 'The.Matrix.1999.1080p.BluRay.x264-AMIABLE.mkv'

def __meta(languages, preferredlanguage):
    meta = lambda: None
    meta.languages = languages
    meta.preferredlanguage = preferredlanguage
    meta.filename_without_ext = __filename.rsplit('.', 1)[0]
    meta.episode = ''
    meta.season = ''
    meta.is_tvshow = False
    return meta

def __rows(lang, count):
    return [{
        'service_name': 'svc',
        'service': 'svc',
        'lang': lang,
        'lang_code': lang[:2].lower(),
        'name': '%s.%d.%s' % (lang, i, __filename),
        'rating': 0,
        'sync': 'false',
        'impaired': 'false',
        'action_args': {'url': '%s-%d' % (lang, i)},
    } for i in range(count)]

def __prepare(results, languages, preferredlanguage, limit='30'):
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    restore = a4ksubtitles_api.mock_settings({'general.results_limit': limit})
    try:
        meta = __meta(languages, preferredlanguage)
        return __search.__prepare_results(a4ksubtitles_api.core, meta, results)
    finally:
        restore()

def __langs(results):
    return [r['lang'] for r in results]

def __counts(results):
    counts = {}
    for lang in __langs(results):
        counts[lang] = counts.get(lang, 0) + 1
    return counts

def __assert_blocked(results, first_lang):
    """Every `first_lang` row precedes every other-language row."""
    langs = __langs(results)
    other = next((i for i, l in enumerate(langs) if l != first_lang), len(langs))
    assert all(x == first_lang for x in langs[:other]), langs
    assert first_lang not in langs[other:], langs

def test_parse_languages_keeps_request_order():
    a4ksubtitles_api = api.A4kSubtitlesApi({'kodi': True})
    parse = __search.__parse_languages

    # Request order is the tiebreak the sorter reads back at search.py's
    # `meta.languages.index(x['lang'])`, so it has to be the request's, not a
    # per-process hash order. It makes the outcome DETERMINISTIC; it is not
    # what makes the preferred language win — the sorter's first key
    # (`not x['lang'] == meta.preferredlanguage`) does that.
    assert parse(a4ksubtitles_api.core, ['French', 'English']) == ['French', 'English']
    assert parse(a4ksubtitles_api.core, ['English', 'French']) == ['English', 'French']
    # De-duplicated, first occurrence wins.
    assert parse(a4ksubtitles_api.core, ['French', 'English', 'French']) == ['French', 'English']
    # 'none' parses to None and drops out.
    assert parse(a4ksubtitles_api.core, ['French', 'none', 'English']) == ['French', 'English']

def test_limit_fills_preferred_first_then_filler():
    # 3 French + 40 English at a limit of 30: the 3 preferred rows are
    # kept and English fills the other 27. Same answer for BOTH request
    # orderings — that independence is the point.
    for languages in (['French', 'English'], ['English', 'French']):
        results = __prepare(__rows('French', 3) + __rows('English', 40),
                            languages, 'French')
        assert len(results) == 30, languages
        assert __counts(results) == {'French': 3, 'English': 27}, (languages, __counts(results))
        __assert_blocked(results, 'French')

def test_limit_gives_the_whole_cap_to_the_preferred_language():
    # 40 French + 40 English at a limit of 30: English is filler only, so
    # it gets nothing. The per-language split this replaces gave 15/15.
    for languages in (['French', 'English'], ['English', 'French']):
        results = __prepare(__rows('French', 40) + __rows('English', 40),
                            languages, 'French')
        assert len(results) == 30, languages
        assert __counts(results) == {'French': 30}, (languages, __counts(results))

def test_limit_honours_english_as_the_preferred_language():
    # The mirror case: English preferred, French is the filler.
    results = __prepare(__rows('English', 3) + __rows('French', 40),
                        ['English', 'French'], 'English')
    assert len(results) == 30
    assert __counts(results) == {'English': 3, 'French': 27}, __counts(results)
    __assert_blocked(results, 'English')

def test_limit_without_a_preferred_language_follows_request_order():
    # The shape a non-Kodi caller sends (no preferredlanguage): the sorter's first key is inert, so request order
    # alone decides which language fills the cap first.
    results = __prepare(__rows('French', 3) + __rows('English', 40),
                        ['French', 'English'], '')
    assert __counts(results) == {'French': 3, 'English': 27}, __counts(results)
    __assert_blocked(results, 'French')

    results = __prepare(__rows('French', 40) + __rows('English', 40),
                        ['French', 'English'], '')
    assert __counts(results) == {'French': 30}, __counts(results)
