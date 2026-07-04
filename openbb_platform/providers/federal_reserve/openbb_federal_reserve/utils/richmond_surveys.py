"""Richmond Fed Fifth District survey download and parsing helpers."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any

BASE_URL = "https://www.richmondfed.org"
MEDIA = f"{BASE_URL}/-/media/RichmondFedOrg"
_SURVEY_ROOT = (
    "region_communities/regional_data_analysis/regional_economy"
    "/surveys_of_business_conditions"
)

SURVEYS: dict[str, dict[str, str]] = {
    "manufacturing": {
        "data": f"{MEDIA}/{_SURVEY_ROOT}/manufacturing/data/mfg_historicaldata.xlsx",
        "sheet": "Mfg Historical Series",
    },
    "non_manufacturing": {
        "data": (
            f"{MEDIA}/{_SURVEY_ROOT}/non-manufacturing/data/nmf_historicaldata.xlsx"
        ),
        "sheet": "Non-Mfg Historical Series",
    },
    "carolinas": {
        "data": f"{MEDIA}/{_SURVEY_ROOT}/carolinas/data/car_historicaldata.xlsx",
        "sheet": "CAR Historical Series",
    },
    "maryland": {
        "data": f"{MEDIA}/{_SURVEY_ROOT}/maryland/data/mar_historicaldata.xlsx",
        "sheet": "MD Historical Series",
    },
    "virginia": {
        "data": f"{MEDIA}/{_SURVEY_ROOT}/virginia/data/va_historicaldata.xlsx",
        "sheet": "VA Historical Series",
    },
}


def request_bytes(url: str) -> bytes:
    """Return the raw bytes of a Richmond Fed URL.

    Parameters
    ----------
    url : str
        The Richmond Fed resource URL.

    Returns
    -------
    bytes
        The response body. Wrapped in one helper so a browser-impersonating
        fallback can be substituted if the host begins rejecting plain clients.
    """
    from openbb_core.provider.utils.helpers import make_request

    response = make_request(url)
    response.raise_for_status()
    return response.content


def fetch_survey_workbook(survey: str) -> bytes:
    """Download a Fifth District survey workbook, cached at a monthly cadence.

    Parameters
    ----------
    survey : str
        One of the keys of :data:`SURVEYS`.

    Returns
    -------
    bytes
        The raw XLSX workbook bytes.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    spec = SURVEYS.get(survey)
    if spec is None:
        raise OpenBBError(
            f"No Richmond Fed survey '{survey}'. Choose from {sorted(SURVEYS)}."
        )
    return cached(
        ("richmond_survey", survey),
        lambda: seconds_until_next_release("monthly"),
        lambda: request_bytes(spec["data"]),
    )


def parse_survey_records(
    content: bytes,
    sheet: str,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Parse a survey workbook sheet into NaN-cleaned, date-filtered records.

    Parameters
    ----------
    content : bytes
        The raw XLSX workbook bytes.
    sheet : str
        The exact worksheet name to read.
    start_date, end_date : date | None
        Inclusive bounds applied to the ``date`` column.

    Returns
    -------
    list[dict]
        One record per month with ``#N/A`` and ``NaN`` cells coerced to ``None``.
    """
    from io import BytesIO

    from pandas import isna, read_excel, to_datetime

    frame = read_excel(BytesIO(content), engine="openpyxl", sheet_name=sheet)
    frame = frame.replace("#N/A", None)
    frame["date"] = to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date"])
    frame["date"] = frame["date"].dt.date

    if start_date:
        frame = frame[frame["date"] >= start_date]
    if end_date:
        frame = frame[frame["date"] <= end_date]

    return [
        {k: (None if isinstance(v, float) and isna(v) else v) for k, v in row.items()}
        for row in frame.sort_values("date").to_dict(orient="records")
    ]


_ADJUSTMENTS = {"nsa": "Not Seasonally Adjusted", "sa": "Seasonally Adjusted"}
_HORIZONS = {"c": "Current", "e": "Expectations (Six Months Ahead)"}
_INFIXES = {"mfg", "nmf", "svc", "car", "mar", "md", "va"}
_INDICATORS = {
    "ship": "Shipments",
    "new_orders": "New Orders",
    "bk_logs": "Backlog of Orders",
    "cap_util": "Capacity Utilization",
    "vend_lead": "Vendor Lead Time",
    "emp": "Number of Employees",
    "workwk": "Average Workweek",
    "wage": "Wages",
    "fd_gds_inv": "Finished Goods Inventories",
    "raw_mats_inv": "Raw Materials Inventories",
    "pct_chg_prcs_recd": "Prices Received",
    "pct_chg_prcs_pd": "Prices Paid",
    "capital_expnd": "Capital Expenditures",
    "local_bus_cond": "Local Business Conditions",
    "nec_skls_avail": "Availability of Necessary Skills",
    "equip_sftw_expnd": "Equipment and Software Expenditures",
    "bus_svcs_expnd": "Business Services Expenditures",
    "composite": "Composite Index",
    "revenues": "Revenues",
    "revs_sales": "Revenues",
    "demand": "Demand",
    "ave_wage": "Wages",
    "ave_workwk": "Average Workweek",
    "prcs_recd": "Prices Received",
    "new_orders_recd": "New Orders Received",
    "bus_act": "Business Activity",
    "gen_bus_cond": "General Business Conditions",
    "sales": "Sales",
    "bus_cond_nation": "Business Conditions (Nation)",
    "bus_cond_region": "Business Conditions (Region)",
}


def _decode_richmond(code: str) -> dict[str, str] | None:
    """Decode a ``{adj}_{survey}_{indicator}_{c|e}`` column into labelled parts."""
    parts = code.strip().lower().split("_")
    if len(parts) < 2 or parts[0] not in _ADJUSTMENTS:
        return None
    rest = parts[1:]
    if rest and rest[0] in _INFIXES:
        rest = rest[1:]
    horizon = _HORIZONS["c"]
    if rest and rest[-1] in _HORIZONS:
        horizon = _HORIZONS[rest[-1]]
        rest = rest[:-1]
    if not rest:
        return None
    key = "_".join(rest)
    return {
        "indicator": _INDICATORS.get(key, key.replace("_", " ").title()),
        "adjustment": _ADJUSTMENTS[parts[0]],
        "horizon": horizon,
    }


def parse_survey_long(
    content: bytes,
    sheet: str,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Decode a survey sheet into long, labelled diffusion-index records."""
    records = parse_survey_records(content, sheet, start_date, end_date)
    out: list[dict[str, Any]] = []
    for record in records:
        observation = record["date"]
        for column, value in record.items():
            if column == "date":
                continue
            decoded = _decode_richmond(str(column))
            if decoded is None:
                out.append(
                    {
                        "date": observation,
                        "indicator": str(column),
                        "adjustment": None,
                        "horizon": None,
                        "value": value,
                    }
                )
            else:
                out.append({"date": observation, **decoded, "value": value})
    return sorted(
        out,
        key=lambda r: (r["date"], r["indicator"], str(r["adjustment"]), r["horizon"]),
    )


def parse_survey_wide(
    content: bytes,
    sheet: str,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Decode a survey sheet into wide rows, one indicator column per series."""
    from openbb_federal_reserve.utils.workbook import pivot_wide

    records = parse_survey_long(content, sheet, start_date, end_date)
    return pivot_wide(
        records,
        index=("date", "adjustment", "horizon"),
        column="indicator",
        value="value",
    )
