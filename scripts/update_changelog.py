# -*- coding: utf-8 -*-

import os
import re
from xml.etree import ElementTree

current_dir = os.path.dirname(__file__)
addon_xml_path = os.path.join(current_dir, '..', 'addon.xml')
changelog_path = os.path.join(current_dir, '..', 'CHANGELOG.md')

tree = ElementTree.parse(addon_xml_path)
root = tree.getroot()
news = root.find('./extension/news')
changelog = news.text.strip() + '\n'

tag_prefix = 'https://github.com/newt-sc/a4kSubtitles/releases/tag/service.subtitles.a4ksubtitles%2Fservice.subtitles.a4ksubtitles'
changelog = re.sub(r'\[v(.*?)\]:', lambda m: '* [v%s](%s-%s):' % (m.group(1), tag_prefix, m.group(1)), changelog)

with open(changelog_path, 'w') as f:
  f.write(changelog)
