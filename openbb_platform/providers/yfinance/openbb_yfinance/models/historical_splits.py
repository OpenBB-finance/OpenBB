"""YFinance Historical Splits Model."""

# pylint: disable=unused-argument
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_splits import (
    HistoricalSplitsData,
    HistoricalSplitsQueryParams,
)


class YFinanceHistoricalSplitsQueryParams(HistoricalSplitsQueryParams):
    """YFinance Historical Splits Query."""


class YFinanceHistoricalSplitsData(HistoricalSplitsData):
    """YFinance Historical Splits Data."""

    __alias_dict__ = {
        "date": "Date",
    }


class YFinanceHistoricalSplitsFetcher(
    Fetcher[YFinanceHistoricalSplitsQueryParams, list[YFinanceHistoricalSplitsData]]
):
    """YFinance Historical Splits Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> YFinanceHistoricalSplitsQueryParams:
        """Transform the query."""
        return YFinanceHistoricalSplitsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceHistoricalSplitsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the raw data from YFinance."""
        # pylint: disable=import-outside-toplevel
        from yfinance import Ticker

        try:
            splits_series = Ticker(query.symbol).get_splits()
            if isinstance(splits_series, list) and not splits_series or splits_series.empty:  # type: ignore
                raise OpenBBError(f"No split data found for {query.symbol}")
        except Exception as e:
            raise OpenBBError(f"Error getting data for {query.symbol}: {e}") from e

        df = splits_series.reset_index()  # type: ignore
        df.columns = ["date", "numerator"]  # type: ignore
        df["date"] = df.date.apply(lambda x: x.date()).astype(str)  # type: ignore
        df["split_ratio"] = df["numerator"].astype(str)  # type: ignore
        df["denominator"] = 1.0
        splits = df[["date", "numerator", "denominator", "split_ratio"]].to_dict("records")  # type: ignore

        return splits

    @staticmethod
    def transform_data(
        query: YFinanceHistoricalSplitsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceHistoricalSplitsData]:
        """Transform the data."""
        return [YFinanceHistoricalSplitsData.model_validate(d) for d in data]
