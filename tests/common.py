# -*- coding: utf-8 -*-

import sys
import os
import json
import re
import pytest
import time

dir_name = os.path.dirname(__file__)
main = os.path.join(dir_name, '..')
a4kSubtitles = os.path.join(main, '..', 'a4kSubtitles')
lib = os.path.join(a4kSubtitles, 'lib')
services = os.path.join(a4kSubtitles, 'services')

sys.path.append(dir_name)
sys.path.append(main)
sys.path.append(a4kSubtitles)
sys.path.append(lib)
sys.path.append(services)

from a4kSubtitles import api, service
from tests import utils
