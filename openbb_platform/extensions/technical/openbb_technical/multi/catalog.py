"""Introspected catalogue of every registered technical indicator."""

import importlib
import inspect
from typing import Any, Literal, get_args, get_origin, get_type_hints

from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field
from pydantic.fields import FieldInfo

router = Router(prefix="", description="Indicator catalogue.")


CatalogCategory = Literal[
    "overlay",
    "oscillator",
    "volatility",
    "volume",
    "trend",
    "signal",
    "structure",
    "stats",
    "multi",
    "all",
]


class IndicatorParam(Data):
    """One input parameter of an indicator endpoint.

    Parameters
    ----------
    name : str
        Parameter name as accepted by the indicator endpoint.
    type : str
        Stable, human-readable rendering of the parameter's Python type
        annotation, e.g. ``"int"`` or ``"Literal['sma', 'ema']"``.
    default : Any, optional
        Default value applied when the caller omits the parameter. ``None``
        for required fields or when the default is not JSON-serialisable.
    description : str, optional
        Human-readable parameter description sourced from the Pydantic
        ``Field`` description.
    choices : list[str], optional
        Allowed values when the parameter is a ``Literal``; ``None``
        otherwise.
    constraints : dict[str, Any], optional
        Pydantic numeric constraints (``gt``, ``ge``, ``lt``, ``le``,
        ``multiple_of``, ``min_length``, ``max_length``) when present.
    """

    name: str = Field(
        description="Parameter name as accepted by the indicator endpoint."
    )
    type: str = Field(
        description="Stable, human-readable rendering of the parameter's Python type annotation, e.g. ``\"int\"`` or ``\"Literal['sma', 'ema']\"``."
    )
    default: Any | None = Field(
        default=None,
        description="Default value applied when the caller omits the parameter. ``None`` for required fields or when the default is not JSON-serialisable.",
    )
    description: str | None = Field(
        default=None,
        description="Human-readable parameter description sourced from the Pydantic ``Field`` description.",
    )
    choices: list[str] | None = Field(
        default=None,
        description="Allowed values when the parameter is a ``Literal``; ``None`` otherwise.",
    )
    constraints: dict[str, Any] | None = Field(
        default=None,
        description="Pydantic numeric constraints (``gt``, ``ge``, ``lt``, ``le``, ``multiple_of``, ``min_length``, ``max_length``) when present.",
    )


class IndicatorOutputColumn(Data):
    """One output column of an indicator endpoint.

    Parameters
    ----------
    name : str
        Output column name.
    type : str
        Stable, human-readable rendering of the column's Python type
        annotation.
    nullable : bool
        ``True`` when the column can produce ``None`` values (e.g. warm-up
        rows).
    description : str, optional
        Human-readable column description sourced from the Pydantic ``Field``
        description on the data model.
    """

    name: str = Field(description="Output column name.")
    type: str = Field(
        description="Stable, human-readable rendering of the column's Python type annotation."
    )
    nullable: bool = Field(
        description="``True`` when the column can produce ``None`` values (e.g. warm-up rows)."
    )
    description: str | None = Field(
        default=None,
        description="Human-readable column description sourced from the Pydantic ``Field`` description on the data model.",
    )


class IndicatorEntry(Data):
    """Catalogue entry for a single indicator endpoint.

    Parameters
    ----------
    name : str
        Endpoint name, matching the function name registered on the router.
    category : str
        Indicator family — e.g. ``"overlay"``, ``"oscillator"``,
        ``"volatility"``, ``"multi"``.
    description : str, optional
        First line of the endpoint's QueryParams docstring.
    requires_columns : list[str]
        OHLCV columns the endpoint references in its docstring, in the
        canonical order ``open``, ``high``, ``low``, ``close``, ``volume``.
    params : list[IndicatorParam]
        Per-parameter metadata for the endpoint's QueryParams.
    output_columns : list[IndicatorOutputColumn]
        Per-column metadata for the endpoint's emitted data rows.
    example_call : dict[str, Any]
        Minimal example payload, populated from each parameter's default.
    """

    name: str = Field(
        description="Endpoint name, matching the function name registered on the router."
    )
    category: str = Field(
        description='Indicator family — e.g. ``"overlay"``, ``"oscillator"``, ``"volatility"``, ``"multi"``.'
    )
    description: str | None = Field(
        description="First line of the endpoint's QueryParams docstring."
    )
    requires_columns: list[str] = Field(
        description="OHLCV columns the endpoint references in its docstring, in the canonical order ``open``, ``high``, ``low``, ``close``, ``volume``."
    )
    params: list[IndicatorParam] = Field(
        description="Per-parameter metadata for the endpoint's QueryParams."
    )
    output_columns: list[IndicatorOutputColumn] = Field(
        description="Per-column metadata for the endpoint's emitted data rows."
    )
    example_call: dict[str, Any] = Field(
        description="Minimal example payload, populated from each parameter's default."
    )


class IndicatorsQueryParams(QueryParams):
    """Query parameters for the catalogue endpoint.

    Parameters
    ----------
    category : CatalogCategory, optional
        Filter to a single family — one of ``"overlay"``, ``"oscillator"``,
        ``"volatility"``, ``"volume"``, ``"trend"``, ``"signal"``,
        ``"structure"``, ``"stats"``, ``"multi"`` — or ``"all"`` (the
        default) to return every entry.
    """

    __category__ = "multi"
    __output_columns__ = ("indicators",)

    category: CatalogCategory | None = Field(
        default="all",
        description="Filter to a single family, or ``all`` to return everything.",
    )


class IndicatorsResponse(Data):
    """Wrapper for the full catalogue response.

    Parameters
    ----------
    indicators : list[IndicatorEntry]
        Catalogue entries matching the requested category.
    """

    indicators: list[IndicatorEntry] = Field(
        description="Catalogue entries matching the requested category."
    )


_OHLCV_COLUMNS = {"open", "high", "low", "close", "volume"}


def _stringify_type(annotation: Any) -> str:
    """Render a type annotation as a stable, human-readable string."""
    if annotation is inspect.Signature.empty or annotation is None:
        return "Any"  # pragma: no cover - all our params are annotated
    return str(annotation).replace("typing.", "")


def _literal_choices(annotation: Any) -> list[str] | None:
    """Extract Literal[...] values, peeling away ``Optional`` / ``Annotated``."""
    origin = get_origin(annotation)
    if origin is Literal:
        return [str(arg) for arg in get_args(annotation)]
    args = get_args(annotation)
    for arg in args:
        choices = _literal_choices(arg)
        if choices is not None:
            return choices
    return None


def _field_constraints(field: FieldInfo) -> dict[str, Any] | None:
    """Extract Pydantic numeric constraints (``gt``, ``ge``, ``lt``, ``le``)."""
    constraints: dict[str, Any] = {}
    for key in ("gt", "ge", "lt", "le", "multiple_of", "max_length", "min_length"):
        meta_value = getattr(field, key, None)
        if meta_value is not None:
            constraints[key] = meta_value
    for meta in getattr(field, "metadata", []) or []:
        for attr in ("gt", "ge", "lt", "le", "multiple_of"):
            if hasattr(meta, attr):
                constraints[attr] = getattr(meta, attr)
    return constraints or None


def _default_for(field: FieldInfo) -> Any | None:
    """Best-effort serialisable default for a Pydantic field."""
    if field.default_factory is not None:  # type: ignore[truthy-function]
        try:
            return field.default_factory()  # ty: ignore[missing-argument]
        except Exception:  # pragma: no cover - factories are pure in practice
            return None
    if field.is_required():
        return None
    return field.default


def _module_query_params(module: Any) -> dict[str, type[QueryParams]]:
    """Find ``XxxQueryParams`` classes defined in or re-exported by ``module``."""
    out: dict[str, type[QueryParams]] = {}
    declared = set(getattr(module, "__all__", ()))
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if not (
            isinstance(attr, type)
            and issubclass(attr, QueryParams)
            and attr is not QueryParams
        ):
            continue
        # Accept classes defined in this module, or explicitly re-exported via
        # ``__all__`` (lets thin router shells reuse a QueryParams class
        # defined elsewhere in the package, e.g. ``relative_rotation``).
        if attr.__module__ == module.__name__ or attr_name in declared:
            out[attr_name] = attr
    return out


def _match_query_params_for(
    endpoint_name: str, candidates: dict[str, type[QueryParams]]
) -> type[QueryParams] | None:
    """Match an endpoint name to its ``XxxQueryParams`` class by convention."""
    expected = endpoint_name.replace("_", "").lower() + "queryparams"
    for class_name, cls in candidates.items():
        if class_name.lower() == expected:
            return cls
    return None


_FAMILY_MODULES: tuple[str, ...] = (
    "openbb_technical.indicators.overlays",
    "openbb_technical.indicators.oscillators",
    "openbb_technical.indicators.volatility",
    "openbb_technical.indicators.volume",
    "openbb_technical.indicators.trend",
    "openbb_technical.indicators.structure",
    "openbb_technical.indicators.statistics",
    "openbb_technical.indicators.relative_rotation",
    "openbb_technical.signals.breakouts",
    "openbb_technical.signals.crossovers",
    "openbb_technical.signals.divergences",
    "openbb_technical.signals.patterns",
    "openbb_technical.signals.regime",
    "openbb_technical.signals.thresholds",
    "openbb_technical.multi.compose",
    "openbb_technical.multi.correlation",
    "openbb_technical.multi.screen",
    "openbb_technical.multi.catalog",
)


def _required_data_columns(query_params: type[QueryParams]) -> list[str]:
    """Report OHLCV columns referenced in the QueryParams docstring."""
    doc = (query_params.__doc__ or "").lower()
    found: list[str] = []
    for col in ("open", "high", "low", "close", "volume"):
        if col in doc and col not in found:
            found.append(col)
    return found


def _example_call(
    endpoint_name: str, query_params: type[QueryParams]
) -> dict[str, Any]:
    """Build a minimal example payload using each field's default."""
    example: dict[str, Any] = {"endpoint": endpoint_name}
    for name, field in query_params.model_fields.items():
        if name == "data":
            example[name] = "<list[Data]>"
            continue
        default = _default_for(field)
        if default is not None:
            example[name] = default
    return example


def _output_column_entries(
    query_params: type[QueryParams], data_model: type[Data] | None
) -> list[IndicatorOutputColumn]:
    """Build the per-column metadata for an indicator's output rows."""
    column_names: tuple[str, ...] = getattr(query_params, "__output_columns__", ())
    if not column_names:
        return []  # pragma: no cover - all migrated families declare columns
    type_map: dict[str, Any] = {}
    description_map: dict[str, str | None] = {}
    nullable_map: dict[str, bool] = {}
    if data_model is not None:
        hints = get_type_hints(data_model)
        for fname, field in data_model.model_fields.items():
            annotation = hints.get(fname, field.annotation)
            type_map[fname] = annotation
            description_map[fname] = field.description
            nullable_map[fname] = type(None) in get_args(annotation)
    entries: list[IndicatorOutputColumn] = []
    for col in column_names:
        annotation = type_map.get(col, str)
        entries.append(
            IndicatorOutputColumn(
                name=col,
                type=_stringify_type(annotation),
                nullable=nullable_map.get(col, False),
                description=description_map.get(col),
            )
        )
    return entries


def _find_data_model(module: Any, endpoint_name: str) -> type[Data] | None:
    """Find the ``XxxData`` model paired with an endpoint, if any."""
    expected = endpoint_name.replace("_", "").lower() + "data"
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (
            isinstance(attr, type)
            and issubclass(attr, Data)
            and attr is not Data
            and attr.__module__ == module.__name__
            and attr_name.lower() == expected
        ):
            return attr
    return None


def _build_catalog() -> list[IndicatorEntry]:
    """Walk every known family module and collect catalogue entries."""
    entries: list[IndicatorEntry] = []
    for module_path in _FAMILY_MODULES:
        try:
            module = importlib.import_module(module_path)
        except ImportError:  # pragma: no cover - family not yet migrated
            continue
        family_router = getattr(module, "router", None)
        if family_router is None:
            continue  # pragma: no cover - every family module exposes ``router``
        candidates = _module_query_params(module)
        for route in family_router.api_router.routes:
            endpoint = route.endpoint
            endpoint_name = endpoint.__name__
            query_params = _match_query_params_for(endpoint_name, candidates)
            if query_params is None:
                continue
            data_model = _find_data_model(module, endpoint_name)
            params: list[IndicatorParam] = []
            for fname, field in query_params.model_fields.items():
                if fname == "data":
                    continue
                annotation = field.annotation
                params.append(
                    IndicatorParam(
                        name=fname,
                        type=_stringify_type(annotation),
                        default=_default_for(field),
                        description=field.description,
                        choices=_literal_choices(annotation),
                        constraints=_field_constraints(field),
                    )
                )
            entries.append(
                IndicatorEntry(
                    name=endpoint_name,
                    category=getattr(query_params, "__category__", "uncategorized"),
                    description=(query_params.__doc__ or "").strip() or None,
                    requires_columns=_required_data_columns(query_params),
                    params=params,
                    output_columns=_output_column_entries(query_params, data_model),
                    example_call=_example_call(endpoint_name, query_params),
                )
            )
    return entries


_CATALOG_CACHE: list[IndicatorEntry] | None = None


def _catalog() -> list[IndicatorEntry]:
    """Return the catalogue, building it lazily on the first call."""
    global _CATALOG_CACHE  # noqa: PLW0603 - module-level lazy cache, no contention
    if _CATALOG_CACHE is None:
        _CATALOG_CACHE = _build_catalog()
    return _CATALOG_CACHE


class _CatalogProxy:
    """Lazy list proxy so legacy access patterns (``_CATALOG``) still work."""

    def __iter__(self):
        return iter(_catalog())

    def __len__(self):
        return len(_catalog())

    def __bool__(self):
        return bool(_catalog())

    def __getitem__(self, item):
        return _catalog()[item]


_CATALOG: _CatalogProxy = _CatalogProxy()


@router.command(methods=["POST"])
def indicators(params: IndicatorsQueryParams) -> OBBject[IndicatorsResponse]:
    """Return the catalogue of registered technical indicators."""
    full = _catalog()
    if params.category in (None, "all"):
        selected = list(full)
    else:
        selected = [e for e in full if e.category == params.category]
    return OBBject(results=IndicatorsResponse(indicators=selected))


__all__ = [
    "CatalogCategory",
    "IndicatorEntry",
    "IndicatorOutputColumn",
    "IndicatorParam",
    "IndicatorsQueryParams",
    "IndicatorsResponse",
    "indicators",
    "router",
]
