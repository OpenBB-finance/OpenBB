"""OECD Unemployment Model."""


from datetime import date, timedelta
from typing import Any, Dict, List, Literal, Optional, Union
import re
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.unemployment import (
    UnemploymentData,
    UnemploymentQueryParams,
)
from openbb_oecd.utils import constants, helpers
from pydantic import Field, field_validator

countries = tuple(constants.COUNTRY_TO_CODE_UNEMPLOYMENT.keys())
CountriesLiteral = Literal[countries]  # type: ignore


class OECDUnemploymentQueryParams(UnemploymentQueryParams):
    """OECD Unemployment Query."""

    country: CountriesLiteral = Field(
        description="Country to get unemployment for.", default="united_states"
    )


class OECDUnemploymentData(UnemploymentData):
    """OECD Unemployment Data."""

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, in_date: Union[date, str]):  # pylint: disable=E0213
        """Validate value."""
        if isinstance(in_date, str):
            # i.e 2022-Q1
            if re.match(r"\d{4}-Q[1-4]$", in_date):
                year, quarter = in_date.split("-")
                _year = int(year)
                if quarter == "Q1":
                    return date(_year, 3, 31)
                if quarter == "Q2":
                    return date(_year, 6, 30)
                if quarter == "Q3":
                    return date(_year, 9, 30)
                if quarter == "Q4":
                    return date(_year, 12, 31)
            # Now match if it is monthly, i.e 2022-01
            elif re.match(r"\d{4}-\d{2}$", in_date):
                year, month = map(int, in_date.split("-"))
                if month == 12:
                    return date(year, month, 31)
                else:
                    next_month = date(year, month + 1, 1)
                    return date(next_month.year, next_month.month, 1) - timedelta(
                        days=1
                    )
        # If the input date is a year
        if isinstance(in_date, int):
            return date(in_date, 12, 31)

        return in_date


class OECDUnemploymentFetcher(
    Fetcher[OECDUnemploymentQueryParams, List[OECDUnemploymentData]]
):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDUnemploymentQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params["start_date"] is None:
            transformed_params["start_date"] = date(1950, 1, 1)
        if transformed_params["end_date"] is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)

        return OECDUnemploymentQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDUnemploymentQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the OECD endpoint."""
        unit = {"annual": "A", "monthly": "M", "quarterly": "Q"}[query.period]

        url = (
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.HUR.TOT.PC_LF.{unit}"
            f"/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en"
        )

        # This decode gets rid of the weird unicode characters in the column names.
        data_df = helpers.fetch_and_decode(
            url, decode_kwargs={"encoding": "utf-8-sig"}, **kwargs
        )
        # Sometimes there is weird unicode characters in the column names, so we need to rename them.
        # Even changing the encoding on the fetch doesn't seem to help.
        data_df = data_df.rename(
            columns={
                "LOCATION": "country",
                "TIME": "date",
                "Value": "value",
                "Location": "country",
            }
        )

        data_df["country"] = data_df["country"].map(
            constants.CODE_TO_COUNTRY_UNEMPLOYMENT
        )
        # Filter by country
        data_df = data_df[data_df["country"] == query.country]
        data_df = data_df[["country", "date", "value"]]
        return data_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDUnemploymentQueryParams, data: Dict, **kwargs: Any
    ) -> List[OECDUnemploymentData]:
        """Transform the data from the OECD endpoint."""
        return [OECDUnemploymentData.model_validate(d) for d in data]
