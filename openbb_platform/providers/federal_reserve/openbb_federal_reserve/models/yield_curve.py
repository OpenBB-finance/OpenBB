"""FederalReserve Yield Curve Model."""

# pylint: disable=unused-argument

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.yield_curve import (
    YieldCurveData,
    YieldCurveQueryParams,
)

if TYPE_CHECKING:
    from pandas import DataFrame  # pylint: disable=import-outside-toplevel

maturities = [
    "month_1",
    "month_3",
    "month_6",
    "year_1",
    "year_2",
    "year_3",
    "year_5",
    "year_7",
    "year_10",
    "year_20",
    "year_30",
]


class FederalReserveYieldCurveQueryParams(YieldCurveQueryParams):
    """FederalReserve Yield Curve Query."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}


class FederalReserveYieldCurveData(YieldCurveData):
    """FederalReserve Yield Curve Data."""


class FederalReserveYieldCurveFetcher(
    Fetcher[
        FederalReserveYieldCurveQueryParams,
        List[FederalReserveYieldCurveData],
    ]
):
    """FederalReserve Yield Curve Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FederalReserveYieldCurveQueryParams:
        """Transform the query params."""
        return FederalReserveYieldCurveQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveYieldCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> "DataFrame":
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        from io import BytesIO  # noqa
        from numpy import nan  # noqa
        from openbb_core.provider.utils.helpers import make_request  # noqa
        from pandas import read_csv  # noqa

        url = (
            "https://www.federalreserve.gov/datadownload/Output.aspx?"
            + "rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&"
            + "from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package"
        )
        r = make_request(url, **kwargs)
        df = read_csv(BytesIO(r.content), header=5, index_col=None, parse_dates=True)
        df.columns = ["date"] + maturities
        df = df.set_index("date").replace("ND", nan)

        return df.dropna(axis=0, how="all").reset_index()

    @staticmethod
    def transform_data(
        query: FederalReserveYieldCurveQueryParams, data: "DataFrame", **kwargs: Any
    ) -> List[FederalReserveYieldCurveData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import Categorical, DatetimeIndex

        df = data.copy()
        df.set_index("date", inplace=True)
        dates = query.date.split(",") if query.date else [df.index.max()]
        df.index = DatetimeIndex(df.index)
        dates_list = DatetimeIndex(dates)
        df.columns.name = "maturity"

        # Find the nearest date in the DataFrame to each date in dates_list
        nearest_dates = [df.index.asof(date) for date in dates_list]

        # Filter for only the nearest dates
        df = df[df.index.isin(nearest_dates)]

        df = df.fillna("N/A").replace("N/A", None)

        # Flatten the DataFrame
        flattened_data = df.reset_index().melt(
            id_vars="date", var_name="maturity", value_name="rate"
        )
        flattened_data = flattened_data.sort_values("date")
        flattened_data["maturity"] = Categorical(
            flattened_data["maturity"], categories=maturities, ordered=True
        )
        flattened_data["rate"] = flattened_data["rate"].astype(float) / 100
        flattened_data = flattened_data.sort_values(
            by=["date", "maturity"]
        ).reset_index(drop=True)
        flattened_data.loc[:, "date"] = flattened_data["date"].dt.strftime("%Y-%m-%d")
        records = flattened_data.to_dict(orient="records")

        return [FederalReserveYieldCurveData.model_validate(d) for d in records]
