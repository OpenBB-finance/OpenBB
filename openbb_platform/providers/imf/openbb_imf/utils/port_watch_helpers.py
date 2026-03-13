"""IMF Port Watch helpers."""

# pylint: disable=R0914

from typing import Any

from async_lru import alru_cache
from openbb_imf.utils.constants import (
    CHOKEPOINTS_BASE_URL,
    DAILY_TRADE_BASE_URL,
)


def list_countries() -> list[dict[str, str]]:
    """List available countries for IMF Port Watch.

    Returns
    -------
    list of dict
        A list of dictionaries with 'label' and 'value' for each country.
    """
    choices: list = []
    ports = get_ports()
    seen: set = set()

    for port in ports:
        if port["ISO3"] in seen:
            continue

        seen.add(port["ISO3"])
        choices.append(
            {
                "label": port["countrynoaccents"],
                "value": port["ISO3"],
            }
        )
    return choices


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
    cc = country_code.upper()
    countries = list_countries()
    code_to_country = {country["value"]: country["label"] for country in countries}
    if cc not in code_to_country:
        raise ValueError("Country code is not supported by IMF Port Watch.")

    return code_to_country.get(cc, cc)


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
    ports = get_ports()
    ports_ids: list = []
    for port in ports:
        if port["ISO3"] == country_code.upper():
            ports_ids.append(port["portid"])

    return ",".join(ports_ids)


def get_port_id_choices() -> list:
    """Get choices for selecting individual ports by ID.

    Returns
    -------
    list
        A list of dictionaries, with labels and values for each port ID.
    """
    choices: list = []
    ports = get_ports()

    for port in ports:
        choices.append(
            {
                "label": port["portname"],
                "value": port["portid"],
            }
        )
    return choices


@alru_cache(maxsize=25)
async def get_daily_chokepoint_data(
    chokepoint_id, start_date: str | None = None, end_date: str | None = None
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
    start_date: str | None = None, end_date: str | None = None
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
    port_id, start_date: str | None = None, end_date: str | None = None
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


@alru_cache(maxsize=1)
async def list_ports() -> list[dict[str, Any]]:
    """List all available ports from the IMF Port Watch dataset.

    Returns
    -------
    list[dict]
        A list of dictionaries, each representing a port with its details.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import get_async_requests_session

    url = (
        "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/PortWatch_ports_database/"
        + "FeatureServer/0/query?where=1%3D1&outFields=countrynoaccents,portid,lon,lat,portname,ISO3,continent,fullname"
        + "+&returnGeometry=false&orderByFields=vessel_count_total%20DESC&outSR=&f=json"
    )
    ports: list[dict] = []

    try:
        async with await get_async_requests_session() as session, await session.get(
            url
        ) as response:
            if response.status != 200:
                raise OpenBBError(
                    f"Failed to fetch ports data: {response.status} - {response.reason}"
                )
            data = await response.json()

            for feature in data.get("features", []):
                ports.append(feature.get("attributes", {}))

        return ports

    except Exception as e:
        raise OpenBBError(f"Error fetching ports data: {e} -> {e.args}") from e


def get_ports() -> list[dict[str, Any]]:
    """Get the list of all ports synchronously."""
    # pylint: disable=import-outside-toplevel
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        # Already in an async context
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, list_ports())
            ports = future.result()
    else:
        ports = asyncio.run(list_ports())

    return ports
