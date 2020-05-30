# -*- coding: utf-8 -*-

import os
import importlib
from a4kSubtitles import api, service

if __name__ == '__main__':
    service.start(api.A4kSubtitlesApi())
