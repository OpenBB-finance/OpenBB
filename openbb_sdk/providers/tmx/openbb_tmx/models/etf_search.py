"""TMX ETF Search fetcher."""

from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import Field

from openbb_tmx.utils.helpers import COLUMNS_DICT, get_all_etfs


def search(query: str = "", **kwargs) -> pd.DataFrame:
    etfs = get_all_etfs()
    results = pd.DataFrame()

    if query:
        results = etfs[
            etfs["name"].str.contains(query, case=False)
            | etfs["short_name"].str.contains(query, case=False)
            | etfs["investment_style"].str.contains(query, case=False)
            | etfs["investment_objectives"].str.contains(query, case=False)
        ]
        results = results.set_index("symbol")

    if not query:
        results = etfs.set_index("symbol")

    results = results.reset_index().convert_dtypes()

    return results


class TmxEtfSearchQueryParams(EtfSearchQueryParams):
    """TMX ETF Search query.

    Source: https://www.tmx.com/
    """

    div_freq: Optional[Literal["monthly", "annually", "quarterly"]] = Field(
        description="The dividend payment frequency.", default=None
    )

    sort_by: Optional[
        Literal[
            "aum",
            "return_1m",
            "return_3m",
            "return_6m",
            "return_1y",
            "return_3y",
            "return_ytd",
            "beta_1y",
            "volume_avg_daily",
            "management_fee",
            "distribution_yield",
            "pb_ratio",
            "pe_ratio",
        ]
    ] = Field(description="The column to sort by.", default=None)


class TmxEtfSearchData(EtfSearchData):
    """TMX ETF Search Data."""

    aum: Optional[int | None] = Field(
        description="The value of the assets under management."
    )
    investment_style: Optional[str | None] = Field(
        description="The investment style of the ETF."
    )
    return_1m: Optional[float | None] = Field(description="The one-month return.")
    return_3m: Optional[float | None] = Field(description="The three-month return.")
    return_ytd: Optional[float | None] = Field(description="The year-to-date return.")
    close: Optional[float | None] = Field(description="The closing price.")
    prev_close: Optional[float | None] = Field(
        description="The previous closing price."
    )
    volume_avg_daily: Optional[int | None] = Field(
        description="The average daily volume."
    )
    management_fee: Optional[float | None] = Field(description="The management fee.")
    distribution_yield: Optional[float | None] = Field(
        description="The distribution yield."
    )
    dividend_frequency: Optional[str | None] = Field(
        description="The dividend payment frequency."
    )


class TmxEtfSearchFetcher(
    Fetcher[
        TmxEtfSearchQueryParams,
        List[TmxEtfSearchData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEtfSearchQueryParams:
        """Transform the query."""
        return TmxEtfSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxEtfSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        data = search(query.query)

        if query.div_freq:
            data = data[data["dividend_frequency"] == query.div_freq.capitalize()]

        if query.sort_by:
            data = data.sort_values(by=query.sort_by, ascending=False)

        return data.to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxEtfSearchData]:
        """Transform the data to the standard format."""
        return [TmxEtfSearchData.parse_obj(d) for d in data]
