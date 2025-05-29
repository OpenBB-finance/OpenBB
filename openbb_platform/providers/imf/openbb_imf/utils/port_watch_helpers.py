"""IMF Port Watch helpers."""

from typing import Optional

from async_lru import alru_cache
from openbb_imf.utils.constants import (
    CHOKEPOINTS_BASE_URL,
    DAILY_TRADE_BASE_URL,
    PORT_COUNTRIES,
)


def map_port_country_code(country_code: str) -> str:
    """Map the 3-letter country code to the full country name.

    Parameters
    ----------
    country_code : str
        The 3-letter ISO country code (e.g., "USA" for the United States).

    Returns
    -------
    str
        The full country name, without accents, corresponding to the provided country code.
    """
    COUNTRY_CODE_TO_PORT = {v: k for k, v in PORT_COUNTRIES.items()}
    if country_code not in COUNTRY_CODE_TO_PORT:
        raise ValueError("Country code is not supported by IMF Port Watch.")

    return COUNTRY_CODE_TO_PORT.get(country_code.upper(), country_code.upper())


def get_port_ids_by_country(country_code: str) -> str:
    """Get all port IDs for a specific country. The country code should be a 3-letter ISO code.

    Parameters
    ----------
    country_code : str
        The 3-letter ISO country code (e.g., "USA" for the United States).

    Returns
    -------
    str
        A list of port IDs as a comma-separated string.
    """
    # pylint: disable=import-outside-toplevel
    import importlib.resources
    import json

    json_path = (
        importlib.resources.files("openbb_imf") / "assets" / "imf_ports_by_country.json"
    )

    if not json_path.exists():  # type: ignore
        raise FileNotFoundError(f"Port IDs JSON file not found at {json_path}")

    port_ids_by_country: dict = {}

    with open(str(json_path), encoding="utf-8") as file:
        port_ids_by_country = json.load(file)

    if country_code.upper() not in port_ids_by_country:
        raise ValueError(
            f"Country code '{country_code}' is not supported by IMF Port Watch."
        )

    return port_ids_by_country.get(country_code.upper(), "")


def get_port_id_choices() -> list:
    """Get choices for selecting individual ports by ID.

    Returns
    -------
    list
        A list of dictionaries, with labels and values for each port ID.
    """
    # pylint: disable=import-outside-toplevel
    import json  # noqa
    import importlib.resources

    json_path = (
        importlib.resources.files("openbb_imf") / "assets" / "imf_portid_map.json"
    )

    if not json_path.exists():  # type: ignore
        raise FileNotFoundError(f"imf_portid_map.json not found at: {json_path}")

    choices: list = []
    portids: dict = {}

    with open(str(json_path), encoding="utf-8") as file:
        portids = json.load(file)

    for portid, portname in portids.items():
        choices.append(
            {
                "label": portname,
                "value": portid,
            }
        )

    return choices


@alru_cache(maxsize=25)
async def get_daily_chokepoint_data(
    chokepoint_id, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> list:
    """Get the daily chokepoint data for a specific chokepoint and date range.

    Parameters
    ----------
    chokepoint_id : str
        The ID of the chokepoint (e.g., "chokepoint1"). 1-24 are valid IDs
    """
    # pylint: disable=import-outside-toplevel
    from datetime import datetime  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import get_async_requests_session

    if start_date is not None and end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if start_date is None and end_date is not None:
        start_date = "2019-01-01"

    def get_chokepoints_url(offset: int):
        """Construct the URL for fetching chokepoint data with offset."""
        nonlocal chokepoint_id
        return (
            (
                CHOKEPOINTS_BASE_URL
                + f"where=portid%20%3D%20%27{chokepoint_id.upper()}%27"
                + f"AND%20date%20>%3D%20TIMESTAMP%20%27{start_date}%2000%3A00%3A00%27"
                + f"%20AND%20date%20<%3D%20TIMESTAMP%20%27{end_date}%2000%3A00%3A00%27&"
                + f"outFields=*&orderByFields=date&returnZ=true&resultOffset={offset}&resultRecordCount=1000"
                + "&maxRecordCountFactor=5&outSR=&f=json"
            )
            if start_date is not None and end_date is not None
            else (
                CHOKEPOINTS_BASE_URL
                + f"where=portid%20%3D%20%27{chokepoint_id.upper()}%27&"
                + f"outFields=*&orderByFields=date&returnZ=true&resultOffset={offset}&resultRecordCount=1000"
                + "&maxRecordCountFactor=5&outSR=&f=json"
            )
        )

    offset: int = 0
    output: dict = {}
    url = get_chokepoints_url(offset)

    async with await get_async_requests_session() as session:
        async with await session.get(url) as response:
            data: dict = {}

            if response.status != 200:
                raise OpenBBError(f"Failed to fetch data: {response.status}")
            data = await response.json()

        if "features" in data:
            output = data.copy()

        while data.get("exceededTransferLimit") is True:
            offset += len(data["features"])
            url = get_chokepoints_url(offset)

            async with await session.get(url) as response:
                data = {}
                if response.status != 200:
                    raise OpenBBError(f"Failed to fetch data: {response.status}")
                data = await response.json()

            if "features" in data:
                output["features"].extend(data["features"])

        final_output: list = []

        for feature in output["features"]:
            date = datetime(
                feature["attributes"]["year"],
                feature["attributes"]["month"],
                feature["attributes"]["day"],
            ).strftime("%Y-%m-%d")
            final_output.append(
                {
                    "date": date,
                    **{
                        k: v
                        for k, v in feature["attributes"].items()
                        if k not in ["year", "month", "day", "date", "ObjectId"]
                    },
                }
            )

    return final_output


@alru_cache(maxsize=1)
async def get_all_daily_chokepoint_activity_data(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> list:
    """Get the complete historical volume dataset for all chokepoints."""
    # pylint: disable=import-outside-toplevel
    import asyncio  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError

    chokepoints = [f"chokepoint{i}" for i in range(1, 25)]
    chokepoints_data: list = []

    async def _get_one_chokepoint_data(chokepoint_id):
        """Get the daily chokepoint data for a specific chokepoint."""
        try:
            data = await get_daily_chokepoint_data(chokepoint_id, start_date, end_date)
            chokepoints_data.extend(data)
        except Exception as e:
            raise OpenBBError(f"Failed to fetch data for {chokepoint_id}: {e}") from e

    try:
        gather_results = await asyncio.gather(
            *[_get_one_chokepoint_data(cp) for cp in chokepoints],
            return_exceptions=True,
        )

        for result in gather_results:
            if isinstance(result, (OpenBBError, Exception)):
                raise result

        if not chokepoints_data:
            raise OpenBBError("All requests were returned empty.")

        return chokepoints_data

    except Exception as e:
        raise OpenBBError(
            f"Error in fetching chokepoint data: {e} -> {e.args[0]}"
        ) from e


@alru_cache(maxsize=1)
async def get_all_daily_port_activity_data() -> list:
    """Get all port activity data as a bulk download CSV.

    This function fetches a large file containing daily global port activity.
    Expect the file to be around 800 MB in size.

    Returns
    -------
    list
        A list of dictionaries, each representing a row of port activity data.
    """
    # pylint: disable=import-outside-toplevel
    from io import StringIO  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import get_async_requests_session
    from pandas import read_csv, to_datetime

    url = (
        "https://hub.arcgis.com/api/v3/datasets/959214444157458aad969389b3ebe1a0_0/"
        + "downloads/data?format=csv&spatialRefId=4326&where=1%3D1"
    )
    content = ""
    try:
        async with await get_async_requests_session(
            timeout=120
        ) as session, await session.get(url) as response:
            if response.status != 200:
                raise OpenBBError(
                    f"Failed to fetch port activity data: {response.status} - {response.reason}"
                )
            if response.content is None:
                raise OpenBBError("No content returned from the request.")
            content = await response.text()

        df = read_csv(StringIO(content))
        df.date = to_datetime(df.date).dt.date
        df = df.drop(
            columns=[
                d
                for d in ["ObjectId", "GlobalID", "year", "month", "day"]
                if d in df.columns
            ]
        )

        return df.to_dict(orient="records")

    except Exception as e:
        raise OpenBBError(f"Error fetching port activity data: {e} -> {e.args}") from e


@alru_cache(maxsize=125)
async def get_daily_port_activity_data(
    port_id, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> list:
    """Get the daily port activity data for a specific port ID.

    Parameters
    ----------
    port_id : str
        The port ID for which to fetch daily activity data.

    Returns
    -------
    list
        A list of dictionaries, each representing daily activity data for the specified port.
    """
    # pylint: disable=import-outside-toplevel
    from datetime import datetime  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import get_async_requests_session

    if port_id is None:
        raise OpenBBError(
            ValueError("Either port_id or country_code must be provided.")
        )

    if start_date is not None and end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if start_date is None and end_date is not None:
        start_date = "2019-01-01"

    def get_port_url(offset: int):
        """Construct the URL for fetching chokepoint data with offset."""
        nonlocal port_id, start_date, end_date
        return (
            (
                DAILY_TRADE_BASE_URL
                + f"where=portid%20%3D%20%27{port_id.upper()}%27&"  # type: ignore
                + f"outFields=*&orderByFields=date&returnZ=true&resultOffset={offset}&resultRecordCount=1000"
                + "&maxRecordCountFactor=5&outSR=&f=json"
            )
            if start_date is None and end_date is None
            else (
                DAILY_TRADE_BASE_URL
                + f"where=portid%20%3D%20%27{port_id.upper()}%27%20"
                + f"AND%20date%20>%3D%20TIMESTAMP%20%27{start_date}%2000%3A00%3A00%27"
                + f"%20AND%20date%20<%3D%20TIMESTAMP%20%27{end_date}%2000%3A00%3A00%27&"
                + f"outFields=*&orderByFields=date&returnZ=true&resultOffset={offset}&resultRecordCount=1000"
                + "&maxRecordCountFactor=5&outSR=&f=json"
            )
        )

    offset: int = 0
    output: dict = {}
    url = get_port_url(offset)

    async with await get_async_requests_session() as session:
        async with await session.get(url) as response:
            data = {}

            if response.status != 200:
                raise OpenBBError(f"Failed to fetch data: {response.status}")
            data = await response.json()

        if "features" in data:
            output = data.copy()

        while data.get("exceededTransferLimit") is True:
            offset += len(data["features"])
            url = get_port_url(offset)

            async with await session.get(url) as response:
                data = {}
                if response.status != 200:
                    raise OpenBBError(f"Failed to fetch data: {response.status}")
                data = await response.json()

            if "features" in data:
                output["features"].extend(data["features"])

        final_output: list = []

        for feature in output["features"]:
            date = datetime(
                feature["attributes"]["year"],
                feature["attributes"]["month"],
                feature["attributes"]["day"],
            ).strftime("%Y-%m-%d")
            final_output.append(
                {
                    "date": date,
                    **{
                        k: v
                        for k, v in feature["attributes"].items()
                        if k not in ["year", "month", "day", "date", "ObjectId"]
                    },
                }
            )

    return final_output
