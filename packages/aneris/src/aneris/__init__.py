# -*- coding: utf-8 -*-

import logging
from pkg_resources import get_distribution

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

# credentials
__authors__ = ['DTOcean Developers']
__version__ = get_distribution('aneris').version
