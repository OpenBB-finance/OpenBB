"""Decorators"""
__docformat__ = "numpy"
import functools
import logging

import gamestonk_terminal.config_terminal as cfg

logger = logging.getLogger(__name__)


def try_except(f):
    """Adds a try except block if the user is not in development mode

    Parameters
    ----------
    f: function
        The function to be wrapped
    """
    # pylint: disable=inconsistent-return-statements
    @functools.wraps(f)
    def inner(*args, **kwargs):
        if cfg.DEBUG_MODE:
            return f(*args, **kwargs)
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception("%s", type(e).__name__)
            return []

    return inner
