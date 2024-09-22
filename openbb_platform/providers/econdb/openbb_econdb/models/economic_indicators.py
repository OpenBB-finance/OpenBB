"""EconDB Economic Indicators."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsData,
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class EconDbEconomicIndicatorsQueryParams(EconomicIndicatorsQueryParams):
    """EconDB Economic Indicators Query."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "country": {"multiple_items_allowed": True},
    }

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " The base symbol for the indicator (e.g. GDP, CPI, etc.)."
        + " Use `available_indicators()` to get a list of available symbols.",
    )

    transform: Union[None, Literal["toya", "tpop", "tusd", "tpgp"]] = Field(
        default=None,
        description="The transformation to apply to the data, default is None."
        + "\n"
        + "\n    tpop: Change from previous period"
        + "\n    toya: Change from one year ago"
        + "\n    tusd: Values as US dollars"
        + "\n    tpgp: Values as a percent of GDP"
        + "\n"
        + "\n"
        + "    Only 'tpop' and 'toya' are applicable to all indicators."
        + " Applying transformations across multiple indicators/countries"
        + " may produce unexpected results."
        + "\n    This is because not all indicators are compatible with all transformations,"
        + " and the original units and scale differ between entities."
        + "\n    `tusd` should only be used where values are currencies.",
    )
    frequency: Literal["annual", "quarter", "month"] = Field(
        default="quarter",
        description="The frequency of the data, default is 'quarter'."
        + " Only valid when 'symbol' is 'main'.",
    )
    use_cache: bool = Field(
        default=True,
        description="If True, the request will be cached for one day."
        + " Using cache is recommended to avoid needlessly requesting the same data.",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_countries(cls, v):
        """Validate each country and convert to a two-letter ISO code."""
        # pylint: disable=import-outside-toplevel
        from openbb_econdb.utils import helpers

        if v:
            country = v if isinstance(v, list) else v.split(",")
            for c in country.copy():
                c = "all" if c == "world" else c  # noqa: PLW2901
                if c == "all":
                    continue
                if (
                    len(c) == 2
                    and c.upper() not in list(helpers.COUNTRY_MAP.values())
                    and c.lower() != "g7"
                ):
                    country.remove(c)
                elif len(c) == 3 and c.lower() != "g20":
                    _c = helpers.THREE_LETTER_ISO_MAP.get(c.upper(), "")
                    if _c:
                        country[country.index(c)] = _c
                    else:
                        warn(f"Error: {c} is not a valid country code.")
                        country.remove(c)
                elif len(c) > 3 and c.lower() in helpers.COUNTRY_MAP:
                    country[country.index(c)] = helpers.COUNTRY_MAP[c.lower()].upper()
                elif len(c) > 2 and c.lower() in helpers.COUNTRY_GROUPS:
                    country[country.index(c)] = ",".join(
                        helpers.COUNTRY_GROUPS[c.lower()]
                    )
            if len(country) == 0:
                raise OpenBBError("No valid countries were supplied.")
            return ",".join(country)
        return None

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def validate_symbols(cls, v):
        """Validate each symbol to check if it is a valid indicator."""
        # pylint: disable=import-outside-toplevel
        from openbb_econdb.utils import helpers

        INDICATORS = list(helpers.INDICATORS_DESCRIPTIONS)
        if not v:
            v = "main"
        symbols = v if isinstance(v, list) else v.split(",")
        new_symbols: List[str] = []
        for symbol in symbols:
            if "_" in symbol:
                new_symbols.append(symbol)
                continue
            if symbol.upper() == "MAIN":
                if len(symbols) > 1:
                    raise OpenBBError(
                        "The 'main' indicator cannot be combined with other indicators."
                    )
                return symbol
            if not any(
                (
                    symbol.upper().startswith(indicator)
                    if len(symbol) >= len(indicator)
                    else symbol.upper() == indicator
                )
                for indicator in INDICATORS
            ):
                warn(f"Invalid indicator: '{symbol}'.")
            else:
                new_symbols.append(symbol)
        if not new_symbols:
            raise OpenBBError(
                "No valid indicators provided. Please choose from: "
                + ",".join(INDICATORS)
            )
        return ",".join(new_symbols)


class EconDbEconomicIndicatorsData(EconomicIndicatorsData):
    """EconDB Economic Indicators Data."""


class EconDbEconomicIndicatorsFetcher(
    Fetcher[EconDbEconomicIndicatorsQueryParams, List[EconDbEconomicIndicatorsData]]
):
    """EconDB Economic Indicators Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> EconDbEconomicIndicatorsQueryParams:
        """Transform the query parameters."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta

        new_params = params.copy()
        if new_params.get("start_date") is None:
            new_params["start_date"] = (
                datetime.today() - timedelta(weeks=52 * 11)
            ).date()
        if new_params.get("end_date") is None:
            new_params["end_date"] = datetime.today().date()
        countries = new_params.get("country")
        if (
            countries is not None
            and len(countries.split(",")) > 1
            and new_params.get("symbol", "").upper() == "MAIN"
        ):
            raise OpenBBError(
                "The 'main' indicator cannot be combined with multiple countries."
            )
        return EconDbEconomicIndicatorsQueryParams(**new_params)

    @staticmethod
    async def aextract_data(  # pylint: disable=R0914.R0912,R0915
        query: EconDbEconomicIndicatorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_econdb.utils import helpers
        from openbb_econdb.utils.main_indicators import get_main_indicators

        if query.symbol.upper() == "MAIN":
            country = query.country.upper() if query.country else "US"

            return await get_main_indicators(
                country,
                query.start_date.strftime("%Y-%m-%d"),  # type: ignore
                query.end_date.strftime("%Y-%m-%d"),  # type: ignore
                query.frequency,
                query.transform,
                query.use_cache,
            )

        token = credentials.get("econdb_api_key", "")  # type: ignore
        # Attempt to create a temporary token if one is not supplied.
        if not token:
            token = await helpers.create_token(use_cache=query.use_cache)
            credentials.update({"econdb_api_key": token})  # type: ignore
        base_url = "https://www.econdb.com/api/series/?ticker="
        data: List[Dict] = []
        symbols = query.symbol.split(",")
        countries = query.country.split(",") if query.country else []
        new_symbols: List = []
        # We need to join country, symbol, and transformation
        # for every combination of country and symbol.
        for s in symbols:
            # We will assume that if the symbol has a '~' in it,
            # the user knows what they are doing. We don't want to
            # match this defined symbol with any supplied country, and we need to
            # ignore the transform parameter because it has already been dictated by ~.
            # We will check if the transform is valid,
            # and return the symbol as 'level' if it is not.
            # We will also check if the symbol should have a country,
            # and if one was supplied.
            symbol = s.upper()
            if "~" in symbol:
                _symbol = symbol.split("~")[0]
                _transform = symbol.split("~")[1]
                if (
                    helpers.HAS_COUNTRIES.get(_symbol) is True
                    and _symbol in helpers.SYMBOL_TO_INDICATOR.values()
                ):
                    message = f"Invalid symbol: '{symbol}'. It must have a two-letter country code."
                    if len(symbols) > 1:
                        warn(message)
                        continue
                    raise OpenBBError(message)
                if _transform and _transform not in helpers.QUERY_TRANSFORMS:
                    message = f"Invalid transformation, '{_transform}', for symbol: '{_symbol}'."
                    if len(symbols) > 1:
                        warn(message)
                        new_symbols.append(_symbol)
                    else:
                        raise OpenBBError(message)
                elif not _transform:
                    new_symbols.append(symbol.replace("~", ""))
                else:
                    new_symbols.append(symbol)
            # Else we need to wrap each symbol with each country code
            # and check if the country is valid for that indicator.
            elif countries and helpers.HAS_COUNTRIES.get(symbol) is True:
                for country in countries:
                    _country = (
                        helpers.INDICATOR_COUNTRIES.get(symbol, [])
                        if country == "all"
                        else (
                            helpers.COUNTRY_GROUPS.get(country, [])
                            if country in helpers.COUNTRY_GROUPS
                            else (
                                [country.upper()]
                                if country.upper()
                                in helpers.INDICATOR_COUNTRIES.get(symbol, [])
                                else ""
                            )
                        )
                    )
                    if _country == "":
                        warn(
                            f"Invalid country code for indicator: {symbol}."
                            + f" Skipping '{country}'. Valid countries are:"
                            + f" {','.join(helpers.INDICATOR_COUNTRIES.get(symbol))}"
                        )
                        continue
                    new_symbol = [
                        symbol + d.upper()
                        for d in _country
                        if d in helpers.INDICATOR_COUNTRIES.get(symbol)
                    ]
                    if query.transform:
                        new_symbol = [
                            d + "~" + query.transform.upper() for d in new_symbol
                        ]
                    new_symbols.extend(new_symbol)
            # If it is a commodity symbol, there will be no country associated with the indicator.
            elif (
                symbol in helpers.HAS_COUNTRIES
                and helpers.HAS_COUNTRIES[symbol] is False
            ):
                new_symbols.append(symbol)
        if not new_symbols:
            symbol_message = helpers.INDICATOR_COUNTRIES.get(
                query.symbol.upper(), "None"
            )
            error_message = (
                "No valid combination of indicator symbols and countries were supplied."
                + f"\nValid countries for '{query.symbol}' are: {symbol_message}"
                + f"\nIf the symbol - {query.symbol} - is missing a country code."
                + " Please add the two-letter country code or use the country parameter."
                + "\nIf already included, add '~' to the end of the symbol."
            )
            raise OpenBBError(error_message)
        url = base_url + f"%5B{','.join(new_symbols)}%5D&format=json&token={token}"
        if query.start_date:
            url += f"&from={query.start_date}"
        if query.end_date:
            url += f"&to={query.end_date}"
        # If too many indicators and countries are supplied the request url will be too long.
        # Instead of chunking we request the user reduce the number of indicators and countries.
        # This might be able to nudge higher, but it is a safe limit for all operating systems.
        if len(url) > 2000:
            raise OpenBBError(
                "The request has generated a url that is too long."
                + " Please reduce the number of symbols or countries and try again."
            )

        async def response_callback(response, session):
            """Response callback."""
            if response.status != 200:
                warn(f"Error: {response.status} - {response.reason}")
            response = await response.json()
            if response.get("results"):
                data.extend(response["results"])
            while response.get("next"):
                response = await session.get(response["next"])
                response = await response.json()
                if response.get("results"):
                    data.extend(response["results"])
            return data

        if query.use_cache is True:
            cache_dir = f"{helpers.get_user_cache_directory()}/http/econdb_indicators"
            async with helpers.CachedSession(
                cache=helpers.SQLiteBackend(
                    cache_dir, expire_after=3600 * 24, ignored_params=["token"]
                )
            ) as session:
                try:
                    data = await helpers.amake_request(  # type: ignore
                        url,
                        session=session,
                        response_callback=response_callback,
                        timeout=20,
                        **kwargs,
                    )
                finally:
                    await session.close()
        else:
            data = await helpers.amake_request(  # type: ignore
                url, response_callback=response_callback, timeout=20, **kwargs
            )
        if not data:
            raise EmptyDataError()
        return data

    @staticmethod
    def transform_data(  # pylint: disable=R0914,R0915
        query: EconDbEconomicIndicatorsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> AnnotatedResult[List[EconDbEconomicIndicatorsData]]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_econdb.utils import helpers
        from pandas import DataFrame, concat

        if query.symbol.upper() == "MAIN":
            return AnnotatedResult(
                result=[
                    EconDbEconomicIndicatorsData.model_validate(r)
                    for r in data[0].get("records", [])
                ],
                metadata={query.country: data[0].get("metadata", [])},
            )
        output = DataFrame()
        metadata = {}
        for d in data:
            if "data" in d and not d["data"].get("values"):
                warn(
                    f"Symbol Error: No data found for '{d.get('ticker', '')}'."
                    + " The country has data, but not for the requested date range."
                )
                continue
            # First we need to parse the metadata for the series.
            title = d.get("description", "")
            title = title.replace("All countries", "World")
            _symbol = d.get("ticker", [])
            symbol = _symbol.split("~")[0] if "~" in _symbol else _symbol
            indicator = helpers.SYMBOL_TO_INDICATOR.get(symbol, "")
            _transform = _symbol.split("~")[1] if "~" in _symbol else ""
            transform = helpers.TRANSFORM_DICT.get(_transform, None)
            country = d.get("geography", "")
            country = country.replace("All countries", "World")
            frequency = d.get("frequency", None)
            dataset = d.get("dataset", None)
            units = helpers.UNITS.get(symbol, "")
            scale = (
                "PERCENT"
                if _transform in ["TPGP", "TPOP", "TOYA"]
                else helpers.SCALES.get(symbol, None)
            )
            if symbol.startswith("Y10YD") or symbol.startswith("M3YD"):
                scale = "Units"
                units = "PERCENT"
            add_info = d.get("additional_metadata", None) or d.get(
                "additional_info", None
            )
            if _transform == "TUSD":
                scale = "Units"
                units = "USD"
            if add_info:
                if (
                    scale in ["Units", "PERCENT"]
                    and units == "DOMESTIC"
                    and "COMMODITY:Commodity" in add_info
                ):
                    units = "USD"
                elif scale == "Units":
                    units = (
                        add_info.get(
                            "UNIT_MEASURE:UNIT_MEASURE",
                            add_info.get("UNIT:Unit of measure", units),
                        )
                        if units != "USD"
                        else units
                    )
            units = units.replace("PC:Percentage", "PERCENT")
            if ", " in units:
                units = units.split(", ")[1]
            multiplier = 1 if scale == "PERCENT" else helpers.MULTIPLIERS.get(symbol, 1)
            # Special handling for the population multiplier
            # because some values are buried elsewhere in the metadata.
            if indicator == "POP" and country in helpers.POP_MULTIPLIER:
                multiplier = helpers.POP_MULTIPLIER[country]
            metadata.update(
                {
                    _symbol: dict(  # pylint: disable=R1735
                        title=title,
                        country=country,
                        frequency=frequency,
                        dataset=dataset,
                        transform=transform if transform else None,
                        units=units if units else None,
                        scale=scale if scale else None,
                        multiplier=multiplier if multiplier else None,
                        additional_info=add_info if add_info else None,
                    )
                }
            )
            # Now we can get the data.
            _result = d.get("data", [])
            result = DataFrame(_result)
            result = result.rename(  # pylint: disable=E1136  # type: ignore
                columns={"dates": "date", "values": "value"}
            )[["date", "value"]].sort_values(by="date")
            result["symbol_root"] = indicator
            result["symbol"] = _symbol
            result["country"] = country
            # We can normalize the percent values here
            # because we have accounted for transformation, if done.
            if units == "PERCENT" or scale == "PERCENT":
                result["value"] = result["value"].astype(float).div(100)
            # Combine it with all the other series requested.
            output = concat([output, result.dropna()], axis=0)
            output = (
                output.set_index(["date", "symbol_root", "country"])
                .sort_index()
                .reset_index()
            )
        if output.empty:
            raise EmptyDataError(
                "Error: The no data was found for the supplied symbols and countries: "
                + f"{query.symbol.split(',')} {query.country.split(',') if query.country else ''}"
            )
        records = (
            output.fillna("N/A")
            .replace("N/A", None)
            .replace("nan", None)
            .replace("", None)
            .replace(0, None)
            .to_dict("records")
        )
        return AnnotatedResult(
            result=[
                EconDbEconomicIndicatorsData.model_validate(r)
                for r in records
                if r["value"] is not None
            ],
            metadata=metadata,
        )
