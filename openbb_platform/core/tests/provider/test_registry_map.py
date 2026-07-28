"""Behavioral tests for ``RegistryMap``.

These tests exercise the *transformations* ``RegistryMap`` performs on a
``Registry`` — field bucketing, multi-provider model merging, results-type
extraction, credential namespacing and validation — using only fake
providers built in ``tests/conftest.py``. The suite intentionally does
not depend on any installed provider extension.
"""

from typing import Any

import pytest
from pydantic import BaseModel

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.registry import Registry
from openbb_core.provider.registry_map import RegistryMap


@pytest.fixture
def registry_map(fake_registry: Registry) -> RegistryMap:
    """``RegistryMap`` over the single-provider fake registry."""
    return RegistryMap(registry=fake_registry)


@pytest.fixture
def multi_registry_map(multi_provider_registry: Registry) -> RegistryMap:
    """``RegistryMap`` over the multi-provider fake registry."""
    return RegistryMap(registry=multi_provider_registry)


def test_credentials_are_namespaced_with_provider_prefix(
    registry_map: RegistryMap,
    fake_provider_name: str,
    fake_credential_names: list[str],
):
    """Each declared credential becomes ``{provider}_{cred}``."""
    creds = registry_map.credentials[fake_provider_name]

    assert creds == fake_credential_names
    assert all(c.startswith(f"{fake_provider_name}_") for c in creds)


def test_credentials_are_empty_for_provider_with_no_credentials(
    multi_registry_map: RegistryMap, second_fake_provider_name: str
):
    """Providers constructed with ``credentials=None`` map to an empty list."""
    assert multi_registry_map.credentials[second_fake_provider_name] == []


def test_available_providers_is_sorted(multi_registry_map: RegistryMap):
    """``available_providers`` returns a sorted list of provider names."""
    available = multi_registry_map.available_providers
    assert available == sorted(available)


def test_models_are_keys_of_standard_extra(registry_map: RegistryMap):
    """``models`` is a list view of ``standard_extra``'s top-level keys."""
    assert set(registry_map.models) == set(registry_map.standard_extra.keys())


def test_standard_fields_land_under_openbb_bucket(
    registry_map: RegistryMap, fake_model_name: str
):
    """Fields defined on the standard model are exposed under the ``"openbb"`` key."""
    openbb_bucket = registry_map.standard_extra[fake_model_name]["openbb"]
    standard_query_fields = openbb_bucket["QueryParams"]["fields"]
    standard_data_fields = openbb_bucket["Data"]["fields"]

    # AvailableIndicatorsData declares these on the standard model
    assert "symbol" in standard_data_fields
    assert "country" in standard_data_fields

    # AvailableIndicesQueryParams declares no fields, so the standard query bucket is empty
    assert standard_query_fields == {}


def test_provider_specific_fields_land_under_provider_bucket(
    registry_map: RegistryMap,
    fake_provider_name: str,
    fake_model_name: str,
):
    """Fields defined only on the provider subclass live under the provider key."""
    provider_bucket = registry_map.standard_extra[fake_model_name][fake_provider_name]
    provider_data_fields = provider_bucket["Data"]["fields"]

    # ``extra_field`` is only defined on _FakeData, not on the standard model
    assert "extra_field" in provider_data_fields
    # And inherited standard fields must NOT be duplicated into the provider bucket
    assert "symbol" not in provider_data_fields
    assert "country" not in provider_data_fields


def test_inherited_query_params_are_not_duplicated(
    multi_registry_map: RegistryMap,
    fake_provider_name: str,
    second_fake_provider_name: str,
    fake_model_name: str,
):
    """A provider that adds query fields gets only its new fields, not standard ones."""
    second_query = multi_registry_map.standard_extra[fake_model_name][
        second_fake_provider_name
    ]["QueryParams"]["fields"]
    primary_query = multi_registry_map.standard_extra[fake_model_name][
        fake_provider_name
    ]["QueryParams"]["fields"]

    # _SecondFakeQueryParams adds ``region`` and inherits nothing else novel
    assert list(second_query.keys()) == ["region"]
    # _FakeQueryParams adds nothing of its own
    assert primary_query == {}


def test_multi_provider_same_model_each_get_their_own_bucket(
    multi_registry_map: RegistryMap,
    fake_provider_name: str,
    second_fake_provider_name: str,
    fake_model_name: str,
):
    """Both providers exposing the same model appear under that model's key."""
    buckets = multi_registry_map.standard_extra[fake_model_name]
    assert "openbb" in buckets
    assert fake_provider_name in buckets
    assert second_fake_provider_name in buckets


def test_openbb_bucket_is_deepcopied_per_model(
    multi_registry_map: RegistryMap,
    fake_model_name: str,
    single_result_model_name: str,
):
    """Mutating the ``openbb`` bucket of one model must not leak to siblings."""
    bucket_a = multi_registry_map.standard_extra[fake_model_name]["openbb"]
    bucket_b = multi_registry_map.standard_extra[single_result_model_name]["openbb"]

    # Different dict objects (deepcopy)
    assert bucket_a is not bucket_b
    bucket_a["sentinel"] = "polluted"
    assert "sentinel" not in bucket_b


def test_provider_specific_fields_are_isolated_between_providers(
    multi_registry_map: RegistryMap,
    fake_provider_name: str,
    second_fake_provider_name: str,
    fake_model_name: str,
):
    """``extra_field`` from provider A must not appear under provider B's bucket."""
    primary_fields = multi_registry_map.standard_extra[fake_model_name][
        fake_provider_name
    ]["Data"]["fields"]
    secondary_fields = multi_registry_map.standard_extra[fake_model_name][
        second_fake_provider_name
    ]["Data"]["fields"]

    assert "extra_field" in primary_fields
    assert "extra_field" not in secondary_fields
    assert "second_extra" in secondary_fields
    assert "second_extra" not in primary_fields


def test_original_models_records_query_data_and_results_type(
    registry_map: RegistryMap,
    fake_provider_name: str,
    fake_model_name: str,
    standard_data_cls: type[Data],
    standard_query_cls: type[QueryParams],
):
    """Each ``original_models`` entry records query class, data class and results type."""
    record = registry_map.original_models[fake_model_name][fake_provider_name]

    assert set(record.keys()) == {"query", "data", "results_type"}
    assert issubclass(record["query"], standard_query_cls)
    assert issubclass(record["data"], standard_data_cls)
    # Fetcher returns ``list[_FakeData]`` → ``get_origin`` is ``list``
    assert record["results_type"] is list


def test_results_type_is_none_for_single_data_return(
    registry_map: RegistryMap,
    fake_provider_name: str,
    single_result_model_name: str,
):
    """A fetcher returning a single ``Data`` (not ``list[Data]``) has ``results_type=None``."""
    record = registry_map.original_models[single_result_model_name][fake_provider_name]
    assert record["results_type"] is None


def test_validate_rejects_non_data_subclass():
    """``_validate`` raises ``ValueError`` for a non-``Data`` data type."""

    class NotData(BaseModel):
        x: int = 0

    with pytest.raises(ValueError, match="must be a subclass of 'Data'"):
        RegistryMap._validate(NotData, "data")


def test_validate_rejects_non_query_params_subclass():
    """``_validate`` raises ``ValueError`` for a non-``QueryParams`` query type."""

    class NotQuery(BaseModel):
        x: int = 0

    with pytest.raises(ValueError, match="must be a subclass of 'QueryParams'"):
        RegistryMap._validate(NotQuery, "query_params")


def test_validate_accepts_proper_subclasses(
    standard_data_cls: type[Data], standard_query_cls: type[QueryParams]
):
    """``_validate`` returns ``None`` (no raise) for proper subclasses."""
    assert RegistryMap._validate(standard_data_cls, "data") is None
    assert RegistryMap._validate(standard_query_cls, "query_params") is None


def test_invalid_fetcher_data_type_fails_registry_map_construction(
    fake_provider_name: str,
):
    """A registry containing a fetcher with a bogus data type raises on map build."""

    class BogusReturn(BaseModel):
        x: int = 0

    class _FakeQ(QueryParams):
        pass

    class BogusFetcher(Fetcher[_FakeQ, list[BogusReturn]]):  # type: ignore[type-var]
        require_credentials = False

        @staticmethod
        def transform_query(params: dict[str, Any]) -> _FakeQ:
            return _FakeQ(**params)

        @staticmethod
        def extract_data(
            query: _FakeQ, credentials: dict[str, str] | None
        ) -> list[dict[str, Any]]:
            return []

        @staticmethod
        def transform_data(
            query: _FakeQ, data: list[dict[str, Any]], **kwargs
        ) -> list[BogusReturn]:
            return []

    from openbb_core.provider.abstract.provider import Provider

    bad_provider = Provider(
        name="bad",
        description="bad",
        fetcher_dict={"BogusModel": BogusFetcher},
    )
    registry = Registry()
    registry.include_provider(bad_provider)

    with pytest.raises(ValueError, match="must be a subclass of 'Data'"):
        RegistryMap(registry=registry)


def test_registry_property_round_trips(
    registry_map: RegistryMap, fake_registry: Registry
):
    """``registry`` exposes the exact ``Registry`` instance passed in."""
    assert registry_map.registry is fake_registry


def test_default_construction_uses_extension_loader(monkeypatch):
    """When no registry is supplied, ``RegistryMap`` falls back to ``RegistryLoader``."""
    sentinel_registry = Registry()
    called = {}

    def _fake_from_extensions():
        called["hit"] = True
        return sentinel_registry

    monkeypatch.setattr(
        "openbb_core.provider.registry_map.RegistryLoader.from_extensions",
        _fake_from_extensions,
    )

    rmap = RegistryMap()

    assert called.get("hit") is True
    assert rmap.registry is sentinel_registry
    assert rmap.available_providers == []
    assert rmap.credentials == {}
    assert rmap.models == []


def test_update_json_schema_extra_merges_standard_and_extra_fields():
    class _Q(QueryParams):
        std: str
        extra: str
        __json_schema_extra__ = {
            "std": {"multiple_items_allowed": True},
            "extra": {"choices": ["a", "b"]},
            "missing": {"ignored": True},
        }

    class _D(Data):
        value: int

    class _F(Fetcher[_Q, list[_D]]):
        query_params_type = _Q
        data_type = _D
        return_type = list[_D]

        @staticmethod
        def transform_query(params: dict[str, Any]) -> _Q:
            return _Q(**params)

        @staticmethod
        def extract_data(query: _Q, credentials: dict[str, str] | None):
            return []

        @staticmethod
        def transform_data(query: _Q, data, **kwargs):
            return []

    model_map = {
        "openbb": {"QueryParams": {"fields": {"std": _Q.model_fields["std"]}}},
        "prov": {"QueryParams": {"fields": {"extra": _Q.model_fields["extra"]}}},
    }

    RegistryMap(registry=Registry())._update_json_schema_extra("prov", _F, model_map)

    assert model_map["openbb"]["QueryParams"]["fields"]["std"].json_schema_extra == {
        "prov": {"multiple_items_allowed": True}
    }
    assert model_map["prov"]["QueryParams"]["fields"]["extra"].json_schema_extra == {
        "prov": {"choices": ["a", "b"]}
    }
