"""FRED Series Model."""

from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_indices import (
    FredIndicesData,
    FredIndicesQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import async_make_request, get_querystring
from pydantic import Field


class FredSeriesQueryParams(FredIndicesQueryParams):
    """FRED Series Query Params."""

    __alias_dict__ = {
        "symbol": "series_id",
        "start_date": "observation_start",
        "end_date": "observation_end",
        "transform": "units",
    }
    frequency: Literal[
        None,
        "a",
        "q",
        "m",
        "w",
        "d",
        "wef",
        "weth",
        "wew",
        "wetu",
        "wem",
        "wesu",
        "wesa",
        "bwew",
        "bwem",
    ] = Field(
        default=None,
        description="""
        Frequency aggregation to convert high frequency data to lower frequency.
            None = No change
            a = Annual
            q = Quarterly
            m = Monthly
            w = Weekly
            d = Daily
            wef = Weekly, Ending Friday
            weth = Weekly, Ending Thursday
            wew = Weekly, Ending Wednesday
            wetu = Weekly, Ending Tuesday
            wem = Weekly, Ending Monday
            wesu = Weekly, Ending Sunday
            wesa = Weekly, Ending Saturday
            bwew = Biweekly, Ending Wednesday
            bwem = Biweekly, Ending Monday
        """,
    )
    aggregation_method: Literal[None, "avg", "sum", "eop"] = Field(
        default="eop",
        description="""
        A key that indicates the aggregation method used for frequency aggregation.
        This parameter has no affect if the frequency parameter is not set.
            avg = Average
            sum = Sum
            eop = End of Period
        """,
    )
    transform: Literal[
        None, "chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"
    ] = Field(
        default=None,
        description="""
        Transformation type
            None = No transformation
            chg = Change
            ch1 = Change from Year Ago
            pch = Percent Change
            pc1 = Percent Change from Year Ago
            pca = Compounded Annual Rate of Change
            cch = Continuously Compounded Rate of Change
            cca = Continuously Compounded Annual Rate of Change
            log = Natural Log
        """,
    )
    limit: int = Field(description=QUERY_DESCRIPTIONS.get("limit", ""), default=100000)


class FredSeriesData(FredIndicesData):
    """FRED Series Data."""


class FredSeriesFetcher(
    Fetcher[
        FredSeriesQueryParams,
        List[FredSeriesData],
    ]
):
    """FRED Series Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredSeriesQueryParams:
        """Transform query."""
        return FredSeriesQueryParams(**params)

    @staticmethod
    async def extract_data(
        query: FredSeriesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""

        api_key = credentials.get("fred_api_key") if credentials else ""
        base_url = "https://api.stlouisfed.org/fred/series/observations?"
        querystring = get_querystring(query.model_dump(), ["series_id"])
        results = {}
        series_ids = query.symbol.split(",") if "," in query.symbol else [query.symbol]

        urls = []
        for series_id in series_ids:
            url = (
                base_url
                + f"series_id={series_id}&"
                + querystring
                + f"&file_type=json&api_key={api_key}"
            )
            urls.append(url)

        async def async_get_fred_data(url, series_id, **kwargs):
            response = await async_make_request(url, timeout=5, **kwargs)

            data = response.get("observations")
            try:
                [d.pop("realtime_start") for d in data]
                [d.pop("realtime_end") for d in data]
                data = (
                    pd.DataFrame(data)
                    .replace(".", None)
                    .set_index("date")["value"]
                    .astype(float)
                    .dropna()
                    .to_dict()
                )
            except KeyError:
                data = {}
            except TypeError:
                data = {}
            if data != {}:
                results.update({series_id: data})
            return results

        for i in range(0, len(series_ids)):
            await async_get_fred_data(urls[i], series_ids[i], **kwargs)

        return results

    @staticmethod
    def transform_data(
        query: FredSeriesQueryParams, data: Dict, **kwargs: Any
    ) -> List[FredSeriesData]:
        """Transform data."""
        results = (
            pd.DataFrame(data)
            .reset_index()
            .rename(columns={"index": "date"})
            .to_dict("records")
        )
        return [FredSeriesData.model_validate(d) for d in results]
