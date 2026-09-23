"""Federal Reserve Bank of Philadelphia State Coincident Indexes Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.philadelphia import MEDIA_URL

URL = f"{MEDIA_URL}/surveys-and-data/coincident/coincident-revised.xls"

_DATASETS = {"indexes": "Indexes", "diffusion": "Diffusion_Indexes"}


class FederalReservePhiladelphiaCoincidentQueryParams(QueryParams):
    """Philadelphia Fed State Coincident Indexes Query Parameters."""

    __json_schema_extra__ = {
        "dataset": {
            "x-widget_config": {
                "options": [
                    {"label": "Indexes", "value": "indexes"},
                    {"label": "Diffusion", "value": "diffusion"},
                ]
            }
        }
    }

    dataset: Literal["indexes", "diffusion"] = Field(
        default="indexes",
        description="The per-state coincident indexes, or the one- and"
        + " three-month diffusion of state index increases.",
    )
    state: str | None = Field(
        default=None,
        description="Filter to a single series; for 'indexes' a two-letter state"
        + " code (e.g. 'PA') or 'US', for 'diffusion' a code ('DI1' or 'DI3').",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaCoincidentData(Data):
    """Philadelphia Fed State Coincident Indexes Data."""

    date: dateType = Field(description="The month, as a month-start date.")
    state: str = Field(
        description="The two-letter state code or 'US', or the diffusion-series"
        + " code ('DI1' or 'DI3')."
    )
    value: float | None = Field(default=None, description="The index value.")


class FederalReservePhiladelphiaCoincidentFetcher(
    Fetcher[
        FederalReservePhiladelphiaCoincidentQueryParams,
        list[FederalReservePhiladelphiaCoincidentData],
    ]
):
    """Philadelphia Fed State Coincident Indexes Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaCoincidentQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaCoincidentQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaCoincidentQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the State Coincident Indexes workbook."""
        from openbb_federal_reserve.utils.philadelphia import fetch_philadelphia

        content = fetch_philadelphia(URL, "state_coincident", "monthly")
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaCoincidentQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaCoincidentData]:
        """Melt the wide state columns into long state/value records."""
        from pandas import isna, to_datetime

        from openbb_federal_reserve.utils.philadelphia import read_workbook

        frame = read_workbook(data[0]["_raw"], _DATASETS[query.dataset])
        frame = frame.rename(columns={frame.columns[0]: "date"})
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date
        long = frame.melt(id_vars="date", var_name="state", value_name="value")

        if query.state:
            long = long[long["state"].str.upper() == query.state.upper()]
        if query.start_date:
            long = long[long["date"] >= query.start_date]
        if query.end_date:
            long = long[long["date"] <= query.end_date]

        records: list[FederalReservePhiladelphiaCoincidentData] = []
        for row in long.sort_values(["date", "state"]).to_dict(orient="records"):
            value = row["value"]
            if isinstance(value, float) and isna(value):
                continue
            records.append(
                FederalReservePhiladelphiaCoincidentData.model_validate(
                    {
                        "date": row["date"],
                        "state": row["state"],
                        "value": float(value),
                    }
                )
            )

        if not records:
            raise EmptyDataError("The request was returned empty.")

        return records
