"""Test provider interface."""

# pylint: disable=redefined-outer-name

from typing import Literal, Optional

import pytest
from openbb_core.app.provider_interface import (
    ProviderChoices,
    ProviderInterface,
)
from pydantic.fields import FieldInfo


@pytest.fixture(scope="module")
def provider_interface():
    """Set up provider_interface."""
    return ProviderInterface()


def test_init(provider_interface):
    """Test init."""
    assert provider_interface


def test_map(provider_interface):
    """Test map."""
    provider_interface_map = provider_interface.map
    assert isinstance(provider_interface_map, dict)
    assert len(provider_interface_map) > 0
    assert "EquityHistorical" in provider_interface_map


def test_credentials(provider_interface):
    """Test required credentials."""
    credentials = provider_interface.credentials
    assert isinstance(credentials, dict)
    assert len(credentials) > 0


def test_model_providers(provider_interface):
    """Test model providers."""
    model_providers = provider_interface.model_providers
    assert isinstance(model_providers, dict)
    assert len(model_providers) > 0


def test_params(provider_interface):
    """Test params."""
    params = provider_interface.params
    assert isinstance(params, dict)
    assert len(params) > 0
    assert "EquityHistorical" in params


def test_data(provider_interface):
    """Test data."""
    data = provider_interface.data
    assert isinstance(data, dict)
    assert len(data) > 0
    assert "EquityHistorical" in data


def test_available_providers(provider_interface):
    """Test providers literal."""
    available_providers = provider_interface.available_providers
    assert isinstance(available_providers, list)
    assert len(available_providers) > 0
    assert "openbb" not in available_providers


def test_provider_choices(provider_interface):
    """Test provider choices."""
    provider_choices = provider_interface.provider_choices
    assert isinstance(provider_choices, type(ProviderChoices))


def test_models(provider_interface):
    """Test models."""
    models = provider_interface.models
    assert isinstance(models, list)
    assert len(models) > 0
    assert "EquityHistorical" in models


# --- _create_field: Literal → choices auto-derivation ---


def test_create_field_literal_annotation_produces_choices():
    """
    _create_field must auto-derive choices from a Literal annotation.

    This is the core of the fix: a provider field declared as
    `frequency: Literal["annual", "quarterly"]` must cause _create_field to emit
    {"multiple_items_allowed": False, "choices": ["annual", "quarterly"]} into the
    json_schema_extra under the provider's key, so that filter_inputs can validate
    user values before the merged ExtraParams dataclass is built.
    """
    field = FieldInfo(annotation=Literal["annual", "quarterly"], default="quarterly")
    result = ProviderInterface._create_field("frequency", field, provider_name="oecd")
    extra = result.default.json_schema_extra
    assert extra is not None
    assert "oecd" in extra
    assert extra["oecd"]["choices"] == ["annual", "quarterly"]


def test_create_field_optional_literal_annotation_produces_choices():
    """
    _create_field must unwrap Optional[Literal[...]] and still derive choices.
    force_optional=True wraps Literal annotations in Optional — choices must survive.
    """
    field = FieldInfo(annotation=Optional[Literal["annual", "quarterly"]], default=None)
    result = ProviderInterface._create_field(
        "frequency", field, provider_name="oecd", force_optional=True
    )
    extra = result.default.json_schema_extra
    assert extra is not None
    assert "oecd" in extra
    assert extra["oecd"]["choices"] == ["annual", "quarterly"]


def test_create_field_str_annotation_produces_no_choices():
    """
    _create_field must NOT produce choices for a plain str annotation.
    Only Literal annotations trigger auto-derivation.
    """
    field = FieldInfo(annotation=str, default="quarterly")
    result = ProviderInterface._create_field("frequency", field, provider_name="oecd")
    extra = result.default.json_schema_extra if result.default else None
    # Either no extra at all, or extra does not contain choices for this provider
    if extra and "oecd" in extra:
        assert "choices" not in extra["oecd"]


def test_create_field_explicit_choices_not_overwritten():
    """
    When json_schema_extra already declares explicit choices for a provider,
    _create_field must not overwrite them with auto-derived Literal choices.
    Explicit choices take precedence.
    """
    field = FieldInfo(
        annotation=Literal["annual", "quarterly"],
        default="quarterly",
        json_schema_extra={"oecd": {"choices": ["annual"]}},
    )
    result = ProviderInterface._create_field("frequency", field, provider_name="oecd")
    extra = result.default.json_schema_extra
    # The explicit single-item choices list must be preserved, not expanded to both values
    assert extra["oecd"]["choices"] == ["annual"]
