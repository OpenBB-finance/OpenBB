"""OECD Produced Price Index Model."""

from datetime import date, timedelta
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.composite_leading_indicator import (
    CompositeLeadingIndicatorData,
    CompositeLeadingIndicatorQueryParams,
)
from openbb_oecd.utils import constants, helpers
from pydantic import Field, field_validator

countries = tuple(constants.COUNTRY_TO_CODE_CLI.keys())
CountriesLiteral = Literal[countries]  # type: ignore


class OECDCompositeLeadingIndicatorQueryParams(CompositeLeadingIndicatorQueryParams):
    """OECD Composite Leading Indicator Query."""

    country: CountriesLiteral = Field(
        description="Country to get CLI for.", default="united_states"
    )


class OECDCompositeLeadingIndicatorData(CompositeLeadingIndicatorData):
    """OECD Composite Leading Indicator Data."""

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, in_date: Union[date, str]):  # pylint: disable=E0213
        """Validate value."""
        if isinstance(in_date, str):
            year, month = map(int, in_date.split("-"))
            if month == 12:
                return date(year, month, 31)
            else:
                next_month = date(year, month + 1, 1)
                return date(next_month.year, next_month.month, 1) - timedelta(days=1)
        # If the input date is a year
        if isinstance(in_date, int):
            return date(in_date, 12, 31)

        return in_date


class OECDCompositeLeadingIndicatorFetcher(
    Fetcher[
        OECDCompositeLeadingIndicatorQueryParams,
        List[OECDCompositeLeadingIndicatorData],
    ]
):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> OECDCompositeLeadingIndicatorQueryParams:
        """Transform query."""
        return OECDCompositeLeadingIndicatorQueryParams(**params)

    @staticmethod
    def extract_data(
        query: OECDCompositeLeadingIndicatorQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""
        url = (
            "https://stats.oecd.org/sdmx-json/data/DP_LIVE/.CLI.AMPLITUD.LTRENDIDX.M"
            "/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en"
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
            }
        )
        data_df["country"] = data_df["country"].map(constants.CODE_TO_COUNTRY_CLI)
        # Filter by country
        data_df = data_df[data_df["country"] == query.country]
        data_df = data_df[["country", "date", "value"]]
        return data_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDCompositeLeadingIndicatorQueryParams, data: Dict, **kwargs: Any
    ) -> List[OECDCompositeLeadingIndicatorData]:
        """Transform data."""

        return [OECDCompositeLeadingIndicatorData.model_validate(item) for item in data]
