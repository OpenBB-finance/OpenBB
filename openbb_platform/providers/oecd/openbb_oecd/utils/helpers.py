import ssl
from io import StringIO
from typing import Any, Dict, Optional

import requests
import urllib3
from openbb_core.provider import helpers
from pandas import DataFrame, read_csv

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


def fetch_data(url: str, csv_kwargs: Optional[Dict] = None, **kwargs: Any) -> DataFrame:
    """Create a session and fetch data from the OECD API."""
    session = get_legacy_session()
    response = helpers.make_request(url, session=session, **kwargs)
    if csv_kwargs is None:
        csv_kwargs = {}
    # Pass any additional arguments to read_csv.  This will likely need to be skiplines
    # or a delimiter.
    data = read_csv(StringIO(response.text), **csv_kwargs)
    return data
