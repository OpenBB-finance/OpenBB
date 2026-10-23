"""BLS Wholesale & Retail Trade Productivity chart data (per-chart tables)."""

from __future__ import annotations

from openbb_core.provider.abstract.fetcher import Fetcher

from openbb_bls.models.charts_common import build_chart_pack
from openbb_bls.utils.wholesale_retail_charts import CHART_SPECS, fetch_and_parse


def wholesale_retail_model_name(chart_key: str) -> str:
    """Stable widget/model name for one wholesale/retail productivity chart key."""
    return "Bls" + "".join(p.capitalize() for p in chart_key.split("-"))


WHOLESALE_RETAIL_CHART_FETCHERS: dict[str, type[Fetcher]] = build_chart_pack(
    specs=CHART_SPECS,
    fetch_and_parse=fetch_and_parse,
    model_name_fn=wholesale_retail_model_name,
    model_id_prefix="BlsWr",
    widget_name_prefix="BLS Wholesale & Retail Trade Productivity",
    subcategory="Productivity by Industry",
    pack_label="Wholesale & Retail Trade Productivity",
    period_header="Year",
)
