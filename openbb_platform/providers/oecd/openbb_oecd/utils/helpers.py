import ssl
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import urllib3
from defusedxml.ElementTree import fromstring
from openbb_core.app.utils import get_user_cache_directory
from openbb_core.provider import helpers
from pandas import DataFrame, read_csv, read_parquet

cache = get_user_cache_directory() + "/oecd"
# Create the cache directory if it does not exist
Path(cache).mkdir(parents=True, exist_ok=True)

# OECD does not play well with newer python.  This code block from stackoverflow helps
# to create a custom session:


class CustomHttpAdapter(requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    # pylint: disable=arguments-differ
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(  # pylint: disable=attribute-defined-outside-init
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )


# pylint: enable=arguments-differ


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


### The functions below are for using the new oecd data-explorer instead of the stats.oecd


def oecd_xml_to_df(xml_string: str) -> DataFrame:
    """Helper function to parse the OECD XML and return a dataframe.

     Parameters
    ----------
    xml_string : str
        A string containing the OECD XML data.

    Returns
    -------
    DataFrame
        A Pandas DataFrame containing the parsed data from the XML string.
    """
    root = fromstring(xml_string)

    namespaces = {
        "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
        "generic": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic",
    }

    # Prepare a list to hold your extracted data
    data = []

    # Iterate through each 'Series' in the XML
    for series in root.findall(".//generic:Series", namespaces=namespaces):
        series_data = {}
        # Extract series key values
        for value in series.findall(".//generic:Value", namespaces=namespaces):
            series_data[value.get("id")] = value.get("value")
        # Extract observation values
        for obs in series.findall("./generic:Obs", namespaces=namespaces):
            obs_data = series_data.copy()
            obs_data["TIME_PERIOD"] = obs.find(
                "./generic:ObsDimension", namespaces=namespaces
            ).get("value")
            obs_data["VALUE"] = obs.find(
                "./generic:ObsValue", namespaces=namespaces
            ).get("value")
            data.append(obs_data)

    # Create a DataFrame
    return DataFrame(data)


def parse_url(url: str) -> DataFrame:
    """Helper function to parse the SDMX url and return a dataframe.

    Parameters
    ----------
    url:str
        URL to parse

    Returns
    -------
    DataFrame
        Pandas dataframe containing URL data
    """
    response = helpers.make_request(url)
    response.raise_for_status()
    return oecd_xml_to_df(response.text)


def check_cache_exists_and_valid(function: str, cache_method: str = "csv") -> bool:
    """Check if the cache exists and is valid.

    Parameters
    ----------
    function : str
        The name of the function for which the cache is being checked.
    cache_method : str, optional
        The method used for caching (default is 'csv').

    Returns
    -------
    bool
        True if the cache exists and is valid for the current day, False otherwise.
    """
    # TODO: add setting to disable cache for tests

    if cache_method not in ["csv", "parquet"]:
        raise NotImplementedError("Currently only working with parquet or csv")
    # First check that the cache exists.  This will be a parquet/csv and a timestamp
    cache_path = f"{cache}/{function}.{cache_method}"
    time_cache_path = f"{cache}/{function}.timestamp"
    if Path(cache_path).exists() and Path(time_cache_path).exists():
        # Now check that the cache is valid.  I am going to check that we write to a file the date the cache was made
        # Read the timestamp
        with open(time_cache_path) as f:
            cached_date = f.read().strip()
        # TODO:  More robust caching logic
        if cached_date == str(date.today()):
            return True
        return False
    return False


def write_to_cache(function: str, data: DataFrame, cache_method: str) -> None:
    """Write data to the cache.

    Parameters
    ----------
    function : str
        The name of the function for which data is being cached.
    data : DataFrame
        The DataFrame to be cached.
    cache_method : str
        The method used for caching the data.

    Raises
    ------
    NotImplementedError
        If the cache_method is not 'parquet'.
    """
    if cache_method == "parquet":
        cache_path = f"{cache}/{function}.parquet"
        data.to_parquet(cache_path, engine="pyarrow")
        # Write the current date to a file called cache/function.timestamp
        with open(f"{cache}/{function}.timestamp", "w") as f:
            f.write(str(date.today()))
    elif cache_method == "csv":
        cache_path = f"{cache}/{function}.csv"
        data.to_csv(cache_path)
        # Write the current date to a file called cache/function.timestamp
        with open(f"{cache}/{function}.timestamp", "w") as f:
            f.write(str(date.today()))
    else:
        raise NotImplementedError


def get_possibly_cached_data(
    url: str, function: Optional[str] = None, cache_method: str = "csv"
) -> DataFrame:
    """
    Retrieve data from a given URL or from the cache if available and valid.

    Parameters
    ----------
    url : str
        The URL from which to fetch the data if it's not available in the cache.
    function : Optional[str], optional
        The name of the function for which data is being fetched or cached.
    cache_method : str, optional
        The method used for caching the data (default is 'csv').

    Returns
    -------
    DataFrame
        A Pandas DataFrame containing the fetched or cached data.
    """
    if cache_method == "parquet":
        cache_path = f"{cache}/{function}.parquet"
    elif cache_method == "csv":
        cache_path = f"{cache}/{function}.csv"

    use_cache = check_cache_exists_and_valid(
        function=function, cache_method=cache_method
    )
    if use_cache:
        if cache_method == "csv":
            data = read_csv(cache_path)
        elif cache_method == "parquet":
            data = read_parquet(cache_path, engine="pyarrow")
    else:
        data = parse_url(url)
        write_to_cache(function=function, data=data, cache_method=cache_method)
    return data
