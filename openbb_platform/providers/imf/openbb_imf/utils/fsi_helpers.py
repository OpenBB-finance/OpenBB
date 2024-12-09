"""IMF FSI Data Set Helpers."""

from typing import Optional


def load_fsi_symbols() -> dict:
    """Load IMF FSI symbols."""
    # pylint: disable=import-outside-toplevel
    from openbb_imf.utils.constants import load_symbols

    return load_symbols("FSI")


def validate_symbols(symbols) -> str:
    """Validate the IMF FSI symbols."""
    # pylint: disable=import-outside-toplevel
    from warnings import warn  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_imf.utils.constants import FSI_PRESETS

    fsi_symbols = load_fsi_symbols()

    if isinstance(symbols, str):
        symbols = symbols.split(",")
    elif not isinstance(symbols, list):
        raise OpenBBError("Invalid symbols list.")

    new_symbols: list = []

    for symbol in symbols:
        if symbol in FSI_PRESETS:
            return symbol
        if symbol.upper() not in fsi_symbols:
            warn(f"Unsupported IMF FSI symbol: {symbol}")
        new_symbols.append(symbol.upper())

    return "+".join(new_symbols) if len(new_symbols) > 1 else new_symbols[0]


# pylint: disable=too-many-branches,too-many-statements,too-many-locals
async def _get_fsi_data(**kwargs) -> list[dict]:  # noqa:PLR0912
    """Get IMF FSI data.
    This function is not intended to be called directly,
    but through the `ImfEconomicIndicatorsFetcher` class.
    """
    # pylint: disable=import-outside-toplevel
    from datetime import date  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_imf.utils.helpers import get_data
    from openbb_imf.utils.irfcl_helpers import load_country_to_code_map
    from openbb_imf.utils import constants
    from pandas import to_datetime
    from pandas.tseries import offsets

    countries = kwargs.get("country", "")
    countries = (
        "" if countries == "all" else countries.replace(",", "+") if countries else ""
    )
    frequency = constants.FREQUENCY_DICT.get(kwargs.get("frequency", "quarter"), "Q")
    start_date = kwargs.get("start_date", "")
    end_date = kwargs.get("end_date", "")
    all_symbols = load_fsi_symbols()
    core_only = [k for k, v in all_symbols.items() if v.get("table") == "fsi_core"]
    encouraged_set = [
        k for k, v in all_symbols.items() if v.get("table") == "fsi_encouraged_set"
    ]
    indicator = kwargs.get("symbol")
    indicators = (
        "+".join(core_only if indicator == "fsi_core" else encouraged_set)
        if indicator in ["fsi_core", "fsi_encouraged_set"]
        else (
            ""
            if indicator
            in ["fsi_other", "fsi_all", "fsi_core_underlying", "fsi_balance_sheets"]
            else validate_symbols(indicator)
        )
    )

    if not indicators and not countries:
        raise OpenBBError(
            "All countries not supported for this group of indicators. Please supply a country."
        )

    if not start_date and not end_date and not countries:
        start_date = (
            date.today().replace(year=date.today().year - 1).strftime("%Y-%m-%d")
        )

    if start_date and not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    # Adjust the dates to the date relative to frequency.
    # The API does not accept arbitrary dates, so we need to adjust them.
    if start_date:
        start_date = to_datetime(start_date)
        if frequency == "Q":
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

    date_range = (
        f"?startPeriod={start_date}&endPeriod={end_date}"
        if start_date and end_date
        else ""
    )
    base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/"
    key = f"CompactData/FSI/{frequency}.{countries}.{indicators}"
    url = f"{base_url}{key}{date_range}"
    series = await get_data(url)
    data: list = []
    all_symbols = load_fsi_symbols()

    if indicator in ["fsi_core", "fsi_encouraged_set"]:
        all_symbols = {
            k: v for k, v in all_symbols.items() if v.get("table") == indicator
        }
    elif indicator == "fsi_core_underlying":
        all_symbols = {
            k: v
            for k, v in all_symbols.items()
            if "core set" in v.get("title", "").lower() and v.get("unit") != "Percent"
        }
    elif indicator == "fsi_balance_sheets":
        all_symbols = {
            k: v
            for k, v in all_symbols.items()
            if "balance sheets" in v.get("title", "").lower()
        }
    elif indicator == "fsi_other":
        all_symbols = {
            k: v
            for k, v in all_symbols.items()
            if "Additional FSIs" in v.get("title", "")
        }

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
        _unit: Optional[str] = None

        if _symbol not in all_symbols:
            continue

        _table = all_symbols.get(_symbol, {}).get("table", "")
        if _table and indicator == "fsi_core_underlying":
            _table = _table.replace("fsi_other", "fsi_core_underlying")  # type: ignore
        _parent = all_symbols.get(_symbol, {}).get("parent", "")
        _order = all_symbols.get(_symbol, {}).get("order", "")
        _level = all_symbols.get(_symbol, {}).get("level", "")
        _title = all_symbols.get(_symbol, {}).get("title", "")
        if _title:
            _title = " - ".join(_title.split(", ")[1:-1]).replace(
                "Financial Soundness Indicators - ", ""
            )
        _unit = all_symbols.get(_symbol, {}).get("unit", "")

        _data = s.pop("Obs", [])

        if isinstance(_data, dict):
            _data = [_data]

        for d in _data:
            _date = d.pop("@TIME_PERIOD", None)
            val = d.pop("@OBS_VALUE", None)
            _ = d.pop("@OBS_STATUS", None)
            if not val:
                continue
            val = float(val)
            if _unit and _unit.lower() == "percent":
                val = val / 100
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
                    "parent": _parent if _parent else _symbol,
                    "level": _level,
                    "order": _order,
                    "country": country_map_dict.get(
                        meta.get("ref_area"), meta.get("ref_area")
                    ),
                    "reference_sector": None,
                    "title": _title,
                    "value": val,
                    "unit": (
                        _unit.upper() if _unit and _unit in ["usd", "eur"] else _unit
                    ),
                    "scale": (
                        "Basis Points"
                        if _unit and _unit.lower() == "percent"
                        else meta.get("unit_mult")
                    ),
                }.items()
                if v
            }

            if vals.get("value") and vals.get("date"):
                d.update(vals)
                data.append(d)

    if not data:
        raise OpenBBError(f"No data found for, '{indicator}', in, '{countries}'.")

    return data
