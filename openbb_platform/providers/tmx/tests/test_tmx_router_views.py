"""Tests for the router endpoints that serve views rather than models."""

from base64 import b64decode

import pytest
from fastapi import HTTPException
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_tmx.routers import (
    equity as equity_router,
    etf as etf_router,
    options as options_router,
)

PDF = b"%PDF-1.6 filing bytes"

FILING_URL = (
    "https://sedar.com/get?symbol=AC:CA&dateFiled=2026-06-01"
    "&formDescription=Annual%20Information%20Form"
)

FILINGS = [
    {
        "filing_date": "2026-06-01",
        "report_type": "AIF",
        "description": "Annual Information Form",
        "report_url": FILING_URL,
    },
    {
        "filing_date": "2026-05-01",
        "report_type": "Material Change",
        "description": "Material Change",
        "report_url": "https://sedar.com/get?symbol=AC:CA",
    },
    {"filing_date": "2026-04-01", "report_type": "AIF", "report_url": None},
]


class TestFilingChoices:
    """The filings the file selector offers."""

    @pytest.fixture
    def filings(self, monkeypatch):
        """Serve the published filings."""

        async def found(symbol, start_date=None, end_date=None):
            return FILINGS

        monkeypatch.setattr(equity_router, "_filings", found)

    async def test_a_description_is_appended_when_it_adds_something(self, filings):
        choices = await equity_router.filing_choices("AC")

        assert choices[0]["label"] == "2026-06-01 - AIF - Annual Information Form"
        assert choices[0]["value"] == FILING_URL

    async def test_a_description_matching_the_report_is_left_off(self, filings):
        choices = await equity_router.filing_choices("AC")

        assert choices[1]["label"] == "2026-05-01 - Material Change"

    async def test_a_filing_without_a_document_is_skipped(self, filings):
        assert len(await equity_router.filing_choices("AC")) == 2


class TestFilings:
    """Reading the filings a symbol has published."""

    async def test_the_published_filings_are_returned(self, monkeypatch):
        from openbb_tmx.models.company_filings import TmxCompanyFilingsData

        filing = TmxCompanyFilingsData.model_validate(
            {
                "filing_date": "2026-06-01",
                "report_type": "AIF",
                "description": "Annual Information Form",
                "report_url": FILING_URL,
            }
        )

        async def fetch(params, credentials):
            return [filing]

        monkeypatch.setattr(
            "openbb_tmx.models.company_filings.TmxCompanyFilingsFetcher.fetch_data",
            fetch,
        )
        found = await equity_router._filings("AC")

        assert [f["report_type"] for f in found] == ["AIF"]

    async def test_an_unreachable_feed_returns_nothing(self, monkeypatch):
        async def failing(params, credentials):
            raise OpenBBError("SEDAR is down.")

        monkeypatch.setattr(
            "openbb_tmx.models.company_filings.TmxCompanyFilingsFetcher.fetch_data",
            failing,
        )

        assert await equity_router._filings("AC") == []


@pytest.fixture
def served(monkeypatch):
    """Serve a document for every download."""

    async def download(url, use_cache=True, accept_type="json", **kwargs):
        return PDF

    monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", download)


@pytest.fixture
def refused(monkeypatch):
    """Refuse every download the way a walled host does."""

    async def download(url, use_cache=True, accept_type="json", **kwargs):
        return b"<HTML>Forbidden</HTML>"

    monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", download)


class TestFilingsView:
    """Handing the viewer the documents it selected."""

    def test_a_filing_is_named_from_its_url(self):
        assert equity_router._filing_filename(FILING_URL) == (
            "AC 2026-06-01 Annual Information Form.pdf"
        )

    def test_a_url_naming_nothing_falls_back(self):
        assert equity_router._filing_filename("https://sedar.com/get") == "filing.pdf"

    async def test_the_document_is_served_to_the_viewer(self, served):
        viewed = await equity_router.filings_view(
            equity_router.FilingRequest(url=FILING_URL)
        )

        assert b64decode(viewed[0]["content"]) == PDF
        assert viewed[0]["data_format"] == {
            "data_type": "pdf",
            "filename": "AC 2026-06-01 Annual Information Form.pdf",
        }

    async def test_a_document_the_host_withholds_falls_back_to_its_url(self, refused):
        viewed = await equity_router.filings_view(
            equity_router.FilingRequest(url=FILING_URL)
        )

        assert viewed[0]["url"] == FILING_URL
        assert "content" not in viewed[0]

    async def test_several_selections_are_accepted(self, served):
        viewed = await equity_router.filings_view(
            equity_router.FilingRequest(url=[FILING_URL, ""])
        )

        assert len(viewed) == 1


class TestAssetPages:
    """The styled overview pages."""

    @pytest.fixture
    def page(self, monkeypatch):
        """Serve a rendered overview."""

        async def html(symbol, theme):
            return f"<html>{symbol}:{theme}</html>"

        monkeypatch.setattr("openbb_tmx.utils.asset_info.asset_info_html", html)

    async def test_the_fund_page_is_served(self, page):
        response = await etf_router.fund_info_page("XIU", "light")

        assert response.status_code == 200
        assert b"XIU:light" in response.body

    async def test_the_asset_page_is_served(self, page):
        response = await equity_router.asset_info_page("AC", "dark")

        assert response.status_code == 200
        assert b"AC:dark" in response.body


class TestChartJson:
    """The shared loader behind every options chart route."""

    @pytest.fixture
    def loaded(self, monkeypatch, options_chain):
        """Serve one loaded chain to the chart routes."""

        async def load(symbol):
            return options_chain

        monkeypatch.setattr(
            "openbb_tmx.utils.options.data_handler.load_symbol", load, raising=False
        )

    async def test_the_figure_is_returned_as_json(self, loaded):
        from openbb_tmx.utils.options.create_stats import create_stats

        figure = await options_router._chart_json(
            create_stats, "AC", "dark", False, by="expiration"
        )

        assert figure["data"]
        assert figure["config"]["displayModeBar"] is False

    async def test_the_rows_are_returned_instead_when_asked(self, loaded):
        from openbb_tmx.utils.options.create_stats import create_stats

        rows = await options_router._chart_json(
            create_stats, "AC", "dark", True, by="expiration"
        )

        assert isinstance(rows, list)
        assert rows[0]["Calls"]

    async def test_an_unavailable_symbol_is_a_404(self, monkeypatch):
        async def missing(symbol):
            raise OpenBBError("No options available for NOPE.")

        monkeypatch.setattr(
            "openbb_tmx.utils.options.data_handler.load_symbol", missing, raising=False
        )

        with pytest.raises(HTTPException) as raised:
            await options_router._chart_json(None, "NOPE", "dark", False)

        assert raised.value.status_code == 404


class TestChartRoutes:
    """Each published chart route plots its own view."""

    @pytest.fixture
    def loaded(self, monkeypatch, options_chain):
        """Serve one loaded chain to the chart routes."""

        async def load(symbol):
            return options_chain

        monkeypatch.setattr(
            "openbb_tmx.utils.options.data_handler.load_symbol", load, raising=False
        )

    async def test_the_smile_is_plotted(self, loaded):
        assert (await options_router.smile_chart("AC"))["data"]

    async def test_the_surface_is_plotted(self, loaded):
        assert (await options_router.surface_chart("AC"))["data"]

    async def test_the_statistics_are_plotted(self, loaded):
        assert (await options_router.stats_chart("AC"))["data"]

    async def test_the_term_structure_is_plotted(self, loaded):
        assert (await options_router.term_structure_chart("AC"))["data"]


class TestTickerChoices:
    """The expiry and strike dropdowns the chart widgets read."""

    @pytest.fixture
    def loaded(self, monkeypatch, options_chain):
        """Load one chain into the shared cache."""
        from openbb_tmx.utils.options import data_handler

        data_handler.LOADED_SYMBOLS.clear()
        data_handler.LOADED_SYMBOLS["AC"] = options_chain

        async def load(symbol):
            return options_chain

        monkeypatch.setattr(
            "openbb_tmx.utils.options.data_handler.load_symbol", load, raising=False
        )

        yield options_chain

        data_handler.LOADED_SYMBOLS.clear()

    async def test_no_symbol_offers_nothing(self):
        assert await options_router.get_tickers() == []

    async def test_an_unavailable_symbol_offers_nothing(self, monkeypatch):
        async def missing(symbol):
            raise OpenBBError("No options available for NOPE.")

        monkeypatch.setattr(
            "openbb_tmx.utils.options.data_handler.load_symbol", missing, raising=False
        )

        assert await options_router.get_tickers("NOPE", expiry_list=True) == []

    async def test_the_expirations_are_offered(self, loaded):
        choices = await options_router.get_tickers("AC", expiry_list=True)

        assert [c["value"] for c in choices] == [str(e) for e in loaded.expirations]

    async def test_the_strikes_are_offered(self, loaded):
        choices = await options_router.get_tickers("AC", strike_list=True)

        assert choices[0]["label"] == "Nearest OTM"

    async def test_neither_list_offers_nothing(self, loaded):
        assert await options_router.get_tickers("AC") == []
