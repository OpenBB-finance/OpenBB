"""OECD Produced Price Index Model."""

from typing import Any, Dict, List, Optional, Literal, Union
from datetime import date, timedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.ppi import (
    ProducerPriceIndexData,
    ProducerPriceIndexQueryParams,
)
from openbb_oecd.utils import constants, helpers
from pydantic import Field, field_validator
import re

countries = tuple(constants.COUNTRY_TO_CODE_PPI.keys())
CountriesLiteral = Literal[countries]  # type: ignore


class OECDProducerPriceIndexQueryParams(ProducerPriceIndexQueryParams):
    """OECD Producer Price Index Query."""

    country: CountriesLiteral = Field(
        description="Country to get PPI for.", default="united_states"
    )


class OECDProducerPriceIndexData(ProducerPriceIndexData):
    """OECD Producer Price Index Data."""

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


class OECDProducerPriceIndexFetcher(
    Fetcher[OECDProducerPriceIndexQueryParams, List[OECDProducerPriceIndexData]]
):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDProducerPriceIndexQueryParams:
        """Transform query."""
        return OECDProducerPriceIndexQueryParams(**params)

    @staticmethod
    def extract_data(
        query: OECDProducerPriceIndexQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""
        unit = {"annual": "A", "monthly": "M", "quarterly": "Q"}[query.period]

        url = (
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.PPI.TOT_MKT.IDX2015.{unit}"
            f"/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en"
        )

        # This decode gets rid of the weird unicode characters in the column names.
        data_df = helpers.fetch_and_decode(
            url, decode_kwargs={"encoding": "utf-8-sig"}, **kwargs
        )
        data_df = data_df.rename(
            columns={
                "LOCATION": "country",
                "TIME": "date",
                "Value": "value",
                "Location": "country",
            }
        )
        data_df["country"] = data_df["country"].map(constants.CODE_TO_COUNTRY_PPI)
        # Filter by country
        data_df = data_df[data_df["country"] == query.country]
        data_df = data_df[["country", "date", "value"]]
        return data_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDProducerPriceIndexQueryParams, data: Dict, **kwargs: Any
    ) -> List[OECDProducerPriceIndexData]:
        """Transform data."""

        return [OECDProducerPriceIndexData.model_validate(item) for item in data]
