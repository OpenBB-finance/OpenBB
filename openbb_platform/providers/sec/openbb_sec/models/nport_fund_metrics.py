"""SEC NPORT Fund Metrics Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

_PERCENT = {"x-unit_measurement": "percent", "x-frontend_multiply": 100}


class SecNportFundMetricsQueryParams(QueryParams):
    """SEC NPORT Fund Metrics Query.

    Source: https://www.sec.gov/Archives/edgar/data/
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "label": "Fund",
                "type": "endpoint",
                "optionsEndpoint": "/api/v1/sec/nport_funds",
                "style": {"popupWidth": 950},
            }
        },
        "date": {
            "x-widget_config": {
                "label": "Filing Period",
                "type": "endpoint",
                "optionsEndpoint": "/api/v1/sec/nport_periods",
                "optionsParams": {"symbol": "$symbol"},
            }
        },
        "year": {"x-widget_config": {"show": False}},
        "quarter": {"x-widget_config": {"show": False}},
    }

    symbol: str = Field(description="Fund ticker symbol (mutual fund or ETF).")
    date: dateType | None = Field(
        default=None,
        description="Specific filing period (period end date). Defaults to the latest.",
    )
    year: int | None = Field(
        default=None,
        description="Reporting year of the filing. Default is the most recent.",
    )
    quarter: int | None = Field(
        default=None,
        description="Reporting quarter of the filing. Default is the most recent.",
    )
    use_cache: bool = Field(
        default=True, description="Whether or not to use cache for the request."
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v):
        """Convert the symbol to uppercase."""
        return v.upper() if isinstance(v, str) else v


class SecNportFundMetricsData(Data):
    """SEC NPORT Fund Metrics Data."""

    period: dateType = Field(description="Month-end date the metrics apply to.")
    fund_name: str | None = Field(default=None, description="Name of the fund series.")
    total_return: float | None = Field(
        default=None,
        description="Monthly total return of the fund.",
        json_schema_extra=_PERCENT,
    )
    net_assets: float | None = Field(
        default=None, description="Net assets of the fund as of the reporting period."
    )
    total_assets: float | None = Field(
        default=None, description="Total assets of the fund as of the reporting period."
    )
    cash_and_equivalents: float | None = Field(
        default=None,
        description="Cash and cash equivalents not reported elsewhere.",
    )
    creation: float | None = Field(
        default=None, description="Total subscriptions (creations) during the month."
    )
    redemption: float | None = Field(
        default=None, description="Total redemptions during the month."
    )
    net_flow: float | None = Field(
        default=None, description="Net fund flow (creations minus redemptions)."
    )
    realized_gains: float | None = Field(
        default=None, description="Net realized gains during the month."
    )
    unrealized_gains: float | None = Field(
        default=None, description="Net unrealized appreciation during the month."
    )
    seven_day_gross_yield: float | None = Field(
        default=None,
        description="Seven-day gross yield (money market funds).",
        json_schema_extra=_PERCENT,
    )
    weighted_average_maturity: float | None = Field(
        default=None,
        description="Weighted average maturity in days (money market funds).",
    )
    weighted_average_life: float | None = Field(
        default=None,
        description="Weighted average life in days (money market funds).",
    )


class SecNportFundMetricsFetcher(
    Fetcher[SecNportFundMetricsQueryParams, list[SecNportFundMetricsData]]
):
    """SEC NPORT Fund Metrics Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecNportFundMetricsQueryParams:
        """Transform the query parameters."""
        return SecNportFundMetricsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecNportFundMetricsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the fund-level metadata from the resolved NPORT-P/N-MFP filing."""
        from openbb_core.provider.abstract.annotated_result import AnnotatedResult

        from openbb_sec.models.nport_disclosure import SecNportDisclosureFetcher

        result = await SecNportDisclosureFetcher().fetch_data(
            {
                "symbol": query.symbol,
                "date": query.date,
                "year": query.year,
                "quarter": query.quarter,
                "use_cache": query.use_cache,
            },
            credentials,
        )
        metadata = result.metadata if isinstance(result, AnnotatedResult) else {}
        return metadata or {}

    @staticmethod
    def transform_data(
        query: SecNportFundMetricsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[SecNportFundMetricsData]:
        """Reshape the metadata into a monthly performance/flow table."""

        def _f(value) -> float | None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        returns = data.get("returns") or {}
        flow = data.get("flow") or {}
        gains = data.get("gains") or {}
        months = sorted(set(returns) | set(flow) | set(gains), reverse=True)
        net_assets = _f(data.get("net_assets"))
        total_assets = _f(data.get("total_assets"))
        cash = _f(data.get("cash_and_equivalents"))

        if not months:
            period = data.get("period_ending")
            if not period:
                raise EmptyDataError("No fund metrics were found in the filing.")
            return [
                SecNportFundMetricsData.model_validate(
                    {
                        "period": period,
                        "fund_name": data.get("fund_name"),
                        "net_assets": net_assets,
                        "total_assets": total_assets,
                        "cash_and_equivalents": cash,
                        "seven_day_gross_yield": _f(data.get("seven_day_gross_yield")),
                        "weighted_average_maturity": _f(
                            data.get("weighted_average_maturity")
                        ),
                        "weighted_average_life": _f(data.get("weighted_average_life")),
                    }
                )
            ]

        results: list[SecNportFundMetricsData] = []
        for month in months:
            month_flow = flow.get(month) or {}
            month_gains = gains.get(month) or {}
            creation = _f(month_flow.get("creation"))
            redemption = _f(month_flow.get("redemption"))
            net_flow = (
                creation - redemption
                if creation is not None and redemption is not None
                else None
            )
            results.append(
                SecNportFundMetricsData.model_validate(
                    {
                        "period": month,
                        "fund_name": data.get("fund_name"),
                        "total_return": returns.get(month),
                        "net_assets": net_assets,
                        "total_assets": total_assets,
                        "cash_and_equivalents": cash,
                        "creation": creation,
                        "redemption": redemption,
                        "net_flow": net_flow,
                        "realized_gains": _f(month_gains.get("realized")),
                        "unrealized_gains": _f(month_gains.get("unrealized")),
                    }
                )
            )
        return results
