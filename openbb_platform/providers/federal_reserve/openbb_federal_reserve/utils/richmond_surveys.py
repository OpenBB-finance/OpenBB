"""Richmond Fed Fifth District survey download, parsing, and PDF helpers.

The Richmond Fed publishes its Fifth District business surveys (manufacturing,
non-manufacturing, and the per-state Carolinas/Maryland/Virginia variants) as
monthly historical-series workbooks, and each release as a per-month PDF linked
from a survey archive page. This module centralises the HTTP access (through a
single patchable ``request_bytes`` so a browser-impersonating fallback can be
swapped in if the site rejects a plain client), the workbook download/parse, and
the PDF archive index, which folds in the static Regional Economic Snapshots for
the multi-file viewer.
"""

from __future__ import annotations

import re
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

_ARCHIVES: dict[str, dict[str, str]] = {
    "manufacturing": {
        "page": (
            f"{BASE_URL}/region_communities/regional_data_analysis/business_surveys"
            "/manufacturing/archive?mode=archive"
        ),
        "prefix": "mfg",
        "label": "Manufacturing Survey",
    },
    "non_manufacturing": {
        "page": (
            f"{BASE_URL}/region_communities/regional_data_analysis/business_surveys"
            "/non-manufacturing?mode=archive"
        ),
        "prefix": "nmf",
        "label": "Service Sector Survey",
    },
}

_SNAPSHOTS: dict[str, str] = {
    "district": "snapshot.pdf",
    "dc": "snapshot_dc.pdf",
    "md": "snapshot_md.pdf",
    "nc": "snapshot_nc.pdf",
    "sc": "snapshot_sc.pdf",
    "va": "snapshot_va.pdf",
    "wv": "snapshot_wv.pdf",
}
_SNAPSHOT_DIR = f"{MEDIA}/region_communities/regional_data_analysis/regional_snapshot"


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


def request_text(url: str) -> str:
    """Return the decoded text body of a Richmond Fed URL."""
    return request_bytes(url).decode("utf-8", "ignore")


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
# Survey infixes that sit between the adjustment prefix and the indicator; the
# per-state surveys omit it, so only a known infix is stripped.
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
    """Decode a survey sheet into wide rows, one indicator column per series.

    Pivots the long records onto ``(date, adjustment, horizon)``, so each row
    carries one field per survey indicator holding that indicator's diffusion
    index. The indicator columns are dynamic.
    """
    from openbb_federal_reserve.utils.workbook import pivot_wide

    records = parse_survey_long(content, sheet, start_date, end_date)
    return pivot_wide(
        records,
        index=("date", "adjustment", "horizon"),
        column="indicator",
        value="value",
    )


def _classify_release(survey: str, href: str) -> dict[str, Any] | None:
    """Classify a survey release PDF href into a catalog record."""
    spec = _ARCHIVES[survey]
    match = re.search(
        rf"/(\d{{4}})/pdf/{spec['prefix']}_(\d{{2}})_(\d{{2}})_(\d{{2}})\.pdf$", href
    )
    if match is None:
        return None
    year, month, day, _yy = (int(group) for group in match.groups())
    try:
        release_date = dateType(year, month, day)
    except ValueError:
        return None
    return {
        "survey": survey,
        "date": release_date.isoformat(),
        "title": f"{spec['label']} {release_date.strftime('%B %d, %Y')}",
        "url": f"{BASE_URL}{href}",
    }


def _snapshot_records() -> list[dict[str, Any]]:
    """Return the static Regional Economic Snapshot catalog records.

    Dated today so the always-current snapshots sort to the top of the catalog.
    """
    today = dateType.today().isoformat()
    return [
        {
            "survey": "regional_snapshot",
            "date": today,
            "title": (
                "Regional Economic Snapshot"
                if area == "district"
                else f"Regional Economic Snapshot ({area.upper()})"
            ),
            "url": f"{_SNAPSHOT_DIR}/{filename}",
        }
        for area, filename in _SNAPSHOTS.items()
    ]


def list_survey_releases(survey: str | None = None) -> list[dict[str, Any]]:
    """Return the catalog of survey release PDFs, newest first.

    Parameters
    ----------
    survey : str | None
        One of ``"manufacturing"`` or ``"non_manufacturing"``; both, plus the
        static Regional Economic Snapshots, if omitted.

    Returns
    -------
    list[dict]
        One record per release ``{survey, date, title, url}``.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    targets = [survey] if survey else list(_ARCHIVES)

    def _producer() -> list[dict[str, Any]]:
        """Scrape and classify every release PDF, folding in static snapshots."""
        records: dict[tuple, dict[str, Any]] = {}
        for name in targets:
            spec = _ARCHIVES[name]
            text = request_text(spec["page"])
            pattern = (
                rf"(/-/media/[^\"']*?/{name.replace('_', '-')}"
                rf"/\d{{4}}/pdf/{spec['prefix']}_\d{{2}}_\d{{2}}_\d{{2}}[^\"']*?\.pdf)"
            )
            for href in re.findall(pattern, text, re.IGNORECASE):
                record = _classify_release(name, href)
                if record is None:
                    continue
                records[(record["survey"], record["date"])] = record
        if survey is None:
            for record in _snapshot_records():
                records[(record["survey"], record["url"])] = record
        return [records[key] for key in sorted(records, reverse=True)]

    return cached(
        ("richmond_survey_releases", survey),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_survey_release_pdf(
    survey: str = "manufacturing", date: str | None = None
) -> dict[str, Any]:
    """Return a selected survey release PDF as a base64 payload.

    Parameters
    ----------
    survey : str
        ``"manufacturing"`` or ``"non_manufacturing"``.
    date : str | None
        The release date as ``YYYY-MM`` or ``YYYY-MM-DD``; the most recent
        release in the month is used. Defaults to the latest release.

    Returns
    -------
    dict
        ``content`` holds the base64-encoded PDF and ``data_format`` its metadata.
    """
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    if survey not in _ARCHIVES:
        raise OpenBBError(
            f"No Richmond Fed survey '{survey}'. Choose from {sorted(_ARCHIVES)}."
        )
    catalog = [r for r in list_survey_releases(survey) if r["survey"] == survey]
    if not catalog:
        raise OpenBBError(f"No Richmond Fed '{survey}' survey releases are available.")

    selected: dict[str, Any] | None = catalog[0]
    if date:
        target = date[:7]
        selected = next((r for r in catalog if r["date"].startswith(target)), None)
        if not selected:
            raise OpenBBError(
                f"No Richmond Fed '{survey}' survey release for '{date}'."
            )

    def _producer() -> str:
        """Download and base64-encode the selected release PDF."""
        return base64.b64encode(request_bytes(selected["url"])).decode("utf-8")

    content = cached(
        ("richmond_survey_release_pdf", selected["survey"], selected["date"]),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"Richmond_{selected['survey']}_{selected['date']}.pdf",
        },
    }
