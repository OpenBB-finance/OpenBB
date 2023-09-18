"""CFTC Commitment of Traders Reports fetcher."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
import quandl
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.helpers import to_snake_case
from openbb_quandl.utils.series_ids import CFTC
from pydantic import Field, validator


class QuandlCotQueryParams(QueryParams):
    """Get CFTC Commitment of Traders Report.

    Source: https://data.nasdaq.com/data/CFTC-commodity-futures-trading-commission-reports/documentation

    Not all combinations of parameters and underlying assets are valid, bad combinations will return an error.
    """

    code: str = Field(
        description="""
            CFTC series code.  Use search_cot() to find the code.
            Codes not listed in the curated list, but are published by on the Nasdaq Data Link website, are valid.
            Certain symbols, such as "ES=F", or exact names are also valid.
            Default report is: S&P 500 Consolidated (CME))
            """,
        default="13874P",
    )
    data_type: Optional[Literal["F", "FO", "CITS"]] = Field(
        description="""
            The type of data to reuturn. Default is "FO".

            F = Futures only

            FO = Futures and Options

            CITS = Commodity Index Trader Supplemental. Only valid for commodities.
        """,
        default="FO",
    )
    legacy_format: Optional[bool] = Field(
        description="Returns the legacy format of report. Default is False.",
        default=False,
    )
    report_type: Optional[Literal["ALL", "CHG", "OLD", "OTR"]] = Field(
        description="""
            The type of report to return. Default is "ALL".

                ALL = All

                CHG = Change in Positions

                OLD = Old Crop Years

                OTR = Other Crop Years
        """,
        default="ALL",
    )
    measure: Optional[Literal["CR", "NT", "OI", "CHG"]] = Field(
        description="""
            The measure to return. Default is None.

            CR = Concentration Ratios

            NT = Number of Traders

            OI = Percent of Open Interest

            CHG = Change in Positions. Only valid when data_type is "CITS".
        """,
        default=None,
    )
    start_date: Optional[dateType] = Field(
        description="The start date of the time series. Defaults to all.", default=None
    )
    end_date: Optional[dateType] = Field(
        description="The end date of the time series. Defaults to the most recent data.",
        default=None,
    )
    transform: Optional[Literal["diff", "rdiff", "cumul", "normalize"]] = Field(
        description="Transform the data as w/w difference, percent change, cumulative, or normalize.",
        default=None,
    )


class QuandlCotData(Data):
    """Quandl CFTC Commitment of Traders Reports data.

    Returns
    -------
    List[Dict]
        Columns in the response object will change according to the parameters and underlying asset.
    """

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""

        return datetime.strptime(v, "%Y-%m-%d").date()


class QuandlCotFetcher(Fetcher[QuandlCotQueryParams, List[QuandlCotData]]):
    """Quandl CFTC Commitment of Traders Reports Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> QuandlCotQueryParams:
        return QuandlCotQueryParams(**params)

    @staticmethod
    def extract_data(
        query: QuandlCotQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        api_key = credentials.get("quandl_api_key") if credentials else ""

        # The "code" can be an exact name, a symbol, or a CFTC series code.
        series_id: str = ""
        series_ids = pd.DataFrame(CFTC).transpose().reset_index(drop=True)
        series_ids.columns = series_ids.columns.str.lower()

        if query.code in series_ids["code"].values:
            series_id = query.code

        if query.code not in series_ids["code"].values:
            if query.code in series_ids["symbol"].values:
                series_id = series_ids.loc[
                    series_ids["symbol"] == query.code, "code"
                ].values[0]
            if query.code in series_ids["name"].values:
                series_id = series_ids.loc[
                    series_ids["name"] == query.code, "code"
                ].values[0]
            # Allows for strings not found in the curated list.
            if (
                query.code not in series_ids["code"].values
                and query.code not in series_ids["symbol"].values
                and query.code not in series_ids["name"].values
            ):
                series_id = query.code

        # The "quandl_code" gets parsed conditionally for the parameters.
        quandl_code = f"CFTC/{series_id}"

        if query.data_type:
            quandl_code = f"{quandl_code}_{query.data_type}"

        if query.legacy_format is False and query.data_type != "CITS":
            quandl_code = f"{quandl_code}_L"

        if query.report_type:
            quandl_code = f"{quandl_code}_{query.report_type}"

        if query.measure is not None:
            quandl_code = f"{quandl_code}_{query.measure}"

        try:
            data = quandl.get(
                quandl_code,
                start_date=query.start_date,
                end_date=query.end_date,
                transform=query.transform,
                api_key=api_key,
            ).reset_index()
            data.columns = [
                to_snake_case(c)
                .replace(" ", "")
                .replace("-", "")
                .replace("%", "_%_")
                .replace("o_i", "oi")
                .replace(";", "")
                for c in data.columns
            ]
            data["date"] = data["date"].astype(str)
            return data.to_dict("records")

        except Exception as e:
            raise RuntimeError(e)

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[QuandlCotData]:
        return [QuandlCotData.parse_obj(d) for d in data]
