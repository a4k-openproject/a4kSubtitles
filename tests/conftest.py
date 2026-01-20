# -*- coding: utf-8 -*-

import pytest
import logging

def pytest_configure(config):
    """Configure logging to reduce verbosity during tests."""
    # Suppress verbose HTTP connection logs from urllib3
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    # Only show warnings and errors by default for third-party libraries
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)


@pytest.fixture(autouse=True)
def suppress_test_warnings():
    """Suppress common deprecation warnings during tests."""
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='ssl.OP_NO_SSL')
        warnings.filterwarnings('ignore', message='ssl.OP_NO_TLS')
        yield
