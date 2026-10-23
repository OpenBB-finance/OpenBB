"""Tests for the FFIEC concept metadata helpers."""

from openbb_federal_reserve.utils import concepts


class TestCleanName:
    """Tests for ``clean_name`` label normalization."""

    def test_returns_none_for_falsy_input(self):
        """An empty or ``None`` raw name yields ``None``."""
        assert concepts.clean_name(None) is None
        assert concepts.clean_name("") is None

    def test_strips_basis_footnote_and_titlecases(self):
        """Ratio basis, footnote markers, and casing are normalized."""
        assert (
            concepts.clean_name("NET INCOME as a percent of Average Assets (***)")
            == "Net Income"
        )

    def test_strips_abbreviated_average_assets_basis(self):
        """The abbreviated ``% of Avg Assets`` basis strips like ``Average Assets``."""
        assert (
            concepts.clean_name("Net Interest Income (TE) % of Avg Assets")
            == "Net Interest Income (TE)"
        )

    def test_keeps_meaningful_denominator(self):
        """A ratio's own denominator is its identity and is kept in full.

        The basis stripper is scoped to the section-redundant Average-Assets basis;
        it must not truncate a named denominator (``Tier 1 Capital``) nor leave a
        dangling ``as a`` connective behind.
        """
        assert (
            concepts.clean_name("Total securities as a % of tier 1 capital")
            == "Total Securities as a % of Tier 1 Capital"
        )
        assert (
            concepts.clean_name(
                "Net Interest Income (TE) as a percent of Average Earning Assets"
            )
            == "Net Interest Income (TE) as a Percent of Average Earning Assets"
        )

    def test_keeps_acronyms_and_lowers_small_words(self):
        """Known acronyms stay upper and small words lower after the first."""
        assert (
            concepts.clean_name("return on AVERAGE assets ROA")
            == "Return on Average Assets ROA"
        )

    def test_expands_residual_abbreviations(self):
        """Guide residual abbreviations expand to full words."""
        assert (
            concepts.clean_name("Ln&Ls Qtr Ann") == "Loans & Leases Quarter Annualized"
        )

    def test_keeps_literal_threshold_percentage(self):
        """A ``10% of …`` threshold is content, not a ratio basis, and is kept."""
        assert (
            concepts.clean_name(
                "FIRST ITEMIZED AMOUNT THAT EXCEEDS 10% OF ALL OTHER"
                " NONINTEREST INCOME (5408)"
            )
            == "First Itemized Amount That Exceeds 10% of All Other Noninterest Income"
        )

    def test_strips_parent_line_footnote(self):
        """A trailing parent-line cross-reference footnote is dropped."""
        assert concepts.clean_name("OTHER NONINTEREST INCOME (5408)") == (
            "Other Noninterest Income"
        )


class TestNarrative:
    """Tests for the ``_narrative`` placeholder filter."""

    def test_drops_pseudo_mdrm_placeholder(self):
        """A Pseudo MDRM placeholder definition is dropped to ``None``."""
        assert concepts._narrative("This is a Pseudo MDRM entry") is None

    def test_drops_empty_text(self):
        """Empty text resolves to ``None``."""
        assert concepts._narrative("") is None
        assert concepts._narrative(None) is None

    def test_passes_through_real_definition(self):
        """A genuine definition passes through unchanged."""
        assert concepts._narrative("Total assets.") == "Total assets."


class TestIndentedName:
    """Tests for ``indented_name`` indentation reapplication."""

    def test_returns_label_when_name_missing(self):
        """A missing name falls back to the label."""
        assert concepts.indented_name("> Foo", None) == "> Foo"

    def test_reapplies_indent_prefix(self):
        """The label's report-indentation prefix is restored on the name."""
        assert concepts.indented_name(">  Sub Item", "Subtotal") == ">  Subtotal"

    def test_no_prefix_returns_bare_name(self):
        """A label without an indent prefix yields the bare name."""
        assert concepts.indented_name("Top", "Total") == "Total"


class TestConceptIndex:
    """Tests for the ``concept_index`` join over taxonomy and MDRM maps."""

    def test_joins_types_names_and_definitions(self, monkeypatch):
        """Each concept code is keyed to its name, narrative, and monetary flag."""
        from openbb_federal_reserve.utils import cache, cdr, mdrm

        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())
        monkeypatch.setattr(cdr, "fetch_taxonomy", lambda *a, **k: b"")
        monkeypatch.setattr(
            cdr,
            "parse_taxonomy",
            lambda _content: [
                {"mdrm": "RCON2170", "data_type": "Monetary"},
                {"mdrm": "UBPRE013", "data_type": "Rate or ratio"},
                {"mdrm": "TEXT4461", "data_type": "Text"},
            ],
        )
        monkeypatch.setattr(
            mdrm,
            "fetch_mdrm_dictionary",
            lambda *a, **k: {
                "RCON2170": "TOTAL ASSETS",
                "UBPRE013": "RETURN ON ASSETS",
                "TEXT4461": "FIRST ITEMIZED AMOUNT",
            },
        )
        monkeypatch.setattr(
            mdrm,
            "fetch_mdrm_definitions",
            lambda *a, **k: {
                "RCON2170": "Total assets.",
                "UBPRE013": "Pseudo MDRM placeholder",
                "TEXT4461": "The field prefixed by the mnemonic TEXT is the name.",
            },
        )

        index = concepts.concept_index("ubpr_ratio_single")
        assert index["RCON2170"]["name"] == "Total Assets"
        assert index["RCON2170"]["narrative"] == "Total assets."
        assert index["RCON2170"]["monetary"] is True
        assert index["RCON2170"]["is_text"] is False
        assert index["UBPRE013"]["monetary"] is False
        assert index["UBPRE013"]["narrative"] is None
        assert index["TEXT4461"]["is_text"] is True
        assert index["TEXT4461"]["monetary"] is False
