# C:\...\a4kSubtitles-SubtitlecatMod\a4kSubtitles\services\subtitlecat.py

# -*- coding: utf-8 -*-

# NO direct import of 'from a4kSubtitles.lib import logger' needed here for 'log' instance
from a4kSubtitles.lib import utils as a4k_utils
# from a4kSubtitles.lib import request as a4k_request

import requests as system_requests
from bs4 import BeautifulSoup
import urllib.parse

# REMOVE this line: log = logger.Logger.get_logger(__name__) 

__subtitlecat_base_url = "https://www.subtitlecat.com"
__user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 a4kSubtitles-SubtitlecatMod/1.0.0'

def build_search_requests(core, service_name, meta):
    # Use core.logger directly
    core.logger.debug(f"[{service_name}] Building search requests for: {meta}") 
    
    query_title = meta.tvshow if meta.is_tvshow else meta.title
    if not query_title:
        core.logger.warning(f"[{service_name}] No title found in meta.") # Use core.logger
        return []

    search_query_parts = [query_title]
    if meta.year:
        search_query_parts.append(str(meta.year))
    
    search_term = " ".join(search_query_parts)
    encoded_query = urllib.parse.quote_plus(search_term)
    search_url = f"{__subtitlecat_base_url}/index.php?search={encoded_query}&d=1"

    core.logger.info(f"[{service_name}] Search URL: {search_url}") # Use core.logger
    
    request_dict = {
        'method': 'GET',
        'url': search_url,
        'headers': {'User-Agent': __user_agent},
    }
    return [request_dict]

def parse_search_response(core, service_name, meta, response):
    core.logger.debug(f"[{service_name}] Parsing search response. Status: {response.status_code}") # Use core.logger
    results = []
    
    if response.status_code != 200:
        core.logger.error(f"[{service_name}] Search request failed. Status: {response.status_code}, URL: {response.url if response else 'N/A'}") # Use core.logger
        return results

    try:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'lxml')
    except Exception as e:
        core.logger.error(f"[{service_name}] Error creating BeautifulSoup object: {e}") # Use core.logger
        return results

    display_name_for_service = service_name 
    try:
        service_module = core.services.get(service_name)
        if service_module and hasattr(service_module, 'display_name'):
            display_name_for_service = service_module.display_name
    except Exception as e_disp:
        core.logger.warning(f"[{service_name}] Could not get display_name from core.services: {e_disp}. Using service_name.") # Use core.logger

    # --- PARSING SEARCH RESULTS PAGE ---
    results_table_body = soup.select_one('table.table.sub-table tbody')
    if not results_table_body:
        results_table_body = soup.find('tbody') 
        if not results_table_body:
             core.logger.warning(f"[{service_name}] A.1: Main results table body ('table.sub-table tbody' or generic 'tbody') not found on {response.url}") # Use core.logger
             return results
    
    potential_movie_items_tr = results_table_body.find_all('tr')
    core.logger.info(f"[{service_name}] Found {len(potential_movie_items_tr)} potential movie rows on search page: {response.url}") # Use core.logger

    for item_tr in potential_movie_items_tr:
        link_tag = item_tr.select_one('td:first-child > a')
        if not link_tag:
            core.logger.debug(f"[{service_name}] No link tag (td:first-child > a) found in a row. Skipping row.") # Use core.logger
            continue
            
        movie_page_relative_url = link_tag.get('href')
        if not (movie_page_relative_url and movie_page_relative_url.startswith('/subs/') and '.html' in movie_page_relative_url):
            core.logger.debug(f"[{service_name}] Found a link, but href '{movie_page_relative_url}' doesn't match expected pattern. Skipping.") # Use core.logger
            continue

        movie_title_on_page = link_tag.get_text(strip=True)
        if not movie_title_on_page:
            movie_title_on_page = "Unknown Title (No text in link)"
        
        movie_page_full_url = __subtitlecat_base_url + movie_page_relative_url
        core.logger.debug(f"[{service_name}] Processing movie link: '{movie_title_on_page}' -> {movie_page_full_url}") # Use core.logger

        try:
            detail_response = system_requests.get(movie_page_full_url, headers={'User-Agent': __user_agent}, timeout=15)
            detail_response.raise_for_status()
            detail_html_content = detail_response.text
            detail_soup = BeautifulSoup(detail_html_content, 'lxml')
        except Exception as e_detail:
            core.logger.error(f"[{service_name}] Failed to fetch detail page {movie_page_full_url}: {e_detail}") # Use core.logger
            continue
        
        try:
            original_subtitle_id_from_url = movie_page_relative_url.split('/')[2]
            original_filename_base_from_url = movie_page_relative_url.split('/')[-1].replace('.html', '')
        except IndexError:
            core.logger.error(f"[{service_name}] Could not parse ID and filename base from relative URL: {movie_page_relative_url}") # Use core.logger
            continue

        language_entries = detail_soup.select('div.sub-single')
        if not language_entries:
            core.logger.debug(f"[{service_name}] No language entries ('div.sub-single') found on detail page: {movie_page_full_url}") # Use core.logger
        
        for entry_div in language_entries:
            img_tag = entry_div.select_one('img.flag')
            if not img_tag:
                core.logger.debug(f"[{service_name}] No img.flag found in a language entry. Skipping entry.") # Use core.logger
                continue
            sc_lang_code = img_tag.get('alt')
            if not sc_lang_code:
                core.logger.debug(f"[{service_name}] img.flag found but no alt attribute. Skipping entry.") # Use core.logger
                continue

            lang_name_span = entry_div.select_one('span:nth-of-type(2)')
            sc_lang_name_full = sc_lang_code 
            if lang_name_span:
                sc_lang_name_full = lang_name_span.get_text(strip=True)
            if not sc_lang_name_full:
                sc_lang_name_full = sc_lang_code

            try:
                kodi_target_lang_full = core.utils.get_language_name_from_code(sc_lang_code, core.kodi.xbmc.ENGLISH_NAME)
                kodi_target_lang_2_letter = core.utils.get_language_code_from_name(kodi_target_lang_full, core.kodi.xbmc.ISO_639_1) if kodi_target_lang_full else sc_lang_code.split('-')[0].lower()
            except Exception as e_lang_conv:
                core.logger.warning(f"[{service_name}] Error converting lang code '{sc_lang_code}': {e_lang_conv}. Using raw values.") # Use core.logger
                kodi_target_lang_full = sc_lang_name_full
                kodi_target_lang_2_letter = sc_lang_code.split('-')[0].lower()

            if kodi_target_lang_full not in meta.languages:
                # core.logger.debug(f"[{service_name}] Skipping language {kodi_target_lang_full} (sc_code: {sc_lang_code}) as it's not in requested: {meta.languages}")
                continue

            srt_download_link = f"{__subtitlecat_base_url}/subs/{original_subtitle_id_from_url}/{original_filename_base_from_url}-{sc_lang_code}.srt"
            srt_filename = f"{original_filename_base_from_url}-{sc_lang_code}.srt"

            result_item = {
                'service_name': service_name,
                'service': display_name_for_service,
                'lang': kodi_target_lang_full,
                'name': f"{movie_title_on_page} ({sc_lang_name_full})",
                'rating': 0,
                'lang_code': kodi_target_lang_2_letter,
                'sync': 'false',
                'impaired': 'false',
                'color': 'white', 
                'action_args': {
                    'url': srt_download_link,
                    'lang': kodi_target_lang_full,
                    'filename': srt_filename,
                    'gzip': False,
                    'service_name': service_name 
                }
            }
            results.append(result_item)
            core.logger.debug(f"[{service_name}] Added result: {result_item['name']}") # Use core.logger

    core.logger.info(f"[{service_name}] Found {len(results)} subtitle results after parsing all pages.") # Use core.logger
    return results

def build_download_request(core, service_name, args):
    download_url = args['url']
    filename_for_log = args.get('filename', download_url.split('/')[-1])
    core.logger.info(f"[{service_name}] Building download request for: {filename_for_log} from {download_url}") # Use core.logger

    request_dict = {
        'method': 'GET',
        'url': download_url,
        'headers': {'User-Agent': __user_agent},
        'stream': True
    }
    return request_dict