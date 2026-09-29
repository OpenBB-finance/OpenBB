"""Tests for the USDA PSD report downloader and query builder."""

import asyncio

import pytest
from aiohttp import ClientError
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.utils import psd_data_downloader as D
from openbb_government_us.usda.utils.psd_codes import ATTRIBUTES, REGIONS

HELPERS = "openbb_core.provider.utils.helpers"

REPORT_CSV = "\r\n".join(
    [
        "Coffee Summary",
        "",
        "",
        ",2022/23,2023/24",
        "Production",
        "Brazil,65.0,55.0",
    ]
)

REPORT_HTML = '<span class="rptSubTitle">Coffee  Million 60-kg Bags</span>'

DEFAULT_COUNTRIES = (("United States", "US"), ("Brazil", "BR"), ("China", "CH"))

DEFAULT_ROWS = [
    {
        "commodity": "Corn",
        "attribute": "Production",
        "country": "United States",
        "unit Description": "(1000 MT)",
        "2023/2024": 389.0,
        "2024/2025": 400.0,
    },
    {
        "commodity": None,
        "attribute": None,
        "country": "Brazil",
        "unit Description": "(1000 MT)",
        "2023/2024": 122.0,
        "2024/2025": 130.0,
    },
]


class _FakeTextResponse:
    """Mirrors the platform session's response, whose text is awaited."""

    def __init__(self, text=""):
        self._text = text

    async def text(self):
        """Return the canned text body."""
        return self._text


class _FakeReportSession:
    """Mirrors the platform session used to download a report."""

    def __init__(self, handler):
        self._handler = handler
        self.urls: list = []
        self.closed = False

    async def get(self, url, **kwargs):
        """Record the request and return the handler's response."""
        self.urls.append(url)
        return self._handler(url)

    async def close(self):
        """Mark the session closed."""
        self.closed = True


class _FakeApiResponse:
    """Mirrors the synchronous metadata response."""

    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        """Return the canned payload."""
        return self._payload


class _FakeQueryResponse:
    """Mirrors the query response, used as an async context manager."""

    def __init__(self, status=200, payload=None, json_error=None):
        self.status = status
        self._payload = {} if payload is None else payload
        self._json_error = json_error

    async def __aenter__(self):
        """Enter the response context."""
        return self

    async def __aexit__(self, *exc):
        """Leave the response context."""
        return False

    async def json(self):
        """Return the canned payload or raise the canned error."""
        if self._json_error is not None:
            raise self._json_error
        return self._payload


class _FakeQuerySession:
    """Mirrors the platform session used to post the PSD query."""

    def __init__(self, handler):
        self._handler = handler
        self.payloads: list = []

    async def post(self, url, json=None, **kwargs):
        """Record the payload and return the handler's response."""
        self.payloads.append(json)
        return self._handler(json)

    async def __aenter__(self):
        """Enter the session context."""
        return self

    async def __aexit__(self, *exc):
        """Leave the session context."""
        return False


def _install_session(monkeypatch, session):
    """Point the platform session factory at a fake session."""

    async def _factory():
        return session

    monkeypatch.setattr(f"{HELPERS}.get_async_requests_session", _factory)
    return session


def _install_metadata(monkeypatch, attribute_ids=(28, 88, 57), countries=None):
    """Point the metadata API at canned attribute and country payloads."""
    countries = DEFAULT_COUNTRIES if countries is None else countries

    def _make_request(url, **kwargs):
        if "GetMultiCommodityAttributes" in url:
            return _FakeApiResponse(200, [{"attributeId": i} for i in attribute_ids])
        return _FakeApiResponse(
            200, [{"value": code, "text": name} for name, code in countries]
        )

    monkeypatch.setattr(f"{HELPERS}.make_request", _make_request)


def _install_query(
    monkeypatch, rows=None, status=200, post_error=None, json_error=None
):
    """Point the query endpoint at a canned result set."""
    rows = DEFAULT_ROWS if rows is None else rows

    def _handler(payload):
        if post_error is not None:
            raise post_error
        return _FakeQueryResponse(
            status=status,
            payload={"queryResult": rows},
            json_error=json_error,
        )

    return _install_session(monkeypatch, _FakeQuerySession(_handler))


class TestGetReportUrl:
    """Tests for building a report's download URL."""

    def test_builds_the_download_url(self):
        """The URL carries the report id, its template and the CSV format."""
        assert D.get_report_url(2109) == (
            "https://apps.fas.usda.gov/psdonline/reportHandler.ashx?"
            "reportId=2109&templateId=8&format=csv&fileName=Coffee_Summary"
        )

    def test_the_format_is_selectable(self):
        """The HTML rendering of the same report is requested by format."""
        assert D.get_report_url(2109, "html").endswith(
            "&format=html&fileName=Coffee_Summary"
        )

    def test_punctuation_is_stripped_from_the_file_name(self):
        """Spaces become underscores and commas are dropped from the name."""
        assert D.get_report_url(2535).endswith("fileName=Coffee_Summary_Continued")

    def test_an_unknown_report_raises(self):
        """A report id no group publishes is rejected."""
        with pytest.raises(ValueError, match="Report ID 999999 not found"):
            D.get_report_url(999999)


class TestGetPsdReportData:
    """Tests for downloading and parsing a PSD report."""

    def test_returns_the_parsed_report(self, monkeypatch):
        """The CSV is parsed with the report's own template."""

        def _handler(url):
            return _FakeTextResponse(REPORT_HTML if "html" in url else REPORT_CSV)

        session = _install_session(monkeypatch, _FakeReportSession(_handler))
        result = asyncio.run(D.get_psd_report_data(2109))
        assert result["report"] == "Coffee Summary"
        assert result["template"] == 8
        assert result["data"][0] == {
            "region": None,
            "country": "Brazil",
            "commodity": "Coffee",
            "attribute": "Production",
            "marketing_year": "2022/23",
            "value": 65.0,
            "unit": "Million 60-kg Bags",
        }
        assert session.closed is True

    def test_both_renderings_are_requested(self, monkeypatch):
        """The HTML carries the unit, the CSV carries the values."""

        def _handler(url):
            return _FakeTextResponse(REPORT_HTML if "html" in url else REPORT_CSV)

        session = _install_session(monkeypatch, _FakeReportSession(_handler))
        asyncio.run(D.get_psd_report_data(2109))
        assert session.urls == [
            D.get_report_url(2109, "html"),
            D.get_report_url(2109, "csv"),
        ]

    def test_an_unknown_report_id_raises(self, monkeypatch):
        """A report id no group publishes never reaches the network."""
        session = _install_session(
            monkeypatch, _FakeReportSession(lambda url: _FakeTextResponse(""))
        )
        with pytest.raises(OpenBBError, match="Invalid report ID -> 999999"):
            asyncio.run(D.get_psd_report_data(999999))
        assert session.urls == []

    def test_a_transport_failure_is_wrapped(self, monkeypatch):
        """A dropped connection is reported against the report id."""

        def _handler(url):
            raise ClientError("connection reset")

        session = _install_session(monkeypatch, _FakeReportSession(_handler))
        with pytest.raises(OpenBBError, match="Error fetching report 2109"):
            asyncio.run(D.get_psd_report_data(2109))
        assert session.closed is True

    def test_a_server_error_body_raises(self, monkeypatch):
        """The host answers 200 with an error body, which is not data."""

        def _handler(url):
            return _FakeTextResponse("An unexpected Error occurred")

        _install_session(monkeypatch, _FakeReportSession(_handler))
        with pytest.raises(OpenBBError, match="Server error fetching report 2109"):
            asyncio.run(D.get_psd_report_data(2109))


class TestGetCommodityAttributes:
    """Tests for resolving the attributes a commodity publishes."""

    def test_returns_the_attributes_the_api_reports(self, monkeypatch):
        """The attribute ids are mapped back to their keys and sorted."""
        _install_metadata(monkeypatch)
        assert D._get_commodity_attributes("0440000") == [
            "exports",
            "imports",
            "production",
        ]

    def test_a_non_200_falls_back_to_every_attribute(self, monkeypatch):
        """A refused metadata request does not narrow the attribute list."""
        monkeypatch.setattr(
            f"{HELPERS}.make_request", lambda url, **kw: _FakeApiResponse(503, [])
        )
        assert D._get_commodity_attributes("0440000") == list(ATTRIBUTES.keys())

    def test_unknown_attribute_ids_fall_back(self, monkeypatch):
        """Ids the mapping does not know leave nothing to narrow to."""
        _install_metadata(monkeypatch, attribute_ids=(999999,))
        assert D._get_commodity_attributes("0440000") == list(ATTRIBUTES.keys())

    def test_a_request_failure_falls_back_to_every_attribute(self, monkeypatch):
        """The metadata call is advisory, so a failure is not an error."""

        def _boom(url, **kwargs):
            raise RuntimeError("metadata down")

        monkeypatch.setattr(f"{HELPERS}.make_request", _boom)
        assert D._get_commodity_attributes("0440000") == list(ATTRIBUTES.keys())


class TestGetCommodityCountries:
    """Tests for resolving the countries a commodity publishes."""

    def test_maps_names_to_codes(self, monkeypatch):
        """Each reported country name resolves to its PSD code."""
        _install_metadata(monkeypatch)
        assert D._get_commodity_countries("0440000") == {
            "United States": "US",
            "Brazil": "BR",
            "China": "CH",
        }

    def test_the_world_row_and_nameless_rows_are_dropped(self, monkeypatch):
        """The world aggregate and unnamed entries are not countries."""
        _install_metadata(
            monkeypatch,
            countries=(("World", "00"), ("", "XX"), ("Brazil", "BR")),
        )
        assert D._get_commodity_countries("0440000") == {"Brazil": "BR"}

    def test_a_non_200_yields_no_countries(self, monkeypatch):
        """A refused metadata request narrows nothing."""
        monkeypatch.setattr(
            f"{HELPERS}.make_request", lambda url, **kw: _FakeApiResponse(503, [])
        )
        assert D._get_commodity_countries("0440000") == {}

    def test_a_request_failure_yields_no_countries(self, monkeypatch):
        """The metadata call is advisory, so a failure is not an error."""

        def _boom(url, **kwargs):
            raise RuntimeError("metadata down")

        monkeypatch.setattr(f"{HELPERS}.make_request", _boom)
        assert D._get_commodity_countries("0440000") == {}


class TestYearColumns:
    """Tests for picking the year columns out of a query result."""

    def test_selects_marketing_and_calendar_year_headers(self):
        """Both the slashed marketing year and the bare calendar year count."""
        columns = ["country", "unit Description", "2023/2024", "2024", "attribute"]
        assert D._year_columns(columns) == ["2023/2024", "2024"]


class TestGetTimeseries:
    """Tests for the commodity time series query."""

    def test_returns_long_rows_with_region_and_unit(self, monkeypatch):
        """Every year column becomes its own row, tagged with its region."""
        _install_metadata(monkeypatch)
        _install_query(monkeypatch)
        result = D.get_timeseries("corn")
        assert result[0] == {
            "region": "North America",
            "country": "United States",
            "commodity": "Corn",
            "attribute": "Production",
            "marketing_year": "2023/2024",
            "value": 389.0,
            "unit": "1000 MT",
        }
        assert [r["value"] for r in result] == [389.0, 122.0, 400.0, 130.0]

    def test_the_commodity_and_attribute_are_carried_forward(self, monkeypatch):
        """The source names the commodity once, on the section's first row."""
        _install_metadata(monkeypatch)
        _install_query(monkeypatch)
        result = D.get_timeseries("corn")
        assert {r["commodity"] for r in result} == {"Corn"}
        assert {r["attribute"] for r in result} == {"Production"}

    def test_every_attribute_and_country_is_requested_by_default(self, monkeypatch):
        """Without a selection the query asks for all the source publishes."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn")
        payload = session.payloads[0]
        assert payload["attributes"] == [88, 57, 28]
        assert set(payload["countries"]) == {"US", "BR", "CH"}
        assert payload["commodities"] == ["0440000"]

    def test_a_comma_separated_attribute_string_is_split(self, monkeypatch):
        """A single string of attributes is split and trimmed."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", attribute=" production , exports ")
        assert session.payloads[0]["attributes"] == [28, 88]

    def test_a_list_of_attributes_is_accepted(self, monkeypatch):
        """Attributes may be given as a list rather than a joined string."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", attribute=["imports", "production"])
        assert session.payloads[0]["attributes"] == [57, 28]

    def test_a_country_code_resolves_directly(self, monkeypatch):
        """A PSD country code is accepted in place of the country name."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", country="US")
        assert session.payloads[0]["countries"] == ["US"]

    def test_an_unknown_commodity_raises(self, monkeypatch):
        """A commodity the source does not publish is rejected."""
        _install_metadata(monkeypatch)
        with pytest.raises(ValueError, match="Unknown commodity: unobtanium"):
            D.get_timeseries("unobtanium")

    def test_an_unknown_attribute_raises(self, monkeypatch):
        """An attribute name the mapping does not know is rejected."""
        _install_metadata(monkeypatch)
        with pytest.raises(ValueError, match="Unknown attribute: 'flux'"):
            D.get_timeseries("corn", attribute="flux")

    def test_an_attribute_the_commodity_lacks_raises(self, monkeypatch):
        """A real attribute the commodity does not publish is rejected."""
        _install_metadata(monkeypatch, attribute_ids=(28,))
        with pytest.raises(
            ValueError, match="Attribute 'exports' is not available for corn"
        ):
            D.get_timeseries("corn", attribute="exports")

    def test_a_region_display_code_selects_that_region(self, monkeypatch):
        """A bare region code is passed through as the country selection."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", country="r01")
        assert session.payloads[0]["countries"] == ["R01"]

    def test_a_region_name_resolves_to_its_code(self, monkeypatch):
        """A region named in words resolves to its PSD region code."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", country="North America")
        assert session.payloads[0]["countries"] == ["R01"]

    def test_eu_resolves_to_the_european_union_region(self, monkeypatch):
        """The source publishes the EU as a region, not a country."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", country="EU")
        assert session.payloads[0]["countries"] == ["R05"]

    def test_a_country_name_resolves_to_its_code(self, monkeypatch):
        """A country named in words resolves to its PSD country code."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", country="Brazil")
        assert session.payloads[0]["countries"] == ["BR"]

    def test_a_country_code_the_commodity_lacks_raises(self, monkeypatch):
        """A country code outside the commodity's universe is rejected."""
        _install_metadata(monkeypatch, countries=(("Brazil", "BR"),))
        with pytest.raises(
            ValueError, match="Country 'US' is not available for corn"
        ) as excinfo:
            D.get_timeseries("corn", country="US")
        assert "['brazil']" in str(excinfo.value)

    def test_a_country_name_the_commodity_lacks_raises(self, monkeypatch):
        """A country name outside the commodity's universe is rejected."""
        _install_metadata(monkeypatch, countries=(("China", "CH"),))
        with pytest.raises(
            ValueError, match="Country 'Brazil' is not available for corn"
        ):
            D.get_timeseries("corn", country="Brazil")

    def test_an_unknown_country_raises(self, monkeypatch):
        """A name that is neither a country nor a region is rejected."""
        _install_metadata(monkeypatch)
        with pytest.raises(
            ValueError, match="Unknown country/region: 'Atlantis' for corn"
        ) as excinfo:
            D.get_timeseries("corn", country="Atlantis")
        assert "Valid regions: ['world'," in str(excinfo.value)

    def test_a_list_of_one_string_is_split(self, monkeypatch):
        """The Workspace posts a single-item list holding a joined string."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", country=["Brazil, China"])
        assert session.payloads[0]["countries"] == ["BR", "CH"]

    def test_aggregating_the_world_asks_for_every_region(self, monkeypatch):
        """Aggregating the world means every region, not the world total."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", country="world", aggregate_region=True)
        assert set(session.payloads[0]["countries"]) == set(REGIONS.values())

    def test_aggregating_a_region_adds_the_world(self, monkeypatch):
        """A region selection is aggregated against the world total."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", country="north_america", aggregate_region=True)
        assert set(session.payloads[0]["countries"]) == {"R00", "R01"}

    def test_aggregating_a_country_adds_its_region_and_the_world(self, monkeypatch):
        """A country selection is aggregated against its region and the world."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", country="Brazil", aggregate_region=True)
        assert set(session.payloads[0]["countries"]) == {"R00", "R04", "BR"}

    def test_aggregating_without_a_selection_adds_every_region(self, monkeypatch):
        """Without a selection every region is added to every country."""
        _install_metadata(
            monkeypatch, countries=(("Brazil", "BR"), ("EU-27", "E4"), ("World", "R00"))
        )
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", aggregate_region=True)
        assert set(session.payloads[0]["countries"]) == set(REGIONS.values()) | {"BR"}

    def test_a_refused_query_reports_no_data(self, monkeypatch):
        """A non-200 query yields no rows, which is reported as no data."""
        _install_metadata(monkeypatch)
        _install_query(monkeypatch, status=500)
        with pytest.raises(OpenBBError, match="No data available"):
            D.get_timeseries("corn")

    def test_an_unreadable_payload_reports_no_data(self, monkeypatch):
        """A body that is not the expected JSON yields no rows."""
        _install_metadata(monkeypatch)
        _install_query(monkeypatch, json_error=ValueError("not json"))
        with pytest.raises(OpenBBError, match="No data available"):
            D.get_timeseries("corn")

    def test_a_transport_failure_is_wrapped(self, monkeypatch):
        """A dropped connection during the query is raised, not swallowed."""
        _install_metadata(monkeypatch)
        _install_query(monkeypatch, post_error=ClientError("connection reset"))
        with pytest.raises(OpenBBError, match="connection reset"):
            D.get_timeseries("corn")

    def test_rows_without_observations_report_no_data(self, monkeypatch):
        """A result whose year cells are all empty carries no observations."""
        _install_metadata(monkeypatch)
        _install_query(
            monkeypatch,
            rows=[
                {
                    "commodity": "Corn",
                    "attribute": "Production",
                    "country": "Brazil",
                    "unit Description": "(1000 MT)",
                    "2023/2024": None,
                }
            ],
        )
        with pytest.raises(OpenBBError, match="No data available"):
            D.get_timeseries("corn")

    def test_a_nameless_country_row_is_dropped(self, monkeypatch):
        """The source pads its result with rows carrying no country."""
        _install_metadata(monkeypatch)
        _install_query(
            monkeypatch,
            rows=[
                {
                    "commodity": "Corn",
                    "attribute": "Production",
                    "country": "Brazil",
                    "unit Description": "(1000 MT)",
                    "2023/2024": 122.0,
                },
                {
                    "commodity": None,
                    "attribute": None,
                    "country": None,
                    "unit Description": "(1000 MT)",
                    "2023/2024": 9.0,
                },
            ],
        )
        result = D.get_timeseries("corn")
        assert [r["country"] for r in result] == ["Brazil"]

    def test_aggregates_are_reported_as_regions(self, monkeypatch):
        """A region row carries the region and a dashed country."""
        _install_metadata(monkeypatch)
        _install_query(
            monkeypatch,
            rows=[
                {
                    "commodity": "Corn",
                    "attribute": "Production",
                    "country": "World",
                    "unit Description": "(1000 MT)",
                    "2023/2024": 1200.0,
                },
                {
                    "commodity": None,
                    "attribute": None,
                    "country": "European Union",
                    "unit Description": "(1000 MT)",
                    "2023/2024": 60.0,
                },
                {
                    "commodity": None,
                    "attribute": None,
                    "country": "Other",
                    "unit Description": "(1000 MT)",
                    "2023/2024": 40.0,
                },
                {
                    "commodity": None,
                    "attribute": None,
                    "country": "Atlantis",
                    "unit Description": "(1000 MT)",
                    "2023/2024": 5.0,
                },
            ],
        )
        result = D.get_timeseries("corn")
        assert [(r["region"], r["country"], r["value"]) for r in result] == [
            ("World", "--", 1200.0),
            ("Other", "--", 40.0),
            ("Other", "Atlantis", 5.0),
            ("European Union", "European Union", 60.0),
        ]

    def test_aggregating_treats_the_eu_as_a_region(self, monkeypatch):
        """When aggregating, the EU is an aggregate rather than a country."""
        _install_metadata(monkeypatch)
        _install_query(
            monkeypatch,
            rows=[
                {
                    "commodity": "Corn",
                    "attribute": "Production",
                    "country": "European Union",
                    "unit Description": "(1000 MT)",
                    "2023/2024": 60.0,
                }
            ],
        )
        result = D.get_timeseries("corn", aggregate_region=True)
        assert [(r["region"], r["country"]) for r in result] == [
            ("European Union", "--")
        ]

    def test_the_year_range_bounds_the_rows(self, monkeypatch):
        """A start and end year trim the marketing years that are returned."""
        _install_metadata(monkeypatch)
        _install_query(monkeypatch)
        result = D.get_timeseries("corn", start_year=2024, end_year=2024)
        assert {r["marketing_year"] for r in result} == {"2024/2025"}

    def test_the_year_range_bounds_the_query(self, monkeypatch):
        """The requested marketing years are sent to the source."""
        _install_metadata(monkeypatch)
        session = _install_query(monkeypatch)
        D.get_timeseries("corn", start_year=2023, end_year=2024)
        assert session.payloads[0]["marketYears"] == [2023, 2024]
