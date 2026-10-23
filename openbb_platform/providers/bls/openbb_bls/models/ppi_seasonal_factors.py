"""BLS PPI seasonal factor tables."""

import re
from datetime import date as dateType
from functools import lru_cache
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_bls.utils.constants import BLS_USER_AGENT
from openbb_bls.utils.tables import (
    PPI_SEASONAL_FACTOR_CANONICAL,
    PPI_SEASONAL_FACTOR_TABLES,
)

PpiSeasonalFactorCategory = Literal["fd_id", "commodity", "forecast"]

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}
_HEADERS = {
    "User-Agent": BLS_USER_AGENT,
    "Accept": "text/html,*/*",
}
_YEAR_RE = re.compile(r"\b(20\d{2})\b")


class BlsPpiSeasonalFactorsQueryParams(QueryParams):
    """BLS PPI Seasonal Factor Table Query Parameters."""

    __json_schema_extra__ = {
        "category": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "FD-ID Aggregation Index (previous 5 years)",
                        "value": "fd_id",
                    },
                    {
                        "label": "Commodity Index (previous 5 years)",
                        "value": "commodity",
                    },
                    {
                        "label": "Commodity Forecast (current year)",
                        "value": "forecast",
                    },
                ]
            }
        },
    }

    category: PpiSeasonalFactorCategory = Field(
        default="fd_id",
        description="Which BLS PPI Seasonal Factor Table to fetch.",
    )


class BlsPpiSeasonalFactorsData(Data):
    """One ``(series, month)`` BLS PPI seasonal-factor observation."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "BLS PPI Seasonal Factors",
                "$.description": ("Producer Price Index seasonal factors."),
                "$.gridData": {"w": 40, "h": 20},
                "$.refetchInterval": False,
                "$.source": ["BLS"],
                "$.category": "Economy",
                "$.subCategory": "PPI",
            }
        }
    )

    date: dateType = Field(
        description="First day of the calendar month the seasonal factor applies to.",
    )
    code: str = Field(
        description="BLS PPI series code with the WPS prefix preserved.",
    )
    label: str | None = Field(
        default=None,
        description="Human-readable series title as published by BLS.",
    )
    seasonal_factor: float | None = Field(
        default=None,
        description="BLS-published multiplicative seasonal factor where 100.000 means no seasonality.",
    )
    table_id: str = Field(
        description="Source BLS table id.",
        json_schema_extra=_HIDE,
    )
    table_name: str = Field(
        description="Full BLS table title.",
        json_schema_extra=_HIDE,
    )


class BlsPpiSeasonalFactorsFetcher(
    Fetcher[
        BlsPpiSeasonalFactorsQueryParams,
        list[BlsPpiSeasonalFactorsData],
    ]
):
    """BLS PPI Seasonal Factor Table Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> BlsPpiSeasonalFactorsQueryParams:
        """Validate and coerce the query."""
        return BlsPpiSeasonalFactorsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsPpiSeasonalFactorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Fetch the seasonal-factor HTML and parse into long-form rows."""
        table_id = PPI_SEASONAL_FACTOR_CANONICAL[query.category]
        entry = PPI_SEASONAL_FACTOR_TABLES.get(table_id)
        if entry is None:  # pragma: no cover -- ``Literal`` constrains the input
            raise OpenBBError(f"Unknown seasonal-factor table_id '{table_id}'.")
        return _fetch_html_table(table_id, entry["url"], entry["label"])

    @staticmethod
    def transform_data(
        query: BlsPpiSeasonalFactorsQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> list[BlsPpiSeasonalFactorsData]:
        """Coerce parsed rows into ``BlsPpiSeasonalFactorsData``."""
        rows = data.get("rows", [])
        if not rows:
            raise EmptyDataError(
                f"No rows parsed from BLS seasonal-factor table "
                f"'{data.get('table_id', '?')}'."
            )
        return [BlsPpiSeasonalFactorsData.model_validate(r) for r in rows]


def _cell_text(node: Any) -> str:
    """Return the trimmed, NBSP-cleaned text of a BeautifulSoup tag."""
    txt = node.get_text(" ", strip=True) if node is not None else ""
    return txt.replace("\xa0", " ").strip()


def _to_float(value: str) -> float | None:
    """Parse a numeric cell, returning ``None`` if it cannot be coerced."""
    if value in ("", "-", "(NA)"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _fetch_html_table(table_id: str, url: str, label: str) -> dict[str, Any]:
    """Download a seasonal-factor HTML page and return long-form rows."""
    from bs4 import BeautifulSoup
    from openbb_core.provider.utils.helpers import get_requests_session

    session = get_requests_session()
    resp = session.get(url, headers=_HEADERS, timeout=60)

    if resp.status_code != 200:
        raise OpenBBError(f"BLS returned HTTP {resp.status_code} fetching {url}.")

    soup = BeautifulSoup(resp.text, "lxml")
    tables = soup.find_all("table")

    if len(tables) < 2:  # pragma: no cover -- BLS always ships >=2 tables
        return {"rows": [], "table_id": table_id, "table_name": label}

    data_table = tables[1]

    if table_id == "ppi-seafac":
        title_text = soup.title.string if soup.title else ""
        rows = _parse_seafac_rows(data_table, title_text or "")
    else:
        rows = _parse_5yr_rows(data_table)

    for row in rows:
        row["table_id"] = table_id
        row["table_name"] = label

    rows.sort(key=lambda r: (r["date"], r["code"]))

    return {"rows": rows, "table_id": table_id, "table_name": label}


def _parse_5yr_rows(data_table: Any) -> list[dict[str, Any]]:
    """Parse blocked five-year tables (``ppi-fdidsf`` / ``ppi-commsf``)."""
    out: list[dict[str, Any]] = []
    code: str | None = None
    title: str | None = None

    for th in data_table.find_all("th"):
        text = _cell_text(th)

        if text.startswith("SERIES CODE"):
            code = text.split(":", 1)[1].strip() if ":" in text else None
            title = None
            continue

        if text.startswith("SERIES TITLE"):
            title = text.split(":", 1)[1].strip() if ":" in text else None
            continue

        year_match = _YEAR_RE.fullmatch(text)

        if year_match is None or code is None:
            continue

        year = int(year_match.group(1))
        cells: list[str] = []
        sib = th.find_next_sibling()

        while sib is not None and sib.name == "td" and len(cells) < 12:
            cells.append(_cell_text(sib))
            sib = sib.find_next_sibling()

        if len(cells) < 12:
            continue

        for month_num, raw in enumerate(cells, start=1):
            out.append(
                {
                    "date": dateType(year, month_num, 1),
                    "code": code,
                    "label": title,
                    "seasonal_factor": _to_float(raw),
                }
            )

    return out


def _parse_seafac_rows(data_table: Any, title_text: str) -> list[dict[str, Any]]:
    """Parse the current-year forecast table (``ppi-seafac``)."""
    year_match = _YEAR_RE.search(title_text)
    year = int(year_match.group(1)) if year_match else None

    if year is None:
        return []

    titles = _wps_titles()
    out: list[dict[str, Any]] = []

    for tr in data_table.find_all("tr"):
        cells = [_cell_text(c) for c in tr.find_all(["th", "td"])]

        if len(cells) < 13:
            continue

        first = cells[0]

        if not first.upper().startswith("WPS"):
            continue

        code = first.replace(" ", "")

        for month_num, raw in enumerate(cells[1:13], start=1):
            out.append(
                {
                    "date": dateType(year, month_num, 1),
                    "code": code,
                    "label": titles.get(code),
                    "seasonal_factor": _to_float(raw),
                }
            )

    return out


@lru_cache(maxsize=1)
def _wps_titles() -> dict[str, str]:
    """Return a memoized {WPS series_id: clean title} map from the PPI metadata cache."""
    from openbb_bls.utils.metadata._core import BlsMetadata

    out: dict[str, str] = {}
    try:
        df = BlsMetadata().get_series("ppi")
    except (FileNotFoundError, KeyError):
        return out
    for sid, title in zip(df["series_id"], df["series_title"]):
        if sid is None or title is None:
            continue
        key = str(sid).strip()
        text = str(title).strip()
        if text.startswith("PPI Commodity data for "):
            text = text[len("PPI Commodity data for ") :]
        for suffix in (", seasonally adjusted", ", not seasonally adjusted"):
            if text.endswith(suffix):
                text = text[: -len(suffix)]
                break
        if key not in out:
            out[key] = text
    return out
