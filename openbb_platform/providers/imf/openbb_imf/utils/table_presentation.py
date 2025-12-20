"""Presentation table utilities for IMF provider.

This module handles the complex pivot/presentation logic for transforming
IMF economic indicator data into hierarchical presentation tables.
"""

# pylint: disable=C0302,R0912,R0911,R0914,R0915,R1702
# flake8: noqa: PLR0912,PLR0911

import re
import warnings
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def extract_unit_from_label(label: str) -> str | None:
    """Extract unit information from an indicator label.

    Parses indicator labels to extract unit suffixes like:
    - "Per capita, US dollar" from "Exporter real gross domestic product, Per capita, US dollar"
    - "Percent" from "GDP growth rate, Percent"
    - "US Dollar, Millions" from "Trade balance (US Dollar, Millions)"

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

    # Check for parenthetical unit at end: "(US Dollar, Millions)" or "(Domestic currency)"
    if label.endswith(")"):
        paren_start = label.rfind(" (")
        if paren_start > 0:
            suffix_content = label[paren_start + 2 : -1]
            # Check if it looks like a unit (contains currency or scale keywords)
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

    # Check for comma-separated unit suffix at the end of the label
    # Look for the last comma-separated part and check if it's a unit
    parts = label.rsplit(", ", 1)
    if len(parts) == 2:
        last_part = parts[1]
        last_part_lower = last_part.lower()
        # "per" indicates a rate/unit (e.g., "US cents per pound", "dollars per metric tonne")
        if " per " in last_part_lower:
            return last_part
        # Check for other unit keywords
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

    Many IMF indicator labels embed both scale and unit in a single suffix like:
    - "Per capita, US dollar" → scale="Per capita", unit="US dollar"
    - "Millions, US dollar" → scale="Millions", unit="US dollar"
    - "US Dollar, Millions" → scale="Millions", unit="US Dollar"
    - "US dollars per metric tonne" → unit="US dollars", scale="per metric tonne"
    - "US cents per pound" → unit="US cents", scale="per pound"
    - "Percent" → scale=None, unit="Percent"
    - "US dollar" → scale=None, unit="US dollar"
    - "Index" → scale=None, unit="Index"

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

    # Check for "Unit of ..." pattern (e.g., "Percent of exports of goods and services")
    # Common units that can be followed by "of ..."
    unit_of_patterns = ["Percent of ", "Ratio of ", "Index of ", "Number of "]
    for pattern in unit_of_patterns:
        if unit_string.startswith(pattern):
            unit = pattern.replace(" of ", "").strip()
            scale = "of " + unit_string[len(pattern) :].strip().title()
            return unit, scale

    # Check for "X per Y" pattern (e.g., "US dollars per metric tonne")
    # Split on " per " - unit is before, scale is "per ..."
    if " per " in unit_string.lower():
        # Find the position case-insensitively
        lower_str = unit_string.lower()
        per_idx = lower_str.find(" per ")
        if per_idx > 0:
            unit = unit_string[:per_idx].strip()
            scale = unit_string[per_idx + 1 :].strip().title()
            return unit, scale

    # Scale indicators that appear before the unit (e.g., "Per capita, US dollar")
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

    # Scale indicators that appear after the unit (e.g., "US Dollar, Millions")
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

    # Check for pattern: "scale_description, Unit" (e.g., "95 percent interval - lower bound, Percent")
    # The unit is after the last comma, scale is before it
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

    # If no scale prefix/suffix, the whole string is the unit
    # But check if it's actually a scale-only value
    scale_only_values = ["Per capita", "Millions", "Billions", "Thousands"]
    if unit_string in scale_only_values:
        return None, unit_string

    return unit_string, None


def strip_title_suffix(title: str) -> str:
    """Strip scale/unit and type suffixes from title.

    Handles:
    - Trailing unit/type suffixes: ", Transactions", ", Stocks", ", Flows"
    - Parenthetical unit patterns: "(Millions, US Dollar)"

    Preserves dimension labels like "(Euro)", "(Foreign Currency)", "(Credit)".

    Parameters
    ----------
    title : str
        The raw title to process.

    Returns
    -------
    str
        The title with suffixes stripped.
    """
    # Strip trailing unit/type suffixes like ", Transactions", ", Stocks"
    unit_suffixes = [", Transactions", ", Stocks", ", Flows"]
    for suffix in unit_suffixes:
        if title.endswith(suffix):
            title = title[: -len(suffix)]
            break
    # Only strip parenthetical suffix if it's a known unit/scale pattern
    # Preserve dimension labels like (Euro), (Foreign Currency), (Credit), etc.
    if title.endswith(")"):
        paren_start = title.rfind(" (")
        if paren_start > 0:
            suffix_content = title[paren_start + 2 : -1]
            # Only strip if it looks like a unit/scale suffix
            # Common patterns: "Millions", "Billions", "Percent", etc.
            # Note: "Domestic currency" is a currency dimension label, not a unit
            unit_patterns = [
                "Millions",
                "Billions",
                "Thousands",
                "Percent",
                "Units",
            ]
            # Also handle compound patterns like "US Dollar, Millions"
            # But NOT pure unit patterns alone (those describe the data)
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
    # Ensure unit and scale are valid strings (not None, nan, or other types)
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

# Patterns that indicate a unit value in comma-separated titles
# e.g., "Lamb, Unit prices, US cents per pound"
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
    """Extract unit/scale from a trailing parenthetical suffix or comma-separated part.

    Handles two patterns:
    1. Parenthetical: "Title (US Dollar, Millions)" -> unit="US Dollar", scale="Millions"
    2. Comma-separated: "Lamb, Unit prices, US cents per pound" -> unit="US cents per pound"

    Only returns values when the suffix contains known unit/scale keywords to
    avoid over-eager parsing for titles that merely contain contextual labels.
    """
    if not title:
        return None, None

    unit_val: str | None = None
    scale_val: str | None = None

    # First try parenthetical pattern: "Title (unit, scale)"
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

    # Try comma-separated pattern: "Title, Unit prices, US cents per pound"
    # Look for the last comma-separated part that contains unit keywords
    parts = [p.strip() for p in title.split(",")]
    if len(parts) >= 2:
        # Check last part for unit keywords
        last_part = parts[-1].lower()
        if any(kw in last_part for kw in UNIT_KEYWORDS):
            unit_val = parts[-1].strip()
            return unit_val, scale_val

    return None, None


def is_bop_suffix_only(text: str) -> bool:
    """Check if text is only a BOP-style suffix that lacks meaningful context.

    Returns True if the text is just:
    - Net, Credit, Debit, Assets, Liabilities (with optional parenthetical)
    - Credit/Revenue, Debit/Expenditure
    - These terms should NOT stand alone as titles
    - Or if it starts with a lowercase word/preposition (fragment of larger phrase)

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

    # Normalize: strip leading comma/space, and trailing parenthetical
    normalized = text.lstrip(", :")
    if not normalized:
        return True

    # Check if starts with lowercase (indicates a fragment, not a proper category)
    # e.g., "excluding reserves and related items, Net" is a fragment
    first_word = normalized.split()[0] if normalized.split() else ""
    # If first word is lowercase and not a number, it's a fragment
    if first_word and first_word[0].islower() and not first_word[0].isdigit():
        return True

    # Strip trailing parenthetical for BOP term check
    check_text = normalized
    if check_text.endswith(")"):
        paren_start = check_text.rfind(" (")
        if paren_start > 0:
            check_text = check_text[:paren_start].strip()

    # Check if what remains is just a BOP suffix term
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

    This class encapsulates the logic for finding ancestor context in
    hierarchical IMF table data, enabling title simplification by stripping
    redundant prefixes and suffixes.

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
        """Get siblings that share the same parent (consecutive rows at same level).

        Siblings are rows at the same level that appear between parent boundaries.
        A parent boundary is any row at a lower level (parent) or a row at same
        level after a gap (different parent group).
        """
        # Find target index
        target_idx = None
        for i, (order, _, level, _) in enumerate(self.order_title_level):
            if order == target_order:
                target_idx = i
                break

        if target_idx is None:
            return []

        siblings: list[tuple[int | float, str]] = []

        # Look backwards to find start of sibling group (stop at parent or start)
        start_idx = target_idx
        for i in range(target_idx - 1, -1, -1):
            _, _, level, _ = self.order_title_level[i]
            if level < target_level:
                # Found parent, siblings start after this
                break
            if level == target_level:
                start_idx = i
            # Skip higher levels (children of previous siblings)

        # Look forwards to find end of sibling group (stop at parent or end)
        end_idx = target_idx
        for i in range(target_idx + 1, len(self.order_title_level)):
            _, _, level, _ = self.order_title_level[i]
            if level < target_level:
                # Found next parent, siblings end before this
                break
            if level == target_level:
                end_idx = i
            # Skip higher levels (children of siblings)

        # Collect all siblings (rows at target_level between start and end)
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

        When multiple rows at the same level share a common prefix like
        "Depository corporations, Liabilities, ", this prefix is redundant
        and can be stripped to show cleaner titles.

        Only considers prefixes that end with ", " to avoid partial word matches.
        Requires at least 3 siblings sharing the prefix to consider it redundant.

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
        # Find target's level
        target_level = None
        for order, _, level, _ in self.order_title_level:
            if order == target_order:
                target_level = level
                break

        if target_level is None:
            return None

        # Get true siblings (respecting parent boundaries)
        siblings = self._get_true_siblings(target_order, target_level)
        if len(siblings) < 3:
            return None

        # Filter to displayed siblings only
        if displayed_orders is not None:
            siblings = [(o, t) for o, t in siblings if o in displayed_orders]
            if len(siblings) < 3:
                return None

        # Split titles by ", " but preserve pattern for later reconstruction
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

        # Get segments for all sibling titles
        sibling_titles = [t for _, t in siblings if t]
        if len(sibling_titles) < 3:
            return None

        # Find the longest common prefix segments
        all_segments = [get_prefix_segments(t) for t in sibling_titles]
        if not all_segments:
            return None

        # Find how many prefix segments are shared by siblings
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

        # Build the common prefix string
        common_prefix = "".join(all_segments[0][:common_count])

        # Make sure the target title starts with this prefix
        if not target_title.lower().startswith(common_prefix.lower()):
            return None

        # SAFEGUARD: Don't strip common prefix if ALL siblings end with BOP suffixes
        # (Credit/Debit/Net, Credit/Revenue, Debit/Expenditure, Assets, Liabilities)
        # In this case the common prefix IS the meaningful category name
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

        # Return the actual prefix from the target (preserve case)
        return target_title[: len(common_prefix)]

    def find_bop_group_prefix(
        self,
        target_order: int | float,
        target_title: str,
        displayed_orders: set[int | float] | None = None,
    ) -> str | None:
        """Find BOP-style group prefix for Credit/Debit/Net patterns.

        BOP tables have patterns like:
        - "Goods, Credit" (order 3.000)
        - "Goods, Debit" (order 3.001)
        - "Goods, Net" (order 3.002)

        These are all at the same level but form a logical group.
        When we see "Goods, Credit", we should strip "Goods, " because
        "Goods, Net" (which becomes "Goods" after Net stripping) serves
        as the implicit header for this group.

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
        # BOP suffixes that indicate a grouped entry
        bop_suffixes = [", Credit", ", Debit", ", Net"]

        # Check if this title ends with a BOP suffix
        base_name = None
        our_suffix = None
        for suffix in bop_suffixes:
            if target_title.endswith(suffix):
                base_name = target_title[: -len(suffix)]
                our_suffix = suffix
                break

        if base_name is None:
            return None

        # For ", Net" suffix, don't strip - it becomes the group header
        if our_suffix == ", Net":
            return None

        # Find siblings with the same base name
        target_level = None
        for order, _, level, _ in self.order_title_level:
            if order == target_order:
                target_level = level
                break

        if target_level is None:
            return None

        # Get nearby siblings (within a small order range to find the group)
        siblings = self._get_true_siblings(target_order, target_level)

        # Filter to displayed siblings
        if displayed_orders is not None:
            siblings = [(o, t) for o, t in siblings if o in displayed_orders]

        # Check if there's a matching Net entry with the same base
        has_matching_net = False
        for _, sib_title in siblings:
            if sib_title == f"{base_name}, Net":
                has_matching_net = True
                break

        if has_matching_net:
            # Strip the base name + ", " prefix
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
        # Find this order in the sorted list
        target_idx = None
        target_level = 0
        for i, (order, title, level, _) in enumerate(self.order_title_level):
            if order == target_order:
                target_idx = i
                target_level = level
                break

        if target_idx is None:
            return None

        # Look backwards for ancestors
        best_prefix = None
        levels_seen: set = set()
        ancestor_key_phrases: set = set()

        for i in range(target_idx - 1, -1, -1):
            order, title, level, _ = self.order_title_level[i]
            # Only consider rows at lower levels
            if level < target_level:
                if level in levels_seen:
                    continue
                levels_seen.add(level)

                # If displayed_orders provided, only consider ancestors that will be shown
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

                # Remove common suffixes to get the key entity
                for suffix in [
                    " survey",
                    " (domestic currency, millions)",
                    " (percent of gdp)",
                ]:
                    if title_lower.endswith(suffix):
                        title_lower = title_lower[: -len(suffix)]
                # Store the normalized phrase
                if title_lower:
                    ancestor_key_phrases.add(title_lower.strip())

        # If no exact prefix match, check for key phrase matches
        if best_prefix is None and ancestor_key_phrases:
            target_lower = target_title.lower()
            # Normalize hyphens to spaces for matching
            target_normalized = target_lower.replace("-", " ")
            for phrase in sorted(ancestor_key_phrases, key=len, reverse=True):
                phrase_normalized = phrase.replace("-", " ")
                # Check if target starts with the phrase followed by ", " or ": "
                for sep in [", ", ": ", " - "]:
                    prefix_pattern = f"{phrase_normalized}{sep}"
                    if target_normalized.startswith(prefix_pattern):
                        # Find the actual case-preserved prefix in the original title
                        prefix_len = len(prefix_pattern)
                        best_prefix = target_title[:prefix_len]
                        break
                if best_prefix:
                    break

        # SAFEGUARD: Don't return prefix if it would leave only a BOP suffix
        # This prevents "Financial account balance..., Net (...)" from becoming just "Net (...)"
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

        Many IMF tables have titles like:
        - Parent: "Domestic Creditors, Liabilities"
        - Child: "Currency and deposits, Net incurrence of liabilities, Domestic Creditors"

        The ", Domestic Creditors" suffix is redundant since it's shown in the parent.
        This function finds such suffixes to strip.

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
        # Find this order in the sorted list
        target_idx = None
        target_level = 0
        for i, (order, title, level, _) in enumerate(self.order_title_level):
            if order == target_order:
                target_idx = i
                target_level = level
                break

        if target_idx is None:
            return None

        # Collect ALL suffix parts from ALL ancestors that we should strip
        # Start with immediate parent, go up the hierarchy
        levels_seen: set = set()
        ancestor_parts: set = set()
        # Never strip accounting-entry qualifiers like Net/Credit/Debit.
        # In BOP tables these are meaningful and required to preserve hierarchy.
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

                # If displayed_orders provided, only consider ancestors that will be shown
                if displayed_orders is not None and order not in displayed_orders:
                    continue

                if not title:
                    continue

                # Split on ", " followed by uppercase letter or colon hierarchy separator
                parts = re.split(r", (?=[A-Z:])", title)
                for p in parts:
                    pp = p.strip()
                    if pp:
                        ancestor_parts.add(pp)
                        # Also add related context patterns that imply each other
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

        # Try to find the rightmost comma-separated part that matches
        if not ancestor_parts:
            return None

        # Check if the title ends with ", <ancestor_part>"
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

        Some IMF titles have ancestor context as a prefix:
        - Parent: "Liabilities"
        - Child: "Total liabilities, Domestic Creditors"

        The "Total liabilities, " prefix is redundant since parent is "Liabilities".

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
        # Find this order in the sorted list
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
                        # Add related patterns
                        if pp == "Liabilities":
                            ancestor_parts.add("Total liabilities")
                        elif pp == "Financial assets":
                            ancestor_parts.add("Financial assets")

        if not ancestor_parts:
            return None

        # Check if title starts with "<ancestor_part>, " or "<ancestor_part>: "
        strippable_single_words = {"Assets", "Liabilities"}
        target_normalized = target_title.lower().replace("-", " ")
        for part in ancestor_parts:
            # Skip single-word parts unless they're known category markers
            if " " not in part and part not in strippable_single_words:
                continue
            part_normalized = part.lower().replace("-", " ")
            # Check both comma and colon separators
            for sep in [", ", ": "]:
                prefix_with_sep = f"{part}{sep}"
                if target_title.startswith(prefix_with_sep):
                    # SAFEGUARD: Don't return if remainder is just a BOP suffix
                    remainder = target_title[len(prefix_with_sep) :]
                    if is_bop_suffix_only(remainder):
                        continue
                    return prefix_with_sep
                # Also check normalized version
                prefix_normalized = f"{part_normalized}{sep}"
                if target_normalized.startswith(prefix_normalized):
                    # SAFEGUARD: Don't return if remainder is just a BOP suffix
                    remainder = target_title[len(prefix_normalized) :]
                    if is_bop_suffix_only(remainder):
                        continue
                    return target_title[: len(prefix_normalized)]

        # Check if title starts with a PARTIAL version of an ancestor part
        # e.g., Parent: "A to B liabilities", Child: "A to B , X"
        # The child prefix "A to B , " is a partial match of parent
        if ", " in target_title:
            comma_idx = target_title.index(", ")
            child_prefix = target_title[:comma_idx].lower().replace("-", " ")
            for part in ancestor_parts:
                part_normalized = part.lower().replace("-", " ")
                # Check if child prefix is a prefix of the ancestor part
                if part_normalized.startswith(child_prefix) and len(child_prefix) > 10:
                    # SAFEGUARD: Don't return if remainder is just a BOP suffix
                    remainder = target_title[comma_idx + 2 :]
                    if is_bop_suffix_only(remainder):
                        continue
                    # Strip the prefix plus ", "
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

        # Only strip prefixes from ancestors that will be displayed
        best_prefix = self.find_best_prefix(order, title, displayed_orders)
        if best_prefix and title.startswith(best_prefix):
            relative = title[len(best_prefix) :].lstrip(", :")
            # Only replace if relative is not empty, and it's not identical
            if relative and title != best_prefix:
                title = relative

        # Check for common prefix among siblings at the same level
        sibling_prefix = self.find_sibling_common_prefix(order, title, displayed_orders)
        if sibling_prefix and title.startswith(sibling_prefix):
            remainder = title[len(sibling_prefix) :]
            if remainder:  # Only strip if something remains
                title = remainder

        # Check for BOP-style Credit/Debit/Net grouping pattern
        # This is INTENTIONAL stripping - we WANT "Credit"/"Debit" as children of "Net" header
        bop_prefix = self.find_bop_group_prefix(order, title, displayed_orders)
        if bop_prefix and title.startswith(bop_prefix):
            remainder = title[len(bop_prefix) :]
            if remainder:  # Only strip if something remains
                title = remainder
                was_bop_group_stripped = True  # Mark that this was intentional

        # Strip ancestor-part prefixes before suffix stripping
        while True:
            part_prefix = self.find_ancestor_part_prefix(order, title, displayed_orders)
            if part_prefix and title.startswith(part_prefix):
                title = title[len(part_prefix) :]
            else:
                break

        # Then strip redundant suffixes from parent context
        while True:
            best_suffix = self.find_best_suffix(order, title, displayed_orders)
            if best_suffix and title.endswith(best_suffix):
                title = title[: -len(best_suffix)]
            else:
                break

        # SAFEGUARD: Never reduce title to ONLY a BOP suffix term
        # UNLESS it was intentionally stripped by BOP group logic (Credit/Debit under Net header)
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
                # Restore the original title (before any stripping)
                title = original_title

        # SAFEGUARD: Never return an empty title - restore original if stripped to nothing
        if not title or not title.strip():
            title = original_title

        return title


def build_order_title_level(
    df: "pd.DataFrame",
) -> list[tuple[int | float, str, int, bool]]:
    """Build sorted list of (order, title, level, is_header) from DataFrame.

    For each order, finds the best representative row (prefers headers,
    otherwise takes longest title).

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

        # Prefer header rows for titles if they exist for this order
        header_rows = order_group[
            order_group["is_category_header"].fillna(False)
        ].copy()
        if not header_rows.empty:
            # If multiple headers, pick one with longest title
            header_rows["title_len"] = header_rows["title"].str.len().fillna(0)
            rep_row = header_rows.loc[header_rows["title_len"].idxmax()]
        else:
            # If no header, find the data row with the best title
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

    # Sort by order to ensure correct sequence
    order_title_level.sort(key=lambda x: x[0])
    return order_title_level


def check_missing_country_data(
    df: "pd.DataFrame",
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
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.model.abstract.warning import OpenBBWarning

    # Build a set of countries that have data for the selected dates
    countries_with_data_for_dates: set[str] = set()
    for d in dates:
        date_df = df[df["date"] == d]
        countries_with_data_for_dates.update(date_df["country"].dropna().unique())

    # Check each requested country
    missing_countries: list[tuple[str, Any]] = []
    for req_country in requested_countries:
        # Find the actual country name (we have codes like DEU, USA)
        # Check if any country in data matches this code
        for c in countries:
            if c and (
                req_country.upper() in c.upper()
                or df[df["country"] == c]["country_code"].iloc[0] == req_country.upper()
            ):
                if c not in countries_with_data_for_dates:
                    # Get the latest date this country has data for
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
    df: "pd.DataFrame",
    dates: list[Any],
    countries: list[str],
) -> "pd.DataFrame":
    """Pivot table for indicator mode.

    Creates DataFrame with ["title", "country", "unit", "scale"] as index and dates as columns.

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
    # pylint: disable=import-outside-toplevel
    import pandas as pd

    rows: list[dict[str, Any]] = []
    # Group by title (indicator name), country, AND unit/scale
    for title in df["title"].unique():
        if pd.isna(title):
            continue
        title_df = df[df["title"] == title]
        for country in countries:
            country_df = title_df[title_df["country"] == country]
            if len(country_df) == 0:
                continue

            # Group by unique unit/scale combinations within this title+country
            # First, extract unit/scale for each row with fallback
            country_df = country_df.copy()
            units = []
            scales = []
            for _, data_row in country_df.iterrows():
                row_unit = data_row.get("unit")
                row_scale = data_row.get("scale")
                # Treat "-" as missing
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

            # Group by unit/scale and create one output row per group
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

                # Track if row has any non-zero values
                has_nonzero_value = False
                for d in dates:
                    val = group_df[group_df["date"] == d]["value"].values
                    if len(val) > 0 and pd.notna(val[0]):
                        row[str(d)] = val[0]
                        if val[0] != 0:
                            has_nonzero_value = True
                    else:
                        row[str(d)] = None

                # Skip rows where all date values are 0 or None
                if not has_nonzero_value:
                    continue

                rows.append(row)

    result_df = pd.DataFrame(rows)
    if not result_df.empty:
        result_df = result_df.set_index(["title", "country", "unit", "scale"])

    return result_df


def pivot_table_mode(
    df: "pd.DataFrame",
    dates: list[Any],
    countries: list[str],
    metadata: dict[str, Any],
) -> "pd.DataFrame":
    """Get a hierarchical pivot for table mode.

    Handles:
    - Parent/child hierarchy detection
    - Title simplification based on displayed ancestors
    - Proper indentation with visual hierarchy markers
    - Uniform vs per-row unit display
    - Hierarchy name headers

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
    # pylint: disable=import-outside-toplevel
    from collections import defaultdict

    import pandas as pd

    # Build the hierarchy context
    order_title_level = build_order_title_level(df)
    hierarchy_ctx = HierarchyContext(order_title_level)

    # Detect ISORA-style tables (topic hierarchy, dash-delimited labels)
    table_name = metadata.get("table", {}).get("hierarchy_name", "")
    dataflow_id = metadata.get("table", {}).get("dataflow_id", "")
    is_isora = "ISORA" in dataflow_id or "INDICATORS BY TOPIC" in table_name.upper()

    # Build helper maps for unit/scale inheritance
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

    # Capture unit/scale per order (from explicit columns or suffix) and inherit down
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

    # First pass: collect RAW data rows and track which orders have actual data
    # Title simplification is deferred until we know which ancestors will be displayed
    orders_with_data: set[int | float] = set()
    raw_data_rows: list[dict[str, Any]] = []

    # Include ALL orders that might have data - don't exclude category headers
    # because they can also have data values (aggregates)
    data_orders = df["order"].dropna().unique()

    for order in sorted(data_orders):
        order_df = df[df["order"] == order]

        # Data rows - one per country, per series/dimension combination
        for country in countries:
            country_df = order_df[order_df["country"] == country]
            if country_df.empty:
                continue

            # Determine grouping columns - use series_id if available, otherwise
            # group by dimension code columns to separate different series
            # ALWAYS include dimension code columns to separate by counterpart_country, etc.
            # Exclude dv_type_code - it's just "Reported official data" for everything
            dim_code_cols = [
                c
                for c in country_df.columns
                if c.endswith("_code")
                and c not in ("country_code", "frequency_code", "dv_type_code")
                and country_df[c].notna().any()
            ]
            if "series_id" in country_df.columns:
                # Include series_id AND dimension codes
                group_cols = ["series_id"] + [
                    c for c in dim_code_cols if c != "series_id"
                ]
            else:
                group_cols = dim_code_cols if dim_code_cols else ["symbol"]

            # Ensure all group columns exist and handle NaN
            valid_group_cols = [c for c in group_cols if c in country_df.columns]
            if not valid_group_cols:
                valid_group_cols = ["symbol"] if "symbol" in country_df.columns else []

            if valid_group_cols:
                for _, series_df in country_df.groupby(valid_group_cols, dropna=False):
                    if series_df.empty:
                        continue
                    first_in_series = series_df.iloc[0]

                    # Check if this series has ANY data for the selected dates
                    has_data = False
                    row_values: dict[str, Any] = {}
                    for d in dates:
                        # Handle date comparison - d may be string or datetime.date
                        # series_df["date"] may also be either type
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

                        # Store RAW title - simplification deferred
                        title = first_in_series.get("title", "")
                        if not title:
                            ind_code = first_in_series.get("indicator_code", "")
                            if ind_code:
                                title = ind_code.replace("_", " ").capitalize()

                        row_unit = first_in_series.get("unit") or ""
                        row_scale = first_in_series.get("scale") or ""

                        # Fallback to order-level (inherited) unit/scale when missing
                        inherited_unit, inherited_scale = unit_scale_by_order.get(
                            order, (None, None)
                        )

                        if not row_unit and inherited_unit:
                            row_unit = inherited_unit
                        if not row_scale and inherited_scale:
                            row_scale = inherited_scale

                        # As a last resort, parse the title suffix for unit/scale
                        if not row_unit or not row_scale:
                            parsed_unit, parsed_scale = extract_unit_scale_from_title(
                                title
                            )
                            if not row_unit and parsed_unit:
                                row_unit = parsed_unit
                            if not row_scale and parsed_scale:
                                row_scale = parsed_scale

                        # Collect dimension values for grouping headers
                        # Look for *_code fields that indicate dimension breakdowns
                        # Column names in the data are lowercase (sector_code, gfs_grp_code, etc.)
                        dimension_values: dict[str, tuple[str, str]] = {}
                        # Dimensions that should create grouping headers
                        # Keys are uppercase (for display), values are lowercase (for column lookup)
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

    # Find all parent orders that lead to data rows
    parent_orders: set[int | float] = set()
    true_header_parents: set[int | float] = set()

    for order in orders_with_data:
        order_df = df[df["order"] == order]
        if len(order_df) == 0:
            continue
        parent_id = order_df.iloc[0].get("parent_id")
        # Trace up the hierarchy to find all parent headers
        while parent_id:
            parent_df = df[df["hierarchy_node_id"] == parent_id]
            # hierarchy_node_id might be "CL_X___CODE" but parent_id is just "CODE"
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
                # Track true headers separately for title stripping
                if parent_is_header:
                    true_header_parents.add(parent_order)
            parent_id = parent_df.iloc[0].get("parent_id")

    # Build per-country orders_with_data
    country_orders_with_data: dict[str, set[int | float]] = {}
    for raw_row in raw_data_rows:
        country = raw_row["country"]
        order = raw_row["order"]
        if country not in country_orders_with_data:
            country_orders_with_data[country] = set()
        country_orders_with_data[country].add(order)

    # Build per-country parent_orders (ancestors of data rows for each country)
    country_parent_orders: dict[str, set[int | float]] = {}
    for country, country_data_orders in country_orders_with_data.items():
        country_parents: set[int | float] = set()
        for order in country_data_orders:
            order_df = df[df["order"] == order]
            if len(order_df) == 0:
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

    # Compute the union of all per-country parent orders
    # This ensures we only show headers that lead to data for at least one country in the result
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

    # Detect which dimensions have multiple values (need grouping headers)
    dim_value_sets: dict[str, set[str]] = {}
    for dr in data_rows:
        for dim_id, (code, label) in dr.get("dimension_values", {}).items():
            if dim_id not in dim_value_sets:
                dim_value_sets[dim_id] = set()
            dim_value_sets[dim_id].add(code)

    # Dimensions with multiple values need synthetic grouping headers
    multi_value_dims = [
        dim_id for dim_id, codes in dim_value_sets.items() if len(codes) > 1
    ]

    # If we have multi-value dimensions, add grouping info to data rows
    if multi_value_dims:
        # Sort multi_value_dims in a sensible order (SECTOR first, then others)
        dim_priority = {"SECTOR": 0, "GFS_GRP": 1, "TYPE_OF_TRANSFORMATION": 2}
        multi_value_dims.sort(key=lambda d: dim_priority.get(d, 99))

        for dr in data_rows:
            dim_vals = dr.get("dimension_values", {})
            # Build grouping key from multi-value dimensions
            grouping_parts = []
            for dim_id in multi_value_dims:
                if dim_id in dim_vals:
                    code, label = dim_vals[dim_id]
                    grouping_parts.append((dim_id, code, label))
            dr["_grouping_dims"] = grouping_parts

        # Sort data rows by (grouping dimensions, order) for proper grouping
        # This groups all items with the same dimension values together,
        # then sorts by hierarchical order within each group
        def row_sort_key(row: dict) -> tuple:
            grouping = tuple(
                (dim_id, code) for dim_id, code, label in row.get("_grouping_dims", [])
            )
            order_val = row.get("order", 0)
            return grouping + (order_val,)

        data_rows.sort(key=row_sort_key)

    # Note: ISORA tables use dash-delimited titles but we do NOT create synthetic
    # headers from them as it causes false groupings (e.g., "On" from "On-time").
    # Instead, we rely on the existing hierarchy metadata (topic parent nodes).

    # Check if all data rows have the same unit and scale
    all_units = {dr.get("unit") for dr in data_rows if dr.get("unit")}
    all_scales = {dr.get("scale") for dr in data_rows if dr.get("scale")}
    uniform_unit = all_units.pop() if len(all_units) == 1 else None
    uniform_scale = all_scales.pop() if len(all_scales) == 1 else None
    # If there are multiple units, we need per-row display even if scale is uniform
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

    # Check if we need to add a hierarchy name header
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

    # Add it if: (1) first level-0 is data, OR (2) hierarchy name differs from first level-0 title
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

    # Second pass: build final rows with headers that have data children
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

    all_orders = list(df["order"].unique())
    sorted_orders = sorted(all_orders, key=lambda o: float(o))  # pylint: disable=W0108

    # Universal dimension grouping, when multi_value_dims exists
    dim_group_map: dict[tuple, list[dict]] = defaultdict(list)
    if multi_value_dims:
        for dr in data_rows:
            grouping_key = tuple(dr.get("_grouping_dims", []))
            dim_group_map[grouping_key].append(dr)
    else:
        dim_group_map[()] = data_rows

    def format_dim_labels(grouping_key: tuple) -> str:
        """Format all dimension labels from a grouping key into a display string.

        Excludes TYPE_OF_TRANSFORMATION when its value is a unit-like label
        (e.g., "Domestic currency") since that's already shown in the parent
        row's unit suffix. Keeps meaningful transformation types like "Index",
        "Percent change", etc.
        """
        if not grouping_key:
            return ""

        # Unit-like transformation values to exclude (already shown in parent suffix)
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

        # If filtering removed everything, fall back to the unfiltered labels so we
        # never render a blank title row for unit-only dimensions.
        effective_labels = filtered_labels if filtered_labels else labels

        return " - ".join(effective_labels) if effective_labels else ""

    # Build a map of order -> list of (grouping_key, data_rows_for_order)
    # Preserve original data order by iterating data_rows directly
    order_to_dim_data: dict[int | float, list[tuple[tuple, list[dict]]]] = defaultdict(
        list
    )
    seen_order_keys: dict[int | float, set[tuple]] = defaultdict(set)

    for dr in data_rows:
        order = dr["order"]
        grouping_key = tuple(dr.get("_grouping_dims", []))

        if grouping_key in seen_order_keys[order]:
            # Find existing entry and append
            for entry in order_to_dim_data[order]:
                if entry[0] == grouping_key:
                    entry[1].append(dr)
                    break
        else:
            # New grouping key for this order - add in data order
            order_to_dim_data[order].append((grouping_key, [dr]))
            seen_order_keys[order].add(grouping_key)

    # Compute parent orders globally (across all dimension groups)
    all_orders_with_data = {dr["order"] for dr in data_rows}
    global_parent_orders: set[int | float] = set()
    for order in all_orders_with_data:
        order_df = df[df["order"] == order]
        if len(order_df) == 0:
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

    # Track BOP-only header nodes we intentionally skip so we can promote descendants.
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
            if len(parent_df) == 0:
                break
            pid = str(parent_df.iloc[0].get("parent_id") or "")
        return adjusted

    # Track the last meaningful (non-BOP-only) header title at each level.
    # This is used to preserve qualifiers like "excluding exceptional financing"
    # for BOP suffix rows even when intermediate accounting-entry headers are skipped.
    last_meaningful_header_by_level: dict[int, str] = {}

    def _normalize_title(raw_title: str | None) -> str:
        title = (raw_title or "").lstrip()

        # Remove header marker (used for promoted headers in the rendered output)
        if title.startswith("▸"):
            title = title[1:].lstrip()

        # Strip parenthetical unit suffix
        if " (" in title and title.endswith(")"):
            paren_idx = title.rfind(" (")
            if paren_idx > 0:
                title = title[:paren_idx]

        # Strip common unit qualifiers that can trail titles
        unit_suffixes = [", Transactions", ", Stocks", ", Flows"]
        for suffix in unit_suffixes:
            if title.endswith(suffix):
                title = title[: -len(suffix)]
                break

        return title

    def _nearest_non_bop_ancestor_title(parent_id: Any) -> str | None:
        pid = str(parent_id) if parent_id else ""
        safety = 0
        while pid and safety < 50:
            safety += 1
            parent_df = _lookup_parent_row(pid)
            if len(parent_df) == 0:
                return None
            parent_first = parent_df.iloc[0]
            parent_title = _normalize_title(str(parent_first.get("title") or ""))
            if (
                parent_title
                and not is_bop_suffix_only(parent_title)
                and not parent_title.endswith((", Net", ", Credit", ", Debit"))
            ):
                return parent_title
            pid = str(parent_first.get("parent_id") or "")
        return None

    # OUTER LOOP: Iterate by sorted_orders (ITEM first)
    for order in sorted_orders:
        order_df = df[df["order"] == order]
        if order_df.empty:
            continue
        first = order_df.iloc[0]
        level = first["level"] or 0

        # Clear deeper header context when we move up the tree.
        for k in [k for k in last_meaningful_header_by_level if k > level]:
            del last_meaningful_header_by_level[k]

        is_header = first["is_category_header"]
        title = first["title"] or ""
        original_unit_suffix = ""

        # Strip parenthetical unit suffix
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

        # Determine if this order should be rendered as a header
        is_promoted_header = (
            not is_header
            and order in global_parent_orders
            and order not in all_orders_with_data
        )
        # Only render as header if it doesn't have data of its own
        should_render_as_header = (
            is_header or is_promoted_header
        ) and order not in all_orders_with_data

        # Skip headers that don't lead to any data
        if should_render_as_header and order not in global_parent_orders:
            # If this is a BOP-only accounting-entry header (Net/Credit/Debit/etc.),
            # track it even when skipped for "no data" so descendants can be promoted.
            if is_bop_suffix_only(title):
                _track_skipped_parent_ids(first.to_dict())
            continue

        # Skip phantom BOP headers that are just "Net", "Credit", "Debit", etc.
        # Record them so descendants can be promoted (prevents Debit nesting under Credit
        # when an intermediate accounting-entry node is hidden).
        if should_render_as_header and is_bop_suffix_only(title):
            _track_skipped_parent_ids(first.to_dict())
            continue

        # If a row's parent (or higher ancestor) was skipped as a BOP-only header,
        # promote it so it doesn't appear as a child of the wrong visible node.
        level = _promote_level_if_parent_skipped(level, first.get("parent_id"))

        # ISORA: Only show topic headers
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

        # Headers get minimal simplification
        if should_render_as_header:
            if title.startswith("Financial corporations, "):
                title = title[len("Financial corporations, ") :]
            elif title.startswith("Depository corporations, "):
                title = title[len("Depository corporations, ") :]
        else:
            # Strip ancestor title prefixes
            best_prefix = hierarchy_ctx.find_best_prefix(order, title, parent_orders)
            if best_prefix and title.startswith(best_prefix):
                relative = title[len(best_prefix) :].lstrip(", :")
                # Don't strip if it would leave only a BOP suffix
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

        # Update header context for this level, or (for BOP suffix rows) inherit
        # the nearest meaningful header when the row's base is a strict prefix.
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

        # Calculate indent
        extra_indent = "   " if should_add_table_header else ""
        indent = extra_indent + "   " * level

        prefix = "▸ " if should_render_as_header else "  "

        if should_render_as_header:
            if order in global_parent_orders:
                if is_isora and title and "___" in title:
                    continue

                header_title = title
                if has_uniform_unit_scale:
                    if level == 0 and uniform_suffix:
                        header_title += uniform_suffix
                elif original_unit_suffix:
                    header_title += original_unit_suffix

                # Check if this header order also has data
                order_data_rows = [dr for dr in data_rows if dr["order"] == order]
                if order_data_rows:
                    # Header WITH data - render data rows with header styling
                    order_dim_groups = order_to_dim_data.get(order, [])
                    if order_dim_groups and len(order_dim_groups[0][1]) > 1:
                        # Multiple dimension values - show header then dimension breakdown
                        row = {
                            "title": f"{indent}{prefix}{header_title}",
                            "country": "",
                        }
                        for d in dates:
                            row[str(d)] = ""
                        rows.append(row)
                        # Render dimension breakdown under header
                        for grouping_key, dim_data_rows in sorted(order_dim_groups):
                            if grouping_key:
                                dim_label = format_dim_labels(grouping_key)
                                for dr in dim_data_rows:
                                    dim_indent = extra_indent + "   " * (level + 1)
                                    row = {
                                        "title": f"{dim_indent}{dim_label}",
                                        "country": dr["country"],
                                    }
                                    row.update(dr["values"])
                                    rows.append(row)
                    else:
                        # Single or no dimension - show header row with its data
                        for dr in order_data_rows:
                            row = {
                                "title": f"{indent}{prefix}{header_title}",
                                "country": dr["country"],
                            }
                            row.update(dr["values"])
                            rows.append(row)
                else:
                    # Pure header - no data
                    row = {
                        "title": f"{indent}{prefix}{header_title}",
                        "country": "",
                    }
                    for d in dates:
                        row[str(d)] = ""
                    rows.append(row)
        else:
            # Data row - check if THIS specific order has multiple dimension values
            order_dim_groups = order_to_dim_data.get(order, [])
            # Has multi dims if there's more than one grouping key OR
            # if a single grouping key has multiple rows (multiple counterpart countries, etc.)
            order_has_multi_dims = len(order_dim_groups) > 1 or (
                len(order_dim_groups) == 1 and len(order_dim_groups[0][1]) > 1
            )

            if order_has_multi_dims:
                # Multiple dimension groups for this item - show breakdown
                data_level = level
                data_indent = extra_indent + "   " * data_level

                display_title = title
                if data_level == 0 and uniform_suffix and not should_add_table_header:
                    display_title += uniform_suffix
                elif not has_uniform_unit_scale:
                    # Get unit from first data row for this order
                    first_dr = order_dim_groups[0][1][0] if order_dim_groups else None
                    if first_dr:
                        row_unit_suffix = format_unit_suffix(
                            first_dr.get("unit"), first_dr.get("scale")
                        )
                        display_title += row_unit_suffix

                # Find "World" or top-level aggregate to show on parent row
                # World is typically code "G001" for COUNTERPART_COUNTRY dimension
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

                # Item row - shows World data if available, otherwise empty
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

                # Check if this is a COUNTERPART_COUNTRY breakdown
                has_counterpart_country = any(
                    dim_id == "COUNTERPART_COUNTRY"
                    for gk, _ in order_dim_groups
                    if gk
                    for dim_id, _, _ in gk
                )

                if has_counterpart_country:
                    # Separate groups from countries and order: groups first, then countries
                    cc_indent = extra_indent + "   " * (data_level + 1)

                    # Helper to detect if a code is a group vs individual country
                    # ISO country codes are 3 letters (e.g., USA, GBR, CHN)
                    # Group codes have letter+digit patterns (e.g., G001, GX225, U005, TX983)
                    def is_group_code(code: str) -> bool:
                        """Group codes have letter(s) followed by digits."""
                        # ISO codes are exactly 3 uppercase letters
                        if re.match(r"^[A-Z]{3}$", code):
                            return False
                        # Group codes: G###, GX###, U###, TX###
                        return bool(re.match(r"^[A-Z]+\d+$", code))

                    # Collect groups and individual countries separately
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

                    # Helper to get the max absolute value for sorting
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

                    # Render groups first (sorted by value, highest first),
                    # then countries (sorted by value, highest first)
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
                    # Non-counterpart-country dimension breakdown (e.g., SECTOR)
                    for grouping_key, dim_data_rows in sorted(order_dim_groups):
                        if grouping_key == world_grouping_key:
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
                # Single dimension group - original behavior
                for dr in data_rows:
                    if dr["order"] == order:
                        # Use the already-corrected level (includes BOP overrides)
                        data_level = level
                        data_indent = extra_indent + "   " * data_level

                        # Use the stripped title (from BOP child processing above), not dr["title"]
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
    country: str,
    limit: int | None,
    metadata: dict[str, Any],
) -> "pd.DataFrame":
    """Pivot table data based on whether hierarchy exists.

    This function determines whether to use indicator mode (simple pivot)
    or table mode (hierarchical pivot) based on the data.

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
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    df = DataFrame(result)
    all_dates = sorted(df["date"].dropna().unique().tolist(), reverse=True)
    dates = all_dates[:limit] if limit is not None and limit > 0 else all_dates
    countries = sorted(df["country"].dropna().unique().tolist())

    # Check if any requested countries have no data for the selected dates
    # and warn the user
    if country and dates:
        requested_countries = [c.strip() for c in country.split(",")]
        check_missing_country_data(df, requested_countries, dates, countries)

    has_hierarchy = df["order"].notna().any() if "order" in df.columns else False

    if not has_hierarchy:
        return pivot_indicator_mode(df, dates, countries)

    return pivot_table_mode(df, dates, countries, metadata)
