"""Test provider interface."""

from dataclasses import is_dataclass
from typing import Literal

import pytest
from pydantic.fields import FieldInfo

from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.provider.registry_map import RegistryMap


@pytest.fixture
def provider_interface(fake_registry):
    """``ProviderInterface`` built over the fake registry from conftest."""
    # ``ProviderInterface`` is a singleton — clear any cached instance built by
    # earlier tests so this fixture's injected registry actually takes effect.
    ProviderInterface._instances.pop(ProviderInterface, None)  # type: ignore[attr-defined]
    pi = ProviderInterface(registry_map=RegistryMap(registry=fake_registry))
    yield pi
    ProviderInterface._instances.pop(ProviderInterface, None)  # type: ignore[attr-defined]


@pytest.fixture
def multi_provider_interface(multi_provider_registry):
    """``ProviderInterface`` over the multi-provider fake registry."""
    ProviderInterface._instances.pop(ProviderInterface, None)  # type: ignore[attr-defined]
    pi = ProviderInterface(registry_map=RegistryMap(registry=multi_provider_registry))
    yield pi
    ProviderInterface._instances.pop(ProviderInterface, None)  # type: ignore[attr-defined]


def test_init(provider_interface):
    """Constructor wires through the injected registry map."""
    assert provider_interface
    assert isinstance(provider_interface.map, dict)


def test_map_exposes_registered_models(
    provider_interface, fake_model_name, single_result_model_name
):
    """``map`` keys are exactly the model names registered on the fake provider."""
    provider_interface_map = provider_interface.map
    assert set(provider_interface_map.keys()) == {
        fake_model_name,
        single_result_model_name,
    }


def test_map_separates_openbb_and_provider_buckets(
    provider_interface, fake_model_name, fake_provider_name
):
    """For each model, ``map[model]`` contains an ``"openbb"`` key plus each provider key."""
    bucket = provider_interface.map[fake_model_name]
    assert "openbb" in bucket
    assert fake_provider_name in bucket
    assert "QueryParams" in bucket["openbb"]
    assert "Data" in bucket["openbb"]


def test_credentials_namespaced_through_interface(
    provider_interface, fake_provider_name, fake_credential_names
):
    """``credentials`` mirrors the underlying ``RegistryMap``'s namespacing."""
    creds = provider_interface.credentials
    assert isinstance(creds, dict)
    assert creds[fake_provider_name] == fake_credential_names


def test_model_providers_returns_dataclass_per_model(
    provider_interface, fake_model_name
):
    """``model_providers[model]`` is a dataclass type (the per-model ``ProviderChoices``)."""
    model_providers = provider_interface.model_providers
    assert fake_model_name in model_providers

    choices_dc = model_providers[fake_model_name]
    assert is_dataclass(choices_dc)


def test_params_split_into_standard_and_extra(provider_interface, fake_model_name):
    """``params[model]`` exposes ``standard``/``extra`` dataclasses (FastAPI deps)."""
    params = provider_interface.params[fake_model_name]
    assert "standard" in params
    assert "extra" in params
    assert is_dataclass(params["standard"])
    assert is_dataclass(params["extra"])


def test_data_split_into_standard_and_extra(provider_interface, fake_model_name):
    """``data[model]`` exposes ``standard``/``extra`` Pydantic model classes.

    Note the asymmetry with ``params``: ``params`` are dataclasses (FastAPI
    dependency-injectable), ``data`` are Pydantic models (validate JSON payloads).
    """
    from pydantic import BaseModel

    data = provider_interface.data[fake_model_name]
    assert "standard" in data
    assert "extra" in data
    assert isinstance(data["standard"], type) and issubclass(
        data["standard"], BaseModel
    )
    assert isinstance(data["extra"], type) and issubclass(data["extra"], BaseModel)


def test_data_extra_carries_provider_specific_fields(
    provider_interface, fake_model_name
):
    """The ``extra`` data model exposes provider-specific fields under namespaced keys."""
    extra_model = provider_interface.data[fake_model_name]["extra"]
    # ``extra_field`` is on _FakeData (the provider data model). It is exposed
    # on the merged extra model under a provider-namespaced field name.
    field_names = set(
        (
            extra_model if isinstance(extra_model, type) else type(extra_model)
        ).model_fields.keys()
    )
    assert any("extra_field" in name for name in field_names), field_names


def test_available_providers_excludes_openbb_sentinel(
    multi_provider_interface, fake_provider_name, second_fake_provider_name
):
    """``available_providers`` lists registered providers, never the ``openbb`` sentinel."""
    available = multi_provider_interface.available_providers
    assert "openbb" not in available
    assert fake_provider_name in available
    assert second_fake_provider_name in available
    # And the list is sorted (stability for downstream Literal generation)
    assert available == sorted(available)


def test_provider_choices_literal_matches_available_providers(
    multi_provider_interface,
):
    """``provider_choices`` is a dataclass whose ``provider`` field Literal equals the provider list."""
    choices = multi_provider_interface.provider_choices
    assert is_dataclass(choices)

    provider_field = choices.__dataclass_fields__["provider"]
    # Literal[<providers>] — extract args
    from typing import get_args

    literal_args = set(get_args(provider_field.type))
    assert literal_args == set(multi_provider_interface.available_providers)


def test_models_matches_map_keys(provider_interface):
    """``models`` is a list view of ``map`` keys."""
    assert set(provider_interface.models) == set(provider_interface.map.keys())


def test_return_annotations_present_for_each_model(
    provider_interface, fake_model_name, single_result_model_name
):
    """Each registered model has a corresponding return annotation."""
    annotations = provider_interface.return_annotations
    assert fake_model_name in annotations
    assert single_result_model_name in annotations


def test_return_schema_property(provider_interface):
    assert provider_interface.return_schema is provider_interface._return_schema


def test_create_executor_uses_injected_registry(provider_interface, fake_registry):
    """``create_executor`` instantiates the executor over the injected registry."""
    executor = provider_interface.create_executor()
    # The executor stores the registry it was built with
    assert getattr(executor, "registry", None) is fake_registry


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
    field = FieldInfo(annotation=Literal["annual", "quarterly"] | None, default=None)
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
