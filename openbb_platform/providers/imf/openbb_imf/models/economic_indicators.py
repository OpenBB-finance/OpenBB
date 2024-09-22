"""IMF Economic Indicators Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsData,
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_imf.utils.constants import IRFCL_PRESET, IRFCL_TABLES
from openbb_imf.utils.irfcl_helpers import (
    load_country_to_code_map,
    load_irfcl_symbols,
    validate_countries,
)


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
        + " Use 'IRFCL' to get all the data from the set of indicators."
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
    """,
    )
    frequency: Literal["annual", "quarter", "month"] = Field(
        default="quarter",
        description="Frequency of the data.",
    )


class ImfEconomicIndicatorsData(EconomicIndicatorsData):
    """IMF Economic Indicators Data."""

    __alias_dict__ = {
        "symbol_root": "parent",
    }

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
    order: Optional[int] = Field(
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
        symbols = "IRFCL" if ("all" in symbols or "IRFCL" in symbols) else symbols
        if symbols == "IRFCL" and not (countries or countries == "all"):
            raise OpenBBError(
                f"The selected symbol(s), {params.get('symbol')}, requires a single country for the 'country' parameter."
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
        from openbb_imf.utils.irfcl_helpers import _get_irfcl_data

        try:
            res = await _get_irfcl_data(**query.model_dump(exclude_none=True))
        except OpenBBError as e:
            raise e from e
        if not res:
            raise EmptyDataError("No results returned for the query.")
        return res

    @staticmethod
    def transform_data(
        query: ImfEconomicIndicatorsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[ImfEconomicIndicatorsData]:
        """Transform the data."""
        # pylint: disable = import-outside-toplevel
        from pandas import Categorical, DataFrame

        if not data:
            raise EmptyDataError("The data is empty.")

        all_symbols = load_irfcl_symbols()
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
            by=["date", "symbol", "parent", "value"],
            ascending=[True, True, True, False],
        ).reset_index(drop=True)

        return [ImfEconomicIndicatorsData(**d) for d in df.to_dict(orient="records")]
