"""IMF IRFCL Data Set Helpers."""

from typing import Dict, List, Optional


def load_irfcl_symbols() -> Dict:
    """Load IMF IRFCL symbols."""
    # pylint: disable=import-outside-toplevel
    import json  # noqa
    from json.decoder import JSONDecodeError
    from pathlib import Path
    from openbb_core.app.model.abstract.error import OpenBBError

    try:
        symbols_file = Path(__file__).parents[1].joinpath("assets", "imf_symbols.json")
        with symbols_file.open(encoding="utf-8") as file:
            symbols = json.load(file)
    except (FileNotFoundError, JSONDecodeError) as e:
        raise OpenBBError(f"Failed to load IMF IRFCL symbols: {e}") from e

    return {k: v for k, v in symbols.items() if v["dataset"] == "IRFCL"}


def load_country_map() -> Dict:
    """Load IMF IRFCL country map."""
    # pylint: disable=import-outside-toplevel
    import json  # noqa
    from json.decoder import JSONDecodeError
    from pathlib import Path
    from openbb_core.app.model.abstract.error import OpenBBError

    try:
        country_map_file = (
            Path(__file__).parents[1].joinpath("assets", "imf_country_map.json")
        )
        with country_map_file.open(encoding="utf-8") as file:
            country_map_dict = json.load(file)
    except (FileNotFoundError, JSONDecodeError) as e:
        raise OpenBBError(f"Failed to load IMF IRFCL country map: {e}") from e

    return {
        k: v.split(",")[0].split("_(")[0]
        for k, v in country_map_dict.items()
        if len(k) == 2
        and k[0] not in ("5", "1", "7")
        and k not in ("X0", "R1", "GW", "F1", "F6")
    }


def load_country_to_code_map() -> Dict:
    """Load a map of lowercase country name to 2-letter ISO symbol."""
    return {
        (
            "euro_area"
            if k == "U2"
            else v.lower()
            .replace(" ", "_")
            .replace("`", "")
            .split(",")[0]
            .split("_(")[0]
        ): k
        for k, v in load_country_map().items()
    }


def validate_countries(countries) -> str:
    """Validate the country and convert to a 2-letter ISO country code."""
    # pylint: disable=import-outside-toplevel
    from warnings import warn  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError

    country_map_dict = load_country_to_code_map()

    if isinstance(countries, str):
        countries = countries.split(",")
    elif not isinstance(countries, list):
        raise OpenBBError("Invalid countries list.")

    new_countries: List = []

    if "all" in countries or "ALL" in countries:
        return "all"

    for country in countries:
        if country.lower() not in country_map_dict and country.upper() not in list(
            country_map_dict.values()
        ):
            warn(f"Invalid IMF IRFCL country: {country}")
            continue

        if country.upper() in list(country_map_dict.values()):
            new_countries.append(country.upper())
        else:
            new_countries.append(country_map_dict.get(country, country).upper())

    new_countries = [c for c in new_countries if c]

    if not new_countries:
        raise OpenBBError("No valid countries found in the supplied list.")

    return ",".join(new_countries)


def validate_symbols(symbols) -> str:
    """Validate the IMF IRFCL symbols."""
    # pylint: disable=import-outside-toplevel
    from warnings import warn  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_imf.utils.constants import IRFCL_PRESET

    irfcl_symbols = load_irfcl_symbols()

    if isinstance(symbols, str):
        symbols = symbols.split(",")
    elif not isinstance(symbols, list):
        raise OpenBBError("Invalid symbols list.")

    if "IRFCL" in symbols or "all" in symbols:
        return "all"

    new_symbols: List = []

    for symbol in symbols:
        if symbol in IRFCL_PRESET:
            return IRFCL_PRESET[symbol].replace(",", "+")
        if symbol.upper() not in irfcl_symbols:
            warn(f"Invalid IMF IRFCL symbol: {symbol}")
        new_symbols.append(symbol.upper())

    return "+".join(new_symbols) if len(new_symbols) > 1 else new_symbols[0]


# We use this as a helper to allow future expansion of the supported IMF indicators.
# Each database has its own nuances with URL construction and schemas.
# In the future, we will check the supported symbols map and direct the call
# to the appropriate dtatabase's function.


# pylint: disable=too-many-branches,too-many-statements,too-many-locals
async def _get_irfcl_data(**kwargs) -> List[Dict]:
    """Get IMF IRFCL data.
    This function is not intended to be called directly,
    but through the `ImfEconomicIndicatorsFetcher` class.
    """
    # pylint: disable=import-outside-toplevel
    from aiohttp.client_exceptions import ContentTypeError  # noqa
    from json.decoder import JSONDecodeError
    from openbb_core.provider.utils.helpers import amake_request
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_imf.utils import constants
    from pandas import to_datetime
    from pandas.tseries import offsets

    countries = kwargs.get("country", "")
    countries = (
        "" if countries == "all" else countries.replace(",", "+") if countries else ""
    )

    frequency = constants.FREQUENCY_DICT.get(kwargs.get("frequency", "quarter"), "Q")
    sector = kwargs.get("sector", "monetary_authorities")
    sector = constants.REF_SECTORS_DICT.get(sector, "")
    start_date = kwargs.get("start_date", "")
    end_date = kwargs.get("end_date", "")

    # Adjust the dates to the date relative to frequency.
    # The API does not accept arbitrary dates, so we need to adjust them.
    if start_date:
        start_date = to_datetime(start_date)
        if frequency == "Q":
            # offset = offsets.QuarterBegin(startingMonth=1)
            # start_date = start_date + offset
            start_date = offsets.QuarterBegin(startingMonth=1).rollback(start_date)
        elif frequency == "A":
            start_date = offsets.YearBegin().rollback(start_date)
        else:
            start_date = offsets.MonthBegin().rollback(start_date)
        start_date = start_date.strftime("%Y-%m-%d")

    if end_date:
        end_date = to_datetime(end_date)
        if frequency == "Q":
            end_date = offsets.QuarterEnd().rollforward(end_date)
        elif frequency == "A":
            end_date = offsets.YearEnd().rollforward(end_date)
        else:
            end_date = offsets.MonthEnd().rollforward(end_date)
        end_date = end_date.strftime("%Y-%m-%d")

    indicator = kwargs.get("symbol")
    indicator = validate_symbols(indicator) if indicator else ""
    indicator = "" if indicator == "all" else indicator

    if not indicator and not countries:
        raise OpenBBError("Country is required when returning the complete dataset.")

    date_range = (
        f"?startPeriod={start_date}&endPeriod={end_date}"
        if start_date and end_date
        else ""
    )
    base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/"
    key = f"CompactData/IRFCL/{frequency}.{countries}.{indicator}.{sector}"
    url = f"{base_url}{key}{date_range}"

    try:
        response = await amake_request(url, timeout=20)
    except (JSONDecodeError, ContentTypeError) as e:
        raise OpenBBError(
            "Error fetching data; This might be rate-limiting. Try again later."
        ) from e

    if "ErrorDetails" in response:
        raise OpenBBError(
            f"{response['ErrorDetails'].get('Code')} -> {response['ErrorDetails'].get('Message')}"  # type: ignore
        )

    series = response.get("CompactData", {}).get("DataSet", {}).pop("Series", {})  # type: ignore

    if not series:
        raise OpenBBError(f"No time series data found -> {response}")

    # If there is only one series, they ruturn a dict instead of a list.
    if series and isinstance(series, dict):
        series = [series]

    data: List = []
    all_symbols = load_irfcl_symbols()
    country_map_dict = {
        v: k.replace("_", " ").title().replace("Ecb", "ECB")
        for k, v in load_country_to_code_map().items()
    }
    # Iterate over the series to extract observations and map the metadata.
    for s in series:
        if "Obs" not in s:
            continue
        meta = {
            k.replace("@", "").lower(): (
                constants.UNIT_MULTIPLIERS_MAP.get(str(v), v)
                if k == "@UNIT_MULT"
                else v
            )
            for k, v in s.items()
            if k != "Obs"
        }
        _symbol = meta.get("indicator")
        _parent: Optional[str] = None
        _order: Optional[str] = None
        _level: Optional[str] = None
        _table: Optional[str] = None
        _title: Optional[str] = None

        if _symbol in all_symbols:
            _table = all_symbols.get(_symbol, {}).get("table")
            _parent = all_symbols.get(_symbol, {}).get("parent", "")
            _order = all_symbols.get(_symbol, {}).get("order", "")
            _level = all_symbols.get(_symbol, {}).get("level", "")
            _title = all_symbols.get(_symbol, {}).get("title", "")

        _data = s.pop("Obs", [])

        if isinstance(_data, dict):
            _data = [_data]

        for d in _data:
            _date = d.pop("@TIME_PERIOD", None)
            val = d.pop("@OBS_VALUE", None)

            if not val:
                continue

            if _date:
                offset = (
                    offsets.QuarterEnd
                    if "Q" in _date
                    else offsets.YearEnd if len(str(_date)) == 4 else offsets.MonthEnd
                )
                _date = to_datetime(_date)
                _date = _date + offset(0)
                _date = _date.strftime("%Y-%m-%d")
            vals = {
                k: v
                for k, v in {
                    "date": _date,
                    "table": _table,
                    "symbol": _symbol,
                    "parent": _parent,
                    "order": _order,
                    "level": _level,
                    "country": country_map_dict.get(
                        meta.get("ref_area"), meta.get("ref_area")
                    ),
                    "reference_sector": constants.SECTOR_MAP.get(
                        meta.get("ref_sector"), meta.get("ref_sector")
                    ),
                    "title": _title,
                    "value": float(val) if val else None,
                    "scale": meta.get("unit_mult"),
                }.items()
                if v
            }

            if vals.get("value") and vals.get("date"):
                d.update(vals)

        if _data:
            data.extend([d for d in _data if d])

    if not data:
        raise OpenBBError("No data found.")

    return data
