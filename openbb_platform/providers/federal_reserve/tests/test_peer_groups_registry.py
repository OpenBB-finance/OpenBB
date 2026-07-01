"""Tests for the FFIEC UBPR peer-group registry."""

import pytest

from openbb_federal_reserve.utils import peer_groups


class TestStaticSnapshot:
    """Tests for the baked peer-group snapshot."""

    def test_known_ids(self):
        """The snapshot carries the verified, category-spanning ``peergroupid`` set."""
        ids = {name: value[0] for name, value in peer_groups.STATIC_PEER_GROUPS.items()}
        assert ids["1"] == 4
        assert ids["101"] == 20
        assert ids["201"] == 25
        assert ids["301"] == 28
        assert ids["401"] == 29
        assert ids["ALCOM"] == 236
        assert ids["NATIONAL"] == 2
        assert ids["COM"] == 3
        assert ids["SVG"] == 19

    def test_concept_categories_present(self):
        """Every documented ``conceptname`` category appears in the snapshot."""
        concepts = {value[2] for value in peer_groups.STATIC_PEER_GROUPS.values()}
        assert {
            "UBPPD186",
            "UBPPM277",
            "UBPPF861",
            "UBPPF863",
            "UBPPF865",
            "UBPPF866",
        } <= concepts

    def test_names_unique(self):
        """The snapshot is keyed on a unique peer-group name."""
        assert len(peer_groups.STATIC_PEER_GROUPS) == 187


class TestRecords:
    """Tests for the ``PGSelector`` row indexer."""

    def test_indexes_rows_by_name(self):
        """Each well-formed row is indexed by its peer-group name."""
        records = peer_groups._records(
            [
                {
                    "peergroupname": "1",
                    "peergroupid": "4",
                    "peergroupdescription": "Largest banks",
                    "conceptname": "UBPPD186",
                },
            ]
        )
        assert records["1"] == {
            "peergroupid": 4,
            "description": "Largest banks",
            "conceptname": "UBPPD186",
        }

    def test_skips_non_dict_rows(self):
        """Non-dict rows are ignored."""
        assert peer_groups._records(["not-a-dict"]) == {}

    def test_skips_rows_missing_name_or_id(self):
        """Rows without a name or id are dropped."""
        records = peer_groups._records(
            [
                {"peergroupid": "4"},
                {"peergroupname": "1"},
                {"peergroupname": "", "peergroupid": "4"},
            ]
        )
        assert records == {}


class TestFetchPeerGroups:
    """Tests for the live registry fetch."""

    def _wire(self, monkeypatch, payload):
        """Patch the router post and run the producer through the cache seam."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: payload,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )

    def test_fetches_and_indexes(self, monkeypatch):
        """A ``PGSelector`` response is indexed by peer-group name."""
        self._wire(
            monkeypatch,
            [
                {
                    "peergroupname": "NATIONAL",
                    "peergroupid": "2",
                    "peergroupdescription": "All banks in nation",
                    "conceptname": "UBPPF866",
                }
            ],
        )
        registry = peer_groups.fetch_peer_groups("151")
        assert registry["NATIONAL"]["peergroupid"] == 2

    def test_requests_full_unfiltered_list(self, monkeypatch):
        """The fetch requests the full list via ``MinMembersReqd`` ``"0"``."""
        captured: dict = {}

        def _post(requestor_id, criteria):
            captured["requestor_id"] = requestor_id
            captured["criteria"] = criteria
            return []

        monkeypatch.setattr("openbb_federal_reserve.utils.ubpr_report._post", _post)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        peer_groups.fetch_peer_groups("151")
        assert captured["requestor_id"] == "PGSelector"
        assert captured["criteria"] == {
            "ReportingCycleID": "151",
            "MinMembersReqd": "0",
        }

    def test_empty_response_falls_back_to_static(self, monkeypatch):
        """An empty or non-list response yields the baked snapshot."""
        self._wire(monkeypatch, [])
        registry = peer_groups.fetch_peer_groups("151")
        assert registry["1"]["peergroupid"] == 4


class TestResolvePeerGroupId:
    """Tests for name -> ``peergroupid`` resolution."""

    def test_static_snapshot_when_no_cycle(self):
        """Without a cycle the baked snapshot resolves the name."""
        assert peer_groups.resolve_peer_group_id("NATIONAL") == 2

    def test_live_registry_when_cycle_given(self, monkeypatch):
        """With a cycle the live registry resolves the name."""
        monkeypatch.setattr(
            peer_groups,
            "fetch_peer_groups",
            lambda cycle_id: {"1": {"peergroupid": 99}},
        )
        assert peer_groups.resolve_peer_group_id("1", cycle_id="151") == 99

    def test_live_miss_falls_back_to_static(self, monkeypatch):
        """A name missing from the live registry falls back to the snapshot."""
        monkeypatch.setattr(peer_groups, "fetch_peer_groups", lambda cycle_id: {})
        assert peer_groups.resolve_peer_group_id("ALCOM", cycle_id="151") == 236

    def test_unknown_name_raises(self):
        """An unknown name raises ``ValueError``."""
        with pytest.raises(ValueError, match="Unknown peer group"):
            peer_groups.resolve_peer_group_id("ZZZ")


class TestPeerGroupOptions:
    """Tests for the dropdown option builder."""

    def test_expanded_labels_and_name_values(self):
        """Options expand to ``name -- description`` with the name as the value."""
        options = peer_groups.peer_group_options()
        assert len(options) == 187
        option = next(o for o in options if o["value"] == "1")
        assert option["label"] == (
            "1 -- Insured commercial banks having assets greater than $100 billion"
        )

    def test_concept_filter(self):
        """A concept filter limits the options to those categories."""
        options = peer_groups.peer_group_options(concepts=("UBPPF863",))
        assert all(
            peer_groups.STATIC_PEER_GROUPS[o["value"]][2] == "UBPPF863" for o in options
        )
        assert options
        assert all(o["value"] not in ("1", "NATIONAL") for o in options)

    def test_blank_description_label_is_name_only(self, monkeypatch):
        """A peer group with no description labels by name alone."""
        monkeypatch.setitem(
            peer_groups._STATIC_RECORDS,
            "ZZZ",
            {"peergroupid": 1, "description": "", "conceptname": "UBPPD186"},
        )
        option = next(
            o for o in peer_groups.peer_group_options() if o["value"] == "ZZZ"
        )
        assert option["label"] == "ZZZ"
