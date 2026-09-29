"""BLS Search Model."""

from typing import Any

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bls_search import (
    SearchData,
    SearchQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_bls.utils.constants import SURVEY_CATEGORIES, SURVEY_CATEGORY_NAMES

_API_PREFIX = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)

# Shared config for the ``symbol`` parameter, declared identically on the Search
# and Series widgets so a cell-click groupBy on the Search table's symbol column
# propagates to the Series widget (cell-click grouping links params by name and
# requires both to be the same ``type: endpoint`` dropdown over one endpoint).
_SYMBOL_PARAM_CONFIG = {
    "type": "endpoint",
    "optionsEndpoint": f"{_API_PREFIX}/bls/series/symbol_choices",
    "optionsParams": {"category": "$category"},
    "show": False,
}

# Values that mean "no title" once stringified from the metadata table.
_BLANK_TITLE = {"", "nan", "none", "null", "-"}

# Resolved descriptive columns, in reading order, used to build a human title
# for series the BLS catalog ships without one (e.g. Major Sector Productivity,
# all of JOLTS). Each holds a name (not a raw code) once BlsMetadata resolves it.
_TITLE_FIELDS = (
    "sector_code",
    "industry_code",
    "region_code",
    "state_code",
    "area_code",
    "item_code",
    "dataelement_code",
    "measure_code",
    "ratelevel_code",
    "sizeclass_code",
    "duration_code",
)

_SEASONAL_LABEL = {"S": "seasonally adjusted", "U": "not seasonally adjusted"}


def _is_blank_title(value: Any) -> bool:
    """Return True when a metadata value carries no usable title text."""
    return value is None or str(value).strip().lower() in _BLANK_TITLE


def _synthesize_title(row: dict[str, Any]) -> str | None:
    """Build a readable title from a row's resolved descriptive metadata."""
    parts: list[str] = []
    seen: set[str] = set()
    for key in _TITLE_FIELDS:
        value = row.get(key)
        if _is_blank_title(value):
            continue
        text = str(value).strip()
        if text not in seen:
            seen.add(text)
            parts.append(text)
    title = " — ".join(parts)
    label = _SEASONAL_LABEL.get(str(row.get("seasonal") or "").strip().upper())
    if label:
        title = f"{title} ({label})" if title else label.capitalize()
    return title or None


def _fill_titles(df):
    """Return a copy of ``df`` with ``series_title`` filled for title-less rows."""
    out = df.copy()
    if "series_title" not in out.columns:
        out["series_title"] = None
    blank = out["series_title"].map(_is_blank_title)
    if blank.any():
        out.loc[blank, "series_title"] = out.loc[blank].apply(
            lambda row: _synthesize_title(row.to_dict()), axis=1
        )
    return out


def _rank_by_recency(df):
    """Order rows so current series rank first and discontinued ones last.

    The catalog mixes live series (``end_year`` at the latest release) with
    long-discontinued ones; sorting by the most recent observation year (then
    period) surfaces what's actually being updated.
    """
    if "end_year" not in df.columns:
        return df
    from pandas import to_numeric

    out = df.assign(_recency=to_numeric(df["end_year"], errors="coerce").fillna(0))
    by = ["_recency"]
    ascending = [False]
    if "end_period" in out.columns:
        by.append("end_period")
        ascending.append(False)
    by.append("series_id")
    ascending.append(True)
    return out.sort_values(by=by, ascending=ascending, kind="stable").drop(
        columns="_recency"
    )


class BlsSearchQueryParams(SearchQueryParams):
    """BLS Search Query Parameters."""

    __json_schema_extra__ = {
        "category": {
            "multiple_items_allowed": False,
            "x-widget_config": {
                "options": [
                    {"label": name, "value": code}
                    for code, name in SURVEY_CATEGORY_NAMES.items()
                ],
            },
        },
        # Anchors cell-click grouping: clicking the symbol column sets this
        # param, which is shared by name with the Series widget's symbol param.
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": _SYMBOL_PARAM_CONFIG,
        },
    }

    symbol: str | None = Field(
        default=None,
        description="Bound to the Series widget via cell-click grouping; clicking"
        " a row's symbol loads it there. Does not filter the search results.",
    )

    category: SURVEY_CATEGORIES = Field(
        description=(
            "The category of BLS survey to search within. An empty search query"
            " returns every series within the category. Options are:\n"
            + "".join(
                f"\n    {code} - {name}" for code, name in SURVEY_CATEGORY_NAMES.items()
            )
        ),
    )
    include_extras: bool = Field(
        default=False,
        description="Include additional information in the search results."
        + " Extra fields returned are metadata and vary by survey."
        + " Fields are undefined strings that typically have names ending with '_code'.",
    )
    include_code_map: bool = Field(
        default=False,
        description="When True, includes the complete code map for eaçh survey in the category,"
        + " returned separately as a nested JSON to the `extras['results_metadata']` property of the response."
        + " Example content is the NAICS industry map for PPI surveys."
        + " Each code is a value within the 'symbol' of the time series.",
    )


class BlsSearchData(SearchData):
    """BLS Search Data."""

    __alias_dict__ = {
        "symbol": "series_id",
        "title": "series_title",
    }

    symbol: str = Field(
        description="BLS series identifier. Click a cell to load it into the"
        " linked BLS Series widget.",
        json_schema_extra={
            "x-widget_config": {
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupBy": {"paramName": "symbol"},
                },
            }
        },
    )


class BlsSearchFetcher(Fetcher[BlsSearchQueryParams, list[BlsSearchData]]):
    """BLS Search Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BlsSearchQueryParams:
        """Transform query parameters."""
        return BlsSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data."""
        from pandas import Series

        from openbb_bls.utils.metadata import BlsMetadata

        df = BlsMetadata().get_series(query.category)
        terms = [term.strip() for term in query.query.split(";")] if query.query else []

        if not terms:
            matches = df
        else:
            combined_mask = Series([True] * len(df), index=df.index)
            for term in terms:
                mask = df.apply(
                    lambda row, term=term: row.astype(str).str.contains(
                        term, case=False, regex=True, na=False
                    )
                ).any(axis=1)
                combined_mask &= mask
            matches = df[combined_mask]
            if matches.empty:
                raise EmptyDataError("No results found for the provided query.")

        # Fill in a readable title for series the catalog ships without one,
        # then rank current (still-updated) series above discontinued ones.
        matches = _fill_titles(matches)
        matches = _rank_by_recency(matches)

        if query.include_extras:
            return matches.to_dict(orient="records")
        return matches.filter(
            items=["series_id", "series_title", "survey_name"], axis=1
        ).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: BlsSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[BlsSearchData]]:
        """Transform the data."""
        from openbb_bls.utils.metadata import BlsMetadata

        metadata: dict = {}
        if query.include_code_map:
            metadata = BlsMetadata().get_codes(query.category)

        return AnnotatedResult(
            result=[BlsSearchData.model_validate(d) for d in data],
            metadata=metadata,
        )
