"""FRED Personal Consumption Expenditures Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.personal_consumption_expenditures import (
    PersonalConsumptionExpendituresData,
    PersonalConsumptionExpendituresQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_fred.utils.query import UseCacheQueryParams
from openbb_fred.utils.release_tables import get_units, shown, tree

PCE_CATEGORY_TO_EID = {
    "personal_income": "155443",
    "wages_by_industry": "3151",
    "real_pce_percent_change": "3160",
    "real_pce_quantity_index": "3196",
    "pce_price_index": "3208",
    "pce_dollars": "3220",
    "real_pce_chained_dollars": "3232",
    "pce_price_percent_change": "3172",
}

PCE_CATEGORY_TO_UNITS = {
    "wages_by_industry": "Bil. of $",
    "real_pce_percent_change": "%",
    "real_pce_quantity_index": "Index 2017=100",
    "pce_price_index": "Index 2017=100",
    "pce_dollars": "Bil. of $",
    "real_pce_chained_dollars": "Bil. of Chn. 2017 $",
    "pce_price_percent_change": "%",
}

PERSONAL_INCOME_UNITS = "Bil. of $"

PERSONAL_INCOME_LINE_TO_UNITS = {
    35: "%",
    36: "Bil. of Chn. 2017 $",
    37: "Bil. of Chn. 2017 $",
    38: "$",
    39: "Chn. 2017",
    40: "Thous.",
}


class FredPersonalConsumptionExpendituresQueryParams(
    UseCacheQueryParams, PersonalConsumptionExpendituresQueryParams
):
    """FRED Personal Consumption Expenditures Query."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}

    category: Literal[
        "personal_income",
        "wages_by_industry",
        "real_pce_percent_change",
        "real_pce_quantity_index",
        "pce_price_index",
        "pce_dollars",
        "real_pce_chained_dollars",
        "pce_price_percent_change",
    ] = Field(
        default="personal_income",
        description="The category to query.",
        json_schema_extra={"choices": list(PCE_CATEGORY_TO_EID)},
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Normalize the dates entered to comma-separated ISO dates."""
        from openbb_fred.utils.query import join_dates

        return join_dates(v)


class FredPersonalConsumptionExpendituresData(PersonalConsumptionExpendituresData):
    """FRED Personal Consumption Expenditures Data."""

    __alias_dict__ = {
        "date": "observation_date",
        "value": "observation_value",
        "symbol": "series_id",
    }

    date: dateType = Field(
        description="The date of the observation.",
        json_schema_extra=shown("date"),
    )
    symbol: str = Field(
        description="The series id of the observation.",
        json_schema_extra=shown("symbol"),
    )
    value: float = Field(
        description="The observed value.",
        json_schema_extra=shown("value"),
    )
    name: str = Field(
        description="The name of the series.",
        json_schema_extra=shown("name"),
    )
    units: str | None = Field(
        default=None,
        description="The unit of measure the series is published in.",
        json_schema_extra=shown("units"),
    )
    element_id: str = Field(
        description="The element id in the parent/child relationship.",
        json_schema_extra=tree(),
    )
    parent_id: str = Field(
        description="The parent id in the parent/child relationship.",
        json_schema_extra=tree(),
    )
    children: str | None = Field(
        default=None,
        description="The element_id of each child, as a comma-separated string.",
        json_schema_extra=tree(),
    )
    level: int = Field(
        description="The indentation level of the element.",
        json_schema_extra=tree(),
    )
    line: int = Field(
        description="The line number of the series in the table.",
        json_schema_extra=tree(),
    )


class FredPersonalConsumptionExpendituresFetcher(
    Fetcher[
        FredPersonalConsumptionExpendituresQueryParams,
        list[FredPersonalConsumptionExpendituresData],
    ]
):
    """FRED Personal Consumption Expenditures Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FredPersonalConsumptionExpendituresQueryParams:
        """Transform query."""
        return FredPersonalConsumptionExpendituresQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredPersonalConsumptionExpendituresQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract data."""
        import asyncio  # noqa
        from openbb_fred.utils.api import observation_dates, release_tables_url
        from openbb_fred.utils.rate_limiter import fred_get
        from numpy import nan
        from pandas import DataFrame, to_datetime

        api_key = credentials.get("fred_api_key") if credentials else ""
        element_id = PCE_CATEGORY_TO_EID[query.category]
        URLS = [
            release_tables_url("54", element_id, api_key, date)
            for date in observation_dates(query.date)
        ]
        results: list = []

        async def get_one(URL):
            """Get the observations for a single date."""
            response = await fred_get(URL, use_cache=query.use_cache)
            data = [
                v
                for v in response.get("elements", {}).values()
                if v.get("observation_value") != "." and v.get("type") != "header"
            ]
            if data:
                df = (
                    DataFrame(data)
                    .set_index(["line", "element_id", "parent_id"])
                    .sort_index()[
                        [
                            "level",
                            "series_id",
                            "name",
                            "observation_date",
                            "observation_value",
                        ]
                    ]
                    .reset_index()
                )
                df["parent_id"] = df.parent_id.astype(str)
                df["element_id"] = df.element_id.astype(str)
                df["observation_value"] = df.observation_value.str.replace(
                    ",", ""
                ).astype(float)
                df["line"] = df.line.astype(int)
                df["observation_date"] = to_datetime(
                    df["observation_date"], format="%b %Y"
                ).dt.date
                children = (
                    df.groupby("parent_id")["element_id"]
                    .apply(lambda x: x.sort_values().unique().tolist())
                    .to_dict()
                )
                children = {k: ",".join(v) for k, v in children.items()}
                df["children"] = df.element_id.map(children)
                df = (
                    df.set_index(
                        ["line", "element_id", "children", "parent_id", "level"]
                    )
                    .sort_index()
                    .reset_index()
                    .replace({nan: None})
                )
                if query.category == "personal_income":
                    df["units"] = df.line.map(
                        lambda line: PERSONAL_INCOME_LINE_TO_UNITS.get(
                            line, PERSONAL_INCOME_UNITS
                        )
                    )
                else:
                    df["units"] = PCE_CATEGORY_TO_UNITS[query.category]

                results.extend(df.to_dict("records"))

        await asyncio.gather(*[get_one(URL) for URL in URLS])

        units = await get_units(54, credentials)

        for row in results:
            row["units"] = units.get(row.get("series_id")) or row.get("units")

        return results

    @staticmethod
    def transform_data(
        query: FredPersonalConsumptionExpendituresQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FredPersonalConsumptionExpendituresData]:
        """Transform data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")

        return [
            FredPersonalConsumptionExpendituresData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: (
                    x["observation_date"],
                    x["line"],
                ),
            )
        ]
