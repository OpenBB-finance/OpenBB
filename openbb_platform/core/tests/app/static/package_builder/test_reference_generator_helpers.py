"""Direct unit tests for static helpers in ``ReferenceGenerator``."""

from typing import Annotated

import pytest

pandas = pytest.importorskip("pandas")

pytestmark = pytest.mark.requires_pandas

from fastapi import Query
from pydantic import Field
from pydantic.fields import FieldInfo

from openbb_core.app.static.package_builder.reference_generator import (
    ReferenceGenerator,
)


def test_clean_string_values_replaces_full_data_path():
    out = ReferenceGenerator._clean_string_values(
        "openbb_core.provider.abstract.data.Data"
    )
    assert out == "Data"


def test_clean_string_values_replaces_list_of_data_path():
    out = ReferenceGenerator._clean_string_values(
        "list[openbb_core.provider.abstract.data.Data]"
    )
    assert out == "list[Data]"


def test_clean_string_values_simplifies_union_type():
    out = ReferenceGenerator._clean_string_values("Union[int, str]")
    # Sorted alphabetically and joined with ' | '
    assert out == "int | str"


def test_clean_string_values_quotes_literal_members():
    out = ReferenceGenerator._clean_string_values("Literal[a, b]")
    assert out == "Literal['a', 'b']"


def test_clean_string_values_does_not_requote_already_quoted_literal():
    out = ReferenceGenerator._clean_string_values("Literal['a', 'b']")
    # Already quoted -> the literal-quoting branch is skipped
    assert "Literal['a', 'b']" in out


def test_clean_string_values_lowercases_dict_and_list_aliases():
    out = ReferenceGenerator._clean_string_values("Dict[str, List[int]]")
    assert "dict" in out
    assert "list" in out
    assert "Dict" not in out
    assert "List" not in out


def test_clean_string_values_recurses_into_dict():
    out = ReferenceGenerator._clean_string_values(
        {"a": "Union[int, str]", "b": "Dict[str, int]"}
    )
    assert out == {"a": "int | str", "b": "dict[str, int]"}


def test_clean_string_values_recurses_into_list():
    out = ReferenceGenerator._clean_string_values(["List[int]", "Dict[str, str]"])
    assert out == ["list[int]", "dict[str, str]"]


def test_clean_string_values_passthrough_non_string():
    assert ReferenceGenerator._clean_string_values(42) == 42
    assert ReferenceGenerator._clean_string_values(None) is None


def test_get_obbject_returns_fields_default_provider():
    out = ReferenceGenerator._get_obbject_returns_fields("MyModel", "")
    assert isinstance(out, list)
    names = [item["name"] for item in out]
    assert names == ["results", "provider", "warnings", "chart", "extra"]
    # When providers is empty, the type defaults to 'str'
    provider_entry = next(item for item in out if item["name"] == "provider")
    assert provider_entry["type"] == "str"


def test_get_obbject_returns_fields_with_providers():
    out = ReferenceGenerator._get_obbject_returns_fields("MyModel", "fmp, polygon")
    provider_entry = next(item for item in out if item["name"] == "provider")
    assert provider_entry["type"] == "fmp, polygon"


def test_get_post_method_returns_info_extracts_obbject_inner_type():
    docstring = (
        "Some description.\n\n"
        "Returns\n"
        "    -------\n"
        "    OBBject[list[Data]]\n"
        "        The OBBject of results.\n"
    )
    out = ReferenceGenerator._get_post_method_returns_info(docstring)
    assert out["name"] == "results"
    assert "list[Data]" in out["type"]
    assert "results" in out["description"] or out["description"]


def test_get_post_method_returns_info_handles_list_wrapper():
    docstring = (
        "Returns\n    -------\n    list[MyData]\n        A list of data points.\n"
    )
    out = ReferenceGenerator._get_post_method_returns_info(docstring)
    assert out["type"] == "MyData"


def test_get_post_method_returns_info_no_match_returns_empty_dict():
    out = ReferenceGenerator._get_post_method_returns_info("No returns section here.")
    assert out == {}


def test_get_post_method_parameters_info_extracts_params():
    docstring = (
        "Parameters\n"
        "    ----------\n"
        "    symbol : str\n"
        "        Symbol of the security.\n"
        "    limit : int, optional\n"
        "        Row limit.\n"
        "    Returns\n"
        "    -------\n"
        "    OBBject[Data]\n"
    )
    out = ReferenceGenerator._get_post_method_parameters_info(docstring)
    names = [p["name"] for p in out]
    assert "symbol" in names
    assert "limit" in names
    limit = next(p for p in out if p["name"] == "limit")
    assert limit["optional"] is True
    assert "optional" not in limit["type"]


def test_get_post_method_parameters_info_no_parameters_returns_empty():
    out = ReferenceGenerator._get_post_method_parameters_info("Just a description.")
    assert out == []


def test_get_post_method_parameters_info_optional_marker_in_type():
    docstring = (
        "Parameters\n    ----------\n    name : Optional[str]\n        A name.\n"
    )
    out = ReferenceGenerator._get_post_method_parameters_info(docstring)
    assert out[0]["optional"] is True


def test_resolve_field_type_str_required_simple():
    fi = FieldInfo(annotation=int)
    type_str, is_required = ReferenceGenerator._resolve_field_type_str(fi)
    assert is_required is True
    assert "int" in type_str


def test_resolve_field_type_str_optional_unwraps():
    fi = FieldInfo(annotation=str | None, default=None)
    type_str, is_required = ReferenceGenerator._resolve_field_type_str(fi)
    assert is_required is False
    assert "str" in type_str
    assert "| None" in type_str


def test_resolve_field_type_str_unwraps_annotated():
    fi = FieldInfo(
        annotation=Annotated[int, "metadata"],
        default=None,
    )
    type_str, is_required = ReferenceGenerator._resolve_field_type_str(fi)
    # Should not start with "Annotated"
    assert not type_str.startswith("Annotated")


def test_apply_query_param_extras_with_multiple_items_dict():
    desc, type_str, choices = ReferenceGenerator._apply_query_param_extras(
        cleaned_description="Symbol",
        field_type_str="str",
        choices=None,
        extra={"fmp": {"multiple_items_allowed": True, "choices": ["a", "b"]}},
    )
    assert "Multiple items allowed" in desc
    assert "fmp" in desc
    assert "list[str]" in type_str
    assert choices == ["a", "b"]


def test_apply_query_param_extras_legacy_list_format():
    desc, type_str, choices = ReferenceGenerator._apply_query_param_extras(
        cleaned_description="Symbol",
        field_type_str="str",
        choices=None,
        extra={"fmp": ["multiple_items_allowed"]},
    )
    assert "Multiple items allowed" in desc
    assert "list[str]" in type_str


def test_apply_query_param_extras_with_choices_only_no_multiple():
    desc, type_str, choices = ReferenceGenerator._apply_query_param_extras(
        cleaned_description="Symbol",
        field_type_str="str",
        choices=None,
        extra={"fmp": {"choices": ["x", "y"]}},
    )
    assert "Multiple items allowed" not in desc
    assert type_str == "str"
    assert choices == ["x", "y"]


def test_apply_query_param_extras_top_level_multiple_items():
    desc, type_str, _ = ReferenceGenerator._apply_query_param_extras(
        cleaned_description="Symbol",
        field_type_str="str",
        choices=None,
        extra={"multiple_items_allowed": True},
    )
    assert "Multiple items allowed" in desc
    assert "list[str]" in type_str


def test_get_function_signature_info_basic_params():
    def f(a: int, b: str = "x", c: int | None = None) -> None:
        return None

    out = ReferenceGenerator._get_function_signature_info(f)
    names = [p["name"] for p in out]
    assert names == ["a", "b", "c"]
    a, b, c = out
    assert a["optional"] is False
    assert b["optional"] is True
    assert b["default"] == "x"
    assert c["optional"] is True
    assert "int" in c["type"]


def test_get_function_signature_info_skips_self_and_cc():
    def f(self, cc, x: int) -> None:
        return None

    out = ReferenceGenerator._get_function_signature_info(f)
    names = [p["name"] for p in out]
    assert names == ["x"]


def test_get_function_signature_info_with_query_default():
    def f(symbol: str = Query(default="AAPL", description="Ticker symbol")) -> None:
        return None

    out = ReferenceGenerator._get_function_signature_info(f)
    assert out[0]["name"] == "symbol"
    assert out[0]["description"] == "Ticker symbol"
    assert out[0]["optional"] is True
    assert out[0]["default"] == "AAPL"


def test_get_function_signature_info_with_annotated_metadata():
    def f(x: Annotated[int, Field(description="x val")]) -> None:
        return None

    out = ReferenceGenerator._get_function_signature_info(f)
    assert out[0]["description"] == "x val"
    # base type stripped from Annotated
    assert "int" in out[0]["type"]


def test_get_function_signature_info_skips_depends_default():
    from fastapi import Depends

    def dep():
        return None

    def f(x: int = Depends(dep)) -> None:
        return None

    out = ReferenceGenerator._get_function_signature_info(f)
    assert out == []


def test_resolve_field_type_str_typing_union_optional_branch():
    fi = FieldInfo(annotation=str | None, default=None)
    type_str, is_required = ReferenceGenerator._resolve_field_type_str(fi)
    assert is_required is False
    assert "str" in type_str


def test_get_function_signature_info_typing_union_optional_branch():
    def f(x: int | None = None) -> None:
        return None

    out = ReferenceGenerator._get_function_signature_info(f)
    assert out[0]["name"] == "x"
    assert out[0]["optional"] is True
    assert "int" in out[0]["type"]


def test_resolve_field_type_str_union_branch_with_pep604(monkeypatch):
    from types import UnionType

    from openbb_core.app.static.package_builder import reference_generator as rg

    monkeypatch.setattr(rg, "Union", UnionType)

    fi = FieldInfo(annotation=str | None, default=None)
    type_str, is_required = ReferenceGenerator._resolve_field_type_str(fi)
    assert is_required is False
    assert "str" in type_str
    assert "| None" in type_str


def test_get_function_signature_info_union_optional_branch_with_pep604(monkeypatch):
    from types import UnionType

    from openbb_core.app.static.package_builder import reference_generator as rg

    monkeypatch.setattr(rg, "Union", UnionType)

    def f(x: int | None = None) -> None:
        return None

    out = ReferenceGenerator._get_function_signature_info(f)
    assert out[0]["name"] == "x"
    assert out[0]["optional"] is True
    assert "int" in out[0]["type"]


def test_resolve_field_type_str_forced_union_branch(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.static.package_builder import reference_generator as rg

    union_sentinel = object()
    monkeypatch.setattr(rg, "Union", union_sentinel)
    monkeypatch.setattr(rg, "get_origin", lambda _x: union_sentinel)
    monkeypatch.setattr(rg, "get_args", lambda _x: (str, type(None)))

    fi = SimpleNamespace(annotation=object(), is_required=lambda: True)
    type_str, is_required = ReferenceGenerator._resolve_field_type_str(fi)

    assert is_required is False
    assert "str" in type_str
    assert "| None" in type_str


def test_get_function_signature_info_forced_optional_union_branch(monkeypatch):
    from inspect import Parameter, Signature

    from openbb_core.app.static.package_builder import reference_generator as rg

    union_sentinel = object()

    class _FakeOptionalType:
        __origin__ = union_sentinel
        __args__ = (int, type(None))

    fake_param = Parameter(
        "x",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=_FakeOptionalType,
        default=0,
    )
    fake_sig = Signature(parameters=[fake_param])

    monkeypatch.setattr(rg, "Union", union_sentinel)
    monkeypatch.setattr(rg, "signature", lambda _func: fake_sig)

    out = ReferenceGenerator._get_function_signature_info(lambda: None)
    assert out[0]["name"] == "x"
    assert out[0]["optional"] is True
    assert "int" in out[0]["type"]
