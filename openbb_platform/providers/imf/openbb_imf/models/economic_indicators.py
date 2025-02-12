"""IMF Economic Indicators Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsData,
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_imf.utils.constants import (
    FSI_PRESETS,
    IRFCL_PRESET,
    IRFCL_TABLES,
    load_symbols,
)
from openbb_imf.utils.irfcl_helpers import (
    load_country_to_code_map,
    validate_countries,
)
from pydantic import Field, field_validator


class ImfEconomicIndicatorsQueryParams(EconomicIndicatorsQueryParams):
    """IMF Economic Indicators Query."""

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
        },
        "country": {
            "multiple_items_allowed": True,
            "choices": ["all"] + list(list(load_country_to_code_map())),
        },
        "frequency": {
            "choices": ["annual", "quarter", "month"],
        },
    }
    symbol: str = Field(
        default="irfcl_top_lines",
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Use `available_indicators()` to get the list of available symbols."
        + " Use 'IRFCL' to get all the data from International Reserves & Foreign Currency Liquidity indicators."
        + " Use 'core_fsi' to get the core Financial Soundness Indicators."
        + " Use 'core_fsi_underlying' to include underlying data for the core Financial Soundness Indicators."
        + " Complete tables are available only by single country, and are keyed as described below."
        + " The default is 'irfcl_top_lines'. Available presets not listed in `available_indicators()` are:"
        + """\n
        'IRFCL': All the data from the set of indicators. Not compatible with multiple countries.
        'irfcl_top_lines': The default, top line items from the IRFCL data. Compatible with multiple countries.
        'reserve_assets_and_other_fx_assets': Table I of the IRFCL data. Not compatible with multiple countries.
        'predetermined_drains_on_fx_assets': Table II of the IRFCL data. Not compatible with multiple countries.
        'contingent_drains_fx_assets': Table III of the IRFCL data. Not compatible with multiple countries.
        'memorandum_items': The memorandum items table of the IRFCL data. Not compatible with multiple countries.
        'gold_reserves': Gold reserves as value in USD and Fine Troy Ounces. Compatible with multiple countries.
        'derivative_assets': Net derivative assets as value in USD. Compatible with multipile countries.
        'fsi_core': The core Financial Soundness Indicators. Compatible with multiple countries.
        'fsi_core_underlying': The core FSIs underlying series data. Not compatible with country='all'.
        'fsi_encouraged_set': The encouraged set of Financial Soundness Indicators. Not compatible with country='all'.
        'fsi_other': The other Financial Soundness Indicators. Not compatible with country='all'.
        'fsi_balance_sheets': Data categorized as Balance Sheets and Income Statements. Not compatible with country='all'.
        'fsi_all': All the Financial Soundness Indicators. Not compatible with multiple countries.
    """,
    )
    frequency: Literal["annual", "quarter", "month"] = Field(
        default="quarter",
        description="Frequency of the data, default is 'quarter'.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _count_presets(cls, v):
        """Validate the symbol."""
        if not v:
            return v
        presets = list(IRFCL_PRESET) + FSI_PRESETS
        n_preset = 0
        symbols = v.split(",")
        for symbol in symbols:
            n_preset += 1 if symbol in presets else 0
        if n_preset > 1:
            raise ValueError("only one preset symbol can be used at a time.")
        return v


class ImfEconomicIndicatorsData(EconomicIndicatorsData):
    """IMF Economic Indicators Data."""

    __alias_dict__ = {
        "symbol_root": "parent",
    }

    unit: Optional[str] = Field(
        default=None,
        description="The unit of the value.",
    )
    scale: Optional[str] = Field(
        default=None,
        description="The scale of the value.",
    )
    table: Optional[str] = Field(
        default=None,
        description="The name of the table associated with the symbol.",
    )
    level: Optional[int] = Field(
        default=None,
        description="The indentation level of the data, relative to the table and symbol_root",
    )
    order: Optional[Union[int, float]] = Field(
        default=None,
        description="Order of the data, relative to the table.",
    )
    reference_sector: Optional[str] = Field(
        default=None,
        description="The reference sector for the data.",
    )
    title: Optional[str] = Field(
        default=None,
        description="The title of the series associated with the symbol.",
    )


class ImfEconomicIndicatorsFetcher(
    Fetcher[ImfEconomicIndicatorsQueryParams, List[ImfEconomicIndicatorsData]]
):
    """IMF Economic Indicators Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> ImfEconomicIndicatorsQueryParams:
        """Transform the query."""
        symbols = params.get("symbol", "")
        countries = params.get("country")
        now = datetime.now().date()
        symbols = (
            "IRFCL"
            if (("all" in symbols or "IRFCL" in symbols) and "fsi_all" not in symbols)
            else symbols if symbols else "irfcl_top_lines"
        )
        incompatible = (
            "fsi_other" in symbols
            or "fsi_encouraged_set" in symbols
            or "fsi_all" in symbols
            or "fsi_core_underlying" in symbols
            or "fsi_balance_sheets" in symbols
        )
        if (symbols == "IRFCL" or incompatible) and not (
            countries or countries == "all"
        ):
            raise OpenBBError(
                f"The selected symbol(s), {params.get('symbol')}, is not compatible with the all-countries group."
                " Please provide country names or two-letter ISO country codes."
            )

        if countries:
            params["country"] = validate_countries(countries)

        if symbols and symbols in IRFCL_PRESET:
            params["symbol"] = IRFCL_PRESET[symbols]
            if symbols in IRFCL_TABLES and countries and countries.split(",") > 1:
                raise OpenBBError(
                    f"Symbol '{symbols}' is a table and can only be used with one country."
                )
        elif symbols:
            params["symbol"] = symbols

        if not params.get("start_date") and (not countries or countries == "all"):
            params["start_date"] = now.replace(
                year=now.year - 1, month=1, day=1
            ).strftime("%Y-%m-%d")

        if not params.get("end_date"):
            params["end_date"] = now.replace(month=12, day=31).strftime("%Y-%m-%d")

        if (not symbols or symbols == "all") and not params.get("start_date"):
            params["start_date"] = now.replace(year=now.year - 1).strftime("%Y-%m-%d")

        return ImfEconomicIndicatorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfEconomicIndicatorsQueryParams,
        credentials: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data."""
        # pylint: disable = import-outside-toplevel
        from openbb_imf.utils.fsi_helpers import _get_fsi_data  # noqa
        from openbb_imf.utils.irfcl_helpers import _get_irfcl_data
        from warnings import warn

        fsi_symbols = load_symbols("FSI")
        irfcl_symbols = load_symbols("IRFCL")
        symbols = query.symbol.split(",")
        new_symbols_irfcl: Union[list, str] = []
        new_symbols_fsi: Union[list, str] = []
        for symbol in symbols:
            if symbol in list(IRFCL_PRESET) + ["all", "IRFCL"]:
                new_symbols_irfcl = symbol
            elif symbol in FSI_PRESETS:
                new_symbols_fsi = symbol
            elif symbol.upper() in fsi_symbols:
                new_symbols_fsi.append(symbol.upper())  # type: ignore
            elif symbol.upper() in irfcl_symbols:
                new_symbols_irfcl.append(symbol.upper())  # type: ignore

        if not new_symbols_irfcl and not new_symbols_fsi:
            raise OpenBBError(
                f"No valid symbols found -> {query.symbol} -> "
                "Use 'available_indicators(provider='imf')' to get the list of available symbols."
            )

        results: list = []
        exceptions: list = []
        try:
            try:
                if new_symbols_irfcl:
                    _kwargs = query.model_dump(exclude_none=True)
                    _kwargs["symbol"] = new_symbols_irfcl
                    results.extend(await _get_irfcl_data(**_kwargs))
            except (EmptyDataError, OpenBBError) as e:
                if new_symbols_fsi:
                    exceptions.append(
                        f"IRFCL dataset error -> {e.__class__.__name__}: {e}"
                    )
                else:
                    raise
            if new_symbols_fsi:
                try:
                    _kwargs = query.model_dump(exclude_none=True)
                    _kwargs["symbol"] = new_symbols_fsi
                    results.extend(await _get_fsi_data(**_kwargs))
                except (EmptyDataError, OpenBBError) as e:
                    if new_symbols_irfcl and len(results) > 0:
                        exceptions.append(
                            f"FSI dataset error -> {e.__class__.__name__}: {e}"
                        )
                    elif not new_symbols_irfcl:
                        raise
        except OpenBBError as exc:
            raise exc from exc

        if not results:
            raise EmptyDataError("No results returned for the query.")

        if results and exceptions:
            msgs = "\n".join(exceptions)
            warn("An error occurred while fetching the data -> " + msgs)

        return results

    @staticmethod
    def transform_data(
        query: ImfEconomicIndicatorsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[ImfEconomicIndicatorsData]:
        """Transform the data."""
        # pylint: disable = import-outside-toplevel
        from numpy import nan
        from pandas import Categorical, DataFrame

        if not data:
            raise EmptyDataError("The data is empty.")

        all_symbols = {
            **load_symbols("all"),
        }
        df = DataFrame(data)

        if df.empty:
            raise EmptyDataError("The data is empty.")

        df = df[df["symbol"].isin(all_symbols)]

        if len(df) == 0:
            raise OpenBBError("The data has a length of 0.")

        df["symbol"] = Categorical(
            df["symbol"],
            categories=all_symbols,
            ordered=True,
        )
        df["parent"] = Categorical(
            df["parent"],
            categories=all_symbols,
            ordered=True,
        )
        df = df.sort_values(
            by=["date", "parent", "symbol", "value"],
            ascending=[True, True, True, False],
        ).reset_index(drop=True)

        df.loc[:, "title"] = df.symbol.apply(
            lambda x: all_symbols.get(x, {}).get("title")
        )
        records = df.replace({nan: None}).to_dict(orient="records")

        return [ImfEconomicIndicatorsData.model_validate(r) for r in records]
