"""IMF Economic Indicators Model."""

# pylint: disable=unused-argument,protected-access,too-many-branches,too-many-statements,too-many-locals,too-many-lines
# flake8: noqa: PLR0912

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsData,
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_imf.utils.helpers import (
    detect_indicator_dimensions,
    detect_transform_dimension,
    parse_time_period,
    translate_error_message,
)
from pydantic import ConfigDict, Field, PrivateAttr, field_validator, model_validator

api_prefix = SystemService().system_settings.api_settings.prefix


class ImfEconomicIndicatorsQueryParams(EconomicIndicatorsQueryParams):
    """IMF Economic Indicators Query.

    Symbol format: 'dataflow::identifier' where identifier is either:
    - A table ID (starts with 'H_') for hierarchical table data
    - An indicator code for individual indicator data

    Examples:
    - 'BOP::H_BOP_BOP_AGG_STANDARD_PRESENTATION' - Balance of Payments table
    - 'BOP_AGG::GS_CD,BOP_AGG::GS_DB' - Multiple BOP_AGG indicators (Goods & Services)
    - 'IL::RGV_REVS' - Gold reserves in millions of fine troy ounces
    - 'WEO::NGDP_RPCH' - Real GDP growth (annual only)
    - 'WEO::POILBRE' - Brent crude oil price (use country='G001' for world)
    - 'PCPS::PGOLD' - Gold price per troy ounce (monthly/quarterly available)

    Use `obb.economy.available_indicators(provider='imf')` to discover symbols.
    Use `obb.economy.imf_utils.list_tables()` to see available tables.
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Indicator Symbol",
                # "description": "The IMF indicator series ID.",
                "multiSelect": False,
                "multiple": True,
                "type": "text",
            },
        },
        "country": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Country",
                "description": "Country or region for the table.",
                "type": "endpoint",
                "multiSelect": True,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/imf_utils/indicator_choices",
                "optionsParams": {
                    "symbol": "$symbol",
                    "country": "true",
                    "dimension_values": "$dimension_values",
                },
                "style": {"popupWidth": 600},
            },
        },
        "frequency": {
            "x-widget_config": {
                "label": "Frequency",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf_utils/indicator_choices",
                "optionsParams": {
                    "symbol": "$symbol",
                    "country": "$country",
                    "frequency": "true",
                    "dimension_values": "$dimension_values",
                },
                "description": "The data frequency.",
            },
        },
        "transform": {
            "x-widget_config": {
                "label": "Transform",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf_utils/indicator_choices",
                "optionsParams": {
                    "symbol": "$symbol",
                    "country": "$country",
                    "frequency": "$frequency",
                    "transform": "true",
                    "dimension_values": "$dimension_values",
                },
                "description": "Transformation to apply to the data.",
                "style": {"popupWidth": 600},
            },
        },
        "dimension_values": {
            "x-widget_config": {
                "label": "Dimension Filters",
                "type": "text",
                "value": None,
                "description": "Additional dimension filters in 'DIM_ID:DIM_VALUE' format."
                + " See IMF Dataflow Parameters widget for all possible combinations.",
                "multiple": True,
            },
        },
        "limit": {
            "x-widget_config": {
                "label": "Limit",
                "value": None,
                "description": "Most recent N records to retrieve per series.",
                "type": "number",
            },
        },
    }

    symbol: str | None = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Symbol format: 'dataflow::identifier' where identifier is either:"
        + "\n- A table ID (starts with 'H_') for hierarchical table data"
        + "\n- An indicator code for individual indicator data"
        + "\n\n"
        + "Examples:"
        + "\n    - 'BOP::H_BOP_BOP_AGG_STANDARD_PRESENTATION' - Balance of Payments table"
        + "\n    - 'BOP_AGG::GS_CD,BOP_AGG::GS_DB' - Multiple BOP_AGG indicators (Goods & Services)"
        + "\n    - 'IL::RGV_REVS' - Gold reserves in millions of fine troy ounces"
        + "\n    - 'WEO::NGDP_RPCH' - Real GDP growth (annual only)"
        + "\n    - 'WEO::POILBRE' - Brent crude oil price (use country='G001' for world)"
        + "\n    - 'PCPS::PGOLD' - Gold price per troy ounce (monthly/quarterly available)"
        + "\n\n"
        + "Use `obb.economy.available_indicators(provider='imf')` to discover symbols."
        + " Use `obb.economy.imf_utils.list_tables()` to see available tables."
    )

    country: str | None = Field(
        default=None,
        description="ISO3 country code(s). Use comma-separated values for multiple countries. "
        + "Validated against the dataflow's available countries via constraint API.",
    )

    frequency: str | None = Field(
        default=None,
        description="The frequency of the data. Choices vary by indicator and country."
        + " Common options: 'annual', 'quarter', 'month'."
        + " Use 'all' or '*' to return all available frequencies."
        + " Direct IMF codes (e.g., 'A', 'Q', 'M') are also accepted.",
    )

    transform: str | None = Field(
        default=None,
        description="Transformation to apply to the data. "
        + "User-friendly options: 'index' (raw values), 'yoy' (year-over-year %), 'period' (period-over-period %). "
        + "Use 'all' or '*' to return all available transformations. "
        + "Direct IMF codes (e.g., 'USD', 'IX') are also accepted.",
    )

    dimension_values: list[str] | None = Field(
        default=None,
        description="List of additional dimension filters in 'DIM_ID:DIM_VALUE' format."
        + " Parameter can be entered multiple times.",
    )

    limit: int | None = Field(
        default=None, description="Maximum number of records to retrieve per series."
    )

    pivot: bool = Field(
        default=False,
        description="If True, pivots the data to presentation view with"
        + " 'indicator' and 'country' as the index, date as values.",
    )

    _is_table: bool = PrivateAttr(default=False)
    _dataflow: str | None = PrivateAttr(default=None)
    _table_id: str | None = PrivateAttr(default=None)
    _indicator_codes: list[str] = PrivateAttr(default_factory=list)
    _indicators_by_dataflow: dict = PrivateAttr(default_factory=dict)

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, v):
        """
        Normalize country inputs to ISO3 codes.

        Accepts:
        - ISO3 codes: "USA", "JPN", "GBR"
        - Country names: "United States", "Japan", "United Kingdom"
        - Snake_case names: "united_states", "japan", "united_kingdom"
        - Wildcards: "*" or "all" to include all countries
        - None: Allowed if dimension_values contains a country dimension (validated in model_validator)
        """
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.metadata import ImfMetadata

        # Allow None - will be validated in model_validator with dimension_values check
        if not v:
            return None

        # Split by comma, handling potential spaces and filtering empty strings
        items = [c.strip() for c in v.split(",") if c.strip()]

        if not items:
            return None

        # Check for wildcards - return early without metadata lookup
        if len(items) == 1 and items[0].lower() in ("*", "all"):
            return "*"

        metadata = ImfMetadata()
        country_codes = metadata._codelist_cache.get("CL_COUNTRY", {})

        # Build lookup tables
        code_set = set(country_codes.keys())
        name_to_code: dict[str, str] = {}
        for code, name in country_codes.items():
            # Add lowercase name
            name_to_code[name.lower()] = code
            # Add snake_case version (replace spaces with underscores)
            snake_name = (
                name.lower()
                .replace(" ", "_")
                .replace(",", "")
                .replace(".", "")
                .replace("'", "")
            )
            name_to_code[snake_name] = code

        result: list[str] = []

        for item in items:
            item_upper = item.upper().strip()
            item_lower = item.lower().strip().replace(" ", "_")

            # Handle wildcards in mixed input
            if item_lower in ("*", "all"):
                return "*"  # Wildcard overrides everything

            # Check if it's already an ISO3 code
            if item_upper in code_set:
                result.append(item_upper)
            # Check if it's a name (with spaces or snake_case)
            elif item_lower in name_to_code:
                result.append(name_to_code[item_lower])
            # Try with original casing as lowercase lookup
            elif item.lower() in name_to_code:
                result.append(name_to_code[item.lower()])
            else:
                # Not found - pass through as uppercase (will fail later with clearer error)
                result.append(item_upper)

        return ",".join(result)

    @model_validator(mode="after")
    def parse_and_validate_symbols(self):
        """Parse symbols and validate table/indicator constraints."""
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.metadata import ImfMetadata

        if not self.symbol:
            raise ValueError("symbol is required.")

        country_dimensions = {"COUNTRY", "REF_AREA", "JURISDICTION", "AREA"}
        frequency_dimensions = {"FREQUENCY", "FREQ"}
        transform_dimensions = {
            "UNIT_MEASURE",
            "UNIT",
            "TRANSFORMATION",
            "TYPE_OF_TRANSFORMATION",
        }

        remaining_dimension_values: list[str] = []

        if self.dimension_values:
            for dv in self.dimension_values:
                if ":" not in dv:
                    remaining_dimension_values.append(dv)
                    continue
                dim_id, dim_value = dv.split(":", 1)
                dim_id_upper = dim_id.strip().upper()
                dim_value = dim_value.strip()

                # dimension_values OVERRIDES the country parameter
                if dim_id_upper in country_dimensions:
                    object.__setattr__(self, "country", dim_value)
                # dimension_values OVERRIDES the frequency parameter
                elif dim_id_upper in frequency_dimensions:
                    object.__setattr__(self, "frequency", dim_value)
                # dimension_values OVERRIDES the transform parameter
                elif dim_id_upper in transform_dimensions:
                    object.__setattr__(self, "transform", dim_value)
                # Keep dimension_values that are not consumed by country/frequency/transform
                else:
                    remaining_dimension_values.append(dv)

            # Update dimension_values to only contain non-consumed dimensions
            object.__setattr__(
                self,
                "dimension_values",
                remaining_dimension_values if remaining_dimension_values else None,
            )

        # Validate country requirement - must have country by now
        if not self.country:
            raise ValueError(
                "Country is required. Provide via 'country' parameter or include a country "
                "dimension (COUNTRY, REF_AREA, JURISDICTION, AREA) in 'dimension_values'."
            )

        symbols = [
            s.strip()
            for s in self.symbol.split(",")  #  type: ignore  # pylint: disable=E1101
        ]
        tables: list[str] = []
        indicators: list[tuple[str, str]] = []
        dataflows_seen: set[str] = set()

        for sym in symbols:
            if "::" not in sym:
                raise ValueError(
                    f"Invalid symbol format '{sym}'. Expected 'dataflow::identifier'. "
                    "Use `available_indicators()` or `list_tables()` to find valid symbols."
                )

            parts = sym.split("::", 1)
            dataflow = parts[0].strip().upper()
            identifier = parts[1].strip()

            if not identifier:
                raise ValueError(
                    f"Invalid symbol format '{sym}'. Identifier cannot be empty. "
                    "Expected 'dataflow::identifier'."
                )

            dataflows_seen.add(dataflow)
            # Tables can start with H_ or be any valid hierarchy ID for the dataflow
            is_table = False

            if identifier.startswith("H_"):
                is_table = True
            else:
                metadata = ImfMetadata()
                try:
                    hierarchies = metadata.get_dataflow_hierarchies(dataflow)
                    hierarchy_ids = {h.get("id") for h in hierarchies}
                    if identifier in hierarchy_ids:
                        is_table = True
                except Exception:  # noqa
                    pass  # If we can't check, assume it's an indicator

            if is_table:
                tables.append(sym)
            else:
                indicators.append((dataflow, identifier))

        if tables and indicators:
            raise ValueError(
                "Cannot mix tables and indicators in the same request. "
                f"Got tables: {tables} and indicators: {[f'{d}::{c}' for d, c in indicators]}"
            )

        if len(tables) > 1:
            raise ValueError(
                f"Only one table can be requested at a time. Got: {tables}"
            )

        if tables:
            self._is_table = True
            parts = tables[0].split("::", 1)
            self._dataflow = parts[0].upper()
            self._table_id = parts[1]
        else:
            self._is_table = False
            indicators_by_df: dict[str, list[str]] = {}

            for dataflow, code in indicators:
                if dataflow not in indicators_by_df:
                    indicators_by_df[dataflow] = []

                indicators_by_df[dataflow].append(code)

            self._indicators_by_dataflow = indicators_by_df

            if len(dataflows_seen) == 1:
                self._dataflow = list(dataflows_seen)[0]
                self._indicator_codes = [code for _, code in indicators]
            else:
                self._dataflow = None  # Multiple dataflows
                self._indicator_codes = []

            # Validate country, frequency, and transform using constraints API
            self._validate_indicator_params()

        return self

    def _validate_indicator_params(self):
        """Validate country, frequency, and transform using the constraints API."""
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.metadata import ImfMetadata

        metadata = ImfMetadata()

        def build_key_up_to(target_dim: str) -> str:
            """Build constraint key up to (and including) target dimension."""
            key_parts: list[str] = []
            countries = self.country.split(",") if self.country else []  # type: ignore  # pylint: disable=E1101
            countries_str = (
                "*"
                if countries in ["*", "all"]
                else "+".join([c.upper() for c in countries])
            )

            for dim_id in dim_order:
                if dim_id == target_dim:
                    key_parts.append("*")
                    break
                if dim_id == country_dim:
                    key_parts.append(countries_str if countries_str else "*")
                elif dim_id == indicator_dim:
                    # Use all indicator codes for this dataflow
                    key_parts.append(
                        "+".join(indicator_codes) if indicator_codes else "*"
                    )
                elif dim_id == freq_dim:
                    freq_map = {
                        "annual": "A",
                        "quarter": "Q",
                        "month": "M",
                        "day": "D",
                    }
                    freq_val = freq_map.get(str(self.frequency).lower(), self.frequency)
                    key_parts.append(str(freq_val) if self.frequency else "*")
                elif dim_id == transform_dim:
                    key_parts.append(str(self.transform) if self.transform else "*")
                else:
                    key_parts.append("*")
            return ".".join(key_parts)

        def get_available_values(dim_id: str, dataflow_id: str) -> list[str]:
            """Get available values for a dimension using constraints API."""
            key = build_key_up_to(dim_id)
            constraints = metadata.get_available_constraints(
                dataflow_id=dataflow_id,
                key=key,
                component_id=dim_id,
            )
            for kv in constraints.get("key_values", []):
                if kv.get("id") == dim_id:
                    return kv.get("values", [])
            return []

        # For each dataflow, validate the parameters
        for dataflow_id, indicator_codes in self._indicators_by_dataflow.items():
            df_obj = metadata.dataflows.get(dataflow_id, {})

            if not df_obj:
                continue

            dsd_id = df_obj.get("structureRef", {}).get("id")
            dsd = metadata.datastructures.get(dsd_id, {})
            dimensions = dsd.get("dimensions", [])
            sorted_dims = sorted(
                [d for d in dimensions if d.get("id") != "TIME_PERIOD"],
                key=lambda x: int(x.get("position", 0)),
            )
            dim_order = [d["id"] for d in sorted_dims]
            country_dim = (
                "COUNTRY"
                if "COUNTRY" in dim_order
                else "JURISDICTION" if "JURISDICTION" in dim_order else "REF_AREA"
            )
            freq_dim = "FREQUENCY" if "FREQUENCY" in dim_order else "FREQ"

            transform_dim, _, _, _ = detect_transform_dimension(dataflow_id)
            indicator_dim_candidates = [
                "INDICATOR",
                "COICOP_1999",
                "SERIES",
                "ITEM",
                "BOP_ACCOUNTING_ENTRY",
                "ACTIVITY",
            ]
            indicator_dim = next(
                (d for d in indicator_dim_candidates if d in dim_order), None
            )

            # Validate country
            if self.country and country_dim in dim_order:
                available_countries = get_available_values(country_dim, dataflow_id)
                if available_countries:
                    countries = [c.strip().upper() for c in self.country.split(",")]  # type: ignore  # pylint: disable=E1101
                    invalid = [
                        c
                        for c in countries
                        if c not in available_countries and c not in ("*", "all")
                    ]
                    if invalid:
                        raise ValueError(
                            f"Invalid value(s) for dimension 'country': {invalid}. "
                            + f"Given prior selections {{'indicator': '{','.join(indicator_codes)}'}}, "
                            + f"available values are: {sorted(available_countries)}"
                        )

            if (
                self.frequency
                and self.frequency.lower() not in ("all", "*")  # type: ignore  # pylint: disable=E1101
                and freq_dim in dim_order
            ):
                freq_map = {"annual": "A", "quarter": "Q", "month": "M", "day": "D"}
                freq_val = freq_map.get(str(self.frequency).lower(), self.frequency)
                available_freqs = get_available_values(freq_dim, dataflow_id)
                if available_freqs and freq_val not in available_freqs:
                    indicator_str = ",".join(indicator_codes)
                    raise ValueError(
                        f"Invalid value(s) for dimension 'frequency': ['{freq_val}']. "
                        f"Given prior selections {{'country': '{self.country}', "
                        f"'indicator': '{indicator_str}'}}, "
                        f"available values are: {available_freqs}"
                    )

            # Validate transform (skip if 'all' or '*')
            if (
                self.transform
                and self.transform.lower() not in ("all", "*")  # type: ignore  # pylint: disable=E1101
                and transform_dim
                and transform_dim in dim_order
            ):
                _, _, transform_lookup, unit_lookup = detect_transform_dimension(
                    dataflow_id
                )
                # Resolve user-friendly name to code
                transform_val = self.transform.strip().lower()  # type: ignore  # pylint: disable=E1101
                resolved_code = transform_lookup.get(
                    transform_val, unit_lookup.get(transform_val, self.transform)
                )
                available_transforms = get_available_values(transform_dim, dataflow_id)

                if available_transforms and resolved_code not in available_transforms:
                    indicator_str = ",".join(indicator_codes)
                    raise ValueError(
                        f"Invalid value(s) for dimension 'transform': ['{resolved_code}']. "
                        f"Given prior selections {{'country': '{self.country}', "
                        f"'indicator': '{indicator_str}'}}, "
                        f"available values are: {available_transforms}"
                    )


class ImfEconomicIndicatorsData(EconomicIndicatorsData):
    """IMF Economic Indicators Data."""

    __alias__dict__ = {
        "title": "Indicator",
        "country": "Country",
        "symbol_root": "parent_code",
    }

    @field_validator("scale", "unit", "title", "description", "value", mode="before")
    @classmethod
    def _convert_nan_to_none(cls, v):
        """Convert NaN float values to None for string fields."""
        if v is None or str(v).lower() == "nan":
            return None
        return v

    model_config = ConfigDict(
        extra="allow",  # Allow dynamic dimension fields from any dataflow
        json_schema_extra={
            "x-widget_config": {
                "$.name": "IMF Indicators",
                "$.refetchInterval": False,
                "$.data": {
                    "table": {
                        "columnsDefs": [
                            {
                                "field": "title",
                                "headerName": "Title",
                                "renderFn": "hoverCard",
                                "renderFnParams": {
                                    "hoverCard": {
                                        "cellField": "title",
                                        "markdown": "{description}",
                                    }
                                },
                            },
                            {
                                "field": "description",
                                "hide": True,
                            },
                            {
                                "field": "symbol",
                                "pinned": False,
                            },
                            {
                                "field": "value",
                                "pinned": "left",
                            },
                        ]
                    }
                },
            },
        },
    )

    unit: str | None = Field(
        default=None,
        description="The unit of measurement.",
    )
    unit_multiplier: int | float | None = Field(
        default=None,
        description="The multiplier for the unit.",
    )
    scale: str | None = Field(
        default=None,
        description="The scale/multiplier of the value.",
    )
    order: int | float | None = Field(
        default=None,
        description="Sort order within the table hierarchy.",
    )
    level: int | None = Field(
        default=None,
        description="Indentation level in the table hierarchy.",
    )
    title: str | None = Field(
        default=None,
        description="Human-readable title of the series.",
        alias="Indicator",
    )
    description: str | None = Field(
        default=None,
        description="Description of the indicator.",
    )
    country_code: str | None = Field(
        default=None,
        description="ISO3 country code.",
    )


class ImfEconomicIndicatorsFetcher(
    Fetcher[ImfEconomicIndicatorsQueryParams, list[ImfEconomicIndicatorsData]]
):
    """IMF Economic Indicators Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfEconomicIndicatorsQueryParams:
        """Transform the query."""
        try:
            return ImfEconomicIndicatorsQueryParams(**params)
        except Exception as e:  # noqa
            raise OpenBBError(e) from e

    @staticmethod
    async def aextract_data(
        query: ImfEconomicIndicatorsQueryParams,
        credentials: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        from datetime import datetime  # noqa
        from openbb_imf.utils.query_builder import ImfQueryBuilder
        from openbb_imf.utils.table_builder import ImfTableBuilder

        countries = query.country.split(",")  # type: ignore
        countries_str = "+".join([c.upper() for c in countries])
        frequency_map = {"annual": "A", "quarter": "Q", "month": "M", "day": "D"}
        frequency = frequency_map.get(query.frequency) or query.frequency  # type: ignore
        start_date = query.start_date.strftime("%Y-%m-%d") if query.start_date else None
        end_date = query.end_date.strftime("%Y-%m-%d") if query.end_date else None

        # Parse dimension_values into a dict of DIM_ID -> DIM_VALUE
        # Input format: list of "DIM_ID:VALUE" strings
        # Example: ["SECTOR:S13", "GFS_GRP:XDC"] -> {"SECTOR": "S13", "GFS_GRP": "XDC"}
        # Handles lowercase inputs: "unit:xdc" -> {"UNIT": "XDC"}
        extra_dimensions: dict[str, str] = {}
        if query.dimension_values:
            for dv in query.dimension_values:
                # Each dv should be "DIMENSION:VALUE"
                if not dv or not isinstance(dv, str):
                    continue
                # Handle comma-separated pairs in a single string
                pairs = [p.strip() for p in dv.split(",") if p.strip()]
                for pair in pairs:
                    if ":" in pair:
                        dim_id, dim_value = pair.split(":", 1)
                        # Uppercase both dimension ID and value for IMF API
                        extra_dimensions[dim_id.strip().upper()] = (
                            dim_value.strip().upper()
                        )

        if query._is_table:
            # Table mode: use ImfTableBuilder (single dataflow only)
            dataflow = query._dataflow
            if not dataflow:
                raise OpenBBError("Could not determine dataflow from symbol.")

            params: dict[str, Any] = {
                "COUNTRY": countries_str,
                "FREQUENCY": frequency,
            }

            # Handle special dimensions for certain dataflows
            # GFS dataflows: GFS_BS, GFS_SOO, GFS_COFOG, GFS_SFCP, GFS_SSUC, QGFS
            if dataflow.startswith("GFS_") or dataflow == "QGFS":
                params["SECTOR"] = "*"
                params["GFS_GRP"] = "*"
            elif dataflow.startswith("FSIC") or dataflow == "IRFCL":
                params["SECTOR"] = "*"
            elif dataflow.startswith("BOP") or dataflow == "DIP":
                params["TYPE_OF_TRANSFORMATION"] = "*"
            elif dataflow == "ISORA_LATEST_DATA_PUB":
                params["INDICATOR"] = "*"

            # Apply user-specified dimension filters (overrides defaults above)
            if extra_dimensions:
                params.update(extra_dimensions)

            # Handle transform/unit for table mode
            if query.transform:
                transform_val = query.transform.strip().lower()
                transform_dim, unit_dim, transform_lookup, unit_lookup = (
                    detect_transform_dimension(dataflow)
                )
                applied = False
                resolved_code = None

                # Try transform dimension first
                if transform_dim:
                    if transform_val in ("all", "*"):
                        params[transform_dim] = "*"
                        applied = True
                    elif transform_val in transform_lookup:
                        resolved_code = transform_lookup[transform_val]
                        params[transform_dim] = resolved_code
                        applied = True

                # Try unit dimension if not applied to transform
                if not applied and unit_dim:
                    if transform_val in ("all", "*"):
                        params[unit_dim] = "*"
                        applied = True
                    elif transform_val in unit_lookup:
                        resolved_code = unit_lookup[transform_val]
                        params[unit_dim] = resolved_code
                        applied = True

                # Raise error if transform value is not valid for dataflow
                if not applied:
                    available = []
                    if transform_lookup:
                        available.extend(
                            sorted(
                                set(transform_lookup.keys())
                                - set(transform_lookup.values())
                            )
                        )
                    if unit_lookup:
                        available.extend(
                            sorted(set(unit_lookup.keys()) - set(unit_lookup.values()))
                        )
                    if not transform_dim and not unit_dim:
                        raise OpenBBError(
                            f"Dataflow '{dataflow}' does not support transform/unit parameter."
                        )
                    raise OpenBBError(
                        f"Invalid transform value '{query.transform}' for dataflow '{dataflow}'. "
                        f"Available options: {', '.join(available) if available else 'none'}"
                    )

            # We request one extra period to ensure value carry-forward for STATUS="NA" obs.
            if query.limit is not None and start_date is None:
                current_year = datetime.now().year
                if frequency == "A":
                    start_year = current_year - query.limit - 1
                    start_date = str(start_year)  # Just year for annual
                elif frequency == "Q":
                    years_back = (query.limit + 7) // 4 + 1
                    start_year = current_year - years_back
                    start_date = str(start_year)
                elif frequency == "M":
                    years_back = (query.limit + 23) // 12 + 1
                    start_year = current_year - years_back
                    start_date = str(start_year)

            table_builder = ImfTableBuilder()

            try:
                result = table_builder.get_table(
                    dataflow=dataflow,
                    table_id=query._table_id,
                    start_date=start_date,
                    end_date=end_date,
                    **params,
                )
                return {
                    "mode": "table",
                    "data": result.get("data", []),
                    "table_metadata": result.get("table_metadata", {}),
                    "series_metadata": result.get("series_metadata", {}),
                }
            except (ValueError, OpenBBError) as e:
                # Translate IMF dimension codes to user-friendly parameter names
                raise OpenBBError(translate_error_message(str(e))) from e

        else:
            # Indicator mode: support multiple dataflows
            query_builder = ImfQueryBuilder()
            all_data: list[dict] = []
            all_metadata: dict = {}
            indicators_by_df = query._indicators_by_dataflow

            if not indicators_by_df:
                raise OpenBBError("No indicators specified.")

            # Fetch data for each dataflow
            for dataflow, indicator_codes in indicators_by_df.items():
                params = {
                    "COUNTRY": countries_str,
                    "FREQUENCY": frequency,
                }

                # Apply user-specified dimension filters
                if extra_dimensions:
                    params.update(extra_dimensions)

                # Handle transform/unit parameter per dataflow
                if query.transform:
                    transform_val = query.transform.strip().lower()
                    transform_dim, unit_dim, transform_lookup, unit_lookup = (
                        detect_transform_dimension(dataflow)
                    )
                    applied = False
                    resolved_code = None

                    # Try transform dimension first
                    if transform_dim:
                        if transform_val in ("all", "*"):
                            params[transform_dim] = "*"
                            applied = True
                        elif transform_val in transform_lookup:
                            resolved_code = transform_lookup[transform_val]
                            params[transform_dim] = resolved_code
                            applied = True

                    # Try unit dimension if not applied to transform
                    if not applied and unit_dim:
                        if transform_val in ("all", "*"):
                            params[unit_dim] = "*"
                            applied = True
                        elif transform_val in unit_lookup:
                            resolved_code = unit_lookup[transform_val]
                            params[unit_dim] = resolved_code
                            applied = True

                    # Raise error if transform value is not valid for dataflow
                    if not applied:
                        available = []
                        if transform_lookup:
                            available.extend(
                                sorted(
                                    set(transform_lookup.keys())
                                    - set(transform_lookup.values())
                                )
                            )
                        if unit_lookup:
                            available.extend(
                                sorted(
                                    set(unit_lookup.keys()) - set(unit_lookup.values())
                                )
                            )
                        if not transform_dim and not unit_dim:
                            raise OpenBBError(
                                f"Dataflow '{dataflow}' does not support transform/unit parameter."
                            )
                        raise OpenBBError(
                            f"Invalid transform value '{query.transform}' for dataflow '{dataflow}'. "
                            f"Available options: {', '.join(available) if available else 'none'}"
                        )

                if query.limit is not None:
                    params["lastNObservations"] = query.limit

                # Detect indicator dimensions for this dataflow
                dimension_codes = detect_indicator_dimensions(
                    dataflow, indicator_codes, query_builder.metadata
                )

                # Add indicator codes to appropriate dimensions
                for dim_id, codes in dimension_codes.items():
                    params[dim_id] = "+".join(codes)

                try:
                    result = query_builder.fetch_data(
                        dataflow=dataflow,
                        start_date=start_date,
                        end_date=end_date,
                        **params,
                    )
                    # Add dataflow info to each record
                    for record in result.get("data", []):
                        record["_dataflow"] = dataflow
                    all_data.extend(result.get("data", []))
                    all_metadata[dataflow] = result.get("metadata", {})
                except ValueError as e:
                    # Translate IMF codes to user-friendly names and raise as OpenBBError
                    raise OpenBBError(translate_error_message(str(e))) from e

            return {
                "mode": "indicator",
                "data": all_data,
                "metadata": all_metadata,
            }

    @staticmethod
    def transform_data(
        query: ImfEconomicIndicatorsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[list[ImfEconomicIndicatorsData]]:
        """Transform the data."""
        mode = data.get("mode", "indicator")
        row_data = data.get("data", [])

        if not row_data:
            raise EmptyDataError("No data returned for the given query parameters.")

        result: list = []
        metadata: dict = {}

        if mode == "table":
            metadata = {
                "table": data.get("table_metadata", {}),
                "series": data.get("series_metadata", {}),
            }
        else:
            metadata = data.get("metadata", {})

        for item in row_data:
            # Filter by date range if needed (IMF API date filtering can be inconsistent)
            item_date = item.get("TIME_PERIOD") or item.get("date")

            # Normalize date format for comparison and storage
            if item_date:
                item_date = parse_time_period(item_date)

            if (
                query.start_date
                and item_date
                and item_date < query.start_date.strftime("%Y-%m-%d")
            ):
                continue
            if (
                query.end_date
                and item_date
                and item_date > query.end_date.strftime("%Y-%m-%d")
            ):
                continue

            # Extract indicator code from various possible fields
            symbol = (
                item.get("series_id")  # Prefer full series_id (dataflow::codes)
                or item.get("INDICATOR_code")
                or item.get("BOP_ACCOUNTING_ENTRY_code")
                or item.get("SERIES_code")
                or item.get("ITEM_code")
                or item.get("indicator_code")
                or item.get("symbol")
            )
            # Get country info (ISORA uses JURISDICTION instead of COUNTRY)
            country = (
                item.get("COUNTRY") or item.get("JURISDICTION") or item.get("country")
            )
            country_code = (
                item.get("country_code")
                or item.get("COUNTRY_code")
                or item.get("JURISDICTION_code")
            )
            # Get hierarchy info (for table mode)
            order = item.get("order")
            level = item.get("level")
            parent_id = item.get("parent_id")
            is_category_header = item.get("is_category_header", False)
            # Get title/label - use the title from table_builder which is the indicator name
            # For data rows, this is the specific indicator (e.g., "Direct investment, Equity...")
            # For headers, this is the category name with units (e.g., "Goods (Millions, US Dollar)")
            title = item.get("title") or item.get("INDICATOR") or item.get("label")
            # Get value - use explicit None check to handle 0 correctly
            value = item.get("OBS_VALUE")

            if value is None:
                value = item.get("value")

            # Sanitize scale - convert nan/None to None, ensure string type
            scale_val = item.get("scale") or item.get("SCALE")
            if scale_val is not None:
                if str(scale_val).lower() == "nan":
                    scale_val = None
                elif not isinstance(scale_val, str):
                    scale_val = str(scale_val) if scale_val else None

            # Sanitize unit - convert nan/None to None, ensure string type
            unit_val = (
                item.get("unit")
                or item.get("UNIT")
                or item.get("TYPE_OF_TRANSFORMATION")
            )
            if unit_val is not None:
                if str(unit_val).lower() == "nan":
                    unit_val = None
                elif not isinstance(unit_val, str):
                    unit_val = str(unit_val) if unit_val else None

            new_row = {
                "date": item_date,
                "symbol": symbol,
                "country": country,
                "country_code": country_code,
                "value": value,
                "unit": unit_val,
                "unit_multiplier": item.get("unit_multiplier") or item.get("UNIT_MULT"),
                "scale": scale_val,
                "order": order,
                "level": level,
                "symbol_root": parent_id,  # Map to symbol_root for base class
                "parent_id": parent_id,  # Also keep as parent_id
                "parent_code": item.get(
                    "parent_code"
                ),  # Resolved parent indicator code
                "hierarchy_node_id": item.get(
                    "hierarchy_node_id"
                ),  # Hierarchy node ID for parent tracing
                "title": title,
                "description": item.get("description"),
                "series_id": item.get("series_id"),
                "is_category_header": is_category_header,
            }

            # Dynamically add ALL dimension fields from the raw data
            # This captures any dimension like SECTOR, PRICE_TYPE, DV_TYPE,
            # COUNTERPART_COUNTRY, etc. with both label and code
            for key, val in item.items():
                # Skip fields we've already handled
                if key in new_row:
                    continue
                # Skip internal/metadata fields
                if key in {
                    "TIME_PERIOD",
                    "OBS_VALUE",
                    "value",
                    "indicator_codes",
                    "COUNTRY",
                    "country_code",
                    "SCALE",
                    "UNIT",
                    "unit_multiplier",
                }:
                    continue
                # Include dimension fields (UPPERCASE) and their _code variants
                if key.isupper() or key.endswith("_code"):
                    # Convert to snake_case for the field name
                    field_name = key.lower()
                    new_row[field_name] = val

            result.append(new_row)

        # Check if all records were filtered out
        if not result:
            raise EmptyDataError(
                "No data remaining after applying date filters. "
                "Try adjusting start_date and end_date parameters."
            )

        result.sort(
            key=lambda x: (
                x["order"] if x.get("order") is not None else 9999,
                x["date"] if x.get("date") else "",
                x["country"] or "",
            )
        )
        to_exclude = [
            "is_category_header",
            "hierarchy_node_id",
            "parent_id",
            "indicator_code",
            "parent_code",
            "series_id",
        ]
        # Non-pivot mode: return flat list
        if not query.pivot:
            new_data: list = []
            for row in result:
                if not row.get("date"):
                    continue
                # Exclude internal fields
                row["symbol"] = row.get("series_id")
                for field in to_exclude:
                    _ = row.pop(field, None)
                new_data.append(ImfEconomicIndicatorsData.model_validate(row))

            return AnnotatedResult(
                result=new_data,
                metadata=metadata,
            )

        # Pivot mode: use the table_presentation utility module
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.table_presentation import pivot_table_data

        result_df = pivot_table_data(
            result=result,
            country=query.country,  # type: ignore
            limit=query.limit,
            metadata=metadata,
        )
        result_df = result_df.fillna(0).reset_index()

        return AnnotatedResult(
            result=[
                ImfEconomicIndicatorsData.model_validate(r)
                for r in result_df.to_dict(orient="records")
            ],
            metadata=metadata,
        )
