"""Unit tests for the IMF Economic Indicators model and fetcher."""

# ruff: noqa: I001

from datetime import date
from typing import Any
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_imf.models.economic_indicators import (
    ImfEconomicIndicatorsData,
    ImfEconomicIndicatorsFetcher,
    ImfEconomicIndicatorsQueryParams,
)


class _StubMetadata:
    """Lightweight ``ImfMetadata`` stand-in for symbol/constraint validation."""

    def __init__(
        self,
        codelist: dict[str, dict[str, str]] | None = None,
        dataflows: dict[str, dict[str, Any]] | None = None,
        datastructures: dict[str, dict[str, Any]] | None = None,
        hierarchies: dict[str, list[dict[str, Any]]] | None = None,
        constraints: dict[tuple, dict[str, Any]] | None = None,
        dataflow_parameters: dict[str, dict[str, list[dict[str, str]]]] | None = None,
    ):
        self._codelist_cache = codelist or {"CL_COUNTRY": {"USA": "United States"}}
        self.dataflows = dataflows or {}
        self.datastructures = datastructures or {}
        self._hierarchies = hierarchies or {}
        self._constraints = constraints or {}
        self._dataflow_parameters = dataflow_parameters or {}
        self.hierarchies_calls: list[str] = []
        self.constraints_calls: list[dict[str, Any]] = []

    def get_dataflow_hierarchies(self, dataflow_id: str) -> list[dict[str, Any]]:
        """Return canned hierarchies for the dataflow."""
        self.hierarchies_calls.append(dataflow_id)
        return self._hierarchies.get(dataflow_id, [])

    def get_dataflow_parameters(
        self, dataflow_id: str
    ) -> dict[str, list[dict[str, str]]]:
        """Return canned dimension parameters for the dataflow."""
        return self._dataflow_parameters.get(dataflow_id, {})

    def get_available_constraints(
        self,
        dataflow_id: str,
        key: str,
        component_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Return canned constraint payload for a dataflow/key/component combo."""
        self.constraints_calls.append(
            {"dataflow_id": dataflow_id, "key": key, "component_id": component_id}
        )
        return self._constraints.get((dataflow_id, component_id), {"key_values": []})


def _patch_metadata(monkeypatch: pytest.MonkeyPatch, stub: _StubMetadata) -> None:
    """Replace ``ImfMetadata`` with a callable returning the stub."""
    monkeypatch.setattr(
        "openbb_imf.utils.metadata.ImfMetadata",
        lambda: stub,
    )


def _patch_detect_transform_dimension(
    monkeypatch: pytest.MonkeyPatch,
    transform_dim: str | None = None,
    unit_dim: str | None = None,
    transform_lookup: dict[str, str] | None = None,
    unit_lookup: dict[str, str] | None = None,
) -> None:
    """Force ``detect_transform_dimension`` to return a fixed shape."""
    monkeypatch.setattr(
        "openbb_imf.models.economic_indicators.detect_transform_dimension",
        lambda _dataflow: (
            transform_dim,
            unit_dim,
            transform_lookup or {},
            unit_lookup or {},
        ),
    )


def _make_query(
    monkeypatch: pytest.MonkeyPatch,
    *,
    symbol: str = "WEO::NGDP_RPCH",
    country: str = "USA",
    metadata_stub: _StubMetadata | None = None,
    **overrides: Any,
) -> ImfEconomicIndicatorsQueryParams:
    """Construct a query with a metadata stub patched in for the lifetime of the call."""
    if metadata_stub is None:
        metadata_stub = _StubMetadata()
    _patch_metadata(monkeypatch, metadata_stub)
    params: dict[str, Any] = {"symbol": symbol, "country": country}
    params.update(overrides)
    return ImfEconomicIndicatorsQueryParams(**params)


class TestValidateCountry:
    """Tests for ``ImfEconomicIndicatorsQueryParams.validate_country``."""

    def test_empty_string_returns_none(self, monkeypatch):
        """An empty string short-circuits to ``None`` (covers line 178)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(ValueError, match="Country is required"):
            ImfEconomicIndicatorsQueryParams(symbol="WEO::X", country="")

    def test_only_commas_returns_none(self, monkeypatch):
        """A string of only commas yields an empty items list (covers line 183)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(ValueError, match="Country is required"):
            ImfEconomicIndicatorsQueryParams(symbol="WEO::X", country=",,")

    def test_single_wildcard(self, monkeypatch):
        """A single ``*`` value short-circuits to wildcard (covers line 186)."""
        q = _make_query(monkeypatch, country="*")
        assert q.country == "*"

    def test_resolves_name_to_code_via_lower(self, monkeypatch):
        """Snake-case names resolve via the lowercase mapping (covers line 216)."""
        stub = _StubMetadata(
            codelist={"CL_COUNTRY": {"USA": "United States", "DEU": "Germany"}}
        )
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(
            symbol="WEO::NGDP_RPCH", country="united_states"
        )
        assert q.country == "USA"

    def test_falls_back_to_item_upper(self, monkeypatch):
        """An unknown token falls through to ``item_upper`` (covers line 220)."""
        stub = _StubMetadata(codelist={"CL_COUNTRY": {}})
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(symbol="WEO::NGDP_RPCH", country="zzz")
        assert q.country == "ZZZ"

    def test_wildcard_overrides_other_items(self, monkeypatch):
        """A second-item wildcard takes precedence (covers line 211)."""
        stub = _StubMetadata(codelist={"CL_COUNTRY": {"USA": "United States"}})
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(symbol="WEO::NGDP_RPCH", country="USA,*")
        assert q.country == "*"

    def test_resolves_lowercase_name_branch(self, monkeypatch):
        """A name with spaces takes the ``item.lower()`` lookup branch (covers 217-218).

        Notes
        -----
        ``item_lower`` substitutes ``_`` for spaces but leaves commas; passing the
        original label exercises the case where the snake form mismatches but
        the lowercase original matches.
        """
        stub = _StubMetadata(
            codelist={"CL_COUNTRY": {"CIV": "Côte d'Ivoire"}},
        )
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(
            symbol="WEO::NGDP_RPCH", country="Côte d'Ivoire"
        )
        assert q.country == "CIV"


class TestParseAndValidateSymbols:
    """Tests for ``parse_and_validate_symbols``."""

    def test_missing_symbol_raises(self, monkeypatch):
        """A blank symbol raises a ``ValueError`` (covers line 230)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(ValueError, match="symbol is required"):
            ImfEconomicIndicatorsQueryParams(symbol=None, country="USA")

    def test_dimension_values_extract_country(self, monkeypatch):
        """A ``COUNTRY`` dimension value populates ``country`` (covers 244-261)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(
            symbol="WEO::NGDP_RPCH",
            country=None,
            dimension_values=[
                "COUNTRY:USA",
                "FREQ:A",
                "UNIT:USD",
                "FOO:BAR",
                "noColonHere",
            ],
        )
        assert q.country == "USA"
        assert q.frequency == "A"
        assert q.transform == "USD"
        assert q.dimension_values == ["FOO:BAR", "noColonHere"]

    def test_missing_country_in_dim_values_raises(self, monkeypatch):
        """If no country can be inferred, the validator raises (covers 268)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(ValueError, match="Country is required"):
            ImfEconomicIndicatorsQueryParams(
                symbol="WEO::NGDP_RPCH",
                country=None,
                dimension_values=["FOO:BAR"],
            )

    def test_unknown_dimension_id_raises(self, monkeypatch):
        """An unknown dim id surfaces a clear error listing the valid extras."""
        stub = _StubMetadata(
            dataflows={
                "CTOT": {
                    "id": "CTOT",
                    "structureRef": {"id": "DSD_CTOT"},
                }
            },
            datastructures={
                "DSD_CTOT": {
                    "dimensions": [
                        {"id": "COUNTRY", "position": "0"},
                        {"id": "INDICATOR", "position": "1"},
                        {"id": "WGT_TYPE", "position": "2"},
                        {"id": "FREQUENCY", "position": "3"},
                    ]
                }
            },
        )
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(
            ValueError,
            match=(
                r"Unknown dimension 'UNIT_MEASUREMENT' for dataflow 'CTOT'\. "
                r"Valid extra dimensions: WGT_TYPE\."
            ),
        ):
            ImfEconomicIndicatorsQueryParams(
                symbol="CTOT::CEPI_CTOTX_GDP",
                country="AUS",
                dimension_values=["UNIT_MEASUREMENT:FWI"],
            )

    def test_known_extra_dimension_accepted(self, monkeypatch):
        """A real extra dim (``WGT_TYPE``) passes through to ``dimension_values``."""
        stub = _StubMetadata(
            dataflows={
                "CTOT": {
                    "id": "CTOT",
                    "structureRef": {"id": "DSD_CTOT"},
                }
            },
            datastructures={
                "DSD_CTOT": {
                    "dimensions": [
                        {"id": "COUNTRY", "position": "0"},
                        {"id": "INDICATOR", "position": "1"},
                        {"id": "WGT_TYPE", "position": "2"},
                        {"id": "FREQUENCY", "position": "3"},
                    ]
                }
            },
        )
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(
            symbol="CTOT::CEPI_CTOTX_GDP",
            country="AUS",
            dimension_values=["WGT_TYPE:FWI"],
        )
        assert q.dimension_values == ["WGT_TYPE:FWI"]

    def test_dim_validation_skips_entries_without_colon(self, monkeypatch):
        """A ``dimension_values`` token without ``:`` is silently kept."""
        stub = _StubMetadata(
            dataflows={"CTOT": {"id": "CTOT", "structureRef": {"id": "DSD_CTOT"}}},
            datastructures={
                "DSD_CTOT": {
                    "dimensions": [
                        {"id": "COUNTRY", "position": "0"},
                        {"id": "INDICATOR", "position": "1"},
                        {"id": "WGT_TYPE", "position": "2"},
                    ]
                }
            },
        )
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(
            symbol="CTOT::CEPI_CTOTX_GDP",
            country="AUS",
            dimension_values=["WGT_TYPE:FWI", "noColonHere"],
        )
        assert q.dimension_values == ["WGT_TYPE:FWI", "noColonHere"]

    def test_invalid_symbol_format_raises(self, monkeypatch):
        """Missing ``::`` raises (covers line 280)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(ValueError, match="Expected 'dataflow::identifier'"):
            ImfEconomicIndicatorsQueryParams(symbol="WEONGDPRPCH", country="USA")

    def test_empty_identifier_raises(self, monkeypatch):
        """An empty identifier raises (covers line 290)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(ValueError, match="Identifier cannot be empty"):
            ImfEconomicIndicatorsQueryParams(symbol="WEO::", country="USA")

    def test_h_prefix_marks_table(self, monkeypatch):
        """Identifiers starting with ``H_`` are treated as tables (covers 299, 326-330)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(
            symbol="BOP::H_BOP_AGG_STANDARD_PRESENTATION", country="USA"
        )
        assert q._is_table is True
        assert q._dataflow == "BOP"
        assert q._table_id == "H_BOP_AGG_STANDARD_PRESENTATION"

    def test_hierarchy_match_marks_table(self, monkeypatch):
        """An identifier that matches a hierarchy id is treated as a table (covers 306-308)."""
        stub = _StubMetadata(
            hierarchies={"BOP": [{"id": "MY_TABLE"}]},
        )
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(symbol="BOP::MY_TABLE", country="USA")
        assert q._is_table is True
        assert q._table_id == "MY_TABLE"

    def test_hierarchy_lookup_exception_is_swallowed(self, monkeypatch):
        """A hierarchy lookup that raises falls through to indicator mode (covers 307-308)."""

        def boom(self, dataflow_id):  # noqa
            raise RuntimeError("oops")

        stub = _StubMetadata(
            dataflows={"WEO": {"id": "WEO", "agencyID": "IMF"}},
        )
        monkeypatch.setattr(
            _StubMetadata, "get_dataflow_hierarchies", boom, raising=False
        )
        _patch_metadata(monkeypatch, stub)
        _patch_detect_transform_dimension(monkeypatch)
        q = ImfEconomicIndicatorsQueryParams(symbol="WEO::NGDP_RPCH", country="USA")
        assert q._is_table is False

    def test_mixing_tables_and_indicators_raises(self, monkeypatch):
        """Mixing tables and indicators raises ``ValueError`` (covers 315-318)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(ValueError, match="Cannot mix tables and indicators"):
            ImfEconomicIndicatorsQueryParams(
                symbol="BOP::H_TABLE,WEO::NGDP_RPCH", country="USA"
            )

    def test_more_than_one_table_raises(self, monkeypatch):
        """More than one table raises (covers line 322-324)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(ValueError, match="Only one table"):
            ImfEconomicIndicatorsQueryParams(symbol="BOP::H_A,BOP::H_B", country="USA")

    def test_multiple_dataflows_indicator_mode_clears_codes(self, monkeypatch):
        """Two dataflows leave ``_dataflow=None`` and ``_indicator_codes=[]`` (covers 347-348)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        q = ImfEconomicIndicatorsQueryParams(
            symbol="WEO::NGDP_RPCH,IFS::FOO", country="USA"
        )
        assert q._dataflow is None
        assert q._indicator_codes == []


class TestValidateIndicatorParams:
    """Tests for ``_validate_indicator_params`` constraint enforcement."""

    @staticmethod
    def _stub_with_dataflow() -> _StubMetadata:
        """Build a ``_StubMetadata`` that exposes a ``WEO`` dataflow + DSD."""
        return _StubMetadata(
            dataflows={
                "WEO": {
                    "id": "WEO",
                    "agencyID": "IMF",
                    "structureRef": {"id": "DSD_WEO"},
                }
            },
            datastructures={
                "DSD_WEO": {
                    "dimensions": [
                        {"id": "COUNTRY", "position": "0"},
                        {"id": "INDICATOR", "position": "1"},
                        {"id": "FREQUENCY", "position": "2"},
                    ]
                }
            },
        )

    def test_no_dataflow_object_is_skipped(self, monkeypatch):
        """Dataflows that aren't in ``metadata.dataflows`` are skipped (covers lines 411-412)."""
        stub = _StubMetadata()  # empty dataflows
        _patch_metadata(monkeypatch, stub)
        ImfEconomicIndicatorsQueryParams(symbol="WEO::NGDP_RPCH", country="USA")

    def test_invalid_country_raises(self, monkeypatch):
        """An invalid country code raises ``ValueError`` (covers 444-458)."""
        stub = self._stub_with_dataflow()
        stub._constraints[("WEO", "COUNTRY")] = {
            "key_values": [{"id": "COUNTRY", "values": ["USA", "JPN"]}]
        }
        _patch_metadata(monkeypatch, stub)
        _patch_detect_transform_dimension(monkeypatch)
        with pytest.raises(
            ValueError, match="Invalid value\\(s\\) for dimension 'country'"
        ):
            ImfEconomicIndicatorsQueryParams(symbol="WEO::NGDP_RPCH", country="ZZZ")

    def test_invalid_frequency_raises(self, monkeypatch):
        """An invalid frequency raises ``ValueError`` (covers 460-475)."""
        stub = self._stub_with_dataflow()
        stub._constraints[("WEO", "FREQUENCY")] = {
            "key_values": [{"id": "FREQUENCY", "values": ["A"]}]
        }
        _patch_metadata(monkeypatch, stub)
        _patch_detect_transform_dimension(monkeypatch)
        with pytest.raises(ValueError, match="frequency"):
            ImfEconomicIndicatorsQueryParams(
                symbol="WEO::NGDP_RPCH",
                country="USA",
                frequency="quarter",
            )

    def test_invalid_transform_raises(self, monkeypatch):
        """An invalid transform raises ``ValueError`` (covers 477-498)."""
        stub = _StubMetadata(
            dataflows={
                "BOP_AGG": {
                    "id": "BOP_AGG",
                    "agencyID": "IMF",
                    "structureRef": {"id": "DSD_BOP_AGG"},
                }
            },
            datastructures={
                "DSD_BOP_AGG": {
                    "dimensions": [
                        {"id": "COUNTRY", "position": "0"},
                        {"id": "INDICATOR", "position": "1"},
                        {"id": "FREQUENCY", "position": "2"},
                        {"id": "TYPE_OF_TRANSFORMATION", "position": "3"},
                    ]
                }
            },
            constraints={
                ("BOP_AGG", "TYPE_OF_TRANSFORMATION"): {
                    "key_values": [{"id": "TYPE_OF_TRANSFORMATION", "values": ["IX"]}]
                }
            },
        )
        _patch_metadata(monkeypatch, stub)
        _patch_detect_transform_dimension(
            monkeypatch,
            transform_dim="TYPE_OF_TRANSFORMATION",
            transform_lookup={"yoy": "YOY_PCH"},
        )
        with pytest.raises(ValueError, match="transform"):
            ImfEconomicIndicatorsQueryParams(
                symbol="BOP_AGG::GS_CD",
                country="USA",
                transform="yoy",
            )

    def test_build_key_default_star_branch(self, monkeypatch):
        """An unknown dim type defaults to ``*`` in the key (covers line 392)."""
        stub = _StubMetadata(
            dataflows={
                "WEO": {
                    "id": "WEO",
                    "agencyID": "IMF",
                    "structureRef": {"id": "DSD_WEO"},
                }
            },
            datastructures={
                "DSD_WEO": {
                    "dimensions": [
                        {"id": "EXTRA", "position": "0"},
                        {"id": "COUNTRY", "position": "1"},
                        {"id": "INDICATOR", "position": "2"},
                        {"id": "FREQUENCY", "position": "3"},
                    ]
                }
            },
            constraints={
                ("WEO", "COUNTRY"): {
                    "key_values": [{"id": "COUNTRY", "values": ["USA"]}]
                }
            },
        )
        _patch_metadata(monkeypatch, stub)
        _patch_detect_transform_dimension(monkeypatch)
        ImfEconomicIndicatorsQueryParams(symbol="WEO::NGDP_RPCH", country="USA")
        keys = [c["key"] for c in stub.constraints_calls]
        # The EXTRA dim slot becomes "*" via the default branch (line 392).
        assert any(k.startswith("*") for k in keys)

    def test_freq_dim_build_key_branch(self, monkeypatch):
        """The constraint key includes resolved freq/transform parts (covers 381-388, 390)."""
        stub = _StubMetadata(
            dataflows={
                "BOP_AGG": {
                    "id": "BOP_AGG",
                    "agencyID": "IMF",
                    "structureRef": {"id": "DSD_BOP_AGG"},
                }
            },
            datastructures={
                "DSD_BOP_AGG": {
                    "dimensions": [
                        {"id": "FREQUENCY", "position": "0"},
                        {"id": "TYPE_OF_TRANSFORMATION", "position": "1"},
                        {"id": "INDICATOR", "position": "2"},
                        {"id": "COUNTRY", "position": "3"},
                    ]
                }
            },
        )
        _patch_metadata(monkeypatch, stub)
        _patch_detect_transform_dimension(
            monkeypatch,
            transform_dim="TYPE_OF_TRANSFORMATION",
            transform_lookup={"yoy": "YOY_PCH"},
        )
        ImfEconomicIndicatorsQueryParams(
            symbol="BOP_AGG::GS_CD",
            country="USA",
            frequency="quarter",
            transform="yoy",
        )
        keys = [c["key"] for c in stub.constraints_calls]
        assert any("Q" in k for k in keys)
        # Building constraint key for the country target visits transform_dim → captures "yoy".
        assert any("yoy" in k for k in keys)


class TestImfEconomicIndicatorsFetcherTransformQuery:
    """Tests for ``transform_query`` exception handling."""

    def test_transform_query_wraps_exception(self, monkeypatch):
        """Any pydantic error is wrapped in ``OpenBBError`` (covers 603-604)."""
        stub = _StubMetadata()
        _patch_metadata(monkeypatch, stub)
        with pytest.raises(OpenBBError):
            ImfEconomicIndicatorsFetcher.transform_query({"symbol": None})


class _StubQueryBuilder:
    """Minimal ``ImfQueryBuilder`` substitute capturing args."""

    instances: list = []
    shared_payload: dict[str, Any] | None = None
    shared_raise: Exception | None = None

    def __init__(self):
        self.metadata: Any = None
        self.calls: list[dict[str, Any]] = []
        _StubQueryBuilder.instances.append(self)

    def fetch_data(self, **kwargs: Any) -> dict[str, Any]:
        """Return preconfigured payload or raise."""
        self.calls.append(kwargs)
        if _StubQueryBuilder.shared_raise is not None:
            raise _StubQueryBuilder.shared_raise
        return _StubQueryBuilder.shared_payload or {"data": [], "metadata": {}}


class _StubTableBuilder:
    """Minimal ``ImfTableBuilder`` substitute capturing args."""

    instances: list = []
    shared_payload: dict[str, Any] | None = None
    shared_raise: Exception | None = None

    def __init__(self):
        self.calls: list[dict[str, Any]] = []
        _StubTableBuilder.instances.append(self)

    def get_table(self, **kwargs: Any) -> dict[str, Any]:
        """Return preconfigured payload or raise."""
        self.calls.append(kwargs)
        if _StubTableBuilder.shared_raise is not None:
            raise _StubTableBuilder.shared_raise
        return _StubTableBuilder.shared_payload or {
            "data": [],
            "table_metadata": {},
            "series_metadata": {},
        }


@pytest.fixture
def patched_builders(monkeypatch: pytest.MonkeyPatch):
    """Swap in stub query/table builders for the model module."""
    _StubQueryBuilder.instances = []
    _StubQueryBuilder.shared_payload = None
    _StubQueryBuilder.shared_raise = None
    _StubTableBuilder.instances = []
    _StubTableBuilder.shared_payload = None
    _StubTableBuilder.shared_raise = None
    monkeypatch.setattr(
        "openbb_imf.utils.query_builder.ImfQueryBuilder",
        _StubQueryBuilder,
    )
    monkeypatch.setattr(
        "openbb_imf.utils.table_builder.ImfTableBuilder",
        _StubTableBuilder,
    )
    return _StubQueryBuilder, _StubTableBuilder


class TestImfEconomicIndicatorsFetcherAextractData:
    """Tests for ``aextract_data`` branches."""

    @pytest.mark.asyncio
    async def test_table_mode_basic(self, monkeypatch, patched_builders):
        """Table-mode dispatch returns table-shaped payload (covers happy path of 637-739)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "BOP::H_AGG", "country": "USA"}
        )
        _, _ = patched_builders
        out = await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        assert out["mode"] == "table"
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["TYPE_OF_TRANSFORMATION"] == "*"
        assert captured["dataflow"] == "BOP"

    @pytest.mark.asyncio
    async def test_table_mode_gfs_branch(self, monkeypatch, patched_builders):
        """GFS dataflows set SECTOR/GFS_GRP defaults (covers line 647-649)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "GFS_R::H_T1", "country": "USA"}
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["SECTOR"] == "*"
        assert captured["GFS_GRP"] == "*"

    @pytest.mark.asyncio
    async def test_table_mode_fsic_branch(self, monkeypatch, patched_builders):
        """FSIC/IRFCL set the ``SECTOR`` default (covers 650-651)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "FSIC::H_T1", "country": "USA"}
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["SECTOR"] == "*"

    @pytest.mark.asyncio
    async def test_table_mode_isora_branch(self, monkeypatch, patched_builders):
        """ISORA_LATEST_DATA_PUB sets the ``INDICATOR`` default (covers 654-655)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "ISORA_LATEST_DATA_PUB::H_T1", "country": "USA"}
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["INDICATOR"] == "*"

    @pytest.mark.asyncio
    async def test_aextract_skips_non_string_dimension_values(
        self, monkeypatch, patched_builders
    ):
        """Non-string entries in ``dimension_values`` are skipped (covers line 628)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "BOP::H_AGG", "country": "USA"}
        )
        object.__setattr__(q, "dimension_values", [None, 42, "FOO:bar"])
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["FOO"] == "BAR"

    @pytest.mark.asyncio
    async def test_table_mode_extra_dimensions(self, monkeypatch, patched_builders):
        """``dimension_values`` are merged into the query params (covers 626-633, 657-658)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "BOP::H_AGG",
                "country": "USA",
                "dimension_values": ["FOO:bar"],
            }
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["FOO"] == "BAR"

    @pytest.mark.asyncio
    async def test_table_mode_transform_resolved_via_transform_lookup(
        self, monkeypatch, patched_builders
    ):
        """A friendly transform name routes through ``transform_lookup`` (covers 668-675)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(
            monkeypatch,
            transform_dim="TYPE_OF_TRANSFORMATION",
            transform_lookup={"yoy": "YOY_PCH"},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "BOP::H_AGG",
                "country": "USA",
                "transform": "yoy",
            }
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["TYPE_OF_TRANSFORMATION"] == "YOY_PCH"

    @pytest.mark.asyncio
    async def test_table_mode_transform_all_wildcard(
        self, monkeypatch, patched_builders
    ):
        """``transform='all'`` is converted to ``*`` (covers 669-671)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(
            monkeypatch, transform_dim="TYPE_OF_TRANSFORMATION"
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "BOP::H_AGG",
                "country": "USA",
                "transform": "all",
            }
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["TYPE_OF_TRANSFORMATION"] == "*"

    @pytest.mark.asyncio
    async def test_table_mode_transform_via_unit_dim(
        self, monkeypatch, patched_builders
    ):
        """``transform`` falling back to ``unit_dim`` resolves via ``unit_lookup`` (covers 677-684)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(
            monkeypatch,
            unit_dim="UNIT",
            unit_lookup={"usd": "USD"},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "IFS::IND",
                "country": "USA",
                "transform": "usd",
            }
        )
        # Force into table mode without H_ prefix.
        object.__setattr__(q, "_is_table", True)
        object.__setattr__(q, "_dataflow", "IFS")
        object.__setattr__(q, "_table_id", "T1")
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["UNIT"] == "USD"

    @pytest.mark.asyncio
    async def test_table_mode_transform_via_unit_dim_wildcard(
        self, monkeypatch, patched_builders
    ):
        """``transform='*'`` with a unit dim sets ``UNIT='*'`` (covers 678-680)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(monkeypatch, unit_dim="UNIT")
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "IFS::IND",
                "country": "USA",
                "transform": "*",
            }
        )
        object.__setattr__(q, "_is_table", True)
        object.__setattr__(q, "_dataflow", "IFS")
        object.__setattr__(q, "_table_id", "T1")
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["UNIT"] == "*"

    @pytest.mark.asyncio
    async def test_table_mode_transform_unrecognized_raises(
        self, monkeypatch, patched_builders
    ):
        """An unknown transform with neither dim raises (covers 686-706)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(monkeypatch)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "BOP::H_AGG",
                "country": "USA",
                "transform": "weird",
            }
        )
        with pytest.raises(OpenBBError, match="does not support transform"):
            await ImfEconomicIndicatorsFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_table_mode_transform_invalid_with_available(
        self, monkeypatch, patched_builders
    ):
        """An invalid value when options exist surfaces available choices (covers 686-706)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(
            monkeypatch,
            transform_dim="TYPE_OF_TRANSFORMATION",
            transform_lookup={"yoy": "YOY", "yoy_lc": "yoy_lc"},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "BOP::H_AGG",
                "country": "USA",
                "transform": "weird",
            }
        )
        with pytest.raises(OpenBBError, match="Invalid transform value"):
            await ImfEconomicIndicatorsFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_table_mode_transform_invalid_only_unit_lookup(
        self, monkeypatch, patched_builders
    ):
        """The unit_lookup branch of the error message is taken (covers line 696)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(
            monkeypatch,
            unit_dim="UNIT",
            unit_lookup={"usd": "USD"},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "BOP::H_AGG",
                "country": "USA",
                "transform": "weird",
            }
        )
        with pytest.raises(OpenBBError, match="Invalid transform value"):
            await ImfEconomicIndicatorsFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_table_mode_limit_with_annual_frequency(
        self, monkeypatch, patched_builders
    ):
        """``limit`` without a ``start_date`` derives a year boundary (covers 708-720)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "BOP::H_AGG",
                "country": "USA",
                "frequency": "annual",
                "limit": 5,
            }
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["start_date"] is not None
        assert len(captured["start_date"]) == 4

    @pytest.mark.asyncio
    async def test_table_mode_limit_with_quarterly_frequency(
        self, monkeypatch, patched_builders
    ):
        """``limit`` with ``quarter`` frequency derives ``start_date`` via 713-716."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "BOP::H_AGG",
                "country": "USA",
                "frequency": "quarter",
                "limit": 5,
            }
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["start_date"] is not None

    @pytest.mark.asyncio
    async def test_table_mode_limit_with_monthly_frequency(
        self, monkeypatch, patched_builders
    ):
        """``limit`` with ``month`` frequency derives ``start_date`` via 717-720."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "BOP::H_AGG",
                "country": "USA",
                "frequency": "month",
                "limit": 5,
            }
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubTableBuilder.instances[0].calls[0]
        assert captured["start_date"] is not None

    @pytest.mark.asyncio
    async def test_table_mode_get_table_value_error_translates(
        self, monkeypatch, patched_builders
    ):
        """A ``ValueError`` from ``get_table`` is wrapped in ``OpenBBError`` (covers 738-739)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "BOP::H_AGG", "country": "USA"}
        )

        def boom(self, **kwargs):
            raise ValueError("table boom")

        monkeypatch.setattr(_StubTableBuilder, "get_table", boom)
        with pytest.raises(OpenBBError):
            await ImfEconomicIndicatorsFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_table_mode_missing_dataflow_raises(
        self, monkeypatch, patched_builders
    ):
        """Table mode with no ``_dataflow`` raises ``OpenBBError`` (covers 639-640)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "BOP::H_AGG", "country": "USA"}
        )
        object.__setattr__(q, "_dataflow", None)
        with pytest.raises(OpenBBError, match="Could not determine dataflow"):
            await ImfEconomicIndicatorsFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_indicator_mode_no_indicators_raises(
        self, monkeypatch, patched_builders
    ):
        """An empty ``_indicators_by_dataflow`` raises (covers line 748)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "WEO::NGDP_RPCH", "country": "USA"}
        )
        object.__setattr__(q, "_is_table", False)
        object.__setattr__(q, "_indicators_by_dataflow", {})
        with pytest.raises(OpenBBError, match="No indicators specified"):
            await ImfEconomicIndicatorsFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_indicator_mode_full_path(self, monkeypatch, patched_builders):
        """Indicator mode happy path exercises transform/limit/dimension_codes paths."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(
            monkeypatch,
            transform_dim="TYPE_OF_TRANSFORMATION",
            transform_lookup={"yoy": "YOY"},
        )
        monkeypatch.setattr(
            "openbb_imf.models.economic_indicators.detect_indicator_dimensions",
            lambda dataflow, codes, meta: {"INDICATOR": codes},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "WEO::NGDP_RPCH",
                "country": "USA",
                "transform": "yoy",
                "limit": 3,
                "dimension_values": ["EXTRA:val"],
            }
        )
        _StubQueryBuilder.shared_payload = {
            "data": [{"OBS_VALUE": 1.0}],
            "metadata": {"foo": "bar"},
        }
        out = await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        assert out["mode"] == "indicator"
        captured = _StubQueryBuilder.instances[0].calls[0]
        assert captured["lastNObservations"] == 3
        assert captured["EXTRA"] == "VAL"
        assert captured["INDICATOR"] == "NGDP_RPCH"
        assert captured["TYPE_OF_TRANSFORMATION"] == "YOY"

    @pytest.mark.asyncio
    async def test_indicator_mode_transform_wildcard_for_transform_dim(
        self, monkeypatch, patched_builders
    ):
        """``transform='*'`` with transform_dim sets ``*`` (covers 768-770)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(
            monkeypatch, transform_dim="TYPE_OF_TRANSFORMATION"
        )
        monkeypatch.setattr(
            "openbb_imf.models.economic_indicators.detect_indicator_dimensions",
            lambda *a, **kw: {"INDICATOR": ["NGDP_RPCH"]},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "WEO::NGDP_RPCH", "country": "USA", "transform": "*"}
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubQueryBuilder.instances[0].calls[0]
        assert captured["TYPE_OF_TRANSFORMATION"] == "*"

    @pytest.mark.asyncio
    async def test_indicator_mode_transform_unit_dim_lookup(
        self, monkeypatch, patched_builders
    ):
        """``unit_dim`` matches a unit_lookup entry (covers 776-783)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(
            monkeypatch,
            unit_dim="UNIT",
            unit_lookup={"usd": "USD"},
        )
        monkeypatch.setattr(
            "openbb_imf.models.economic_indicators.detect_indicator_dimensions",
            lambda *a, **kw: {"INDICATOR": ["NGDP_RPCH"]},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "WEO::NGDP_RPCH", "country": "USA", "transform": "usd"}
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubQueryBuilder.instances[0].calls[0]
        assert captured["UNIT"] == "USD"

    @pytest.mark.asyncio
    async def test_indicator_mode_transform_unit_dim_wildcard(
        self, monkeypatch, patched_builders
    ):
        """``unit_dim`` wildcard branch is reached (covers 777-780)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(monkeypatch, unit_dim="UNIT")
        monkeypatch.setattr(
            "openbb_imf.models.economic_indicators.detect_indicator_dimensions",
            lambda *a, **kw: {"INDICATOR": ["NGDP_RPCH"]},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "WEO::NGDP_RPCH", "country": "USA", "transform": "*"}
        )
        await ImfEconomicIndicatorsFetcher.aextract_data(q, None)
        captured = _StubQueryBuilder.instances[0].calls[0]
        assert captured["UNIT"] == "*"

    @pytest.mark.asyncio
    async def test_indicator_mode_transform_unrecognized_dataflow_raises(
        self, monkeypatch, patched_builders
    ):
        """Unrecognized transform on a dataflow without dims raises (covers 800-807)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(monkeypatch)
        monkeypatch.setattr(
            "openbb_imf.models.economic_indicators.detect_indicator_dimensions",
            lambda *a, **kw: {"INDICATOR": ["NGDP_RPCH"]},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "WEO::NGDP_RPCH", "country": "USA", "transform": "weird"}
        )
        with pytest.raises(OpenBBError):
            await ImfEconomicIndicatorsFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_indicator_mode_transform_unrecognized_with_lookups(
        self, monkeypatch, patched_builders
    ):
        """Unknown transform with options raises with available list (covers 804-807)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        _patch_detect_transform_dimension(
            monkeypatch,
            transform_dim="TYPE_OF_TRANSFORMATION",
            transform_lookup={"yoy": "YOY"},
            unit_dim="UNIT",
            unit_lookup={"usd": "USD"},
        )
        monkeypatch.setattr(
            "openbb_imf.models.economic_indicators.detect_indicator_dimensions",
            lambda *a, **kw: {"INDICATOR": ["NGDP_RPCH"]},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "WEO::NGDP_RPCH", "country": "USA", "transform": "weird"}
        )
        with pytest.raises(OpenBBError, match="Invalid transform"):
            await ImfEconomicIndicatorsFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_indicator_mode_query_builder_value_error_translates(
        self, monkeypatch, patched_builders
    ):
        """A ``ValueError`` from ``fetch_data`` is wrapped in ``OpenBBError`` (covers 830-831)."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        monkeypatch.setattr(
            "openbb_imf.models.economic_indicators.detect_indicator_dimensions",
            lambda *a, **kw: {"INDICATOR": ["NGDP_RPCH"]},
        )
        q = ImfEconomicIndicatorsFetcher.transform_query(
            {"symbol": "WEO::NGDP_RPCH", "country": "USA"}
        )

        def boom(self, **kwargs):
            raise ValueError("translate me")

        monkeypatch.setattr(_StubQueryBuilder, "fetch_data", boom)
        with pytest.raises(OpenBBError):
            await ImfEconomicIndicatorsFetcher.aextract_data(q, None)


class TestImfEconomicIndicatorsFetcherTransformData:
    """Tests for ``transform_data`` branches."""

    def _query(self, monkeypatch, **overrides: Any) -> ImfEconomicIndicatorsQueryParams:
        """Build a query bypassing constraint validation."""
        stub_meta = _StubMetadata()
        _patch_metadata(monkeypatch, stub_meta)
        params: dict[str, Any] = {"symbol": "WEO::NGDP_RPCH", "country": "USA"}
        params.update(overrides)
        return ImfEconomicIndicatorsFetcher.transform_query(params)

    def test_empty_payload_raises(self, monkeypatch):
        """An empty ``data`` raises ``EmptyDataError`` (covers line 850)."""
        q = self._query(monkeypatch)
        with pytest.raises(EmptyDataError):
            ImfEconomicIndicatorsFetcher.transform_data(q, {"data": []})

    def test_table_mode_metadata_routing(self, monkeypatch):
        """Table mode pulls table_metadata/series_metadata (covers lines 855-859)."""
        q = self._query(monkeypatch)
        rows = [
            {
                "TIME_PERIOD": "2024-01-01",
                "OBS_VALUE": 1.0,
                "COUNTRY": "United States",
                "country_code": "USA",
            }
        ]
        result = ImfEconomicIndicatorsFetcher.transform_data(
            q,
            {
                "mode": "table",
                "data": rows,
                "table_metadata": {"foo": 1},
                "series_metadata": {"bar": 2},
            },
        )
        assert result.metadata == {"table": {"foo": 1}, "series": {"bar": 2}}

    def test_start_and_end_date_filter(self, monkeypatch):
        """``start_date`` and ``end_date`` skip rows (covers lines 874, 880)."""
        q = self._query(
            monkeypatch, start_date=date(2024, 2, 1), end_date=date(2024, 4, 1)
        )
        rows = [
            {"TIME_PERIOD": "2024-01-01", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2024-03-01", "OBS_VALUE": 2.0},
            {"TIME_PERIOD": "2024-05-01", "OBS_VALUE": 3.0},
        ]
        result = ImfEconomicIndicatorsFetcher.transform_data(
            q, {"data": rows, "metadata": {}}
        )
        assert len(result.result) == 1
        assert result.result[0].value == 2.0

    def test_all_rows_filtered_raises(self, monkeypatch):
        """All rows being filtered raises ``EmptyDataError`` (covers 973-977)."""
        q = self._query(monkeypatch, start_date=date(2024, 12, 1))
        rows = [{"TIME_PERIOD": "2024-01-01", "OBS_VALUE": 1.0}]
        with pytest.raises(EmptyDataError, match="No data remaining"):
            ImfEconomicIndicatorsFetcher.transform_data(
                q, {"data": rows, "metadata": {}}
            )

    def test_row_without_date_is_skipped(self, monkeypatch):
        """Rows without a ``date`` are dropped (covers line 998)."""
        q = self._query(monkeypatch)
        rows = [
            {"TIME_PERIOD": "2024-01-01", "OBS_VALUE": 1.0},
            {"OBS_VALUE": 2.0},
        ]
        result = ImfEconomicIndicatorsFetcher.transform_data(
            q, {"data": rows, "metadata": {}}
        )
        # Only the dated row survives.
        assert len(result.result) == 1

    def test_value_falls_back_to_value_field(self, monkeypatch):
        """Missing ``OBS_VALUE`` falls back to ``value`` (covers line 907)."""
        q = self._query(monkeypatch)
        rows = [{"TIME_PERIOD": "2024-01-01", "value": 7.0}]
        result = ImfEconomicIndicatorsFetcher.transform_data(
            q, {"data": rows, "metadata": {}}
        )
        assert result.result[0].value == 7.0

    def test_nan_scale_and_unit_are_normalised(self, monkeypatch):
        """``nan`` scale/unit become ``None`` (covers 911-914 and 922-925)."""
        q = self._query(monkeypatch)
        rows = [
            {
                "TIME_PERIOD": "2024-01-01",
                "OBS_VALUE": 1.0,
                "SCALE": "nan",
                "UNIT": "nan",
            }
        ]
        result = ImfEconomicIndicatorsFetcher.transform_data(
            q, {"data": rows, "metadata": {}}
        )
        assert result.result[0].scale is None
        assert result.result[0].unit is None

    def test_non_string_scale_and_unit_are_stringified(self, monkeypatch):
        """Numeric scale/unit values are coerced to strings (covers 913-914, 924-925)."""
        q = self._query(monkeypatch)
        rows = [
            {
                "TIME_PERIOD": "2024-01-01",
                "OBS_VALUE": 1.0,
                "scale": 1.5,
                "unit": 9,
            }
        ]
        result = ImfEconomicIndicatorsFetcher.transform_data(
            q, {"data": rows, "metadata": {}}
        )
        assert result.result[0].scale == "1.5"
        assert result.result[0].unit == "9"

    def test_pivot_path_exercises_pivot_table_data(self, monkeypatch):
        """``pivot=True`` builds a DataFrame via ``pivot_table_data`` (covers 1009-1019)."""
        q = self._query(monkeypatch, pivot=True)
        rows = [
            {
                "TIME_PERIOD": "2024-01-01",
                "OBS_VALUE": 1.0,
                "COUNTRY": "United States",
                "country_code": "USA",
                "INDICATOR": "NGDP_RPCH",
                "series_id": "WEO::NGDP_RPCH",
            }
        ]

        class _FakeDF:
            def fillna(self, _):
                return self

            def reset_index(self):
                return self

            def to_dict(self, orient: str):  # noqa: ARG002
                return [
                    {
                        "date": "2024-01-01",
                        "country": "United States",
                        "country_code": "USA",
                        "value": 1.0,
                        "symbol": "WEO::NGDP_RPCH",
                    }
                ]

        with patch(
            "openbb_imf.utils.table_presentation.pivot_table_data",
            return_value=_FakeDF(),
        ):
            out = ImfEconomicIndicatorsFetcher.transform_data(
                q, {"data": rows, "metadata": {}}
            )
        assert isinstance(out.result[0], ImfEconomicIndicatorsData)
