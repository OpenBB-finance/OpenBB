"""Invesco ETF Search fetcher."""

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from openbb_invesco.utils.helpers import COUNTRIES, America
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import Field


class InvescoEtfSearchQueryParams(EtfSearchQueryParams):
    """Invesco ETF Search Query Params"""

    country: COUNTRIES = Field(
        description="The country the ETF is registered in.", default="america"
    )
    div_freq: Optional[Literal["monthly", "annually", "quarterly"]] = Field(
        description="The dividend payment frequency.", default=None
    )
    options: Optional[Literal["True", "False"]] = Field(
        description="Does the fund trade options?", default=None
    )
    short: Optional[Literal["True", "False"]] = Field(
        description="Is the fund shortable?", default=None
    )


class InvescoEtfSearchData(EtfSearchData):
    """Invesco ETF Search Data."""

    symbol: str = Field(description="The ticker symbol of the asset.", alias="Ticker")
    name: str = Field(description="The name of the fund.", alias="Name")
    inception_date: Optional[dateType] = Field(
        description="The inception date of the fund.",
        alias="Inception_Date",
        default=None,
    )
    index_ticker: Optional[str] = Field(
        description="The ticker symbol of the tracking index.",
        alias="Index_Ticker",
        default=None,
    )
    iiv_ticker: Optional[str] = Field(
        description="The intraday indicative value ticker.",
        alias="IIV_Ticker",
        default=None,
    )
    cusip: Optional[str] = Field(
        description="The CUSIP of the fund.", alias="CUSIP", default=None
    )
    isin: Optional[str] = Field(
        description="The ISIN of the fund.", alias="ISIN", default=None
    )
    exchange: Optional[str] = Field(
        description="The primary exchange where the fund is listed.",
        alias="Exchange",
        default=None,
    )
    distribution_yield: Optional[float] = Field(
        description="The distribution yield of the fund.",
        alias="Distribution_Yield",
        default=None,
    )
    sec_yield: Optional[float] = Field(
        description="The SEC yield of the fund.", alias="Day_SEC_Yield", default=None
    )
    ttm_yield: Optional[float] = Field(
        description="The TTM yield of the fund.",
        alias="Twelve_Month_Yield",
        default=None,
    )
    distribution_frequency: Optional[str] = Field(
        description="The distribution frequency of the fund.",
        alias="Distribution_Frequency",
        default=None,
    )
    marginable: Optional[str] = Field(
        description="Is the fund marginable?", alias="Marginable", default=None
    )
    short: Optional[str] = Field(
        description="Is the fund shortable?", alias="Short", default=None
    )
    options: Optional[str] = Field(
        description="Is the fund optionable?", alias="Options", default=None
    )


class InvescoEtfSearchFetcher(
    Fetcher[
        InvescoEtfSearchQueryParams,
        List[InvescoEtfSearchData],
    ]
):
    """Transform the query, extract and transform the data from the Invesco endpoint."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> InvescoEtfSearchQueryParams:
        """Transform the query."""
        return InvescoEtfSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: InvescoEtfSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Invesco endpoint."""

        etfs = pd.DataFrame()
        results = pd.DataFrame()

        if query.country == "america":
            etfs = America.get_all_etfs()

        results = etfs[
            etfs["Name"].str.contains(query.query, case=False)  # type: ignore
            | etfs["Ticker"].str.contains(query.query, case=False)  # type: ignore
            | etfs["Exchange"].str.contains(query.query, case=False)  # type: ignore
            | etfs["Index_Ticker"].str.contains(query.query, case=False)  # type: ignore
            | etfs["IIV_Ticker"].str.contains(query.query, case=False)  # type: ignore
        ]

        if query.div_freq:
            results = results[
                results["Distribution_Frequency"] == query.div_freq.capitalize()
            ]

        if query.options:
            results = results[results["Options"] == query.options]

        if query.short:
            results = results[results["Short"] == query.short]

        results = results.drop(columns=["Date"]).sort_values(
            by="Twelve_Month_Yield", ascending=False
        )

        return results.to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict], **kwargs: Any) -> List[InvescoEtfSearchData]:
        """Transform the data."""
        return [InvescoEtfSearchData.model_validate(d) for d in data]
