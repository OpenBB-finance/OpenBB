"""Tests for the CDR bulk-download helpers."""

import io
import zipfile

from openbb_federal_reserve.utils import cdr

_PAGE = (
    '<input id="__VIEWSTATE" value="VS0" />'
    '<input id="__VIEWSTATEGENERATOR" value="GEN0" />'
)
_REFRESHED = (
    '<input id="__VIEWSTATE" value="VS1" />'
    '<input id="__VIEWSTATEGENERATOR" value="GEN1" />'
    '<select name="DatesDropDownList" id="DatesDropDownList">'
    '<option value="3/31/2024">03/31/2024</option>'
    '<option value="12/31/2023">12/31/2023</option>'
    "</select>"
)


class _FakeResponse:
    """Minimal stand-in for a curl_cffi response carrying text and bytes."""

    def __init__(self, text: str = "", content: bytes = b""):
        self.text = text
        self.content = content


class _FakeSession:
    """Records the ASP.NET postback flow and returns scripted responses."""

    def __init__(self, posts: list[_FakeResponse]):
        self._posts = list(posts)
        self.post_payloads: list[dict] = []

    def get(self, url, timeout=None):
        """Return the initial page that carries the view state."""
        return _FakeResponse(text=_PAGE)

    def post(self, url, data=None, timeout=None):
        """Record the posted form data and return the next scripted response."""
        self.post_payloads.append(data)
        return self._posts.pop(0)


class TestGetSession:
    """Tests for the shared impersonating session delegate."""

    def test_delegates_to_shared_session(self, monkeypatch):
        """``_get_session`` returns the shared ``cdr`` session and reuses it."""
        from openbb_federal_reserve.utils import curl_session

        sentinel = object()
        keys: list[str] = []
        monkeypatch.setattr(curl_session, "_sessions", {})
        monkeypatch.setattr(
            curl_session,
            "get_session",
            lambda key, warmup=None: keys.append(key) or sentinel,
        )
        monkeypatch.setattr(cdr, "get_session", curl_session.get_session)
        first = cdr._get_session()
        assert first is sentinel
        assert cdr._get_session() is sentinel
        assert keys == ["cdr", "cdr"]


class TestViewstate:
    """Tests for the view-state field extractor."""

    def test_extracts_present_and_missing_fields(self):
        """Present fields parse to their value; absent fields default to empty."""
        state = cdr._viewstate('<input id="__VIEWSTATE" value="ABC" />')
        assert state["__VIEWSTATE"] == "ABC"
        assert state["__VIEWSTATEGENERATOR"] == ""


class TestSelectProduct:
    """Tests for the product-selection postback."""

    def test_returns_refreshed_state_and_periods(self):
        """Selecting a product yields the refreshed view state and its periods."""
        session = _FakeSession([_FakeResponse(text=_REFRESHED)])
        state, periods = cdr._select_product(session, "ReportingSeriesSinglePeriod")
        assert state["__VIEWSTATE"] == "VS1"
        assert periods == [
            ("3/31/2024", "03/31/2024"),
            ("12/31/2023", "12/31/2023"),
        ]
        assert session.post_payloads[0][f"{cdr._PREFIX}ListBox1"] == (
            "ReportingSeriesSinglePeriod"
        )

    def test_no_dropdown_yields_empty_periods(self):
        """A refreshed page without the dates dropdown yields no periods."""
        session = _FakeSession([_FakeResponse(text=_PAGE)])
        _, periods = cdr._select_product(session, "ReportingSeriesSinglePeriod")
        assert periods == []


class TestListPeriods:
    """Tests for the public period listing."""

    def test_lists_period_records(self, monkeypatch):
        """``list_periods`` maps the dropdown options to date-id records."""
        session = _FakeSession([_FakeResponse(text=_REFRESHED)])
        monkeypatch.setattr(cdr, "_get_session", lambda: session)
        assert cdr.list_periods("call_single") == [
            {"date_id": "3/31/2024", "date": "03/31/2024"},
            {"date_id": "12/31/2023", "date": "12/31/2023"},
        ]

    def test_caches_periods_across_calls(self, monkeypatch):
        """A repeat ``list_periods`` call is served from disk, not re-posted."""
        calls = {"n": 0}

        def _counted(session, value, radio="TSVRadioButton"):
            """Count postback navigations and return a fixed period set."""
            calls["n"] += 1
            return {}, [("3/31/2024", "03/31/2024")]

        monkeypatch.setattr(cdr, "_select_product", _counted)
        monkeypatch.setattr(cdr, "_get_session", object)
        first = cdr.list_periods("call_single")
        second = cdr.list_periods("call_single")
        assert first == second == [{"date_id": "3/31/2024", "date": "03/31/2024"}]
        assert calls["n"] == 1


class TestFetchBulk:
    """Tests for the three-step bulk download flow."""

    def test_downloads_selected_period(self, monkeypatch):
        """The flow selects a period by label and posts the download."""
        session = _FakeSession(
            [_FakeResponse(text=_REFRESHED), _FakeResponse(content=b"PKzip")]
        )
        monkeypatch.setattr(cdr, "_get_session", lambda: session)
        content = cdr.fetch_bulk("call_single", "12/31/2023", fmt="tsv")
        assert content == b"PKzip"
        download = session.post_payloads[-1]
        assert download[f"{cdr._PREFIX}DatesDropDownList"] == "12/31/2023"
        assert download[f"{cdr._PREFIX}FormatType"] == "TSVRadioButton"
        assert download[f"{cdr._PREFIX}TabStrip1$Download_0"] == "Download"

    def test_defaults_to_latest_period(self, monkeypatch):
        """An unmatched period falls back to the first (latest) available."""
        session = _FakeSession(
            [_FakeResponse(text=_REFRESHED), _FakeResponse(content=b"PKlatest")]
        )
        monkeypatch.setattr(cdr, "_get_session", lambda: session)
        cdr.fetch_bulk("call_single", "01/01/1900", fmt="xbrl")
        assert session.post_payloads[-1][f"{cdr._PREFIX}DatesDropDownList"] == (
            "3/31/2024"
        )

    def test_no_periods_returns_empty(self, monkeypatch):
        """A product with no reporting periods returns empty bytes."""
        session = _FakeSession([_FakeResponse(text=_PAGE)])
        monkeypatch.setattr(cdr, "_get_session", lambda: session)
        assert cdr.fetch_bulk("call_single") == b""


class TestFetchTaxonomy:
    """Tests for the taxonomy download flow."""

    def test_ubpr_taxonomy_no_form_chooser(self, monkeypatch):
        """A product without a form type posts the taxonomy and returns it."""
        session = _FakeSession(
            [_FakeResponse(text=_REFRESHED), _FakeResponse(content=b"UBPRTAX")]
        )
        monkeypatch.setattr(cdr, "_get_session", lambda: session)
        assert cdr.fetch_taxonomy("ubpr_ratio_single") == b"UBPRTAX"
        download = session.post_payloads[-1]
        assert download[f"{cdr._PREFIX}TabStrip1$Download_Taxonomy_1"] == (
            "Download Taxonomy"
        )

    def test_call_taxonomy_posts_form_chooser(self, monkeypatch):
        """A Call Report form type triggers the extra form-chooser postback."""
        session = _FakeSession(
            [
                _FakeResponse(text=_REFRESHED),
                _FakeResponse(text=_PAGE, content=b"PANEL"),
                _FakeResponse(content=b"CALL051TAX"),
            ]
        )
        monkeypatch.setattr(cdr, "_get_session", lambda: session)
        assert cdr.fetch_taxonomy("call_single", "051") == b"CALL051TAX"
        pick = session.post_payloads[-1]
        assert pick["__EVENTTARGET"] == (f"{cdr._PREFIX}FormTypeControl1$LinkButton051")

    def test_taxonomy_no_periods(self, monkeypatch):
        """A refreshed page with no periods downloads with an empty date id."""
        session = _FakeSession(
            [_FakeResponse(text=_PAGE), _FakeResponse(content=b"TAX")]
        )
        monkeypatch.setattr(cdr, "_get_session", lambda: session)
        assert cdr.fetch_taxonomy("ubpr_ratio_single") == b"TAX"
        assert session.post_payloads[-1][f"{cdr._PREFIX}DatesDropDownList"] == ""


def _por_zip(header: str, *data_rows: str) -> bytes:
    """Build a bulk ZIP carrying a single tab-delimited POR roster member."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "FFIEC CDR Call Bulk POR 03312024.txt",
            "\n".join([header, *data_rows]) + "\n",
        )
    return buffer.getvalue()


class TestPorName:
    """Tests for the POR-roster name lookup."""

    def test_missing_name_column_returns_none(self):
        """A roster without the name column resolves to ``None``."""
        content = _por_zip('"IDRSSD"\t"Other"', '"37"\t"x"')
        assert cdr._por_name(zipfile.ZipFile(io.BytesIO(content)), "37") is None


class TestResolveFdicCert:
    """Tests for the FDIC-certificate to RSSD resolver."""

    def test_resolves_cert_to_rssd(self):
        """A certificate present in the roster resolves to its RSSD."""
        content = _por_zip(
            '"IDRSSD"\tFDIC Certificate Number\tName', '"37"\t10057\tBANK'
        )
        assert cdr.resolve_fdic_cert(content, "10057") == "37"

    def test_no_por_member_returns_none(self):
        """A ZIP without a POR roster resolves to ``None``."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("other.txt", "x")
        assert cdr.resolve_fdic_cert(buffer.getvalue(), "10057") is None

    def test_missing_cert_column_returns_none(self):
        """A roster lacking the FDIC certificate column resolves to ``None``."""
        content = _por_zip('"IDRSSD"\tName', '"37"\tBANK')
        assert cdr.resolve_fdic_cert(content, "10057") is None

    def test_unknown_cert_returns_none(self):
        """A certificate absent from the roster resolves to ``None``."""
        content = _por_zip(
            '"IDRSSD"\tFDIC Certificate Number\tName', '"37"\t10057\tBANK'
        )
        assert cdr.resolve_fdic_cert(content, "99999") is None


class TestTotalAssetsByRssd:
    """Tests for ``total_assets_by_rssd``."""

    def test_reads_latest_total_assets(self, monkeypatch):
        """Total assets come from RCFD2170/RCON2170 at the most recent period."""
        monkeypatch.setattr(cdr, "fetch_bulk", lambda *a, **k: b"PKzip")
        instances = {
            "1": {
                "items": [
                    {"mdrm": "RCFD2170", "value": "1000", "period": "2024-03-31"},
                    # prior-period comparison fact, must be ignored
                    {"mdrm": "RCFD2170", "value": "900", "period": "2023-12-31"},
                ]
            },
            "2": {
                "items": [{"mdrm": "RCON2170", "value": "50", "period": "2024-03-31"}]
            },
            # no total-assets concept present
            "3": {
                "items": [{"mdrm": "RCFD2200", "value": "999", "period": "2024-03-31"}]
            },
        }
        monkeypatch.setattr(
            cdr, "parse_xbrl_instance", lambda content, rssd: instances[str(rssd)]
        )
        assets = cdr.total_assets_by_rssd("03/31/2024", ["1", "2", "3"])
        assert assets == {"1": 1000.0, "2": 50.0, "3": 0.0}

    def test_ignores_non_numeric_values(self, monkeypatch):
        """A non-numeric total-assets fact resolves to ``0.0``."""
        monkeypatch.setattr(cdr, "fetch_bulk", lambda *a, **k: b"PKzip")
        monkeypatch.setattr(
            cdr,
            "parse_xbrl_instance",
            lambda content, rssd: {
                "items": [{"mdrm": "RCFD2170", "value": "n/a", "period": "2024-03-31"}]
            },
        )
        assert cdr.total_assets_by_rssd(None, ["9"]) == {"9": 0.0}
