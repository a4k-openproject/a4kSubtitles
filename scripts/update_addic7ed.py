# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import requests
import traceback

try:
    response = requests.get('https://www.addic7ed.com', timeout=20)
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        sys.exit(0)
except:
    traceback.print_exc()
    sys.exit(0)

tvshow_options = []

try:
    response = response.text.split('[Select a TV Show]')[1]
    tvshow_options = re.findall(r'<option\s*?value="(.*?)"\s*?>(.*?)</option>', response)
except:
    traceback.print_exc()

if len(tvshow_options) == 0:
    sys.exit(0)

tvshows = {}
for option in tvshow_options:
    tvshows[option[1]] = option[0]

dirname = os.path.dirname(__file__)
filepath = os.path.join(dirname, '..', 'a4kSubtitles', 'data', 'addic7ed', 'tvshows.json')

with open(filepath, 'w') as f_out:
    json.dump(tvshows, f_out, indent=4)
