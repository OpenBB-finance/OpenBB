"""TMX ETF Holdings fetcher."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from pydantic import Field, field_validator


class TmxEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """TMX ETF Holdings query.

    Source: https://www.tmx.com/
    """

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily."
        + " To bypass, set to False. If True, the data will be cached for 4 hours.",
    )


class TmxEtfHoldingsData(EtfHoldingsData):
    """TMX ETF Holdings Data."""

    __alias_dict__ = {
        "shares": "number_of_shares",
    }

    symbol: str | None = Field(
        description="The ticker symbol of the asset.", default=None
    )
    name: str | None = Field(description="The name of the asset.", default=None)
    weight: float | None = Field(
        description="The weight of the asset in the portfolio, as a normalized percentage.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    shares: int | str | None = Field(
        description="The value of the assets under management.",
        default=None,
    )
    market_value: float | str | None = Field(
        description="The market value of the holding.", default=None
    )
    currency: str | None = Field(
        default=None, description="The currency of the holding."
    )
    share_percentage: float | None = Field(
        description="The share percentage of the holding, as a normalized percentage.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    share_change: float | str | None = Field(
        description="The change in shares of the holding.", default=None
    )
    country: str | None = Field(description="The country of the holding.", default=None)
    exchange: str | None = Field(
        description="The exchange code of the holding.", default=None
    )
    type_id: str | None = Field(
        description="The holding type ID of the asset.", default=None
    )
    fund_id: str | None = Field(description="The fund ID of the asset.", default=None)

    @field_validator("share_percentage", "weight", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None


class TmxEtfHoldingsFetcher(
    Fetcher[
        TmxEtfHoldingsQueryParams,
        list[TmxEtfHoldingsData],
    ]
):
    """TMX ETF Holdings Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEtfHoldingsQueryParams:
        """Transform the query."""
        params["symbol"] = (
            params["symbol"].replace(".TO", "").replace(".TSX", "").replace("-", ".")
        )
        return TmxEtfHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEtfHoldingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_tmx.utils.helpers import get_all_etfs
        from pandas import DataFrame

        query.symbol = query.symbol.upper()
        results = []
        etf = DataFrame()
        etfs = DataFrame(await get_all_etfs(use_cache=query.use_cache))
        etf = etfs[etfs["symbol"] == query.symbol]

        if len(etf) == 1:
            top_holdings = DataFrame(etf["holdings_top10"].iloc[0])
            top_holdings = top_holdings.dropna(axis=1, how="all")
            _columns = {
                "numberofshares": "number_of_shares",
                "symbol": "symbol",
                "country": "country",
                "fundid": "fund_id",
                "excode": "exchange",
                "securityname": "name",
                "currency": "currency",
                "marketvalue": "market_value",
                "detailholdingtypeid": "type_id",
                "weighting": "weight",
                "sharepercentage": "share_percentage",
                "sharechange": "share_change",
                "shareChange": "share_change",
            }
            top_holdings.rename(columns=_columns, inplace=True)
            results = (
                top_holdings.fillna("N/A")
                .replace("NA", None)
                .replace("N/A", None)
                .to_dict("records")
            )

        return results

    @staticmethod
    def transform_data(
        query: TmxEtfHoldingsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEtfHoldingsData]:
        """Transform the data to the standard format."""
        return [TmxEtfHoldingsData.model_validate(d) for d in data]
