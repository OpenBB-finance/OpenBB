"""SEC Frames Utilities."""

# pylint: disable=line-too-long

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Union
from warnings import warn

from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.utils import get_user_cache_directory
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_sec.utils.definitions import (
    FISCAL_PERIODS,
    FISCAL_PERIODS_DICT,
    HEADERS,
    SHARES_FACTS,
    TAXONOMIES,
    USD_PER_SHARE_FACTS,
)
from openbb_sec.utils.helpers import get_all_companies, symbol_map
from pandas import DataFrame


async def fetch_data(url, use_cache, persist) -> Union[Dict, List[Dict]]:
    """Fetch the data from the constructed URL."""
    response: Union[Dict, List[Dict]] = {}
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_frames"
        async with CachedSession(
            cache=(
                SQLiteBackend(cache_dir, expire_after=3600 * 24)
                if persist is False
                else SQLiteBackend(cache_dir)
            )
        ) as session:
            try:
                response = await amake_request(url, headers=HEADERS, session=session)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, headers=HEADERS)  # type: ignore
    return response


async def get_frame(  # pylint: disable =too-many-arguments,too-many-locals, too-many-statements
    fact: str = "Revenues",
    year: Optional[int] = None,
    fiscal_period: Optional[FISCAL_PERIODS] = None,
    taxonomy: Optional[TAXONOMIES] = "us-gaap",
    units: Optional[str] = "USD",
    instantaneous: bool = False,
    use_cache: bool = True,
) -> Dict:
    """Get a frame of data for a given fact.

    Source: https://www.sec.gov/edgar/sec-api-documentation

    The xbrl/frames API aggregates one fact for each reporting entity
    that is last filed that most closely fits the calendrical period requested.

    This API supports for annual, quarterly and instantaneous data:

    https://data.sec.gov/api/xbrl/frames/us-gaap/AccountsPayableCurrent/USD/CY2019Q1I.json

    Where the units of measure specified in the XBRL contains a numerator and a denominator,
    these are separated by “-per-” such as “USD-per-shares”. Note that the default unit in XBRL is “pure”.

    The period format is CY#### for annual data (duration 365 days +/- 30 days),
    CY####Q# for quarterly data (duration 91 days +/- 30 days).

    Because company financial calendars can start and end on any month or day and even change in length from quarter to
    quarter according to the day of the week, the frame data is assembled by the dates that best align with a calendar
    quarter or year. Data users should be mindful different reporting start and end dates for facts contained in a frame.

    Parameters
    ----------
    fact : str
        The fact to retrieve. This should be a valid fact from the SEC taxonomy, in UpperCamelCase.
        Defaults to "Revenues".
        AAPL, MSFT, GOOG, BRK-A all report revenue as, "RevenueFromContractWithCustomerExcludingAssessedTax".
        In previous years, they may have reported as "Revenues".
    year : int, optional
        The year to retrieve the data for. If not provided, the current year is used.
    fiscal_period: Literal["fy", "q1", "q2", "q3", "q4"], optional
        The fiscal period to retrieve the data for. If not provided, the most recent quarter is used.
    taxonomy : Literal["us-gaap", "dei", "ifrs-full", "srt"], optional
        The taxonomy to use. Defaults to "us-gaap".
    units : str, optional
        The units to use. Defaults to "USD". This should be a valid unit from the SEC taxonomy, see the notes above.
        The most common units are "USD", "shares", and "USD-per-shares". EPS and outstanding shares facts will
        automatically set.
    instantaneous: bool
        Whether to retrieve instantaneous data. See the notes above for more information. Defaults to False.
        Some facts are only available as instantaneous data.
        The function will automatically attempt to retrieve the data if the initial fiscal quarter request fails.
    use_cache: bool
        Whether to use cache for the request. Defaults to True.

    Returns
    -------
    Dict:
        Nested dictionary with keys, "metadata" and "data".
        The "metadata" key contains information about the frame.
    """
    current_date = datetime.now().date()
    quarter = FISCAL_PERIODS_DICT.get(fiscal_period) if fiscal_period else None
    if year is None and quarter is None:
        quarter = (current_date.month - 1) // 3
        year = current_date.year

    if year is None:
        year = current_date.year

    persist = current_date.year == year

    if fact in SHARES_FACTS:
        units = "shares"

    if fact in USD_PER_SHARE_FACTS:
        units = "USD-per-shares"

    url = f"https://data.sec.gov/api/xbrl/frames/{taxonomy}/{fact}/{units}/CY{year}"

    if quarter:
        url = url + f"Q{quarter}"

    if instantaneous:
        url = url + "I"

    url = url + ".json"
    response: Union[Dict, List[Dict]] = {}
    try:
        response = await fetch_data(url, use_cache, persist)
    except Exception as e:  # pylint: disable=W0718
        message = (
            "No frame was found with the combination of parameters supplied."
            + " Try adjusting the period."
            + " Not all GAAP measures have frames available."
        )
        if url.endswith("I.json"):
            warn("No instantaneous frame was found, trying calendar period data.")
            url = url.replace("I.json", ".json")
            try:
                response = await fetch_data(url, use_cache, persist)
            except Exception:
                raise OpenBBError(message) from e
        elif "Q" in url and not url.endswith("I.json"):
            warn(
                "No frame was found for the requested quarter, trying instantaneous data."
            )
            url = url.replace(".json", "I.json")
            try:
                response = await fetch_data(url, use_cache, persist)
            except Exception:
                raise OpenBBError(message) from e
        else:
            raise OpenBBError(message) from e

    data = sorted(response.get("data", {}), key=lambda x: x["val"], reverse=True)  # type: ignore
    metadata = {
        "frame": response.get("ccp", ""),  # type: ignore
        "tag": response.get("tag", ""),  # type: ignore
        "label": response.get("label", ""),  # type: ignore
        "description": response.get("description", ""),  # type: ignore
        "taxonomy": response.get("taxonomy", ""),  # type: ignore
        "unit": response.get("uom", ""),  # type: ignore
        "count": response.get("pts", ""),  # type: ignore
    }
    df = DataFrame(data)
    companies = await get_all_companies(use_cache=use_cache)
    cik_to_symbol = companies.set_index("cik")["symbol"].to_dict()
    df["symbol"] = df["cik"].astype(str).map(cik_to_symbol)
    df["unit"] = metadata.get("unit")
    df["fact"] = metadata.get("label")
    df["frame"] = metadata.get("frame")
    df = df.fillna("N/A").replace("N/A", None)
    results = {"metadata": metadata, "data": df.to_dict("records")}

    return results


async def get_concept(
    symbol: str,
    fact: str = "Revenues",
    year: Optional[int] = None,
    taxonomy: Optional[TAXONOMIES] = "us-gaap",
    use_cache: bool = True,
) -> Dict:
    """Return all the XBRL disclosures from a single company (CIK) Concept (a taxonomy and tag) into a single JSON file.

    Each entry contains a separate array of facts for each units of measure that the company has chosen to disclose
    (e.g. net profits reported in U.S. dollars and in Canadian dollars).

    Parameters
    ----------
    symbol: str
        The ticker symbol to look up.
    fact : str
        The fact to retrieve. This should be a valid fact from the SEC taxonomy, in UpperCamelCase.
        Defaults to "Revenues".
        AAPL, MSFT, GOOG, BRK-A all report revenue as, "RevenueFromContractWithCustomerExcludingAssessedTax".
        In previous years, they may have reported as "Revenues".
    year : int, optional
        The year to retrieve the data for. If not provided, all reported values will be returned.
    taxonomy : Literal["us-gaap", "dei", "ifrs-full", "srt"], optional
        The taxonomy to use. Defaults to "us-gaap".
    use_cache: bool
        Whether to use cache for the request. Defaults to True.

    Returns
    -------
    Dict:
        Nested dictionary with keys, "metadata" and "data".
        The "metadata" key contains information about the company concept.
    """
    symbols = symbol.split(",")
    results: List[Dict] = []
    messages: List = []
    metadata: Dict = {}

    async def get_one(ticker):
        """Get data for one symbol."""
        ticker = ticker.upper()
        message = f"Symbol Error: No data was found for, {ticker} and {fact}"
        cik = await symbol_map(ticker)
        if cik == "":
            message = f"Symbol Error: No CIK was found for, {ticker}"
            warn(message)
            messages.append(message)
        else:
            url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{fact}.json"
            response: Union[Dict, List[Dict]] = {}
            try:
                response = await fetch_data(url, use_cache, False)
            except Exception as _:  # pylint: disable=W0718
                warn(message)
                messages.append(message)
            if response:
                units = response.get("units", {})  # type: ignore
                metadata[ticker] = {
                    "cik": response.get("cik", ""),  # type: ignore
                    "taxonomy": response.get("taxonomy", ""),  # type: ignore
                    "tag": response.get("tag", ""),  # type: ignore
                    "label": response.get("label", ""),  # type: ignore
                    "description": response.get("description", ""),  # type: ignore
                    "name": response.get("entityName", ""),  # type: ignore
                    "units": (
                        list(units) if units and len(units) > 1 else list(units)[0]
                    ),
                }
                for k, v in units.items():
                    unit = k
                    values = v
                    for item in values:
                        item["unit"] = unit
                        item["symbol"] = ticker
                        item["cik"] = metadata[ticker]["cik"]
                        item["name"] = metadata[ticker]["name"]
                        item["fact"] = metadata[ticker]["label"]
                    results.extend(values)

    await asyncio.gather(*[get_one(ticker) for ticker in symbols])

    if not results:
        raise EmptyDataError(f"{messages}")

    if year is not None:
        filtered_results = [d for d in results if str(year) == str(d.get("fy"))]
        if len(filtered_results) > 0:
            results = filtered_results
        if len(filtered_results) == 0:
            warn(
                f"No results were found for {fact} in the year, {year}."
                " Returning all entries instead. Concept and fact names may differ by company and year."
            )

    return {
        "metadata": metadata,
        "data": sorted(results, key=lambda x: (x["filed"], x["end"]), reverse=True),
    }
