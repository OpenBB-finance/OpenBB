"""FederalReserve Money Measures Model."""

from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.money_measures import (
    MoneyMeasuresData,
    MoneyMeasuresQueryParams,
)
from openbb_core.provider.utils.helpers import make_request

titles = {
    "M1": "M1",
    "M2": "M2",
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


class FederalReserveMoneyMeasuresFetcher(
    Fetcher[
        FederalReserveMoneyMeasuresQueryParams,
        List[FederalReserveMoneyMeasuresData],
    ]
):
    """Transform the query, extract and transform the data from the FederalReserve endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FederalReserveMoneyMeasuresQueryParams:
        """Transform the query params. Start and end dates are set to a 90 day interval."""
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
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FederalReserve endpoint."""
        url = (
            "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H6&series=798e2796917702a5f8423426ba7e6b42"
            "&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package"
        )

        r = make_request(url, **kwargs)
        df = pd.read_csv(BytesIO(r.content), header=5, index_col=None, parse_dates=True)

        columns_to_get = ["Time Period"] + [
            col + f'{"_N" if query.adjusted else ""}.M' for col in titles
        ]
        df = df[columns_to_get]
        df.columns = ["month"] + list(titles.values())
        df = df.replace("ND", None)
        df["month"] = pd.to_datetime(df["month"])
        df = df[
            (pd.to_datetime(df.month) >= pd.to_datetime(query.start_date))
            & (pd.to_datetime(df.month) <= pd.to_datetime(query.end_date))
        ].set_index("month")
        # Needs the date to not be in the columns
        df = df.applymap(lambda x: float(x) if x != "-" and x is not None else x)
        df = df.reset_index(drop=False)

        return df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: FederalReserveMoneyMeasuresQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FederalReserveMoneyMeasuresData]:
        """Return the transformed data."""
        fed_data = []
        for d in data:
            for k, v in d.items():
                if pd.isna(v) and not isinstance(v, str):
                    d[k] = None
            fed_data.append(FederalReserveMoneyMeasuresData.model_validate(d))

        return fed_data
