"""Tests for the FFIEC NIC client."""

import io
import zipfile

import pytest

from openbb_federal_reserve.utils import ffiec


def _zip_bytes(name: str, payload: str) -> bytes:
    """Build an in-memory single-member ZIP archive."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(name, payload)
    return buffer.getvalue()


_BHCF = "RSSD9001^RSSD9999^BHCK2170^RSSD9007\n1039502^20250331^4357856000^20230101\n^20250331^0^\n"
_ATTRS = "#ID_RSSD,NM_LGL,CITY\n1039502,JPMORGAN CHASE & CO.,NEW YORK\n"
_RELS = "#ID_RSSD_PARENT,ID_RSSD_OFFSPRING,RELN_LVL\n1039502,852218,1\n"


class _FakeResponse:
    """Minimal stand-in for a curl_cffi response."""

    def __init__(self, status_code: int, content: bytes):
        self.status_code = status_code
        self.content = content

    def raise_for_status(self):
        """Raise for non-2xx responses."""
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _FakeSession:
    """A fake session whose data fetch 403s once, then succeeds."""

    def __init__(self, payloads):
        self._payloads = list(payloads)
        self.warmups = 0

    def get(self, url, headers=None, timeout=None):
        """Return the warmup page, then queued payloads in order."""
        if url.endswith("/npw/"):
            self.warmups += 1
            return _FakeResponse(200, b"<html></html>")
        return self._payloads.pop(0)


class TestReadSingleZipMember:
    """Tests for ``_read_single_zip_member``."""

    def test_extracts_member_bytes(self):
        """The sole archive member is returned as bytes."""
        content = _zip_bytes("X.txt", "hello")
        assert ffiec._read_single_zip_member(content) == b"hello"


class TestSession:
    """Tests for session warm-up and the 403 retry."""

    def test_get_session_warms_up_once(self, monkeypatch):
        """``_get_session`` builds and warms a curl_cffi session once."""
        ffiec.reset_session()
        session = _FakeSession([])
        monkeypatch.setattr("curl_cffi.requests.Session", lambda **_k: session)
        first = ffiec._get_session()
        assert ffiec._get_session() is first
        assert session.warmups == 1
        ffiec.reset_session()

    def test_fetch_bytes_retries_once_on_403(self, monkeypatch):
        """A 403 triggers one session reset and retry."""
        session = _FakeSession([_FakeResponse(403, b""), _FakeResponse(200, b"ok")])
        resets: list[int] = []
        monkeypatch.setattr(ffiec, "_get_session", lambda: session)
        monkeypatch.setattr(ffiec, "reset_session", lambda: resets.append(1))
        assert ffiec._fetch_bytes("FinancialReport/X") == b"ok"
        assert resets == [1]


class TestFetchBhcf:
    """Tests for ``fetch_bhcf``."""

    def test_parses_caret_records(self, monkeypatch):
        """The caret-delimited BHCF file parses to RSSD-keyed records."""
        monkeypatch.setattr(
            ffiec, "_fetch_bytes", lambda *a, **k: _zip_bytes("BHCF.txt", _BHCF)
        )
        rows = ffiec.fetch_bhcf(2025, 1)
        assert len(rows) == 1
        assert rows[0]["RSSD9001"] == "1039502"
        assert rows[0]["BHCK2170"] == "4357856000"

    def test_invalid_quarter_raises(self):
        """An out-of-range quarter raises ``ValueError``."""
        with pytest.raises(ValueError, match="quarter must be"):
            ffiec.fetch_bhcf(2025, 5)


class TestFetchInstitutions:
    """Tests for ``fetch_institutions``."""

    def test_parses_attributes_csv(self, monkeypatch):
        """The attributes CSV parses to institution records."""
        monkeypatch.setattr(
            ffiec,
            "_fetch_bytes",
            lambda *a, **k: _zip_bytes("CSV_ATTRIBUTES_ACTIVE.CSV", _ATTRS),
        )
        rows = ffiec.fetch_institutions("active")
        assert rows[0]["#ID_RSSD"] == "1039502"

    def test_invalid_status_raises(self):
        """An unknown status raises ``ValueError``."""
        with pytest.raises(ValueError, match="status must be"):
            ffiec.fetch_institutions("bogus")


class TestFetchRelationships:
    """Tests for ``fetch_relationships``."""

    def test_parses_relationships_csv(self, monkeypatch):
        """The relationships CSV parses to records."""
        monkeypatch.setattr(
            ffiec, "_fetch_bytes", lambda *a, **k: _zip_bytes("CSV_REL.CSV", _RELS)
        )
        rows = ffiec.fetch_relationships()
        assert rows[0]["ID_RSSD_OFFSPRING"] == "852218"


class TestAvailableBhcfYears:
    """Tests for ``available_bhcf_years``."""

    def test_parses_years_descending(self, monkeypatch):
        """Years are parsed from the page options, newest first."""
        html = b"<select><option>-- Select --</option><option>2024</option><option>2025</option></select>"
        monkeypatch.setattr(ffiec, "_fetch_bytes", lambda *a, **k: html)
        assert ffiec.available_bhcf_years() == [2025, 2024]


class TestFetchTransformations:
    """Tests for ``fetch_transformations``."""

    def test_parses_transformations_csv(self, monkeypatch):
        """The transformations CSV parses to merger records."""
        payload = "#ID_RSSD_PREDECESSOR,ID_RSSD_SUCCESSOR,TRNSFM_CD\n1,2,1\n"
        monkeypatch.setattr(
            ffiec,
            "_fetch_bytes",
            lambda *a, **k: _zip_bytes("CSV_TRANSFORMATIONS.CSV", payload),
        )
        rows = ffiec.fetch_transformations()
        assert rows[0]["ID_RSSD_SUCCESSOR"] == "2"


class TestFetchTopHolders:
    """Tests for ``fetch_top_holders``."""

    def test_parses_json(self, monkeypatch):
        """The top-holders JSON parses to a list of records."""
        monkeypatch.setattr(
            ffiec,
            "_fetch_bytes",
            lambda *a, **k: b'[{"Rank":1,"Name":"JPM","RssdId":1039502}]',
        )
        rows = ffiec.fetch_top_holders()
        assert rows[0]["RssdId"] == 1039502


class TestResolveBhcprHolder:
    """Tests for ``resolve_bhcpr_holder`` and ``_top_tier_holder``."""

    @staticmethod
    def _run_producer(monkeypatch):
        """Make ``cached`` execute its producer directly, bypassing the disk cache."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )

    def test_top_tier_holder_reads_hierarchy_rssd(self, monkeypatch):
        """The NIC BuildTier hierarchy's top-tier RSSD is returned as a string."""
        self._run_producer(monkeypatch)

        class _Resp:
            """A stand-in BuildTier response carrying the top-tier RSSD."""

            @staticmethod
            def json():
                """Return the hierarchy payload."""
                return {"top_tier_id_rssd": 1039502}

        class _Sess:
            """A session whose POST returns the hierarchy response."""

            @staticmethod
            def post(url, data=None, headers=None, timeout=None):
                """Return the fixed BuildTier response."""
                return _Resp()

        monkeypatch.setattr(ffiec, "_get_session", _Sess)
        assert ffiec._top_tier_holder("852218") == "1039502"

    def test_top_tier_holder_none_when_absent(self, monkeypatch):
        """A zero or missing top-tier RSSD resolves to ``None``."""
        self._run_producer(monkeypatch)

        class _Resp:
            """A BuildTier response with no resolvable top holder."""

            @staticmethod
            def json():
                """Return a payload whose top-tier RSSD is zero."""
                return {"top_tier_id_rssd": 0}

        class _Sess:
            """A session returning the empty-hierarchy response."""

            @staticmethod
            def post(url, data=None, headers=None, timeout=None):
                """Return the empty-hierarchy response."""
                return _Resp()

        monkeypatch.setattr(ffiec, "_get_session", _Sess)
        assert ffiec._top_tier_holder("852218") is None

    def test_top_tier_holder_none_on_error(self, monkeypatch):
        """A network or parse error resolves to ``None`` rather than raising."""
        self._run_producer(monkeypatch)

        class _Sess:
            """A session whose POST fails."""

            @staticmethod
            def post(url, data=None, headers=None, timeout=None):
                """Raise to simulate an unavailable hierarchy service."""
                raise RuntimeError("hierarchy down")

        monkeypatch.setattr(ffiec, "_get_session", _Sess)
        assert ffiec._top_tier_holder("852218") is None

    def test_filer_returned_unchanged(self, monkeypatch):
        """A firm that already files the BHCPR is used directly, not resolved."""
        monkeypatch.setattr(
            ffiec,
            "fetch_institution_financial_reports",
            lambda rssd: {"BHCPR": {"periods": []}},
        )
        assert ffiec.resolve_bhcpr_holder("1039502") == "1039502"

    def test_non_filer_resolves_to_top_tier_holder(self, monkeypatch):
        """A bank that files no BHCPR resolves to its top-tier holder."""
        monkeypatch.setattr(
            ffiec,
            "fetch_institution_financial_reports",
            lambda rssd: {"FFIEC101": {}},
        )
        monkeypatch.setattr(ffiec, "_top_tier_holder", lambda rssd: "1039502")
        assert ffiec.resolve_bhcpr_holder("852218") == "1039502"

    def test_blank_rssd_returns_blank(self):
        """A blank RSSD resolves to itself without a lookup."""
        assert ffiec.resolve_bhcpr_holder("  ") == ""

    def test_profile_failure_falls_through_to_hierarchy(self, monkeypatch):
        """A profile-fetch failure still resolves via the hierarchy."""

        def _boom(rssd):
            """Raise to simulate an unavailable NIC profile."""
            raise RuntimeError("profile down")

        monkeypatch.setattr(ffiec, "fetch_institution_financial_reports", _boom)
        monkeypatch.setattr(ffiec, "_top_tier_holder", lambda rssd: "1039502")
        assert ffiec.resolve_bhcpr_holder("852218") == "1039502"

    def test_unresolvable_holder_keeps_original(self, monkeypatch):
        """When the hierarchy cannot resolve, the original RSSD is kept."""
        monkeypatch.setattr(
            ffiec, "fetch_institution_financial_reports", lambda rssd: {}
        )
        monkeypatch.setattr(ffiec, "_top_tier_holder", lambda rssd: None)
        assert ffiec.resolve_bhcpr_holder("852218") == "852218"


class TestFetchDictionary:
    """Tests for ``fetch_dictionary``."""

    def test_builds_code_to_description_map(self, monkeypatch):
        """Both worksheets contribute MDRM code to description entries."""
        from openpyxl import Workbook

        workbook = Workbook()
        financial = workbook.active
        financial.title = "Financial"
        financial.append(["MDRM Item", "Start Date", "End Date", "Short Description"])
        financial.append(["BHCK2170", None, None, "TOTAL ASSETS"])
        structure = workbook.create_sheet("Structure")
        structure.append(["MDRM Item", "Item Name"])
        structure.append(["RSSD9001", "ID RSSD"])
        structure.append([None, "skip"])
        buffer = io.BytesIO()
        workbook.save(buffer)

        monkeypatch.setattr(ffiec, "_fetch_bytes", lambda *a, **k: buffer.getvalue())
        dictionary = ffiec.fetch_dictionary()
        assert dictionary["BHCK2170"] == "TOTAL ASSETS"
        assert dictionary["RSSD9001"] == "ID RSSD"


class TestEntityType:
    """Tests for the NIC entity-type resolver."""

    def test_resolves_from_directory(self, monkeypatch):
        """A listed institution resolves to its NIC entity type."""
        monkeypatch.setattr(
            ffiec,
            "fetch_institutions",
            lambda status="active": [
                {"#ID_RSSD": "1039502", "ENTITY_TYPE": "FHD"},
                {"#ID_RSSD": "37", "ENTITY_TYPE": ""},
                {"ENTITY_TYPE": "skip"},
            ],
        )
        assert ffiec.entity_type("1039502") == "FHD"

    def test_blank_and_unknown_resolve_none(self, monkeypatch):
        """A blank entity type or an unlisted RSSD resolves to ``None``."""
        monkeypatch.setattr(
            ffiec,
            "fetch_institutions",
            lambda status="active": [{"#ID_RSSD": "37", "ENTITY_TYPE": ""}],
        )
        assert ffiec.entity_type("37") is None
        assert ffiec.entity_type("99999") is None

    def test_directory_failure_returns_none(self, monkeypatch):
        """A failed directory lookup is swallowed and resolves to ``None``."""

        def _boom(status="active"):
            """Raise as if the NIC directory were unavailable."""
            raise RuntimeError("directory unavailable")

        monkeypatch.setattr(ffiec, "fetch_institutions", _boom)
        assert ffiec.entity_type("1039502") is None


class TestRssdNames:
    """Tests for the RSSD-to-name index."""

    def test_merges_active_and_closed_prefers_short_name(self, monkeypatch):
        """The index merges active + closed directories, preferring the short name."""
        directories = {
            "active": [
                {
                    "#ID_RSSD": "1039502",
                    "NM_SHORT": "JPMORGAN CHASE",
                    "NM_LGL": "JPMORGAN CHASE & CO",
                },
                {"#ID_RSSD": "37", "NM_SHORT": "", "NM_LGL": ""},
            ],
            "closed": [{"#ID_RSSD": "111", "NM_SHORT": "", "NM_LGL": "OLD BANK NA"}],
        }
        monkeypatch.setattr(
            ffiec, "fetch_institutions", lambda status="active": directories[status]
        )
        index = ffiec.rssd_names()
        assert index["1039502"] == "JPMORGAN CHASE"
        assert index["111"] == "OLD BANK NA"
        assert "37" not in index

    def test_directory_failure_returns_empty(self, monkeypatch):
        """A failed directory lookup yields an empty index, not an error."""

        def _boom(status="active"):
            """Raise as if the NIC directory were unavailable."""
            raise RuntimeError("directory unavailable")

        monkeypatch.setattr(ffiec, "fetch_institutions", _boom)
        assert ffiec.rssd_names() == {}

    def test_cache_failure_returns_empty(self, monkeypatch):
        """A failure in the cache layer is swallowed and yields an empty index."""
        from openbb_federal_reserve.utils import cache

        def _boom(*args, **kwargs):
            """Raise as if the disk cache were unavailable."""
            raise RuntimeError("cache unavailable")

        monkeypatch.setattr(cache, "cached", _boom)
        assert ffiec.rssd_names() == {}


class TestFry15:
    """Tests for the FR Y-15 snapshot listing and download."""

    _INDEX = (
        b'<a href="/npw/StaticData/Y15SnapShot/20241231_20250722_FRY15 Snapshot All.csv">x</a>'
        b'<a href="/npw/StaticData/Y15SnapShot/20231231_20240724_FRY15 Snapshot All.csv">y</a>'
    )

    def test_snapshots_parsed_newest_first(self, monkeypatch):
        """Snapshot periods parse from the index, newest first."""
        monkeypatch.setattr(ffiec, "_fetch_bytes", lambda *a, **k: self._INDEX)
        snapshots = ffiec.fetch_fry15_snapshots()
        assert [s["report_date"] for s in snapshots] == ["20241231", "20231231"]

    def test_fetch_defaults_to_latest(self, monkeypatch):
        """``fetch_fry15`` downloads the latest snapshot's CSV by default."""

        def _fetch(path, referer=None):
            if path.endswith("FRY15Reports"):
                return self._INDEX
            return b"ID_RSSD,Name,RISK2170\n1039502,JPM,100\n"

        monkeypatch.setattr(ffiec, "_fetch_bytes", _fetch)
        rows = ffiec.fetch_fry15()
        assert rows[0]["ID_RSSD"] == "1039502"

    def test_fetch_specific_period(self, monkeypatch):
        """A requested report date selects that snapshot."""

        def _fetch(path, referer=None):
            if path.endswith("FRY15Reports"):
                return self._INDEX
            return b"ID_RSSD,RISK2170\n9,5\n"

        monkeypatch.setattr(ffiec, "_fetch_bytes", _fetch)
        assert ffiec.fetch_fry15("20231231")[0]["ID_RSSD"] == "9"

    def test_fetch_empty_when_no_snapshots(self, monkeypatch):
        """No snapshots yields an empty list."""
        monkeypatch.setattr(ffiec, "_fetch_bytes", lambda *a, **k: b"<html></html>")
        assert ffiec.fetch_fry15() == []


class TestListBhcprReports:
    """Tests for ``list_bhcpr_reports`` and the BHCPR download helper."""

    def test_parses_both_naming_conventions(self, monkeypatch):
        """Legacy and current BHCPR PDF names parse to structured records."""
        html = (
            b'<a href="/npw/StaticData/bhcpRRPT/REPORTS/BHCPR_PEER/Dec2002/'
            b'PeerGroup_1_Dec2002.pdf">x</a>'
            b'<a href="/npw/StaticData/bhcpRRPT/REPORTS/BHCPR_PEER/20240630/'
            b'BHCPR_PeerGrp5_20240630.pdf">y</a>'
        )
        monkeypatch.setattr(ffiec, "_cached_bytes", lambda *a, **k: html)
        reports = {
            (r["peer_group"], r["year"], r["quarter"]): r
            for r in ffiec.list_bhcpr_reports()
        }
        legacy = reports[(1, 2002, 4)]
        assert legacy["name"] == "PeerGroup_1_Dec2002.pdf"
        assert legacy["period_end"] == "2002-12-31"
        assert legacy["url"].startswith("https://www.ffiec.gov/npw/StaticData")
        current = reports[(5, 2024, 2)]
        assert current["name"] == "BHCPR_PeerGrp5_20240630.pdf"
        assert current["period_end"] == "2024-06-30"

    def test_skips_unparseable_names(self, monkeypatch):
        """Filenames matching neither convention are dropped."""
        html = b'<a href="/npw/StaticData/bhcpRRPT/REPORTS/junk.pdf">x</a>'
        monkeypatch.setattr(ffiec, "_cached_bytes", lambda *a, **k: html)
        assert ffiec.list_bhcpr_reports() == []

    def test_skips_unmapped_period(self, monkeypatch):
        """Names whose month or month-end maps to no quarter are dropped."""
        html = (
            b'<a href="/npw/StaticData/bhcpRRPT/REPORTS/PeerGroup_1_Foo2010.pdf">x</a>'
            b'<a href="/npw/StaticData/bhcpRRPT/REPORTS/BHCPR_PeerGrp1_20100115.pdf">y</a>'
        )
        monkeypatch.setattr(ffiec, "_cached_bytes", lambda *a, **k: html)
        assert ffiec.list_bhcpr_reports() == []

    def test_download_validates_and_strips_prefix(self, monkeypatch):
        """``download_bhcpr_pdf`` fetches a valid PDF URL via the warmed session."""
        seen: dict[str, str] = {}

        def _fetch(path, referer=None):
            """Record the requested path and return PDF bytes."""
            seen["path"] = path
            return b"%PDF"

        monkeypatch.setattr(ffiec, "_fetch_bytes", _fetch)
        out = ffiec.download_bhcpr_pdf(
            "https://www.ffiec.gov/npw/StaticData/bhcpRRPT/x/PeerGroup_1.pdf"
        )
        assert out == b"%PDF"
        assert seen["path"] == "StaticData/bhcpRRPT/x/PeerGroup_1.pdf"

    def test_download_rejects_invalid_url(self):
        """Non-FFIEC hosts and non-PDF paths are rejected."""
        from openbb_core.provider.utils.errors import OpenBBError

        with pytest.raises(OpenBBError):
            ffiec.download_bhcpr_pdf("https://evil.com/npw/StaticData/bhcpRRPT/x.pdf")
        with pytest.raises(OpenBBError):
            ffiec.download_bhcpr_pdf(
                "https://www.ffiec.gov/npw/StaticData/bhcpRRPT/x.txt"
            )


class TestDownloadFinancialReportPdf:
    """Tests for ``download_financial_report_pdf``."""

    _URL = (
        "https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportPDF"
        "?rpt=FRY9C&id=1039502&dt=20250331"
    )

    def test_fetches_path_with_query(self, monkeypatch):
        """A valid URL fetches the bare path carrying the report query string."""
        seen: dict[str, str] = {}

        def _fetch(path, referer=None):
            """Record the requested path and return PDF bytes."""
            seen["path"] = path
            return b"%PDF"

        monkeypatch.setattr(ffiec, "_fetch_bytes", _fetch)
        out = ffiec.download_financial_report_pdf(self._URL)
        assert out == b"%PDF"
        assert seen["path"] == (
            "FinancialReport/ReturnFinancialReportPDF?rpt=FRY9C&id=1039502&dt=20250331"
        )

    def test_fetches_path_without_query(self, monkeypatch):
        """A valid URL with no query string fetches the bare path alone."""
        seen: dict[str, str] = {}

        def _fetch(path, referer=None):
            """Record the requested path and return PDF bytes."""
            seen["path"] = path
            return b"%PDF"

        monkeypatch.setattr(ffiec, "_fetch_bytes", _fetch)
        ffiec.download_financial_report_pdf(
            "https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportPDF"
        )
        assert seen["path"] == "FinancialReport/ReturnFinancialReportPDF"

    def test_rejects_invalid_url(self):
        """Non-FFIEC hosts and other paths are rejected."""
        from openbb_core.provider.utils.errors import OpenBBError

        with pytest.raises(OpenBBError):
            ffiec.download_financial_report_pdf(
                "https://evil.com/npw/FinancialReport/ReturnFinancialReportPDF"
            )
        with pytest.raises(OpenBBError):
            ffiec.download_financial_report_pdf(
                "https://www.ffiec.gov/npw/StaticData/bhcpRRPT/x.pdf"
            )


_REPORT_CSV = (
    "ItemName,Description,Value\n"
    "Institution Name,,JPMORGAN CHASE & CO.\n"
    "Street Address,,383 MADISON AVENUE\n"
    'Report Date,,"June 30, 2025"\n'
    "Report Date,Reporting date in numeric format,20250630\n"
    "ID_RSSD,Reporting entity identifier,1039502\n"
    "BHCK2170,TOTAL ASSETS,4357856000\n"
    "BHCK3210,TOTAL EQUITY,345000000\n"
    "notacode,Should be ignored,1\n"
)


# The collapsible toggle the profile renders per report series; its text is the
# report's official NIC name carrying the parenthetical code, mapped to the code.
_PROFILE_TITLES = {
    "FFIEC101": "Regulatory Capital Reporting for Institutions Subject to the"
    " Advanced Capital Adequacy Framework (FFIEC 101)",
    "FFIEC102": "Market Risk Regulatory Report for Institutions Subject to the"
    " Market Risk Capital Rule (FFIEC 102)",
    "FRY9C": "Consolidated Financial Statements for BHCs (FR Y-9C)",
}


def _profile_button(code: str) -> str:
    """Build one collapsible toggle button carrying a series' official name."""
    title = _PROFILE_TITLES.get(code, f"Report {code} ({code})")
    return (
        f'<button class="btn" data-toggle="collapse" href="#{code}"'
        f' aria-expanded="false">\n        {title}\n'
        '        <span class="glyphicon"></span>\n    </button>'
    )


def _profile_block(count: int, code: str, cards: str) -> str:
    """Build one report-series section: its title toggle and guarded option block."""
    return (
        _profile_button(code)
        + f" <script>if({count}>0){{ var dateCards = {cards}; var idRssd=852218;"
        f" buildOptionCards(dateCards,'{code}',idRssd); }}"
        f" else {{ $('#row_{code}').empty(); }}</script>"
    )


# A bank profile: FFIEC101/FFIEC102 are filed (``if(21>0)``) with two periods;
# FRY9C — a holding-company report — is zero-guarded (``if(0>0)``) and omitted.
# FFIEC102's older card carries an unmapped ``monthDay`` that is skipped.
_BANK_PROFILE = (
    "<html>"
    + _profile_block(
        21,
        "FFIEC101",
        '[{"year":"2026","dateOptions":[{"monthDay":"3/31","pdfAvailable":true}],'
        '"ShowDateCard":true}]',
    )
    + _profile_block(
        21,
        "FFIEC102",
        '[{"year":"2026","dateOptions":[{"monthDay":"3/31","pdfAvailable":true},'
        '{"monthDay":"13/01","pdfAvailable":false}],"ShowDateCard":true},'
        '{"year":"2025","dateOptions":[{"monthDay":"12/31","pdfAvailable":false}],'
        '"ShowDateCard":true}]',
    )
    + _profile_block(
        0,
        "FRY9C",
        '[{"year":"2025","dateOptions":[{"monthDay":"12/31","pdfAvailable":true}],'
        '"ShowDateCard":true}]',
    )
    + "</html>"
)


class TestParseProfileReportNames:
    """Tests for ``_parse_profile_report_names``."""

    def test_maps_official_name_by_parenthetical_code(self):
        """The parenthetical code (spaces/hyphens stripped) keys the official name."""
        names = ffiec._parse_profile_report_names(_BANK_PROFILE)
        assert names["FRY9C"] == "Consolidated Financial Statements for BHCs (FR Y-9C)"
        assert names["FFIEC101"] == (
            "Regulatory Capital Reporting for Institutions Subject to the"
            " Advanced Capital Adequacy Framework (FFIEC 101)"
        )

    def test_ignores_buttons_without_parenthetical(self):
        """A toggle whose text carries no parenthetical code yields no entry."""
        html = '<button href="#X">Plain Title</button>'
        assert ffiec._parse_profile_report_names(html) == {}

    def test_keeps_first_occurrence_per_code(self):
        """A repeated code keeps the first official name parsed."""
        html = (
            '<button href="#FRY9C">First Name (FR Y-9C)</button>'
            '<button href="#FRY9C">Second Name (FR Y-9C)</button>'
        )
        assert ffiec._parse_profile_report_names(html) == {
            "FRY9C": "First Name (FR Y-9C)"
        }


class TestFetchInstitutionFinancialReports:
    """Tests for ``fetch_institution_financial_reports``."""

    def test_parses_only_filed_reports_with_names_and_periods(self, monkeypatch):
        """Filed series parse to names and newest-first periods; zero-guarded drop."""
        captured: dict = {}

        def _fetch(path, referer=None):
            """Capture the profile path and return the bank profile HTML."""
            captured["path"] = path
            return _BANK_PROFILE.encode("utf-8")

        monkeypatch.setattr(ffiec, "_fetch_bytes", _fetch)
        reports = ffiec.fetch_institution_financial_reports(" 852218 ")
        assert "Institution/Profile/852218" in captured["path"]
        # The zero-guarded holding-company report is omitted entirely.
        assert "FRY9C" not in reports
        assert set(reports) == {"FFIEC101", "FFIEC102"}
        # Each filed series carries its official NIC name.
        assert reports["FFIEC102"]["name"] == (
            "Market Risk Regulatory Report for Institutions Subject to the"
            " Market Risk Capital Rule (FFIEC 102)"
        )
        # Periods are newest-first; the unmapped "13/01" monthDay is skipped.
        assert reports["FFIEC102"]["periods"] == [
            {"year": 2026, "quarter": 1, "month_day": "3/31", "pdf_available": True},
            {"year": 2025, "quarter": 4, "month_day": "12/31", "pdf_available": False},
        ]
        assert reports["FFIEC101"]["periods"] == [
            {"year": 2026, "quarter": 1, "month_day": "3/31", "pdf_available": True},
        ]

    def test_name_is_none_when_profile_lacks_title(self, monkeypatch):
        """A filed series with no matching toggle title carries a ``None`` name."""
        html = (
            "<html><script>if(3>0){ var dateCards ="
            ' [{"year":"2026","dateOptions":[{"monthDay":"3/31",'
            '"pdfAvailable":true}],"ShowDateCard":true}]; var idRssd=852218;'
            " buildOptionCards(dateCards,'FFIEC101',idRssd); }</script></html>"
        )
        monkeypatch.setattr(ffiec, "_fetch_bytes", lambda *a, **k: html.encode("utf-8"))
        reports = ffiec.fetch_institution_financial_reports("852218")
        assert reports["FFIEC101"]["name"] is None

    def test_series_with_only_unmapped_periods_is_dropped(self, monkeypatch):
        """A filed series whose every period is unmapped yields no entry."""
        html = (
            "<html>"
            + _profile_block(
                3,
                "FFIEC101",
                '[{"year":"2026","dateOptions":[{"monthDay":"13/01",'
                '"pdfAvailable":true}],"ShowDateCard":true}]',
            )
            + "</html>"
        )
        monkeypatch.setattr(ffiec, "_fetch_bytes", lambda *a, **k: html.encode("utf-8"))
        assert ffiec.fetch_institution_financial_reports("852218") == {}


class TestNormalizeReportDate:
    """Tests for ``_normalize_report_date``."""

    def test_numeric_form_passes_through(self):
        """An eight-digit value is returned unchanged."""
        assert ffiec._normalize_report_date("20250630") == "20250630"

    def test_descriptive_form_is_parsed(self):
        """A "Month DD, YYYY" value is normalized to YYYYMMDD."""
        assert ffiec._normalize_report_date("March 31, 2025") == "20250331"

    def test_unparseable_returns_none(self):
        """A value matching neither form returns ``None``."""
        assert ffiec._normalize_report_date("") is None
        assert ffiec._normalize_report_date("Q2") is None


class TestParseFinancialReportCsv:
    """Tests for ``_parse_financial_report_csv``."""

    def test_parses_identity_and_facts(self):
        """The CSV yields institution identity and an MDRM fact map."""
        parsed = ffiec._parse_financial_report_csv(_REPORT_CSV)
        assert parsed["institution_name"] == "JPMORGAN CHASE & CO."
        assert parsed["report_date"] == "20250630"
        assert parsed["rssd_id"] == "1039502"
        assert parsed["facts"] == {
            "BHCK2170": "4357856000",
            "BHCK3210": "345000000",
        }

    def test_prefers_descriptive_date_when_no_numeric(self):
        """With only a descriptive date row, the date is still normalized."""
        text = (
            "ItemName,Description,Value\n"
            "Institution Name,,X\n"
            'Report Date,,"March 31, 2025"\n'
            "ID_RSSD,,1\n"
            "RISK2170,TOTAL ASSETS,5\n"
        )
        assert ffiec._parse_financial_report_csv(text)["report_date"] == "20250331"

    def test_missing_header_yields_empty(self):
        """An HTML error page (no header row) yields an empty result."""
        parsed = ffiec._parse_financial_report_csv("<!DOCTYPE html><html></html>")
        assert parsed["facts"] == {}
        assert parsed["institution_name"] is None
        assert parsed["rssd_id"] is None

    def test_short_rows_are_skipped(self):
        """A row with fewer than three columns is skipped."""
        text = "ItemName,Description,Value\nBHCK2170,x,7\nbad\n"
        assert ffiec._parse_financial_report_csv(text)["facts"] == {"BHCK2170": "7"}


class TestFetchFinancialReport:
    """Tests for ``fetch_financial_report``."""

    def test_fetches_and_parses_per_institution_csv(self, monkeypatch):
        """The endpoint payload is fetched, parsed, and cached daily."""
        captured: dict = {}

        def _fetch(path, referer=None):
            """Capture the request path and return the report CSV."""
            captured["path"] = path
            return _REPORT_CSV.encode("utf-8")

        monkeypatch.setattr(ffiec, "_fetch_bytes", _fetch)
        report = ffiec.fetch_financial_report("fry9c", " 1039502 ", "20250630")
        assert "rpt=FRY9C" in captured["path"]
        assert "id=1039502" in captured["path"]
        assert "dt=20250630" in captured["path"]
        assert report["institution_name"] == "JPMORGAN CHASE & CO."
        assert report["facts"]["BHCK2170"] == "4357856000"

    def test_unfiled_period_returns_empty_facts(self, monkeypatch):
        """A period the institution did not file returns an empty fact map."""
        monkeypatch.setattr(ffiec, "_fetch_bytes", lambda *a, **k: b"<!DOCTYPE html>")
        report = ffiec.fetch_financial_report("FRY9C", "1039502", "20200101")
        assert report["facts"] == {}


class TestFetchBhcpr:
    """Tests for ``fetch_bhcpr``."""

    def test_fetches_csv_and_parses_coded_values(self, monkeypatch):
        """The BHCPR CSV is fetched, parsed into coded values, and cached daily."""
        captured: dict = {}

        def _fetch(path, referer=None):
            """Capture the request path and return placeholder CSV bytes."""
            captured["path"] = path
            return (
                "﻿MDRM,Description,Value\r\n"
                "Institution Name,,JPMORGAN CHASE & CO.\r\n"
                "DT,Current,20250331\r\n"
                "BHCK2170,TOTAL ASSETS (BHC CONSOLIDATED),4900475\r\n"
            ).encode()

        monkeypatch.setattr(ffiec, "_fetch_bytes", _fetch)
        data = ffiec.fetch_bhcpr(" 1039502 ", "20250331")
        assert "ReturnFinancialReportCSV" in captured["path"]
        assert "rpt=BHCPR" in captured["path"]
        assert "id=1039502" in captured["path"]
        assert "dt=20250331" in captured["path"]
        assert data["identity"]["institution_name"] == "JPMORGAN CHASE & CO."
        assert data["periods"][""] == "20250331"
        assert data["values"]["BHCK2170"][""] == 4900475
