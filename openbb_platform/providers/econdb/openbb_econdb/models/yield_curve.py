"""EconDB Yield Curve."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.yield_curve import (
    YieldCurveData,
    YieldCurveQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_econdb.utils.yield_curves import COUNTRIES_DICT, COUNTRIES_LIST
from pydantic import Field, field_validator


class EconDbYieldCurveQueryParams(YieldCurveQueryParams):
    """EconDB Economic Indicators Query."""

    __json_schema_extra__ = {
        "date": {"multiple_items_allowed": True},
        "country": {"multiple_items_allowed": True, "choices": COUNTRIES_LIST},
    }
    country: str = Field(
        default="united_states",
        description=QUERY_DESCRIPTIONS.get("country", "")
        + " New Zealand, Mexico, Singapore, and Thailand have only monthly data."
        + " The nearest date to the requested one will be used.",
    )
    use_cache: bool = Field(
        default=True,
        description="If true, cache the request for four hours.",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, v) -> str:
        """Validate the country."""
        if v is None:
            return "united_states"

        countries = v.split(",")
        new_countries: list = []

        for country in countries:
            if country not in COUNTRIES_DICT:
                raise ValueError(
                    f"Invalid country, {country}, must be one of {list(COUNTRIES_DICT)}"
                )
            new_countries.append(country)

        return ",".join(new_countries)


class EconDbYieldCurveData(YieldCurveData):
    """EconDB Yield Curve Data."""


class EconDbYieldCurveFetcher(
    Fetcher[EconDbYieldCurveQueryParams, List[EconDbYieldCurveData]]
):
    """EconDB Yield Curve Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EconDbYieldCurveQueryParams:
        """Transform the query parameters."""
        if not params.get("date"):
            params["date"] = datetime.now().strftime("%Y-%m-%d")
        return EconDbYieldCurveQueryParams(**params)

    @staticmethod
    async def aextract_data(  # pylint: disable=R0914.R0912,R0915
        query: EconDbYieldCurveQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  #  noqa
        from openbb_econdb.utils import helpers
        from warnings import warn

        token = credentials.get("econdb_api_key") if credentials else ""  # type: ignore
        # Attempt to create a temporary token if one is not supplied.
        if not token:
            token = await helpers.create_token(use_cache=query.use_cache)
            credentials.update({"econdb_api_key": token})  # type: ignore

        results: dict = {}
        messages: list = []

        async def get_one_country(country):
            """Get the data for one country."""
            base_url = "https://www.econdb.com/api/series/?ticker="
            symbols = list(COUNTRIES_DICT[country].keys())
            url = (
                base_url
                + f"%5B{','.join(symbols)}%5D&page_size=50&format=json&token={token}"
            )
            data: list = []
            response: Union[dict, list[dict]] = {}
            if query.use_cache is True:
                cache_dir = (
                    f"{helpers.get_user_cache_directory()}/http/econdb_yield_curve"
                )
                async with helpers.CachedSession(
                    cache=helpers.SQLiteBackend(
                        cache_dir, expire_after=3600 * 4, ignored_params=["token"]
                    )
                ) as session:
                    await session.delete_expired_responses()
                    try:
                        response = await helpers.amake_request(  # type: ignore
                            url,
                            session=session,
                            timeout=20,
                            **kwargs,
                        )
                    finally:
                        await session.close()
            else:
                response = await helpers.amake_request(  # type: ignore
                    url, timeout=20, **kwargs
                )
            if not response:
                messages.append(f"No data was returned for, {country}")
                return
            data = response.get("results")  # type: ignore
            if not data:
                messages.append(f"The response for, {country}, was returned empty.")
                return
            results[country] = data

            return

        _countries = query.country.split(",")

        tasks = [asyncio.create_task(get_one_country(c)) for c in _countries]
        await asyncio.gather(*tasks)

        if not results and messages:
            msg_str = "\n".join(messages)
            raise OpenBBError(msg_str)

        if not results and not messages:
            raise OpenBBError("Unexpected outcome -> All requests were returned empty.")

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: EconDbYieldCurveQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[list[EconDbYieldCurveData]]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import Categorical, DataFrame, DatetimeIndex

        results_metadata: dict = {}
        results_data: list = []

        def process_country_data(country, country_data):
            """Process the data for one country."""
            maturity_order = list(COUNTRIES_DICT[country].values())
            dates = query.date.split(",")  # type: ignore
            dates_list = DatetimeIndex(dates)
            new_data: Dict = {}
            metadata: Dict = {}
            # Unpack the data for each maturity.
            for item in country_data:
                ticker = item.get("ticker")
                maturity = COUNTRIES_DICT[country].get(ticker)
                dataset = item.get("dataset")
                additional_metadata = item.get("additional_metadata")
                units = "percent"
                description = item.get("description")
                dates = item["data"]["dates"]
                rates = item["data"]["values"]
                meta = {
                    "symbol": ticker,
                    "description": description,
                    "dataset": dataset,
                    "units": units,
                    "additional_metadata": additional_metadata,
                }
                metadata[maturity] = meta
                for d, r in zip(dates, rates):
                    if maturity not in new_data:
                        new_data[maturity] = {}
                    new_data[maturity][d] = r

            # Create a DataFrame from the data
            df = DataFrame(new_data)

            # Convert the index to a DatetimeIndex
            df.index = DatetimeIndex(df.index)

            # Find the nearest date in the DataFrame to each date in dates_list
            def get_nearest_date(df, target_date):
                differences = (df.index - target_date).to_series().abs()
                nearest_date_index = differences.argmin()
                nearest_date = df.index[nearest_date_index]
                return nearest_date

            nearest_dates = [get_nearest_date(df, date) for date in dates_list]

            # Filter for only the nearest dates
            df = df[df.index.isin(nearest_dates)]

            # Flatten the DataFrame
            flattened_data = df.reset_index().melt(
                id_vars="index", var_name="maturity", value_name="rate"
            )
            flattened_data = flattened_data.rename(
                columns={"index": "date"}
            ).sort_values("date")
            flattened_data["maturity"] = Categorical(
                flattened_data["maturity"], categories=maturity_order, ordered=True
            )
            flattened_data["rate"] = flattened_data["rate"].astype(float) / 100
            flattened_data = flattened_data.sort_values(
                by=["date", "maturity"]
            ).reset_index(drop=True)
            flattened_data.loc[:, "date"] = flattened_data["date"].dt.strftime(
                "%Y-%m-%d"
            )
            new_df = flattened_data.copy()
            new_df.loc[:, "country"] = country

            def convert_duration(x):
                """Convert the duration to a decimal representation of years."""
                period, unit = x.split("_")
                if period == "long" and unit == "term":
                    return 30
                if period == "year":
                    return int(unit)
                return int(unit) / 12

            new_df.loc[:, "maturity_years"] = new_df.maturity.apply(convert_duration)

            new_df = new_df.replace({nan: None})
            records = [
                EconDbYieldCurveData.model_validate(r)
                for r in new_df.to_dict("records")
                if r.get("rate")
            ]
            results_data.extend(records)
            results_metadata[country] = metadata

        for country, country_data in data.items():
            process_country_data(country, country_data)

        if not results_data:
            raise EmptyDataError(
                f"No data was found for the country, {query.country},"
                f" and dates, {query.date}"
            )
        return AnnotatedResult(result=results_data, metadata=results_metadata)
