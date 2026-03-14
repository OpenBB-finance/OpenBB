"""OECD Economic Indicators Model — generic fetcher for ALL OECD dataflows."""

# pylint: disable=unused-argument,too-many-branches,protected-access,too-many-instance-attributes,too-many-statements,too-many-locals,too-many-return-statements

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsData,
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, PrivateAttr, field_validator, model_validator

api_prefix = SystemService().system_settings.api_settings.prefix


class OecdEconomicIndicatorsQueryParams(EconomicIndicatorsQueryParams):
    """OECD Economic Indicators Query."""

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "multiSelect": False,
                "multiple": True,
                "type": "text",
            },
        },
        "country": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "multiSelect": True,
                "optionsEndpoint": f"{api_prefix}/oecd_utils/indicator_choices",
                "optionsParams": {
                    "symbol": "$symbol",
                    "country": "true",
                    "dimension_values": "$dimension_values",
                },
                "style": {"popupWidth": 500},
            },
        },
        "frequency": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/indicator_choices",
                "optionsParams": {
                    "symbol": "$symbol",
                    "country": "$country",
                    "frequency": "true",
                    "dimension_values": "$dimension_values",
                },
            },
        },
        "transform": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/indicator_choices",
                "optionsParams": {
                    "symbol": "$symbol",
                    "country": "$country",
                    "frequency": "$frequency",
                    "transform": "true",
                    "dimension_values": "$dimension_values",
                },
                "style": {"popupWidth": 500},
            },
        },
        "dimension_values": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "text",
                "value": None,
                "multiple": True,
                "multiSelect": False,
            },
        },
        "limit": {
            "x-widget_config": {
                "label": "Limit",
                "type": "number",
            },
        },
    }

    symbol: str = Field(
        description=(
            "OECD indicator symbol(s). Format: 'DATAFLOW::INDICATOR' or "
            "'DATAFLOW::TABLE_ID'. Multiple symbols from the same dataflow "
            "can be comma-separated."
        ),
    )
    country: str | None = Field(
        default=None,
        description="Country name or ISO code. Comma-separated for multiples. 'all' for all.",
    )
    frequency: str | None = Field(
        default=None,
        description="Frequency: 'annual'/'yearly', 'quarterly'/'quarter', 'monthly'/'month', or SDMX code (A/Q/M).",
    )
    transform: str | None = Field(
        default=None,
        description="Transformation code (dataflow-specific, e.g. 'GY' for growth rate).",
    )
    dimension_values: list[str] | str | None = Field(
        default=None,
        description=(
            "Additional dimension constraints. Format: 'DIM_ID:VALUE'. e.g. ['SECTOR:S1', 'UNIT_MEASURE:USD_PPP']"
        ),
    )
    limit: int | None = Field(
        default=None,
        description="Maximum number of most recent observations per series.",
    )
    pivot: bool = Field(
        default=False,
        description="If True, pivot dates to columns for presentation-table output.",
    )

    # Internal parsed state.
    _is_table: bool = PrivateAttr(default=False)
    _dataflow: str | None = PrivateAttr(default=None)
    _table_id: str | None = PrivateAttr(default=None)
    _indicator_codes: list[str] = PrivateAttr(default_factory=list)
    _indicators_by_dataflow: dict = PrivateAttr(default_factory=dict)

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Normalize country input."""
        if c is None:
            return c
        return c.replace(" ", "_").strip().lower()

    @field_validator("dimension_values", mode="before")
    @classmethod
    def validate_dimension_values(cls, v):
        """Accept a bare string or list; split comma-joined items into a list."""
        if v is None:
            return v
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()] or None
        return list(v)

    @model_validator(mode="after")
    def parse_and_validate_symbols(self):
        """Parse the symbol string into dataflow + indicator codes or table ID."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.metadata import OecdMetadata

        symbol = self.symbol

        if not symbol:
            raise ValueError("Symbol is required.")

        parts = [
            s.strip() for s in symbol.split(",") if s.strip()  # pylint: disable=E1101
        ]
        dataflows: set[str] = set()
        identifiers: list[str] = []

        for part in parts:
            if "::" in part:
                df, identifier = part.split("::", 1)
                dataflows.add(df.strip())
                identifiers.append(identifier.strip())
            else:
                identifiers.append(part.strip())

        if len(dataflows) > 1:
            raise ValueError(
                f"All symbols must be from the same dataflow. Got: {dataflows}"
            )

        if not dataflows and not identifiers:
            raise ValueError("No valid symbols provided.")

        dataflow = dataflows.pop() if dataflows else None
        self._dataflow = dataflow

        if not dataflow:
            self._indicator_codes = identifiers
            return self

        # Detect table mode: check if identifier is a TABLE_IDENTIFIER value.
        metadata = OecdMetadata()

        if len(identifiers) == 1:
            hierarchies = metadata.get_dataflow_hierarchies(dataflow)
            table_ids = {h["id"] for h in hierarchies}
            if identifiers[0] in table_ids:
                self._is_table = True
                self._table_id = identifiers[0]
                return self

        # Indicator mode.
        self._is_table = False
        self._indicator_codes = identifiers
        self._indicators_by_dataflow = {dataflow: identifiers}

        return self


class OecdEconomicIndicatorsData(EconomicIndicatorsData):
    """OECD Economic Indicators Data."""

    __alias_dict__ = {
        "title": "Indicator",
        "country": "Country",
        "symbol_root": "parent_code",
    }

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "x-widget_config": {
                "$.name": "OECD Indicators",
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
                                        "cellField": "description",
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
                        ]
                    }
                },
            },
        },
    )

    unit: str | None = Field(default=None, description="Unit of measurement.")
    unit_multiplier: int | float | None = Field(
        default=None, description="Unit multiplier (power of 10)."
    )
    scale: str | None = Field(
        default=None, description="Scale description (e.g. Thousands, Millions)."
    )
    order: int | float | None = Field(
        default=None, description="Sort order within the table hierarchy."
    )
    level: int | None = Field(
        default=None, description="Indentation level in the table hierarchy."
    )
    title: str | None = Field(
        default=None,
        description="Human-readable title of the series.",
        alias="Indicator",
    )
    description: str | None = Field(default=None, description="Indicator description.")
    country_code: str | None = Field(default=None, description="ISO country code.")

    @field_validator(
        "scale",
        "unit",
        "title",
        "description",
        "value",
        "unit_multiplier",
        "order",
        "level",
        mode="before",
    )
    @classmethod
    def nan_to_none(cls, v):
        """Convert NaN float values to None for optional fields."""
        if not v:
            return None
        if isinstance(v, float) and v != v:  # fast NaN check
            return None
        if isinstance(v, str) and v.strip().lower() == "nan":
            return None
        return v

    @model_validator(mode="before")
    @classmethod
    def _sanitize_extra_nan(cls, values):
        """Replace NaN in extra/dynamic fields so JSON serialization doesn't break."""
        if isinstance(values, dict):
            for k, v in values.items():
                if isinstance(v, float) and v != v:
                    values[k] = None
        return values


class OecdEconomicIndicatorsFetcher(
    Fetcher[OecdEconomicIndicatorsQueryParams, list[OecdEconomicIndicatorsData]]
):
    """OECD Economic Indicators Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> OecdEconomicIndicatorsQueryParams:
        """Transform the query."""
        return OecdEconomicIndicatorsQueryParams(**params)

    @staticmethod
    def extract_data(  # noqa: PLR0912
        query: OecdEconomicIndicatorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Fetch data from OECD for the given indicators or table."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import (
            detect_indicator_dimensions,
            detect_transform_dimension,
        )
        from openbb_oecd.utils.query_builder import OecdQueryBuilder
        from openbb_oecd.utils.table_builder import OecdTableBuilder

        qb = OecdQueryBuilder()
        dataflow = query._dataflow  # noqa: SLF001

        if not dataflow:
            raise OpenBBError(
                "Could not determine dataflow from symbol. Use format 'DATAFLOW::INDICATOR'."
            )

        # Parse dimension_values into extra_dimensions dict.
        extra_dimensions: dict[str, str] = {}
        if query.dimension_values:
            for dv in query.dimension_values:
                if not dv or not isinstance(dv, str):
                    continue
                for pair in (p.strip() for p in dv.split(",") if p.strip()):
                    if ":" in pair:
                        dim_id, dim_value = pair.split(":", 1)
                        extra_dimensions[dim_id.strip().upper()] = (
                            dim_value.strip().upper()
                        )

        # Resolve country codes.
        countries_str = ""
        if query.country:
            countries = qb.metadata.resolve_country_codes(dataflow, query.country)
            if countries:
                countries_str = "+".join(countries)

        # Map frequency to SDMX code.
        freq_map = {
            "annual": "A",
            "annually": "A",
            "yearly": "A",
            "year": "A",
            "quarter": "Q",
            "quarterly": "Q",
            "monthly": "M",
            "month": "M",
        }
        frequency = (
            freq_map.get(str(query.frequency).lower(), query.frequency.upper())  # type: ignore[union-attr]
            if query.frequency
            else None
        )

        start_date = str(query.start_date) if query.start_date else None
        end_date = str(query.end_date) if query.end_date else None

        if query._is_table:
            params: dict[str, Any] = {}

            if countries_str:
                params["REF_AREA"] = countries_str

            if frequency:
                params["FREQ"] = frequency

            # Apply user-specified dimension filters.
            if extra_dimensions:
                params.update(extra_dimensions)

            # Handle transform/unit for table mode.
            if query.transform:
                _apply_transform(
                    query.transform, dataflow, params, detect_transform_dimension
                )

            builder = OecdTableBuilder()

            try:
                result = builder.get_table(
                    dataflow=dataflow,
                    table_id=query._table_id,  # noqa: SLF001
                    start_date=start_date,
                    end_date=end_date,
                    limit=query.limit,
                    **params,
                )
            except (ValueError, OpenBBError) as exc:
                raise OpenBBError(str(exc)) from exc

            return {
                "mode": "table",
                "data": result.get("data", []),
                "table_metadata": result.get("table_metadata", {}),
                "structure": result.get("structure", {}),
                "series_metadata": result.get("series_metadata", {}),
            }

        # ---- INDICATOR MODE ----
        params = {}
        if countries_str:
            params["REF_AREA"] = countries_str
        if frequency:
            params["FREQ"] = frequency

        # Apply user-specified dimension filters.
        if extra_dimensions:
            dsd_dims = qb.metadata.get_dimension_order(dataflow)
            dsd_dim_map = {d.upper(): d for d in dsd_dims}
            invalid_keys: list[str] = []
            for dim_upper, dim_val in extra_dimensions.items():
                canonical = dsd_dim_map.get(dim_upper)
                if canonical is None:
                    invalid_keys.append(dim_upper)
                else:
                    params[canonical] = dim_val
            if invalid_keys:
                raise OpenBBError(
                    f"Invalid dimension(s) for dataflow '{dataflow}': {invalid_keys}. Available dimensions: {dsd_dims}"
                )

        # Handle transform via detect_transform_dimension.
        if query.transform:
            _apply_transform(
                query.transform, dataflow, params, detect_transform_dimension
            )

        # Compound-code decomposition via detect_indicator_dimensions.
        indicator_codes = query._indicator_codes  # noqa: SLF001
        if indicator_codes:
            dimension_codes = detect_indicator_dimensions(
                dataflow, indicator_codes, qb.metadata
            )
            for dim_id, codes in dimension_codes.items():
                params[dim_id] = "+".join(codes)

        # Build content dimension order for symbol construction.
        _SKIP_DIMS = {
            "REF_AREA",
            "COUNTERPART_AREA",
            "JURISDICTION",
            "COUNTRY",
            "AREA",
            "FREQ",
            "FREQUENCY",
            "TIME_PERIOD",
            "UNIT_MEASURE",
            "UNIT_MULT",
            "TRANSFORMATION",
            "ADJUSTMENT",
            "DECIMALS",
            "CURRENCY",
            "PRICE_BASE",
            "TABLE_IDENTIFIER",
            "REF_YEAR_PRICE",
            "CONF_STATUS",
            "OBS_STATUS",
            "BASE_PER",
            "BASE_REF_AREA",
            "CURRENCY_DENOM",
        }
        try:
            all_dims = qb.metadata.get_dimension_order(dataflow)
            content_dims = [d for d in all_dims if d.upper() not in _SKIP_DIMS]
        except Exception:
            content_dims = []

        try:
            result = qb.fetch_data(
                dataflow=dataflow,
                start_date=start_date,
                end_date=end_date,
                limit=query.limit,
                _skip_validation=False,
                **params,
            )
        except Exception as exc:
            raise OpenBBError(f"OECD data fetch failed: {exc}") from exc

        records = result.get("data", [])

        if not records:
            raise EmptyDataError()

        return {
            "mode": "indicator",
            "data": records,
            "metadata": result.get("metadata", {}),
            "content_dims": content_dims,
        }

    @staticmethod
    def transform_data(  # noqa: PLR0912
        query: OecdEconomicIndicatorsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[list[OecdEconomicIndicatorsData]]:
        """Transform the raw data into the output model."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        mode = data.get("mode", "indicator")
        row_data = data.get("data", [])

        if not row_data:
            raise EmptyDataError("No data returned for the given query parameters.")

        result: list[dict] = []
        metadata: dict = {}
        dataflow = query._dataflow or ""  # noqa: SLF001

        if mode == "table":
            metadata = {
                "table": data.get("table_metadata", {}),
                "series": data.get("series_metadata", {}),
            }
            # Build order→code map from the hierarchy structure.
            structure = data.get("structure", {})
            order_to_code: dict[int | float, str] = {}
            for entry in structure.get("indicators", []):
                order_val = entry.get("order")
                if order_val is not None:
                    order_to_code[order_val] = entry.get("code", "")

            # When a single country is queried, REF_AREA is a fixed
            # dimension (not on each row).  Pull it from table_metadata.
            fixed_dims = metadata.get("table", {}).get("fixed_dimensions", {})
            fixed_country = ""
            fixed_country_code = ""
            for dim_key in ("REF_AREA", "COUNTRY", "AREA"):
                if dim_key in fixed_dims:
                    fixed_country = fixed_dims[dim_key].get("label", "")
                    fixed_country_code = fixed_dims[dim_key].get("code", "")
                    break

            for row in row_data:
                time_str = row.get("time_period", "")
                parsed_date = oecd_date_to_python_date(time_str) if time_str else None

                if query.start_date and parsed_date and parsed_date < query.start_date:
                    continue
                if query.end_date and parsed_date and parsed_date > query.end_date:
                    continue

                ind_code = row.get("code", "") or order_to_code.get(
                    row.get("order"), ""
                )
                country = (
                    row.get("ref_area", "") or row.get("country", "") or fixed_country
                )
                country_code = fixed_country_code

                new_row: dict[str, Any] = {
                    "date": parsed_date,
                    "symbol": f"{dataflow}::{ind_code}" if ind_code else "",
                    "country": country,
                    "country_code": country_code,
                    "value": row.get("value"),
                    "unit": row.get("unit_measure"),
                    "unit_multiplier": row.get("unit_mult"),
                    "scale": row.get("scale"),
                    "order": row.get("order"),
                    "level": row.get("level"),
                    "symbol_root": row.get("parent_code"),
                    "title": row.get("label", ""),
                    "description": row.get("description"),
                }
                result.append(new_row)

        else:
            # Indicator mode.
            metadata = data.get("metadata", {})
            content_dims = data.get("content_dims", [])

            _SKIP_TITLE_DIMS = {
                "REF_AREA",
                "FREQ",
                "TIME_PERIOD",
                "UNIT_MEASURE",
                "UNIT_MULT",
                "BASE_REF_AREA",
                "DECIMALS",
                "CURRENCY",
                "TRANSFORMATION",
                "ADJUSTMENT",
                "PRICE_BASE",
                "TABLE_IDENTIFIER",
                "REF_YEAR_PRICE",
                "CONF_STATUS",
                "OBS_STATUS",
                "BASE_PER",
                "CURRENCY_DENOM",
            }
            _SKIP_TITLE_VALUES = {
                "not applicable",
                "total economy",
                "not specified",
                "no breakdown",
                "all activities",
                "total",
                "non transformed data",
            }

            for row in row_data:
                time_str = row.get("TIME_PERIOD", "")
                parsed_date = oecd_date_to_python_date(time_str)
                if parsed_date is None:
                    continue

                if query.start_date and parsed_date < query.start_date:
                    continue
                if query.end_date and parsed_date > query.end_date:
                    continue

                val = row.get("OBS_VALUE")
                if val is None or val == "":
                    continue
                try:
                    if str(val).lower() == "nan":
                        continue
                    val = float(val) if not isinstance(val, (int, float)) else val
                except (ValueError, TypeError):
                    continue

                # Build compound-code symbol from content dims in DSD order.
                code_parts = [row.get(d, "") for d in content_dims if row.get(d)]
                compound_code = "_".join(code_parts)
                symbol_root = code_parts[0] if code_parts else ""

                # Build title from indicator + content dimension labels.
                title_parts: list[str] = []
                for k, v in row.items():
                    if not k.endswith("_label") or not v:
                        continue
                    dim_id = k[:-6]
                    if dim_id in _SKIP_TITLE_DIMS:
                        continue
                    sv = str(v).strip()
                    raw_code = row.get(dim_id, "")
                    if sv.lower() not in _SKIP_TITLE_VALUES and raw_code not in (
                        "_Z",
                        "_T",
                        "_X",
                    ):
                        title_parts.append(sv)

                # Sanitize scale/unit.
                scale_val = row.get("UNIT_MULT_label", "")
                if scale_val and str(scale_val).lower() in ("nan", "units"):
                    scale_val = None

                unit_val = row.get("UNIT_MEASURE_label", row.get("UNIT_MEASURE"))
                if unit_val and str(unit_val).lower() == "nan":
                    unit_val = None

                new_row = {
                    "date": parsed_date,
                    "symbol": (f"{dataflow}::{compound_code}" if compound_code else ""),
                    "country": row.get("REF_AREA_label", row.get("REF_AREA", "")),
                    "country_code": row.get("REF_AREA", ""),
                    "value": val,
                    "unit": unit_val,
                    "title": " - ".join(title_parts) if title_parts else compound_code,
                }

                result.append(new_row)

        if not result:
            raise EmptyDataError(
                "No data remaining after applying date filters. Try adjusting start_date and end_date parameters."
            )

        result.sort(
            key=lambda x: (
                x["order"] if x.get("order") is not None else 9999,
                x["date"] if x.get("date") else "",
                x["country"] or "",
            )
        )

        to_exclude = ["is_category_header"]

        # Non-pivot mode: return flat list.
        if not query.pivot:
            new_data: list[OecdEconomicIndicatorsData] = []
            for row in result:
                if not row.get("date") and not row.get("is_category_header"):
                    continue
                for field in to_exclude:
                    row.pop(field, None)
                new_data.append(OecdEconomicIndicatorsData.model_validate(row))

            return AnnotatedResult(result=new_data, metadata=metadata)

        # Pivot mode.
        from pandas import DataFrame

        df = DataFrame(result)
        if df.empty:
            raise EmptyDataError("No data for pivot.")

        # Determine pivot shape based on cardinality of countries/symbols.
        unique_countries = df["country"].nunique() if "country" in df.columns else 0
        unique_symbols = df["symbol"].nunique() if "symbol" in df.columns else 0

        if unique_countries <= 1:
            # One country: rows=title, columns=date.
            pivot_index = ["title"]
        elif unique_symbols <= 1:
            # Multiple countries, one symbol: rows=country, columns=date.
            pivot_index = ["country"]
        else:
            # Multiple countries, multiple symbols: rows=title+country, columns=date.
            pivot_index = ["title", "country"]

        pivot_index = [c for c in pivot_index if c in df.columns]

        try:
            pivoted = df.pivot_table(
                index=pivot_index,
                columns="date",
                values="value",
                observed=True,
            )
            pivoted.columns = [str(c) for c in pivoted.columns]
            pivoted = pivoted.reset_index()
        except Exception:
            # Fallback: return unpivoted.
            new_data = [
                OecdEconomicIndicatorsData.model_validate(
                    {k: v for k, v in r.items() if k not in to_exclude}
                )
                for r in result
                if r.get("date")
            ]
            return AnnotatedResult(result=new_data, metadata=metadata)

        pivot_records = pivoted.where(pivoted.notna(), other=None).to_dict(
            orient="records"
        )
        return AnnotatedResult(
            result=[
                OecdEconomicIndicatorsData.model_validate(r)
                for r in pivot_records
            ],
            metadata=metadata,
        )


def _apply_transform(
    transform: str,
    dataflow: str,
    params: dict[str, Any],
    detect_fn: Any,
) -> None:
    """Resolve and apply a transform/unit dimension value to *params*.

    Mutates *params* in place.  Raises ``OpenBBError`` if the transform
    value cannot be resolved for the dataflow.
    """
    transform_val = transform.strip().lower()
    transform_dim, unit_dim, transform_lookup, unit_lookup = detect_fn(dataflow)
    applied = False

    if transform_dim:
        if transform_val in ("all", "*"):
            params[transform_dim] = "*"
            applied = True
        elif transform_val in transform_lookup:
            params[transform_dim] = transform_lookup[transform_val]
            applied = True

    if not applied and unit_dim:
        if transform_val in ("all", "*"):
            params[unit_dim] = "*"
            applied = True
        elif transform_val in unit_lookup:
            params[unit_dim] = unit_lookup[transform_val]
            applied = True

    if not applied:
        if not transform_dim and not unit_dim:
            raise OpenBBError(
                f"Dataflow '{dataflow}' does not support transform/unit parameter."
            )
        available: list[str] = []
        if transform_lookup:
            available.extend(
                sorted(set(transform_lookup.keys()) - set(transform_lookup.values()))
            )
        if unit_lookup:
            available.extend(
                sorted(set(unit_lookup.keys()) - set(unit_lookup.values()))
            )
        raise OpenBBError(
            f"Invalid transform value '{transform}' for dataflow '{dataflow}'. "
            f"Available options: {', '.join(available) if available else 'none'}"
        )
