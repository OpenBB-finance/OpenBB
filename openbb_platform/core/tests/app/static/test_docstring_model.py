"""Drive `generate_model_docstring` kwarg-param branches.

Targets format_description's "Choices for", "(provider:", "Multiple comma
separated", json_schema_extra Literal/multiple_items_allowed paths.
"""

from inspect import Parameter
from types import SimpleNamespace
from typing import Annotated, Literal

import pytest

pandas = pytest.importorskip("pandas")
pytestmark = pytest.mark.requires_pandas

from openbb_core.app.model.field import OpenBBField  # noqa: E402
from openbb_core.app.static.package_builder import DocstringGenerator  # noqa: E402


class _Query:
    """Stand-in for fastapi.Query — class name contains 'Query'."""

    def __init__(self, description="", json_schema_extra=None):
        self.description = description
        self.json_schema_extra = json_schema_extra


def _kwarg(
    type_,
    description="",
    json_schema_extra=None,
    annotation=None,
):
    """Build a fake dataclass-style field that mimics provider extras."""
    default = _Query(description=description, json_schema_extra=json_schema_extra)
    return SimpleNamespace(type=type_, default=default, annotation=annotation)


def test_kwargs_with_literal_choices_and_provider_in_description():
    g = DocstringGenerator()
    kwargs = {
        "asset_type": _kwarg(
            type_=Literal["stock", "etf"],
            description="The asset (provider: prov_a)",
        )
    }
    out = g.generate_model_docstring(
        model_name="X",
        summary="A summary.",
        explicit_params={},
        kwarg_params=kwargs,
        returns={},
        results_type="X",
        sections=["description", "parameters", "returns"],
    )
    assert "asset_type" in out
    assert "Choices for prov_a" in out


def test_kwargs_with_json_schema_extra_choices():
    g = DocstringGenerator()
    kwargs = {
        "exchange": _kwarg(
            type_=str,
            description="An exchange.",
            json_schema_extra={
                "prov_a": {"choices": ["nyse", "nasdaq"]},
                "prov_b": {"choices": ["lse", "tsx"], "multiple_items_allowed": True},
            },
        )
    }
    out = g.generate_model_docstring(
        model_name="X",
        summary="x",
        explicit_params={},
        kwarg_params=kwargs,
        returns={},
        results_type="X",
        sections=["parameters"],
    )
    assert "Choices for prov_a" in out
    assert "Choices for prov_b" in out
    assert "Multiple comma separated items allowed for provider(s): prov_b" in out


def test_kwargs_with_multiple_items_only():
    g = DocstringGenerator()
    kwargs = {
        "symbol": _kwarg(
            type_=str,
            description="The symbol.",
            json_schema_extra={"prov_a": {"multiple_items_allowed": True}},
        )
    }
    out = g.generate_model_docstring(
        model_name="X",
        summary="x",
        explicit_params={},
        kwarg_params=kwargs,
        returns={},
        results_type="X",
        sections=["parameters"],
    )
    assert "Multiple comma separated items allowed for provider(s): prov_a" in out


def test_kwargs_description_with_choices_for_block():
    """Trigger the 'Choices for ' parsing branch in format_description."""
    g = DocstringGenerator()
    description = (
        "An exchange.\n"
        "Choices for prov_a: nyse, nasdaq\n"
        "Choices for prov_b: lse, tsx\n"
        "Multiple comma separated items allowed for provider(s): prov_a, prov_b."
    )
    kwargs = {"exchange": _kwarg(type_=str, description=description)}
    out = g.generate_model_docstring(
        model_name="X",
        summary="x",
        explicit_params={},
        kwarg_params=kwargs,
        returns={},
        results_type="X",
        sections=["parameters"],
    )
    assert "exchange" in out


def test_kwargs_description_with_provider_sections():
    """Trigger the '(provider: name)' formatting branch."""
    g = DocstringGenerator()
    description = (
        "Same first sentence. (provider: prov_a) Detail A.;"
        "Same first sentence. (provider: prov_b) Detail B."
    )
    kwargs = {"region": _kwarg(type_=str, description=description)}
    out = g.generate_model_docstring(
        model_name="X",
        summary="x",
        explicit_params={},
        kwarg_params=kwargs,
        returns={},
        results_type="X",
        sections=["parameters"],
    )
    assert "region" in out


def test_kwargs_with_long_choice_list_wraps():
    g = DocstringGenerator()
    long = [f"opt_{i}" for i in range(40)]
    kwargs = {
        "x": _kwarg(
            type_=str,
            description="X.",
            json_schema_extra={"prov": {"choices": long}},
        )
    }
    out = g.generate_model_docstring(
        model_name="X",
        summary="x",
        explicit_params={},
        kwarg_params=kwargs,
        returns={},
        results_type="X",
        sections=["parameters"],
    )
    assert "Choices for prov" in out


def test_kwargs_with_query_default_only():
    g = DocstringGenerator()
    default = _Query(description="From query default.", json_schema_extra=None)
    param = SimpleNamespace(type=str, default=default, annotation=None)
    out = g.generate_model_docstring(
        model_name="X",
        summary="x",
        explicit_params={},
        kwarg_params={"y": param},
        returns={},
        results_type="X",
        sections=["parameters"],
    )
    assert "From query default." in out


def test_explicit_provider_and_chart_params():
    g = DocstringGenerator()
    annot = Annotated[str, OpenBBField(description="The provider.")]
    provider_param = Parameter(
        "provider", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=annot
    )
    provider_param._annotation = annot  # type: ignore[attr-defined]

    chart_annot = Annotated[bool, OpenBBField(description="Chart it.")]
    chart_param = Parameter(
        "chart", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=chart_annot
    )
    chart_param._annotation = chart_annot  # type: ignore[attr-defined]

    other_annot = Annotated[str, OpenBBField(description="Other.")]
    other = Parameter(
        "symbol", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=other_annot
    )
    other._annotation = other_annot  # type: ignore[attr-defined]

    out = g.generate_model_docstring(
        model_name="X",
        summary="X command.",
        explicit_params={
            "symbol": other,
            "provider": provider_param,
            "chart": chart_param,
        },
        kwarg_params={},
        returns={},
        results_type="X",
        sections=["description", "parameters", "returns"],
    )
    assert "provider : str" in out
    assert "chart : bool" in out
    assert "symbol" in out


def test_format_description_provider_interface_lookup(monkeypatch):
    """Drive lines 647-694: Union p_type with provider_interface.map populated."""
    from dataclasses import dataclass
    from typing import Literal

    from openbb_core.app.static.package_builder.docstring_generator import (
        DocstringGenerator,
    )

    class _FieldInfoLiteral:
        annotation = Literal["x", "y", "z"]

    @dataclass
    class _Providers:
        provider: Literal["openbb", "prov_a", "prov_b"] = "prov_a"

    class _FakePI:
        model_providers = {"MyModel": _Providers}
        map = {
            "MyModel": {
                "openbb": {"QueryParams": {"fields": {"symbol": _FieldInfoLiteral()}}},
                "prov_a": {"QueryParams": {"fields": {"symbol": _FieldInfoLiteral()}}},
                "prov_b": {"QueryParams": {"fields": {}}},
            }
        }

    monkeypatch.setattr(DocstringGenerator, "provider_interface", _FakePI())

    kwargs = {
        "symbol": _kwarg(
            type_=Literal["x", "y", "z"] | None,
            description="Sym field. (provider: prov_a, prov_b)",
        )
    }
    out = DocstringGenerator().generate_model_docstring(
        model_name="MyModel",
        summary="S.",
        explicit_params={},
        kwarg_params=kwargs,
        returns={},
        results_type="X",
        sections=["description", "parameters", "returns"],
    )
    assert "symbol" in out
