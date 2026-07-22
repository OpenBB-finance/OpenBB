"""Tests for the USAspending recipient search, info, and awards widgets."""

import asyncio
import json
import re

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.treasury import treasury_router
from openbb_government_us.treasury.models.usaspending_recipient_awards import (
    UsSpendingRecipientAwardsFetcher,
)
from openbb_government_us.treasury.models.usaspending_recipient_search import (
    UsSpendingRecipientSearchData,
    UsSpendingRecipientSearchFetcher,
)
from openbb_government_us.treasury.treasury_router import recipient_info, router
from openbb_government_us.treasury.utils import (
    recipient as recipient_utils,
    usaspending,
)
from openbb_government_us.treasury.utils.recipient_render import render_recipient_info

RID = "b97d19b0-833c-8d8f-3a2c-157d04ea55ef-P"


def _profile(**overrides) -> dict:
    """Build a recipient profile payload with overridable defaults."""
    record = {
        "name": "LOCKHEED MARTIN CORP",
        "alternate_names": [],
        "duns": "834951691",
        "uei": "ZFN2JJXBLZT3",
        "recipient_id": RID,
        "recipient_level": "P",
        "parent_id": RID,
        "parent_name": "LOCKHEED MARTIN CORP",
        "parent_duns": "834951691",
        "parent_uei": "ZFN2JJXBLZT3",
        "parents": [],
        "business_types": ["category_business"],
        "location": {"city_name": "BETHESDA", "state_code": "MD", "zip": "20817"},
        "total_transaction_amount": 63372229980.46,
        "total_transactions": 987462,
        "total_face_value_loan_amount": 0.0,
        "total_face_value_loan_transactions": 0,
    }
    record.update(overrides)
    return record


def _child(number: int = 1) -> dict:
    """Build a child recipient row."""
    return {
        "recipient_id": f"6cf5fb1b-4988-d087-5dc1-70939d8fc6c{number}-C",
        "name": "LOCKHEED MARTIN CORPORATION",
        "duns": "007038032",
        "uei": "G4KDGE4JFFK7",
        "amount": 26355172263.5,
        "state_province": "TX",
    }


class TestNormalizeRecipientId:
    """Tests for recipient id normalization."""

    def test_lowercases_the_hash(self):
        """An uppercased hash is lowercased, which the source requires."""
        assert recipient_utils.normalize_recipient_id(RID.upper()) == RID

    def test_uppercases_the_level(self):
        """A lowercased level is restored to upper case."""
        assert recipient_utils.normalize_recipient_id(RID[:-1] + "p") == RID

    def test_rejects_a_missing_level(self):
        """An id with no recipient level is rejected rather than sent."""
        with pytest.raises(OpenBBError, match="must end with a recipient level"):
            recipient_utils.normalize_recipient_id(RID.rsplit("-", 1)[0])

    def test_rejects_an_unknown_level(self):
        """An id with an unrecognized level is rejected."""
        with pytest.raises(OpenBBError, match="must end with a recipient level"):
            recipient_utils.normalize_recipient_id(RID[:-1] + "X")


class TestRecipientHelpers:
    """Tests for the recipient request helpers."""

    def test_profile_omits_the_year_when_absent(self, monkeypatch):
        """No year sends no query string, since an empty one means all-time."""
        captured: dict = {}

        async def _fake(path, **kwargs):
            captured["path"] = path
            return {}

        monkeypatch.setattr(usaspending, "get_usaspending", _fake)
        asyncio.run(recipient_utils.get_profile(RID))
        assert captured["path"] == f"recipient/{RID}/"

    def test_profile_sends_a_given_year(self, monkeypatch):
        """An explicit year is appended to the path."""
        captured: dict = {}

        async def _fake(path, **kwargs):
            captured["path"] = path
            return {}

        monkeypatch.setattr(usaspending, "get_usaspending", _fake)
        asyncio.run(recipient_utils.get_profile(RID, year="all"))
        assert captured["path"] == f"recipient/{RID}/?year=all"

    def test_children_skips_an_unusable_key(self, monkeypatch):
        """A key that is neither a DUNS nor a UEI makes no request."""
        called: list = []

        async def _fake(path, **kwargs):
            called.append(path)
            return []

        monkeypatch.setattr(usaspending, "get_usaspending", _fake)
        assert asyncio.run(recipient_utils.get_children("abc")) == []
        assert called == []

    def test_children_accepts_duns_and_uei_lengths(self, monkeypatch):
        """A 9-character DUNS and a 12-character UEI are both requested."""
        called: list = []

        async def _fake(path, **kwargs):
            called.append(path)
            return [_child()]

        monkeypatch.setattr(usaspending, "get_usaspending", _fake)
        assert len(asyncio.run(recipient_utils.get_children("834951691"))) == 1
        assert len(asyncio.run(recipient_utils.get_children("ZFN2JJXBLZT3"))) == 1
        assert called == [
            "recipient/children/834951691/",
            "recipient/children/ZFN2JJXBLZT3/",
        ]

    def test_children_sends_a_given_year(self, monkeypatch):
        """An explicit year is appended to the children path."""
        captured: dict = {}

        async def _fake(path, **kwargs):
            captured["path"] = path
            return [_child()]

        monkeypatch.setattr(usaspending, "get_usaspending", _fake)
        asyncio.run(recipient_utils.get_children("834951691", year="all"))
        assert captured["path"] == "recipient/children/834951691/?year=all"

    def test_fiscal_year_window(self):
        """A fiscal year spans October through the following September."""
        assert recipient_utils.fiscal_year_window(2025) == {
            "start_date": "2024-10-01",
            "end_date": "2025-09-30",
        }

    def test_new_awards_retries_once(self, monkeypatch):
        """A single timeout is retried, since the source times out sporadically."""
        calls: list = []

        async def _fake(path, payload, **kwargs):
            calls.append(payload)
            if len(calls) == 1:
                raise OpenBBError("timeout")
            return {"results": [{"new_award_count_in_period": 5}]}

        monkeypatch.setattr(usaspending, "post_usaspending", _fake)
        window = recipient_utils.fiscal_year_window(2025)
        rows = asyncio.run(
            recipient_utils.get_new_awards_over_time(RID, "quarter", window)
        )
        assert len(calls) == 2
        assert rows == [{"new_award_count_in_period": 5}]

    def test_new_awards_reraises_a_second_failure(self, monkeypatch):
        """Two consecutive failures surface the error."""

        async def _fake(path, payload, **kwargs):
            raise OpenBBError("timeout")

        monkeypatch.setattr(usaspending, "post_usaspending", _fake)
        window = recipient_utils.fiscal_year_window(2025)
        with pytest.raises(OpenBBError):
            asyncio.run(
                recipient_utils.get_new_awards_over_time(RID, "quarter", window)
            )


class TestUsSpendingRecipientSearch:
    """Tests for the recipient search model."""

    @staticmethod
    def _patch(monkeypatch, results):
        """Patch the recipient list POST and record its payload."""
        captured: dict = {}

        async def _fake(path, payload, **kwargs):
            captured["path"] = path
            captured["payload"] = payload
            return {"results": results, "page_metadata": {"total": len(results)}}

        monkeypatch.setattr(usaspending, "post_usaspending", _fake)
        return captured

    def test_defaults(self):
        """The default search ranks every recipient by trailing amount."""
        query = UsSpendingRecipientSearchFetcher.transform_query({})
        assert query.award_type == "all"
        assert query.sort == "amount"
        assert query.order == "desc"
        assert query.keyword is None

    def test_blank_keyword_normalizes_to_none(self):
        """An empty or whitespace-only keyword is dropped rather than searched."""
        assert (
            UsSpendingRecipientSearchFetcher.transform_query({"keyword": "  "}).keyword
            is None
        )
        assert (
            UsSpendingRecipientSearchFetcher.transform_query({"keyword": ""}).keyword
            is None
        )

    def test_extract_omits_an_absent_keyword(self, monkeypatch):
        """No keyword sends no keyword field."""
        captured = self._patch(monkeypatch, [{"id": RID}])
        query = UsSpendingRecipientSearchFetcher.transform_query({})
        asyncio.run(UsSpendingRecipientSearchFetcher.aextract_data(query, None))
        assert captured["path"] == "recipient/duns/"
        assert "keyword" not in captured["payload"]
        assert captured["payload"]["award_type"] == "all"

    def test_extract_sends_the_keyword_and_award_type(self, monkeypatch):
        """A keyword and award type are forwarded to the source."""
        captured = self._patch(monkeypatch, [{"id": RID}])
        query = UsSpendingRecipientSearchFetcher.transform_query(
            {"keyword": "Lockheed", "award_type": "contracts"}
        )
        asyncio.run(UsSpendingRecipientSearchFetcher.aextract_data(query, None))
        assert captured["payload"]["keyword"] == "Lockheed"
        assert captured["payload"]["award_type"] == "contracts"

    def test_extract_empty_raises(self, monkeypatch):
        """No matching recipient raises EmptyDataError."""
        self._patch(monkeypatch, [])
        query = UsSpendingRecipientSearchFetcher.transform_query({"keyword": "zzz"})
        with pytest.raises(EmptyDataError, match="No recipients matched"):
            asyncio.run(UsSpendingRecipientSearchFetcher.aextract_data(query, None))

    def test_transform_labels_the_level(self):
        """The single-letter recipient level is expanded to a readable label."""
        query = UsSpendingRecipientSearchFetcher.transform_query({})
        rows = UsSpendingRecipientSearchFetcher.transform_data(
            query,
            [
                {"id": RID, "name": "A", "recipient_level": "P", "amount": 1.0},
                {"id": "x-C", "name": "B", "recipient_level": "C", "amount": -2.0},
                {"id": "y-R", "name": "C", "recipient_level": "R", "amount": 0.0},
            ],
        )
        assert [row.recipient_level for row in rows] == ["Parent", "Child", "Recipient"]
        assert rows[1].amount == -2.0

    def test_transform_drops_rows_without_an_id(self):
        """A row with no recipient id is dropped."""
        query = UsSpendingRecipientSearchFetcher.transform_query({})
        assert (
            UsSpendingRecipientSearchFetcher.transform_data(query, [{"name": "A"}])
            == []
        )

    def test_recipient_id_column_drives_the_drilldown(self):
        """The recipient_id column emits into the shared recipient_id group."""
        cfg = UsSpendingRecipientSearchData.model_fields[
            "recipient_id"
        ].json_schema_extra["x-widget_config"]
        assert cfg["renderFn"] == "cellOnClick"
        assert cfg["renderFnParams"]["groupByParamName"] == "recipient_id"


class TestUsSpendingRecipientAwards:
    """Tests for the recipient awards drill-down."""

    @staticmethod
    def _patch(monkeypatch, profile, results):
        """Patch the profile GET and the award-search POST."""
        captured: dict = {}

        async def _fake_get(path, **kwargs):
            return profile

        async def _fake_post(path, payload, **kwargs):
            captured["path"] = path
            captured["payload"] = payload
            return {"results": results}

        monkeypatch.setattr(usaspending, "get_usaspending", _fake_get)
        monkeypatch.setattr(usaspending, "post_usaspending", _fake_post)
        return captured

    def test_extract_searches_by_uei_not_recipient_id(self, monkeypatch):
        """The award search is scoped by UEI, which it honors, not recipient_id."""
        captured = self._patch(
            monkeypatch,
            _profile(),
            [{"generated_internal_id": "CONT_AWD_X", "Award Amount": 1.0}],
        )
        query = UsSpendingRecipientAwardsFetcher.transform_query({"recipient_id": RID})
        asyncio.run(UsSpendingRecipientAwardsFetcher.aextract_data(query, None))
        filters = captured["payload"]["filters"]
        assert filters["recipient_search_text"] == ["ZFN2JJXBLZT3"]
        assert "recipient_id" not in filters
        assert filters["award_type_codes"] == ["A", "B", "C", "D"]
        assert "Contract Award Type" in captured["payload"]["fields"]

    def test_extract_uses_the_assistance_type_field(self, monkeypatch):
        """A non-contract group requests the assistance award-type field."""
        captured = self._patch(
            monkeypatch, _profile(), [{"generated_internal_id": "ASST_X"}]
        )
        query = UsSpendingRecipientAwardsFetcher.transform_query(
            {"recipient_id": RID, "award_group": "grants"}
        )
        asyncio.run(UsSpendingRecipientAwardsFetcher.aextract_data(query, None))
        assert "Award Type" in captured["payload"]["fields"]
        assert "Contract Award Type" not in captured["payload"]["fields"]

    def test_extract_without_a_uei_raises(self, monkeypatch):
        """A recipient with no UEI cannot be searched and says so."""
        self._patch(monkeypatch, _profile(uei=None), [])
        query = UsSpendingRecipientAwardsFetcher.transform_query({"recipient_id": RID})
        with pytest.raises(OpenBBError, match="has no UEI registered"):
            asyncio.run(UsSpendingRecipientAwardsFetcher.aextract_data(query, None))

    def test_extract_empty_raises(self, monkeypatch):
        """A recipient with no awards in the group raises EmptyDataError."""
        self._patch(monkeypatch, _profile(), [])
        query = UsSpendingRecipientAwardsFetcher.transform_query({"recipient_id": RID})
        with pytest.raises(EmptyDataError, match="No 'contracts' awards"):
            asyncio.run(UsSpendingRecipientAwardsFetcher.aextract_data(query, None))

    def test_transform_maps_fields(self):
        """Source fields map to the unified schema."""
        query = UsSpendingRecipientAwardsFetcher.transform_query({"recipient_id": RID})
        rows = UsSpendingRecipientAwardsFetcher.transform_data(
            query,
            [
                {
                    "generated_internal_id": "CONT_AWD_X",
                    "Award ID": "N0001917C0001",
                    "Recipient Name": "LOCKHEED MARTIN CORPORATION",
                    "Award Amount": 35135514910.2,
                    "Contract Award Type": "DEFINITIVE CONTRACT",
                    "Start Date": "2016-08-01",
                }
            ],
        )
        assert rows[0].award_id == "CONT_AWD_X"
        assert rows[0].award_number == "N0001917C0001"
        assert rows[0].award_amount == 35135514910.2
        assert rows[0].award_type == "DEFINITIVE CONTRACT"

    def test_transform_drops_rows_without_an_award_id(self):
        """A row missing the generated award id is dropped."""
        query = UsSpendingRecipientAwardsFetcher.transform_query({"recipient_id": RID})
        assert (
            UsSpendingRecipientAwardsFetcher.transform_data(query, [{"Award ID": "x"}])
            == []
        )


class TestRecipientRender:
    """Tests for the recipient profile renderer."""

    def test_renders_identity_and_location(self):
        """The profile renders its identity and location sections."""
        html = render_recipient_info(_profile())
        assert re.findall(r"<h2>([^<]+)</h2>", html) == ["Identity", "Location"]
        assert "LOCKHEED MARTIN CORP" in html
        assert "BETHESDA" in html

    def test_leaves_no_unreplaced_tokens(self):
        """Every template token is substituted."""
        assert "__" not in render_recipient_info(_profile())

    def test_totals_keep_full_precision(self):
        """Totals are emitted raw, unrounded and unabbreviated."""
        html = render_recipient_info(_profile())
        assert 'data-value="63372229980.46"' in html
        assert "63.37" not in html

    def test_derives_the_share_of_total(self):
        """Each category row's share is derived from the supplied denominator."""
        html = render_recipient_info(
            _profile(),
            {"awarding_agency": [{"name": "DOD", "amount": 25.0}]},
            [],
            100.0,
        )
        assert 'data-prefix="pct">25.0<' in html

    def test_omits_the_share_without_a_denominator(self):
        """No denominator renders an empty share cell rather than a wrong one."""
        html = render_recipient_info(
            _profile(), {"awarding_agency": [{"name": "DOD", "amount": 25.0}]}, [], None
        )
        assert 'data-prefix="pct"' not in html
        assert "DOD" in html

    def test_top_categories_are_collapsible(self):
        """The top-category tables sit in one collapsible container."""
        html = render_recipient_info(
            _profile(), {"awarding_agency": [{"name": "DOD", "amount": 1.0}]}, [], 1.0
        )
        assert '<details class="tops"><summary>Top Categories</summary>' in html
        assert "Awarding Agencies" in html

    def test_children_are_collapsible_cards(self):
        """Child recipients render as collapsible cards in one container."""
        html = render_recipient_info(_profile(), {}, [_child(1), _child(2)], None, 2)
        assert (
            '<details class="children"><summary>Child Recipients (2)</summary>' in html
        )
        assert html.count('<details class="child">') == 2

    def test_discloses_a_truncated_child_render(self):
        """Rendering fewer children than exist states the shortfall."""
        html = render_recipient_info(_profile(), {}, [_child(1)], None, 216)
        assert "Child Recipients (216)" in html
        assert "Showing the first 1 of 216." in html

    def test_no_children_renders_no_container(self):
        """A recipient with no children renders no child container."""
        html = render_recipient_info(_profile(), {}, [], None)
        assert '<details class="children">' not in html

    def test_escapes_hostile_values(self):
        """Source text is escaped rather than injected as markup."""
        html = render_recipient_info(_profile(name="<script>alert(1)</script>"))
        assert "<script>alert" not in html
        assert "&lt;script&gt;alert" in html

    def test_absent_location_renders_no_section(self):
        """A recipient with no location renders no location section."""
        html = render_recipient_info(_profile(location={}))
        assert re.findall(r"<h2>([^<]+)</h2>", html) == ["Identity"]

    def test_empty_profile_renders_placeholder(self):
        """A profile with no fields renders the empty-state message."""
        html = render_recipient_info({})
        assert "No recipient detail was returned." in html
        assert "__" not in html

    def test_empty_top_categories_render_no_container(self):
        """Categories that all come back empty render no container."""
        html = render_recipient_info(_profile(), {"awarding_agency": []}, [], 100.0)
        assert '<details class="tops">' not in html


class TestRecipientRows:
    """Tests for the tabular flattening of a recipient profile."""

    def test_alternate_names_become_their_own_section(self):
        """Every alternate name is served as its own row under one section."""
        from openbb_government_us.treasury.utils.recipient_render import recipient_rows

        rows = recipient_rows(_profile(alternate_names=["LOCKHEED CORP", "LMT"]))
        alternates = [row for row in rows if row["section"] == "Alternate Names"]
        assert [row["name"] for row in alternates] == ["LOCKHEED CORP", "LMT"]
        assert all(row["value"] is None for row in alternates)

    def test_every_row_shares_one_column_set(self):
        """All sections emit the same keys so the raw view renders as a table."""
        from openbb_government_us.treasury.utils.recipient_render import recipient_rows

        rows = recipient_rows(
            _profile(alternate_names=["LMT"]),
            {"awarding_agency": [{"name": "DOD", "amount": 25.0}]},
            [_child()],
            100.0,
        )
        assert len({tuple(sorted(row)) for row in rows}) == 1
        sections = {row["section"] for row in rows}
        assert "Alternate Names" in sections
        assert "Child Recipients" in sections


class TestRecipientInfoEndpoint:
    """Tests for the recipient_info endpoint."""

    @staticmethod
    def _patch(monkeypatch, profile, children=None):
        """Patch every upstream call the endpoint makes."""

        async def _fake_get(path, **kwargs):
            return children or [] if "children" in path else profile

        async def _fake_post(path, payload, **kwargs):
            if "spending_over_time" in path:
                return {"results": [{"aggregated_amount": 100.0}]}
            return {"results": [{"name": "DOD", "amount": 50.0}]}

        monkeypatch.setattr(usaspending, "get_usaspending", _fake_get)
        monkeypatch.setattr(usaspending, "post_usaspending", _fake_post)

    def test_html_branch(self, monkeypatch):
        """Without raw, the endpoint returns the rendered profile page."""
        self._patch(monkeypatch, _profile(), [_child()])
        response = asyncio.run(recipient_info(RID))
        body = response.body.decode()
        assert response.media_type == "text/html"
        assert "LOCKHEED MARTIN CORP" in body
        assert '<details class="children">' in body

    def test_raw_branch_returns_tabular_records(self, monkeypatch):
        """With raw=True, the endpoint returns a flat list of records rather than a nested object."""
        self._patch(monkeypatch, _profile(), [_child()])
        response = asyncio.run(recipient_info(RID, raw=True))
        rows = json.loads(response.body.decode())
        assert response.media_type == "application/json"
        assert isinstance(rows, list)
        assert rows, "the raw view must return at least one record"

    def test_raw_records_share_one_column_set(self, monkeypatch):
        """Every record carries the same keys so the table renders squarely."""
        self._patch(monkeypatch, _profile(), [_child()])
        rows = json.loads(asyncio.run(recipient_info(RID, raw=True)).body.decode())
        columns = {tuple(sorted(row)) for row in rows}
        assert len(columns) == 1, f"ragged raw records: {columns}"
        assert "section" in rows[0]
        assert "name" in rows[0]

    def test_raw_covers_every_rendered_section(self, monkeypatch):
        """The raw view carries the same facts the page renders."""
        self._patch(monkeypatch, _profile(), [_child()])
        rows = json.loads(asyncio.run(recipient_info(RID, raw=True)).body.decode())
        sections = {row["section"] for row in rows}
        assert {"Identity", "Location", "Totals", "Child Recipients"} <= sections
        totals = [r for r in rows if r["section"] == "Totals"]
        assert any(r["amount"] == 63372229980.46 for r in totals)

    def test_children_skipped_for_a_non_parent(self, monkeypatch):
        """Only a parent recipient is asked for children."""
        self._patch(monkeypatch, _profile(recipient_level="R"), [_child()])
        body = asyncio.run(recipient_info(RID)).body.decode()
        assert '<details class="children">' not in body

    def test_rejects_a_year_below_the_floor(self, monkeypatch):
        """A digit year the source 503s on is rejected before the request."""
        self._patch(monkeypatch, _profile())
        with pytest.raises(OpenBBError, match="Invalid year"):
            asyncio.run(recipient_info(RID, year="1000"))

    def test_blank_year_falls_back_to_latest(self, monkeypatch):
        """A blank year becomes 'latest', never an empty value meaning all-time."""
        captured: dict = {}

        async def _fake_get(path, **kwargs):
            captured.setdefault("path", path)
            return _profile()

        async def _fake_post(path, payload, **kwargs):
            return {"results": [{"aggregated_amount": 1.0}]}

        monkeypatch.setattr(usaspending, "get_usaspending", _fake_get)
        monkeypatch.setattr(usaspending, "post_usaspending", _fake_post)
        asyncio.run(recipient_info(RID, year=""))
        assert captured["path"].endswith("?year=latest")

    def test_child_render_cap_is_disclosed(self, monkeypatch):
        """More children than the render cap are truncated and disclosed."""
        monkeypatch.setattr(treasury_router, "CHILD_RENDER_CAP", 2)
        self._patch(monkeypatch, _profile(), [_child(i) for i in range(5)])
        body = asyncio.run(recipient_info(RID)).body.decode()
        assert body.count('<details class="child">') == 2
        assert "Showing the first 2 of 5." in body

    def test_widget_declares_html_with_the_raw_toggle(self):
        """The registered route advertises an HTML widget with the raw toggle."""
        route = next(r for r in router.api_router.routes if r.path == "/recipient_info")
        config = route.openapi_extra["widget_config"]
        assert config["type"] == "html"
        assert config["raw"] is True
        assert config["widgetId"] == "ustreasury_recipient_info_us_treasury_obb"
        assert [p["paramName"] for p in config["params"]] == [
            "recipient_id",
            "year",
            "raw",
        ]
