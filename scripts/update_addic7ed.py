# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import requests

try:
    response = requests.get('https://www.addic7ed.com', timeout=20)
    if response.status_code != 200:
        sys.exit(0)
except:
    sys.exit(0)

response = response.text.split('[Select a TV Show]')[1]
tvshow_options = re.findall(r'<option\s*?value="(.*?)"\s*?>(.*?)</option>', response)

tvshows = {}
for option in tvshow_options:
    tvshows[option[1]] = option[0]

dirname = os.path.dirname(__file__)
filepath = os.path.join(dirname, '..', 'a4kSubtitles', 'data', 'addic7ed', 'tvshows.json')

with open(filepath, 'w') as f_out:
    json.dump(tvshows, f_out, indent=4)
