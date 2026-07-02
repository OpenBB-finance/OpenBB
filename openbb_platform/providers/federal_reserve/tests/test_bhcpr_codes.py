"""Tests for the BHCPR schema-item to CSV-code binder."""

from openbb_federal_reserve.utils import bhcpr_codes
from openbb_federal_reserve.utils.bhcpr_codes import (
    _align,
    _close,
    _description_sim,
    _infer_basis,
    _insurance_bind,
    _items_with_context,
    _loan_type,
    _matrix_bind,
    _numeric_id,
    _parent_bind,
    _parent_entity,
    _pastdue_bind,
    _pastdue_bucket,
    _pastdue_sig,
    _period_dates,
    _prefix,
    _printed_values,
    _scope,
    _sec_block,
    _secblock_bind,
    _secblock_sig,
    _securitization_sig,
    _series,
    _value_code,
    bind_codes,
)


class TestCodeHelpers:
    """Tests for the code-shape helpers."""

    def test_prefix_and_numeric_id(self):
        """A code splits into its alphabetic prefix and numeric id."""
        assert _prefix("BHSR028") == "BHSR"
        assert _numeric_id("BHSR028") == "028"

    def test_malformed_code_yields_empty(self):
        """A code that does not match the shape yields empty parts."""
        assert _prefix("???") == ""
        assert _numeric_id("???") == ""


class TestDimensionHelpers:
    """Tests for the caption-dimension helpers."""

    def test_loan_type(self):
        """A loan-type caption maps to its dimension tag."""
        assert _loan_type("credit card receivables") == "credit_card"
        assert _loan_type("total") is None

    def test_pastdue_bucket(self):
        """Past-due and status captions map to their bucket."""
        assert _pastdue_bucket("30-89 days past due") == "30_89"
        assert _pastdue_bucket("90+ days past due") == "90_over"
        assert _pastdue_bucket("net loss") == "net_loss"
        assert _pastdue_bucket("nonaccrual") == "nonaccrual"
        assert _pastdue_bucket("current") is None

    def test_scope(self):
        """The securitized/managed scope is read from a caption."""
        assert _scope("securitized loans") == "securitized"
        assert _scope("managed assets") == "managed"
        assert _scope("held for sale") is None

    def test_sec_block(self):
        """A securitization block is read from a caption."""
        assert _sec_block("seller's interest carried") == "seller"
        assert _sec_block("retained credit exposure of x") == "retained"
        assert _sec_block("securitization activities") == "outstanding"
        assert _sec_block("something else") is None

    def test_parent_entity(self):
        """The subsidiary entity is read from a caption."""
        assert _parent_entity("Investment in Nonbank Subsidiaries") == "nonbank"
        assert _parent_entity("Investment in Bank Subsidiaries") == "bank"
        assert _parent_entity("Subsidiary Holding Companies") == "bhcs"
        assert _parent_entity("Cash") is None


class TestClose:
    """Tests for ``_close`` value equality."""

    def test_exact_and_scaled(self):
        """A printed value matches its coded value directly or scaled x1000."""
        assert _close(2.15, 2.15) is True
        assert _close(4900475000000, 4900475000) is True

    def test_mismatch(self):
        """A mismatched pair is not close."""
        assert _close(100, 200) is False


class TestInferBasis:
    """Tests for ``_infer_basis`` from a bound code."""

    _DESC = {
        "BHSR028": "NET INTEREST INCOME / AVERAGE ASSETS",
        "BHCK2170": "TOTAL ASSETS (BHC CONSOLIDATED)",
        "BHSR1069": "SECURITIZED HOME EQUITY LINES/CONSOLIDATED ASSETS",
        "BHSR561": "TIER 1 LEVERAGE RATIO",
        "BHCK9999": "NUMBER OF SUBSIDIARIES",
    }

    def test_spaced_ratio_is_percent(self):
        """A spaced ``x / y`` description is a percent."""
        assert _infer_basis("NII", "BHSR028", self._DESC, set()) == "Percent"

    def test_unspaced_ratio_is_percent(self):
        """A slash without spaces still marks a ratio percent."""
        assert _infer_basis("Home Equity", "BHSR1069", self._DESC, set()) == "Percent"

    def test_ranked_code_is_percent(self):
        """A code carrying a percentile rank is a percent."""
        assert _infer_basis("Tier 1", "BHSR561", self._DESC, {"561"}) == "Percent"

    def test_dollar_default(self):
        """A plain non-ratio description is a dollar amount."""
        assert _infer_basis("Total Assets", "BHCK2170", self._DESC, set()) == (
            "Dollar Amount in Thousands"
        )

    def test_multiple_label(self):
        """A ``(X)`` label is a multiple regardless of description."""
        assert _infer_basis("Leverage (X)", "BHCK2170", self._DESC, set()) == (
            "Multiple (X)"
        )

    def test_number_label(self):
        """A count label is a number."""
        assert _infer_basis("Number of Subs", "BHCK9999", self._DESC, set()) == "Number"


class TestDescriptionSim:
    """Tests for ``_description_sim``."""

    def test_containment_boost(self):
        """A caption contained in a description scores at least the boost."""
        assert (
            _description_sim("Total Assets", "TOTAL ASSETS (BHC CONSOLIDATED)") >= 0.75
        )

    def test_empty_is_zero(self):
        """An empty caption or description scores zero."""
        assert _description_sim("", "anything") == 0.0


class TestSeries:
    """Tests for the value-series helpers."""

    _CSV = {
        "periods": {"": "20260331", "_4Q": "20250331", "bad": "20"},
        "values": {
            "BHCK2170": {"": 100, "_4Q": 90},
            "BHSR028": {"": 2.0, "_4Q": None},
            "PHSR028": {"": 3.0},
            "RKSR028": {"": 11},
        },
    }

    def test_period_dates_drops_malformed(self):
        """Only eight-digit period dates are converted to ISO."""
        dates = _period_dates(self._CSV)
        assert dates == {"": "2026-03-31", "_4Q": "2025-03-31"}

    def test_series_splits_primary_peer_pct(self):
        """``_series`` splits primary, peer, and percentile series by ISO date."""
        primary, peer, pct = _series(self._CSV)
        assert primary["BHCK2170"] == {"2026-03-31": 100, "2025-03-31": 90}
        assert primary["BHSR028"] == {"2026-03-31": 2.0}
        assert peer["028"] == {"2026-03-31": 3.0}
        assert pct["028"] == {"2026-03-31": 11}


class TestValueCode:
    """Tests for ``_value_code`` fingerprint matching."""

    _PRIMARY = {"BHCK2170": {"2026-03-31": 100, "2025-03-31": 90}}

    def test_matches_scaled_amount_fingerprint(self):
        """A printed dollar row matches its x1000 coded fingerprint."""
        row = {
            "periods": {
                "2026-03-31": {"amount": 100000},
                "2025-03-31": {"amount": 90000},
            }
        }
        assert _value_code(row, self._PRIMARY, {}, {}, set()) == "BHCK2170"

    def test_single_cell_row_is_unbound(self):
        """A row with fewer than two values is never bound."""
        row = {"periods": {"2026-03-31": {"amount": 100000}}}
        assert _value_code(row, self._PRIMARY, {}, {}, set()) is None

    def test_all_zero_row_is_unbound(self):
        """An all-zero fingerprint is not a confident binding."""
        primary = {"BHZZ001": {"2026-03-31": 0, "2025-03-31": 0}}
        row = {"periods": {"2026-03-31": {"amount": 0}, "2025-03-31": {"amount": 0}}}
        assert _value_code(row, primary, {}, {}, set()) is None

    def test_printed_values_collapse_amount_to_bhc(self):
        """Amount and BHC sub-columns collapse to ``bhc``; peer/pct keep their key."""
        row = {"periods": {"2026-03-31": {"amount": 5, "peer": 3, "pct": 90}}}
        printed = _printed_values(row)
        assert printed[("bhc", "2026-03-31")] == 5
        assert printed[("peer", "2026-03-31")] == 3
        assert printed[("pct", "2026-03-31")] == 90


class TestSecuritizationMatrix:
    """Tests for the securitization matrix signature and binding."""

    def test_matrix_binds_by_dimension_join(self):
        """A securitized past-due percent row binds to its exact-dimension code."""
        descriptions = {
            "BHSR1123": "SECURITIZED 1-4 FAMILY RES LOANS: 30-89 DAYS PAST DUE PERCENT"
        }
        sig = _securitization_sig(descriptions)
        items = [
            (
                {"label": "1-4 Family Residential Loans"},
                "30-89 Days Past Due Securitized Assets as a Percent of Type",
            )
        ]
        assert _matrix_bind(items, True, sig, set()) == {0: "BHSR1123"}

    def test_secblock_binds_outstanding_by_block_and_loan(self):
        """A securitization-activities row binds by (block, loan type)."""
        descriptions = {
            "BHCKB705": "OUTSTANDING PRINCIPLE BAL. OF 1-4 FAMILY RESIDENTIAL LOANS"
        }
        sig = _secblock_sig(descriptions)
        items = [
            ({"label": "1-4 Family Residential Loans"}, "Securitization Activities")
        ]
        assert _secblock_bind(items, sig, set()) == {0: "BHCKB705"}


class TestPastDueMatrix:
    """Tests for the past-due-by-loan-type matrix."""

    def test_pastdue_binds_loan_type_ratio(self):
        """A loan-type past-due row binds to its ``x / that loan`` ratio code."""
        descriptions = {"BHSR264": "C&I LOANS 90+ DAYS PAST DUE / C&I LOANS"}
        sig = _pastdue_sig(descriptions)
        items = [
            (
                {"label": "Commercial and Industrial Loans—90 Days and Over Past Due"},
                "",
            )
        ]
        assert _pastdue_bind(items, sig, set()) == {0: "BHSR264"}


class TestParentBind:
    """Tests for the parent-company balance-sheet binder."""

    def test_exact_caption_binds_parent_code(self):
        """An exact parent caption binds its ``BHCP`` code."""
        descriptions = {"BHCP2170": "TOTAL ASSETS (BHC PARENT-ONLY)"}
        items = [({"label": "Total Assets"}, "Assets")]
        assert _parent_bind(items, descriptions) == {0: "BHCP2170"}


class TestInsuranceBind:
    """Tests for the insurance concept binder."""

    def test_binds_separate_account_assets(self):
        """A life/health separate-account row binds its consolidated dollar code."""
        descriptions = {
            "BHCKB992": "LIFE & HEALTH ASSETS - SEPARATE ACCOUNT ASSETS (BHC CONSOLIDATED)"
        }
        items = [({"label": "Separate Account Assets (L/H)"}, "")]
        assert _insurance_bind(items, descriptions, set()) == {0: "BHCKB992"}


class TestAlign:
    """Tests for ``_align`` item-to-row alignment."""

    def test_positional_when_labels_match_in_order(self):
        """Equal-length, same-order captions align positionally."""
        items = [({"label": "Net Income"}, ""), ({"label": "Total Assets"}, "")]
        rows = [{"label": "Net Income"}, {"label": "Total Assets"}]
        assert _align(items, rows) == {0: 0, 1: 1}

    def test_monotonic_when_counts_differ(self):
        """Unequal counts align by order-preserving best similarity."""
        items = [({"label": "Total Assets"}, "")]
        rows = [{"label": "Cash"}, {"label": "Total Assets"}]
        assert _align(items, rows) == {0: 1}


class TestItemsWithContext:
    """Tests for ``_items_with_context``."""

    def test_pairs_items_with_nearest_subheader(self):
        """Each item is paired with its nearest preceding sub-header."""
        entry = {
            "entries": [
                {"kind": "subheader", "label": "Earnings"},
                {"kind": "item", "label": "Net Income"},
            ]
        }
        assert _items_with_context(entry) == [
            ({"kind": "item", "label": "Net Income"}, "Earnings")
        ]


class TestBindCodes:
    """Tests for ``bind_codes`` over small synthetic filings."""

    _CSV = {
        "periods": {"": "20260331", "_4Q": "20250331"},
        "values": {
            "BHCK2170": {"": 100, "_4Q": 90},
            "BHZZ999": {"": 7, "_4Q": 7},
        },
        # BHCK2170 carries no description here, so only the curated override (not a
        # description match) can reach the "Total Assets" row.
        "descriptions": {"BHZZ999": "SOME UNRELATED METRIC"},
    }

    def _schema(self):
        """A minimal schema whose sections trigger curated, value, and blank paths."""
        return [
            {
                "section": "Assets",
                "entries": [
                    {"kind": "item", "label": "Total Assets", "level": 0},
                    {"kind": "item", "label": "Nonexistent Line", "level": 0},
                ],
            },
            {
                "section": "Zeta",
                "entries": [{"kind": "item", "label": "Mystery", "level": 0}],
            },
        ]

    def test_curated_override_wins(self):
        """A curated override binds its exact section/label with a completed basis."""
        schema = self._schema()
        report = bind_codes(schema, [({}, self._CSV)])
        total = schema[0]["entries"][0]
        assert total["code"] == "BHCK2170"
        assert total["code_source"] == "curated"
        assert total["basis"] == "Dollar Amount in Thousands"
        assert report["counts"]["curated"] == 1

    def test_value_binding_from_pdf_row(self):
        """A printed PDF row's fingerprint binds its code in a non-curated section."""
        pdf = {
            "Zeta": [
                {
                    "label": "Mystery",
                    "periods": {
                        "2026-03-31": {"amount": 100000},
                        "2025-03-31": {"amount": 90000},
                    },
                }
            ]
        }
        schema = self._schema()
        bind_codes(schema, [(pdf, self._CSV)])
        mystery = schema[1]["entries"][0]
        assert mystery["code"] == "BHCK2170"
        assert mystery["code_source"] == "value"

    def test_unbound_row_is_null(self):
        """A row that no signal can reach is left unbound and counted."""
        schema = self._schema()
        report = bind_codes(schema, [({}, self._CSV)])
        blank = schema[0]["entries"][1]
        assert blank["code"] is None
        assert blank["code_source"] is None
        assert report["counts"]["unbound"] >= 1

    def test_module_has_overrides(self):
        """The curated override table is a non-empty mapping keyed by triples."""
        assert bhcpr_codes._OVERRIDES
        assert all(len(key) == 3 for key in bhcpr_codes._OVERRIDES)


class TestBinderBranches:
    """Tests for the guard and edge branches of the individual binders."""

    def test_pastdue_sig_skips_derived_non_ratio_and_securitized(self):
        """Derived, slash-less, and securitized/managed descriptions are not indexed."""
        sig = _pastdue_sig(
            {
                "BHSR264": "C&I LOANS 90+ DAYS PAST DUE / C&I LOANS",
                "BHSR900": "NO SLASH HERE",
                "RKSR264": "PG RANK: X / Y",
                "BHSR777": "SECURITIZED CREDIT CARD 30-89 PAST DUE / MANAGED CARD",
            }
        )
        assert sig == {("c_i", "90_over"): "BHSR264"}

    def test_pastdue_bind_skips_non_loan_row(self):
        """A row with no loan type or bucket binds nothing."""
        assert _pastdue_bind([({"label": "Some Total"}, "")], {}, set()) == {}

    def test_matrix_bind_skips_loanless_non_total(self):
        """A dimensioned row with neither a loan type nor a total binds nothing."""
        sig = _securitization_sig(
            {"BHSR1123": "SECURITIZED 1-4 FAMILY: 30-89 DAYS PAST DUE PERCENT"}
        )
        items = [({"label": "Miscellaneous"}, "30-89 Days Past Due Securitized Assets")]
        assert _matrix_bind(items, True, sig, set()) == {}

    def test_secblock_bind_skips_loanless_row(self):
        """A securitization block row with no loan type binds nothing."""
        sig = _secblock_sig(
            {"BHCKB705": "OUTSTANDING PRINCIPLE BAL. OF 1-4 FAMILY RESIDENTIAL LOANS"}
        )
        items = [({"label": "Total"}, "Securitization Activities")]
        assert _secblock_bind(items, sig, set()) == {}

    def test_value_code_tie_is_unbound(self):
        """Two codes matching a row with equal agreement leave it unbound."""
        primary = {
            "BHCK1": {"2026-03-31": 100, "2025-03-31": 90},
            "BHCK2": {"2026-03-31": 100, "2025-03-31": 90},
        }
        row = {
            "periods": {
                "2026-03-31": {"amount": 100000},
                "2025-03-31": {"amount": 90000},
            }
        }
        assert _value_code(row, primary, {}, {}, set()) is None

    def test_parent_bind_carries_entity_into_pass_two(self):
        """A running entity from an investment line drives a fuzzy pass-2 match."""
        descriptions = {"BHCP0010": "CASH AND DUE FROM NONBANK SUBSIDIARIES"}
        items = [
            ({"label": "Investment in Nonbank Subsidiaries"}, "Assets"),
            ({"label": "Cash and Due"}, "Assets"),
        ]
        assert _parent_bind(items, descriptions) == {1: "BHCP0010"}

    def test_securitization_sig_skips_derived(self):
        """A derived-prefix securitization code is not indexed."""
        sig = _securitization_sig(
            {
                "BHSR1123": "SECURITIZED 1-4 FAMILY RES LOANS: 30-89 DAYS PAST DUE PERCENT",
                "RKSR1123": "PG RANK: SECURITIZED 1-4 FAMILY 30-89 DAYS PAST DUE PERCENT",
            }
        )
        assert set(sig.values()) == {"BHSR1123"}

    def test_matrix_bind_skips_dimensionless_row(self):
        """A row lacking a past-due bucket or scope binds nothing."""
        assert (
            _matrix_bind([({"label": "Random"}, "No Context")], False, {}, set()) == {}
        )

    def test_secblock_bind_skips_percent_context(self):
        """A percent-context securitization row is left to value binding."""
        sig = _secblock_sig(
            {"BHCKB705": "OUTSTANDING PRINCIPLE BAL. OF 1-4 FAMILY RESIDENTIAL LOANS"}
        )
        items = [({"label": "1-4 Family Residential Loans"}, "Percent of Type")]
        assert _secblock_bind(items, sig, set()) == {}

    def test_value_code_skips_used_code(self):
        """A code already used yields no match."""
        primary = {"BHCK2170": {"2026-03-31": 100, "2025-03-31": 90}}
        row = {
            "periods": {
                "2026-03-31": {"amount": 100000},
                "2025-03-31": {"amount": 90000},
            }
        }
        assert _value_code(row, primary, {}, {}, {"BHCK2170"}) is None

    def test_value_code_ignores_absent_fingerprint_cell(self):
        """A printed cell with no matching fingerprint key is ignored, not fatal."""
        primary = {"BHCK2170": {"2026-03-31": 100, "2025-03-31": 90}}
        row = {
            "periods": {
                "2026-03-31": {"amount": 100000, "peer": 50},
                "2025-03-31": {"amount": 90000},
            }
        }
        assert _value_code(row, primary, {}, {}, set()) == "BHCK2170"

    def test_align_positional_with_unmatched_item(self):
        """Equal counts stay positional when one item has no exact row match."""
        items = [({"label": "Foo"}, ""), ({"label": "Nomatch"}, "")]
        rows = [{"label": "Foo"}, {"label": "Other"}]
        assert _align(items, rows) == {0: 0, 1: 1}

    def test_align_falls_back_to_monotonic_on_disorder(self):
        """Equal counts in the wrong order abandon the positional alignment."""
        items = [({"label": "Bar"}, ""), ({"label": "Foo"}, "")]
        rows = [{"label": "Foo"}, {"label": "Bar"}]
        assert _align(items, rows) != {0: 0, 1: 1}

    def test_align_monotonic_drops_extra_item(self):
        """An item with no matching row is dropped from the monotonic alignment."""
        items = [({"label": "Total Assets"}, ""), ({"label": "Zzz Qqq"}, "")]
        rows = [{"label": "Total Assets"}]
        assert _align(items, rows) == {0: 0}

    def test_align_monotonic_skips_intervening_row(self):
        """A monotonic alignment can skip a non-matching row between matches."""
        items = [({"label": "Total Assets"}, ""), ({"label": "Net Income"}, "")]
        rows = [
            {"label": "Total Assets"},
            {"label": "Unrelated Middle"},
            {"label": "Net Income"},
        ]
        assert _align(items, rows) == {0: 0, 1: 2}

    def test_insurance_bind_skips_non_concept_row(self):
        """A row matching no insurance concept binds nothing."""
        assert _insurance_bind([({"label": "Random Row"}, "")], {}, set()) == {}

    def test_insurance_bind_skips_missing_business_line(self):
        """A concept row without a business line marker binds nothing."""
        descriptions = {
            "BHCKB992": "LIFE & HEALTH ASSETS - SEPARATE ACCOUNT ASSETS (BHC CONSOLIDATED)"
        }
        items = [({"label": "Separate Account Assets"}, "")]
        assert _insurance_bind(items, descriptions, set()) == {}


class TestBindCodesOrchestration:
    """Tests for ``bind_codes`` section-specific wiring and fallbacks."""

    _CSV = {
        "periods": {"": "20260331", "_4Q": "20250331"},
        "values": {
            "BHSR1123": {"": 1.0, "_4Q": 1.1},
            "BHCKB705": {"": 100, "_4Q": 90},
            "BHSR264": {"": 0.5, "_4Q": 0.4},
            "BHCP2170": {"": 700, "_4Q": 680},
            "BHSR227": {"": 5, "_4Q": 4},
            "BHCKB992": {"": 11, "_4Q": 10},
        },
        "descriptions": {
            "BHSR1123": "SECURITIZED 1-4 FAMILY RES LOANS: 30-89 DAYS PAST DUE PERCENT",
            "BHCKB705": "OUTSTANDING PRINCIPLE BAL. OF 1-4 FAMILY RESIDENTIAL LOANS",
            "BHSR264": "C&I LOANS 90+ DAYS PAST DUE / C&I LOANS",
            "BHCP2170": "TOTAL ASSETS (BHC PARENT-ONLY)",
            "BHSR227": "OTHER REAL ESTATE OWNED",
            "BHCKB992": "LIFE & HEALTH ASSETS - SEPARATE ACCOUNT ASSETS (BHC CONSOLIDATED)",
        },
    }

    def test_matrix_sections_wire_each_binder(self):
        """Each dimensioned section binds through its dedicated binder or fallback."""
        schema = [
            {
                "section": "Servicing, Securitization, and Asset Sale Activities—Part 1",
                "entries": [
                    {
                        "kind": "subheader",
                        "label": "30-89 Days Past Due Securitized Assets as a Percent of Type",
                        "level": 0,
                    },
                    {
                        "kind": "item",
                        "label": "1-4 Family Residential Loans",
                        "level": 1,
                    },
                    {
                        "kind": "subheader",
                        "label": "Securitization Activities",
                        "level": 0,
                    },
                    {
                        "kind": "item",
                        "label": "1-4 Family Residential Loans",
                        "level": 1,
                    },
                ],
            },
            {
                "section": "Past Due and Nonaccrual Loans and Leases",
                "entries": [
                    {
                        "kind": "item",
                        "label": "Commercial and Industrial Loans—90 Days and Over Past Due",
                        "level": 0,
                    }
                ],
            },
            {
                "section": "Parent Company Balance Sheet",
                "entries": [
                    {"kind": "item", "label": "Total Assets", "level": 0},
                    {"kind": "item", "label": "Other Real Estate Owned", "level": 0},
                ],
            },
            {
                "section": "Insurance and Broker-Dealer Activities",
                "entries": [
                    {
                        "kind": "item",
                        "label": "Separate Account Assets (L/H)",
                        "level": 0,
                    }
                ],
            },
        ]
        bind_codes(schema, [({}, self._CSV)])
        codes = [
            item.get("code")
            for section in schema
            for item in section["entries"]
            if item["kind"] == "item"
        ]
        assert codes == [
            "BHSR1123",
            "BHCKB705",
            "BHSR264",
            "BHCP2170",
            "BHSR227",
            "BHCKB992",
        ]

    def test_description_fallback_margin_and_same_metric_tie(self):
        """The fallback binds a clear winner and accepts a same-description tie."""
        csv = {
            "periods": {"": "20260331", "_4Q": "20250331"},
            "values": {
                "BHSR028": {"": 2.0},
                "BHSR227": {"": 5},
                "BHSR485": {"": 5},
            },
            "descriptions": {
                "BHSR028": "NET INTEREST INCOME / AVERAGE ASSETS",
                "BHSR227": "OTHER REAL ESTATE OWNED",
                "BHSR485": "OTHER REAL ESTATE OWNED",
            },
        }
        schema = [
            {
                "section": "Summary Ratios",
                "entries": [
                    {"kind": "item", "label": "Net Interest Income", "level": 0},
                    {"kind": "item", "label": "Other Real Estate Owned", "level": 0},
                ],
            }
        ]
        bind_codes(schema, [({}, csv)])
        items = schema[0]["entries"]
        assert items[0]["code"] == "BHSR028"
        assert items[0]["code_source"] == "description"
        assert items[1]["code"] in {"BHSR227", "BHSR485"}
        assert items[1]["code_source"] == "description"

    def test_value_conflict_recorded_and_code_reused_once(self):
        """A row matched to two codes across filings is recorded as a conflict."""
        csv1 = {
            "periods": {"": "20260331", "_4Q": "20250331"},
            "values": {"BHCK2170": {"": 100, "_4Q": 90}},
            "descriptions": {"BHCK2170": "TOTAL ASSETS (BHC CONSOLIDATED)"},
        }
        csv2 = {
            "periods": {"": "20260331", "_4Q": "20250331"},
            "values": {"BHSR999": {"": 50, "_4Q": 40}},
            "descriptions": {"BHSR999": "SOME OTHER METRIC"},
        }
        pdf1 = {
            "Zeta": [
                {
                    "label": "Mystery",
                    "periods": {
                        "2026-03-31": {"amount": 100000},
                        "2025-03-31": {"amount": 90000},
                    },
                }
            ]
        }
        pdf2 = {
            "Zeta": [
                {
                    "label": "Mystery",
                    "periods": {
                        "2026-03-31": {"amount": 50000},
                        "2025-03-31": {"amount": 40000},
                    },
                }
            ]
        }
        schema = [
            {
                "section": "Zeta",
                "entries": [{"kind": "item", "label": "Mystery", "level": 0}],
            }
        ]
        report = bind_codes(schema, [(pdf1, csv1), (pdf2, csv2)])
        assert any(
            row[0] == "Zeta" and row[1] == "Mystery" for row in report["conflicts"]
        )
        assert schema[0]["entries"][0]["code"] in {"BHCK2170", "BHSR999"}

    def test_duplicate_value_code_bound_once_across_rows(self):
        """When two rows match one code across filings, only the first keeps it."""
        csv = {
            "periods": {"": "20260331", "_4Q": "20250331"},
            "values": {"BHCK2170": {"": 100, "_4Q": 90}},
            "descriptions": {"BHCK2170": "TOTAL ASSETS (BHC CONSOLIDATED)"},
        }
        match = {
            "2026-03-31": {"amount": 100000},
            "2025-03-31": {"amount": 90000},
        }
        pdf1 = {
            "Zeta": [{"label": "A", "periods": match}, {"label": "B", "periods": {}}]
        }
        pdf2 = {
            "Zeta": [{"label": "A", "periods": {}}, {"label": "B", "periods": match}]
        }
        schema = [
            {
                "section": "Zeta",
                "entries": [
                    {"kind": "item", "label": "A", "level": 0},
                    {"kind": "item", "label": "B", "level": 0},
                ],
            }
        ]
        bind_codes(schema, [(pdf1, csv), (pdf2, csv)])
        bound = [e["code"] for e in schema[0]["entries"]]
        assert bound.count("BHCK2170") == 1
