"""FederalReserve Money Measures Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.money_measures import (
    MoneyMeasuresData,
    MoneyMeasuresQueryParams,
)
from pydantic import Field

titles = {
    "M1": "m1",
    "M2": "m2",
    "MCU": "currency",
    "MDD": "demand_deposits",
    "MMFGB": "retail_money_market_funds",
    "MDL": "other_liquid_deposits",
    "MDTS": "small_denomination_time_deposits",
}


class FederalReserveMoneyMeasuresQueryParams(MoneyMeasuresQueryParams):
    """FederalReserve Money Measures Query."""


class FederalReserveMoneyMeasuresData(MoneyMeasuresData):
    """FederalReserve Money Measures Data."""

    m1: float = Field(
        description="Value of the M1 money supply in dollars.",
    )
    m2: float = Field(
        description="Value of the M2 money supply in dollars.",
    )
    currency: float | None = Field(
        description="Value of currency in circulation in dollars.",
        default=None,
    )
    demand_deposits: float | None = Field(
        description="Value of demand deposits in dollars.",
        default=None,
    )
    retail_money_market_funds: float | None = Field(
        description="Value of retail money market funds in dollars.",
        default=None,
    )
    other_liquid_deposits: float | None = Field(
        description="Value of other liquid deposits in dollars.",
        default=None,
    )
    small_denomination_time_deposits: float | None = Field(
        description="Value of small denomination time deposits in dollars.",
        default=None,
    )


class FederalReserveMoneyMeasuresFetcher(
    Fetcher[
        FederalReserveMoneyMeasuresQueryParams,
        list[FederalReserveMoneyMeasuresData],
    ]
):
    """Transform the query, extract and transform the data from the FederalReserve endpoints."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveMoneyMeasuresQueryParams:
        """Transform the query params. Start and end dates are set to a 90 day interval."""
        from datetime import timedelta

        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=10 * 365)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FederalReserveMoneyMeasuresQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: FederalReserveMoneyMeasuresQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FederalReserve endpoint."""
        from io import BytesIO

        from openbb_core.provider.utils.helpers import make_request
        from pandas import read_csv, to_datetime

        url = (
            "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H6&series=798e2796917702a5f8423426ba7e6b42"
            "&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package"
        )

        r = make_request(url, **kwargs)
        df = read_csv(BytesIO(r.content), header=5, index_col=None, parse_dates=True)

        columns_to_get = ["Time Period"] + [
            col + f"{'_N' if query.adjusted else ''}.M" for col in titles
        ]
        df = df[columns_to_get]
        df.columns = ["month"] + list(titles.values())
        df = df.replace("ND", None)
        df["month"] = to_datetime(df["month"])
        df = df[
            (to_datetime(df.month) >= to_datetime(query.start_date))  # ty: ignore[no-matching-overload]
            & (to_datetime(df.month) <= to_datetime(query.end_date))  # ty: ignore[no-matching-overload]
        ].set_index("month")
        # Needs the date to not be in the columns
        df = df.map(lambda x: float(x) if x != "-" and x is not None else x)
        df = df.reset_index(drop=False)

        return df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: FederalReserveMoneyMeasuresQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FederalReserveMoneyMeasuresData]:
        """Return the transformed data, expanded from billions to full dollars."""
        from pandas import isna

        money_fields = list(titles.values())
        fed_data = []
        for d in data:
            for k, v in d.items():
                if isna(v) and not isinstance(v, str):
                    d[k] = None
                elif k in money_fields and isinstance(v, (int, float)):
                    d[k] = int(round(v * 1e9))
            fed_data.append(FederalReserveMoneyMeasuresData.model_validate(d))

        return sorted(fed_data, key=lambda x: x.month)
