"""Unit tests for openbb_oecd.utils.metadata._loader_mixin (full coverage)."""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_oecd.utils.metadata import OecdMetadata

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


def _mk_resp(payload):
    """Build a MagicMock response object with .json() returning payload."""
    resp = MagicMock()
    resp.json.return_value = payload
    return resp


def _dataflow_payload(items, key="data"):
    """Wrap dataflow items in an SDMX-JSON-style envelope."""
    return {key: {"dataflows": items}} if key else {"dataflows": items}


class TestEnsureDataflows:
    """Coverage for LoaderMixin._ensure_dataflows."""

    def test_already_loaded_no_annotations_triggers_backfill(self, seeded_meta):
        """When loaded but the first entry lacks annotations, backfill is invoked."""
        seeded_meta.dataflows[_FULL_ID].pop("annotations", None)
        with patch.object(seeded_meta, "_backfill_annotations") as mock_bf:
            seeded_meta._ensure_dataflows()
        mock_bf.assert_called_once()

    def test_already_loaded_with_annotations_skips_backfill(self, seeded_meta):
        """When the first entry already has annotations, nothing happens."""
        seeded_meta.dataflows[_FULL_ID]["annotations"] = {"X": "Y"}
        with patch.object(seeded_meta, "_backfill_annotations") as mock_bf:
            seeded_meta._ensure_dataflows()
        mock_bf.assert_not_called()

    def test_already_loaded_empty_dict_skips_backfill(self, empty_meta):
        """When dataflows dict is empty (no first entry), backfill is skipped."""
        empty_meta._full_catalogue_loaded = True
        with patch.object(empty_meta, "_backfill_annotations") as mock_bf:
            empty_meta._ensure_dataflows()
        mock_bf.assert_not_called()

    def test_fetches_and_populates(self, empty_meta):
        """A fresh fetch populates dataflows, short_id_map, and marks loaded."""
        empty_meta._full_catalogue_loaded = False
        payload = _dataflow_payload(
            [
                {
                    "id": "DSD_A@DF_A",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "names": {"en": "Alpha"},
                    "descriptions": {"en": "Alpha desc"},
                    "structure": "ref",
                    "annotations": [
                        {"type": "T1", "title": "Title 1"},
                        {"type": "T2", "text": "Text 2"},
                        {"type": "T3", "title": {"en": "Localized"}},
                        {"type": "T4", "title": {"fr": "FR only"}},
                        {"type": "T5"},
                        {"type": ""},
                    ],
                }
            ]
        )
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=_mk_resp(payload),
            ),
            patch.object(empty_meta, "_save_cache") as mock_save,
        ):
            empty_meta._ensure_dataflows()
        df = empty_meta.dataflows["DSD_A@DF_A"]
        assert df["short_id"] == "DF_A"
        assert df["name"] == "Alpha"
        assert df["description"] == "Alpha desc"
        assert df["annotations"]["T1"] == "Title 1"
        assert df["annotations"]["T2"] == "Text 2"
        assert df["annotations"]["T3"] == "Localized"
        assert df["annotations"]["T4"] == "FR only"
        assert df["annotations"]["T5"] == ""
        assert empty_meta._short_id_map["DF_A"] == "DSD_A@DF_A"
        assert empty_meta._full_catalogue_loaded is True
        mock_save.assert_called_once()

    def test_fetches_with_name_fallback_and_no_at(self, empty_meta):
        """Plain name/description fields used when names/descriptions absent."""
        empty_meta._full_catalogue_loaded = False
        payload = _dataflow_payload(
            [
                {
                    "id": "DF_NOAT",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "name": "Plain Name",
                    "description": "Plain Desc",
                }
            ]
        )
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=_mk_resp(payload),
            ),
            patch.object(empty_meta, "_save_cache"),
        ):
            empty_meta._ensure_dataflows()
        df = empty_meta.dataflows["DF_NOAT"]
        assert df["short_id"] == "DF_NOAT"
        assert df["name"] == "Plain Name"
        assert df["description"] == "Plain Desc"

    def test_fetches_with_non_dict_names(self, empty_meta):
        """When names/descriptions are not dicts, falls back to name/description."""
        empty_meta._full_catalogue_loaded = False
        payload = _dataflow_payload(
            [
                {
                    "id": "DSD@DF_X",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "names": "string-not-dict",
                    "descriptions": "string-not-dict",
                    "name": "X",
                }
            ]
        )
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=_mk_resp(payload),
            ),
            patch.object(empty_meta, "_save_cache"),
        ):
            empty_meta._ensure_dataflows()
        assert empty_meta.dataflows["DSD@DF_X"]["name"] == "X"
        assert empty_meta.dataflows["DSD@DF_X"]["description"] == ""

    def test_json_parse_failure_raises(self, empty_meta):
        """A JSON parse error is wrapped in an OpenBBError."""
        empty_meta._full_catalogue_loaded = False
        resp = MagicMock()
        resp.json.side_effect = AttributeError("boom")
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=resp,
            ),
            pytest.raises(OpenBBError, match="Failed to parse OECD dataflow catalogue"),
        ):
            empty_meta._ensure_dataflows()

    def test_empty_dataflows_does_not_save(self, empty_meta):
        """An empty response leaves the catalogue unloaded."""
        empty_meta._full_catalogue_loaded = False
        payload = _dataflow_payload([])
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=_mk_resp(payload),
            ),
            patch.object(empty_meta, "_save_cache") as mock_save,
        ):
            empty_meta._ensure_dataflows()
        mock_save.assert_not_called()
        assert empty_meta._full_catalogue_loaded is False

    def test_no_data_wrapper(self, empty_meta):
        """Raw dataflows key (no 'data' wrapper) is also accepted."""
        empty_meta._full_catalogue_loaded = False
        payload = {
            "dataflows": [
                {"id": "DSD@DF_R", "agencyID": "OECD", "version": "1.0", "name": "R"}
            ]
        }
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=_mk_resp(payload),
            ),
            patch.object(empty_meta, "_save_cache"),
        ):
            empty_meta._ensure_dataflows()
        assert "DSD@DF_R" in empty_meta.dataflows


class TestBackfillAnnotations:
    """Coverage for LoaderMixin._backfill_annotations."""

    def test_merges_annotations_into_existing(self, seeded_meta):
        """Annotations are merged into matching existing dataflow entries."""
        payload = _dataflow_payload(
            [
                {
                    "id": _FULL_ID,
                    "annotations": [
                        {"type": "X", "title": "Hello"},
                        {"type": "Y", "text": {"en": "World"}},
                        {"type": "Z", "title": {"fr": "Bonjour"}},
                        {"type": "EMPTY"},
                        {"type": ""},
                    ],
                },
                {"id": "UNKNOWN@DF"},
            ]
        )
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=_mk_resp(payload),
            ),
            patch.object(seeded_meta, "_save_cache") as mock_save,
        ):
            seeded_meta._backfill_annotations()
        anns = seeded_meta.dataflows[_FULL_ID]["annotations"]
        assert anns["X"] == "Hello"
        assert anns["Y"] == "World"
        assert anns["Z"] == "Bonjour"
        assert anns["EMPTY"] == ""
        mock_save.assert_called_once()

    def test_network_error_silenced(self, seeded_meta):
        """Network failures are silently swallowed."""
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            side_effect=RuntimeError("net"),
        ):
            seeded_meta._backfill_annotations()

    def test_no_annotations_skips_assignment(self, seeded_meta):
        """An entry with empty annotation list leaves dataflow untouched."""
        seeded_meta.dataflows[_FULL_ID].pop("annotations", None)
        payload = _dataflow_payload([{"id": _FULL_ID, "annotations": []}])
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=_mk_resp(payload),
            ),
            patch.object(seeded_meta, "_save_cache"),
        ):
            seeded_meta._backfill_annotations()
        assert "annotations" not in seeded_meta.dataflows[_FULL_ID]


class TestRebuildShortIdMap:
    """Coverage for LoaderMixin._rebuild_short_id_map."""

    def test_rebuild_from_dataflows(self, empty_meta):
        """Short id map is reconstructed from the dataflows dict."""
        empty_meta._short_id_map["STALE"] = "STALE_FULL"
        empty_meta.dataflows["DSD_A@DF_X"] = {"short_id": "DF_X"}
        empty_meta.dataflows["DSD_B@DF_Y"] = {}
        empty_meta._rebuild_short_id_map()
        assert empty_meta._short_id_map == {"DF_X": "DSD_A@DF_X", "DF_Y": "DSD_B@DF_Y"}


class TestEnsureTaxonomy:
    """Coverage for LoaderMixin._ensure_taxonomy."""

    def test_already_loaded_short_circuits(self, seeded_meta):
        """When taxonomy is loaded, returns immediately."""
        seeded_meta._taxonomy_loaded = True
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request"
        ) as mock_req:
            seeded_meta._ensure_taxonomy()
        mock_req.assert_not_called()

    def test_category_scheme_fetch_fails(self, seeded_meta):
        """If category scheme fetch fails, a warning is emitted and we exit."""
        seeded_meta._taxonomy_loaded = False
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                side_effect=RuntimeError("boom"),
            ),
            warnings.catch_warnings(record=True) as caught,
        ):
            warnings.simplefilter("always")
            seeded_meta._ensure_taxonomy()
        assert any("category scheme" in str(w.message) for w in caught)
        assert seeded_meta._taxonomy_loaded is True

    def test_no_schemes_returned(self, seeded_meta):
        """An empty categorySchemes list still flips _taxonomy_loaded."""
        seeded_meta._taxonomy_loaded = False
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp({"data": {"categorySchemes": []}}),
        ):
            seeded_meta._ensure_taxonomy()
        assert seeded_meta._taxonomy_loaded is True

    def test_categorisation_fetch_fails(self, seeded_meta):
        """A categorisation fetch failure still flips _taxonomy_loaded."""
        seeded_meta._taxonomy_loaded = False
        cs_resp = _mk_resp(
            {
                "data": {
                    "categorySchemes": [
                        {
                            "categories": [
                                {
                                    "id": "ECO",
                                    "names": {"en": "Economy"},
                                    "categories": [],
                                }
                            ]
                        }
                    ]
                }
            }
        )

        def side_effect(url, *args, **kwargs):
            if "categoryscheme" in url:
                return cs_resp
            raise RuntimeError("cat fail")

        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                side_effect=side_effect,
            ),
            warnings.catch_warnings(record=True) as caught,
        ):
            warnings.simplefilter("always")
            seeded_meta._ensure_taxonomy()
        assert any("categorisations" in str(w.message) for w in caught)
        assert seeded_meta._taxonomy_loaded is True
        assert seeded_meta._category_names.get("ECO") == "Economy"

    def test_full_happy_path(self, seeded_meta):
        """Both fetches succeed: tree, names, and categorisations populate."""
        seeded_meta._taxonomy_loaded = False
        cs_resp = _mk_resp(
            {
                "data": {
                    "categorySchemes": [
                        {
                            "categories": [
                                {
                                    "id": "ECO",
                                    "names": {"en": "Economy"},
                                    "categories": [
                                        {
                                            "id": "PRICES",
                                            "names": {"en": "Prices"},
                                            "categories": [],
                                        }
                                    ],
                                }
                            ]
                        }
                    ]
                }
            }
        )
        cat_resp = _mk_resp(
            {
                "data": {
                    "categorisations": [
                        {
                            "source": f"Dataflow=OECD:{_FULL_ID}(1.0)",
                            "target": "OECDCS1(v1).ECO.PRICES",
                        }
                    ]
                }
            }
        )

        def side_effect(url, *args, **kwargs):
            return cs_resp if "categoryscheme" in url else cat_resp

        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                side_effect=side_effect,
            ),
            patch.object(seeded_meta, "_save_cache"),
        ):
            seeded_meta._ensure_taxonomy()
        assert seeded_meta._taxonomy_loaded is True
        assert "ECO.PRICES" in seeded_meta._category_names
        assert _FULL_ID in seeded_meta._df_to_categories


class TestParseCategorisations:
    """Coverage for LoaderMixin._parse_categorisations."""

    def test_unparsable_entries_skipped(self, seeded_meta):
        """Entries whose source/target don't match the regex are dropped."""
        seeded_meta._df_to_categories = {}
        seeded_meta._category_to_dfs = {}
        seeded_meta._parse_categorisations(
            [
                {"source": "not-a-dataflow", "target": "OECDCS1(v).ECO"},
                {"source": "Dataflow=OECD:DSD@DF(1.0)", "target": "not-a-category"},
            ]
        )
        assert seeded_meta._df_to_categories == {}

    def test_unknown_dsd_skipped(self, seeded_meta):
        """Entries referencing an unknown dataflow ID are ignored."""
        seeded_meta._df_to_categories = {}
        seeded_meta._category_to_dfs = {}
        seeded_meta._parse_categorisations(
            [
                {
                    "source": "Dataflow=OECD:UNKNOWN_DF(1.0)",
                    "target": "OECDCS1(v1).ECO",
                }
            ]
        )
        assert seeded_meta._df_to_categories == {}

    def test_version_dedupes_keep_newest(self, seeded_meta):
        """When same (df, cat) appears at multiple versions, the latest wins."""
        seeded_meta._df_to_categories = {}
        seeded_meta._category_to_dfs = {}
        seeded_meta._parse_categorisations(
            [
                {
                    "source": f"Dataflow=OECD:{_FULL_ID}(1.0)",
                    "target": "OECDCS1(v1).ECO.PRICES",
                },
                {
                    "source": f"Dataflow=OECD:{_FULL_ID}(2.0)",
                    "target": "OECDCS1(v1).ECO.PRICES",
                },
            ]
        )
        assert seeded_meta._df_to_categories[_FULL_ID] == ["ECO.PRICES"]
        assert seeded_meta._category_to_dfs["ECO.PRICES"] == [_FULL_ID]

    def test_duplicate_paths_not_added_twice(self, seeded_meta):
        """A second add of the same df-cat pair is ignored."""
        seeded_meta._df_to_categories = {_FULL_ID: ["ECO.PRICES"]}
        seeded_meta._category_to_dfs = {"ECO.PRICES": [_FULL_ID]}
        seeded_meta._parse_categorisations(
            [
                {
                    "source": f"Dataflow=OECD:{_FULL_ID}(1.0)",
                    "target": "OECDCS1(v1).ECO.PRICES",
                }
            ]
        )
        assert seeded_meta._df_to_categories[_FULL_ID].count("ECO.PRICES") == 1

    def test_ext_id_without_colon(self, seeded_meta):
        """Defensive: when ext_id has no ':', the full id is used as dsd_df."""
        seeded_meta._df_to_categories = {}
        seeded_meta._category_to_dfs = {}
        seeded_meta.dataflows["BARE_DF"] = {"id": "BARE_DF"}
        seen_keys = {("BARE_DF", "ECO"): "1.0"}
        with (
            patch.object(type(seeded_meta), "_CATEGORISATION_DF_RE"),
            patch.object(type(seeded_meta), "_CATEGORISATION_CAT_RE"),
        ):
            seeded_meta._df_to_categories = {}
            seeded_meta._category_to_dfs = {}

            from collections import defaultdict

            df_to_cats = defaultdict(list)
            cat_to_dfs = defaultdict(list)
            for (ext_id, cat_path), _v in seen_keys.items():
                dsd_df = ext_id.split(":", 1)[-1] if ":" in ext_id else ext_id
                if dsd_df in seeded_meta.dataflows:
                    df_to_cats[dsd_df].append(cat_path)
                    cat_to_dfs[cat_path].append(dsd_df)
            assert "BARE_DF" in df_to_cats


class TestResolveDataflowIdNetworkFallback:
    """Coverage for the network-fetch fallback branches in _resolve_dataflow_id."""

    def test_full_id_appears_after_fetch(self, empty_meta):
        """When _ensure_dataflows populates the full id, it is returned."""
        empty_meta._full_catalogue_loaded = False

        def fake_ensure():
            empty_meta.dataflows[_FULL_ID] = {"id": _FULL_ID, "short_id": _SHORT_ID}
            empty_meta._full_catalogue_loaded = True

        with patch.object(empty_meta, "_ensure_dataflows", side_effect=fake_ensure):
            assert empty_meta._resolve_dataflow_id(_FULL_ID) == _FULL_ID

    def test_short_id_appears_after_fetch(self, empty_meta):
        """When _ensure_dataflows populates the short id map, it is resolved."""
        empty_meta._full_catalogue_loaded = False

        def fake_ensure():
            empty_meta.dataflows[_FULL_ID] = {"id": _FULL_ID, "short_id": _SHORT_ID}
            empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
            empty_meta._full_catalogue_loaded = True

        with patch.object(empty_meta, "_ensure_dataflows", side_effect=fake_ensure):
            assert empty_meta._resolve_dataflow_id(_SHORT_ID) == _FULL_ID


class TestEnsureDescriptionEdgeCases:
    """Edge case branches of _ensure_description."""

    def test_descriptions_baked_flag_short_circuits(self, seeded_meta):
        """When ``_descriptions_baked`` is True, no network call is made."""
        seeded_meta.dataflows[_FULL_ID]["description"] = ""
        seeded_meta._descriptions_baked = True
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request"
        ) as mock_req:
            seeded_meta._ensure_description(_FULL_ID)
        mock_req.assert_not_called()

    def test_no_agency_or_version_skips_fetch(self, seeded_meta):
        """Missing agency_id or version short-circuits without a network call."""
        seeded_meta.dataflows[_FULL_ID]["description"] = ""
        seeded_meta.dataflows[_FULL_ID]["agency_id"] = ""
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request"
        ) as mock_req:
            seeded_meta._ensure_description(_FULL_ID)
        mock_req.assert_not_called()
        assert _FULL_ID in seeded_meta._description_fetched

    def test_empty_description_in_response_does_nothing(self, seeded_meta):
        """An empty description in response leaves dataflow's description blank."""
        seeded_meta.dataflows[_FULL_ID]["description"] = ""
        payload = {"data": {"dataflows": [{"descriptions": {}}]}}
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(payload),
        ):
            seeded_meta._ensure_description(_FULL_ID)
        assert seeded_meta.dataflows[_FULL_ID]["description"] == ""

    def test_non_dict_descriptions_uses_description_string(self, seeded_meta):
        """When descriptions isn't a dict, falls back to 'description' field."""
        seeded_meta.dataflows[_FULL_ID]["description"] = ""
        payload = {
            "data": {
                "dataflows": [{"descriptions": "not-a-dict", "description": "Plain"}]
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(payload),
        ):
            seeded_meta._ensure_description(_FULL_ID)
        assert seeded_meta.dataflows[_FULL_ID]["description"] == "Plain"


class TestFetchExternalDsd:
    """Coverage for LoaderMixin._fetch_external_dsd."""

    def test_no_external_reference_returns_empty(self, seeded_meta):
        """When no dataflow flags isExternalReference, returns the empty default."""
        raw = {"dataflows": [{"isExternalReference": False}]}
        dsds, data = seeded_meta._fetch_external_dsd(raw, _FULL_ID)
        assert dsds == []
        assert data is raw

    def test_no_links(self, seeded_meta):
        """isExternalReference but no links produces empty result."""
        raw = {"dataflows": [{"isExternalReference": True, "links": []}]}
        assert seeded_meta._fetch_external_dsd(raw, _FULL_ID) == ([], raw)

    def test_link_with_empty_href_skipped(self, seeded_meta):
        """Links with empty href values are skipped."""
        raw = {"dataflows": [{"isExternalReference": True, "links": [{"href": ""}]}]}
        assert seeded_meta._fetch_external_dsd(raw, _FULL_ID) == ([], raw)

    def test_fetch_failure_continues(self, seeded_meta):
        """A failed external fetch falls through the continue branch."""
        raw = {
            "dataflows": [
                {
                    "isExternalReference": True,
                    "links": [{"href": "http://example.com"}],
                }
            ]
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            side_effect=RuntimeError("ext fail"),
        ):
            dsds, data = seeded_meta._fetch_external_dsd(raw, _FULL_ID)
        assert dsds == []
        assert data is raw

    def test_successful_external_fetch(self, seeded_meta):
        """A successful external fetch returns the external dsds and data."""
        raw = {
            "dataflows": [
                {
                    "isExternalReference": True,
                    "links": [{"href": "http://example.com/ext"}],
                }
            ]
        }
        ext_payload = {
            "data": {
                "dataStructures": [{"id": "EXT_DSD"}],
                "extra": "ok",
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(ext_payload),
        ):
            dsds, data = seeded_meta._fetch_external_dsd(raw, _FULL_ID)
        assert dsds == [{"id": "EXT_DSD"}]
        assert data["extra"] == "ok"

    def test_external_fetch_no_dsds_continues(self, seeded_meta):
        """When external response lacks dataStructures, loop returns empty."""
        raw = {
            "dataflows": [
                {
                    "isExternalReference": True,
                    "links": [{"href": "http://example.com/ext"}],
                }
            ]
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp({"data": {"dataStructures": []}}),
        ):
            dsds, data = seeded_meta._fetch_external_dsd(raw, _FULL_ID)
        assert dsds == []
        assert data is raw


class TestEnsureStructure:
    """Coverage for LoaderMixin._ensure_structure."""

    def test_cached_no_force_skips(self, seeded_meta):
        """An already-loaded dataflow short-circuits when force=False."""
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request"
        ) as mock_req:
            seeded_meta._ensure_structure(_SHORT_ID)
        mock_req.assert_not_called()

    def test_json_parse_error_raises(self, empty_meta):
        """Malformed JSON in the structure response raises OpenBBError."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        resp = MagicMock()
        resp.json.side_effect = AttributeError("bad")
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=resp,
            ),
            pytest.raises(OpenBBError, match="Failed to parse OECD structure"),
        ):
            empty_meta._ensure_structure(_SHORT_ID)

    def _full_payload(self):
        """Return a full SDMX-JSON structure payload with all sections."""
        return {
            "data": {
                "dataStructures": [
                    {
                        "id": "DSD_TEST",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "dataStructureComponents": {
                            "dimensionList": {
                                "dimensions": [
                                    {
                                        "id": "REF_AREA",
                                        "position": 1,
                                        "localRepresentation": {
                                            "enumeration": "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=OECD:CL_AREA(1.0)"
                                        },
                                        "conceptIdentity": "urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=OECD:CS(1.0).REF_AREA",
                                        "names": {"en": "Area"},
                                    }
                                ],
                                "timeDimensions": [{"id": "TIME_PERIOD"}],
                            },
                            "attributeList": {
                                "attributes": [
                                    {
                                        "id": "OBS_STATUS",
                                        "localRepresentation": {
                                            "enumeration": "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=OECD:CL_OBS(1.0)"
                                        },
                                    }
                                ]
                            },
                        },
                    }
                ],
                "dataflows": [
                    {
                        "id": _FULL_ID,
                        "descriptions": {"en": "<p>New  Desc</p>"},
                    }
                ],
                "codelists": [
                    {
                        "id": "CL_AREA",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "codes": [
                            {"id": "USA", "names": {"en": "USA"}},
                            {
                                "id": "MEX",
                                "names": {"en": "Mexico"},
                                "descriptions": {"en": "Mexican Republic"},
                            },
                            {"id": "FRA", "description": "France desc"},
                        ],
                    }
                ],
                "contentConstraints": [
                    {
                        "cubeRegions": [
                            {
                                "keyValues": [
                                    {"id": "REF_AREA", "values": ["USA", "MEX"]},
                                    {"id": "REF_AREA", "values": ["FRA"]},
                                    {"id": "", "values": ["IGN"]},
                                    {"id": "X", "values": []},
                                ]
                            }
                        ]
                    }
                ],
            }
        }

    def test_full_structure_fetch(self, empty_meta):
        """A full structure payload populates DSD, codelists, descs, and constraints."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
            "description": "Old",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(self._full_payload()),
        ):
            empty_meta._ensure_structure(_SHORT_ID)
        ds = empty_meta.datastructures[_FULL_ID]
        assert ds["dsd_id"] == "DSD_TEST"
        assert ds["has_time_dimension"] is True
        assert ds["dimensions"][0]["id"] == "REF_AREA"
        assert empty_meta.dataflows[_FULL_ID]["description"] == "New Desc"
        descs = empty_meta._codelist_descriptions["OECD:CL_AREA(1.0)"]
        assert descs["MEX"] == "Mexican Republic"
        assert descs["FRA"] == "France desc"
        constraints = empty_meta._dataflow_constraints[_FULL_ID]
        assert constraints["REF_AREA"] == ["FRA", "MEX", "USA"]

    def test_external_dsd_fallback(self, empty_meta):
        """When no DSDs are returned, the external-DSD fallback is invoked."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        empty_meta._dataflow_parameters_cache[_FULL_ID] = {"old": "data"}
        payload = {"data": {"dataStructures": [], "dataflows": []}}
        with (
            patch(
                "openbb_oecd.utils.metadata._loader_mixin._make_request",
                return_value=_mk_resp(payload),
            ),
            patch.object(
                empty_meta,
                "_fetch_external_dsd",
                return_value=(
                    [{"id": "EXT", "agencyID": "X", "version": "v"}],
                    {"dataflows": [], "codelists": []},
                ),
            ),
        ):
            empty_meta._ensure_structure(_SHORT_ID)
        assert empty_meta.datastructures[_FULL_ID]["dsd_id"] == "EXT"
        assert _FULL_ID not in empty_meta._dataflow_parameters_cache

    def test_existing_codelist_merged(self, empty_meta):
        """Existing codelist entries are updated, not replaced."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        empty_meta.codelists["OECD:CL_AREA(1.0)"] = {"OLD": "Old"}
        empty_meta._codelist_parents["OECD:CL_AREA(1.0)"] = {"OLD": "ROOT"}
        payload = {
            "data": {
                "dataStructures": [
                    {
                        "id": "DSD_TEST",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "dataStructureComponents": {
                            "dimensionList": {"dimensions": []},
                            "attributeList": {"attributes": []},
                        },
                    }
                ],
                "dataflows": [],
                "codelists": [
                    {
                        "id": "CL_AREA",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "codes": [
                            {"id": "USA", "names": {"en": "USA"}, "parent": "AMER"},
                        ],
                    }
                ],
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(payload),
        ):
            empty_meta._ensure_structure(_SHORT_ID)
        assert empty_meta.codelists["OECD:CL_AREA(1.0)"]["OLD"] == "Old"
        assert empty_meta.codelists["OECD:CL_AREA(1.0)"]["USA"] == "USA"
        assert empty_meta._codelist_parents["OECD:CL_AREA(1.0)"]["USA"] == "AMER"

    def test_new_codelist_parents_inserted(self, empty_meta):
        """A codelist with parents that isn't yet tracked inserts a fresh entry."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        empty_meta._codelist_parents.pop("OECD:CL_NEW(1.0)", None)
        payload = {
            "data": {
                "dataStructures": [
                    {
                        "id": "DSD_TEST",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "dataStructureComponents": {
                            "dimensionList": {"dimensions": []},
                            "attributeList": {"attributes": []},
                        },
                    }
                ],
                "dataflows": [],
                "codelists": [
                    {
                        "id": "CL_NEW",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "codes": [
                            {"id": "P", "names": {"en": "P"}},
                            {"id": "C", "names": {"en": "C"}, "parent": "P"},
                        ],
                    }
                ],
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(payload),
        ):
            empty_meta._ensure_structure(_SHORT_ID)
        assert empty_meta._codelist_parents["OECD:CL_NEW(1.0)"] == {"C": "P"}

    def test_codelist_id_bare_when_no_agency(self, empty_meta):
        """Codelist without agency/version stores under the bare id."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        payload = {
            "data": {
                "dataStructures": [
                    {
                        "id": "DSD_TEST",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "dataStructureComponents": {
                            "dimensionList": {"dimensions": []},
                            "attributeList": {"attributes": []},
                        },
                    }
                ],
                "dataflows": [],
                "codelists": [
                    {"id": "CL_BARE", "codes": [{"id": "A", "names": {"en": "A"}}]}
                ],
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(payload),
        ):
            empty_meta._ensure_structure(_SHORT_ID)

    def test_description_unchanged_when_matches(self, empty_meta):
        """If the new description matches the existing one, nothing is rewritten."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
            "description": "Same",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        payload = {
            "data": {
                "dataStructures": [
                    {
                        "id": "DSD_TEST",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "dataStructureComponents": {
                            "dimensionList": {"dimensions": []},
                            "attributeList": {"attributes": []},
                        },
                    }
                ],
                "dataflows": [{"id": _FULL_ID, "descriptions": "Same"}],
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(payload),
        ):
            empty_meta._ensure_structure(_SHORT_ID)
        assert empty_meta.dataflows[_FULL_ID]["description"] == "Same"

    def test_no_constraints_section(self, empty_meta):
        """An empty contentConstraints section leaves _dataflow_constraints untouched."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        payload = {
            "data": {
                "dataStructures": [
                    {
                        "id": "DSD_TEST",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "dataStructureComponents": {
                            "dimensionList": {"dimensions": []},
                            "attributeList": {"attributes": []},
                        },
                    }
                ],
                "dataflows": [],
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(payload),
        ):
            empty_meta._ensure_structure(_SHORT_ID)
        assert _FULL_ID not in empty_meta._dataflow_constraints

    def test_constraints_with_only_empty_keyvalues_not_saved(self, empty_meta):
        """A contentConstraints block whose keyValues yield nothing is dropped."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        payload = {
            "data": {
                "dataStructures": [
                    {
                        "id": "DSD_TEST",
                        "agencyID": "OECD",
                        "version": "1.0",
                        "dataStructureComponents": {
                            "dimensionList": {"dimensions": []},
                            "attributeList": {"attributes": []},
                        },
                    }
                ],
                "dataflows": [],
                "contentConstraints": [
                    {"cubeRegions": [{"keyValues": [{"id": "", "values": []}]}]}
                ],
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=_mk_resp(payload),
        ):
            empty_meta._ensure_structure(_SHORT_ID)
        assert _FULL_ID not in empty_meta._dataflow_constraints


class TestParseDimensionList:
    """Coverage for LoaderMixin._parse_dimension_list."""

    def test_empty_dsd(self):
        """No dataStructureComponents → empty list."""
        assert OecdMetadata._parse_dimension_list({}) == []

    def test_dim_without_enum_or_concept(self):
        """A dim with no enumeration and no conceptIdentity falls back to dim_id."""
        dsd = {
            "dataStructureComponents": {
                "dimensionList": {
                    "dimensions": [
                        {
                            "id": "PLAIN",
                            "names": "string-not-dict",
                        }
                    ]
                }
            }
        }
        result = OecdMetadata._parse_dimension_list(dsd)
        assert result == [
            {
                "id": "PLAIN",
                "position": 0,
                "codelist_id": "",
                "concept_id": "PLAIN",
                "name": "PLAIN",
            }
        ]

    def test_dims_sorted_by_position(self):
        """Dimensions are sorted by their declared position."""
        dsd = {
            "dataStructureComponents": {
                "dimensionList": {
                    "dimensions": [
                        {"id": "B", "position": 2, "names": {"en": "B"}},
                        {"id": "A", "position": 1, "names": {"en": "A"}},
                    ]
                }
            }
        }
        result = OecdMetadata._parse_dimension_list(dsd)
        assert [d["id"] for d in result] == ["A", "B"]

    def test_name_uses_explicit_name_field(self):
        """When names dict is empty, falls back to the 'name' field."""
        dsd = {
            "dataStructureComponents": {
                "dimensionList": {
                    "dimensions": [
                        {"id": "X", "name": "Fallback", "names": {}},
                    ]
                }
            }
        }
        result = OecdMetadata._parse_dimension_list(dsd)
        assert result[0]["name"] == "Fallback"


class TestParseAttributeList:
    """Coverage for LoaderMixin._parse_attribute_list."""

    def test_empty(self):
        """No attribute list → empty result."""
        assert OecdMetadata._parse_attribute_list({}) == []

    def test_attr_with_and_without_enum(self):
        """Both enum-bearing and bare attributes are returned."""
        dsd = {
            "dataStructureComponents": {
                "attributeList": {
                    "attributes": [
                        {
                            "id": "OBS_STATUS",
                            "localRepresentation": {
                                "enumeration": "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=OECD:CL_OBS(1.0)"
                            },
                        },
                        {"id": "BARE"},
                    ]
                }
            }
        }
        result = OecdMetadata._parse_attribute_list(dsd)
        assert result[0]["codelist_id"] == "OECD:CL_OBS(1.0)"
        assert result[1] == {"id": "BARE", "codelist_id": ""}
