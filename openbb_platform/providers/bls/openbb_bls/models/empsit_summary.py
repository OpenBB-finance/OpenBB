"""BLS Employment Situation Summary Tables A and B."""

from __future__ import annotations

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_bls.utils.empsit_summary import SUMMARY_SPECS, fetch_and_parse

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}
_CATEGORY: dict[str, Any] = {"x-widget_config": {"chartDataType": "category"}}


def _num(header: str, change: bool = False) -> dict[str, Any]:
    """Numeric value column config; ``change`` columns render green/red."""
    cfg: dict[str, Any] = {"headerName": header, "cellDataType": "number"}
    if change:
        cfg["renderFn"] = "greenRed"
    return {"x-widget_config": cfg}


def empsit_summary_model_name(key: str) -> str:
    """Stable model/widget name for a summary table key (``a`` / ``b``)."""
    return f"BlsEmpsitSummary{key.upper()}"


def _widget(label: str) -> dict[str, Any]:
    """Table widget config for one summary table."""
    return {
        "x-widget_config": {
            "$.name": f"BLS Employment Situation — {label}",
            "$.description": (
                f"{label}. Months run oldest to latest; labels shift each release."
            ),
            "$.gridData": {"w": 40, "h": 24},
            "$.refetchInterval": False,
            "$.source": ["BLS"],
            "$.category": "Economy",
            "$.subCategory": "Employment Situation",
            "table": {"showAll": True, "enableCharts": True},
        }
    }


class _EmpsitSummaryQueryParams(QueryParams):
    """Query params for an Employment Situation summary table (latest release)."""


class _EmpsitSummaryBaseData(Data):
    """Shared fields for an Employment Situation summary-table row."""

    model_config = ConfigDict(extra="ignore")

    section: str | None = Field(
        default=None,
        description="Section heading the row falls under.",
        json_schema_extra=_CATEGORY,
    )
    category: str = Field(
        description="Row category / metric.",
        json_schema_extra=_CATEGORY,
    )
    year_ago: float | None = Field(
        default=None,
        description="Value for the same month a year ago.",
        json_schema_extra=_num("Year Ago"),
    )
    two_months_prior: float | None = Field(
        default=None,
        description="Value two months before the latest.",
        json_schema_extra=_num("2 Months Prior"),
    )
    prior_month: float | None = Field(
        default=None,
        description="Value for the month before the latest.",
        json_schema_extra=_num("Prior Month"),
    )
    latest: float | None = Field(
        default=None,
        description="Value for the latest (most recent) month.",
        json_schema_extra=_num("Latest"),
    )
    table_id: str = Field(description="Source table id.", json_schema_extra=_HIDE)


def _make_summary_model(key: str) -> type[Data]:
    """Build the typed Data model for summary table ``key``."""
    spec = SUMMARY_SPECS[key]
    fields: dict[str, Any] = {}
    if spec["has_change"]:
        fields["change_1_month"] = (
            float | None,
            Field(
                default=None,
                description="Over-the-month change (prior month to latest).",
                json_schema_extra=_num("1-Month Change", change=True),
            ),
        )
    from pydantic import create_model

    model = create_model(  # type: ignore[call-overload]
        f"BlsEmpsitSummary{key.upper()}Data",
        __base__=_EmpsitSummaryBaseData,
        **fields,
    )
    model.model_config["json_schema_extra"] = _widget(spec["label"])
    return model


def _make_fetcher(key: str, data_class: type[Data]) -> type[Fetcher]:
    """Build the Fetcher bound to one summary table."""

    class _Fetcher(Fetcher[_EmpsitSummaryQueryParams, list[Data]]):
        """BLS Employment Situation summary-table fetcher."""

        require_credentials = False
        data_type = data_class

        @staticmethod
        def transform_query(params: dict[str, Any]) -> _EmpsitSummaryQueryParams:
            """Validate and coerce the (empty) query."""
            return _EmpsitSummaryQueryParams(**params)

        @staticmethod
        def extract_data(
            query: _EmpsitSummaryQueryParams,
            credentials: dict[str, str] | None,
            **kwargs: Any,
        ) -> list[dict[str, Any]]:
            """Scrape and parse the bound summary table for the latest release."""
            parsed = fetch_and_parse(key)
            table_id = parsed["table_id"]
            return [{**row, "table_id": table_id} for row in parsed["rows"]]

        @staticmethod
        def transform_data(
            query: _EmpsitSummaryQueryParams,
            data: list[dict[str, Any]],
            **kwargs: Any,
        ) -> list[Data]:
            """Coerce parsed rows into the table-specific Data model."""
            if not data:
                raise EmptyDataError(
                    f"No rows parsed from Employment Situation summary table '{key}'."
                )
            return [data_class.model_validate(r) for r in data]

    _Fetcher.__name__ = f"BlsEmpsitSummary{key.upper()}Fetcher"
    _Fetcher.__qualname__ = _Fetcher.__name__
    return _Fetcher


EMPSIT_SUMMARY_FETCHERS: dict[str, type[Fetcher]] = {}
for _key in SUMMARY_SPECS:
    _model = _make_summary_model(_key)
    EMPSIT_SUMMARY_FETCHERS[empsit_summary_model_name(_key)] = _make_fetcher(
        _key, _model
    )
