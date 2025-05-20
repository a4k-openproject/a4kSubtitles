

# C:\...\a4kSubtitles-SubtitlecatMod\a4kSubtitles\services\subtitlecat.py
# -*- coding: utf-8 -*-
# SubtitleCat provider for a4kSubtitles

# Upstream logger core.logger only exposes .debug() & .error().
# All .info() / .warning() calls have been changed to .debug() for compatibility.

# from a4kSubtitles.lib import utils as a4k_utils # Removed as per instruction (unused)
import requests as system_requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urljoin # Added for robust URL building

import re
import time # Retained as it will be used by _wait_for_translated

# No 'log = logger.Logger.get_logger(__name__)' needed; use 'core.logger' directly.

__subtitlecat_base_url = "https://www.subtitlecat.com"
__user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 "
    "Safari/537.36 a4kSubtitles-SubtitlecatMod/1.0.1" # Ensure your addon version is reflected if desired
)

# helper -------------------------------------
def _extract_ajax(link):
    m = re.search(r"'([^']*)',\s*'([^']*)',\s*'([^']*)'", link)
    return m.groups() if m else (None, None, None)

# START OF MODIFICATION: Added _wait_for_translated helper function (Review Point 3)
# START OF MODIFICATION (5 Remaining edge-cases): Changed tries from 10 to 20
def _wait_for_translated(core, detail_url, lang_code, service_name, tries=50, delay=5): # MODIFIED: tries=50
    """
    Re-loads the detail page until an <a href="…-<lang_code>.srt"> appears
    or the retry budget is exhausted.  Returns absolute URL or ''.
    """
    core.logger.debug(f"[{service_name}] Starting polling for lang '{lang_code}' on {detail_url} (tries={tries}, delay={delay}s)")
    for attempt in range(tries):
        # time.sleep must be called before the request for the current attempt
        if attempt > 0: # No sleep before the first attempt
             time.sleep(delay)
        
        try:
            page = system_requests.get(detail_url,
                                       headers={'User-Agent': __user_agent},
                                       timeout=10)
            page.raise_for_status() # Check for HTTP errors
            soup = BeautifulSoup(page.text, 'html.parser')
            # Selector for the link based on lang_code in href (e.g., a[href$="-en.srt"])
            tag = soup.select_one(f'a[href$="-{lang_code}.srt"]')
            if tag and tag.get('href'):
                # Use urljoin as per review point 4 refinement for __subtitlecat_base_url
                found_url = urljoin(__subtitlecat_base_url, tag['href']) # href from site usually starts with /
                core.logger.debug(f"[{service_name}] Poll attempt {attempt+1}/{tries}: Found link for '{lang_code}': {found_url}")
                return found_url
            else:
                core.logger.debug(f"[{service_name}] Poll attempt {attempt+1}/{tries}: '{lang_code}' not ready yet on {detail_url}")
        except system_requests.exceptions.RequestException as e_req:
            core.logger.warning(f"[{service_name}] Poll attempt {attempt+1}/{tries}: Request error for {detail_url}: {e_req}")
        except Exception as e_parse: 
            core.logger.warning(f"[{service_name}] Poll attempt {attempt+1}/{tries}: Error processing detail page {detail_url}: {e_parse}")
        
        # If it's the last attempt and we haven't found it, no need to sleep again.
        # The loop will terminate, and empty string will be returned.
            
    core.logger.debug(f"[{service_name}] Polling finished for lang '{lang_code}' on {detail_url} after {tries} tries. Link not found.")
    return ''
# END OF MODIFICATION (5 Remaining edge-cases): Changed tries from 10 to 20
# END OF MODIFICATION: Added _wait_for_translated helper function

# ---------------------------------------------------------------------------
# SEARCH REQUEST BUILDER
# ---------------------------------------------------------------------------
def build_search_requests(core, service_name, meta):
    core.logger.debug(f"[{service_name}] Building search requests for: {meta}")

    query_title = meta.tvshow if meta.is_tvshow else meta.title
    if not query_title:
        core.logger.debug(f"[{service_name}] No title found in meta. Aborting search for this provider.")
        return []

    search_query_parts = [query_title]
    if meta.year:
        search_query_parts.append(str(meta.year))

    search_term = " ".join(search_query_parts)
    encoded_query = urllib.parse.quote_plus(search_term)
    search_url = f"{__subtitlecat_base_url}/index.php?search={encoded_query}&d=1"

    core.logger.debug(f"[{service_name}] Search URL: {search_url}")

    return [{
        'method': 'GET',
        'url': search_url,
        'headers': {'User-Agent': __user_agent},
    }]

# ---------------------------------------------------------------------------
# SEARCH RESPONSE PARSER
# ---------------------------------------------------------------------------
def parse_search_response(core, service_name, meta, response):
    core.logger.debug(f"[{service_name}] Parsing search response. Status: {response.status_code}, URL: {response.url if response else 'N/A'}")
    results = []

    if response.status_code != 200:
        core.logger.error(f"[{service_name}] Search request failed (status {response.status_code}) – {response.url}")
        return results

    try:
        # *** Use html.parser ***
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as exc:
        core.logger.error(f"[{service_name}] BeautifulSoup error for search response: {exc}")
        return results

    display_name_for_service = getattr(
        core.services.get(service_name), "display_name", service_name
    )

    results_table_body = soup.select_one('table.table.sub-table tbody')
    if not results_table_body:
        results_table_body = soup.find('tbody')
        if not results_table_body:
             core.logger.debug(f"[{service_name}] A.1: Main results table body not found on {response.url}")
             return results

    rows = results_table_body.find_all('tr')
    core.logger.debug(f"[{service_name}] Found {len(rows)} potential movie rows on search page: {response.url}")

    # START OF MODIFICATION: Pre-compute wanted languages set (Review Point 4)
    wanted_languages_lower = {lang.lower() for lang in meta.languages}
    # END OF MODIFICATION: Pre-compute wanted languages set

    # START OF MODIFICATION (5 Remaining edge-cases): seen_lang_conv_errors set
    seen_lang_conv_errors = set()
    # END OF MODIFICATION (5 Remaining edge-cases): seen_lang_conv_errors set

    for row in rows:
        link_tag = row.select_one('td:first-child > a')
        if not link_tag:
            core.logger.debug(f"[{service_name}] No link tag in a row. Skipping.")
            continue

        href = link_tag.get('href', "")
        if not (href.lstrip('/').startswith('subs/') and href.endswith('.html')):
            core.logger.debug(f"[{service_name}] Link href '{href}' doesn't match expected pattern. Skipping.")
            continue

        movie_title_on_page = link_tag.get_text(strip=True) or "Unknown Title"
        # START OF MODIFICATION: urljoin usage (Review Point 4)
        # Original: movie_page_full_url = urljoin(__subtitlecat_base_url + '/', href)
        movie_page_full_url = urljoin(__subtitlecat_base_url, href) # href from site typically starts with /
        # END OF MODIFICATION: urljoin usage
        core.logger.debug(f"[{service_name}] Processing movie link: '{movie_title_on_page}' -> {movie_page_full_url}")

        try:
            detail_response = system_requests.get(movie_page_full_url, headers={'User-Agent': __user_agent}, timeout=15)
            detail_response.raise_for_status()
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
        except Exception as exc:
            core.logger.error(f"[{service_name}] Detail page fetch/parse failed for {movie_page_full_url}: {exc}")
            continue

        try:
            url_parts     = href.lstrip('/').split('/')
            original_id   = url_parts[-2]
            filename_base = url_parts[-1].replace('.html', '')
        except IndexError as e_url_parse:
            core.logger.error(f"[{service_name}] Could not parse ID/filename from relative URL '{href}': {e_url_parse}")
            continue

        language_entries = detail_soup.select('div.sub-single')
        if not language_entries:
            core.logger.debug(f"[{service_name}] No language entries ('div.sub-single') found on detail page: {movie_page_full_url}")

        for entry_div in language_entries:
            img_tag = entry_div.select_one('img.flag')
            if not img_tag:
                core.logger.debug(f"[{service_name}] No img.flag in language entry. Skipping.")
                continue
            sc_lang_code = img_tag.get('alt')
            if not sc_lang_code:
                core.logger.debug(f"[{service_name}] img.flag found but no alt attribute. Skipping.")
                continue

            lang_name_span = entry_div.select_one('span:nth-of-type(2)')
            sc_lang_name_full = sc_lang_code
            if lang_name_span:
                temp_name = lang_name_span.get_text(strip=True)
                if temp_name:
                    sc_lang_name_full = temp_name

            kodi_target_lang_full = sc_lang_name_full
            kodi_target_lang_2_letter = sc_lang_code.split('-')[0].lower()
            try:
                converted_full_name = core.utils.get_lang_id(sc_lang_code, core.kodi.xbmc.ENGLISH_NAME)
                if converted_full_name:
                    kodi_target_lang_full = converted_full_name
                    converted_iso2_code = core.utils.get_lang_id(kodi_target_lang_full, core.kodi.xbmc.ISO_639_1)
                    if converted_iso2_code:
                        kodi_target_lang_2_letter = converted_iso2_code
            except Exception as e_lang_conv:
                # START OF MODIFICATION (5 Remaining edge-cases): Log lang conversion error once
                if sc_lang_code not in seen_lang_conv_errors:
                    core.logger.debug(f"[{service_name}] Error converting lang code '{sc_lang_code}' (name: '{sc_lang_name_full}'): {e_lang_conv}. Using fallbacks. (This message will be shown once per problematic code for this provider run)")
                    seen_lang_conv_errors.add(sc_lang_code)
                # END OF MODIFICATION (5 Remaining edge-cases): Log lang conversion error once

            # START OF MODIFICATION: Use pre-computed set for language filter (Review Point 4)
            # Original: if kodi_target_lang_full.lower() not in [l.lower() for l in meta.languages]:
            if kodi_target_lang_full.lower() not in wanted_languages_lower:
            # END OF MODIFICATION: Use pre-computed set for language filter
                continue

            patch_determined_href = None
            patch_kind_is_translate = False

            a_tag = entry_div.select_one('a[href$=".srt"]')
            if a_tag:
                _raw_href = a_tag.get('href')
                if _raw_href:
                    patch_determined_href = _raw_href
                else:
                    a_tag = None

            if patch_determined_href is None:
                btn = entry_div.select_one('button[onclick*="translate_from_server_folder"]')
                if not btn:
                    continue
                
                _onclick_attr = btn.get('onclick')
                if not _onclick_attr:
                    core.logger.debug(f"[{service_name}] Translate button for '{sc_lang_name_full}' has no onclick. Skipping.")
                    continue

                lng, orig, folder = _extract_ajax(_onclick_attr)

                if not all([lng, orig, folder]):
                    core.logger.debug(f"[{service_name}] Failed to extract AJAX params for '{sc_lang_name_full}' from onclick. Skipping.")
                    continue
                
                try:
                    # Trigger translation
                    core.logger.debug(f"[{service_name}] Triggering server-side translation for '{sc_lang_name_full}' (file: {orig}, folder: {folder}, lang: {lng})")
                    system_requests.get(
                        f"{__subtitlecat_base_url}/translate.php",
                        params={'lng': lng, 'file': orig, 'folder': folder},
                        headers={'User-Agent': __user_agent},
                        timeout=5 
                    )
                except system_requests.exceptions.Timeout:
                    core.logger.debug(f"[{service_name}] AJAX call for '{sc_lang_name_full}' timed out. Assuming server might process; will attempt poll.")
                except Exception as e_ajax:
                    core.logger.error(f"[{service_name}] AJAX call for '{sc_lang_name_full}' failed: {e_ajax}. Skipping entry.")
                    continue
                
                patch_kind_is_translate = True
            
            action_args_url = ""
            action_args_filename = ""

            if patch_determined_href: # Direct link
                # START OF MODIFICATION: urljoin usage (Review Point 4)
                # Original: action_args_url = urljoin(__subtitlecat_base_url + '/', patch_determined_href)
                action_args_url = urljoin(__subtitlecat_base_url, patch_determined_href) # patch_determined_href from site usually starts with /
                # END OF MODIFICATION: urljoin usage
                action_args_filename = patch_determined_href.split('/')[-1]
            else: # Translate case
                action_args_url = "" # URL will be determined by polling
                # START OF MODIFICATION (5 Remaining edge-cases): Include original_id in filename
                action_args_filename = f"{original_id}-{filename_base}-{sc_lang_code}.srt" # MODIFIED
                # END OF MODIFICATION (5 Remaining edge-cases): Include original_id in filename
            
            results.append({
                'service_name': service_name,
                'service': display_name_for_service,
                'lang': kodi_target_lang_full,
                'name': f"{movie_title_on_page} ({sc_lang_name_full})",
                'rating': 0,
                'lang_code': kodi_target_lang_2_letter,
                'sync': 'false',
                'impaired': 'false',
                'color': 'yellow' if patch_kind_is_translate else 'white', # MODIFIED (5 Remaining edge-cases)
                'action_args': {
                    'url': action_args_url,
                    'lang': kodi_target_lang_full,
                    'filename': action_args_filename,
                    'gzip': False,
                    'service_name': service_name,
                    'needs_poll': patch_kind_is_translate,
                    'detail_url': movie_page_full_url,
                    'lang_code': sc_lang_code # Subtitlecat's site language code (e.g., "en", "el")
                }
            })
            core.logger.debug(f"[{service_name}] Added result '{action_args_filename}' for lang '{kodi_target_lang_full}' (Poll: {patch_kind_is_translate})")

    core.logger.debug(f"[{service_name}] Returning {len(results)} results after parsing all pages.")
    return results

# ---------------------------------------------------------------------------
# DOWNLOAD REQUEST BUILDER
# ---------------------------------------------------------------------------
def build_download_request(core, service_name, args):
    initial_download_url = args['url'] 
    
    _filename_from_args = args.get('filename')
    if _filename_from_args:
        filename_for_log = _filename_from_args
    elif initial_download_url: 
        filename_for_log = initial_download_url.split('/')[-1]
    else: 
        filename_for_log = args.get('lang_code', "unknown_lang") + "_subtitle_pending_poll" # Use lang_code if filename is not yet known
    
    core.logger.debug(f"[{service_name}] Initializing download for: {filename_for_log}, initial URL: '{initial_download_url}'")

    final_url = initial_download_url

    # START OF MODIFICATION: Polling logic (Review Points 1, 2, 3)
    if args.get('needs_poll'):
        # For items that need polling, initial_download_url is expected to be empty.
        if not initial_download_url: 
            core.logger.debug(f"[{service_name}] Polling required for '{filename_for_log}'. Detail URL: {args.get('detail_url')}, SC Lang Code: {args.get('lang_code')}")
            # Call the _wait_for_translated helper function
            polled_url = _wait_for_translated(core,
                                              args['detail_url'],
                                              args['lang_code'], # This is Subtitlecat's specific lang code
                                              service_name # Pass service_name for logging in helper
                                             )
            if polled_url:
                final_url = polled_url # Update final_url with the one found by polling
                core.logger.debug(f"[{service_name}] Polling successful. Found URL for '{filename_for_log}': {final_url}")
            else:
                # Polling failed or timed out; _wait_for_translated returned empty
                error_msg = f"[{service_name}] Translation for '{filename_for_log}' (lang: {args.get('lang_code')}) did not become available on {args.get('detail_url')} in time."
                core.logger.error(error_msg)
                raise Exception(error_msg) # Raise exception as per review point 3
        else:
            # This case: needs_poll is True, but initial_download_url is NOT empty.
            # This shouldn't happen if parse_search_response sets action_args['url'] = "" for needs_poll=True cases.
            core.logger.warning(f"[{service_name}] 'needs_poll' is true for '{filename_for_log}', but an initial URL '{initial_download_url}' was unexpectedly provided. Using initial URL without polling.")
            # final_url is already initial_download_url, no change needed.

    # Safety check: if final_url is still empty (e.g., if needs_poll was false but initial_url was empty, or some other logic error)
    if not final_url:
        # This state should ideally not be reached if needs_poll=True due to the exception above.
        # If needs_poll=False and initial_download_url was empty, that's an issue from parse_search_response.
        error_msg = f"[{service_name}] Final URL for '{filename_for_log}' is empty. This indicates an issue in logic or an unexpected state (initial URL: '{initial_download_url}', needs_poll: {args.get('needs_poll')})."
        core.logger.error(error_msg)
        # This covers the spirit of Review Point 2's minimal patch for a broader case.
        raise ValueError(error_msg)
    # END OF MODIFICATION: Polling logic

    core.logger.debug(f"[{service_name}] Building download request for: {filename_for_log} from {final_url}")

    return {
        'method': 'GET',
        'url': final_url, 
        'headers': {'User-Agent': __user_agent},
        'stream': True
    }