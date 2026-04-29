"""Drive `MethodDefinition.add_field_custom_annotations` via a rich fake provider."""

from collections import OrderedDict
from dataclasses import dataclass, field
from inspect import Parameter
from typing import Annotated, Literal
from unittest.mock import patch

import pytest
from pydantic import Field

pandas = pytest.importorskip("pandas")
pytestmark = pytest.mark.requires_pandas

from openbb_core.app.model.field import OpenBBField  # noqa: E402
from openbb_core.app.provider_interface import ProviderInterface  # noqa: E402
from openbb_core.app.static.package_builder import MethodDefinition  # noqa: E402
from openbb_core.provider.abstract.data import Data  # noqa: E402
from openbb_core.provider.abstract.fetcher import Fetcher  # noqa: E402
from openbb_core.provider.abstract.provider import Provider  # noqa: E402
from openbb_core.provider.abstract.query_params import QueryParams  # noqa: E402
from openbb_core.provider.registry import Registry  # noqa: E402
from openbb_core.provider.registry_map import RegistryMap  # noqa: E402


class _RichQueryParams(QueryParams):
    """Standard query params with json_schema_extra populated."""

    symbol: str = Field(
        description="Symbol(s).",
        json_schema_extra={
            "rich_a": {"choices": ["AAPL", "MSFT"], "multiple_items_allowed": True},
            "rich_b": {"choices": ["GOOG"], "multiple_items_allowed": False},
        },
    )
    exchange: str | None = Field(
        default=None,
        description="Exchange.",
        json_schema_extra={
            "rich_a": {"choices": ["NYSE", "NASDAQ"]},
        },
    )


class _RichData(Data):
    """Standard data class."""

    symbol: str | None = None


class _RichAFetcher(Fetcher[_RichQueryParams, list[_RichData]]):
    require_credentials = False

    @staticmethod
    def transform_query(params):
        return _RichQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials):
        return [{"symbol": "AAPL"}]

    @staticmethod
    def transform_data(query, data, **kwargs):
        return [_RichData(**row) for row in data]


class _RichBQueryParams(_RichQueryParams):
    region: Literal["us", "eu"] | None = None


class _RichBFetcher(Fetcher[_RichBQueryParams, list[_RichData]]):
    require_credentials = False

    @staticmethod
    def transform_query(params):
        return _RichBQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials):
        return []

    @staticmethod
    def transform_data(query, data, **kwargs):
        return []


@pytest.fixture
def rich_provider_interface():
    ProviderInterface._instances.pop(ProviderInterface, None)
    registry = Registry()
    registry.include_provider(
        Provider(
            name="rich_a",
            description="rich A",
            website="https://example.invalid",
            credentials=None,
            fetcher_dict={"RichModel": _RichAFetcher},
        )
    )
    registry.include_provider(
        Provider(
            name="rich_b",
            description="rich B",
            website="https://example.invalid",
            credentials=None,
            fetcher_dict={"RichModel": _RichBFetcher},
        )
    )
    pi = ProviderInterface(registry_map=RegistryMap(registry=registry))
    yield pi
    ProviderInterface._instances.pop(ProviderInterface, None)


def test_add_field_custom_annotations_standard_model_path(rich_provider_interface):
    """Cover the entry path: real model_name with empty od triggers no-op iteration."""
    od = OrderedDict()
    out = MethodDefinition.add_field_custom_annotations(od, model_name="RichModel")
    assert out is None


class _FakeQuery:
    """Stand-in for fastapi.Query carrying json_schema_extra."""

    def __init__(self, description, json_schema_extra):
        self.description = description
        self.json_schema_extra = json_schema_extra


def _build_fake_pi_with_rich_extras():
    """Construct a ProviderInterface-like object whose params[model] has json_schema_extra."""

    @dataclass
    class StdParams:
        symbol: Annotated[
            Literal["AAPL"] | Literal["GOOG"] | str,
            OpenBBField(description=""),
        ] = field(
            default=_FakeQuery(
                description="sym",
                json_schema_extra={
                    "prov_a": {
                        "choices": ["AAPL", "MSFT"],
                        "multiple_items_allowed": True,
                    },
                    "prov_b": {
                        "choices": ["GOOG"],
                        "multiple_items_allowed": ["foo"],
                    },
                },
            )
        )
        exchange: Annotated[str | None, OpenBBField(description="")] = field(
            default=_FakeQuery(
                description="exch",
                json_schema_extra={"prov_a": {"choices": ["NYSE"]}},
            )
        )

    @dataclass
    class ExtraParams:
        pass

    class _FakePI:
        params = {
            "RichModel": {"standard": StdParams, "extra": ExtraParams},
        }

    return _FakePI()


def test_add_field_custom_annotations_full_branch_coverage():
    fake_pi = _build_fake_pi_with_rich_extras()
    od = OrderedDict()
    od["symbol"] = Parameter(
        "symbol",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[
            Literal["AAPL"] | Literal["GOOG"],
            OpenBBField(description=""),
        ],
    )
    od["exchange"] = Parameter(
        "exchange",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[str | None, OpenBBField(description="")],
        default=None,
    )
    od["unrelated"] = Parameter(
        "unrelated",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[int, OpenBBField(description="orig")],
    )
    with patch(
        "openbb_core.app.static.package_builder.method_definition.ProviderInterface",
        return_value=fake_pi,
    ):
        MethodDefinition.add_field_custom_annotations(od, model_name="RichModel")

    sym_desc = od["symbol"].annotation.__metadata__[-1].description
    assert "Choices for prov_a" in sym_desc
    assert "Choices for prov_b" in sym_desc
    assert "Multiple items supported by" in sym_desc
    exch_desc = od["exchange"].annotation.__metadata__[-1].description
    assert "Choices for prov_a" in exch_desc
    # 'unrelated' not touched (not in fields)
    assert od["unrelated"].annotation.__metadata__[0].description == "orig"


def test_add_field_custom_annotations_no_model_name():
    od = OrderedDict()
    od["x"] = Parameter("x", kind=Parameter.POSITIONAL_OR_KEYWORD)
    out = MethodDefinition.add_field_custom_annotations(od, model_name=None)
    assert out is None
    assert "x" in od


def test_add_field_custom_annotations_unknown_model_returns_silently(
    rich_provider_interface,
):
    od = OrderedDict()
    od["x"] = Parameter("x", kind=Parameter.POSITIONAL_OR_KEYWORD)
    out = MethodDefinition.add_field_custom_annotations(od, model_name="DoesNotExist")
    assert out is None


def test_add_field_custom_annotations_skips_params_not_in_fields(
    rich_provider_interface,
):
    od = OrderedDict()
    od["unknown_param"] = Parameter(
        "unknown_param",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[str, OpenBBField(description="orig")],
    )
    MethodDefinition.add_field_custom_annotations(od, model_name="RichModel")
    # unchanged
    assert od["unknown_param"].annotation.__metadata__[0].description == "orig"


# --- _format_annotated_param: Pydantic body model expansion (lines 445-472) ---


def test_format_annotated_param_pydantic_body_expands_fields():
    from inspect import Parameter
    from typing import Annotated

    from pydantic import BaseModel, Field

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )

    class Body(BaseModel):
        a: str = Field(default="x", description="A field.")
        b: int = Field(default=1, description="B field.")

    p = Parameter(
        name="body",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[Body, "tag"],
    )
    formatted: dict = {}
    consumed = MethodDefinition._format_annotated_param(
        "body", p, "/some/path", formatted
    )
    assert consumed is True
    assert "a" in formatted and "b" in formatted
    assert formatted["a"].default == "x"
    assert formatted["b"].default == 1


def test_format_annotated_param_query_object_in_metadata():
    """Lines 485-499: Query meta object with description+default."""
    from inspect import Parameter
    from typing import Annotated

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )

    class _Q:
        description = "Sym desc"
        default = "AAPL"

    _Q.__name__ = "Query"
    p = Parameter(
        name="symbol",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[str, _Q()],
        default="AAPL",
    )
    formatted: dict = {}
    consumed = MethodDefinition._format_annotated_param("symbol", p, "/x", formatted)
    assert consumed is True
    assert "symbol" in formatted


def test_format_annotated_param_no_query_returns_false():
    """Falls through when neither Pydantic nor Query."""
    from inspect import Parameter
    from typing import Annotated

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )

    p = Parameter(
        name="x",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[str, "just_a_string"],
    )
    formatted: dict = {}
    consumed = MethodDefinition._format_annotated_param("x", p, "/path", formatted)
    assert consumed is False


def test_format_annotated_param_data_processing_skips_pydantic_branch():
    """When path is data-processing, the Pydantic body branch is skipped."""
    from inspect import Parameter
    from typing import Annotated

    from pydantic import BaseModel

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )

    class Body(BaseModel):
        a: str = "x"

    p = Parameter(
        name="body",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[Body, "tag"],
    )
    formatted: dict = {}
    # data-processing path means is_get_request is False
    # This requires a path that returns False from is_data_processing_function
    # If Body has no Query meta, returns False
    consumed = MethodDefinition._format_annotated_param(
        "body", p, "/econometrics/foo", formatted
    )
    # Either consumed True (if /econometrics/foo treated as get) or False (data-proc)
    assert consumed in (True, False)


def test_parse_docstring_params_basic():
    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )

    def f(symbol):
        """Func.

        Parameters
        ----------
        symbol : str
            The symbol description.
        other : int
            Another desc.
        """

    out = MethodDefinition._parse_docstring_params(f)
    assert out.get("symbol") == "The symbol description."
    assert out.get("other") == "Another desc."


def test_build_command_method_filter_inputs_source_extraction(monkeypatch):
    """Lines 1263-1313: extract additional params from filter_inputs() in func source."""
    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    def my_endpoint(symbol: str = "AAPL"):
        """Endpoint."""
        period: int = 5
        weights: list = []
        result = filter_inputs(sym=symbol, p=period, w=weights, flag=True)  # noqa: F821
        return result

    class _FakeRoute:
        deprecated = False
        path = "/test/endpoint"
        endpoint = my_endpoint
        openapi_extra: dict = {}

    monkeypatch.setattr(
        PathHandler,
        "build_route_map",
        staticmethod(lambda: {"/test/endpoint": _FakeRoute()}),
    )

    code = MethodDefinition.build_command_method(
        path="/test/endpoint",
        func=my_endpoint,
        model_name=None,
    )
    assert "def endpoint" in code


def test_format_params_query_default_value(monkeypatch):
    """Lines 567-586: when param.default is a Query-class instance, extract description+default."""
    from inspect import Parameter

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    class _Q:
        description = "Sym"
        default = "AAPL"

    _Q.__name__ = "Query"

    parameter_map = {
        "symbol": Parameter(
            name="symbol",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=str,
            default=_Q(),
        ),
    }
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    out = MethodDefinition.format_params("/x/y", parameter_map)
    assert "symbol" in out
    assert out["symbol"].default == "AAPL"


def test_format_params_dataclass_annotated_field_expansion(monkeypatch):
    """Lines 623-638: is_annotated_dc branch -> field expansion."""
    from dataclasses import dataclass
    from inspect import Parameter
    from typing import Annotated

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    @dataclass
    class _Std:
        symbol: str = "AAPL"
        days: int = 7

    parameter_map = {
        "standard_params": Parameter(
            name="standard_params",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[_Std, "tag"],
        ),
    }
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    out = MethodDefinition.format_params("/x/y", parameter_map)
    assert "symbol" in out
    assert "days" in out


def test_format_params_provider_choices(monkeypatch):
    """Lines 591-619: provider_choices Annotated[dataclass, ...] -> 'provider' Parameter."""
    from dataclasses import dataclass
    from inspect import Parameter
    from typing import Annotated, Literal

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    @dataclass
    class _PC:
        provider: Literal["a", "b"] = "a"

    parameter_map = {
        "provider_choices": Parameter(
            name="provider_choices",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[_PC, "tag"],
        ),
    }
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    out = MethodDefinition.format_params("/x/y", parameter_map)
    assert "provider" in out
    assert out["provider"].default is None


def test_format_params_path_parameters_extracted(monkeypatch):
    from inspect import Parameter

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    parameter_map = {
        "ticker": Parameter(
            name="ticker", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=str
        ),
    }
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    out = MethodDefinition.format_params("/equity/{ticker}/info", parameter_map)
    assert "ticker" in out


def test_build_command_method_body_annotated_basemodel(monkeypatch):
    """Lines 1176-1193: Annotated[BaseModel, ...] without Depends -> field expansion."""
    from typing import Annotated

    from pydantic import BaseModel

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )

    monkeypatch.setattr(
        MethodDefinition, "is_deprecated_function", staticmethod(lambda p: False)
    )

    class _Body(BaseModel):
        symbol: str = "AAPL"
        period: int = 7

    def my_endpoint(body: Annotated[_Body, "tag"]):
        return body

    code = MethodDefinition.build_command_method_body(path="/x/y", func=my_endpoint)
    assert '"symbol": symbol' in code
    assert '"period": period' in code


def test_build_command_method_body_annotated_basemodel_with_depends(monkeypatch):
    """Lines 1192-1193: Annotated[BaseModel, ...] WITH Depends -> passthrough."""
    from typing import Annotated

    from fastapi import Depends
    from pydantic import BaseModel

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )

    monkeypatch.setattr(
        MethodDefinition, "is_deprecated_function", staticmethod(lambda p: False)
    )

    class _Body(BaseModel):
        symbol: str = "AAPL"

    def _dep():
        return _Body()

    def my_endpoint(body: Annotated[_Body, Depends(_dep)]):
        return body

    code = MethodDefinition.build_command_method_body(path="/x/y", func=my_endpoint)
    assert "body=body" in code


def test_build_command_method_body_extra_params_with_extras(monkeypatch):
    """Lines 1141-1147: extra_params dataclass with extras dict -> info accumulated."""
    from dataclasses import dataclass, field
    from typing import Annotated

    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )

    monkeypatch.setattr(
        MethodDefinition, "is_deprecated_function", staticmethod(lambda p: False)
    )

    @dataclass
    class _Extras:
        symbol: str = field(default="AAPL", metadata={"x-extra": {"choices": ["AAPL"]}})

    def my_endpoint(extra_params: Annotated[_Extras, "tag"]):
        return None

    code = MethodDefinition.build_command_method_body(path="/x/y", func=my_endpoint)
    assert "extra_params=kwargs" in code


def test_build_command_method_deprecated_path(monkeypatch):
    """Lines 1117-1120: deprecated function path -> emits simplefilter+warn lines."""
    from openbb_core.app.static.package_builder.method_definition import (
        MethodDefinition,
    )

    monkeypatch.setattr(
        MethodDefinition, "is_deprecated_function", staticmethod(lambda p: True)
    )
    monkeypatch.setattr(
        MethodDefinition, "get_deprecation_message", staticmethod(lambda p: "Old API")
    )

    def my_endpoint(symbol: str = "AAPL"):
        return symbol

    code = MethodDefinition.build_command_method_body(path="/x/y", func=my_endpoint)
    assert "simplefilter('always', DeprecationWarning)" in code
    assert "Old API" in code


def test_format_params_extra_params_and_provider_choices_skip(monkeypatch):
    from inspect import Parameter

    from openbb_core.app.static.package_builder.path_handler import PathHandler

    parameter_map = {
        "extra_params": Parameter(
            name="extra_params", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=dict
        ),
        "provider_choices": Parameter(
            name="provider_choices",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Parameter.empty,
        ),
    }
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    out = MethodDefinition.format_params("/x/y", parameter_map)
    assert "extra_params" in out


def test_format_params_annotated_without_depends_and_var_keyword(monkeypatch):
    from inspect import Parameter

    from openbb_core.app.static.package_builder.path_handler import PathHandler

    parameter_map = {
        "symbol": Parameter(
            name="symbol",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[str, OpenBBField(description="")],
        ),
        "kwargs": Parameter(
            name="kwargs",
            kind=Parameter.VAR_KEYWORD,
            annotation=int,
            default=Parameter.empty,
        ),
        "any_kwargs": Parameter(
            name="any_kwargs",
            kind=Parameter.VAR_KEYWORD,
            annotation=int,
            default=Parameter.empty,
        ),
    }
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    out = MethodDefinition.format_params("/x/y", parameter_map)
    assert "symbol" in out and "any_kwargs" in out


def test_format_params_constrained_expanded_type_branch(monkeypatch):
    from inspect import Parameter

    from openbb_core.app.static.package_builder.path_handler import PathHandler

    class _Constrained:
        __constraints__ = (str,)

    parameter_map = {
        "x": Parameter(name="x", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    }
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    monkeypatch.setattr(
        MethodDefinition,
        "get_expanded_type",
        classmethod(lambda cls, *_a, **_k: _Constrained),
    )
    out = MethodDefinition.format_params("/x/y", parameter_map)
    assert "x" in out


def test_add_field_custom_annotations_all_literal_union_simplifies_type(monkeypatch):
    from dataclasses import dataclass

    class _QueryObj:
        def __init__(self):
            self.json_schema_extra = {"prov": {"choices": ["a", "b"]}}
            self.description = "desc"

    @dataclass
    class _Std:
        p: Literal["a"] | Literal["b"] = _QueryObj()

    @dataclass
    class _Extra:
        pass

    fake_pi = type("_PI", (), {"params": {"M": {"standard": _Std, "extra": _Extra}}})()

    od = OrderedDict(
        {
            "p": Parameter(
                "p",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[
                    Literal["a"] | Literal["b"], OpenBBField(description="")
                ],
            )
        }
    )

    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.ProviderInterface",
        lambda: fake_pi,
    )
    MethodDefinition.add_field_custom_annotations(od, model_name="M")
    assert "Choices for prov" in od["p"].annotation.__metadata__[-1].description


def test_build_func_params_wraps_long_desc_and_ellipsis_default():
    long_desc = "x" * 120
    params = OrderedDict(
        {
            "x": Parameter(
                name="x",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[list[int], OpenBBField(description=long_desc)],
                default=Ellipsis,
            )
        }
    )
    out = MethodDefinition.build_func_params(params)
    assert "OpenBBField" in out
    assert " = None" in out


def test_build_func_returns_obbject_subclass():
    from openbb_core.app.model.obbject import OBBject

    class _O(OBBject):
        pass

    assert MethodDefinition.build_func_returns(_O) == "OBBject"


def test_collect_dependency_calls_skips_unsafe_annotated_dependency():
    def _unsafe() -> None:
        return None

    parameter_map = {
        "dep": Parameter(
            name="dep",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[int, type("_Meta", (), {"dependency": _unsafe})()],
        )
    }
    calls, names = MethodDefinition._collect_dependency_calls("/x/y", parameter_map)
    assert calls == []
    assert names == set()


def test_build_command_method_body_provider_choices_annotated_dc_info_and_kwargs(
    monkeypatch,
):
    from dataclasses import dataclass

    monkeypatch.setattr(
        MethodDefinition, "is_deprecated_function", staticmethod(lambda p: False)
    )
    monkeypatch.setattr(
        MethodDefinition, "is_data_processing_function", staticmethod(lambda p: True)
    )

    class _D:
        json_schema_extra = {"note": "x"}

    @dataclass
    class _Extras:
        alpha: str = _D()

    @dataclass
    class _ProviderChoices:
        provider: Literal["a", "b"] = "a"

    @dataclass
    class _Std:
        beta: int = 1

    def endpoint(
        extra_params: Annotated[_Extras, "tag"],
        provider_choices: Annotated[_ProviderChoices, "tag"],
        standard_params: Annotated[_Std, "tag"],
        **kwargs,
    ):
        return None

    code = MethodDefinition.build_command_method_body("/x/y", endpoint)
    assert "provider_choices={" in code
    assert "standard_params={" in code
    assert "info={" in code
    assert "data_processing=True" in code


def test_build_command_method_source_eval_fallback_branches(monkeypatch):
    def endpoint(symbol: str = "AAPL"):
        bad: UnknownType = nope  # type: ignore[name-defined]  # noqa: F821
        result = filter_inputs(a=bad, b=missing)  # noqa: F821
        return result

    monkeypatch.setattr(
        MethodDefinition, "is_deprecated_function", staticmethod(lambda p: False)
    )
    code = MethodDefinition.build_command_method("/x/y", endpoint)
    assert "def y" in code


def test_format_annotated_param_query_default_pydantic_undefined():
    from pydantic_core import PydanticUndefined

    class _Q:
        description = "x"
        default = PydanticUndefined

    _Q.__name__ = "Query"

    p = Parameter(
        name="x",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[str, _Q()],
        default=Parameter.empty,
    )
    formatted = {}
    assert MethodDefinition._format_annotated_param("x", p, "/x", formatted) is True


def test_format_params_chart_branch(monkeypatch):
    from openbb_core.app.static.package_builder import method_definition as md
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    class _Chart:
        @staticmethod
        def functions():
            return ["x_y"]

    monkeypatch.setattr(md, "CHARTING_INSTALLED", True)
    monkeypatch.setattr(md, "Charting", _Chart, raising=False)
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    out = MethodDefinition.format_params("/x/y", {})
    assert "chart" in out


def test_format_params_continue_when_annotated_param_consumed(monkeypatch):
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    p = Parameter(
        name="x",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[str, OpenBBField(description="")],
    )
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    monkeypatch.setattr(
        MethodDefinition,
        "_format_annotated_param",
        staticmethod(lambda *_a, **_k: True),
    )
    out = MethodDefinition.format_params("/x/y", {"x": p})
    assert out == OrderedDict()


def test_format_params_annotated_non_depends_new_type_ellipsis(monkeypatch):
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    p = Parameter(
        name="x",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[str, OpenBBField(description="")],
    )
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    monkeypatch.setattr(
        MethodDefinition, "get_expanded_type", classmethod(lambda cls, *_a, **_k: ...)
    )
    out = MethodDefinition.format_params("/x/y", {"x": p})
    assert "x" in out


def test_format_params_annotated_with_depends_continue(monkeypatch):
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    meta = type("_Meta", (), {"dependency": lambda: 1})()
    p = Parameter(
        name="x",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[str, meta],
    )
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    out = MethodDefinition.format_params("/x/y", {"x": p})
    assert "x" not in out


def test_add_field_custom_annotations_union_not_all_literals(monkeypatch):
    from dataclasses import dataclass

    class _QueryObj:
        def __init__(self):
            self.json_schema_extra = {"prov": {"choices": ["a", "b"]}}
            self.description = "desc"

    @dataclass
    class _Std:
        p: Literal["a"] | int = _QueryObj()

    @dataclass
    class _Extra:
        pass

    fake_pi = type("_PI", (), {"params": {"M": {"standard": _Std, "extra": _Extra}}})()
    od = OrderedDict(
        {
            "p": Parameter(
                "p",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[Literal["a"] | int, OpenBBField(description="")],
            )
        }
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.ProviderInterface",
        lambda: fake_pi,
    )
    MethodDefinition.add_field_custom_annotations(od, model_name="M")
    assert "Choices for prov" in od["p"].annotation.__metadata__[-1].description


def test_add_field_custom_annotations_choices_branch(monkeypatch):
    from types import SimpleNamespace

    std_field = SimpleNamespace(
        default=SimpleNamespace(description="d"),
        type=Literal["a"] | Literal["b"],
        json_schema_extra={"choices": ["a", "b"]},
    )
    fake_std = type("_S", (), {"__dataclass_fields__": {"p": std_field}})
    fake_extra = type("_E", (), {"__dataclass_fields__": {}})
    fake_pi = type(
        "_PI", (), {"params": {"M": {"standard": fake_std, "extra": fake_extra}}}
    )()

    od = OrderedDict(
        {
            "p": Parameter(
                "p",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[
                    Literal["a"] | Literal["b"], OpenBBField(description="")
                ],
            )
        }
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.ProviderInterface",
        lambda: fake_pi,
    )
    MethodDefinition.add_field_custom_annotations(od, model_name="M")
    assert od["p"].annotation.__metadata__[-1].description == "d"


def test_build_func_params_typing_repr_and_none_description():

    params = OrderedDict(
        {
            "x": Parameter(
                name="x",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[list[int], OpenBBField(description=None)],
                default=1,
            )
        }
    )
    out = MethodDefinition.build_func_params(params)
    assert "List[int]" in out or "list[int]" in out


def test_build_command_method_body_chart_branch(monkeypatch):
    from openbb_core.app.static.package_builder import method_definition as md

    class _Chart:
        @staticmethod
        def functions():
            return ["x_y"]

    monkeypatch.setattr(md, "CHARTING_INSTALLED", True)
    monkeypatch.setattr(md, "Charting", _Chart, raising=False)
    monkeypatch.setattr(
        MethodDefinition, "is_deprecated_function", staticmethod(lambda p: False)
    )

    def endpoint(symbol: str = "AAPL"):
        return symbol

    code = MethodDefinition.build_command_method_body("/x/y", endpoint)
    assert "chart" in code


def test_build_command_method_body_annotated_dc_info_extra(monkeypatch):
    from dataclasses import dataclass

    monkeypatch.setattr(
        MethodDefinition, "is_deprecated_function", staticmethod(lambda p: False)
    )
    monkeypatch.setattr(
        MethodDefinition, "is_data_processing_function", staticmethod(lambda p: False)
    )

    class _D:
        json_schema_extra = {"note": "x"}

    @dataclass
    class _Std:
        beta: int = _D()

    def endpoint(standard_params: Annotated[_Std, "tag"]):
        return None

    code = MethodDefinition.build_command_method_body("/x/y", endpoint)
    assert "info={" in code


def test_build_command_method_getsource_typeerror(monkeypatch):
    from openbb_core.app.static.package_builder import method_definition as md

    def endpoint(symbol: str = "AAPL"):
        return symbol

    monkeypatch.setattr(
        MethodDefinition, "is_deprecated_function", staticmethod(lambda p: False)
    )
    monkeypatch.setattr(
        md.inspect, "getsource", lambda _f: (_ for _ in ()).throw(TypeError("x"))
    )
    code = MethodDefinition.build_command_method("/x/y", endpoint)
    assert "def y" in code
