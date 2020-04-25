# -*- coding: utf-8 -*-

import importlib
from a4kSubtitles.lib import utils

__all__ = utils.get_all_relative_py_files(__file__)

def __set_fn_if_missing(service, fn_name, fn):
    if not getattr(service, fn_name, None):
        setattr(service, fn_name, fn)

services = {}
for service_name in __all__:
    service = services[service_name] = importlib.import_module('a4kSubtitles.services.%s' % service_name)

    context = lambda: None

    class Context:
        def __getattr__(self, name):
            return getattr(context, name, None)

        def __setattr__(self, name, value):
            return setattr(context, name, value)

    service.context = Context()

    __set_fn_if_missing(service, 'build_auth_request', lambda _, __: None)

    assert service.build_search_requests
    assert service.parse_search_response
    assert service.build_download_request
