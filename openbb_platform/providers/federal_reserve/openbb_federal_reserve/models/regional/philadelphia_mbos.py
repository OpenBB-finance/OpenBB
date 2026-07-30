"""Federal Reserve Bank of Philadelphia Manufacturing Business Outlook Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.philadelphia import MEDIA_URL

URL = f"{MEDIA_URL}/surveys-and-data/mbos/historical-data/diffusion-indexes/bos_dif.csv"


class FederalReservePhiladelphiaManufacturingQueryParams(QueryParams):
    """Philadelphia Fed Manufacturing Business Outlook Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaManufacturingData(Data):
    """Philadelphia Fed Manufacturing Business Outlook Survey Data."""

    date: dateType = Field(description="The survey month, as a month-start date.")


class FederalReservePhiladelphiaManufacturingFetcher(
    Fetcher[
        FederalReservePhiladelphiaManufacturingQueryParams,
        list[FederalReservePhiladelphiaManufacturingData],
    ]
):
    """Philadelphia Fed Manufacturing Business Outlook Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaManufacturingQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaManufacturingQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaManufacturingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the manufacturing diffusion-index CSV."""
        from openbb_federal_reserve.utils.philadelphia import fetch_philadelphia

        content = fetch_philadelphia(URL, "mbos_diffusion", "monthly")
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaManufacturingQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaManufacturingData]:
        """Parse the already-wide CSV and return wide rows."""
        from io import StringIO

        from pandas import isna, read_csv

        from openbb_federal_reserve.utils.philadelphia import parse_two_digit_month

        frame = read_csv(StringIO(data[0]["_raw"].decode("utf-8", "ignore")))
        frame = frame.rename(columns={"DATE": "date"})
        frame["date"] = parse_two_digit_month(frame["date"])
        frame = frame.dropna(subset=["date"])

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        value_columns = [column for column in frame.columns if column != "date"]
        records: list[FederalReservePhiladelphiaManufacturingData] = []
        for raw in frame.sort_values("date").to_dict(orient="records"):
            row: dict[str, Any] = {"date": raw["date"]}
            for column in value_columns:
                value = raw[column]
                if isinstance(value, float) and isna(value):
                    continue
                row[column] = float(value)
            if len(row) > 1:
                records.append(
                    FederalReservePhiladelphiaManufacturingData.model_validate(row)
                )
        return records
