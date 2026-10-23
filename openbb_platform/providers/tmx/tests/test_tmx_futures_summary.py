"""Tests for the Montreal Exchange session summary."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_tmx.utils.mx import (
    INDEX_PRODUCTS,
    _parse_summary,
    _summary_value,
    get_futures_summary,
)

CONTRACT_HEAD = (
    "<thead><tr><th>Month</th><th>Open</th><th>High</th><th>Low</th>"
    "<th>Last</th><th>Change</th><th>Volume</th><th>Open Interest</th></tr></thead>"
)


def _contract(root, code, year, month, values):
    """Build one contract row."""
    cells = "".join(f'<td data-order="{v}">{v}</td>' for v in values)

    return (
        f'<tr><td data-order="{month}" class="text-left">'
        f'<a href="/en/trading/data/quotes?symbol={root}#{root}{code}{year}">'
        f"{month}</a></td>{cells}</tr>"
    )


PAGE = f"""
<h1>Intra-Session Summary</h1>
<ul id="intrasession-summaries">
<li id="options">
<a href="#">Equity, Currency, Index and ETF Options
<span class="session">Session: 9:30 a.m.</span></a>
<div><table class="data">
<thead><tr><th>&nbsp;</th><th colspan="3">Call</th></tr>
<tr><th>Options</th><th>Trans.</th><th>Volume</th><th>Value</th></tr></thead>
<tbody><tr><td>Equity</td><td>1</td><td>2</td><td>3</td></tr></tbody>
</table></div>
</li>
<li id="cra">
<a href="#cra">Three-Month CORRA Futures (CRA)
<span class="session">Session: 2:00 a.m.</span></a>
<div><table class="data">
{CONTRACT_HEAD}
<tfoot><tr><th>Total</th><td colspan="5">&nbsp;</td><td>5,413</td>
<td>231,162</td></tr></tfoot>
<tbody>
{_contract("CRA", "U", "26", "2026-09-01", [97.62, 97.63, 97.6175, 97.6275, 0.01, 5413, 231162])}
{_contract("CRA", "Z", "26", "2026-12-01", [0, 0, 0, 0, 0, 0, 835])}
<tr><td class="text-left">No contract</td><td>0</td><td>0</td><td>0</td>
<td>0</td><td>0</td><td>0</td><td>0</td></tr>
</tbody></table></div>
</li>
<li id="sector-futures">
<a href="#sector-futures">Sector Index Futures (SXA, SXW)
<span class="session">Session: 8:00 p.m. (t-1)</span></a>
<div><table class="data">
{CONTRACT_HEAD}
<tbody>
<tr class="dark"><td class="text-left" colspan="8">
<a href="/en/trading/data/quotes?symbol=SXA#quotes">SXA</a></td></tr>
{_contract("SXA", "U", "26", "2026-09-01", [0, 0, 0, 0, 0, 0, 12])}
</tbody>
<tbody>
{_contract("SXW", "Z", "26", "2026-12-01", [0, 0, 0, 0, 0, 0, 0])}
</tbody>
</table></div>
</li>
<li id="share-futures">
<a href="#share-futures">Share Futures
<span class="session">Session: 6:00 a.m.</span></a>
<div><table class="data">
<thead><tr><th>Symbol</th><th>Transactions</th><th>Volume</th>
<th>Open Interest</th></tr></thead>
<tbody>
<tr><td data-order="FAA" class="text-left">
<a href="/en/trading/data/quotes?symbol=FAA*#quotes">FAA</a></td>
<td data-order="0">0</td><td data-order="0">0</td>
<td data-order="3140">3,140</td></tr>
<tr><td data-order="" class="text-left"></td><td data-order="0">0</td>
<td data-order="0">0</td><td data-order="0">0</td></tr>
</tbody></table></div>
</li>
<li id="baf">
<a href="#baf">Basis Trade on Close (BAF)
<span class="session">Session: 9:30 a.m.</span></a>
<div><table class="data">
<thead><tr><th>Month</th><th>Open</th><th>High</th><th>Low</th><th>Last</th>
<th>Change</th><th>Volume</th><th>Value</th></tr></thead>
<tbody>
{_contract("BAF", "U", "26", "2026-09-01", [27.5, 27.5, 27.5, 27.5, -4, 75, 1800])}
</tbody></table></div>
</li>
<li id="sxo">
<a href="#sxo">S&amp;P/TSX 60 Index Options (SXO)</a>
<div><table class="data">
<thead><tr><th>Expiry date</th><th>Strike</th><th>Last price</th></tr></thead>
<tbody><tr><td data-order="2026-09-18">September 18, 2026</td>
<td data-order="1790">1,790.0</td><td data-order="301.2">301.20</td></tr></tbody>
</table></div>
</li>
<li id="notes">
<a href="#notes">Notes</a>
<div><p>No table here.</p></div>
</li>
</ul>
"""


class TestSummaryValues:
    """Reading a published cell."""

    @pytest.mark.parametrize("field", ["open", "high", "low", "price"])
    def test_an_unquoted_price_is_nothing(self, field):
        """A level the exchange has not quoted is published as a zero."""
        assert _summary_value("0", field) is None

    @pytest.mark.parametrize("field", ["volume", "open_interest", "transactions"])
    def test_a_traded_count_keeps_its_zero(self, field):
        assert _summary_value("0", field) == 0

    @pytest.mark.parametrize("raw", ["", None, "n/a"])
    def test_an_unreadable_cell_is_nothing(self, raw):
        assert _summary_value(raw, "volume") is None

    def test_a_quoted_price_is_returned(self):
        assert _summary_value("97.6275", "price") == 97.6275


class TestSummaryParsing:
    """Reading the published session summary."""

    @pytest.fixture
    def rows(self):
        """Parse the sample page once."""
        return _parse_summary(PAGE)

    def test_contracts_are_addressed_by_their_symbol(self, rows):
        contracts = {r["symbol"] for r in rows if r.get("contract")}

        assert contracts == {"/CRAU6", "/CRAZ6", "/SXAU6", "/SXWZ6", "/BAFU6"}

    def test_an_unpublished_column_is_left_out(self, rows):
        found = next(r for r in rows if r["symbol"] == "/BAFU6")

        assert found["volume"] == 75
        assert "value" not in found

    def test_a_table_keyed_by_something_else_is_skipped(self, rows):
        assert all("Options" not in (r["name"] or "") for r in rows)
        assert all(r["root"] != "SXO" for r in rows)

    def test_the_contract_carries_its_delivery_month(self, rows):
        found = next(r for r in rows if r["symbol"] == "/CRAU6")

        assert found["contract"] == "CRAU26"
        assert found["expiration"] == "2026-09-01"
        assert found["root"] == "CRA"
        assert found["exchange"] == "MOE"

    def test_the_session_is_read(self, rows):
        found = next(r for r in rows if r["symbol"] == "/CRAU6")

        assert found["open"] == 97.62
        assert found["high"] == 97.63
        assert found["low"] == 97.6175
        assert found["price"] == 97.6275
        assert found["net_change"] == 0.01
        assert found["volume"] == 5413
        assert found["open_interest"] == 231162

    def test_a_contract_that_has_not_traded_keeps_its_open_interest(self, rows):
        found = next(r for r in rows if r["symbol"] == "/CRAZ6")

        assert found["price"] is None
        assert found["net_change"] is None
        assert found["volume"] == 0
        assert found["open_interest"] == 835

    def test_a_single_product_is_named_as_published(self, rows):
        found = next(r for r in rows if r["symbol"] == "/CRAU6")

        assert found["name"] == "Three-Month CORRA Futures"

    def test_a_shared_section_names_each_product(self, rows):
        names = {r["symbol"]: r["name"] for r in rows}

        assert names["/SXAU6"] == INDEX_PRODUCTS["SXA"]
        assert names["/SXWZ6"] == INDEX_PRODUCTS["SXW"]

    def test_a_product_reported_at_the_root_is_kept(self, rows):
        found = next(r for r in rows if r["symbol"] == "/FAA")

        assert found["contract"] is None
        assert found["name"] == "Share Futures"
        assert found["transactions"] == 0
        assert found["open_interest"] == 3140

    def test_options_sections_are_skipped(self, rows):
        assert all("Options" not in r["name"] for r in rows)

    def test_a_row_without_a_contract_is_skipped(self, rows):
        assert all(r["symbol"] != "/" for r in rows)
        assert len([r for r in rows if r["root"] == "CRA"]) == 2

    def test_a_separator_row_is_skipped(self, rows):
        assert all(r["symbol"] != "/SXA" for r in rows)

    def test_a_row_without_a_symbol_is_skipped(self, rows):
        assert len([r for r in rows if r.get("contract") is None]) == 1

    def test_a_section_without_a_table_is_skipped(self, rows):
        assert all(r["name"] != "Notes" for r in rows)

    def test_an_empty_page_yields_nothing(self):
        assert _parse_summary("") == []


class TestFuturesSummary:
    """Fetching the published session summary."""

    @pytest.fixture(autouse=True)
    def _forget(self):
        """Keep each test from reading the previous one's result."""
        get_futures_summary.cache_clear()

        yield

        get_futures_summary.cache_clear()

    async def test_the_summary_is_read(self, http):
        http["intra-session-summary"] = PAGE
        rows = await get_futures_summary()

        assert len(rows) == 6
        assert rows[0]["symbol"] == "/CRAU6"

    async def test_an_unreadable_summary_is_reported(self, http):
        http["intra-session-summary"] = "<html></html>"

        with pytest.raises(OpenBBError, match="came back empty"):
            await get_futures_summary()
