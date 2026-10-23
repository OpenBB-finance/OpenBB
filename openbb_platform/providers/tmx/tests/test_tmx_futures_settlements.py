"""Tests for the Montreal Exchange settlement prices."""

import pytest

from openbb_tmx.utils.mx import (
    _contract_symbol,
    _parse_quotes,
    _settlement_value,
    get_root_settlements,
    get_settlement_prices,
)

QUOTE_HEAD = (
    "<thead><tr><th>Month</th><th>Bid price</th><th>Ask price</th>"
    "<th>Settl. price</th><th>Net change</th><th>Open int.</th>"
    "<th>Vol.</th></tr></thead>"
)


def _quote(month, *cells):
    """Build one published quote row."""
    published = "".join(f"<td>{cell}</td>" for cell in cells)

    return f'<tr><td class="text-left">{month}</td>{published}</tr>'


PAGE = f"""
<table class="data">
{QUOTE_HEAD}
<tbody>
{_quote("September 2026", "0", "0", "110.990", "0", "21,365", "0")}
{_quote("December 2026", "111.020", "111.040", "111.250", "0.040", "326,395", "1,356")}
{_quote("March 2027", "0", "0", "0", "0", "0", "0")}
{_quote("Trimester 2027", "0", "0", "99.500", "0", "0", "0")}
<tr><td class="text-left">June 2027</td><td>0</td></tr>
</tbody>
</table>
<table class="data">
<thead><tr><th>Expiry</th><th>Strike</th></tr></thead>
<tbody><tr><td>September 2026</td><td>1,790.0</td></tr></tbody>
</table>
<table class="data"><tbody><tr><td>No head here</td></tr></tbody></table>
"""


class TestSettlementValues:
    """Reading a published settlement cell."""

    def test_a_grouped_number_is_read(self):
        assert _settlement_value("1,790.5") == 1790.5

    def test_an_unsettled_contract_is_nothing(self):
        assert _settlement_value("0") is None

    @pytest.mark.parametrize("raw", ["", "n/a"])
    def test_an_unreadable_cell_is_nothing(self, raw):
        assert _settlement_value(raw) is None

    def test_a_cell_that_is_not_text_is_nothing(self):
        assert _settlement_value(None) is None


class TestContractSymbols:
    """Building a contract symbol from a delivery month."""

    def test_the_month_becomes_its_code(self):
        assert _contract_symbol("CRA", "September 2026") == "/CRAU6"
        assert _contract_symbol("AXF", "December 2030") == "/AXFZ0"

    def test_a_cell_that_names_no_month_is_nothing(self):
        assert _contract_symbol("CRA", "Trimester 2027") is None

    @pytest.mark.parametrize("cell", ["September", "September 18, 2026", ""])
    def test_a_cell_that_is_not_a_month_is_nothing(self, cell):
        assert _contract_symbol("CRA", cell) is None


class TestQuotesParsing:
    """Reading the published quotes page."""

    @pytest.fixture
    def settlements(self):
        """Parse the sample page once."""
        return _parse_quotes(PAGE, "CGF")

    def test_every_settled_month_is_addressed(self, settlements):
        assert set(settlements) == {"/CGF", "/CGFU6", "/CGFZ6"}

    def test_the_published_settlement_is_read(self, settlements):
        assert settlements["/CGFU6"] == 110.99
        assert settlements["/CGFZ6"] == 111.25

    def test_the_root_carries_the_front_month(self, settlements):
        assert settlements["/CGF"] == 110.99

    def test_an_unsettled_month_is_left_out(self, settlements):
        assert "/CGFH7" not in settlements

    def test_a_row_of_the_wrong_width_is_skipped(self, settlements):
        assert "/CGFM7" not in settlements

    def test_a_table_without_the_column_is_skipped(self, settlements):
        assert len(settlements) == 3

    def test_an_empty_page_yields_nothing(self):
        assert _parse_quotes("", "CGF") == {}


class TestRootSettlements:
    """Fetching one product's settlement prices."""

    @pytest.fixture(autouse=True)
    def _forget(self):
        """Keep each test from reading the previous one's result."""
        get_root_settlements.cache_clear()

        yield

        get_root_settlements.cache_clear()

    async def test_the_page_is_read(self, http):
        http["symbol=CGF"] = PAGE
        settlements = await get_root_settlements("CGF")

        assert settlements["/CGFU6"] == 110.99

    async def test_a_page_that_does_not_answer_yields_nothing(self, http):
        assert await get_root_settlements("CGF") == {}


class TestSettlementPrices:
    """Fetching the settlement prices of several products."""

    @pytest.fixture(autouse=True)
    def _forget(self):
        """Keep each test from reading the previous one's result."""
        get_root_settlements.cache_clear()

        yield

        get_root_settlements.cache_clear()

    async def test_every_product_is_read(self, http):
        http["symbol=CGF"] = PAGE
        http["symbol=CGZ"] = PAGE.replace("110.990", "104.600")
        settlements = await get_settlement_prices(["CGF", "CGZ"])

        assert settlements["/CGFU6"] == 110.99
        assert settlements["/CGZU6"] == 104.6

    async def test_a_product_that_cannot_be_read_is_skipped(self, http, monkeypatch):
        http["symbol=CGF"] = PAGE

        async def fail(root, use_cache=True):
            """Refuse one product."""
            if root == "CGZ":
                raise RuntimeError("refused")

            return await get_root_settlements(root, use_cache=use_cache)

        monkeypatch.setattr("openbb_tmx.utils.mx.get_root_settlements", fail)
        settlements = await get_settlement_prices(["CGF", "CGZ"])

        assert settlements["/CGFU6"] == 110.99
        assert "/CGZU6" not in settlements

    async def test_nothing_is_read_without_a_product(self):
        assert await get_settlement_prices([]) == {}
