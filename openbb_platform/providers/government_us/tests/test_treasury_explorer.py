"""Tests for the USAspending spending explorer model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.treasury.models.usaspending_explorer import (
    UsSpendingExplorerFetcher,
)
from openbb_government_us.treasury.utils import spending, usaspending

SUBMISSIONS = {
    "available_periods": [
        {"submission_fiscal_year": 2025, "submission_fiscal_month": 12},
        {"submission_fiscal_year": 2026, "submission_fiscal_month": 8},
        {"submission_fiscal_year": 2026, "submission_fiscal_month": 6},
    ]
}


def _response(**overrides) -> dict:
    """Build a spending response with overridable defaults."""
    payload = {
        "total": 254327502910.38,
        "end_date": "2026-05-31T00:00:00Z",
        "results": [
            {
                "amount": 175955142315.31,
                "type": "agency",
                "name": "Department of Defense",
                "code": "097",
                "id": "1173",
            },
            {
                "amount": 35608441608.03,
                "type": "agency",
                "name": "Department of Homeland Security",
                "code": "070",
                "id": "766",
            },
        ],
    }
    payload.update(overrides)
    return payload


def _capture(monkeypatch, response):
    """Patch the spending POST and the submission-period lookup."""
    captured: dict = {}

    async def _fake_post(path, payload, **kwargs):
        captured["path"] = path
        captured["payload"] = payload
        return response

    async def _fake_get(path, **kwargs):
        return SUBMISSIONS

    monkeypatch.setattr(usaspending, "post_usaspending", _fake_post)
    monkeypatch.setattr(usaspending, "get_usaspending", _fake_get)
    return captured


class TestPeriodOptions:
    """Tests for the reporting-period control."""

    def test_options_lead_with_latest(self):
        """The default option resolves to whatever the source has published."""
        options = spending.period_options()
        assert options[0] == {"label": "Latest available", "value": "latest"}

    def test_options_are_human_readable_and_string_valued(self):
        """Every option reads as a month and carries a string value."""
        options = spending.period_options()
        assert {"label": "Through March (Q2)", "value": "6"} in options
        assert {"label": "Through September (Q4)", "value": "12"} in options
        assert all(isinstance(o["value"], str) for o in options)

    def test_quarter_ends_are_marked(self):
        """The four quarter-closing periods are labelled as such."""
        marked = [v for v, label in spending.PERIOD_LABELS.items() if "(Q" in label]
        assert marked == ["3", "6", "9", "12"]

    def test_period_one_is_not_offered(self):
        """Period 1 is not separately reportable, so it is not offered."""
        assert "1" not in spending.PERIOD_LABELS


class TestLatestSubmission:
    """Tests for resolving the latest published period."""

    def test_resolves_the_newest_year_and_period(self, monkeypatch):
        """Without a year, the newest published year and period are used."""
        _capture(monkeypatch, _response())
        assert asyncio.run(spending.latest_submission()) == (2026, "8")

    def test_resolves_within_a_given_year(self, monkeypatch):
        """With a year, the newest period of that year is used."""
        _capture(monkeypatch, _response())
        assert asyncio.run(spending.latest_submission(2025)) == (2025, "12")

    def test_unpublished_year_raises(self, monkeypatch):
        """A year the source has not published raises rather than returning zero."""
        _capture(monkeypatch, _response())
        with pytest.raises(OpenBBError, match="No published submission period"):
            asyncio.run(spending.latest_submission(2030))


class TestParseScope:
    """Tests for the drill-token parser."""

    def test_no_token_is_not_a_scope(self):
        """No token means no scope rather than an error."""
        assert spending.parse_scope(None) is None

    def test_a_blank_token_is_not_a_scope(self):
        """Whitespace is treated the same as no token."""
        assert spending.parse_scope("   ") is None

    def test_a_valid_token_splits_into_dimension_and_id(self):
        """A well-formed token yields its dimension and id."""
        assert spending.parse_scope("agency:1173") == ("agency", "1173")

    def test_surrounding_whitespace_is_trimmed(self):
        """Padding around either half is stripped off."""
        assert spending.parse_scope("  federal_account : 4174 ") == (
            "federal_account",
            "4174",
        )

    def test_an_id_containing_a_colon_keeps_its_tail(self):
        """Only the first colon separates, so ids may contain colons."""
        assert spending.parse_scope("federal_account:017-1612:x") == (
            "federal_account",
            "017-1612:x",
        )

    def test_a_token_without_a_separator_raises(self):
        """A bare dimension name is rejected with the expected format."""
        with pytest.raises(OpenBBError, match="Invalid scope: 'agency'"):
            spending.parse_scope("agency")

    def test_a_token_with_an_empty_id_raises(self):
        """A dimension with no id behind the colon is rejected."""
        with pytest.raises(OpenBBError, match="Invalid scope: 'agency:'"):
            spending.parse_scope("agency:")

    def test_a_token_with_a_blank_id_raises(self):
        """Whitespace does not count as an id."""
        with pytest.raises(OpenBBError, match="must read '<dimension>:<id>'"):
            spending.parse_scope("agency:   ")

    def test_an_unknown_dimension_raises_and_lists_the_valid_ones(self):
        """A dimension the endpoint does not filter by is rejected by name."""
        with pytest.raises(
            OpenBBError, match="Invalid scope dimension: 'award_category'"
        ) as exc:
            spending.parse_scope("award_category:A")
        assert "budget_function" in str(exc.value)

    def test_every_scope_dimension_round_trips(self):
        """Each declared dimension is accepted by the parser."""
        for dimension in spending.SCOPE_DIMENSIONS:
            assert spending.parse_scope(f"{dimension}:1") == (dimension, "1")


class TestDimensionOptions:
    """Tests for the dimension-entry option lists."""

    @staticmethod
    def _patch(monkeypatch, results) -> dict:
        """Patch the spending POST and the submission lookup, recording the POST."""
        captured: dict = {}

        async def _fake_post(path, payload, **kwargs):
            captured["path"] = path
            captured["payload"] = payload
            return {"results": results}

        async def _fake_get(path, **kwargs):
            return SUBMISSIONS

        monkeypatch.setattr(usaspending, "post_usaspending", _fake_post)
        monkeypatch.setattr(usaspending, "get_usaspending", _fake_get)
        return captured

    def test_an_unsupported_dimension_returns_nothing(self, monkeypatch):
        """A dimension with no enumerable list returns an empty control."""
        self._patch(monkeypatch, [])
        assert asyncio.run(spending.dimension_options("recipient")) == []

    def test_an_unsupported_dimension_sends_no_request(self, monkeypatch):
        """The unsupported case short-circuits before any request is made."""
        captured = self._patch(monkeypatch, [{"id": "1", "name": "x"}])
        asyncio.run(spending.dimension_options("award"))
        assert captured == {}

    def test_options_pair_each_name_with_its_id(self, monkeypatch):
        """Each entry becomes a label of its name and a value of its id."""
        self._patch(
            monkeypatch,
            [{"id": 1173, "name": "Department of Defense"}],
        )
        assert asyncio.run(spending.dimension_options("agency")) == [
            {"label": "Department of Defense", "value": "1173"}
        ]

    def test_options_are_sorted_by_label(self, monkeypatch):
        """The control lists entries alphabetically, not in source order."""
        self._patch(
            monkeypatch,
            [
                {"id": "1", "name": "Veterans Affairs"},
                {"id": "2", "name": "Agriculture"},
                {"id": "3", "name": "Commerce"},
            ],
        )
        options = asyncio.run(spending.dimension_options("agency"))
        assert [option["label"] for option in options] == [
            "Agriculture",
            "Commerce",
            "Veterans Affairs",
        ]

    def test_unidentified_and_unnamed_rows_are_dropped(self, monkeypatch):
        """A row with no id or no name cannot be selected, so it is not offered."""
        self._patch(
            monkeypatch,
            [
                {"id": None, "name": "Unreported Data"},
                {"id": "9", "name": ""},
                {"id": "4174", "name": "National Sea-Based Deterrence Fund"},
            ],
        )
        assert asyncio.run(spending.dimension_options("federal_account")) == [
            {"label": "National Sea-Based Deterrence Fund", "value": "4174"}
        ]

    def test_a_zero_id_is_kept(self, monkeypatch):
        """An id of zero is a real id, not a missing one."""
        self._patch(monkeypatch, [{"id": 0, "name": "Unclassified"}])
        assert asyncio.run(spending.dimension_options("object_class")) == [
            {"label": "Unclassified", "value": "0"}
        ]

    def test_a_null_results_block_yields_no_options(self, monkeypatch):
        """A response carrying no results returns an empty control."""
        self._patch(monkeypatch, None)
        assert asyncio.run(spending.dimension_options("agency")) == []

    def test_the_request_uses_the_latest_published_period(self, monkeypatch):
        """The list is drawn from the newest published fiscal year and period."""
        captured = self._patch(monkeypatch, [])
        asyncio.run(spending.dimension_options("object_class"))
        assert captured["path"] == "spending/"
        assert captured["payload"] == {
            "type": "object_class",
            "filters": {"fy": "2026", "period": "8"},
        }

    def test_an_agency_narrows_the_request(self, monkeypatch):
        """An agency is sent as a filter so the list stays practical."""
        captured = self._patch(monkeypatch, [])
        asyncio.run(spending.dimension_options("federal_account", agency="1173"))
        assert captured["payload"]["filters"] == {
            "fy": "2026",
            "period": "8",
            "agency": "1173",
        }

    def test_a_blank_agency_is_not_sent(self, monkeypatch):
        """An empty agency leaves the request government-wide."""
        captured = self._patch(monkeypatch, [])
        asyncio.run(spending.dimension_options("agency", agency=""))
        assert "agency" not in captured["payload"]["filters"]


class TestAwardingAgencyOptions:
    """Tests for the awarding-agency option list."""

    @staticmethod
    def _patch(monkeypatch, results) -> dict:
        """Patch the references GET, recording the path it is called with."""
        captured: dict = {}

        async def _fake_get(path, **kwargs):
            captured["path"] = path
            captured["kwargs"] = kwargs
            return {"results": results}

        monkeypatch.setattr(usaspending, "get_usaspending", _fake_get)
        return captured

    def test_options_use_the_agency_name_for_both_halves(self, monkeypatch):
        """The endpoint filters by name, so the value is the name too."""
        self._patch(monkeypatch, [{"agency_name": "Department of Defense"}])
        assert asyncio.run(spending.awarding_agency_options()) == [
            {
                "label": "Department of Defense",
                "value": "Department of Defense",
            }
        ]

    def test_options_are_sorted_by_name(self, monkeypatch):
        """The control lists agencies alphabetically."""
        self._patch(
            monkeypatch,
            [
                {"agency_name": "Department of the Treasury"},
                {"agency_name": "Department of Agriculture"},
            ],
        )
        options = asyncio.run(spending.awarding_agency_options())
        assert [option["label"] for option in options] == [
            "Department of Agriculture",
            "Department of the Treasury",
        ]

    def test_unnamed_agencies_are_dropped(self, monkeypatch):
        """A row with no name cannot be selected, so it is not offered."""
        self._patch(
            monkeypatch,
            [
                {"agency_name": ""},
                {"agency_name": None},
                {"agency_name": "Department of Energy"},
            ],
        )
        assert asyncio.run(spending.awarding_agency_options()) == [
            {"label": "Department of Energy", "value": "Department of Energy"}
        ]

    def test_a_null_results_block_yields_no_options(self, monkeypatch):
        """A response carrying no results returns an empty control."""
        self._patch(monkeypatch, None)
        assert asyncio.run(spending.awarding_agency_options()) == []

    def test_it_reads_the_toptier_agencies_reference(self, monkeypatch):
        """The list comes from the top-tier agency reference endpoint."""
        captured = self._patch(monkeypatch, [])
        asyncio.run(spending.awarding_agency_options())
        assert captured["path"] == "references/toptier_agencies/"
        assert captured["kwargs"]["timeout"] == 90


class TestUsSpendingExplorerQueryParams:
    """Tests for the explorer query params."""

    def test_defaults(self):
        """The default breakdown is an entry point at the latest period."""
        query = UsSpendingExplorerFetcher.transform_query({})
        assert query.explorer_type == "object_class"
        assert query.period == "latest"
        assert query.fiscal_year is None

    def test_rejects_a_scope_only_breakdown_without_a_scope(self):
        """A breakdown too large to enumerate government-wide needs a scope."""
        for explorer_type in (
            "recipient",
            "award",
            "award_category",
            "program_activity",
        ):
            with pytest.raises(OpenBBError, match="too large to return"):
                UsSpendingExplorerFetcher.transform_query(
                    {"explorer_type": explorer_type}
                )

    def test_every_standalone_breakdown_is_accepted(self):
        """The dimensions that work government-wide need no scope.

        Each was verified against the live source rather than taken from the
        contract doc, which names only three entry points.
        """
        for explorer_type in (
            "object_class",
            "budget_function",
            "budget_subfunction",
            "agency",
            "federal_account",
        ):
            query = UsSpendingExplorerFetcher.transform_query(
                {"explorer_type": explorer_type}
            )
            assert query.explorer_type == explorer_type

    def test_an_explicit_filter_unlocks_a_detail_breakdown(self):
        """An explicit scoping filter also counts."""
        query = UsSpendingExplorerFetcher.transform_query(
            {"explorer_type": "federal_account", "object_class": "30"}
        )
        assert query.explorer_type == "federal_account"


class TestUsSpendingExplorerFetcher:
    """Tests for the explorer fetcher."""

    def test_latest_resolves_year_and_period(self, monkeypatch):
        """The default resolves to the newest published year and period."""
        captured = _capture(monkeypatch, _response())
        query = UsSpendingExplorerFetcher.transform_query({})
        asyncio.run(UsSpendingExplorerFetcher.aextract_data(query, None))
        assert captured["payload"]["filters"] == {"fy": "2026", "period": "8"}

    def test_an_explicit_period_is_kept(self, monkeypatch):
        """A chosen period is sent as-is."""
        captured = _capture(monkeypatch, _response())
        query = UsSpendingExplorerFetcher.transform_query(
            {"fiscal_year": 2024, "period": "6"}
        )
        asyncio.run(UsSpendingExplorerFetcher.aextract_data(query, None))
        assert captured["payload"]["filters"] == {"fy": "2024", "period": "6"}

    def test_latest_within_an_explicit_year(self, monkeypatch):
        """A year with 'latest' resolves that year's newest period."""
        captured = _capture(monkeypatch, _response())
        query = UsSpendingExplorerFetcher.transform_query({"fiscal_year": 2025})
        asyncio.run(UsSpendingExplorerFetcher.aextract_data(query, None))
        assert captured["payload"]["filters"] == {"fy": "2025", "period": "12"}

    def test_scoping_filters_stack(self, monkeypatch):
        """Several scoping filters combine into one request."""
        captured = _capture(monkeypatch, _response())
        query = UsSpendingExplorerFetcher.transform_query(
            {
                "explorer_type": "federal_account",
                "agency": "1173",
                "object_class": "30",
            }
        )
        asyncio.run(UsSpendingExplorerFetcher.aextract_data(query, None))
        filters = captured["payload"]["filters"]
        assert filters["agency"] == "1173"
        assert filters["object_class"] == "30"

    def test_no_param_is_both_emitted_and_filtered(self):
        """No column emits into a param the endpoint filters by.

        Emitting into a filter collapses the table to the clicked row.
        """
        from openbb_government_us.treasury.models.usaspending_explorer import (
            UsSpendingExplorerData,
            UsSpendingExplorerQueryParams,
        )

        emitted = {
            ((field.json_schema_extra or {}).get("x-widget_config") or {})
            .get("renderFnParams", {})
            .get("groupByParamName")
            for field in UsSpendingExplorerData.model_fields.values()
        } - {None}
        assert not emitted & set(UsSpendingExplorerQueryParams.model_fields)

    def test_extract_empty_raises(self, monkeypatch):
        """A breakdown with no rows raises EmptyDataError."""
        _capture(monkeypatch, _response(results=[], total=None))
        query = UsSpendingExplorerFetcher.transform_query({})
        with pytest.raises(EmptyDataError, match="No 'object_class' spending"):
            asyncio.run(UsSpendingExplorerFetcher.aextract_data(query, None))

    def test_transform_carries_each_entry_id(self):
        """Each row carries the id its matching scope filter accepts."""
        query = UsSpendingExplorerFetcher.transform_query(
            {"explorer_type": "agency", "object_class": "30"}
        )
        rows = UsSpendingExplorerFetcher.transform_data(query, _response())
        assert rows[0].explorer_id == "1173"
        assert rows[1].explorer_id == "766"

    def test_transform_derives_the_share_of_total(self):
        """Each row's share is derived from the response total."""
        query = UsSpendingExplorerFetcher.transform_query({})
        rows = UsSpendingExplorerFetcher.transform_data(query, _response())
        assert rows[0].percent_of_total == pytest.approx(69.18, abs=0.01)

    def test_transform_keeps_the_as_of_date(self):
        """The response's as-of date is carried onto every row, date only."""
        query = UsSpendingExplorerFetcher.transform_query({})
        rows = UsSpendingExplorerFetcher.transform_data(query, _response())
        assert all(row.as_of_date == "2026-05-31" for row in rows)

    def test_transform_carries_the_account_number(self):
        """A federal-account breakdown keeps its account symbol."""
        query = UsSpendingExplorerFetcher.transform_query(
            {"explorer_type": "federal_account", "agency": "1173"}
        )
        rows = UsSpendingExplorerFetcher.transform_data(
            query,
            _response(
                results=[
                    {
                        "amount": 30834298487.99,
                        "id": "4174",
                        "account_number": "017-1612",
                        "type": "federal_account",
                        "name": "National Sea-Based Deterrence Fund, Navy",
                        "code": "017-1612",
                    }
                ]
            ),
        )
        assert rows[0].account_number == "017-1612"
        assert rows[0].explorer_id == "4174"

    def test_transform_handles_an_unreported_row(self):
        """A row with no id renders with no drill token rather than a broken one."""
        query = UsSpendingExplorerFetcher.transform_query({})
        rows = UsSpendingExplorerFetcher.transform_data(
            query,
            _response(
                results=[
                    {
                        "amount": -270920000000.0,
                        "id": None,
                        "code": None,
                        "type": "object_class",
                        "name": "Unreported Data",
                    }
                ]
            ),
        )
        assert rows[0].name == "Unreported Data"
        assert rows[0].explorer_id is None

    def test_transform_without_a_total_omits_the_share(self):
        """No total yields no derived share rather than a wrong one."""
        query = UsSpendingExplorerFetcher.transform_query({})
        rows = UsSpendingExplorerFetcher.transform_data(query, _response(total=None))
        assert all(row.percent_of_total is None for row in rows)


class TestOfferedBreakdownsAllWork:
    """Every option the control offers must load, in every scope state."""

    @staticmethod
    def _offered(scoped: bool) -> list[str]:
        """Return the breakdown values offered for a scope state."""
        return [option["value"] for option in spending.explorer_type_options(scoped)]

    def test_unscoped_offers_only_standalone_breakdowns(self):
        """With no scope, only the breakdowns that stand alone are offered.

        The four that need a scope would 400, so the control must not list
        them until a scope narrows them.
        """
        offered = set(self._offered(scoped=False))
        assert offered == set(spending.STANDALONE_TYPES)
        assert not offered & set(spending.SCOPE_ONLY_TYPES)

    def test_scoped_offers_every_breakdown(self):
        """Once a scope is set, every breakdown becomes reachable."""
        offered = set(self._offered(scoped=True))
        assert offered == set(spending.STANDALONE_TYPES) | set(
            spending.SCOPE_ONLY_TYPES
        )

    def test_every_unscoped_option_passes_validation(self):
        """No offered option is rejected by the query validator."""
        for explorer_type in self._offered(scoped=False):
            query = UsSpendingExplorerFetcher.transform_query(
                {"explorer_type": explorer_type}
            )
            assert query.explorer_type == explorer_type

    def test_every_scoped_option_passes_validation(self):
        """No offered option is rejected once a scope is present."""
        for explorer_type in self._offered(scoped=True):
            query = UsSpendingExplorerFetcher.transform_query(
                {"explorer_type": explorer_type, "agency": "1173"}
            )
            assert query.explorer_type == explorer_type

    def test_options_carry_human_labels(self):
        """The control reads as words, not as raw API tokens."""
        options = spending.explorer_type_options(scoped=True)
        assert {"label": "Object Class", "value": "object_class"} in options
        assert {"label": "Award Category", "value": "award_category"} in options
        assert all(option["label"] != option["value"] for option in options)

    def test_every_literal_value_is_offered_when_scoped(self):
        """No declared breakdown is unreachable through the control."""
        from typing import get_args

        from openbb_government_us.treasury.models.usaspending_explorer import (
            ExplorerType,
        )

        assert set(get_args(ExplorerType)) == set(self._offered(scoped=True))


class TestSelfScopeIsIgnored:
    """Breaking down by a dimension means showing every entry of it."""

    def test_a_scope_on_the_breakdown_dimension_is_dropped(self, monkeypatch):
        """Scoping a breakdown by its own dimension would collapse it to one row."""
        captured = _capture(monkeypatch, _response())
        query = UsSpendingExplorerFetcher.transform_query(
            {"explorer_type": "budget_function", "budget_function": "350"}
        )
        asyncio.run(UsSpendingExplorerFetcher.aextract_data(query, None))
        assert "budget_function" not in captured["payload"]["filters"]

    def test_other_scopes_survive(self, monkeypatch):
        """A scope on a different dimension is still applied."""
        captured = _capture(monkeypatch, _response())
        query = UsSpendingExplorerFetcher.transform_query(
            {"explorer_type": "agency", "agency": "1173", "object_class": "30"}
        )
        asyncio.run(UsSpendingExplorerFetcher.aextract_data(query, None))
        filters = captured["payload"]["filters"]
        assert "agency" not in filters
        assert filters["object_class"] == "30"

    def test_a_self_scope_does_not_satisfy_the_scope_requirement(self):
        """A scope-only breakdown still needs a scope on a DIFFERENT dimension."""
        with pytest.raises(OpenBBError, match="too large to return"):
            UsSpendingExplorerFetcher.transform_query(
                {"explorer_type": "recipient", "recipient": "abc"}
            )

    def test_a_cross_dimension_scope_satisfies_it(self):
        """A scope on another dimension does unlock a scope-only breakdown."""
        query = UsSpendingExplorerFetcher.transform_query(
            {"explorer_type": "recipient", "agency": "1173"}
        )
        assert query.explorer_type == "recipient"
