from io import StringIO
from pandas import DataFrame, read_csv
import urllib3
import ssl
from typing import Any
import requests
import sys
from openbb_provider import helpers

from typing import Optional, Dict

if sys.version_info >= (3, 10):
    PATCH = True
else:
    PATCH = False


# OECD does not play well with newer python.  This code block from stackoverflow helps
# to create a custom session:


class CustomHttpAdapter(requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )


def get_legacy_session():
    """Stackoverflow code to create a custom session."""
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.Session()
    session.mount("https://", CustomHttpAdapter(ctx))
    return session


def create_session():
    """Create a session for making requests to the OECD API.

    This will create the patched session if the python version is >= 3.10.  Otherwise,
    it will just use regular requests.
    """
    if PATCH:
        return get_legacy_session()
    return requests.Session()


def fetch_data(url: str, csv_kwargs: Optional[Dict] = None, **kwargs: Any) -> DataFrame:
    """Create a session and fetch data from the OECD API."""
    session = create_session()
    response = helpers.make_request(url, session=session, **kwargs)
    if csv_kwargs is None:
        csv_kwargs = {}
    # Pass any additional arguments to read_csv.  This will likely need to be skiplines
    # or a delimiter.
    data = read_csv(StringIO(response.text), **csv_kwargs)
    return data
