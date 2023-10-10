"""BMO ETF Info fetcher."""
import concurrent.futures
from datetime import date as dateType
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_bmo.utils.helpers import get_fund_properties
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from pydantic import Field


class BmoEtfInfoQueryParams(EtfInfoQueryParams):
    """BMO ETF Info query.

    Source: https://www.bmogam.com/
    """

    use_cache: bool = Field(
        description="Whether to cache the request. Defaults to True.",
        default=True,
    )


class BmoEtfInfoData(EtfInfoData):
    """Bmo ETF Info Data."""

    __alias_dict__ = {
        "date": "as_of_date",
        "name": "fund_name",
        "symbol": "ticker",
        "inception_date": "date_started",
    }
    currency: Optional[str] = Field(
        description="The base currency of the fund.",
        alias="base_currency",
        default=None,
    )
    region: Optional[str] = Field(
        description="The target region of the fund.", alias="region", default=None
    )
    asset_class: Optional[str] = Field(
        description="The asset class of the fund.", alias="fund_class", default=None
    )
    sub_asset_class: Optional[str] = Field(
        description="The sub asset class of the fund.",
        alias="sub_asset_class",
        default=None,
    )
    strategy: Optional[str] = Field(
        description="The strategy of the fund.", alias="strategy", default=None
    )
    objective: Optional[str] = Field(
        description="The investment objective of the fund.",
        alias="objective",
        default=None,
    )
    structure: Optional[str] = Field(
        description="The structure of the fund.", alias="structure", default=None
    )
    index_name: Optional[str] = Field(
        description="The name of tracking index.", alias="index_name", default=None
    )
    index_inception_date: Optional[dateType] = Field(
        description="The inception date of tracking index.",
        alias="index_inception_date",
        default=None,
    )
    number_of_securites: Optional[int] = Field(
        description="The number of securities in the fund.",
        alias="number_of_securities",
        default=None,
    )
    beta: Optional[float] = Field(
        description="The beta of the fund with respect to its benchmark.",
        alias="beta",
        default=None,
    )
    price: Optional[float] = Field(
        description="The market price of the fund.", alias="market_price", default=None
    )
    volume: Optional[int] = Field(
        description="The market volume of the fund.",
        alias="market_volume",
        default=None,
    )
    market_cap: Optional[float] = Field(
        description="The market cap of the fund, in billions.",
        alias="market_cap_billion",
        default=None,
    )
    nav: Optional[float] = Field(
        description="The net asset value of the fund.",
        alias="net_asset_value",
        default=None,
    )
    net_assets: Optional[float] = Field(
        description="The net assets of the fund.",
        alias="net_assets",
        default=None,
    )
    management_fee: Optional[float] = Field(
        description="The management fee of the fund.",
        alias="management_fee",
        default=None,
    )
    mer: Optional[float] = Field(
        description="The management expense ratio of the fund.",
        alias="management_expense_ratio",
        default=None,
    )
    pe: Optional[float] = Field(
        description="The price to earnings ratio of the fund.",
        alias="price_earning_ratio",
        default=None,
    )
    pb: Optional[float] = Field(
        description="The price to book ratio of the fund.",
        alias="price_book_ratio",
        default=None,
    )
    roc: Optional[float] = Field(
        description="The return on capital of the fund.",
        alias="return_of_capital",
        default=None,
    )
    income_frequency: Optional[str] = Field(
        description="The frequency of income distributions.",
    )
    distribution_yield: Optional[float] = Field(
        description="The distribution yield of the fund.",
        alias="ann_dist_yield_pct",
    )
    weight_avg_coupon: Optional[float] = Field(
        description="The weighted average coupon of the fund.",
        alias="weight_avg_coupon",
        default=None,
    )
    weight_avg_current_yield: Optional[float] = Field(
        description="The weighted average current yield of the fund.",
        alias="weight_avg_current_yield",
        default=None,
    )
    weight_avg_duration: Optional[float] = Field(
        description="The weighted average duration of the fund.",
        alias="weight_avg_duration",
        default=None,
    )
    weight_avg_maturity: Optional[float] = Field(
        description="The weighted average term-maturity of the fund.",
        alias="weight_avg_term_maturity",
    )
    weight_avg_ytm: Optional[float] = Field(
        description="The weighted average yield-to-maturity of the fund.",
        alias="weight_avg_yield_to_maturity",
        default=None,
    )


class BmoEtfInfoFetcher(
    Fetcher[
        BmoEtfInfoQueryParams,
        List[BmoEtfInfoData],
    ]
):
    """Transform the query, extract and transform the data from the BMO endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BmoEtfInfoQueryParams:
        """Transform the query."""
        return BmoEtfInfoQueryParams(**params)

    @staticmethod
    def get_properties(symbol: str, use_cache: bool = True, **kwargs) -> List[Dict]:
        """Helper to get the fund properties."""

        symbol = symbol.replace(".TO", "").replace(".TSX", "").replace("-", ".")  # noqa
        _properties = pd.DataFrame()
        _price = pd.DataFrame()
        _profile = pd.DataFrame()
        _distribution = pd.DataFrame()
        data = get_fund_properties(symbol, use_cache, **kwargs)

        # Positional values for each response may be different, so we need to find the correct item in the list.
        if isinstance(data, List) and len(data) == 1 and "properties_pub" in data[0]:
            _info = pd.DataFrame(data[0]["properties_pub"])
            _properties = (
                pd.concat([_properties, _info])
                .transpose()
                .rename(columns={"value": symbol})
            )

        if isinstance(data, List) and len(data) == 1 and "statistics" in data[0]:
            key = -1
            for i in range(0, len(data[0]["statistics"])):
                if data[0]["statistics"][i]["code"] == "price":
                    key = i
            if key != -1:
                _price = pd.DataFrame(data[0]["statistics"][key]["values"])
                _price = (
                    _price.drop(columns=["as_of_date", "value", "label"])
                    .transpose()
                    .rename(columns={0: symbol})
                )
                _properties = pd.concat([_properties, _price], axis=0)
            # Reset the loop for the next property to parse.
            key = -1
            for i in range(0, len(data[0]["statistics"])):
                if data[0]["statistics"][i]["code"] == "fund_profile_characteristics":
                    key = i
            if key != -1:
                _profile = pd.DataFrame(data[0]["statistics"][key]["values"])
                _profile = (
                    (
                        _profile.drop(
                            columns=[
                                "as_of_date",
                                "value",
                                "label",
                                "shares_outstanding",
                                "net_assets_mm",
                            ]
                        )
                    )
                    .transpose()
                    .rename(columns={0: symbol})
                )
                _properties = pd.concat([_properties, _profile], axis=0)

            key = -1
            for i in range(0, len(data[0]["statistics"])):
                if data[0]["statistics"][i]["code"] == "fund_annual_distribution":
                    key = i
            if key != -1:
                _distribution = pd.DataFrame(data[0]["statistics"][key]["values"])
                _distribution = (
                    (_distribution.drop(columns=["value", "label"]))
                    .transpose()
                    .rename(columns={0: symbol})
                )
                _properties = pd.concat([_properties, _distribution], axis=0)

            # Force list items to a string.
            for item in [
                "asset_class",
                "region",
                "sub_asset_class",
                "strategy",
                "structure",
            ]:
                if item in _properties.index:
                    _properties.loc[item] = (
                        _properties.loc[item]
                        .astype(str)
                        .str.replace("[", "")
                        .str.replace("]", "")
                        .str.replace("'", "")
                        .str.replace(", ", ",")
                        .fillna(value="-")
                        .replace("-", None)
                    )

        return _properties.transpose().to_dict("records")

    @staticmethod
    def extract_data(
        query: BmoEtfInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the BMO endpoint."""

        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        results = []
        output = pd.DataFrame()

        def get_one(symbol):
            _data = BmoEtfInfoFetcher.get_properties(
                symbol, use_cache=query.use_cache, **kwargs
            )
            if len(_data) == 1:
                results.extend(_data)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_one, symbols)

        if results != []:
            output = (
                pd.DataFrame.from_records(results)
                .set_index("ticker")
                .sort_values(by="market_cap_billion", ascending=False)
            )
            # Replace stray NaN values in fields.
            for column in ["structure", "index_inception_date"]:
                if column in output.columns:
                    output[column] = output[column].fillna(value="-").replace("-", None)

        return output.reset_index().to_dict("records")

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[BmoEtfInfoData]:
        """Transform the data."""
        return [BmoEtfInfoData.model_validate(d) for d in data]
