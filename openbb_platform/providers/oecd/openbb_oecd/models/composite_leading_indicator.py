"""OECD CLI Data."""

import re
from datetime import date, timedelta
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.composite_leading_indicator import (
    CLIData,
    CLIQueryParams,
)
from openbb_oecd.utils import helpers
from openbb_oecd.utils.constants import CODE_TO_COUNTRY_CLI, COUNTRY_TO_CODE_CLI
from pydantic import Field, field_validator

countries = tuple(CODE_TO_COUNTRY_CLI.values()) + ("all",)
CountriesLiteral = Literal[countries]  # type: ignore


class OECDCLIQueryParams(CLIQueryParams):
    """OECD CLI Query."""

    country: CountriesLiteral = Field(
        description="Country to get GDP for.", default="united_states"
    )


class OECDCLIData(CLIData):
    """OECD CLI Data."""

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
                year, month = map(int, in_date.split("-"))  # type: ignore
                if month == 12:
                    return date(year, month, 31)  # type: ignore
                next_month = date(year, month + 1, 1)  # type: ignore
                return date(next_month.year, next_month.month, 1) - timedelta(days=1)
            # Now match if it is yearly, i.e 2022
            elif re.match(r"\d{4}$", in_date):
                return date(int(in_date), 12, 31)
        # If the input date is a year
        if isinstance(in_date, int):
            return date(in_date, 12, 31)

        return in_date


class OECDCLIFetcher(Fetcher[OECDCLIQueryParams, List[OECDCLIData]]):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDCLIQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params["start_date"] is None:
            transformed_params["start_date"] = date(1950, 1, 1)
        if transformed_params["end_date"] is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)

        return OECDCLIQueryParams(**transformed_params)

    # pylint: disable=unused-argument
    @staticmethod
    def extract_data(
        query: OECDCLIQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        country = "" if query.country == "all" else COUNTRY_TO_CODE_CLI[query.country]

        # Note this is only available monthly from OECD
        url = f"https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_KEI@DF_KEI,4.0/{country}.M.LI...."

        query_dict = {
            k: v
            for k, v in query.__dict__.items()
            if k not in ["start_date", "end_date"]
        }
        data = helpers.get_possibly_cached_data(
            url, function="economy_composite_leading_indicator", query_dict=query_dict
        )

        if query.country != "all":
            data = data.query(f"REF_AREA == '{country}'")

        # Filter down
        data = data.reset_index(drop=True)[["REF_AREA", "TIME_PERIOD", "VALUE"]].rename(
            columns={"REF_AREA": "country", "TIME_PERIOD": "date", "VALUE": "value"}
        )
        data["country"] = data["country"].map(CODE_TO_COUNTRY_CLI)

        data = data.to_dict(orient="records")
        start_date = query.start_date.strftime("%Y-%m-%d")  # type: ignore
        end_date = query.end_date.strftime("%Y-%m-%d")  # type: ignore
        data = list(filter(lambda x: start_date <= x["date"] <= end_date, data))

        return data

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: OECDCLIQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[OECDCLIData]:
        """Transform the data from the OECD endpoint."""
        return [OECDCLIData.model_validate(d) for d in data]
