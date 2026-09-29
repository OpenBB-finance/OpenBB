"""Federal Reserve Bank of San Francisco Daily News Sentiment Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.frbsf.org/wp-content/uploads/news_sentiment_data.xlsx"


class FederalReserveSanFranciscoNewsSentimentQueryParams(QueryParams):
    """San Francisco Fed Daily News Sentiment Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveSanFranciscoNewsSentimentData(Data):
    """San Francisco Fed Daily News Sentiment Index Data."""

    date: dateType = Field(description="The observation date.")
    news_sentiment: float | None = Field(
        default=None, description="The Daily News Sentiment Index value."
    )


class FederalReserveSanFranciscoNewsSentimentFetcher(
    Fetcher[
        FederalReserveSanFranciscoNewsSentimentQueryParams,
        list[FederalReserveSanFranciscoNewsSentimentData],
    ]
):
    """San Francisco Fed Daily News Sentiment Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveSanFranciscoNewsSentimentQueryParams:
        """Transform the query params."""
        return FederalReserveSanFranciscoNewsSentimentQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSanFranciscoNewsSentimentQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the News Sentiment workbook from the San Francisco Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw News Sentiment workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "san_francisco_news_sentiment",
            lambda: seconds_until_next_release("daily"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveSanFranciscoNewsSentimentQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveSanFranciscoNewsSentimentData]:
        """Parse the News Sentiment sheet and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(
            BytesIO(data[0]["_raw"]), engine="openpyxl", sheet_name="Data"
        )
        frame = frame.rename(columns={"News Sentiment": "news_sentiment"})
        frame = frame[["date", "news_sentiment"]]
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveSanFranciscoNewsSentimentData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
