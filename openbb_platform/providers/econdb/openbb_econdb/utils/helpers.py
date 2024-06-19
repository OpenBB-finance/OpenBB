"""EconDB Helpers."""

import asyncio
import json
from importlib.resources import files
from io import StringIO
from typing import Dict, List, Optional, Tuple, Union

from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.utils import get_user_cache_directory
from openbb_core.provider.utils.helpers import amake_request, amake_requests
from pandas import DataFrame, concat, read_csv

COUNTRY_MAP = {
    "albania": "AL",
    "argentina": "AR",
    "australia": "AU",
    "austria": "AT",
    "azerbaijan": "AZ",
    "bangladesh": "BD",
    "belarus": "BY",
    "belgium": "BE",
    "bosnia_and_herzegovina": "BA",
    "brazil": "BR",
    "bulgaria": "BG",
    "cambodia": "KH",
    "canada": "CA",
    "chile": "CL",
    "china": "CN",
    "colombia": "CO",
    "costa rica": "CR",
    "croatia": "HR",
    "cyprus": "CY",
    "czechia": "CZ",
    "denmark": "DK",
    "dominican republic": "DO",
    "egypt": "EG",
    "estonia": "EE",
    "european_union": "EU",
    "euro_area": "EA",
    "finland": "FI",
    "france": "FR",
    "germany": "DE",
    "greece": "GR",
    "honduras": "HN",
    "hong_kong": "HK",
    "hungary": "HU",
    "india": "IN",
    "indonesia": "ID",
    "iran": "IR",
    "ireland": "IE",
    "israel": "IL",
    "italy": "IT",
    "japan": "JP",
    "jordan": "JO",
    "kazakhstan": "KZ",
    "laos": "LA",
    "latvia": "LV",
    "lithuania": "LT",
    "luxembourg": "LU",
    "macao": "MO",
    "malaysia": "MY",
    "mexico": "MX",
    "mongolia": "MN",
    "morocco": "MA",
    "netherlands": "NL",
    "new_zealand": "NZ",
    "nigeria": "NG",
    "norway": "NO",
    "oman": "OM",
    "pakistan": "PK",
    "panama": "PA",
    "peru": "PE",
    "philippines": "PH",
    "poland": "PL",
    "portugal": "PT",
    "romania": "RO",
    "russia": "RU",
    "saudi_arabia": "SA",
    "serbia": "RS",
    "singapore": "SG",
    "slovakia": "SK",
    "slovenia": "SI",
    "south_africa": "ZA",
    "south_korea": "KR",
    "spain": "ES",
    "sweden": "SE",
    "switzerland": "CH",
    "taiwan": "TW",
    "thailand": "TH",
    "tunisia": "TN",
    "turkey": "TR",
    "ukraine": "UA",
    "united_arab_emirates": "AE",
    "united_kingdom": "UK",
    "united_states": "US",
    "uzbekistan": "UZ",
    "vietnam": "VN",
    "world": "W00",
}

THREE_LETTER_ISO_MAP = {
    "ALB": "AL",
    "ARG": "AR",
    "AUS": "AU",
    "AUT": "AT",
    "AZE": "AZ",
    "BGD": "BD",
    "BLR": "BY",
    "BEL": "BE",
    "BIH": "BA",
    "BRA": "BR",
    "BGR": "BG",
    "KHM": "KH",
    "CAN": "CA",
    "CHL": "CL",
    "CHN": "CN",
    "COL": "CO",
    "CRI": "CR",
    "HRV": "HR",
    "CYP": "CY",
    "CZE": "CZ",
    "DNK": "DK",
    "DOM": "DO",
    "EGY": "EG",
    "EST": "EE",
    "FIN": "FI",
    "FRA": "FR",
    "DEU": "DE",
    "GRC": "GR",
    "HND": "HN",
    "HKG": "HK",
    "HUN": "HU",
    "IND": "IN",
    "IDN": "ID",
    "IRN": "IR",
    "IRL": "IE",
    "ISR": "IL",
    "ITA": "IT",
    "JPN": "JP",
    "JOR": "JO",
    "KAZ": "KZ",
    "LAO": "LA",
    "LVA": "LV",
    "LTU": "LT",
    "LUX": "LU",
    "MAC": "MO",
    "MYS": "MY",
    "MEX": "MX",
    "MNG": "MN",
    "MAR": "MA",
    "NLD": "NL",
    "NZL": "NZ",
    "NGA": "NG",
    "NOR": "NO",
    "OMN": "OM",
    "PAK": "PK",
    "PAN": "PA",
    "PER": "PE",
    "PHL": "PH",
    "POL": "PL",
    "PRT": "PT",
    "ROU": "RO",
    "RUS": "RU",
    "SAU": "SA",
    "SRB": "RS",
    "SGP": "SG",
    "SVK": "SK",
    "SVN": "SI",
    "ZAF": "ZA",
    "KOR": "KR",
    "ESP": "ES",
    "SWE": "SE",
    "CHE": "CH",
    "TWN": "TW",
    "THA": "TH",
    "TUN": "TN",
    "TUR": "TR",
    "UKR": "UA",
    "ARE": "AE",
    "USA": "US",
    "UZB": "UZ",
    "VNM": "VN",
}

COUNTRY_GROUPS = {
    "africa": ["ZA", "MA", "EG", "NG", "TN"],
    "central_asia": ["AZ", "KZ", "MN", "UZ"],
    "east_asia": ["CN", "HK", "JP", "KR", "MO", "TW"],
    "europe": [
        "AL",
        "AT",
        "BY",
        "BE",
        "BA",
        "BG",
        "HR",
        "CY",
        "CZ",
        "DK",
        "EE",
        "FI",
        "FR",
        "DE",
        "GR",
        "HU",
        "IE",
        "IT",
        "LV",
        "LT",
        "LU",
        "NL",
        "NO",
        "PL",
        "PT",
        "RO",
        "RU",
        "RS",
        "SK",
        "SI",
        "ES",
        "SE",
        "CH",
        "TR",
        "UA",
        "UK",
    ],
    "g7": ["US", "CA", "FR", "DE", "IT", "JP", "UK"],
    "g20": [
        "AR",
        "AU",
        "BR",
        "CA",
        "CN",
        "FR",
        "DE",
        "EA",
        "IN",
        "ID",
        "IT",
        "JP",
        "KR",
        "MX",
        "RU",
        "SA",
        "TR",
        "US",
        "UK",
        "ZA",
    ],
    "latin_america": ["AR", "BR", "CL", "CO", "CR", "DO", "HN", "PA", "PE"],
    "middle_east": ["IR", "IL", "JO", "OM", "SA", "AE"],
    "north_america": ["CA", "MX", "US"],
    "oceania": ["AU", "NZ"],
    "south_asia": ["BD", "IN", "PK"],
    "southeast_asia": ["KH", "ID", "LA", "MY", "PH", "SG", "TH", "VN"],
}

with (files("openbb_econdb.utils") / "indicators_descriptions.json").open() as f:
    INDICATORS_DESCRIPTIONS = json.load(f)

with (files("openbb_econdb.utils") / "multipliers.json").open() as f:
    MULTIPLIERS = json.load(f)

with (files("openbb_econdb.utils") / "scales.json").open() as f:
    SCALES = json.load(f)

with (files("openbb_econdb.utils") / "units.json").open() as f:
    UNITS = json.load(f)

with (files("openbb_econdb.utils") / "symbol_to_indicator.json").open() as f:
    SYMBOL_TO_INDICATOR = json.load(f)

with (files("openbb_econdb.utils") / "indicator_countries.json").open() as f:
    INDICATOR_COUNTRIES = json.load(f)

HAS_COUNTRIES = {
    d: INDICATOR_COUNTRIES.get(d) != ["W00"] for d in INDICATORS_DESCRIPTIONS
}

QUERY_TRANSFORMS = ["TOYA", "TPOP", "TUSD", "TPGP"]

TRANSFORM_DICT = {
    "TOYA": "Change from one year ago",
    "TPOP": "Change from previous period",
    "TUSD": "Values as US dollars",
    "TPGP": "Values as a percent of GDP",
    "TNOR": "Indexed to 100",
}

POP_MULTIPLIER = {
    "United States": 1000,
    "China": 10000,
    "Japan": 10000,
    "Russian Federation": 1000000,
    "Australia": 1000,
    "Brazil": 1000,
    "South Africa": 1000,
    "Switzerland": 1000,
    "Taiwan": 1000,
    "Bangladesh": 1000000,
    "Pakistan": 1000000,
    "Panama": 1000,
    "Honduras": 1000000,
    "Vietnam": 1000,
    "Malaysia": 1000,
    "Laos": 1000,
}

PROFILE_ORDER = [
    "Population",
    "GDP ($B USD)",
    "GDP QoQ",
    "GDP YoY",
    "CPI YoY",
    "Core CPI YoY",
    "Retail Sales YoY",
    "Industrial Production YoY",
    "Policy Rate",
    "10Y Yield",
    "Govt Debt/GDP",
    "Current Account/GDP",
    "Jobless Rate",
]

GDP_ADJUST = [
    "United States",
    "Canada",
    "Mexico",
    "South Africa",
    "Argentina",
    "Uzbekistan",
    "Kazakhstan",
    "Bosnia And Herzegovina",
]


def parse_symbols(
    symbol,
    transform: Optional[str] = None,
    countries: Optional[Union[str, List[str]]] = None,
):
    """Parse the indicator symbol with the optional transformation for a list of countries. Returns a string list."""
    symbols = []
    if not countries:
        if transform:
            symbol += "~" + transform
        symbols.append(symbol)
    elif countries and HAS_COUNTRIES.get(symbol, False) is False:
        raise OpenBBError(f"Indicator {symbol} does not have countries.")
    elif countries and HAS_COUNTRIES.get(symbol, False) is True:
        countries = countries if isinstance(countries, list) else countries.split(",")
        for country in countries:
            new_country = (
                "EA19"
                if country == "EA" and (symbol in ["URATE", "POP", "GDEBT"])
                else country
            )
            new_symbol = symbol + new_country
            if transform:
                new_symbol += "~" + transform
            symbols.append(new_symbol)

    return ",".join(symbols)


def unit_multiplier(unit: str) -> int:  # pylint: disable=R0911
    """Return the multiplier for a given unit measurement."""
    if unit == "thousands":
        return 1000
    if unit in ["tens of thousands", "tens thousands"]:
        return 10000
    if unit in ["hundreds of thousands", "hundreds thousands"]:
        return 100000
    if unit in ["millions", "milions"]:
        return 1000000
    if unit in ["tens of millions", "tens millions"]:
        return 10000000
    if unit in ["hundreds of millions", "hundreds millions"]:
        return 100000000
    if unit == "billions":
        return 1000000000
    if unit == "trillions":
        return 1000000000000
    return 1


def get_indicator_countries(indicator: str) -> List[str]:
    """Get the list of countries for a given indicator."""
    return INDICATOR_COUNTRIES.get(indicator, [])


async def create_token(use_cache: bool = True) -> str:
    """Create a temporary token for the EconDB API."""

    async def _callback(_response, _):
        """Response callback function."""
        try:
            return await _response.json()
        except Exception as e:
            raise OpenBBError(
                "The temporary EconDB token could not be retrieved."
                + " Please try again later or provide your own token."
                + " Sign-up at: https://www.econdb.com/"
                + " Your IP address may have been flagged by Cloudflare."
            ) from e

    response: Union[dict, List[dict]] = {}
    url = "https://www.econdb.com/user/create_token/?reset=0"
    if use_cache:
        cache_dir = f"{get_user_cache_directory()}/http/econdb_indicators_temp_token"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 12)
        ) as session:
            try:
                response = await amake_request(
                    url, response_callback=_callback, session=session  # type: ignore
                )
            finally:
                await session.close()
    else:
        response = await amake_request(url, response_callback=_callback)  # type: ignore
    return response.get("api_key", "")  # type: ignore


async def download_indicators(use_cache: bool = True) -> DataFrame:
    """Download the list of main indicators from the EconDB website."""
    url = "http://econdb.com/static/help/main_tickers.csv"

    async def callback(response, _) -> str:
        """Response callback to read the CSV response."""
        return await response.text()

    response: Union[dict, List[dict]] = {}
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/econdb_indicators"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24 * 7)
        ) as session:
            try:
                response = await amake_request(url, session=session, response_callback=callback)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, response_callback=callback)  # type: ignore
    all_tickers = read_csv(StringIO(response))  # type: ignore
    # Drop all the OECD stuff that is obsolete.
    all_tickers = all_tickers[all_tickers.iso.astype(str) != "OECD"]
    # Clear out some other known, bad data.
    all_tickers = all_tickers[~all_tickers.short_ticker.isin(["POPNP", "M3CO"])]
    all_tickers = all_tickers[~all_tickers.short_ticker.str.contains("_")]
    country_indicators = all_tickers[all_tickers.iso.str.len() == 2].copy()
    country_indicators.loc[:, "symbol_root"] = country_indicators.apply(
        lambda row: (
            row["short_ticker"][::-1].replace(row["iso"][::-1], "", 1)[::-1]
            if row["short_ticker"].endswith(row["iso"])
            else row["short_ticker"]
        ),
        axis=1,
    )
    country_indicators = country_indicators.query(
        "symbol_root != 'XUSD' and ~symbol_root.str.startswith('USD')"
        " and symbol_root != 'EURUSD' and short_ticker != 'PPIAZ'"
    )
    commodity_indicators = all_tickers.query(
        "iso == 'W00' and ~short_ticker.str.endswith('W00')"
    ).copy()
    commodity_indicators["symbol_root"] = commodity_indicators["short_ticker"]
    commodity_indicators["currency"] = "USD"
    tickers = concat([country_indicators, commodity_indicators], axis=0)
    tickers["multiplier"] = tickers.scale.astype(str).str.lower().apply(unit_multiplier)
    # Fix a typo in the data.
    tickers["scale"] = tickers.scale.astype(str).str.replace("Milions", "Millions")
    # Fix a known incorrect value.
    tickers.loc[tickers["short_ticker"] == "GDPPCNZ", "multiplier"] = 1
    tickers.loc[tickers["short_ticker"] == "GDPPCNZ", "scale"] = "Units"
    tickers.entity = tickers.entity.str.replace("All countries", "World")
    tickers = tickers.fillna("N/A").replace("N/A", None).replace("nan", None)
    return tickers.sort_values(by="last_date", ascending=False)


async def get_context(
    symbol: str,
    countries: Union[str, List[str]],
    transform: Optional[str] = None,
    use_cache: bool = True,
) -> Union[dict, List[dict]]:
    """Get the data for a symbol and a list of countries."""
    response: Union[dict, List[dict]] = {}
    urls = []
    countries = countries if isinstance(countries, list) else countries.split(",")
    # Multiple countries could be passed in a single request, but the request is prone
    # to failure if there is a bad symbol. To avoid this, each country is requested individually.
    # If one country does not return data, the request will still be successful.
    for country in countries:
        if country not in INDICATOR_COUNTRIES.get(symbol, []):
            continue
        symbols_string = parse_symbols(symbol, transform, country)
        url = f"https://www.econdb.com/series/context/?tickers=[{symbols_string}]"
        urls.append(url)
    # Using cache is recommended to avoid needlessly requesting the same data.
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/econdb_context"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24)
        ) as session:
            try:
                response = await amake_requests(urls, session=session)
            finally:
                await session.close()
    else:
        response = await amake_requests(urls)
    return response


def parse_context(  # pylint: disable=R0912, R0914, R0915
    response: List[Dict], latest: bool = False, with_metadata: bool = False
) -> Union[DataFrame, Tuple[DataFrame, Dict]]:
    """Parse the output from `get_context()`, and optionally return the metadata."""
    metadata = {}
    results = DataFrame()
    if response is None:
        raise OpenBBError("No data was in the response")
    if not isinstance(response, List):
        raise OpenBBError("Expecting a list of dictionaries and received a dictionary.")
    for item in response:
        symbol = item.get("id", "")
        _symbol = symbol.split("~")[0].replace("19", "")
        temp_unit = ""
        temp_meta = item.get("td", {})
        temp_data = item.get("dataarray", [])
        temp_transform = symbol.split("~")[1] if "~" in symbol else ""
        temp_country = item.get("geography", {}).get("name", "")
        temp_country = temp_country.replace(" (19 countries)", "")
        # We need the metadata to process the results.
        if temp_meta:
            temp_unit = temp_meta.get("units", "")
            temp_scale = temp_meta.get("scale", "")
            if temp_transform:
                if temp_transform in ["TOYA", "TPOP", "TPGP"]:
                    temp_unit = "Percent"
                if temp_transform == "TUSD":
                    temp_unit = "USD"
                temp_transform = TRANSFORM_DICT.get(temp_transform, "")
            temp_multiplier = (
                1 if temp_unit == "Percent" else unit_multiplier(temp_scale.lower())
            )
            date_ranges = temp_meta.get("range", [])
            # We store the metadata for each indicator.
            metadata[_symbol] = dict(  # pylint: disable=R1735
                country=temp_country.title(),
                title=item.get("verbose_title", None),
                frequency=temp_meta.get("frequency", None),
                transformation=temp_transform if temp_transform else None,
                unit=temp_unit,
                unit_multiplier=temp_multiplier,
                scale=temp_unit if temp_unit == "Percent" else temp_scale,
                description=temp_meta.get("descrip_long", None),
                last_update=temp_meta.get("lastupdate", None),
                next_release=temp_meta.get("next_release", None),
                first_date=date_ranges[0] if date_ranges else None,
                last_date=date_ranges[1] if date_ranges else None,
                dataset=item.get("dataset", None),
            )
            if temp_data:
                temp_series = (
                    DataFrame(temp_data).set_index("date").sort_index().get(symbol)
                )
                temp_series.name = _symbol
                temp_series = temp_series.replace("nan", None).dropna()
                temp_series.name = temp_series.name[:-2]
                temp_series = temp_series.to_frame()
                temp_series["Country"] = metadata[_symbol].get("country")
                # To make the GDP data comparable across countries, it needs to be consistent.
                # We scale everything to billions for GDP. The data needs to be annualized for most countries.
                if "GDP" in symbol and temp_unit != "Percent":
                    temp_series[_symbol[:-2]] = (
                        temp_series[_symbol[:-2]].astype(float).dropna()
                    )
                    # For some countries, we need to annualize the GDP data.
                    if temp_country not in GDP_ADJUST:
                        temp_series[_symbol[:-2]] = (
                            temp_series[_symbol[:-2]].rolling(4).sum()
                        )
                    temp_series[_symbol[:-2]] = (
                        temp_series[_symbol[:-2]] * temp_multiplier
                    ) / 1000000000
                    # Update the metadata to reflect the new scale.
                    metadata[_symbol]["unit_multiplier"] = 1000000000
                    metadata[_symbol]["scale"] = "Billions"
                if "GDEBT" in symbol and temp_unit != "Percent":
                    # We apply the multiplier in the metadata to the data and then convert it to billions.
                    temp_series[_symbol[:-2]] = (
                        temp_series[_symbol[:-2]].astype(float) * temp_multiplier
                    ) / 1000000000
                if "POP" in symbol and temp_unit != "Percent":
                    temp_series[_symbol[:-2]] = (
                        temp_series[_symbol[:-2]].astype(int).dropna()
                    )
                    # We don't use the metadata multiplier here because it is not always accurate.
                    if temp_country in POP_MULTIPLIER:
                        temp_series[_symbol[:-2]] = (
                            temp_series[_symbol[:-2]] * POP_MULTIPLIER[temp_country]
                        )
                        metadata[_symbol]["unit_multiplier"] = POP_MULTIPLIER[
                            temp_country
                        ]
                # If we are just getting the latest data, clip it.
                if latest is True:
                    temp_series = temp_series.set_index("Country").tail(1)
                results = concat([results, temp_series], axis=0)
    if with_metadata is True:
        return results, metadata
    return results


def update_json_files() -> None:
    """Update the static JSON files with fresh values from EconDB."""
    loop = asyncio.get_event_loop()
    indicators = loop.run_until_complete(download_indicators(use_cache=False))

    def update_symbol_to_indicator() -> None:
        """Update the symbol to indicator mapping."""
        with open(
            files("openbb_econdb.utils") / "symbol_to_indicator.json",
            "w",  # type: ignore
            encoding="utf-8",
        ) as f:
            json_data = json.dumps(
                indicators.set_index("short_ticker")
                .sort_index()["symbol_root"]
                .to_dict()
            )
            f.write(json_data)

    def update_multipliers() -> None:
        """Update the unit multipliers."""
        with open(  # type: ignore
            files("openbb_econdb.utils") / "multipliers.json", "w", encoding="utf-8"
        ) as f:
            json_data = json.dumps(
                indicators.set_index("short_ticker")
                .sort_index()["multiplier"]
                .to_dict()
            )
            f.write(json_data)

    def update_scales() -> None:
        """Update the scales."""
        with open(  # type: ignore
            files("openbb_econdb.utils") / "scales.json", "w", encoding="utf-8"
        ) as f:
            json_data = json.dumps(
                indicators.set_index("short_ticker").sort_index()["scale"].to_dict()
            )
            f.write(json_data)

    def update_units() -> None:
        """Update the units."""
        with open(  # type: ignore
            files("openbb_econdb.utils") / "units.json", "w", encoding="utf-8"
        ) as f:
            json_data = json.dumps(
                indicators.set_index("short_ticker").sort_index()["currency"].to_dict()
            )
            f.write(json_data)

    def update_descriptions() -> None:
        """Update the indicator descriptions."""
        descriptions_dict = dict(
            zip(indicators["symbol_root"], indicators["description"])
        )
        descriptions_dict = {k: descriptions_dict[k] for k in sorted(descriptions_dict)}
        with open(  # type: ignore
            files("openbb_econdb.utils") / "indicators_descriptions.json",
            "w",
            encoding="utf-8",
        ) as f:
            json_data = json.dumps(descriptions_dict)
            f.write(json_data)

    def update_indicator_countries() -> None:
        """Update the indicator countries."""
        with open(  # type: ignore
            files("openbb_econdb.utils") / "indicator_countries.json",
            "w",
            encoding="utf-8",
        ) as f:
            json_data = json.dumps(
                indicators[indicators["symbol_root"] != "[W00]"]
                .groupby("symbol_root")["iso"]
                .apply(lambda x: x.sort_values().unique().tolist())
                .to_dict()
            )
            f.write(json_data)

    update_symbol_to_indicator()
    update_multipliers()
    update_scales()
    update_units()
    update_descriptions()
    update_indicator_countries()
