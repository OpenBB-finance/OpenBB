"""EconDB GDP Real Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.gdp_nominal import (
    GdpNominalData,
    GdpNominalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class EconDbGdpRealQueryParams(GdpNominalQueryParams):
    """EconDB GDP Real Query."""

    __json_schema_extra__ = {
        "country": {"multiple_items_allowed": True},
    }

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", "")
        + "Use 'all' to get data for all available countries.",
        default="united_states",
    )
    use_cache: bool = Field(
        default=True,
        description="If True, the request will be cached for one day."
        + " Using cache is recommended to avoid needlessly requesting the same data.",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, v):
        """Validate the country."""
        # pylint: disable=import-outside-toplevel
        from openbb_econdb.utils.helpers import (
            COUNTRY_GROUPS,
            COUNTRY_MAP,
            INDICATOR_COUNTRIES,
            THREE_LETTER_ISO_MAP,
        )

        country = v if isinstance(v, list) else v.split(",")

        if "all" in country:
            return ",".join(INDICATOR_COUNTRIES.get("RGDP"))

        for c in country.copy():
            if (
                len(c) == 2
                and c.upper() not in list(COUNTRY_MAP.values())
                and c.lower() != "g7"
            ) or (
                len(c) > 3 and c.lower() not in list(COUNTRY_MAP) + list(COUNTRY_GROUPS)
            ):
                country.remove(c)
            elif len(c) == 3 and c.lower() != "g20":
                _c = THREE_LETTER_ISO_MAP.get(c.upper(), "")
                if _c:  # pylint: disable=R0801
                    country[country.index(c)] = _c
                else:
                    warn(f"Error: {c} is not a valid country code.")
                    country.remove(c)
            elif len(c) > 3 and c.lower() in COUNTRY_MAP:
                country[country.index(c)] = COUNTRY_MAP[c.lower()].upper()
            elif len(c) > 2 and c.lower() in COUNTRY_GROUPS:
                country[country.index(c)] = ",".join(COUNTRY_GROUPS[c.lower()])
        if len(country) == 0:
            raise OpenBBError("No valid countries were supplied.")
        return ",".join(country)


class EconDbGdpRealData(GdpNominalData):
    """EconDB GDP Real Data."""

    real_growth_qoq: float = Field(
        description="Real GDP growth rate quarter over quarter.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    real_growth_yoy: float = Field(
        description="Real GDP growth rate year over year.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    value: Union[int, float] = Field(
        description="Real GDP value for the country and date.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )


class EconDbGdpRealFetcher(
    Fetcher[
        EconDbGdpRealQueryParams,
        List[EconDbGdpRealData],
    ]
):
    """EconDB GDP Real Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> EconDbGdpRealQueryParams:
        """Transform the query parameters."""
        return EconDbGdpRealQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EconDbGdpRealQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs,
    ) -> List[Dict]:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from pandas import DataFrame, concat
        from openbb_econdb.utils.helpers import get_context, parse_context, COUNTRY_MAP

        country = query.country.split(",")
        results: List = []

        async def get_one_country(_country):
            """Get the GDP data for one country."""
            _country = (
                _country.upper()
                if len(_country) == 2
                else COUNTRY_MAP[_country.lower()]
            )
            final_df = DataFrame()
            gdp_response, gdp_qoq_response, gdp_yoy_response = await asyncio.gather(
                get_context(
                    "RGDP",
                    _country,
                    None if _country == "US" else "TUSD",
                    query.use_cache,
                ),
                get_context("RGDP", _country, "TPOP", query.use_cache),
                get_context("RGDP", _country, "TOYA", query.use_cache),
            )
            gdp = parse_context(gdp_response, latest=False).rename(columns={"RGDP": "value"})  # type: ignore
            gdp_qoq = parse_context(gdp_qoq_response, latest=False).rename(columns={"RGDP": "real_growth_qoq"})  # type: ignore
            gdp_yoy = parse_context(gdp_yoy_response, latest=False).rename(columns={"RGDP": "real_growth_yoy"})  # type: ignore
            gdp = (
                gdp.set_index("Country", append=True)
                if "Country" in gdp.columns
                else gdp
            )
            gdp_qoq = (
                gdp_qoq.set_index("Country", append=True)
                if "Country" in gdp_qoq.columns
                else gdp_qoq
            )
            gdp_yoy = (
                gdp_yoy.set_index("Country", append=True)
                if "Country" in gdp_yoy.columns
                else gdp_yoy
            )
            final_df = concat(
                [gdp, gdp_qoq, gdp_yoy],
                axis=1,
            )
            if final_df.empty:
                warn(f"Error: No data returned for {_country}.")
            if not final_df.empty:
                results.extend(
                    final_df.reset_index()
                    .rename(columns={"Country": "country"})
                    .to_dict(orient="records")
                )

        chunks = [country[i : i + 6] for i in range(0, len(country), 6)]
        for chunk in chunks:
            await asyncio.gather(*[get_one_country(c) for c in chunk])

        if not results:
            raise EmptyDataError("The request returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: EconDbGdpRealQueryParams,
        data: List[Dict],
        **kwargs,
    ) -> List[EconDbGdpRealData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame, to_datetime

        df = DataFrame(data)

        if query.start_date:
            df = df[to_datetime(df["date"]) >= to_datetime(query.start_date)]
        if query.end_date:
            df = df[to_datetime(df["date"]) <= to_datetime(query.end_date)]

        if df.empty:  # type: ignore
            raise EmptyDataError(
                "No data was found for the supplied date range and countries."
            )

        df = df.set_index(["date", "country"])  # type: ignore
        df = df.dropna()
        df["value"] = (df["value"] * 1_000_000_000).astype("int64")
        df["real_growth_qoq"] = df["real_growth_qoq"] / 100
        df["real_growth_yoy"] = df["real_growth_yoy"] / 100
        df = df.reset_index()
        df = df.sort_values(by=["date", "value"], ascending=[True, False])

        return [
            EconDbGdpRealData.model_validate(d) for d in df.to_dict(orient="records")
        ]
