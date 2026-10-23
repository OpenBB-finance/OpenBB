"""Presentation table utilities for IMF provider."""

from __future__ import annotations

import re
import warnings
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def extract_unit_from_label(label: str) -> str | None:
    """Extract unit information from an indicator label.

    Parameters
    ----------
    label : str
        The indicator label to parse.

    Returns
    -------
    str | None
        The extracted unit string, or None if no unit found.
    """
    if not label:
        return None

    if label.endswith(")"):
        paren_start = label.rfind(" (")
        if paren_start > 0:
            suffix_content = label[paren_start + 2 : -1]
            unit_keywords = [
                "dollar",
                "Dollar",
                "USD",
                "Euro",
                "euro",
                "Yen",
                "yen",
                "Percent",
                "percent",
                "%",
                "Millions",
                "Billions",
                "Thousands",
                "Units",
                "Per capita",
                "per capita",
                "Index",
                "index",
                "Domestic currency",
                "National currency",
                "currency",
                "SDR",
            ]
            if any(kw in suffix_content for kw in unit_keywords):
                return suffix_content

    parts = label.rsplit(", ", 1)
    if len(parts) == 2:
        last_part = parts[1]
        last_part_lower = last_part.lower()
        if " per " in last_part_lower:
            return last_part
        unit_keywords_lower = [
            "dollar",
            "percent",
            "index",
            "ratio",
            "currency",
            "capita",
            "cent",
        ]
        if any(kw in last_part_lower for kw in unit_keywords_lower):
            return last_part

    return None


def parse_unit_and_scale(unit_string: str | None) -> tuple[str | None, str | None]:
    """Parse a combined unit string into separate scale and unit components.

    Parameters
    ----------
    unit_string : str | None
        The combined unit/scale string extracted from a label.

    Returns
    -------
    tuple[str | None, str | None]
        A tuple of (unit, scale) where:
        - unit: The unit of measurement (e.g., "US dollar", "Percent")
        - scale: The scale/multiplier (e.g., "Per capita", "Millions", "per metric tonne")
    """
    if not unit_string:
        return None, None

    unit_of_patterns = ["Percent of ", "Ratio of ", "Index of ", "Number of "]
    for pattern in unit_of_patterns:
        if unit_string.startswith(pattern):
            unit = pattern.replace(" of ", "").strip()
            scale = "of " + unit_string[len(pattern) :].strip().title()
            return unit, scale

    if " per " in unit_string.lower():
        lower_str = unit_string.lower()
        per_idx = lower_str.find(" per ")
        if per_idx > 0:
            unit = unit_string[:per_idx].strip()
            scale = unit_string[per_idx + 1 :].strip().title()
            return unit, scale

    scale_prefixes = [
        "Per capita, ",
        "Percent, ",
        "Millions, ",
        "Billions, ",
        "Thousands, ",
        "Mean, ",
    ]

    for prefix in scale_prefixes:
        if unit_string.startswith(prefix):
            scale = prefix.rstrip(", ")
            unit = unit_string[len(prefix) :]
            return unit, scale

    scale_suffixes = [
        ", Millions",
        ", Billions",
        ", Thousands",
        ", Per capita",
    ]

    for suffix in scale_suffixes:
        if unit_string.endswith(suffix):
            scale = suffix.lstrip(", ")
            unit = unit_string[: -len(suffix)]
            return unit, scale

    unit_keywords = [
        "Percent",
        "US dollar",
        "US Dollar",
        "Index",
        "Ratio",
        "SDR",
        "EUR",
        "Domestic currency",
        "National currency",
        "Euro",
    ]
    last_comma = unit_string.rfind(", ")
    if last_comma > 0:
        potential_unit = unit_string[last_comma + 2 :]
        if potential_unit in unit_keywords:
            scale = unit_string[:last_comma]
            return potential_unit, scale

    scale_only_values = ["Per capita", "Millions", "Billions", "Thousands"]
    if unit_string in scale_only_values:
        return None, unit_string

    return unit_string, None


def strip_title_suffix(title: str) -> str:
    """Strip scale/unit and type suffixes from title.

    Parameters
    ----------
    title : str
        The raw title to process.

    Returns
    -------
    str
        The title with suffixes stripped.
    """
    unit_suffixes = [", Transactions", ", Stocks", ", Flows"]
    for suffix in unit_suffixes:
        if title.endswith(suffix):
            title = title[: -len(suffix)]
            break
    if title.endswith(")"):
        paren_start = title.rfind(" (")
        if paren_start > 0:
            suffix_content = title[paren_start + 2 : -1]
            unit_patterns = [
                "Millions",
                "Billions",
                "Thousands",
                "Percent",
                "Units",
            ]
            is_unit_suffix = any(pattern in suffix_content for pattern in unit_patterns)
            if is_unit_suffix:
                title = title[:paren_start]
    return title


def format_unit_suffix(unit: str | None, scale: str | None) -> str:
    """Format unit and scale into a display suffix.

    Parameters
    ----------
    unit : str | None
        The unit of measurement (e.g., "US Dollar", "Percent").
    scale : str | None
        The scale/multiplier (e.g., "Millions", "Billions").

    Returns
    -------
    str
        A formatted suffix like "(Percent)" or "(US Dollar, Millions)",
        or empty string if no meaningful unit/scale provided.
    """
    parts = []
    if unit and isinstance(unit, str) and unit not in ("-", "nan", ""):
        parts.append(unit)
    if scale and isinstance(scale, str) and scale not in ("Units", "-", "nan", ""):
        parts.append(scale)
    if parts:
        return f" ({', '.join(parts)})"
    return ""


UNIT_SCALE_PATTERNS = {
    "Millions",
    "Billions",
    "Thousands",
    "Percent",
    "Units",
}

UNIT_KEYWORDS = {
    "dollars",
    "cents",
    "pound",
    "tonne",
    "ton",
    "meter",
    "metre",
    "liter",
    "litre",
    "barrel",
    "ounce",
    "kilogram",
    "gram",
    "index",
    "percent",
    "ratio",
    "rate",
    "number",
    "per",
}


def extract_unit_scale_from_title(title: str) -> tuple[str | None, str | None]:
    """Extract unit/scale from a trailing parenthetical suffix or comma-separated part."""
    if not title:
        return None, None

    unit_val: str | None = None
    scale_val: str | None = None

    if title.endswith(")"):
        paren_start = title.rfind(" (")
        if paren_start > 0:
            suffix_content = title[paren_start + 2 : -1]
            if any(pattern in suffix_content for pattern in UNIT_SCALE_PATTERNS):
                parts = [p.strip() for p in suffix_content.split(",") if p.strip()]

                if len(parts) == 1:
                    only = parts[0]
                    if only in UNIT_SCALE_PATTERNS:
                        scale_val = only
                    else:
                        unit_val = only
                elif len(parts) >= 2:
                    unit_val = parts[0]
                    scale_val = parts[1]

                return unit_val, scale_val

    parts = [p.strip() for p in title.split(",")]
    if len(parts) >= 2:
        last_part = parts[-1].lower()
        if any(kw in last_part for kw in UNIT_KEYWORDS):
            unit_val = parts[-1].strip()
            return unit_val, scale_val

    return None, None


def is_bop_suffix_only(text: str) -> bool:
    """Check if text is only a BOP-style suffix that lacks meaningful context.

    Parameters
    ----------
    text : str
        The text to check.

    Returns
    -------
    bool
        True if text is just a BOP suffix without meaningful context.
    """
    if not text:
        return False

    normalized = text.lstrip(", :")
    if not normalized:
        return True

    first_word = normalized.split()[0] if normalized.split() else ""
    if first_word and first_word[0].islower() and not first_word[0].isdigit():
        return True

    check_text = normalized
    if check_text.endswith(")"):
        paren_start = check_text.rfind(" (")
        if paren_start > 0:
            check_text = check_text[:paren_start].strip()

    bop_only_terms = {
        "net",
        "credit",
        "debit",
        "assets",
        "liabilities",
        "credit/revenue",
        "debit/expenditure",
        "assets (excl. reserves)",
        "liabilities (incl. net incurrence)",
    }
    return check_text.lower() in bop_only_terms


class HierarchyContext:
    """Manages hierarchical order/title/level data for title stripping.

    Parameters
    ----------
    order_title_level : list[tuple[int | float, str, int, bool]]
        Sorted list of (order, title, level, is_header) tuples representing
        the hierarchical structure.
    """

    def __init__(
        self, order_title_level: list[tuple[int | float, str, int, bool]]
    ) -> None:
        """Initialize with sorted list of hierarchy metadata."""
        self.order_title_level = sorted(order_title_level, key=lambda x: x[0])

    def _get_true_siblings(
        self, target_order: int | float, target_level: int
    ) -> list[tuple[int | float, str]]:
        """Get siblings that share the same parent (consecutive rows at same level)."""
        target_idx = None
        for i, (order, _, level, _) in enumerate(self.order_title_level):
            if order == target_order:
                target_idx = i
                break

        if target_idx is None:
            return []

        siblings: list[tuple[int | float, str]] = []

        start_idx = target_idx
        for i in range(target_idx - 1, -1, -1):
            _, _, level, _ = self.order_title_level[i]
            if level < target_level:
                break
            if level == target_level:
                start_idx = i

        end_idx = target_idx
        for i in range(target_idx + 1, len(self.order_title_level)):
            _, _, level, _ = self.order_title_level[i]
            if level < target_level:
                break
            if level == target_level:
                end_idx = i

        for i in range(start_idx, end_idx + 1):
            order, title, level, _ = self.order_title_level[i]
            if level == target_level:
                siblings.append((order, title))

        return siblings

    def find_sibling_common_prefix(
        self,
        target_order: int | float,
        target_title: str,
        displayed_orders: set[int | float] | None = None,
    ) -> str | None:
        """Find common prefix shared by siblings at the same level.

        Parameters
        ----------
        target_order : int | float
            The order value of the target row.
        target_title : str
            The title to find a common prefix for.
        displayed_orders : set[int | float] | None
            Set of order values that will actually be displayed.

        Returns
        -------
        str | None
            The common prefix including trailing ", " to strip, or None.
        """
        target_level = None
        for order, _, level, _ in self.order_title_level:
            if order == target_order:
                target_level = level
                break

        if target_level is None:
            return None

        siblings = self._get_true_siblings(target_order, target_level)
        if len(siblings) < 3:
            return None

        if displayed_orders is not None:
            siblings = [(o, t) for o, t in siblings if o in displayed_orders]
            if len(siblings) < 3:
                return None

        def get_prefix_segments(title: str) -> list[str]:
            """Split title into prefix segments (each ending with ', ')."""
            segments = []
            parts = re.split(r"(, )", title)
            current = ""
            for _, part in enumerate(parts):
                current += part
                if part == ", ":
                    segments.append(current)
                    current = ""
            return segments

        sibling_titles = [t for _, t in siblings if t]
        if len(sibling_titles) < 3:
            return None

        all_segments = [get_prefix_segments(t) for t in sibling_titles]
        if (
            not all_segments
        ):  # pragma: no cover -- guarded by len(sibling_titles) >= 3 check above
            return None

        min_segments = min(len(s) for s in all_segments)
        common_count = 0
        for i in range(min_segments):
            first_seg = all_segments[0][i].lower()
            if all(segs[i].lower() == first_seg for segs in all_segments):
                common_count += 1
            else:
                break

        if common_count == 0:
            return None

        common_prefix = "".join(all_segments[0][:common_count])

        if not target_title.lower().startswith(common_prefix.lower()):
            return None

        bop_endings = (
            ", Credit",
            ", Debit",
            ", Net",
            ", Credit/Revenue",
            ", Debit/Expenditure",
            ", Assets",
            ", Liabilities",
            " Assets",
            " Liabilities",
        )
        if all(
            any(t.endswith(ending) for ending in bop_endings) for t in sibling_titles
        ):
            return None

        return target_title[: len(common_prefix)]

    def find_bop_group_prefix(
        self,
        target_order: int | float,
        target_title: str,
        displayed_orders: set[int | float] | None = None,
    ) -> str | None:
        """Find BOP-style group prefix for Credit/Debit/Net patterns.

        Parameters
        ----------
        target_order : int | float
            The order value of the target row.
        target_title : str
            The title to find a group prefix for.
        displayed_orders : set[int | float] | None
            Set of order values that will actually be displayed.

        Returns
        -------
        str | None
            The group prefix to strip (e.g., "Goods, "), or None.
        """
        bop_suffixes = [", Credit", ", Debit", ", Net"]

        base_name = None
        our_suffix = None
        for suffix in bop_suffixes:
            if target_title.endswith(suffix):
                base_name = target_title[: -len(suffix)]
                our_suffix = suffix
                break

        if base_name is None:
            return None

        if our_suffix == ", Net":
            return None

        target_level = None
        for order, _, level, _ in self.order_title_level:
            if order == target_order:
                target_level = level
                break

        if target_level is None:
            return None

        siblings = self._get_true_siblings(target_order, target_level)

        if displayed_orders is not None:
            siblings = [(o, t) for o, t in siblings if o in displayed_orders]

        has_matching_net = False
        for _, sib_title in siblings:
            if sib_title == f"{base_name}, Net":
                has_matching_net = True
                break

        if has_matching_net:
            return f"{base_name}, "

        return None

    def find_best_prefix(
        self,
        target_order: int | float,
        target_title: str,
        displayed_orders: set[int | float] | None = None,
    ) -> str | None:
        """Find the longest ancestor title that is a prefix of target_title.

        Parameters
        ----------
        target_order : int | float
            The order value of the target row.
        target_title : str
            The title to find a prefix for.
        displayed_orders : set[int | float] | None
            Set of order values that will actually be displayed.
            If provided, only consider ancestors in this set.

        Returns
        -------
        str | None
            The longest matching prefix, or None if no match found.
        """
        target_idx = None
        target_level = 0
        for i, (order, title, level, _) in enumerate(self.order_title_level):
            if order == target_order:
                target_idx = i
                target_level = level
                break

        if target_idx is None:
            return None

        best_prefix = None
        levels_seen: set = set()
        ancestor_key_phrases: set[str] = set()

        for i in range(target_idx - 1, -1, -1):
            order, title, level, _ = self.order_title_level[i]
            if level < target_level:
                if level in levels_seen:
                    continue
                levels_seen.add(level)

                if displayed_orders is not None and order not in displayed_orders:
                    continue

                if not title:
                    continue

                if target_title.startswith(title) and (
                    best_prefix is None or len(title) > len(best_prefix)
                ):
                    best_prefix = title

                title_lower = title.lower()

                if title_lower.endswith(")"):
                    paren_start = title_lower.rfind(" (")
                    if paren_start > 0:
                        title_lower = title_lower[:paren_start]

                for suffix in [
                    " survey",
                    " (domestic currency, millions)",
                    " (percent of gdp)",
                ]:
                    if title_lower.endswith(suffix):
                        title_lower = title_lower[: -len(suffix)]
                if title_lower:
                    ancestor_key_phrases.add(title_lower.strip())

        if best_prefix is None and ancestor_key_phrases:
            target_lower = target_title.lower()
            target_normalized = target_lower.replace("-", " ")
            for phrase in sorted(ancestor_key_phrases, key=lambda s: -len(s)):
                phrase_normalized = phrase.replace("-", " ")
                for sep in [", ", ": ", " - "]:
                    prefix_pattern = f"{phrase_normalized}{sep}"
                    if target_normalized.startswith(prefix_pattern):
                        prefix_len = len(prefix_pattern)
                        best_prefix = target_title[:prefix_len]
                        break
                if best_prefix:
                    break

        if best_prefix:
            remainder = target_title[len(best_prefix) :].lstrip(", :")
            if is_bop_suffix_only(remainder):
                return None

        return best_prefix

    def find_best_suffix(
        self,
        target_order: int | float,
        target_title: str,
        displayed_orders: set[int | float] | None = None,
    ) -> str | None:
        """Find ancestor context that appears as a suffix in the title.

        Parameters
        ----------
        target_order : int | float
            The order value of the target row.
        target_title : str
            The title to find a suffix for.
        displayed_orders : set[int | float] | None
            Set of order values that will actually be displayed.
            If provided, only consider ancestors in this set.

        Returns
        -------
        str | None
            The matching suffix (including leading ", "), or None if no match.
        """
        target_idx = None
        target_level = 0
        for i, (order, title, level, _) in enumerate(self.order_title_level):
            if order == target_order:
                target_idx = i
                target_level = level
                break

        if target_idx is None:
            return None

        levels_seen: set = set()
        ancestor_parts: set = set()
        protected_suffixes = {
            "Assets",
            "Liabilities",
            "Net",
            "Credit",
            "Debit",
            "Credit/Revenue",
            "Debit/Expenditure",
        }

        for i in range(target_idx - 1, -1, -1):
            order, title, level, _ = self.order_title_level[i]
            if level < target_level:
                if level in levels_seen:
                    continue
                levels_seen.add(level)

                if displayed_orders is not None and order not in displayed_orders:
                    continue

                if not title:
                    continue

                parts = re.split(r", (?=[A-Z:])", title)
                for p in parts:
                    pp = p.strip()
                    if pp:
                        ancestor_parts.add(pp)
                        if pp == "Liabilities":
                            ancestor_parts.add("Net incurrence of liabilities")
                            ancestor_parts.add("Total liabilities")
                        elif pp == "Net acquisition of financial assets":
                            ancestor_parts.add("Net acquisition of financial assets")
                        elif pp == "Financial assets":
                            ancestor_parts.add("Assets")
                        elif "Debtors" in pp:
                            ancestor_parts.add("Net acquisition of financial assets")
                            ancestor_parts.add("Assets")
                        elif "Creditors" in pp:
                            ancestor_parts.add("Net incurrence of liabilities")
                            ancestor_parts.add("Total liabilities")

        if not ancestor_parts:
            return None

        for part in ancestor_parts:
            if part in protected_suffixes:
                continue
            suffix_with_comma = f", {part}"
            if target_title.endswith(suffix_with_comma):
                return suffix_with_comma

        return None

    def find_ancestor_part_prefix(
        self,
        target_order: int | float,
        target_title: str,
        displayed_orders: set[int | float] | None = None,
    ) -> str | None:
        """Find ancestor context parts that appear as a prefix in the title.

        Parameters
        ----------
        target_order : int | float
            The order value of the target row.
        target_title : str
            The title to find a prefix for.
        displayed_orders : set[int | float] | None
            Set of order values that will actually be displayed.
            If provided, only consider ancestors in this set.

        Returns
        -------
        str | None
            The matching prefix (including trailing ", " or ": "), or None.
        """
        target_idx = None
        target_level = 0
        for i, (order, title, level, _) in enumerate(self.order_title_level):
            if order == target_order:
                target_idx = i
                target_level = level
                break

        if target_idx is None:
            return None

        levels_seen: set = set()
        ancestor_parts: set = set()

        for i in range(target_idx - 1, -1, -1):
            order, title, level, _ = self.order_title_level[i]
            if level < target_level:
                if level in levels_seen:
                    continue
                levels_seen.add(level)

                if displayed_orders is not None and order not in displayed_orders:
                    continue

                if not title:
                    continue

                if title == target_title:
                    continue

                parts = re.split(r", (?=[A-Z:])", title)

                for p in parts:
                    pp = p.strip()
                    if pp:
                        ancestor_parts.add(pp)
                        if pp == "Liabilities":
                            ancestor_parts.add("Total liabilities")
                        elif pp == "Financial assets":
                            ancestor_parts.add("Financial assets")

        if not ancestor_parts:
            return None

        strippable_single_words = {"Assets", "Liabilities"}
        target_normalized = target_title.lower().replace("-", " ")
        for part in ancestor_parts:
            if " " not in part and part not in strippable_single_words:
                continue
            part_normalized = part.lower().replace("-", " ")
            for sep in [", ", ": "]:
                prefix_with_sep = f"{part}{sep}"
                if target_title.startswith(prefix_with_sep):
                    remainder = target_title[len(prefix_with_sep) :]
                    if is_bop_suffix_only(remainder):
                        continue
                    return prefix_with_sep
                prefix_normalized = f"{part_normalized}{sep}"
                if target_normalized.startswith(prefix_normalized):
                    remainder = target_title[len(prefix_normalized) :]
                    if is_bop_suffix_only(remainder):
                        continue
                    return target_title[: len(prefix_normalized)]

        if ", " in target_title:
            comma_idx = target_title.index(", ")
            child_prefix = target_title[:comma_idx].lower().replace("-", " ")
            for part in ancestor_parts:
                part_normalized = part.lower().replace("-", " ")
                if part_normalized.startswith(child_prefix) and len(child_prefix) > 10:
                    remainder = target_title[comma_idx + 2 :]
                    if is_bop_suffix_only(remainder):
                        continue
                    return target_title[: comma_idx + 2]

        return None

    def simplify_title(
        self,
        order: int | float,
        title: str,
        displayed_orders: set[int | float] | None = None,
    ) -> str:
        """Apply all title simplifications (strip suffix, prefix, ancestor parts).

        Parameters
        ----------
        order : int | float
            The order value of the row.
        title : str
            The raw title to simplify.
        displayed_orders : set[int | float] | None
            Set of order values that will actually be displayed.

        Returns
        -------
        str
            The simplified title.
        """
        title = strip_title_suffix(title)
        original_title = title  # Save for safeguard
        was_bop_group_stripped = False  # Track if BOP group stripping happened

        best_prefix = self.find_best_prefix(order, title, displayed_orders)
        if best_prefix and title.startswith(best_prefix):
            relative = title[len(best_prefix) :].lstrip(", :")
            if relative and title != best_prefix:
                title = relative

        sibling_prefix = self.find_sibling_common_prefix(order, title, displayed_orders)
        if sibling_prefix and title.startswith(sibling_prefix):
            remainder = title[len(sibling_prefix) :]
            if remainder:  # Only strip if something remains
                title = remainder

        bop_prefix = self.find_bop_group_prefix(order, title, displayed_orders)
        if bop_prefix and title.startswith(bop_prefix):
            remainder = title[len(bop_prefix) :]
            if remainder:  # Only strip if something remains
                title = remainder
                was_bop_group_stripped = True  # Mark that this was intentional

        while True:
            part_prefix = self.find_ancestor_part_prefix(order, title, displayed_orders)
            if part_prefix and title.startswith(part_prefix):
                title = title[len(part_prefix) :]
            else:
                break

        while True:
            best_suffix = self.find_best_suffix(order, title, displayed_orders)
            if best_suffix and title.endswith(best_suffix):
                title = title[: -len(best_suffix)]
            else:
                break

        if not was_bop_group_stripped:
            bop_only_terms = {
                "Net",
                "Credit",
                "Debit",
                "Credit/Revenue",
                "Debit/Expenditure",
                "Assets",
                "Liabilities",
                "Assets (excl. reserves)",
                "Liabilities (incl. net incurrence)",
            }
            stripped_title = title.strip()
            if stripped_title in bop_only_terms:
                title = original_title

        if not title or not title.strip():
            title = original_title

        return title


def build_order_title_level(
    df: pd.DataFrame,
) -> list[tuple[int | float, str, int, bool]]:
    """Build sorted list of (order, title, level, is_header) from DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing IMF indicator data.

    Returns
    -------
    list[tuple[int | float, str, int, bool]]
        Sorted list of (order, title, level, is_header) tuples.
    """
    order_title_level: list[tuple[int | float, str, int, bool]] = []

    for order_val in df["order"].dropna().unique():
        order_group = df[df["order"] == order_val]
        rep_row = None

        header_rows = order_group[
            order_group["is_category_header"].fillna(False)
        ].copy()
        if not header_rows.empty:
            header_rows["title_len"] = header_rows["title"].str.len().fillna(0)
            rep_row = header_rows.loc[header_rows["title_len"].idxmax()]
        else:
            data_rows_group = order_group[
                ~order_group["is_category_header"].fillna(False)
            ].copy()
            if not data_rows_group.empty:
                data_rows_group["title_len"] = (
                    data_rows_group["title"].str.len().fillna(0)
                )
                rep_row = data_rows_group.loc[data_rows_group["title_len"].idxmax()]

        if rep_row is not None:
            title = rep_row.get("title", "")
            title = strip_title_suffix(title)
            level = rep_row.get("level") or 0
            is_header = rep_row.get("is_category_header", False)
            order_title_level.append((order_val, title, level, is_header))

    order_title_level.sort(key=lambda x: x[0])
    return order_title_level


def check_missing_country_data(
    df: pd.DataFrame,
    requested_countries: list[str],
    dates: list[Any],
    countries: list[str],
) -> None:
    """Check which requested countries have no data for selected dates and warn.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing IMF indicator data.
    requested_countries : list[str]
        List of country codes/names requested by the user.
    dates : list[Any]
        List of dates in the selected date range.
    countries : list[str]
        List of countries that have data.
    """
    from openbb_core.app.model.abstract.warning import OpenBBWarning

    countries_with_data_for_dates: set[str] = set()
    for d in dates:
        date_df = df[df["date"] == d]
        countries_with_data_for_dates.update(date_df["country"].dropna().unique())

    missing_countries: list[tuple[str, Any]] = []
    for req_country in requested_countries:
        for c in countries:
            if c and (
                req_country.upper() in c.upper()
                or df[df["country"] == c]["country_code"].iloc[0] == req_country.upper()
            ):
                if c not in countries_with_data_for_dates:
                    country_dates = sorted(
                        df[df["country"] == c]["date"].dropna().unique(),
                        reverse=True,
                    )
                    latest = country_dates[0] if country_dates else None
                    missing_countries.append((c, latest))
                break

    if missing_countries:
        for country_name, latest_date in missing_countries:
            warnings.warn(
                f"No data for '{country_name}' in selected date range. "
                f"Latest available data: {latest_date}. "
                f"Try increasing 'limit' or adjusting date range.",
                OpenBBWarning,
            )


def pivot_indicator_mode(
    df: pd.DataFrame,
    dates: list[Any],
    countries: list[str],
) -> pd.DataFrame:
    """Pivot table for indicator mode.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing IMF indicator data.
    dates : list[Any]
        List of dates to use as columns.
    countries : list[str]
        List of countries.

    Returns
    -------
    pd.DataFrame
        Pivoted DataFrame with title, country, unit, and scale as index.
    """
    import pandas as pd

    rows: list[dict[str, Any]] = []
    for title in df["title"].unique():
        if pd.isna(title):
            continue
        title_df = df[df["title"] == title]
        for country in countries:
            country_df = title_df[title_df["country"] == country]
            if len(country_df) == 0:
                continue

            country_df = country_df.copy()
            units = []
            scales = []
            for _, data_row in country_df.iterrows():
                row_unit = data_row.get("unit")
                row_scale = data_row.get("scale")
                if row_unit == "-":
                    row_unit = None
                if row_scale == "-":
                    row_scale = None
                if not row_unit or not row_scale:
                    parsed_unit, parsed_scale = extract_unit_scale_from_title(
                        str(data_row.get("title") or "")
                    )
                    if not row_unit and parsed_unit:
                        row_unit = parsed_unit
                    if not row_scale and parsed_scale:
                        row_scale = parsed_scale
                units.append(row_unit if row_unit else None)
                scales.append(row_scale if row_scale else None)

            country_df["_unit"] = units
            country_df["_scale"] = scales

            for (unit_val, scale_val), group_df in country_df.groupby(
                ["_unit", "_scale"], dropna=False
            ):
                row: dict[str, Any] = {
                    "title": title,
                    "country": country,
                }
                if unit_val is not None:
                    row["unit"] = unit_val

                if scale_val is not None:
                    row["scale"] = scale_val

                has_nonzero_value = False
                for d in dates:
                    val = group_df[group_df["date"] == d]["value"].values
                    if len(val) > 0 and pd.notna(val[0]):
                        row[str(d)] = val[0]
                        if val[0] != 0:
                            has_nonzero_value = True
                    else:
                        row[str(d)] = None

                if not has_nonzero_value:
                    continue

                rows.append(row)

    result_df = pd.DataFrame(rows)
    if not result_df.empty:
        result_df = result_df.set_index(["title", "country", "unit", "scale"])

    return result_df


def pivot_table_mode(
    df: pd.DataFrame,
    dates: list[Any],
    countries: list[str],
    metadata: dict[str, Any],
) -> pd.DataFrame:
    """Get a hierarchical pivot for table mode.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing IMF indicator data.
    dates : list[Any]
        List of dates to use as columns.
    countries : list[str]
        List of countries.
    metadata : dict[str, Any]
        Metadata dictionary containing table information.

    Returns
    -------
    pd.DataFrame
        Pivoted DataFrame with hierarchical structure.
    """
    from collections import defaultdict

    import pandas as pd

    order_title_level = build_order_title_level(df)
    hierarchy_ctx = HierarchyContext(order_title_level)

    table_name = metadata.get("table", {}).get("hierarchy_name", "")
    dataflow_id = metadata.get("table", {}).get("dataflow_id", "")
    is_isora = "ISORA" in dataflow_id or "INDICATORS BY TOPIC" in table_name.upper()

    node_id_to_order: dict[str, int | float] = {}
    for node_row in df.itertuples(index=False):
        node_id = getattr(node_row, "hierarchy_node_id", None)
        order_val = getattr(node_row, "order", None)
        if node_id and order_val is not None:
            node_id_to_order[str(node_id)] = order_val

    order_to_parent: dict[int | float, int | float] = {}
    for order_val in df["order"].dropna().unique():
        order_df = df[df["order"] == order_val]
        first_row = order_df.iloc[0]
        parent_id = first_row.get("parent_id")
        parent_order: int | float | None = None
        if parent_id:
            parent_id_str = str(parent_id)
            parent_order = node_id_to_order.get(parent_id_str)
            if parent_order is None:
                suffix_pattern = f"___{parent_id_str}"
                for node_id, node_order in node_id_to_order.items():
                    if node_id.endswith(suffix_pattern):
                        parent_order = node_order
                        break
        if parent_order is not None:
            order_to_parent[order_val] = parent_order

    unit_scale_by_order: dict[int | float, tuple[str | None, str | None]] = {}

    for order_val in df["order"].dropna().unique():
        order_df = df[df["order"] == order_val]
        unit_val: str | None = None
        scale_val: str | None = None

        for _, row in order_df.iterrows():
            if unit_val is None:
                candidate_unit = row.get("unit")
                if candidate_unit and str(candidate_unit) != "nan":
                    unit_val = str(candidate_unit)
            if scale_val is None:
                candidate_scale = row.get("scale")
                if candidate_scale and str(candidate_scale) != "nan":
                    scale_val = str(candidate_scale)

            if unit_val is None or scale_val is None:
                parsed_unit, parsed_scale = extract_unit_scale_from_title(
                    str(row.get("title") or "")
                )
                if unit_val is None and parsed_unit:
                    unit_val = parsed_unit
                if scale_val is None and parsed_scale:
                    scale_val = parsed_scale

            if unit_val is not None and scale_val is not None:
                break

        unit_scale_by_order[order_val] = (unit_val, scale_val)
    for order_val in list(unit_scale_by_order.keys()):
        unit_val, scale_val = unit_scale_by_order[order_val]
        if unit_val is not None and scale_val is not None:
            continue

        visited: set[int | float] = set()
        parent_order = order_to_parent.get(order_val)
        while parent_order is not None and parent_order not in visited:
            visited.add(parent_order)
            p_unit, p_scale = unit_scale_by_order.get(parent_order, (None, None))
            if unit_val is None and p_unit is not None:
                unit_val = p_unit
            if scale_val is None and p_scale is not None:
                scale_val = p_scale
            if unit_val is not None and scale_val is not None:
                break
            parent_order = order_to_parent.get(parent_order)

        unit_scale_by_order[order_val] = (unit_val, scale_val)

    orders_with_data: set[int | float] = set()
    raw_data_rows: list[dict[str, Any]] = []

    data_orders = df["order"].dropna().unique()

    for order in sorted(data_orders):
        order_df = df[df["order"] == order]

        for country in countries:
            country_df = order_df[order_df["country"] == country]
            if country_df.empty:
                continue

            dim_code_cols = [
                c
                for c in country_df.columns
                if c.endswith("_code")
                and c not in ("country_code", "frequency_code", "dv_type_code")
                and country_df[c].notna().any()
            ]
            if "series_id" in country_df.columns:
                group_cols = ["series_id"] + [
                    c for c in dim_code_cols if c != "series_id"
                ]
            else:
                group_cols = dim_code_cols if dim_code_cols else ["symbol"]

            valid_group_cols = [c for c in group_cols if c in country_df.columns]
            if not valid_group_cols:
                valid_group_cols = ["symbol"] if "symbol" in country_df.columns else []

            if valid_group_cols:
                for _, series_df in country_df.groupby(valid_group_cols, dropna=False):
                    if (
                        series_df.empty
                    ):  # pragma: no cover -- pandas groupby never yields empty groups
                        continue
                    first_in_series = series_df.iloc[0]

                    has_data = False
                    row_values: dict[str, Any] = {}
                    for d in dates:
                        d_str = str(d)
                        date_matches = series_df["date"].astype(str) == d_str
                        val = series_df[date_matches]["value"].values
                        if len(val) > 0 and pd.notna(val[0]):
                            row_values[str(d)] = val[0]
                            has_data = True
                        else:
                            row_values[str(d)] = None

                    if has_data:
                        orders_with_data.add(order)

                        title = first_in_series.get("title", "")
                        if not title:
                            ind_code = first_in_series.get("indicator_code", "")
                            if ind_code:
                                title = ind_code.replace("_", " ").capitalize()

                        row_unit = first_in_series.get("unit") or ""
                        row_scale = first_in_series.get("scale") or ""

                        inherited_unit, inherited_scale = unit_scale_by_order.get(
                            order, (None, None)
                        )

                        if not row_unit and inherited_unit:
                            row_unit = inherited_unit
                        if not row_scale and inherited_scale:
                            row_scale = inherited_scale

                        if not row_unit or not row_scale:
                            parsed_unit, parsed_scale = extract_unit_scale_from_title(
                                title
                            )
                            if (
                                not row_unit and parsed_unit
                            ):  # pragma: no cover -- unit_scale_by_order already parsed every order row's title, so a parseable title was applied via inheritance above
                                row_unit = parsed_unit
                            if (
                                not row_scale and parsed_scale
                            ):  # pragma: no cover -- unit_scale_by_order already parsed every order row's title, so a parseable title was applied via inheritance above
                                row_scale = parsed_scale

                        dimension_values: dict[str, tuple[str, str]] = {}
                        grouping_dims = {
                            "SECTOR": "sector",
                            "TYPE_OF_TRANSFORMATION": "type_of_transformation",
                            "COUNTERPART_COUNTRY": "counterpart_country",
                            "CURRENCY": "currency",
                            "INDEX_TYPE": "index_type",
                            "BOP_ACCOUNTING_ENTRY": "bop_accounting_entry",
                            "ACCOUNTING_ENTRY": "accounting_entry",
                            "ACCOUNT": "account",
                            "PRICE_TYPE": "price_type",
                            "S_ADJUSTMENT": "s_adjustment",
                        }
                        for dim_id, col_name in grouping_dims.items():
                            code_key = f"{col_name}_code"
                            code_val = first_in_series.get(code_key)
                            label_val = first_in_series.get(col_name)
                            if code_val and label_val:
                                dimension_values[dim_id] = (
                                    str(code_val),
                                    str(label_val),
                                )

                        raw_data_rows.append(
                            {
                                "order": order,
                                "level": first_in_series["level"] or 0,
                                "raw_title": title,  # Store raw title
                                "country": country,
                                "values": row_values,
                                "unit": row_unit,
                                "scale": row_scale,
                                "dimension_values": dimension_values,
                            }
                        )

    parent_orders: set[int | float] = set()
    true_header_parents: set[int | float] = set()

    for order in orders_with_data:
        order_df = df[df["order"] == order]
        if (
            len(order_df) == 0
        ):  # pragma: no cover -- orders_with_data only contains orders present in df
            continue
        parent_id = order_df.iloc[0].get("parent_id")
        while parent_id:
            parent_df = df[df["hierarchy_node_id"] == parent_id]
            if len(parent_df) == 0:
                suffix_pattern = f"___{parent_id}"
                parent_df = df[
                    df["hierarchy_node_id"].fillna("").str.endswith(suffix_pattern)
                ]
            if len(parent_df) == 0:
                break
            parent_order = parent_df.iloc[0]["order"]
            parent_is_header = parent_df.iloc[0].get("is_category_header", False)
            if parent_order is not None:
                parent_orders.add(parent_order)
                if parent_is_header:
                    true_header_parents.add(parent_order)
            parent_id = parent_df.iloc[0].get("parent_id")

    country_orders_with_data: dict[str, set[int | float]] = {}
    for raw_row in raw_data_rows:
        country = raw_row["country"]
        order = raw_row["order"]
        if country not in country_orders_with_data:
            country_orders_with_data[country] = set()
        country_orders_with_data[country].add(order)

    country_parent_orders: dict[str, set[int | float]] = {}
    for country, country_data_orders in country_orders_with_data.items():
        country_parents: set[int | float] = set()
        for order in country_data_orders:
            order_df = df[df["order"] == order]
            if (
                len(order_df) == 0
            ):  # pragma: no cover -- country_data_orders only contains orders from raw_data_rows built from df
                continue
            parent_id = order_df.iloc[0].get("parent_id")
            while parent_id:
                parent_df = df[df["hierarchy_node_id"] == parent_id]
                if len(parent_df) == 0:
                    suffix_pattern = f"___{parent_id}"
                    parent_df = df[
                        df["hierarchy_node_id"].fillna("").str.endswith(suffix_pattern)
                    ]
                if len(parent_df) == 0:
                    break
                parent_order = parent_df.iloc[0]["order"]
                if parent_order is not None:
                    country_parents.add(parent_order)
                parent_id = parent_df.iloc[0].get("parent_id")
        country_parent_orders[country] = country_parents

    effective_parent_orders: set[int | float] = set()
    for country_parents in country_parent_orders.values():
        effective_parent_orders.update(country_parents)

    data_rows: list[dict[str, Any]] = []

    for raw_row in raw_data_rows:
        order = raw_row["order"]
        title = raw_row["raw_title"]
        country = raw_row["country"]
        country_data_orders = country_orders_with_data.get(country, set())
        displayed_orders = true_header_parents | country_data_orders
        title = hierarchy_ctx.simplify_title(order, title, displayed_orders)

        data_rows.append(
            {
                "order": order,
                "level": raw_row["level"],
                "title": title,
                "country": raw_row["country"],
                "values": raw_row["values"],
                "unit": raw_row["unit"],
                "scale": raw_row["scale"],
                "dimension_values": raw_row.get("dimension_values", {}),
            }
        )

    dim_value_sets: dict[str, set[str]] = {}
    for dr in data_rows:
        for dim_id, (code, label) in dr.get("dimension_values", {}).items():
            if dim_id not in dim_value_sets:
                dim_value_sets[dim_id] = set()
            dim_value_sets[dim_id].add(code)

    multi_value_dims = [
        dim_id for dim_id, codes in dim_value_sets.items() if len(codes) > 1
    ]

    if multi_value_dims:
        dim_priority = {"SECTOR": 0, "GFS_GRP": 1, "TYPE_OF_TRANSFORMATION": 2}
        multi_value_dims.sort(key=lambda d: dim_priority.get(d, 99))

        for dr in data_rows:
            dim_vals = dr.get("dimension_values", {})
            grouping_parts = []
            for dim_id in multi_value_dims:
                if dim_id in dim_vals:
                    code, label = dim_vals[dim_id]
                    grouping_parts.append((dim_id, code, label))
            dr["_grouping_dims"] = grouping_parts

        def row_sort_key(row: dict) -> tuple:
            dims_present = {
                dim_id: code for dim_id, code, _label in row.get("_grouping_dims", [])
            }
            grouping = tuple(
                (dim_id, dims_present.get(dim_id, "")) for dim_id in multi_value_dims
            )
            order_val = float(row.get("order") or 0)
            return grouping + (order_val,)

        data_rows.sort(key=row_sort_key)

    all_units = {dr.get("unit") for dr in data_rows if dr.get("unit")}
    all_scales = {dr.get("scale") for dr in data_rows if dr.get("scale")}
    uniform_unit = all_units.pop() if len(all_units) == 1 else None
    uniform_scale = all_scales.pop() if len(all_scales) == 1 else None
    has_uniform_unit_scale = uniform_unit is not None
    uniform_suffix = ""

    if has_uniform_unit_scale:
        parts = []
        if uniform_unit:
            parts.append(uniform_unit)
        if uniform_scale and uniform_scale != "Units":
            parts.append(uniform_scale)
        if parts:
            uniform_suffix = f" ({', '.join(parts)})"

    hierarchy_name = metadata.get("table", {}).get("hierarchy_name")
    first_level_0_is_data = False
    first_level_0_title = None

    for order in sorted(df["order"].unique()):
        order_df = df[df["order"] == order]
        first = order_df.iloc[0]
        level = first["level"] or 0

        if level == 0:
            is_header = first["is_category_header"]
            first_level_0_title = first["title"] or ""

            if not is_header:
                first_level_0_is_data = True
            break

    should_add_table_header = False

    if hierarchy_name:
        if first_level_0_is_data:
            should_add_table_header = True
        elif first_level_0_title:
            hierarchy_name_clean = hierarchy_name.upper().replace("_", " ")
            first_title_clean = first_level_0_title.upper().split(" (")[0]
            if (
                hierarchy_name_clean not in first_title_clean
                and first_title_clean not in hierarchy_name_clean
            ):
                should_add_table_header = True

    rows: list[dict[str, Any]] = []

    if should_add_table_header and hierarchy_name:
        header_title = hierarchy_name.upper()
        if uniform_suffix:
            header_title += uniform_suffix
        row = {
            "title": f"▸ {header_title}",
            "country": "",
        }
        for d in dates:
            row[str(d)] = ""
        rows.append(row)

    all_orders: list[float] = [float(o) for o in df["order"].unique()]
    sorted_orders = sorted(all_orders)

    dim_group_map: dict[tuple, list[dict]] = defaultdict(list)
    if multi_value_dims:
        for dr in data_rows:
            grouping_key = tuple(dr.get("_grouping_dims", []))
            dim_group_map[grouping_key].append(dr)
    else:
        dim_group_map[()] = data_rows

    def format_dim_labels(grouping_key: tuple) -> str:
        """Format all dimension labels from a grouping key into a display string."""
        if (
            not grouping_key
        ):  # pragma: no cover -- only called from a branch gated by `if grouping_key`
            return ""

        unit_like_transformations = {
            "Domestic currency",
            "National currency",
            "US dollar",
            "US Dollar",
            "SDR",
            "Euro",
        }

        labels = []
        filtered_labels = []
        for dim_id, _, label in grouping_key:
            labels.append(label)
            if (
                dim_id == "TYPE_OF_TRANSFORMATION"
                and label in unit_like_transformations
            ):
                continue
            filtered_labels.append(label)

        effective_labels = filtered_labels if filtered_labels else labels

        return " - ".join(effective_labels) if effective_labels else ""

    order_to_dim_data: dict[int | float, list[tuple[tuple, list[dict]]]] = defaultdict(
        list
    )
    seen_order_keys: dict[int | float, set[tuple]] = defaultdict(set)

    for dr in data_rows:
        order = dr["order"]
        grouping_key = tuple(dr.get("_grouping_dims", []))

        if grouping_key in seen_order_keys[order]:
            for entry in order_to_dim_data[order]:
                if entry[0] == grouping_key:
                    entry[1].append(dr)
                    break
        else:
            order_to_dim_data[order].append((grouping_key, [dr]))
            seen_order_keys[order].add(grouping_key)

    all_orders_with_data = {dr["order"] for dr in data_rows}
    global_parent_orders: set[int | float] = set()
    for order in all_orders_with_data:
        order_df = df[df["order"] == order]
        if (
            len(order_df) == 0
        ):  # pragma: no cover -- all_orders_with_data only contains orders from data_rows built from df
            continue
        parent_id = order_df.iloc[0].get("parent_id")
        while parent_id:
            parent_df = df[df["hierarchy_node_id"] == parent_id]
            if len(parent_df) == 0:
                suffix_pattern = f"___{parent_id}"
                parent_df = df[
                    df["hierarchy_node_id"].fillna("").str.endswith(suffix_pattern)
                ]
            if len(parent_df) == 0:
                break
            parent_order = parent_df.iloc[0]["order"]
            if parent_order is not None:
                global_parent_orders.add(parent_order)
            parent_id = parent_df.iloc[0].get("parent_id")

    bop_skipped_parent_ids: set[str] = set()

    def _track_skipped_parent_ids(row_like: dict[str, Any]) -> None:
        node_id = row_like.get("hierarchy_node_id")
        ind_code = row_like.get("indicator_code")
        for v in (node_id, ind_code):
            if not v:
                continue
            sv = str(v)
            bop_skipped_parent_ids.add(sv)
            if "___" in sv:
                bop_skipped_parent_ids.add(sv.rsplit("___", 1)[-1])

    def _lookup_parent_row(parent_id: str):
        parent_df = df[df["hierarchy_node_id"] == parent_id]
        if len(parent_df) == 0:
            suffix_pattern = f"___{parent_id}"
            parent_df = df[
                df["hierarchy_node_id"].fillna("").str.endswith(suffix_pattern)
            ]
        if len(parent_df) == 0 and "indicator_code" in df.columns:
            parent_df = df[df["indicator_code"] == parent_id]
        return parent_df

    def _promote_level_if_parent_skipped(level: int, parent_id: Any) -> int:
        adjusted = level
        pid = str(parent_id) if parent_id else ""
        while pid and pid in bop_skipped_parent_ids and adjusted > 0:
            adjusted -= 1
            parent_df = _lookup_parent_row(pid)
            if (
                len(parent_df) == 0
            ):  # pragma: no cover -- ids added to bop_skipped_parent_ids always resolve via hierarchy_node_id/suffix/indicator_code lookup
                break
            pid = str(parent_df.iloc[0].get("parent_id") or "")
        return adjusted

    last_meaningful_header_by_level: dict[int, str] = {}

    for order in sorted_orders:
        order_df = df[df["order"] == order]
        if (
            order_df.empty
        ):  # pragma: no cover -- sorted_orders is derived from df["order"].unique()
            continue
        first = order_df.iloc[0]
        level = first["level"] or 0

        for k in [k for k in last_meaningful_header_by_level if k > level]:
            del last_meaningful_header_by_level[k]

        is_header = first["is_category_header"]
        title = first["title"] or ""
        original_unit_suffix = ""

        if " (" in title and title.endswith(")"):
            paren_idx = title.rfind(" (")
            if paren_idx > 0:
                original_unit_suffix = title[paren_idx:]
                title = title[:paren_idx]

        unit_suffixes = [", Transactions", ", Stocks", ", Flows"]
        for suffix in unit_suffixes:
            if title.endswith(suffix):
                title = title[: -len(suffix)]
                break

        is_promoted_header = (
            not is_header
            and order in global_parent_orders
            and order not in all_orders_with_data
        )
        should_render_as_header = (
            is_header or is_promoted_header
        ) and order not in all_orders_with_data

        if should_render_as_header and order not in global_parent_orders:
            if is_bop_suffix_only(title):
                _track_skipped_parent_ids(first.to_dict())
            continue

        if should_render_as_header and is_bop_suffix_only(title):
            _track_skipped_parent_ids(first.to_dict())
            continue

        level = _promote_level_if_parent_skipped(level, first.get("parent_id"))

        if is_isora and should_render_as_header:
            if title and "___" in title:
                continue
            is_topic = bool(
                title
                and (
                    re.match(r"^\d+\.\s", title)
                    or "INDICATORS BY TOPIC" in title.upper()
                )
            )
            if not is_topic:
                continue

        if should_render_as_header:
            if title.startswith("Financial corporations, "):
                title = title[len("Financial corporations, ") :]
            elif title.startswith("Depository corporations, "):
                title = title[len("Depository corporations, ") :]
        else:
            best_prefix = hierarchy_ctx.find_best_prefix(order, title, parent_orders)
            if best_prefix and title.startswith(best_prefix):
                relative = title[len(best_prefix) :].lstrip(", :")
                if (
                    relative
                    and title != best_prefix
                    and not is_bop_suffix_only(relative)
                ):
                    title = relative

            while True:
                best_suffix = hierarchy_ctx.find_best_suffix(
                    order, title, parent_orders
                )
                if best_suffix and title.endswith(best_suffix):
                    title = title[: -len(best_suffix)]
                else:
                    break

            while True:
                part_prefix = hierarchy_ctx.find_ancestor_part_prefix(
                    order, title, parent_orders
                )
                if part_prefix and title.startswith(part_prefix):
                    title = title[len(part_prefix) :]
                else:
                    break

        if should_render_as_header:
            header_base = title.strip()
            if header_base and not is_bop_suffix_only(header_base):
                last_meaningful_header_by_level[level] = header_base
        else:
            for bop_suffix in (", Net", ", Credit", ", Debit"):
                if title.endswith(bop_suffix):
                    base = title[: -len(bop_suffix)].strip()
                    ancestor_title: str | None = None
                    for ancestor_level in range(level - 1, -1, -1):
                        cand = last_meaningful_header_by_level.get(ancestor_level)
                        if not cand:
                            continue
                        if cand.endswith((", Net", ", Credit", ", Debit")):
                            continue
                        ancestor_title = cand
                        break

                    if (
                        ancestor_title
                        and ancestor_title != base
                        and ancestor_title.startswith(base)
                    ):
                        title = f"{ancestor_title}{bop_suffix}"
                    break

        extra_indent = "   " if should_add_table_header else ""
        indent = extra_indent + "   " * level

        prefix = "▸ " if should_render_as_header else "  "

        if should_render_as_header:
            if order in global_parent_orders:
                if (
                    is_isora and title and "___" in title
                ):  # pragma: no cover -- ISORA "___" titles are already filtered at the earlier should_render_as_header gate
                    continue

                header_title = title
                if has_uniform_unit_scale:
                    if level == 0 and uniform_suffix:
                        header_title += uniform_suffix
                elif original_unit_suffix:
                    header_title += original_unit_suffix

                row = {
                    "title": f"{indent}{prefix}{header_title}",
                    "country": "",
                }
                for d in dates:
                    row[str(d)] = ""
                rows.append(row)
        else:
            order_dim_groups = order_to_dim_data.get(order, [])
            order_has_multi_dims = len(order_dim_groups) > 1 or (
                len(order_dim_groups) == 1 and len(order_dim_groups[0][1]) > 1
            )

            if order_has_multi_dims:
                data_level = level
                data_indent = extra_indent + "   " * data_level

                display_title = title
                if data_level == 0 and uniform_suffix and not should_add_table_header:
                    display_title += uniform_suffix
                elif not has_uniform_unit_scale:
                    first_dr = order_dim_groups[0][1][0] if order_dim_groups else None
                    if first_dr:
                        row_unit_suffix = format_unit_suffix(
                            first_dr.get("unit"), first_dr.get("scale")
                        )
                        display_title += row_unit_suffix

                world_grouping_key = None
                world_data_row = None
                for gk, drs in order_dim_groups:
                    if gk:
                        for dim_id, code, label in gk:
                            if dim_id == "COUNTERPART_COUNTRY" and (
                                code == "G001" or label == "World"
                            ):
                                world_grouping_key = gk
                                world_data_row = drs[0] if drs else None
                                break
                    if world_grouping_key:
                        break

                item_row: dict[str, Any] = {
                    "title": f"{data_indent}{display_title}",
                    "country": world_data_row["country"] if world_data_row else "",
                }
                if world_data_row:
                    item_row.update(world_data_row["values"])
                else:
                    for d in dates:
                        item_row[str(d)] = ""
                rows.append(item_row)

                has_counterpart_country = any(
                    dim_id == "COUNTERPART_COUNTRY"
                    for gk, _ in order_dim_groups
                    if gk
                    for dim_id, _, _ in gk
                )

                if has_counterpart_country:
                    cc_indent = extra_indent + "   " * (data_level + 1)

                    def is_group_code(code: str) -> bool:
                        """Group codes have letter(s) followed by digits."""
                        if re.match(r"^[A-Z]{3}$", code):
                            return False
                        return bool(re.match(r"^[A-Z]+\d+$", code))

                    groups: list[tuple[tuple, list[dict], str, str]] = []
                    individual_countries: list[tuple[tuple, list[dict], str, str]] = []

                    for gk, drs in order_dim_groups:
                        if gk == world_grouping_key:
                            continue  # Skip World - already on parent
                        if gk:
                            cc_code = None
                            cc_label = None
                            for dim_id, code, label in gk:
                                if dim_id == "COUNTERPART_COUNTRY":
                                    cc_code = code
                                    cc_label = label
                                    break

                            if cc_label and cc_code:
                                if is_group_code(cc_code):
                                    groups.append((gk, drs, cc_label, cc_code))
                                else:
                                    individual_countries.append(
                                        (gk, drs, cc_label, cc_code)
                                    )

                    def get_sort_value(item: tuple) -> float:
                        """Get the first numeric value from data rows for sorting."""
                        _, drs, _, _ = item
                        for dr in drs:
                            for v in dr.get("values", {}).values():
                                if v is not None:
                                    try:
                                        return abs(float(v))
                                    except (ValueError, TypeError):
                                        pass
                        return 0.0

                    for gk, drs, cc_label, cc_code in sorted(
                        groups, key=get_sort_value, reverse=True
                    ):
                        for dr in drs:
                            if all(d == 0 or d is None for d in dr["values"].values()):
                                continue  # Skip zero-value countries
                            row = {
                                "title": f"{cc_indent}▸ {cc_label}",
                                "country": dr["country"],
                            }
                            row.update(dr["values"])
                            rows.append(row)

                    for gk, drs, cc_label, cc_code in sorted(
                        individual_countries, key=get_sort_value, reverse=True
                    ):
                        for dr in drs:
                            if all(d == 0 or d is None for d in dr["values"].values()):
                                continue  # Skip zero-value countries
                            row = {
                                "title": f"{cc_indent}  {cc_label}",
                                "country": dr["country"],
                            }
                            row.update(dr["values"])
                            rows.append(row)
                else:
                    for grouping_key, dim_data_rows in sorted(order_dim_groups):
                        if (
                            grouping_key == world_grouping_key
                        ):  # pragma: no cover -- world_grouping_key is None in this else branch (no COUNTERPART_COUNTRY); tuple grouping_key never equals None
                            continue
                        if grouping_key:
                            dim_label = format_dim_labels(grouping_key)
                            for dr in dim_data_rows:
                                sector_indent = extra_indent + "   " * (data_level + 1)
                                row = {
                                    "title": f"{sector_indent}  {dim_label}",
                                    "country": dr["country"],
                                }
                                row.update(dr["values"])
                                rows.append(row)
                        else:
                            for dr in dim_data_rows:
                                row = {
                                    "title": f"{data_indent}{display_title}",
                                    "country": dr["country"],
                                }
                                row.update(dr["values"])
                                rows.append(row)
            else:
                for dr in data_rows:
                    if dr["order"] == order:
                        data_level = level
                        data_indent = extra_indent + "   " * data_level

                        display_title = title
                        if (
                            data_level == 0
                            and uniform_suffix
                            and not should_add_table_header
                        ):
                            display_title += uniform_suffix
                        elif not has_uniform_unit_scale:
                            row_unit_suffix = format_unit_suffix(
                                dr.get("unit"), dr.get("scale")
                            )
                            display_title += row_unit_suffix

                        row = {
                            "title": f"{data_indent}{display_title}",
                            "country": dr["country"],
                        }
                        row.update(dr["values"])
                        rows.append(row)

    result_df = pd.DataFrame(rows)
    result_df = result_df.set_index(["title", "country"])

    return result_df


def pivot_table_data(
    result: list[Any],
    country: str | None,
    limit: int | None,
    metadata: dict[str, Any],
) -> pd.DataFrame:
    """Pivot table data based on whether hierarchy exists.

    Parameters
    ----------
    result : list[Any]
        List of ImfEconomicIndicatorsData records to pivot.
    country : str
        Comma-separated country codes from the query.
    limit : int | None
        Maximum number of date columns to show.
    metadata : dict[str, Any]
        Metadata dictionary containing table information.

    Returns
    -------
    pd.DataFrame
        Pivoted DataFrame with appropriate structure.
    """
    from pandas import DataFrame

    df = DataFrame(result)
    all_dates = sorted(df["date"].dropna().unique().tolist(), reverse=True)
    dates = all_dates[:limit] if limit is not None and limit > 0 else all_dates
    countries = sorted(df["country"].dropna().unique().tolist())

    if country and dates:
        requested_countries = [c.strip() for c in country.split(",")]
        check_missing_country_data(df, requested_countries, dates, countries)

    has_hierarchy = df["order"].notna().any() if "order" in df.columns else False

    if not has_hierarchy:
        return pivot_indicator_mode(df, dates, countries)

    return pivot_table_mode(df, dates, countries, metadata)
