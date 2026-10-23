"""Direct unit tests for ReferenceGenerator static helpers."""

from typing import Annotated

import pytest
from pydantic_core import PydanticUndefined

pandas = pytest.importorskip("pandas")
pytestmark = pytest.mark.requires_pandas

from openbb_core.app.model.field import OpenBBField  # noqa: E402
from openbb_core.app.model.obbject import OBBject  # noqa: E402
from openbb_core.app.static.package_builder.reference_generator import (  # noqa: E402
    ReferenceGenerator,
)
from openbb_core.provider.abstract.data import Data  # noqa: E402


class _ResData(Data):
    """Simple typed result model for return-type extraction tests."""

    symbol: str = "AAPL"


def _f_no_annotation():
    return None


def _f_obbject_typed() -> OBBject[list[_ResData]]:
    return OBBject(results=[])


def test_clean_string_values_str_basic():
    out = ReferenceGenerator._clean_string_values("hello")
    assert out == "hello"


def test_clean_string_values_replaces_data_path():
    out = ReferenceGenerator._clean_string_values(
        "list[openbb_core.provider.abstract.data.Data]"
    )
    assert out == "list[Data]"


def test_clean_string_values_data_path_singular():
    out = ReferenceGenerator._clean_string_values(
        "openbb_core.provider.abstract.data.Data"
    )
    assert out == "Data"


def test_clean_string_values_union_collapses():
    out = ReferenceGenerator._clean_string_values("Union[int, str]")
    assert "|" in out


def test_clean_string_values_unquoted_literal():
    out = ReferenceGenerator._clean_string_values("Literal[a, b, c]")
    assert "'a'" in out and "'b'" in out and "'c'" in out


def test_clean_string_values_dict_recurses():
    out = ReferenceGenerator._clean_string_values({"k": 'val "x"'})
    assert out == {"k": "val 'x'"}


def test_clean_string_values_list_recurses():
    out = ReferenceGenerator._clean_string_values(['a "x"', "b"])
    assert out == ["a 'x'", "b"]


def test_clean_string_values_passthrough_non_string():
    assert ReferenceGenerator._clean_string_values(42) == 42
    assert ReferenceGenerator._clean_string_values(None) is None


def test_clean_string_values_union_exception_path(monkeypatch):
    import builtins

    original_set = builtins.set
    monkeypatch.setattr(
        builtins,
        "set",
        lambda *_a, **_k: (_ for _ in ()).throw(Exception("x")),
    )
    out = ReferenceGenerator._clean_string_values("Union[int, str]")
    monkeypatch.setattr(builtins, "set", original_set)
    assert out == "Union[int, str]"


def test_get_post_method_returns_info_extracts_obbject():
    docstring = (
        "Summary.\n\nReturns\n-------\nOBBject[list[MyResult]]\n    The results.\n"
    )
    out = ReferenceGenerator._get_post_method_returns_info(docstring)
    assert out["name"] == "results"
    assert "MyResult" in out["type"]
    assert out["description"]


def test_get_post_method_returns_info_no_match():
    out = ReferenceGenerator._get_post_method_returns_info("no returns block here")
    assert out == {}


def test_get_post_method_returns_info_list_type():
    docstring = "x.\n\nReturns\n-------\nlist[MyData]\n    A list of results.\n"
    out = ReferenceGenerator._get_post_method_returns_info(docstring)
    assert out["type"] == "MyData"


def test_extract_parameters_from_docstring_basic():
    doc = (
        "Summary.\n\n"
        "Parameters\n"
        "----------\n"
        "    symbol : str\n"
        "        The symbol.\n"
        "    days : int = 7\n"
        "        Number of days.\n\n"
        "Returns\n"
        "-------\n"
        "    Any\n"
    )
    out = ReferenceGenerator._get_post_method_parameters_info(doc)
    names = [p["name"] for p in out]
    assert "symbol" in names
    assert "days" in names


def test_extract_parameters_from_docstring_no_section():
    out = ReferenceGenerator._get_post_method_parameters_info("no params here")
    assert out == []


def test_extract_parameters_from_docstring_parameters_without_returns():
    doc = "Summary.\n\nParameters\n----------\n    symbol : str\n        The symbol.\n"
    out = ReferenceGenerator._get_post_method_parameters_info(doc)
    assert out and out[0]["name"] == "symbol"


def test_extract_parameters_from_docstring_optional_marker():
    doc = (
        "Summary.\n\n"
        "Parameters\n"
        "----------\n"
        "    region : str, optional\n"
        "        The region.\n\n"
        "Returns\n-------\nAny\n"
    )
    out = ReferenceGenerator._get_post_method_parameters_info(doc)
    assert out
    assert out[0]["optional"] is True
    assert "optional" not in out[0]["type"]


def _func_with_signature(
    symbol: Annotated[str, OpenBBField(description="The sym.")],
    limit: int | None = None,
):
    """Body."""


def test_get_function_signature_info_basic():
    out = ReferenceGenerator._get_function_signature_info(_func_with_signature)
    names = [p["name"] for p in out]
    assert "symbol" in names
    assert "limit" in names
    sym = next(p for p in out if p["name"] == "symbol")
    assert "The sym." in sym["description"]


def test_get_function_signature_info_skips_self_and_cc():
    def f(self, cc, x: int = 1):
        pass

    out = ReferenceGenerator._get_function_signature_info(f)
    names = [p["name"] for p in out]
    assert "self" not in names
    assert "cc" not in names
    assert "x" in names


def test_get_function_signature_info_skips_depends_default():
    from fastapi import Depends

    def dep():
        return 1

    def f(x: int = Depends(dep)):
        pass

    out = ReferenceGenerator._get_function_signature_info(f)
    assert all(p["name"] != "x" for p in out)


def test_get_function_signature_info_query_default_branch():
    from fastapi import Query

    def f(symbol: str = Query(default="AAPL", description="Sym")):
        return None

    out = ReferenceGenerator._get_function_signature_info(f)
    assert out
    assert out[0]["name"] == "symbol"
    assert out[0]["default"] == "AAPL"
    assert out[0]["optional"] is True


def test_get_function_signature_info_skips_dependency_annotation_metadata():
    class _Dep:
        dependency = object()

    def f(x: Annotated[str, _Dep()]):
        return None

    out = ReferenceGenerator._get_function_signature_info(f)
    assert out == []


def _f_obbject_data() -> OBBject[_ResData]:
    """Func."""


def _f_obbject_dict() -> OBBject[dict[str, _ResData]]:
    """Func."""


def _f_obbject_plain() -> OBBject:
    """Plain OBBject."""


def _f_int() -> int:
    pass


def _f_str_dotted() -> "openbb_core.provider.abstract.data.Data":  # noqa
    pass


def test_extract_return_type_no_annotation():
    out = ReferenceGenerator._extract_return_type(_f_no_annotation)
    assert out == {"type": "Any"}


def test_extract_return_type_obbject_list():
    out = ReferenceGenerator._extract_return_type(_f_obbject_typed)
    assert isinstance(out, dict)
    assert "OBBject" in out


def test_extract_return_type_obbject_dict():
    out = ReferenceGenerator._extract_return_type(_f_obbject_dict)
    assert isinstance(out, dict)


def test_extract_return_type_obbject_data():
    out = ReferenceGenerator._extract_return_type(_f_obbject_data)
    assert isinstance(out, dict)


def test_extract_return_type_obbject_plain():
    out = ReferenceGenerator._extract_return_type(_f_obbject_plain)
    assert isinstance(out, dict)


def test_extract_return_type_int_basic():
    out = ReferenceGenerator._extract_return_type(_f_int)
    assert out == "int"


def test_get_obbject_returns_fields_with_provider():
    out = ReferenceGenerator._get_obbject_returns_fields("MyModel", "Literal['a','b']")
    assert any(f["name"] == "results" and f["type"] == "MyModel" for f in out)
    assert any(f["name"] == "provider" and f["type"] == "Literal['a','b']" for f in out)


def test_get_obbject_returns_fields_no_provider_uses_str():
    out = ReferenceGenerator._get_obbject_returns_fields("MyModel", "")
    assert any(f["name"] == "provider" and f["type"] == "str" for f in out)


def test_apply_query_param_extras_multiple_items_provider_dict():
    desc, ftype, choices = ReferenceGenerator._apply_query_param_extras(
        "Symbol",
        "str",
        None,
        {"prov_a": {"multiple_items_allowed": True, "choices": ["x"]}},
    )
    assert "Multiple items allowed" in desc
    assert "prov_a" in desc
    assert "list[str]" in ftype
    assert choices == ["x"]


def test_apply_query_param_extras_multiple_items_provider_list():
    desc, ftype, choices = ReferenceGenerator._apply_query_param_extras(
        "Symbol",
        "str",
        None,
        {"prov_a": ["multiple_items_allowed"]},
    )
    assert "Multiple items allowed" in desc
    assert "prov_a" in desc


def test_apply_query_param_extras_choices_only_no_multi():
    desc, ftype, choices = ReferenceGenerator._apply_query_param_extras(
        "Sym",
        "str",
        None,
        {"prov_a": {"choices": ["x", "y"]}},
    )
    assert choices == ["x", "y"]
    assert "Multiple items" not in desc
    assert ftype == "str"


def test_apply_query_param_extras_top_level_multi():
    desc, ftype, choices = ReferenceGenerator._apply_query_param_extras(
        "Sym",
        "str",
        None,
        {"multiple_items_allowed": True},
    )
    assert "Multiple items allowed" in desc
    assert "list[str]" in ftype


def test_apply_query_param_extras_no_extras_pass_through():
    desc, ftype, choices = ReferenceGenerator._apply_query_param_extras(
        "Plain", "str", ["a"], {}
    )
    assert desc == "Plain"
    assert ftype == "str"
    assert choices == ["a"]


def _f_returns_data() -> _ResData:
    pass


def _f_returns_dict_str() -> "dict[str, int]":
    pass


def _f_returns_list_data() -> list[_ResData]:
    pass


def test_extract_return_type_data_class_returns_name():
    out = ReferenceGenerator._extract_return_type(_f_returns_data)
    assert out == "_ResData"


def test_extract_return_type_container_type():
    out = ReferenceGenerator._extract_return_type(_f_returns_list_data)
    assert "list" in out and "_ResData" in out


def _f_obbject_unbound_with_doc() -> OBBject[list[Data]]:
    """Func with doc.

    Returns
    -------
    OBBject[MyDocModel]
        Some docs.
    """


def test_extract_return_type_obbject_fallback_from_docstring():
    import inspect

    from openbb_core.app.static.package_builder import reference_generator as rg

    return_annotation = inspect.signature(_f_obbject_unbound_with_doc).return_annotation

    original_get_origin = rg.get_origin
    original_get_args = rg.get_args

    def _fake_get_origin(tp):
        if tp is return_annotation:
            return OBBject
        if str(tp) == "list[Data]":
            return list
        return original_get_origin(tp)

    def _fake_get_args(tp):
        if tp is return_annotation:
            return (list[Data],)
        if str(tp) == "list[Data]":
            return (Data,)
        return original_get_args(tp)

    rg.get_origin = _fake_get_origin
    rg.get_args = _fake_get_args
    out = ReferenceGenerator._extract_return_type(_f_obbject_unbound_with_doc)
    rg.get_origin = original_get_origin
    rg.get_args = original_get_args
    assert isinstance(out, dict)
    assert "OBBject" in out
    assert out["OBBject"][0]["type"] == "MyDocModel"


def test_get_provider_field_params_uses_class_and_field_json_extra(monkeypatch):
    from types import SimpleNamespace

    class _ProviderClass:
        __json_schema_extra__ = {
            "symbol": {
                "openbb": {"choices": ["A", "B"]},
                "multiple_items_allowed": True,
            }
        }

    field_info = SimpleNamespace(
        annotation=str,
        is_required=lambda: True,
        description='A "desc"',
        default="",
        json_schema_extra={"openbb": {"choices": ["C"]}},
    )

    fake_pi = SimpleNamespace(
        map={
            "M": {
                "openbb": {
                    "QueryParams": {
                        "class": _ProviderClass,
                        "fields": {"symbol": field_info},
                    }
                }
            }
        }
    )

    monkeypatch.setattr(ReferenceGenerator, "pi", fake_pi)
    out = ReferenceGenerator._get_provider_field_params("M", "QueryParams", "openbb")
    assert out
    assert out[0]["name"] == "symbol"
    assert out[0]["choices"] == ["C"]
    assert out[0]["default"] is None


def test_resolve_field_type_str_annotated_regex_path(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder.docstring_generator import (
        DocstringGenerator,
    )

    monkeypatch.setattr(
        DocstringGenerator,
        "get_field_type",
        staticmethod(lambda *_args, **_kwargs: "Annotated | None"),
    )

    field_info = SimpleNamespace(
        annotation="typing.Annotated[CustomThing, OpenBBField()]",
        is_required=lambda: False,
    )

    field_type_str, is_required = ReferenceGenerator._resolve_field_type_str(field_info)
    assert field_type_str == "CustomThing | None"
    assert is_required is False


def test_resolve_field_type_str_optional_suffix_cleanup(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder.docstring_generator import (
        DocstringGenerator,
    )

    monkeypatch.setattr(
        DocstringGenerator,
        "get_field_type",
        staticmethod(lambda *_args, **_kwargs: "int, optional"),
    )

    field_info = SimpleNamespace(
        annotation=int,
        is_required=lambda: True,
    )

    field_type_str, is_required = ReferenceGenerator._resolve_field_type_str(field_info)
    assert field_type_str == "int"
    assert is_required is False


def test_extract_return_type_obbject_two_args_path(monkeypatch):
    import inspect
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder import reference_generator as rg

    def _func() -> OBBject:
        return OBBject(results=[])

    ann = inspect.signature(_func).return_annotation

    monkeypatch.setattr(rg, "get_origin", lambda tp: OBBject if tp is ann else None)
    monkeypatch.setattr(
        rg,
        "get_args",
        lambda tp: (int, SimpleNamespace(__name__="TwoArgModel")) if tp is ann else (),
    )

    out = ReferenceGenerator._extract_return_type(_func)
    assert out["OBBject"][0]["type"] == "TwoArgModel"


def test_extract_return_type_obbject_unclosed_bracket_completion(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder import reference_generator as rg

    def _func():
        return None

    monkeypatch.setattr(
        rg.inspect,
        "signature",
        lambda _f: SimpleNamespace(return_annotation="OBBject[X][Model[]]"),
    )
    monkeypatch.setattr(rg, "get_type_hints", lambda _f: {})
    monkeypatch.setattr(rg, "get_origin", lambda _t: None)

    out = ReferenceGenerator._extract_return_type(_func)
    assert out["OBBject"][0]["type"] == "Model[]"


def test_get_routers_uses_main_router(monkeypatch, fake_router):
    from openbb_core.app.router import RouterLoader
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    # Existing fixture lambda has wrong arity for instance call; rebind
    parent = RouterLoader.from_extensions()
    monkeypatch.setattr(
        "openbb_core.app.router.RouterLoader.from_extensions",
        staticmethod(lambda: parent),
    )
    route_map = PathHandler.build_route_map()
    out = ReferenceGenerator.get_routers(route_map)
    assert isinstance(out, dict)


def test_get_paths_removes_standard_choices_when_provider_specific_exists(monkeypatch):
    from types import SimpleNamespace

    def endpoint():
        return None

    route = SimpleNamespace(
        methods={"GET"},
        endpoint=endpoint,
        description="desc",
        openapi_extra={"model": "M"},
    )

    fake_pi = SimpleNamespace(map={"M": {"openbb": {}, "prov": {}}})
    monkeypatch.setattr(ReferenceGenerator, "pi", fake_pi)
    monkeypatch.setattr(
        ReferenceGenerator,
        "_get_provider_field_params",
        classmethod(
            lambda cls, _m, params_type, provider="openbb": (
                [{"name": "symbol", "choices": ["A"]}]
                if params_type == "QueryParams" and provider == "openbb"
                else (
                    [{"name": "symbol", "choices": ["B"]}]
                    if params_type == "QueryParams"
                    else [{"name": "x"}]
                )
            )
        ),
    )
    monkeypatch.setattr(
        ReferenceGenerator,
        "_get_provider_parameter_info",
        classmethod(lambda cls, _m: {"type": "Literal['openbb','prov']"}),
    )
    monkeypatch.setattr(
        ReferenceGenerator,
        "_extract_return_type",
        staticmethod(
            lambda _f: {
                "OBBject": [{"name": "results", "type": "Any", "description": "r"}]
            }
        ),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.is_deprecated_function",
        staticmethod(lambda _p: False),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.get_deprecation_message",
        staticmethod(lambda _p: ""),
    )
    monkeypatch.setattr(
        ReferenceGenerator,
        "_get_endpoint_examples",
        classmethod(lambda cls, _p, _f, _e: []),
    )

    out = ReferenceGenerator.get_paths({"/x": route})
    assert out["/x"]["parameters"]["standard"][0]["choices"] is None


def test_get_paths_no_validate_adds_returns_any(monkeypatch):
    from types import SimpleNamespace

    def endpoint():
        return None

    route = SimpleNamespace(
        methods={"GET"},
        endpoint=endpoint,
        description="desc",
        openapi_extra={"model": "M", "no_validate": True},
    )
    fake_pi = SimpleNamespace(map={"M": {"openbb": {}}})
    monkeypatch.setattr(ReferenceGenerator, "pi", fake_pi)
    monkeypatch.setattr(
        ReferenceGenerator,
        "_get_provider_field_params",
        classmethod(lambda cls, _m, _pt, provider="openbb": [{"name": "x"}]),
    )
    monkeypatch.setattr(
        ReferenceGenerator,
        "_get_provider_parameter_info",
        classmethod(lambda cls, _m: {"type": "str"}),
    )
    monkeypatch.setattr(
        ReferenceGenerator,
        "_extract_return_type",
        staticmethod(lambda _f: {"OBBject": [{"name": "results", "type": "Any"}]}),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.is_deprecated_function",
        staticmethod(lambda _p: False),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.get_deprecation_message",
        staticmethod(lambda _p: ""),
    )
    monkeypatch.setattr(
        ReferenceGenerator,
        "_get_endpoint_examples",
        classmethod(lambda cls, _p, _f, _e: []),
    )

    out = ReferenceGenerator.get_paths({"/x": route})
    assert out["/x"]["returns"]["Any"]["description"] == "Unvalidated results object."


def test_get_routers_adds_description_entries(monkeypatch):
    from types import SimpleNamespace

    class _Main:
        @staticmethod
        def get_attr(path, attr):
            if path == "/a" and attr == "description":
                return "desc a"
            return None

    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.reference_generator.RouterLoader",
        lambda: SimpleNamespace(from_extensions=_Main),
    )

    out = ReferenceGenerator.get_routers({"/a/b": object()})
    assert out["/a"]["description"] == "desc a"


def test_get_paths_data_processing_parameter_and_data_model_extraction(monkeypatch):
    from inspect import Parameter
    from types import SimpleNamespace
    from typing import Annotated

    from pydantic import BaseModel, Field

    class _Ret(BaseModel):
        name: str = Field(default="x", description="Name")

    def endpoint(symbol: str, amount: int = 1):
        return None

    route = SimpleNamespace(
        methods=None,
        endpoint=endpoint,
        openapi_extra={},
        description="d",
    )

    fake_pi = SimpleNamespace(map={})
    monkeypatch.setattr(ReferenceGenerator, "pi", fake_pi)
    monkeypatch.setattr(
        ReferenceGenerator,
        "_extract_return_type",
        staticmethod(
            lambda _f: {
                "OBBject": [{"name": "results", "type": "_Ret", "description": "r"}]
            }
        ),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.is_deprecated_function",
        staticmethod(lambda _p: False),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.get_deprecation_message",
        staticmethod(lambda _p: ""),
    )
    monkeypatch.setattr(
        ReferenceGenerator,
        "_get_endpoint_examples",
        classmethod(lambda cls, _p, _f, _e: []),
    )

    formatted_params = {
        "symbol": Parameter(
            name="symbol",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[str, OpenBBField(description="sym")],
            default=Parameter.empty,
        ),
        "amount": Parameter(
            name="amount",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=int,
            default=1,
        ),
    }
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.format_params",
        staticmethod(lambda **_k: formatted_params),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.docstring_generator.DocstringGenerator.generate",
        classmethod(lambda cls, **_k: "Desc\n\nParameters\n----------\n"),
    )

    import sys

    setattr(sys.modules[endpoint.__module__], "_Ret", _Ret)

    out = ReferenceGenerator.get_paths({"/dp": route})
    assert out["/dp"]["description"] == "Desc"
    assert out["/dp"]["parameters"]["standard"][0]["name"] == "symbol"
    assert out["/dp"]["parameters"]["standard"][1]["type"] == "int"
    assert out["/dp"]["returns"]["OBBject"]
    assert out["/dp"]["data"]["standard"][0]["name"] == "name"


def test_get_provider_field_params_provider_specific_extra_and_expanded_type(
    monkeypatch,
):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder import method_definition as md

    field_info = SimpleNamespace(
        annotation=str,
        is_required=lambda: False,
        description="desc",
        default="",
        json_schema_extra={"prov": {"choices": ["x"]}},
    )

    fake_pi = SimpleNamespace(
        map={
            "M": {
                "prov": {
                    "QueryParams": {
                        "class": object,
                        "fields": {"symbol": field_info},
                    }
                }
            }
        }
    )
    monkeypatch.setattr(ReferenceGenerator, "pi", fake_pi)
    monkeypatch.setattr(md.MethodDefinition, "TYPE_EXPANSION", {"symbol": list[str]})

    out = ReferenceGenerator._get_provider_field_params("M", "QueryParams", "prov")
    assert out[0]["choices"] == ["x"]
    assert out[0]["default"] is None


def test_get_provider_field_params_field_extra_choices_and_expanded_field(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder import method_definition as md

    field_info = SimpleNamespace(
        annotation=str,
        is_required=lambda: False,
        description="desc",
        default="",
        json_schema_extra={"choices": ["A", "B"]},
    )
    fake_pi = SimpleNamespace(
        map={
            "M": {
                "openbb": {
                    "QueryParams": {"class": object, "fields": {"symbol": field_info}},
                }
            }
        }
    )
    monkeypatch.setattr(ReferenceGenerator, "pi", fake_pi)
    monkeypatch.setattr(md.MethodDefinition, "TYPE_EXPANSION", {"symbol": list[str]})
    out = ReferenceGenerator._get_provider_field_params("M", "QueryParams", "openbb")
    assert out[0]["choices"] == ["A", "B"]
    assert out[0]["type"]


def test_extract_return_type_inner_type_name_and_bound_branches(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder import reference_generator as rg

    def _f():
        return None

    ann = OBBject

    class _Inner:
        __name__ = "Inner"
        __bound__ = SimpleNamespace(__name__="Bounded")

    monkeypatch.setattr(
        rg.inspect, "signature", lambda _fn: SimpleNamespace(return_annotation=ann)
    )
    monkeypatch.setattr(rg, "get_type_hints", lambda _fn: {"return": ann})
    monkeypatch.setattr(rg, "get_origin", lambda t: OBBject if t is ann else None)
    monkeypatch.setattr(rg, "get_args", lambda t: (_Inner,) if t is ann else ())

    out = ReferenceGenerator._extract_return_type(_f)
    assert out["OBBject"][0]["type"] == "Bounded"


def test_extract_return_type_inner_type_name_attr_branch(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder import reference_generator as rg

    def _f():
        return None

    ann = OBBject
    inner = SimpleNamespace(_name="InnerAlias")

    monkeypatch.setattr(
        rg.inspect, "signature", lambda _fn: SimpleNamespace(return_annotation=ann)
    )
    monkeypatch.setattr(rg, "get_type_hints", lambda _fn: {"return": ann})
    monkeypatch.setattr(rg, "get_origin", lambda t: OBBject if t is ann else None)
    monkeypatch.setattr(rg, "get_args", lambda t: (inner,) if t is ann else ())

    out = ReferenceGenerator._extract_return_type(_f)
    assert out["OBBject"][0]["type"] == "InnerAlias"


def test_get_provider_field_params_expanded_type_non_queryparams(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder import method_definition as md

    field_info = SimpleNamespace(
        annotation=str,
        is_required=lambda: False,
        description="desc",
        default="",
        json_schema_extra={},
    )
    fake_pi = SimpleNamespace(
        map={
            "M": {
                "openbb": {
                    "Data": {"class": object, "fields": {"symbol": field_info}},
                }
            }
        }
    )
    monkeypatch.setattr(ReferenceGenerator, "pi", fake_pi)
    monkeypatch.setattr(md.MethodDefinition, "TYPE_EXPANSION", {"symbol": list[str]})
    out = ReferenceGenerator._get_provider_field_params("M", "Data", "openbb")
    assert "list[str]" in out[0]["type"]


def test_resolve_field_type_str_annotated_empty_args_break_and_fallback(monkeypatch):
    from types import SimpleNamespace
    from typing import Annotated

    from openbb_core.app.static.package_builder import reference_generator as rg

    fake_field = SimpleNamespace(annotation="X", is_required=lambda: True)

    monkeypatch.setattr(rg, "get_origin", lambda t: Annotated if t == "X" else None)
    monkeypatch.setattr(rg, "get_args", lambda _t: ())
    monkeypatch.setattr(
        rg.DocstringGenerator,
        "get_field_type",
        staticmethod(lambda *_a, **_k: "AnnotatedType"),
    )
    out_type, out_required = ReferenceGenerator._resolve_field_type_str(fake_field)
    assert out_type == "X"
    assert out_required is True


def test_resolve_field_type_str_annotated_type_repr_else_branch(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder import reference_generator as rg

    class _NoName:
        def __str__(self):
            return "NoNameType"

    fake_field = SimpleNamespace(annotation=_NoName(), is_required=lambda: True)

    monkeypatch.setattr(rg, "get_origin", lambda _t: None)
    monkeypatch.setattr(
        rg.DocstringGenerator,
        "get_field_type",
        staticmethod(lambda *_a, **_k: "AnnotatedPlaceholder"),
    )
    out_type, _ = ReferenceGenerator._resolve_field_type_str(fake_field)
    assert out_type == "NoNameType"


def test_resolve_field_type_str_annotated_unwrap_and_name_branch(monkeypatch):
    from types import SimpleNamespace
    from typing import Annotated

    from openbb_core.app.static.package_builder import reference_generator as rg

    class _Named:
        __name__ = "NamedType"

    fake_field = SimpleNamespace(annotation="wrapped", is_required=lambda: True)

    monkeypatch.setattr(
        rg, "get_origin", lambda t: Annotated if t == "wrapped" else None
    )
    monkeypatch.setattr(rg, "get_args", lambda _t: (_Named,))
    monkeypatch.setattr(
        rg.DocstringGenerator,
        "get_field_type",
        staticmethod(lambda *_a, **_k: "AnnotatedAlias"),
    )
    out_type, out_required = ReferenceGenerator._resolve_field_type_str(fake_field)
    assert out_type == "_Named"
    assert out_required is True


def test_get_paths_data_processing_empty_docstring_continue(monkeypatch):
    from starlette.routing import Route

    async def endpoint():
        return None

    endpoint.operation_id = "mod.func"
    endpoint.include_in_api = True
    endpoint.openapi_extra = {"model": ""}

    route = Route("/dp-empty", endpoint=endpoint)
    route.path = "/dp-empty"
    route.include_in_schema = True

    monkeypatch.setattr(
        ReferenceGenerator,
        "_extract_return_type",
        staticmethod(
            lambda _f: {"OBBject": [{"name": "results", "type": "list[Pkg.Model]"}]}
        ),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.is_deprecated_function",
        staticmethod(lambda _p: False),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.get_deprecation_message",
        staticmethod(lambda _p: ""),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.format_params",
        staticmethod(lambda **_k: {}),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.docstring_generator.DocstringGenerator.generate",
        classmethod(lambda cls, **_k: ""),
    )

    out = ReferenceGenerator.get_paths({"/dp-empty": route})
    assert "/dp-empty" in out


def test_get_paths_data_processing_kwargs_skip_and_missing_module(monkeypatch):
    from inspect import Parameter
    from types import SimpleNamespace
    from typing import Annotated

    from starlette.routing import Route

    async def endpoint():
        return None

    endpoint.__module__ = "missing.module"
    endpoint.operation_id = "mod.func"
    endpoint.include_in_api = True
    endpoint.openapi_extra = {"model": ""}

    route = Route("/dp-kwargs", endpoint=endpoint)
    route.path = "/dp-kwargs"
    route.include_in_schema = True

    ann = Annotated[str, object(), OpenBBField(description="from-meta")]
    formatted_params = {
        "a": SimpleNamespace(name="a", annotation=ann, default=Parameter.empty),
        "kwargs": SimpleNamespace(
            name="kwargs", annotation=dict, default=Parameter.empty
        ),
    }

    monkeypatch.setattr(
        ReferenceGenerator,
        "_extract_return_type",
        staticmethod(
            lambda _f: {
                "OBBject": [{"name": "results", "type": "dict[str,MissingModel]"}]
            }
        ),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.is_deprecated_function",
        staticmethod(lambda _p: False),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.get_deprecation_message",
        staticmethod(lambda _p: ""),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.format_params",
        staticmethod(lambda **_k: formatted_params),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.docstring_generator.DocstringGenerator.generate",
        classmethod(lambda cls, **_k: "Desc\n\nParameters\n----------\n"),
    )

    out = ReferenceGenerator.get_paths({"/dp-kwargs": route})
    params = out["/dp-kwargs"]["parameters"]["standard"]
    assert len(params) == 1
    assert params[0]["name"] == "a"
    assert params[0]["description"] == "from-meta"


def test_get_paths_data_processing_list_model_name_extraction(monkeypatch):
    from inspect import Parameter
    from types import SimpleNamespace

    from starlette.routing import Route

    async def endpoint():
        return None

    endpoint.operation_id = "mod.func"
    endpoint.include_in_api = True
    endpoint.openapi_extra = {"model": ""}

    route = Route("/dp-list", endpoint=endpoint)
    route.path = "/dp-list"
    route.include_in_schema = True

    class _Model:
        model_fields = {
            "name": SimpleNamespace(
                annotation=str,
                is_required=lambda: True,
                description="nm",
                default=PydanticUndefined,
                json_schema_extra={},
            )
        }

    import sys

    setattr(sys.modules[endpoint.__module__], "_Model", _Model)

    monkeypatch.setattr(
        ReferenceGenerator,
        "_extract_return_type",
        staticmethod(
            lambda _f: {"OBBject": [{"name": "results", "type": "list[_Model]"}]}
        ),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.is_deprecated_function",
        staticmethod(lambda _p: False),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.get_deprecation_message",
        staticmethod(lambda _p: ""),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.method_definition.MethodDefinition.format_params",
        staticmethod(
            lambda **_k: {
                "x": SimpleNamespace(name="x", annotation=str, default=Parameter.empty)
            }
        ),
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.docstring_generator.DocstringGenerator.generate",
        classmethod(lambda cls, **_k: "Desc\n\nParameters\n----------\n"),
    )

    out = ReferenceGenerator.get_paths({"/dp-list": route})
    assert out["/dp-list"]["data"]["standard"][0]["name"] == "name"
