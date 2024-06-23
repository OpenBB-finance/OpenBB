"""EconDB Country Profile."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.country_profile import (
    CountryProfileData,
    CountryProfileQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class EconDbCountryProfileQueryParams(CountryProfileQueryParams):
    """Country Profile Query."""

    __json_schema_extra__ = {"country": {"multiple_items_allowed": True}}

    latest: bool = Field(
        default=True,
        description="If True, return only the latest data."
        + " If False, return all available data for each indicator.",
    )
    use_cache: bool = Field(
        default=True,
        description="If True, the request will be cached for one day."
        + "Using cache is recommended to avoid needlessly requesting the same data.",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, v):
        """Validate the country."""
        # pylint: disable=import-outside-toplevel
        from openbb_econdb.utils.helpers import (
            COUNTRY_GROUPS,
            COUNTRY_MAP,
            THREE_LETTER_ISO_MAP,
        )

        country = v if isinstance(v, list) else v.split(",")
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


class EconDbCountryProfileData(CountryProfileData):
    """EconDB Country Profile Data."""

    __alias_dict__ = {
        "country": "Country",
        "gdp_usd": "GDP ($B USD)",
        "gdp_qoq": "GDP QoQ",
        "gdp_yoy": "GDP YoY",
        "cpi_yoy": "CPI YoY",
        "core_yoy": "Core CPI YoY",
        "retail_sales_yoy": "Retail Sales YoY",
        "industrial_production_yoy": "Industrial Production YoY",
        "policy_rate": "Policy Rate",
        "yield_10y": "10Y Yield",
        "govt_debt_gdp": "Govt Debt/GDP",
        "current_account_gdp": "Current Account/GDP",
        "jobless_rate": "Jobless Rate",
        "population": "Population",
    }

    @field_validator(
        "gdp_qoq",
        "gdp_yoy",
        "cpi_yoy",
        "core_yoy",
        "retail_sales_yoy",
        "industrial_production_yoy",
        "policy_rate",
        "yield_10y",
        "current_account_gdp",
        "jobless_rate",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Normalize the percent values."""
        return float(v) / 100 if v is not None else None


class EconDbCountryProfileFetcher(
    Fetcher[EconDbCountryProfileQueryParams, List[EconDbCountryProfileData]]
):
    """EconDB Country Profile Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> EconDbCountryProfileQueryParams:
        """Transform the query parameters."""
        return EconDbCountryProfileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EconDbCountryProfileQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_econdb.utils.helpers import get_context, parse_context  # noqa
        from pandas import DataFrame, concat  # noqa

        country = query.country.split(",")
        latest = query.latest
        use_cache = query.use_cache
        results = []

        async def get_one_country(_country):  # pylint: disable=too-many-locals
            """Get the profile for one country."""
            _country = _country.upper()
            final_df = DataFrame()
            (
                gdp_response,
                gdp_qoq_response,
                gdp_yoy_response,
                pop_response,
                cpi_response,
                core_response,
                retail_response,
                industrial_response,
                policy_response,
                y10y_response,
                gdebt_response,
                ca_response,
                urate_response,
            ) = await asyncio.gather(
                get_context("GDP", _country, "TUSD", use_cache),
                get_context("RGDP", _country, "TPOP", use_cache),
                get_context("RGDP", _country, "TOYA", use_cache),
                get_context("POP", _country, None, use_cache),
                get_context("CPI", _country, "TOYA", use_cache),
                get_context("CORE", _country, "TOYA", use_cache),
                get_context("RETA", _country, "TOYA", use_cache),
                get_context("IP", _country, "TOYA", use_cache),
                get_context("POLIR", _country, None, use_cache),
                get_context("Y10YD", _country, None, use_cache),
                get_context("GDEBT", _country, "TUSD", use_cache),
                get_context("CA", _country, "TPGP", use_cache),
                get_context("URATE", _country, None, use_cache),
            )
            gdp = parse_context(gdp_response, latest=latest).rename(columns={"GDP": "GDP ($B USD)"})  # type: ignore
            gdp_qoq = parse_context(gdp_qoq_response, latest=latest).rename(columns={"RGDP": "GDP QoQ"})  # type: ignore
            gdp_yoy = parse_context(gdp_yoy_response, latest=latest).rename(columns={"RGDP": "GDP YoY"})  # type: ignore
            pop = parse_context(pop_response, latest=latest).rename(columns={"POP": "Population"})  # type: ignore
            cpi = parse_context(cpi_response, latest=latest).rename(columns={"CPI": "CPI YoY"})  # type: ignore
            core_cpi = parse_context(core_response, latest=latest).rename(columns={"CORE": "Core CPI YoY"})  # type: ignore
            retail_sales = parse_context(retail_response, latest=latest).rename(columns={"RETA": "Retail Sales YoY"})  # type: ignore
            industrial_production = parse_context(
                industrial_response, latest=latest
            ).rename(
                columns={"IP": "Industrial Production YoY"}
            )  # type: ignore
            policy_rate = parse_context(policy_response, latest=latest).rename(columns={"POLIR": "Policy Rate"})  # type: ignore
            y10y = parse_context(y10y_response, latest=latest).rename(columns={"Y10YD": "10Y Yield"})  # type: ignore
            gdebt = parse_context(gdebt_response, latest=latest).rename(columns={"GDEBT": "Govt Debt/GDP"})  # type: ignore
            ca = parse_context(ca_response, latest=latest).rename(columns={"CA": "Current Account/GDP"})  # type: ignore
            urate = parse_context(urate_response, latest=latest).rename(columns={"URATE": "Jobless Rate"})  # type: ignore
            # If returning a pivot table, we need to add the country as an index before concatenating.
            if latest is False:
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
                pop = (
                    pop.set_index("Country", append=True)
                    if "Country" in pop.columns
                    else pop
                )
                cpi = (
                    cpi.set_index("Country", append=True)
                    if "Country" in cpi.columns
                    else cpi
                )
                core_cpi = (
                    core_cpi.set_index("Country", append=True)
                    if "Country" in core_cpi.columns
                    else core_cpi
                )
                retail_sales = (
                    retail_sales.set_index("Country", append=True)
                    if "Country" in retail_sales.columns
                    else retail_sales
                )
                industrial_production = (
                    industrial_production.set_index("Country", append=True)
                    if "Country" in industrial_production.columns
                    else industrial_production
                )
                policy_rate = (
                    policy_rate.set_index("Country", append=True)
                    if "Country" in policy_rate.columns
                    else policy_rate
                )
                y10y = (
                    y10y.set_index("Country", append=True)
                    if "Country" in y10y.columns
                    else y10y
                )
                gdebt = (
                    gdebt.set_index("Country", append=True)
                    if "Country" in gdebt.columns
                    else gdebt
                )
                ca = (
                    ca.set_index("Country", append=True)
                    if "Country" in ca.columns
                    else ca
                )
                urate = (
                    urate.set_index("Country", append=True)
                    if "Country" in urate.columns
                    else urate
                )
            final_df = concat(
                [
                    gdp,
                    gdp_qoq,
                    gdp_yoy,
                    cpi,
                    core_cpi,
                    retail_sales,
                    industrial_production,
                    policy_rate,
                    y10y,
                    gdebt,
                    ca,
                    urate,
                    pop,
                ],
                axis=1,
            )
            # Here, calculating this ratio ourselves produces better results than directly transforming from the API.
            if (
                "Govt Debt/GDP" in final_df.columns
                and "GDP ($B USD)" in final_df.columns
            ):
                final_df["Govt Debt/GDP"] = (
                    final_df["Govt Debt/GDP"] / final_df["GDP ($B USD)"]
                )
            if "Current Account/GDP" in final_df.columns and _country == "US":
                final_df["Current Account/GDP"] = final_df["Current Account/GDP"] * 4
            if final_df.empty:
                warn(f"Error: No data returned for {_country}.")
            if not final_df.empty:
                results.extend(final_df.reset_index().to_dict(orient="records"))

        chunks = [country[i : i + 3] for i in range(0, len(country), 3)]
        for chunk in chunks:
            await asyncio.gather(*[get_one_country(c) for c in chunk])
        if not results:
            raise EmptyDataError("The request returned empty.")
        return results

    @staticmethod
    def transform_data(
        query: EconDbCountryProfileQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[EconDbCountryProfileData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_econdb.utils.helpers import PROFILE_ORDER
        from pandas import DataFrame

        output_df = (
            DataFrame(data)
            .filter(items=["date", "Country"] + PROFILE_ORDER, axis=1)
            .sort_values("GDP ($B USD)", ascending=False)
            .fillna("N/A")
            .replace("N/A", None)
        )
        if "date" in output_df.columns:
            output_df.sort_values(["date", "Country"], inplace=True)
        return [
            EconDbCountryProfileData.model_validate(d)
            for d in output_df.to_dict(orient="records")
        ]
