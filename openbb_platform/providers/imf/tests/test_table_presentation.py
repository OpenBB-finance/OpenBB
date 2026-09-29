"""Tests for openbb_imf.utils.table_presentation."""

# ruff: noqa: I001

from __future__ import annotations

from typing import Any

import pandas as pd
import pytest

from openbb_core.app.model.abstract.warning import OpenBBWarning

from openbb_imf.utils.table_presentation import (
    HierarchyContext,
    build_order_title_level,
    check_missing_country_data,
    extract_unit_from_label,
    extract_unit_scale_from_title,
    format_unit_suffix,
    is_bop_suffix_only,
    parse_unit_and_scale,
    pivot_indicator_mode,
    pivot_table_data,
    pivot_table_mode,
    strip_title_suffix,
)


class TestExtractUnitFromLabel:
    """Tests for extract_unit_from_label."""

    def test_empty_returns_none(self):
        """Empty string yields None."""
        assert extract_unit_from_label("") is None

    def test_paren_with_unit_keyword(self):
        """Trailing parenthetical containing a keyword is returned."""
        assert (
            extract_unit_from_label("GDP (Millions of US Dollar)")
            == "Millions of US Dollar"
        )

    def test_paren_no_keyword_returns_none(self):
        """Trailing parenthetical with no unit keyword returns None."""
        assert extract_unit_from_label("GDP (seasonally adjusted)") is None

    def test_paren_no_leading_space_returns_none(self):
        """A '(' without leading space is not treated as a unit."""
        assert extract_unit_from_label("(USD)") is None

    def test_comma_per_phrase(self):
        """A ', X per Y' suffix yields the last part."""
        assert (
            extract_unit_from_label("Trade, US dollars per metric tonne")
            == "US dollars per metric tonne"
        )

    def test_comma_unit_keyword(self):
        """A ', percent' style suffix is returned."""
        assert extract_unit_from_label("Inflation, percent") == "percent"

    def test_comma_no_keyword_returns_none(self):
        """A trailing comma part that has no keyword returns None."""
        assert extract_unit_from_label("Trade, exports") is None

    def test_no_comma_no_paren(self):
        """A plain label returns None."""
        assert extract_unit_from_label("Population") is None


class TestParseUnitAndScale:
    """Tests for parse_unit_and_scale."""

    def test_empty_returns_none_none(self):
        """Empty input yields (None, None)."""
        assert parse_unit_and_scale("") == (None, None)
        assert parse_unit_and_scale(None) == (None, None)

    def test_percent_of_pattern(self):
        """'Percent of GDP' splits into ('Percent', 'of Gdp')."""
        unit, scale = parse_unit_and_scale("Percent of GDP")
        assert unit == "Percent"
        assert scale == "of Gdp"

    def test_per_pattern(self):
        """'US Dollar per metric tonne' splits into unit and scale."""
        unit, scale = parse_unit_and_scale("US Dollar per metric tonne")
        assert unit == "US Dollar"
        assert scale == "Per Metric Tonne"

    def test_scale_prefix(self):
        """'Millions, X' yields unit X and scale 'Millions'."""
        unit, scale = parse_unit_and_scale("Millions, US Dollar")
        assert unit == "US Dollar"
        assert scale == "Millions"

    def test_scale_suffix(self):
        """'X, Millions' yields unit X and scale 'Millions'."""
        unit, scale = parse_unit_and_scale("US Dollar, Millions")
        assert unit == "US Dollar"
        assert scale == "Millions"

    def test_unit_keyword_at_end(self):
        """A trailing unit keyword after comma extracts unit."""
        unit, scale = parse_unit_and_scale("Some scale, Percent")
        assert unit == "Percent"
        assert scale == "Some scale"

    def test_scale_only(self):
        """A bare scale word becomes scale with None unit."""
        unit, scale = parse_unit_and_scale("Per capita")
        assert unit is None
        assert scale == "Per capita"

    def test_unknown_string_returns_as_unit(self):
        """An unrecognized string is returned as a unit only."""
        unit, scale = parse_unit_and_scale("Strange unit")
        assert unit == "Strange unit"
        assert scale is None


class TestStripTitleSuffix:
    """Tests for strip_title_suffix."""

    def test_transactions_suffix(self):
        """', Transactions' suffix is stripped."""
        assert strip_title_suffix("Goods, Transactions") == "Goods"

    def test_stocks_suffix(self):
        """', Stocks' suffix is stripped."""
        assert strip_title_suffix("Assets, Stocks") == "Assets"

    def test_paren_unit_suffix_stripped(self):
        """A trailing parenthetical with a unit pattern is stripped."""
        assert strip_title_suffix("GDP (Millions)") == "GDP"

    def test_paren_non_unit_kept(self):
        """A trailing parenthetical without unit pattern is kept."""
        assert strip_title_suffix("GDP (Seasonally adjusted)") == (
            "GDP (Seasonally adjusted)"
        )

    def test_plain_unchanged(self):
        """A plain title is returned unchanged."""
        assert strip_title_suffix("GDP") == "GDP"


class TestFormatUnitSuffix:
    """Tests for format_unit_suffix."""

    def test_both(self):
        """Unit and scale combine into ' (unit, scale)'."""
        assert format_unit_suffix("US Dollar", "Millions") == " (US Dollar, Millions)"

    def test_unit_only(self):
        """Unit alone yields ' (unit)'."""
        assert format_unit_suffix("Percent", None) == " (Percent)"

    def test_skips_units_scale(self):
        """The literal scale 'Units' is filtered out."""
        assert format_unit_suffix("Item", "Units") == " (Item)"

    def test_dash_and_nan_filtered(self):
        """Values like '-' and 'nan' are filtered out."""
        assert format_unit_suffix("-", "nan") == ""
        assert format_unit_suffix(None, None) == ""

    def test_non_string_input(self):
        """Non-string inputs are ignored."""
        assert format_unit_suffix(123, 456) == ""


class TestExtractUnitScaleFromTitle:
    """Tests for extract_unit_scale_from_title."""

    def test_empty(self):
        """Empty input yields (None, None)."""
        assert extract_unit_scale_from_title("") == (None, None)

    def test_paren_single_scale(self):
        """A single scale-only parenthetical produces only a scale."""
        unit, scale = extract_unit_scale_from_title("GDP (Millions)")
        assert unit is None
        assert scale == "Millions"

    def test_paren_single_unit_only(self):
        """A single non-scale-pattern paren returns it as unit if pattern matches."""
        unit, scale = extract_unit_scale_from_title("GDP (US dollar, Percent)")
        assert unit == "US dollar"
        assert scale == "Percent"

    def test_paren_single_non_pattern(self):
        """A single unit element without a known scale becomes unit."""
        unit, scale = extract_unit_scale_from_title("GDP (Foo Percent)")
        assert unit == "Foo Percent"
        assert scale is None

    def test_paren_two_parts(self):
        """A two-part parenthetical yields (first, second)."""
        unit, scale = extract_unit_scale_from_title("GDP (US Dollar, Millions)")
        assert unit == "US Dollar"
        assert scale == "Millions"

    def test_paren_with_no_scale_pattern_falls_through(self):
        """A paren without a known scale pattern falls through to comma logic."""
        unit, scale = extract_unit_scale_from_title("Trade, US dollars")
        assert unit == "US dollars"
        assert scale is None

    def test_no_match_returns_none(self):
        """A plain title yields (None, None)."""
        assert extract_unit_scale_from_title("Population") == (None, None)


class TestIsBopSuffixOnly:
    """Tests for is_bop_suffix_only."""

    def test_empty(self):
        """Empty string returns False."""
        assert is_bop_suffix_only("") is False

    def test_only_punctuation(self):
        """Punctuation-only normalizes to empty and returns True."""
        assert is_bop_suffix_only(", :") is True

    def test_lowercase_first_word(self):
        """A lowercase first word is treated as BOP suffix only."""
        assert is_bop_suffix_only("net flows") is True

    def test_bop_term(self):
        """Recognized BOP terms return True."""
        assert is_bop_suffix_only("Credit") is True
        assert is_bop_suffix_only("Assets (excl. reserves)") is True

    def test_non_bop_term(self):
        """A normal title returns False."""
        assert is_bop_suffix_only("Goods") is False

    def test_bop_paren_stripping(self):
        """A trailing paren is stripped before bop check."""
        assert is_bop_suffix_only("Assets (some context)") is True


class TestHierarchyContextSiblings:
    """Tests for HierarchyContext._get_true_siblings and sibling prefix logic."""

    def test_sort_on_init(self):
        """Order list is sorted by order value."""
        ctx = HierarchyContext(
            [(3.0, "C", 1, False), (1.0, "A", 0, True), (2.0, "B", 1, False)]
        )
        assert [t[0] for t in ctx.order_title_level] == [1.0, 2.0, 3.0]

    def test_missing_target_returns_empty(self):
        """If target order not found, returns []."""
        ctx = HierarchyContext([(1.0, "A", 0, False)])
        assert ctx._get_true_siblings(99.0, 0) == []

    def test_siblings_consecutive(self):
        """Consecutive same-level rows are siblings."""
        ctx = HierarchyContext(
            [
                (1.0, "Parent", 0, True),
                (2.0, "Goods, Credit", 1, False),
                (3.0, "Goods, Debit", 1, False),
                (4.0, "Goods, Net", 1, False),
            ]
        )
        sibs = ctx._get_true_siblings(2.0, 1)
        assert {t for _, t in sibs} == {"Goods, Credit", "Goods, Debit", "Goods, Net"}

    def test_sibling_common_prefix_below_three(self):
        """Fewer than 3 siblings yields no common prefix."""
        ctx = HierarchyContext(
            [
                (1.0, "Goods, Credit", 1, False),
                (2.0, "Goods, Debit", 1, False),
            ]
        )
        assert ctx.find_sibling_common_prefix(1.0, "Goods, Credit") is None

    def test_sibling_common_prefix_target_missing(self):
        """Target order not in list returns None."""
        ctx = HierarchyContext([(1.0, "X", 0, False)])
        assert ctx.find_sibling_common_prefix(99.0, "X") is None

    def test_sibling_common_prefix_bop_endings_returns_none(self):
        """All-BOP-ending siblings skip prefix detection."""
        ctx = HierarchyContext(
            [
                (1.0, "Goods, Credit", 1, False),
                (2.0, "Goods, Debit", 1, False),
                (3.0, "Goods, Net", 1, False),
            ]
        )
        assert ctx.find_sibling_common_prefix(1.0, "Goods, Credit") is None

    def test_sibling_common_prefix_real_match(self):
        """A shared multi-segment prefix among non-BOP siblings is detected."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade, Goods, Exports", 1, False),
                (2.0, "Trade, Goods, Imports", 1, False),
                (3.0, "Trade, Goods, Balance", 1, False),
            ]
        )
        prefix = ctx.find_sibling_common_prefix(1.0, "Trade, Goods, Exports")
        assert prefix == "Trade, Goods, "

    def test_sibling_common_prefix_displayed_filter(self):
        """displayed_orders filter culls to < 3 siblings -> None."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade, A", 1, False),
                (2.0, "Trade, B", 1, False),
                (3.0, "Trade, C", 1, False),
            ]
        )
        assert (
            ctx.find_sibling_common_prefix(1.0, "Trade, A", displayed_orders={1.0})
            is None
        )

    def test_sibling_common_prefix_no_common(self):
        """If no common first segment, returns None."""
        ctx = HierarchyContext(
            [
                (1.0, "A, X", 1, False),
                (2.0, "B, Y", 1, False),
                (3.0, "C, Z", 1, False),
            ]
        )
        assert ctx.find_sibling_common_prefix(1.0, "A, X") is None

    def test_sibling_common_prefix_target_does_not_match(self):
        """Target title that doesn't start with common prefix returns None."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade, A, X", 1, False),
                (2.0, "Trade, A, Y", 1, False),
                (3.0, "Trade, A, Z", 1, False),
            ]
        )
        assert ctx.find_sibling_common_prefix(1.0, "Different, A, X") is None

    def test_sibling_common_prefix_empty_titles(self):
        """Empty sibling titles drop count below threshold."""
        ctx = HierarchyContext(
            [
                (1.0, "", 1, False),
                (2.0, "", 1, False),
                (3.0, "", 1, False),
            ]
        )
        assert ctx.find_sibling_common_prefix(1.0, "X") is None


class TestHierarchyContextBopGroup:
    """Tests for HierarchyContext.find_bop_group_prefix."""

    def test_no_bop_suffix(self):
        """A title without a BOP suffix returns None."""
        ctx = HierarchyContext([(1.0, "X", 0, False)])
        assert ctx.find_bop_group_prefix(1.0, "Goods") is None

    def test_net_suffix_skipped(self):
        """A ', Net' suffix never returns a group prefix."""
        ctx = HierarchyContext([(1.0, "Goods, Net", 0, False)])
        assert ctx.find_bop_group_prefix(1.0, "Goods, Net") is None

    def test_target_missing(self):
        """Missing target order returns None."""
        ctx = HierarchyContext([(1.0, "X", 0, False)])
        assert ctx.find_bop_group_prefix(99.0, "Goods, Credit") is None

    def test_no_matching_net(self):
        """Credit without a matching Net sibling returns None."""
        ctx = HierarchyContext(
            [
                (1.0, "Goods, Credit", 0, False),
                (2.0, "Goods, Debit", 0, False),
            ]
        )
        assert ctx.find_bop_group_prefix(1.0, "Goods, Credit") is None

    def test_returns_prefix(self):
        """Credit with a matching Net sibling returns the base prefix."""
        ctx = HierarchyContext(
            [
                (1.0, "Goods, Credit", 0, False),
                (2.0, "Goods, Debit", 0, False),
                (3.0, "Goods, Net", 0, False),
            ]
        )
        assert ctx.find_bop_group_prefix(1.0, "Goods, Credit") == "Goods, "

    def test_displayed_filter(self):
        """displayed_orders filter removes matching Net."""
        ctx = HierarchyContext(
            [
                (1.0, "Goods, Credit", 0, False),
                (2.0, "Goods, Debit", 0, False),
                (3.0, "Goods, Net", 0, False),
            ]
        )
        assert (
            ctx.find_bop_group_prefix(1.0, "Goods, Credit", displayed_orders={1.0, 2.0})
            is None
        )


class TestHierarchyContextBestPrefix:
    """Tests for HierarchyContext.find_best_prefix."""

    def test_missing_target(self):
        """Missing target order returns None."""
        ctx = HierarchyContext([(1.0, "X", 0, True)])
        assert ctx.find_best_prefix(99.0, "Anything") is None

    def test_no_ancestors(self):
        """No ancestor rows -> None."""
        ctx = HierarchyContext([(1.0, "Goods, Trade", 0, False)])
        assert ctx.find_best_prefix(1.0, "Goods, Trade") is None

    def test_direct_prefix(self):
        """An ancestor title that is a prefix is returned."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade", 0, True),
                (2.0, "Trade, Goods", 1, False),
            ]
        )
        assert ctx.find_best_prefix(2.0, "Trade, Goods") == "Trade"

    def test_displayed_filter_excludes_ancestor(self):
        """Ancestor not in displayed_orders is skipped."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade", 0, True),
                (2.0, "Trade, Goods", 1, False),
            ]
        )
        assert ctx.find_best_prefix(2.0, "Trade, Goods", displayed_orders=set()) is None

    def test_empty_ancestor_skipped(self):
        """Empty ancestor titles are skipped."""
        ctx = HierarchyContext(
            [
                (1.0, "", 0, True),
                (2.0, "Trade, Goods", 1, False),
            ]
        )
        assert ctx.find_best_prefix(2.0, "Trade, Goods") is None

    def test_phrase_match_with_separator(self):
        """An ancestor key phrase can match via ': ' separator."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade Survey", 0, True),
                (2.0, "Trade: Detail", 1, False),
            ]
        )
        result = ctx.find_best_prefix(2.0, "Trade: Detail")
        assert result == "Trade: "

    def test_bop_only_remainder_returns_none(self):
        """If remainder after stripping is BOP-only, return None."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade", 0, True),
                (2.0, "Trade, Credit", 1, False),
            ]
        )
        assert ctx.find_best_prefix(2.0, "Trade, Credit") is None

    def test_picks_longest_prefix(self):
        """When multiple ancestors match, the longest wins."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade", 0, True),
                (2.0, "Trade Goods", 1, True),
                (3.0, "Trade Goods, Exports", 2, False),
            ]
        )
        assert ctx.find_best_prefix(3.0, "Trade Goods, Exports") == "Trade Goods"

    def test_skip_repeat_levels(self):
        """Once a level is seen, deeper rows at that level are skipped."""
        ctx = HierarchyContext(
            [
                (1.0, "Foo", 0, True),
                (2.0, "Bar", 0, True),
                (3.0, "Bar, X", 1, False),
            ]
        )
        result = ctx.find_best_prefix(3.0, "Bar, X")
        assert result == "Bar"


class TestHierarchyContextBestSuffix:
    """Tests for HierarchyContext.find_best_suffix."""

    def test_missing_target(self):
        """Missing target order returns None."""
        ctx = HierarchyContext([(1.0, "X", 0, True)])
        assert ctx.find_best_suffix(99.0, "X, Y") is None

    def test_no_ancestor_parts(self):
        """No ancestors leaves nothing to match -> None."""
        ctx = HierarchyContext([(1.0, "Goods, Trade", 0, False)])
        assert ctx.find_best_suffix(1.0, "Goods, Trade") is None

    def test_displayed_filter(self):
        """Ancestor filtered out by displayed_orders is ignored."""
        ctx = HierarchyContext(
            [
                (1.0, "Special", 0, True),
                (2.0, "X, Special", 1, False),
            ]
        )
        assert ctx.find_best_suffix(2.0, "X, Special", displayed_orders=set()) is None

    def test_empty_ancestor_skipped(self):
        """Empty ancestor titles are skipped."""
        ctx = HierarchyContext(
            [
                (1.0, "", 0, True),
                (2.0, "X, Y", 1, False),
            ]
        )
        assert ctx.find_best_suffix(2.0, "X, Y") is None

    def test_protected_suffix_not_stripped(self):
        """Protected BOP suffixes like 'Assets' are not removed."""
        ctx = HierarchyContext(
            [
                (1.0, "Assets", 0, True),
                (2.0, "X, Assets", 1, False),
            ]
        )
        assert ctx.find_best_suffix(2.0, "X, Assets") is None

    def test_returns_matching_suffix(self):
        """A regular ancestor word that appears as suffix is returned."""
        ctx = HierarchyContext(
            [
                (1.0, "Special", 0, True),
                (2.0, "X, Special", 1, False),
            ]
        )
        assert ctx.find_best_suffix(2.0, "X, Special") == ", Special"

    def test_debtors_creditors_expansion(self):
        """Debtors/Creditors ancestors are detected as suffix ancestors."""
        ctx = HierarchyContext(
            [
                (1.0, "Debtors group", 0, True),
                (2.0, "Foo, Debtors group", 1, False),
            ]
        )
        ctx2 = HierarchyContext(
            [
                (1.0, "Creditors group", 0, True),
                (2.0, "X, Creditors group", 1, False),
            ]
        )
        ctx3 = HierarchyContext(
            [
                (1.0, "Financial assets", 0, True),
                (2.0, "X, Financial assets", 1, False),
            ]
        )
        assert ctx.find_best_suffix(2.0, "Foo, Debtors group") == ", Debtors group"
        assert ctx2.find_best_suffix(2.0, "X, Creditors group") == ", Creditors group"
        assert ctx3.find_best_suffix(2.0, "X, Financial assets") == ", Financial assets"

    def test_liabilities_expansion(self):
        """A 'Liabilities' ancestor adds 'Net incurrence of liabilities' and 'Total liabilities'."""
        ctx = HierarchyContext(
            [
                (1.0, "Liabilities", 0, True),
                (2.0, "X, Total liabilities", 1, False),
            ]
        )
        assert (
            ctx.find_best_suffix(2.0, "X, Total liabilities") == ", Total liabilities"
        )


class TestHierarchyContextAncestorPartPrefix:
    """Tests for HierarchyContext.find_ancestor_part_prefix."""

    def test_missing_target(self):
        """Missing target order returns None."""
        ctx = HierarchyContext([(1.0, "X", 0, True)])
        assert ctx.find_ancestor_part_prefix(99.0, "X, Y") is None

    def test_no_ancestor_parts(self):
        """No ancestors -> None."""
        ctx = HierarchyContext([(1.0, "Goods, Trade", 0, False)])
        assert ctx.find_ancestor_part_prefix(1.0, "Goods, Trade") is None

    def test_single_word_skipped(self):
        """A single-word ancestor that's not strippable is ignored."""
        ctx = HierarchyContext(
            [
                (1.0, "Foo", 0, True),
                (2.0, "Foo, X", 1, False),
            ]
        )
        assert ctx.find_ancestor_part_prefix(2.0, "Foo, X") is None

    def test_assets_strippable(self):
        """The single word 'Assets' is in the strippable set."""
        ctx = HierarchyContext(
            [
                (1.0, "Assets", 0, True),
                (2.0, "Assets, X", 1, False),
            ]
        )
        assert ctx.find_ancestor_part_prefix(2.0, "Assets, X") == "Assets, "

    def test_multi_word_ancestor_prefix(self):
        """Multi-word ancestors strip a matching prefix."""
        ctx = HierarchyContext(
            [
                (1.0, "Financial corporations", 0, True),
                (2.0, "Financial corporations, X", 1, False),
            ]
        )
        assert (
            ctx.find_ancestor_part_prefix(2.0, "Financial corporations, X")
            == "Financial corporations, "
        )

    def test_displayed_filter(self):
        """Ancestor filtered by displayed_orders is ignored."""
        ctx = HierarchyContext(
            [
                (1.0, "Financial corporations", 0, True),
                (2.0, "Financial corporations, X", 1, False),
            ]
        )
        assert (
            ctx.find_ancestor_part_prefix(
                2.0, "Financial corporations, X", displayed_orders=set()
            )
            is None
        )

    def test_bop_remainder_skipped(self):
        """A remainder that's BOP-only is skipped (loop continues)."""
        ctx = HierarchyContext(
            [
                (1.0, "Financial corporations", 0, True),
                (2.0, "Financial corporations, Net", 1, False),
            ]
        )
        assert ctx.find_ancestor_part_prefix(2.0, "Financial corporations, Net") is None

    def test_self_skip(self):
        """Ancestors equal to target title are skipped."""
        ctx = HierarchyContext(
            [
                (1.0, "Foo bar", 0, True),
                (2.0, "Foo bar", 1, False),
            ]
        )
        assert ctx.find_ancestor_part_prefix(2.0, "Foo bar") is None

    def test_child_prefix_long_form(self):
        """A long comma-prefix matching an ancestor word triggers fallback."""
        ctx = HierarchyContext(
            [
                (1.0, "International investment position", 0, True),
                (2.0, "International investment, Detail", 1, False),
            ]
        )
        result = ctx.find_ancestor_part_prefix(2.0, "International investment, Detail")
        assert result == "International investment, "


class TestHierarchyContextSimplifyTitle:
    """Tests for HierarchyContext.simplify_title."""

    def test_strip_suffix_only(self):
        """A bare title with a unit suffix is stripped."""
        ctx = HierarchyContext([(1.0, "Plain (Millions)", 0, False)])
        assert ctx.simplify_title(1.0, "Plain (Millions)") == "Plain"

    def test_prefix_then_suffix(self):
        """Prefix from ancestor is removed."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade", 0, True),
                (2.0, "Trade, Goods", 1, False),
            ]
        )
        assert ctx.simplify_title(2.0, "Trade, Goods") == "Goods"

    def test_bop_only_restored(self):
        """If stripping leaves a BOP-only term, original is restored."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade", 0, True),
                (2.0, "Trade, Net", 1, False),
                (3.0, "Trade, Credit", 1, False),
            ]
        )
        out = ctx.simplify_title(2.0, "Trade, Net")
        assert out == "Trade, Net"

    def test_empty_restored(self):
        """If stripping yields empty, original is restored."""
        ctx = HierarchyContext(
            [
                (1.0, "Foo", 0, True),
                (2.0, "Foo", 1, False),
            ]
        )
        out = ctx.simplify_title(2.0, "Foo")
        assert out == "Foo"

    def test_bop_group_stripped_keeps_short(self):
        """BOP group stripping keeps a short like 'Credit'."""
        ctx = HierarchyContext(
            [
                (1.0, "Goods, Credit", 0, False),
                (2.0, "Goods, Debit", 0, False),
                (3.0, "Goods, Net", 0, False),
            ]
        )
        out = ctx.simplify_title(1.0, "Goods, Credit")
        assert out == "Credit"

    def test_sibling_prefix_strip(self):
        """A common multi-segment sibling prefix is stripped."""
        ctx = HierarchyContext(
            [
                (1.0, "Trade, Goods, Exports", 1, False),
                (2.0, "Trade, Goods, Imports", 1, False),
                (3.0, "Trade, Goods, Balance", 1, False),
            ]
        )
        out = ctx.simplify_title(1.0, "Trade, Goods, Exports")
        assert out == "Exports"

    def test_best_suffix_strip(self):
        """An ancestor suffix that appears is removed."""
        ctx = HierarchyContext(
            [
                (1.0, "Special", 0, True),
                (2.0, "X, Special", 1, False),
            ]
        )
        out = ctx.simplify_title(2.0, "X, Special")
        assert out == "X"


class TestBuildOrderTitleLevel:
    """Tests for build_order_title_level."""

    def test_header_row_picked(self):
        """The header row with longest title is used."""
        df = pd.DataFrame(
            [
                {
                    "order": 1.0,
                    "title": "Short",
                    "level": 0,
                    "is_category_header": True,
                },
                {
                    "order": 1.0,
                    "title": "Longer header title",
                    "level": 0,
                    "is_category_header": True,
                },
            ]
        )
        out = build_order_title_level(df)
        assert out == [(1.0, "Longer header title", 0, True)]

    def test_data_row_when_no_header(self):
        """Without a header row, the longest data row is used."""
        df = pd.DataFrame(
            [
                {
                    "order": 2.0,
                    "title": "A",
                    "level": 1,
                    "is_category_header": False,
                },
                {
                    "order": 2.0,
                    "title": "AAAA",
                    "level": 1,
                    "is_category_header": False,
                },
            ]
        )
        out = build_order_title_level(df)
        assert out == [(2.0, "AAAA", 1, False)]

    def test_drops_na_orders(self):
        """Rows with NaN order are dropped."""
        df = pd.DataFrame(
            [
                {
                    "order": None,
                    "title": "X",
                    "level": 0,
                    "is_category_header": False,
                },
                {
                    "order": 1.0,
                    "title": "Y",
                    "level": 0,
                    "is_category_header": False,
                },
            ]
        )
        out = build_order_title_level(df)
        assert out == [(1.0, "Y", 0, False)]

    def test_sorted(self):
        """Results are sorted by order ascending."""
        df = pd.DataFrame(
            [
                {
                    "order": 3.0,
                    "title": "C",
                    "level": 0,
                    "is_category_header": False,
                },
                {
                    "order": 1.0,
                    "title": "A",
                    "level": 0,
                    "is_category_header": False,
                },
                {
                    "order": 2.0,
                    "title": "B",
                    "level": 0,
                    "is_category_header": False,
                },
            ]
        )
        out = build_order_title_level(df)
        assert [t[0] for t in out] == [1.0, 2.0, 3.0]


class TestCheckMissingCountryData:
    """Tests for check_missing_country_data."""

    def test_no_warning_when_data_present(self):
        """Country with data in selected dates does not warn."""
        df = pd.DataFrame(
            [
                {"country": "USA", "country_code": "USA", "date": "2020-01-01"},
            ]
        )
        check_missing_country_data(df, ["USA"], ["2020-01-01"], ["USA"])

    def test_warns_when_missing(self):
        """Country missing data in selected dates produces a warning."""
        df = pd.DataFrame(
            [
                {"country": "USA", "country_code": "USA", "date": "2019-01-01"},
                {"country": "GBR", "country_code": "GBR", "date": "2020-01-01"},
            ]
        )
        with pytest.warns(OpenBBWarning, match="No data for 'USA'"):
            check_missing_country_data(df, ["USA"], ["2020-01-01"], ["USA", "GBR"])

    def test_match_by_country_code(self):
        """A requested code matches via country_code column."""
        df = pd.DataFrame(
            [
                {
                    "country": "United States",
                    "country_code": "USA",
                    "date": "2019-01-01",
                }
            ]
        )
        with pytest.warns(OpenBBWarning):
            check_missing_country_data(df, ["USA"], ["2020-01-01"], ["United States"])


class TestPivotIndicatorMode:
    """Tests for pivot_indicator_mode."""

    def test_basic_pivot(self):
        """A basic dataset pivots into MultiIndex DataFrame."""
        df = pd.DataFrame(
            [
                {
                    "title": "GDP",
                    "country": "USA",
                    "date": "2020-01-01",
                    "value": 100.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                },
                {
                    "title": "GDP",
                    "country": "USA",
                    "date": "2021-01-01",
                    "value": 110.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                },
            ]
        )
        result = pivot_indicator_mode(df, ["2020-01-01", "2021-01-01"], ["USA"])
        assert not result.empty
        assert ("GDP", "USA", "US Dollar", "Millions") in result.index

    def test_skips_nan_title(self):
        """Rows with NaN title are skipped."""
        df = pd.DataFrame(
            [
                {
                    "title": None,
                    "country": "USA",
                    "date": "2020-01-01",
                    "value": 5.0,
                    "unit": "US",
                    "scale": "M",
                }
            ]
        )
        result = pivot_indicator_mode(df, ["2020-01-01"], ["USA"])
        assert result.empty

    def test_country_with_no_data_skipped(self):
        """Country with no rows for a title is skipped."""
        df = pd.DataFrame(
            [
                {
                    "title": "GDP",
                    "country": "USA",
                    "date": "2020-01-01",
                    "value": 1.0,
                    "unit": "U",
                    "scale": "S",
                }
            ]
        )
        result = pivot_indicator_mode(df, ["2020-01-01"], ["USA", "GBR"])
        assert ("GDP", "USA", "U", "S") in result.index
        assert ("GDP", "GBR", "U", "S") not in result.index

    def test_dash_unit_treated_as_none_then_parsed(self):
        """'-' unit/scale gets replaced via title parsing."""
        df = pd.DataFrame(
            [
                {
                    "title": "GDP (US Dollar, Millions)",
                    "country": "USA",
                    "date": "2020-01-01",
                    "value": 1.0,
                    "unit": "-",
                    "scale": "-",
                }
            ]
        )
        result = pivot_indicator_mode(df, ["2020-01-01"], ["USA"])
        assert (
            "GDP (US Dollar, Millions)",
            "USA",
            "US Dollar",
            "Millions",
        ) in result.index

    def test_all_zero_dropped(self):
        """A series whose only values are zero is omitted."""
        df = pd.DataFrame(
            [
                {
                    "title": "GDP",
                    "country": "USA",
                    "date": "2020-01-01",
                    "value": 0.0,
                    "unit": "U",
                    "scale": "S",
                }
            ]
        )
        result = pivot_indicator_mode(df, ["2020-01-01"], ["USA"])
        assert result.empty


class TestPivotTableMode:
    """Tests for pivot_table_mode."""

    @staticmethod
    def _base_df(rows: list[dict[str, Any]]) -> pd.DataFrame:
        """Build a DataFrame from row dicts with required columns defaulted."""
        defaults = {
            "title": "",
            "level": 0,
            "order": 0.0,
            "country": "USA",
            "country_code": "USA",
            "date": "2020-01-01",
            "value": float("nan"),
            "unit": "",
            "scale": "",
            "is_category_header": False,
            "hierarchy_node_id": None,
            "parent_id": None,
            "indicator_code": None,
            "symbol": "S",
        }
        out = []
        for r in rows:
            d = dict(defaults)
            d.update(r)
            out.append(d)
        return pd.DataFrame(out)

    def test_simple_hierarchy(self):
        """A simple two-row hierarchy pivots into rows with indented titles."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                    "parent_id": None,
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Trade, Goods",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "TRD_G",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade Table", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert not result.empty
        titles = [idx[0] for idx in result.index]
        assert any("Trade" in t for t in titles)

    def test_no_data_returns_empty_df(self):
        """If no rows have any data, result is an empty DataFrame."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade Table", "dataflow_id": "BOP"}}
        try:
            pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        except KeyError:
            pass

    def test_inherited_unit_scale_from_parent(self):
        """A child without unit/scale inherits from its parent's order."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                    "unit": "US Dollar",
                    "scale": "Millions",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Trade, Goods",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "indicator_code": "TRD_G",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade Table", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert not result.empty

    def test_isora_filters_non_topic_headers(self):
        """For ISORA dataflows, non-topic headers are skipped."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Some random header",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Trade, Goods",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "TRD_G",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "ISORA Survey", "dataflow_id": "ISORA"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_isora_topic_header_kept(self):
        """For ISORA, topic-style headers (numbered) are kept."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "1. Some topic",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "1. Some topic, Detail",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 7.0,
                    "unit": "Percent",
                    "scale": "Units",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "ISORA Survey", "dataflow_id": "ISORA"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert not result.empty

    def test_first_level0_data_adds_table_header(self):
        """If the first level-0 row is data (not a header), a table header row is added."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Direct Data",
                    "is_category_header": False,
                    "hierarchy_node_id": "n1",
                    "value": 1.5,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "DD",
                },
            ]
        )
        meta = {
            "table": {
                "hierarchy_name": "Trade Statistics",
                "dataflow_id": "BOP",
            }
        }
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        titles = [idx[0] for idx in result.index]
        assert any("TRADE STATISTICS" in t for t in titles)

    def test_dimension_grouping_with_counterpart_country(self):
        """Counterpart country grouping renders ▸ group / country rows."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 10.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "G001",
                    "counterpart_country": "World",
                    "indicator_code": "B",
                    "series_id": "s1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "GBR",
                    "counterpart_country": "United Kingdom",
                    "indicator_code": "B",
                    "series_id": "s2",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 3.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "G002",
                    "counterpart_country": "Europe",
                    "indicator_code": "B",
                    "series_id": "s3",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert not result.empty
        titles = [idx[0] for idx in result.index]
        assert any("World" in t or "Bilateral" in t for t in titles)

    def test_sector_multi_dim(self):
        """Multiple SECTOR codes group under a header with sector indents."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Indicator",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Detail",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S1",
                    "sector": "Households",
                    "indicator_code": "I1",
                    "series_id": "p1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Detail",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S2",
                    "sector": "Corporations",
                    "indicator_code": "I1",
                    "series_id": "p2",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Indicator", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert not result.empty

    def test_bop_credit_debit_net_grouping(self):
        """BOP Credit/Debit/Net sibling grouping is exercised."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Goods, Credit",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "G_C",
                },
                {
                    "order": 3.0,
                    "level": 1,
                    "title": "Goods, Debit",
                    "hierarchy_node_id": "n3",
                    "parent_id": "n1",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "G_D",
                },
                {
                    "order": 4.0,
                    "level": 1,
                    "title": "Goods, Net",
                    "hierarchy_node_id": "n4",
                    "parent_id": "n1",
                    "value": 3.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "G_N",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert not result.empty
        titles = [idx[0] for idx in result.index]
        assert any("Credit" in t or "Debit" in t or "Net" in t for t in titles)


class TestPivotTableData:
    """Tests for pivot_table_data dispatcher."""

    def test_no_hierarchy_indicator_mode(self):
        """When no 'order' column exists, indicator mode is used."""
        records = [
            {
                "title": "GDP",
                "country": "USA",
                "date": "2020-01-01",
                "value": 100.0,
                "unit": "US Dollar",
                "scale": "Millions",
            }
        ]
        result = pivot_table_data(records, country="USA", limit=None, metadata={})
        assert isinstance(result, pd.DataFrame)
        assert ("GDP", "USA", "US Dollar", "Millions") in result.index

    def test_with_hierarchy_table_mode(self):
        """When 'order' column has values, table mode is used."""
        records = [
            {
                "title": "Trade",
                "country": "USA",
                "country_code": "USA",
                "date": "2020-01-01",
                "value": 0.0,
                "level": 0,
                "order": 1.0,
                "is_category_header": True,
                "hierarchy_node_id": "n1",
                "parent_id": None,
                "indicator_code": None,
                "unit": "",
                "scale": "",
                "symbol": "S",
            },
            {
                "title": "Trade, Goods",
                "country": "USA",
                "country_code": "USA",
                "date": "2020-01-01",
                "value": 5.0,
                "level": 1,
                "order": 2.0,
                "is_category_header": False,
                "hierarchy_node_id": "n2",
                "parent_id": "n1",
                "indicator_code": "TRD_G",
                "unit": "US Dollar",
                "scale": "Millions",
                "symbol": "S",
            },
        ]
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_data(records, country="USA", limit=1, metadata=meta)
        assert isinstance(result, pd.DataFrame)

    def test_limit_zero_returns_all_dates(self):
        """limit=0 falls back to all dates."""
        records = [
            {
                "title": "GDP",
                "country": "USA",
                "date": "2020-01-01",
                "value": 100.0,
                "unit": "US Dollar",
                "scale": "Millions",
            }
        ]
        result = pivot_table_data(records, country=None, limit=0, metadata={})
        assert isinstance(result, pd.DataFrame)


class TestPivotTableModeExtras:
    """Tests targeting specific branches in pivot_table_mode."""

    @staticmethod
    def _base_df(rows: list[dict[str, Any]]) -> pd.DataFrame:
        """Same defaults as TestPivotTableMode._base_df."""
        defaults = {
            "title": "",
            "level": 0,
            "order": 0.0,
            "country": "USA",
            "country_code": "USA",
            "date": "2020-01-01",
            "value": float("nan"),
            "unit": "",
            "scale": "",
            "is_category_header": False,
            "hierarchy_node_id": None,
            "parent_id": None,
            "indicator_code": None,
            "symbol": "S",
        }
        out = []
        for r in rows:
            d = dict(defaults)
            d.update(r)
            out.append(d)
        return pd.DataFrame(out)

    def test_parent_lookup_via_suffix_pattern(self):
        """Parent_id matched via '___pid' suffix lookup branch."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Parent",
                    "is_category_header": True,
                    "hierarchy_node_id": "PFX___N1",
                    "parent_id": None,
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Child",
                    "hierarchy_node_id": "PFX___N2",
                    "parent_id": "N1",  # No direct match; suffix lookup matches PFX___N1
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "C",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Parent", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_indicator_code_fallback_title(self):
        """When title is empty, indicator_code drives the raw_title path."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Parent",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "gross_domestic_product",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Parent", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_parent_unit_scale_inheritance_via_traversal(self):
        """A grandchild inherits unit/scale from grandparent via traversal."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Root",
                    "is_category_header": True,
                    "hierarchy_node_id": "r",
                    "unit": "US Dollar",
                    "scale": "Millions",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Mid",
                    "is_category_header": True,
                    "hierarchy_node_id": "m",
                    "parent_id": "r",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Leaf",
                    "hierarchy_node_id": "leaf",
                    "parent_id": "m",
                    "value": 7.0,
                    "indicator_code": "L",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Root", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_first_level0_data_matches_hierarchy_name(self):
        """If first level-0 title matches hierarchy_name, no extra table header is added."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": False,
                    "hierarchy_node_id": "n1",
                    "value": 3.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "TR",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        titles = [idx[0] for idx in result.index]
        assert not any(t.strip() == "TRADE" for t in titles)

    def test_bop_suffix_only_header_skipped(self):
        """Headers whose title is a BOP-only suffix are skipped."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Real Header",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Credit",
                    "is_category_header": True,
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Real Header, Goods",
                    "hierarchy_node_id": "n3",
                    "parent_id": "n2",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Real Header", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        titles = [idx[0] for idx in result.index]
        assert not any(t.strip().endswith("Credit") and "▸" in t for t in titles)

    def test_financial_corporations_prefix_strip(self):
        """Header titles starting with 'Financial corporations, ' have that prefix stripped."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Financial corporations, Survey",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Financial corporations, Survey, Detail",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {
            "table": {"hierarchy_name": "Financial corporations", "dataflow_id": "BOP"}
        }
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        titles = [idx[0] for idx in result.index]
        assert any("Survey" in t for t in titles)

    def test_depository_corporations_prefix_strip(self):
        """Header titles starting with 'Depository corporations, ' have prefix stripped."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Depository corporations, Items",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Depository corporations, Items, Specific",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {
            "table": {"hierarchy_name": "Depository corporations", "dataflow_id": "BOP"}
        }
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        titles = [idx[0] for idx in result.index]
        assert any("Items" in t for t in titles)

    def test_paren_unit_suffix_stripped_in_pivot(self):
        """A trailing parenthetical unit suffix is captured separately."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Indicator (US Dollar)",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Detail, Transactions",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "D",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Indicator", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_bop_credit_promotion_to_ancestor_title(self):
        """A child Credit row is rewritten to use its ancestor title as base."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Goods Total",
                    "is_category_header": True,
                    "hierarchy_node_id": "h0",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Goods Total, Credit",
                    "hierarchy_node_id": "h1",
                    "parent_id": "h0",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Goods Total", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_two_dates_with_limit(self):
        """Two dates with limit pivots correctly through pivot_table_data."""
        records = [
            {
                "title": "Trade",
                "country": "USA",
                "country_code": "USA",
                "date": "2020-01-01",
                "value": 0.0,
                "level": 0,
                "order": 1.0,
                "is_category_header": True,
                "hierarchy_node_id": "n1",
                "parent_id": None,
                "indicator_code": None,
                "unit": "",
                "scale": "",
                "symbol": "S",
            },
            {
                "title": "Trade, Goods",
                "country": "USA",
                "country_code": "USA",
                "date": "2020-01-01",
                "value": 5.0,
                "level": 1,
                "order": 2.0,
                "is_category_header": False,
                "hierarchy_node_id": "n2",
                "parent_id": "n1",
                "indicator_code": "TRD_G",
                "unit": "US Dollar",
                "scale": "Millions",
                "symbol": "S",
            },
            {
                "title": "Trade, Goods",
                "country": "USA",
                "country_code": "USA",
                "date": "2021-01-01",
                "value": 6.0,
                "level": 1,
                "order": 2.0,
                "is_category_header": False,
                "hierarchy_node_id": "n2",
                "parent_id": "n1",
                "indicator_code": "TRD_G",
                "unit": "US Dollar",
                "scale": "Millions",
                "symbol": "S",
            },
        ]
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_data(records, country="USA", limit=2, metadata=meta)
        assert isinstance(result, pd.DataFrame)

    def test_counterpart_country_individual_only(self):
        """All counterpart countries are individual (no group code)."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "GBR",
                    "counterpart_country": "United Kingdom",
                    "indicator_code": "B",
                    "series_id": "s1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 3.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "DEU",
                    "counterpart_country": "Germany",
                    "indicator_code": "B",
                    "series_id": "s2",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        titles = [idx[0] for idx in result.index]
        assert any("United Kingdom" in t or "Germany" in t for t in titles)

    def test_counterpart_country_all_zero_skipped(self):
        """Zero-only counterpart country values are skipped."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 0.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "G001",
                    "counterpart_country": "World",
                    "indicator_code": "B",
                    "series_id": "s1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 0.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "G002",
                    "counterpart_country": "Europe",
                    "indicator_code": "B",
                    "series_id": "s2",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 0.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "GBR",
                    "counterpart_country": "United Kingdom",
                    "indicator_code": "B",
                    "series_id": "s3",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        titles = [idx[0] for idx in result.index]
        assert all("Europe" not in t for t in titles)

    def test_no_symbol_column_fallback(self):
        """When no dim_code columns and no symbol, the loop just skips."""
        df = pd.DataFrame(
            [
                {
                    "title": "GDP",
                    "level": 0,
                    "order": 1.0,
                    "country": "USA",
                    "country_code": "USA",
                    "date": "2020-01-01",
                    "value": 5.0,
                    "unit": "",
                    "scale": "",
                    "is_category_header": False,
                    "hierarchy_node_id": "n1",
                    "parent_id": None,
                    "indicator_code": "GDP",
                    "symbol": "S",
                }
            ]
        )
        meta = {"table": {"hierarchy_name": "GDP", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_isora_topic_indicator(self):
        """ISORA dataflow with 'INDICATORS BY TOPIC' in title keeps the header."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "INDICATORS BY TOPIC",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Detail value",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 7.0,
                    "unit": "Percent",
                    "scale": "Units",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {
            "table": {
                "hierarchy_name": "INDICATORS BY TOPIC",
                "dataflow_id": "OTHER",
            }
        }
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        titles = [idx[0] for idx in result.index]
        assert any("INDICATORS BY TOPIC" in t for t in titles)

    def test_dim_value_in_title_only_uses_iterrows_path(self):
        """Test that title without unit/scale parses from title for an order with NaN unit."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Population (Millions)",
                    "is_category_header": False,
                    "hierarchy_node_id": "n1",
                    "value": 100.0,
                    "indicator_code": "POP",
                    "unit": "",
                    "scale": "",
                }
            ]
        )
        meta = {"table": {"hierarchy_name": "Population", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)


class TestPivotIndicatorModeExtras:
    """Extra tests for pivot_indicator_mode branches."""

    def test_no_unit_no_scale_parsed_from_title(self):
        """When unit/scale are missing, they get parsed from title."""
        df = pd.DataFrame(
            [
                {
                    "title": "GDP (US Dollar, Millions)",
                    "country": "USA",
                    "date": "2020-01-01",
                    "value": 1.0,
                    "unit": None,
                    "scale": None,
                }
            ]
        )
        result = pivot_indicator_mode(df, ["2020-01-01"], ["USA"])
        assert not result.empty

    def test_missing_date_value(self):
        """A date with no value is stored as None."""
        df = pd.DataFrame(
            [
                {
                    "title": "GDP",
                    "country": "USA",
                    "date": "2020-01-01",
                    "value": 5.0,
                    "unit": "U",
                    "scale": "S",
                },
            ]
        )
        result = pivot_indicator_mode(df, ["2020-01-01", "2021-01-01"], ["USA"])
        assert not result.empty


class TestExtractUnitFromLabelExtra:
    """Additional tests for extract_unit_from_label edge cases."""

    def test_paren_with_no_leading_space_at_zero(self):
        """A label that is exactly '(X)' has paren_start == 0 and returns None via the path."""
        assert extract_unit_from_label("(Percent)") is None

    def test_comma_split_no_second_part(self):
        """No comma at all means rsplit returns one part."""
        assert extract_unit_from_label("Population") is None


class TestPivotTableModeMoreBranches:
    """More branch tests for pivot_table_mode."""

    @staticmethod
    def _base_df(rows: list[dict[str, Any]]) -> pd.DataFrame:
        """Default row builder with NaN value default."""
        defaults = {
            "title": "",
            "level": 0,
            "order": 0.0,
            "country": "USA",
            "country_code": "USA",
            "date": "2020-01-01",
            "value": float("nan"),
            "unit": "",
            "scale": "",
            "is_category_header": False,
            "hierarchy_node_id": None,
            "parent_id": None,
            "indicator_code": None,
            "symbol": "S",
        }
        out = []
        for r in rows:
            d = dict(defaults)
            d.update(r)
            out.append(d)
        return pd.DataFrame(out)

    def test_header_with_own_data_and_dim_groups(self):
        """A parent order that has own data AND multiple sector dim groups."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Indicator",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                    "value": 100.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S1",
                    "sector": "Households",
                    "indicator_code": "X",
                    "series_id": "a",
                },
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Indicator",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                    "value": 200.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S2",
                    "sector": "Firms",
                    "indicator_code": "X",
                    "series_id": "b",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Indicator, Sub",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 50.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S1",
                    "sector": "Households",
                    "indicator_code": "Y",
                    "series_id": "c",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Indicator, Sub",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 60.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S2",
                    "sector": "Firms",
                    "indicator_code": "Y",
                    "series_id": "d",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Indicator", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_multi_dim_non_uniform_unit_scale(self):
        """A multi-dim order with mixed units/scales pulls suffix from first dr."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Parent",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 1.0,
                    "unit": "Percent",
                    "scale": "Units",
                    "sector_code": "S1",
                    "sector": "A",
                    "indicator_code": "X",
                    "series_id": "p1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S2",
                    "sector": "B",
                    "indicator_code": "X",
                    "series_id": "p2",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Parent", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_isora_underscored_promoted_title_continues(self):
        """An ISORA title with '___' is skipped."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "1. INDICATORS BY TOPIC",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "internal___thing",
                    "is_category_header": True,
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Detail",
                    "hierarchy_node_id": "n3",
                    "parent_id": "n2",
                    "value": 7.0,
                    "unit": "Percent",
                    "scale": "Units",
                    "indicator_code": "Y",
                },
            ]
        )
        meta = {
            "table": {
                "hierarchy_name": "1. INDICATORS BY TOPIC",
                "dataflow_id": "ISORA",
            }
        }
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_bop_header_skipped_via_skipped_parent(self):
        """A BOP-only header gets tracked as skipped parent."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Credit",  # BOP-only header
                    "is_category_header": True,
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "indicator_code": "CRD",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Trade, Credit, Goods",
                    "hierarchy_node_id": "n3",
                    "parent_id": "n2",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_bop_credit_promotion_with_meaningful_ancestor(self):
        """A child Credit row picks up the ancestor header that starts with its base."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Goods Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "h0",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Goods, Credit",
                    "hierarchy_node_id": "h1",
                    "parent_id": "h0",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Goods Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_counterpart_country_individual_zero_skipped(self):
        """Individual counterpart with all-zero values is skipped."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "GBR",
                    "counterpart_country": "United Kingdom",
                    "indicator_code": "B",
                    "series_id": "s1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 0.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "DEU",
                    "counterpart_country": "Germany",
                    "indicator_code": "B",
                    "series_id": "s2",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        titles = [idx[0] for idx in result.index]
        assert any("United Kingdom" in t for t in titles)

    def test_bop_skipped_parent_with_underscores(self):
        """Skipped BOP parent with '___' in node_id triggers the suffix-split branch."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "prefix___n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Credit",
                    "is_category_header": True,
                    "hierarchy_node_id": "PFX___N2",
                    "parent_id": "prefix___n1",
                    "indicator_code": None,
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Trade, Credit, Goods",
                    "hierarchy_node_id": "X___N3",
                    "parent_id": "PFX___N2",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_bop_skipped_parent_only_indicator_code(self):
        """A skipped header with only indicator_code (no node id) is tracked."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Credit",
                    "is_category_header": True,
                    "hierarchy_node_id": None,
                    "parent_id": "n1",
                    "indicator_code": "CRED_IND",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Trade, Credit, Goods",
                    "hierarchy_node_id": "n3",
                    "parent_id": "CRED_IND",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_get_sort_value_non_numeric(self):
        """get_sort_value catches non-numeric values via try/except."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": "not-a-number",
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "GBR",
                    "counterpart_country": "United Kingdom",
                    "indicator_code": "B",
                    "series_id": "s1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Bilateral",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": "also-not-numeric",
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "counterpart_country_code": "G001",
                    "counterpart_country": "World",
                    "indicator_code": "B",
                    "series_id": "s2",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)


class TestHierarchyContextMore:
    """Targeted branch coverage for HierarchyContext methods."""

    def test_break_on_lower_level_sibling_lookup(self):
        """_get_true_siblings breaks once a lower-level row is encountered after target."""
        ctx = HierarchyContext(
            [
                (1.0, "ParentA", 0, True),
                (2.0, "A1", 1, False),
                (3.0, "A2", 1, False),
                (4.0, "ParentB", 0, True),
                (5.0, "B1", 1, False),
            ]
        )
        sibs = ctx._get_true_siblings(2.0, 1)
        titles = {t for _, t in sibs}
        assert titles == {"A1", "A2"}

    def test_best_suffix_repeats_level_skipped(self):
        """A second ancestor at the same level is skipped (line 697)."""
        ctx = HierarchyContext(
            [
                (1.0, "Older Special", 0, True),
                (2.0, "Closer Special", 0, True),
                (3.0, "X, Closer Special", 1, False),
            ]
        )
        result = ctx.find_best_suffix(3.0, "X, Closer Special")
        assert result == ", Closer Special"

    def test_best_suffix_net_acq_branch(self):
        """'Net acquisition of financial assets' ancestor is preserved."""
        ctx = HierarchyContext(
            [
                (1.0, "Net acquisition of financial assets", 0, True),
                (2.0, "X, Net acquisition of financial assets", 1, False),
            ]
        )
        result = ctx.find_best_suffix(2.0, "X, Net acquisition of financial assets")
        assert result == ", Net acquisition of financial assets"

    def test_ancestor_part_prefix_repeats_level_skipped(self):
        """Repeat ancestor levels are skipped via levels_seen (line 778)."""
        ctx = HierarchyContext(
            [
                (1.0, "Older corporations", 0, True),
                (2.0, "Financial corporations", 0, True),
                (3.0, "Financial corporations, X", 1, False),
            ]
        )
        result = ctx.find_ancestor_part_prefix(3.0, "Financial corporations, X")
        assert result == "Financial corporations, "

    def test_ancestor_part_prefix_liabilities_expansion(self):
        """Liabilities ancestor expansion is exercised (lines 797-799)."""
        ctx = HierarchyContext(
            [
                (1.0, "Liabilities", 0, True),
                (2.0, "Total liabilities, X", 1, False),
            ]
        )
        result = ctx.find_ancestor_part_prefix(2.0, "Total liabilities, X")
        assert result == "Total liabilities, "

    def test_ancestor_part_prefix_normalized_dash(self):
        """A normalized dash mismatch falls through to the normalized branch."""
        ctx = HierarchyContext(
            [
                (1.0, "Financial-Corporations", 0, True),
                (2.0, "Financial corporations, Detail", 1, False),
            ]
        )
        result = ctx.find_ancestor_part_prefix(2.0, "Financial corporations, Detail")
        assert result == "Financial corporations, "

    def test_simplify_title_only_paren_strip(self):
        """A title with only a unit paren -- no prefix/suffix to find."""
        ctx = HierarchyContext([(1.0, "Plain (Percent)", 0, False)])
        assert ctx.simplify_title(1.0, "Plain (Percent)") == "Plain"


class TestExtractUnitFromLabelMore:
    """A few more targeted unit-extraction tests."""

    def test_paren_with_percent_sign(self):
        """A trailing '(%)' is detected."""
        assert extract_unit_from_label("Inflation (%)") == "%"


class TestPivotTableModeMoreEdgeCases:
    """Additional pivot_table_mode edge cases."""

    @staticmethod
    def _base_df(rows: list[dict[str, Any]]) -> pd.DataFrame:
        """Default builder with NaN value."""
        defaults = {
            "title": "",
            "level": 0,
            "order": 0.0,
            "country": "USA",
            "country_code": "USA",
            "date": "2020-01-01",
            "value": float("nan"),
            "unit": "",
            "scale": "",
            "is_category_header": False,
            "hierarchy_node_id": None,
            "parent_id": None,
            "indicator_code": None,
            "symbol": "S",
        }
        out = []
        for r in rows:
            d = dict(defaults)
            d.update(r)
            out.append(d)
        return pd.DataFrame(out)

    def test_parent_lookup_break_when_missing(self):
        """An unresolvable parent_id chain breaks the parent traversal loop."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Trade, Goods",
                    "hierarchy_node_id": "n2",
                    "parent_id": "completely_missing_id",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_unit_like_transformation_filtered(self):
        """A TYPE_OF_TRANSFORMATION dim with a unit-like value is filtered from label."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Detail",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "type_of_transformation_code": "USD",
                    "type_of_transformation": "US dollar",
                    "sector_code": "S1",
                    "sector": "Households",
                    "indicator_code": "X",
                    "series_id": "p1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Detail",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 7.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "type_of_transformation_code": "USD",
                    "type_of_transformation": "US dollar",
                    "sector_code": "S2",
                    "sector": "Firms",
                    "indicator_code": "X",
                    "series_id": "p2",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_isora_underscored_promoted_title(self):
        """An ISORA promoted header with '___' in title is skipped (line 1714)."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "1. Topic",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Abc___Xyz",
                    "is_category_header": True,
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Detail",
                    "hierarchy_node_id": "n3",
                    "parent_id": "n2",
                    "value": 7.0,
                    "unit": "Percent",
                    "scale": "Units",
                    "indicator_code": "Y",
                },
            ]
        )
        meta = {
            "table": {
                "hierarchy_name": "1. INDICATORS BY TOPIC",
                "dataflow_id": "ISORA",
            }
        }
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_track_skipped_parent_continues_for_empty(self):
        """_track_skipped_parent_ids continues when a value is empty (line 1598)."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Credit",
                    "is_category_header": True,
                    "hierarchy_node_id": None,
                    "parent_id": "n1",
                    "indicator_code": None,
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Trade, Credit, Goods",
                    "hierarchy_node_id": "n3",
                    "parent_id": "n2",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_promote_level_break_on_missing_parent(self):
        """_promote_level_if_parent_skipped breaks when lookup fails (line 1622)."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Credit",
                    "is_category_header": True,
                    "hierarchy_node_id": "n2",
                    "parent_id": "missing_parent",
                    "indicator_code": "C",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Trade, Credit, Goods",
                    "hierarchy_node_id": "n3",
                    "parent_id": "n2",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_prune_deeper_headers(self):
        """When level drops, deeper levels' last_meaningful_header is pruned."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Root",
                    "is_category_header": True,
                    "hierarchy_node_id": "r",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Mid",
                    "is_category_header": True,
                    "hierarchy_node_id": "m",
                    "parent_id": "r",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Mid leaf",
                    "hierarchy_node_id": "ml",
                    "parent_id": "m",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
                {
                    "order": 4.0,
                    "level": 0,
                    "title": "OtherRoot",
                    "is_category_header": True,
                    "hierarchy_node_id": "r2",
                },
                {
                    "order": 5.0,
                    "level": 1,
                    "title": "OtherRoot, sub",
                    "hierarchy_node_id": "r2s",
                    "parent_id": "r2",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "Y",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Root", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_paren_unit_suffix_kept_for_promoted_header(self):
        """A promoted header carrying parenthetical unit applies original_unit_suffix."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Indicator (Percent of GDP)",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Indicator, X",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "Percent",
                    "scale": "Units",
                    "indicator_code": "X",
                },
                {
                    "order": 3.0,
                    "level": 1,
                    "title": "Indicator, Y",
                    "hierarchy_node_id": "n3",
                    "parent_id": "n1",
                    "value": 10.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "Y",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Indicator", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_dim_dedup_same_grouping_key(self):
        """When two raw rows share the same grouping_key, the later is appended (1562-1565)."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Parent",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S1",
                    "sector": "A",
                    "type_of_transformation_code": "T1",
                    "type_of_transformation": "Type1",
                    "indicator_code": "X",
                    "series_id": "p1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S1",
                    "sector": "A",
                    "type_of_transformation_code": "T1",
                    "type_of_transformation": "Type1",
                    "indicator_code": "X",
                    "series_id": "p2",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 3.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S2",
                    "sector": "B",
                    "type_of_transformation_code": "T2",
                    "type_of_transformation": "Type2",
                    "indicator_code": "X",
                    "series_id": "p3",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Parent", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_bop_promotion_to_ancestor_via_meaningful_header(self):
        """BOP suffix child finds a non-BOP ancestor header and rewrites itself."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Goods Trade Account",
                    "is_category_header": True,
                    "hierarchy_node_id": "h0",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Goods, Credit",
                    "hierarchy_node_id": "h1",
                    "parent_id": "h0",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
                {
                    "order": 3.0,
                    "level": 1,
                    "title": "Goods, Debit",
                    "hierarchy_node_id": "h2",
                    "parent_id": "h0",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "Y",
                },
            ]
        )
        meta = {
            "table": {"hierarchy_name": "Goods Trade Account", "dataflow_id": "BOP"}
        }
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_raw_row_unit_scale_parsed_from_title(self):
        """A row missing unit/scale picks them up from title parsing."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Goods (US Dollar, Millions)",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "",
                    "scale": "",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_empty_order_df_skipped(self):
        """If sorted_orders iterates a value not in df, the loop continues (line 1669)."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Trade, Goods",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "TRD_G",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)


class TestParseUnitAndScaleExtra:
    """Additional tests for parse_unit_and_scale edge cases."""

    def test_ratio_of_pattern(self):
        """'Ratio of X' splits into unit Ratio and scale 'of X'."""
        unit, scale = parse_unit_and_scale("Ratio of GDP")
        assert unit == "Ratio"
        assert scale == "of Gdp"

    def test_number_of_pattern(self):
        """'Number of X' splits into unit Number."""
        unit, scale = parse_unit_and_scale("Number of People")
        assert unit == "Number"
        assert scale == "of People"

    def test_index_of_pattern(self):
        """'Index of X' splits into unit Index."""
        unit, scale = parse_unit_and_scale("Index of Prices")
        assert unit == "Index"
        assert scale == "of Prices"


class TestHierarchyContextEmptyAncestor:
    """Edge cases for ancestor traversal with empty titles."""

    def test_ancestor_part_prefix_skips_empty_title(self):
        """An ancestor row with an empty title is skipped via continue."""
        ctx = HierarchyContext(
            [
                (1.0, "", 0, True),
                (2.0, "Top context", 1, True),
                (3.0, "Top context, Detail", 2, False),
            ]
        )
        out = ctx.find_ancestor_part_prefix(3.0, "Top context, Detail")
        assert out == "Top context, "

    def test_ancestor_part_prefix_financial_assets_alias(self):
        """An ancestor containing 'Financial assets' adds the alias to ancestor_parts."""
        ctx = HierarchyContext(
            [
                (1.0, "Holdings, Financial assets", 0, True),
                (2.0, "Financial assets, Bonds", 1, False),
            ]
        )
        out = ctx.find_ancestor_part_prefix(2.0, "Financial assets, Bonds")
        assert out == "Financial assets, "

    def test_ancestor_part_prefix_case_insensitive_match(self):
        """A case-insensitive match returns the matched slice from target_title."""
        ctx = HierarchyContext(
            [
                (1.0, "Other Investment", 0, True),
                (2.0, "other investment, Loans", 1, False),
            ]
        )
        out = ctx.find_ancestor_part_prefix(2.0, "other investment, Loans")
        assert out == "other investment, "

    def test_ancestor_part_prefix_case_insensitive_bop_remainder_skipped(self):
        """A case-insensitive match whose remainder is BOP-only continues the loop."""
        ctx = HierarchyContext(
            [
                (1.0, "Other Investment", 0, True),
                (2.0, "other investment, Net", 1, False),
            ]
        )
        out = ctx.find_ancestor_part_prefix(2.0, "other investment, Net")
        assert out is None


class TestSimplifyTitleExtraPaths:
    """Additional paths through simplify_title."""

    def test_part_prefix_strip_via_ancestor_part(self):
        """An ancestor whose part matches strips via the part_prefix loop."""
        ctx = HierarchyContext(
            [
                (1.0, "Z, Assets", 0, True),
                (2.0, "Assets, X", 1, False),
            ]
        )
        assert ctx.simplify_title(2.0, "Assets, X") == "X"

    def test_sibling_strip_leaves_bop_only_restores(self):
        """A sibling-prefix strip that leaves only 'Net' restores original title."""
        ctx = HierarchyContext(
            [
                (1.0, "Foo, Bar, Net", 0, False),
                (2.0, "Foo, Bar, X", 0, False),
                (3.0, "Foo, Bar, Y", 0, False),
            ]
        )
        assert ctx.simplify_title(1.0, "Foo, Bar, Net") == "Foo, Bar, Net"

    def test_part_prefix_consumes_full_title_restores(self):
        """A part_prefix strip that empties the title restores original."""
        ctx = HierarchyContext(
            [
                (1.0, "Z, Assets", 0, True),
                (2.0, "Assets, ", 1, False),
            ]
        )
        assert ctx.simplify_title(2.0, "Assets, ") == "Assets, "


class TestPivotTableModeCoverageGaps:
    """Targeted pivot_table_mode coverage gaps."""

    @staticmethod
    def _base_df(rows: list[dict[str, Any]]) -> pd.DataFrame:
        """Default row builder.

        Parameters
        ----------
        rows : list[dict[str, Any]]
            List of partial row dicts merged with defaults.

        Returns
        -------
        pd.DataFrame
            Built DataFrame.
        """
        defaults = {
            "title": "",
            "level": 0,
            "order": 0.0,
            "country": "USA",
            "country_code": "USA",
            "date": "2020-01-01",
            "value": float("nan"),
            "unit": "",
            "scale": "",
            "is_category_header": False,
            "hierarchy_node_id": None,
            "parent_id": None,
            "indicator_code": None,
            "symbol": "S",
        }
        out = []
        for r in rows:
            d = dict(defaults)
            d.update(r)
            out.append(d)
        return pd.DataFrame(out)

    def test_country_without_data_for_order_skipped(self):
        """A country lacking rows at a given order hits the country_df.empty continue."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Trade, Goods",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "G",
                    "country": "USA",
                    "country_code": "USA",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Trade, Goods",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 6.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "G",
                    "country": "CAN",
                    "country_code": "CAN",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA", "CAN", "MEX"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_no_symbol_column_falls_back_to_empty(self):
        """A DataFrame with neither dim_code cols nor symbol triggers the symbol-fallback line."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "GDP (Millions of US Dollar)",
                    "is_category_header": False,
                    "hierarchy_node_id": "n1",
                    "value": 10.0,
                    "indicator_code": "G",
                },
            ]
        ).drop(columns=["symbol", "indicator_code"])
        meta = {"table": {"hierarchy_name": "GDP", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_unit_scale_parsed_from_title_fills_missing(self):
        """A row without unit/scale parses them from the title."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Trade, Goods (Millions, US Dollar)",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "indicator_code": "G",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_format_dim_labels_empty_grouping_key_returns_empty(self):
        """An empty grouping_key yields an empty dim label string."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Top",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Top, A",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "A",
                    "sector_code": "S1",
                    "sector": "AA",
                    "series_id": "a",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Top, B",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "B",
                    "sector_code": "S2",
                    "sector": "BB",
                    "series_id": "b",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Top, C",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 3.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "C",
                    "series_id": "c",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Top", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_unit_like_transformation_filtered_from_labels(self):
        """A unit-like TYPE_OF_TRANSFORMATION value is filtered from dim labels."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Top",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Top, Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "type_of_transformation_code": "T1",
                    "type_of_transformation": "US dollar",
                    "indicator_code": "A",
                    "series_id": "a",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Top, Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "type_of_transformation_code": "T2",
                    "type_of_transformation": "Euro",
                    "indicator_code": "A",
                    "series_id": "b",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Top", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_track_skipped_with_empty_string_node_id(self):
        """A bop-only header with empty hierarchy_node_id continues past the empty value."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Trade",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Credit",
                    "is_category_header": True,
                    "hierarchy_node_id": "",
                    "parent_id": "n1",
                    "indicator_code": "CRED",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Trade, Credit, Goods",
                    "hierarchy_node_id": "n3",
                    "parent_id": "CRED",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "X",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Trade", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_data_row_best_suffix_stripped(self):
        """A data row whose title ends with an ancestor's name strips the suffix."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Survey Metric",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Detail, Survey Metric",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "D",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Survey Metric", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_data_row_part_prefix_stripped(self):
        """A data row whose title starts with an ancestor part strips the prefix."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Z, Trade total",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Trade total, Detail",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 5.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "D",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Z, Trade total", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_bop_promotion_skips_empty_and_bop_ancestor_levels(self):
        """BOP promotion walks past empty and bop-ending ancestor levels to a meaningful one."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Top",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Top, Sub, Net",
                    "is_category_header": True,
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                },
                {
                    "order": 3.0,
                    "level": 2,
                    "title": "Top, Sub, Net, Detail",
                    "hierarchy_node_id": "n3",
                    "parent_id": "n2",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "D",
                },
                {
                    "order": 4.0,
                    "level": 3,
                    "title": "Top, Sub, Net, Detail, Credit",
                    "hierarchy_node_id": "n4",
                    "parent_id": "n3",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "indicator_code": "E",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Top", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)

    def test_multi_dim_no_counterpart_with_empty_grouping_row(self):
        """A row at a multi-dim order with no dim values falls into the empty-grouping branch."""
        df = self._base_df(
            [
                {
                    "order": 1.0,
                    "level": 0,
                    "title": "Top",
                    "is_category_header": True,
                    "hierarchy_node_id": "n1",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Top, Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 1.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S1",
                    "sector": "A",
                    "indicator_code": "X",
                    "series_id": "a",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Top, Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 2.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": "S2",
                    "sector": "B",
                    "indicator_code": "X",
                    "series_id": "b",
                },
                {
                    "order": 2.0,
                    "level": 1,
                    "title": "Top, Item",
                    "hierarchy_node_id": "n2",
                    "parent_id": "n1",
                    "value": 3.0,
                    "unit": "US Dollar",
                    "scale": "Millions",
                    "sector_code": None,
                    "sector": None,
                    "indicator_code": "X",
                    "series_id": "c",
                },
            ]
        )
        meta = {"table": {"hierarchy_name": "Top", "dataflow_id": "BOP"}}
        result = pivot_table_mode(df, ["2020-01-01"], ["USA"], meta)
        assert isinstance(result, pd.DataFrame)
