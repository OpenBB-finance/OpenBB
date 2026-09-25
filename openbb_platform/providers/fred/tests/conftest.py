"""Shared fixtures for the FRED provider tests."""

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def fred_cache(tmp_path_factory):
    """Give the run its own FRED response cache, and empty it at the end."""
    from openbb_fred.utils import cache
    from openbb_fred.utils.rate_limiter import cache_clear

    directory = tmp_path_factory.mktemp("fred-cache")
    previous = os.environ.get("OPENBB_FRED_DISK_CACHE_DIR")
    os.environ["OPENBB_FRED_DISK_CACHE_DIR"] = str(directory)
    cache.close()
    cache_clear()

    yield cache

    cache.clear()
    cache.close()
    cache_clear()

    if previous is None:
        os.environ.pop("OPENBB_FRED_DISK_CACHE_DIR", None)
    else:
        os.environ["OPENBB_FRED_DISK_CACHE_DIR"] = previous
