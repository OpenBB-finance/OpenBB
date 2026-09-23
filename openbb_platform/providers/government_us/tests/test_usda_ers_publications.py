"""Tests for the USDA ERS publications utils and models."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.ers_publication_download import (
    ErsPublicationDownloadFetcher,
    ErsPublicationDownloadQueryParams,
)
from openbb_government_us.usda.models.ers_publications import (
    ErsPublicationsFetcher,
    ErsPublicationsQueryParams,
)
from openbb_government_us.usda.utils import ers_publications as P

PAGE_URL = "https://www.ers.usda.gov/publications/115092"

DOWNLOAD_HTML = """
<div id="download" class="padding-bottom-3 border-bottom scrollspy">
    <h2 class="font-heading-xl section-heading-gold">Download</h2>
    <ul class="usa-collection">
        <li class="usa-collection__item maxw-full custom-list-item">
            <div class="usa-collection__body">
                <h3 class="usa-collection__heading">Report Summary</h3>
                <a href="/media/7744/gfa-36-report-summary.pdf?v=50959">Download</a>
            </div>
        </li>
        <li class="usa-collection__item maxw-full custom-list-item">
            <div class="usa-collection__body">
                <h3 class="usa-collection__heading">Full Report</h3>
                <a href="/media/9155/gfa-36.pdf?v=76542">Download</a>
            </div>
        </li>
    </ul>
</div>
<div id="relatedContent"><ul class="usa-collection">
    <li class="usa-collection__item"><div class="usa-collection__body">
        <h3 class="usa-collection__heading">Full Report</h3>
        <a href="/media/1/decoy.pdf">Decoy</a>
    </div></li>
</ul></div>
"""


def _row(**overrides):
    """Build a listing row shaped like the live API's."""
    row = {
        "id": "115092",
        "title": "Livestock, Dairy, and Poultry Outlook: July 2026",
        "releaseDate": "2026-07-16",
        "baseUrl": "http://www.ers.usda.gov",
        "url": "/publications/115092",
        "pubType": "Outlook",
        "series": {
            "id": "233",
            "code": "LDPM",
            "name": "Livestock, Dairy, and Poultry Outlook",
            "fullName": "LDPM: Livestock, Dairy, and Poultry Outlook",
        },
        "reportNumber": "LDP-M-385",
        "authors": [{"id": "457", "name": "Russell Knight", "url": "/authors/rk"}],
        "description": "<p>Analysis.</p>",
        "shortDescription": "Analysis.",
        "newsroomImage": 0,
        "relatedTopics": [{"id": "121", "name": "Animal Products", "url": "/t/ap"}],
    }
    row.update(overrides)
    return row


class TestSeriesValidation:
    """Tests for series group expansion and validation."""

    def test_outlook_group_expands_to_its_thirteen_codes(self):
        """The default group expands to the codes the API actually accepts."""
        codes = P.resolve_series("outlook-reports")
        assert sorted(codes) == sorted(
            [
                "CWS",
                "FDS",
                "GFA",
                "FTS",
                "LDPM",
                "OCS",
                "AES",
                "RCS",
                "SSSM",
                "TBS",
                "OCE",
                "VGS",
                "WHS",
            ]
        )

    def test_every_group_member_is_a_known_code(self):
        """No group may name a code the code table does not describe."""
        for group, codes in P.SERIES_GROUPS.items():
            unknown = [code for code in codes if code not in P.SERIES_CODES]
            assert unknown == [], f"{group} names unknown codes {unknown}"

    def test_the_url_slug_is_never_passed_through_as_a_series_code(self):
        """The browser slug is not an API value.

        Sending series=outlook-reports returns zero rows, so the slug must be
        expanded to codes rather than forwarded.
        """
        codes = P.resolve_series("outlook-reports")
        assert "outlook-reports" not in codes
        for group in P.SERIES_GROUPS:
            assert group not in P.SERIES_CODES

    def test_an_unknown_series_raises_instead_of_reaching_the_api(self):
        """An unknown series silently returns the entire corpus, so it raises.

        The API ignores an unrecognized series filter and answers with all
        4844 rows, which would masquerade as a successful query.
        """
        with pytest.raises(OpenBBError, match="Invalid publication series: ZZZZ"):
            P.resolve_series("ZZZZ")

    def test_a_mixed_list_raises_on_the_bad_token(self):
        """The API drops only the bad token, so a mixed list must still raise."""
        with pytest.raises(OpenBBError, match="Invalid publication series: ZZZZ"):
            P.resolve_series("CWS,ZZZZ")

    def test_codes_and_groups_are_case_insensitive(self):
        """The API matches series codes case-insensitively."""
        assert P.resolve_series("ldpm") == ["LDPM"]
        assert P.resolve_series("Outlook-Reports") == P.resolve_series(
            "outlook-reports"
        )

    def test_a_list_is_accepted_and_deduplicated(self):
        """Overlapping selections resolve to each code once."""
        assert P.resolve_series(["LDPM", "CWS", "LDPM"]) == ["LDPM", "CWS"]

    def test_group_and_member_overlap_is_deduplicated(self):
        """Naming a group and one of its members does not double the code."""
        codes = P.resolve_series("outlook-reports,LDPM")
        assert codes.count("LDPM") == 1

    def test_whitespace_is_trimmed(self):
        """Padded tokens resolve."""
        assert P.resolve_series(" LDPM , CWS ") == ["LDPM", "CWS"]

    def test_an_empty_selection_raises(self):
        """An empty selection would otherwise fetch nothing silently."""
        with pytest.raises(OpenBBError, match="No publication series requested"):
            P.resolve_series(" , ")


class TestCoerceSentinel:
    """Tests for the int 0 sentinel rule."""

    def test_zero_becomes_none(self):
        """The API fills unset string and object fields with the int 0."""
        assert P.coerce_sentinel(0) is None

    def test_strings_and_dicts_pass_through(self):
        """A populated value is untouched."""
        assert P.coerce_sentinel("text") == "text"
        assert P.coerce_sentinel({"url": "/x"}) == {"url": "/x"}

    def test_none_passes_through(self):
        """A missing key stays None."""
        assert P.coerce_sentinel(None) is None

    def test_a_nonzero_int_passes_through(self):
        """Only the zero sentinel is coerced."""
        assert P.coerce_sentinel(37) == 37

    def test_false_is_not_a_sentinel(self):
        """False equals 0 but is a real boolean value."""
        assert P.coerce_sentinel(False) is False

    def test_empty_string_is_not_a_sentinel(self):
        """An empty string is a real, if blank, published value."""
        assert P.coerce_sentinel("") == ""


class TestNormalizeRow:
    """Tests for row normalization."""

    def test_zero_short_description_becomes_none(self):
        """18% of outlook rows carry the int 0 in shortDescription."""
        record = P.normalize_row(_row(shortDescription=0))
        assert record["short_description"] is None

    def test_zero_newsroom_image_never_subscripts(self):
        """97% of outlook rows carry the int 0 in newsroomImage."""
        record = P.normalize_row(_row(newsroomImage=0))
        assert record["image_url"] is None

    def test_a_populated_newsroom_image_yields_its_url(self):
        """The 3% that carry an object expose the image URL."""
        record = P.normalize_row(_row(newsroomImage={"url": "/media/1/i.jpg"}))
        assert record["image_url"] == "/media/1/i.jpg"

    def test_author_urls_are_coerced_per_element(self):
        """One row mixes authors with a string url and authors with the int 0.

        60% of author objects carry the sentinel, and the same row can hold
        both kinds, so coercion must run per element.
        """
        record = P.normalize_row(
            _row(
                authors=[
                    {"id": "1", "name": "With URL", "url": "/authors/with-url"},
                    {"id": "2", "name": "Without URL", "url": 0},
                ]
            )
        )
        assert record["authors"] == [
            {"id": "1", "name": "With URL", "url": "/authors/with-url"},
            {"id": "2", "name": "Without URL", "url": None},
        ]

    def test_amber_waves_shaped_row_coerces_every_sentinel(self):
        """Amber Waves rows carry the int 0 in series, pubType and more."""
        record = P.normalize_row(
            _row(
                series=0,
                pubType=0,
                reportNumber=0,
                description=0,
                shortDescription=0,
                authors=[],
                relatedTopics=[],
            )
        )
        assert record["series_code"] is None
        assert record["series_name"] is None
        assert record["series_full_name"] is None
        assert record["pub_type"] is None
        assert record["report_number"] is None
        assert record["description"] is None
        assert record["authors"] == []
        assert record["topics"] == []

    def test_populated_fields_survive(self):
        """A fully populated row keeps every published value."""
        record = P.normalize_row(_row())
        assert record["id"] == "115092"
        assert record["series_code"] == "LDPM"
        assert record["series_name"] == "Livestock, Dairy, and Poultry Outlook"
        assert record["report_number"] == "LDP-M-385"
        assert record["short_description"] == "Analysis."
        assert record["topics"] == ["Animal Products"]

    def test_missing_optional_keys_do_not_raise(self):
        """A row without the optional keys normalizes to None."""
        record = P.normalize_row(
            {"id": "1", "title": "T", "releaseDate": "2026-01-01", "url": "/p/1"}
        )
        assert record["series_code"] is None
        assert record["authors"] == []
        assert record["topics"] == []


class TestPublicationPageUrl:
    """Tests for the publication page URL."""

    def test_uses_https_not_the_rows_http_base_url(self):
        """The row's baseUrl is http and redirects, so it is not used."""
        assert P.publication_page_url(_row()) == PAGE_URL

    def test_ignores_a_foreign_base_url_on_the_row(self):
        """The origin is fixed, so a row cannot redirect the fetch."""
        row = _row(baseUrl="http://evil.example.com")
        assert P.publication_page_url(row) == PAGE_URL


class TestBuildListingUrl:
    """Tests for the listing request URL."""

    def test_requests_one_code_at_the_page_size_ceiling(self):
        """items_per_page is hard-clamped to 50, so 50 is requested."""
        url = P.build_listing_url("LDPM", 0)
        assert "series=LDPM" in url
        assert "items_per_page=50" in url
        assert "sort_by=releaseDate" in url
        assert "sort_order=DESC" in url
        assert "page=0" in url

    def test_pages_are_zero_based(self):
        """The API's page param is zero-based."""
        assert "page=3" in P.build_listing_url("LDPM", 3)


class TestFetchPublications:
    """Tests for the listing fetch."""

    @staticmethod
    def _patch(monkeypatch, corpus):
        """Serve a paginated fake of the API and record every request."""
        requested: list = []

        async def fake_request(url, **kwargs):
            from urllib.parse import parse_qs, urlparse

            params = parse_qs(urlparse(url).query)
            code = params["series"][0]
            page = int(params["page"][0])
            size = int(params["items_per_page"][0])
            requested.append((code, page))
            if "," in code:
                raise AssertionError(f"multi-code request issued -> {code}")
            rows = corpus.get(code, [])
            start = page * size
            return {
                "pager": {"total_items": len(rows)},
                "rows": rows[start : start + size],
            }

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_request
        )
        return requested

    @staticmethod
    def _corpus(code, count, start_id=0):
        """Build a series' rows, newest first."""
        return [
            _row(
                id=str(start_id + i),
                url=f"/publications/{start_id + i}",
                releaseDate=f"2026-01-{(i % 28) + 1:02d}",
                series={"id": "1", "code": code, "name": code, "fullName": code},
            )
            for i in range(count)
        ]

    def test_paginates_one_series_code_at_a_time(self, monkeypatch):
        """A multi-code query duplicates and drops rows across page bounds.

        Walking all 13 outlook codes in one query returns 1569 rows but only
        1558 unique ids, so each code is paginated on its own.
        """
        corpus = {
            "LDPM": self._corpus("LDPM", 120, 0),
            "CWS": self._corpus("CWS", 30, 500),
        }
        requested = self._patch(monkeypatch, corpus)
        rows = asyncio.run(P.fetch_publications(["LDPM", "CWS"], use_cache=False))
        assert sorted(requested) == [
            ("CWS", 0),
            ("LDPM", 0),
            ("LDPM", 1),
            ("LDPM", 2),
        ]
        assert len(rows) == 150
        assert len({row["id"] for row in rows}) == 150

    def test_walks_every_page_of_a_series(self, monkeypatch):
        """The pager reports only a total, so the page count is derived."""
        self._patch(monkeypatch, {"LDPM": self._corpus("LDPM", 220, 0)})
        rows = asyncio.run(P.fetch_publications("LDPM", use_cache=False))
        assert len(rows) == 220

    def test_an_exact_page_multiple_does_not_request_a_trailing_page(self, monkeypatch):
        """A total that is an exact multiple of 50 needs no extra request."""
        requested = self._patch(monkeypatch, {"LDPM": self._corpus("LDPM", 100, 0)})
        asyncio.run(P.fetch_publications("LDPM", use_cache=False))
        assert requested == [("LDPM", 0), ("LDPM", 1)]

    def test_duplicate_ids_are_collapsed(self, monkeypatch):
        """Rows are keyed by id, so a repeated row is returned once."""
        rows = self._corpus("LDPM", 3, 0)
        rows.append(rows[0])
        self._patch(monkeypatch, {"LDPM": rows})
        assert len(asyncio.run(P.fetch_publications("LDPM", use_cache=False))) == 3

    def test_an_empty_series_returns_nothing(self, monkeypatch):
        """A series with no rows requests one page and stops."""
        requested = self._patch(monkeypatch, {"LDPM": []})
        assert asyncio.run(P.fetch_publications("LDPM", use_cache=False)) == []
        assert requested == [("LDPM", 0)]

    def test_rows_are_normalized(self, monkeypatch):
        """Sentinels are coerced before the rows leave the client."""
        self._patch(
            monkeypatch,
            {"LDPM": [_row(id="1", url="/publications/1", shortDescription=0)]},
        )
        rows = asyncio.run(P.fetch_publications("LDPM", use_cache=False))
        assert rows[0]["short_description"] is None
        assert rows[0]["url"] == "https://www.ers.usda.gov/publications/1"

    def test_results_are_sorted_newest_first(self, monkeypatch):
        """The listing is ordered by release date, descending."""
        self._patch(
            monkeypatch,
            {
                "LDPM": [
                    _row(id="1", url="/publications/1", releaseDate="2024-01-01"),
                    _row(id="2", url="/publications/2", releaseDate="2026-01-01"),
                    _row(id="3", url="/publications/3", releaseDate="2025-01-01"),
                ]
            },
        )
        rows = asyncio.run(P.fetch_publications("LDPM", use_cache=False))
        assert [row["id"] for row in rows] == ["2", "3", "1"]

    def test_dates_filter_the_listing(self, monkeypatch):
        """The API ignores date params, so the client filters."""
        self._patch(
            monkeypatch,
            {
                "LDPM": [
                    _row(id="1", url="/publications/1", releaseDate="2024-01-01"),
                    _row(id="2", url="/publications/2", releaseDate="2026-01-01"),
                    _row(id="3", url="/publications/3", releaseDate="2025-01-01"),
                ]
            },
        )
        rows = asyncio.run(
            P.fetch_publications(
                "LDPM",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                use_cache=False,
            )
        )
        assert [row["id"] for row in rows] == ["3"]

    def test_an_unknown_series_never_reaches_the_network(self, monkeypatch):
        """Validation runs before any request is issued."""
        requested = self._patch(monkeypatch, {})
        with pytest.raises(OpenBBError, match="Invalid publication series"):
            asyncio.run(P.fetch_publications("ZZZZ", use_cache=False))
        assert requested == []

    def test_an_unexpected_response_raises(self, monkeypatch):
        """A response without rows is an error, not an empty listing."""

        async def fake_request(url, **kwargs):
            return "<html>error</html>"

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_request
        )
        with pytest.raises(OpenBBError, match="Unexpected ERS publications response"):
            asyncio.run(P.fetch_publications("LDPM", use_cache=False))

    def test_a_missing_pager_total_reads_the_first_page_only(self, monkeypatch):
        """A response without a pager still returns its rows."""

        async def fake_request(url, **kwargs):
            return {"rows": [_row(id="1", url="/publications/1")]}

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_request
        )
        rows = asyncio.run(P.fetch_publications("LDPM", use_cache=False))
        assert len(rows) == 1

    def test_the_listing_is_cached_and_reused(self, monkeypatch, tmp_path):
        """The listing is served from disk on the second call."""
        monkeypatch.setenv("OPENBB_USDA_CACHE_DIR", str(tmp_path / "cache"))
        requested = self._patch(monkeypatch, {"LDPM": self._corpus("LDPM", 3, 0)})
        first = asyncio.run(P.fetch_publications("LDPM"))
        second = asyncio.run(P.fetch_publications("LDPM"))
        assert requested == [("LDPM", 0)]
        assert [row["id"] for row in first] == [row["id"] for row in second]


class TestValidatePublicationUrl:
    """Tests for publication URL validation."""

    def test_a_publication_page_is_accepted(self):
        """The canonical page URL passes."""
        assert P.validate_publication_url(PAGE_URL) == PAGE_URL

    def test_whitespace_is_trimmed(self):
        """A padded URL passes and is normalized."""
        assert P.validate_publication_url(f"  {PAGE_URL} ") == PAGE_URL

    def test_a_foreign_host_raises(self):
        """Only the ERS host is fetched."""
        with pytest.raises(OpenBBError, match="Invalid ERS publication URL"):
            P.validate_publication_url("https://evil.example.com/publications/1")

    def test_another_path_on_the_ers_host_raises(self):
        """An ERS URL that is not a publication page is rejected."""
        with pytest.raises(OpenBBError, match="Invalid ERS publication URL"):
            P.validate_publication_url("https://www.ers.usda.gov/data-products/x")


class TestParseFullReportPath:
    """Tests for the download-block parser."""

    def test_selects_full_report_over_a_preceding_report_summary(self):
        """A Report Summary PDF can precede the Full Report.

        Taking the first PDF returns the summary, so the heading decides.
        """
        assert P.parse_full_report_path(DOWNLOAD_HTML) == "/media/9155/gfa-36.pdf"

    def test_ignores_non_pdf_companions_under_the_full_report_heading(self):
        """Spreadsheet companions are filtered on the extension."""
        html = """
        <div id="download"><ul class="usa-collection">
            <li class="usa-collection__item"><div class="usa-collection__body">
                <h3 class="usa-collection__heading">Full Report</h3>
                <a href="/media/10/tables.xlsx">x</a>
                <a href="/media/11/report.pdf">p</a>
            </div></li>
        </ul></div>
        """
        assert P.parse_full_report_path(html) == "/media/11/report.pdf"

    def test_ignores_other_headings(self):
        """Frontmatter and appendices are not the full report."""
        html = """
        <div id="download"><ul class="usa-collection">
            <li class="usa-collection__item"><div class="usa-collection__body">
                <h3 class="usa-collection__heading">Frontmatter</h3>
                <a href="/media/1/front.pdf">f</a>
            </div></li>
            <li class="usa-collection__item"><div class="usa-collection__body">
                <h3 class="usa-collection__heading">Appendices</h3>
                <a href="/media/2/appendix.pdf">a</a>
            </div></li>
            <li class="usa-collection__item"><div class="usa-collection__body">
                <h3 class="usa-collection__heading">Full Report</h3>
                <a href="/media/3/report.pdf">r</a>
            </div></li>
        </ul></div>
        """
        assert P.parse_full_report_path(html) == "/media/3/report.pdf"

    def test_only_the_download_block_is_searched(self):
        """A Full Report link elsewhere on the page is not the download."""
        assert P.parse_full_report_path(DOWNLOAD_HTML) != "/media/1/decoy.pdf"

    def test_the_heading_is_matched_case_insensitively(self):
        """The source's heading casing varies between reports."""
        html = """
        <div id="download"><ul class="usa-collection">
            <li class="usa-collection__item"><div class="usa-collection__body">
                <h3 class="usa-collection__heading">FULL REPORT</h3>
                <a href="/media/3/report.pdf">r</a>
            </div></li>
        </ul></div>
        """
        assert P.parse_full_report_path(html) == "/media/3/report.pdf"

    def test_a_page_without_a_download_block_returns_none(self):
        """Not every publication offers a download."""
        assert P.parse_full_report_path("<html><body>none</body></html>") is None

    def test_a_block_without_a_full_report_returns_none(self):
        """A download block may offer only companions."""
        html = """
        <div id="download"><ul class="usa-collection">
            <li class="usa-collection__item"><div class="usa-collection__body">
                <h3 class="usa-collection__heading">Report Summary</h3>
                <a href="/media/1/summary.pdf">s</a>
            </div></li>
        </ul></div>
        """
        assert P.parse_full_report_path(html) is None

    def test_a_full_report_without_a_pdf_returns_none(self):
        """A Full Report heading with no PDF link yields nothing."""
        html = """
        <div id="download"><ul class="usa-collection">
            <li class="usa-collection__item"><div class="usa-collection__body">
                <h3 class="usa-collection__heading">Full Report</h3>
                <a href="/media/1/report.xlsx">x</a>
            </div></li>
        </ul></div>
        """
        assert P.parse_full_report_path(html) is None

    def test_an_item_without_a_heading_is_skipped(self):
        """A malformed item does not break the scan."""
        html = """
        <div id="download"><ul class="usa-collection">
            <li class="usa-collection__item"><div class="usa-collection__body">
                <a href="/media/1/orphan.pdf">o</a>
            </div></li>
            <li class="usa-collection__item"><div class="usa-collection__body">
                <h3 class="usa-collection__heading">Full Report</h3>
                <a href="/media/2/report.pdf">r</a>
            </div></li>
        </ul></div>
        """
        assert P.parse_full_report_path(html) == "/media/2/report.pdf"


class TestResolveFullReport:
    """Tests for the page-to-PDF resolution."""

    @staticmethod
    def _patch(monkeypatch, html):
        """Serve fake page HTML and record every fetch."""
        requested: list = []

        async def fake_download(url):
            requested.append(url)
            return html.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client._download", fake_download
        )
        return requested

    def test_returns_the_full_report_url(self, monkeypatch):
        """The resolved URL is absolute and on the ERS host."""
        self._patch(monkeypatch, DOWNLOAD_HTML)
        url = asyncio.run(P.resolve_full_report(PAGE_URL, use_cache=False))
        assert url == "https://www.ers.usda.gov/media/9155/gfa-36.pdf"

    def test_fetches_the_publication_page(self, monkeypatch):
        """Resolution reads the page, which is the only source of the media id."""
        requested = self._patch(monkeypatch, DOWNLOAD_HTML)
        asyncio.run(P.resolve_full_report(PAGE_URL, use_cache=False))
        assert requested == [PAGE_URL]

    def test_a_foreign_url_never_reaches_the_network(self, monkeypatch):
        """The host is validated before the page is fetched."""
        requested = self._patch(monkeypatch, DOWNLOAD_HTML)
        with pytest.raises(OpenBBError, match="Invalid ERS publication URL"):
            asyncio.run(
                P.resolve_full_report(
                    "https://evil.example.com/publications/1", use_cache=False
                )
            )
        assert requested == []

    def test_a_page_without_a_full_report_returns_none(self, monkeypatch):
        """A page with no full report resolves to None."""
        self._patch(monkeypatch, "<html>none</html>")
        assert asyncio.run(P.resolve_full_report(PAGE_URL, use_cache=False)) is None

    def test_the_resolution_is_cached(self, monkeypatch, tmp_path):
        """The page is parsed once and reused."""
        monkeypatch.setenv("OPENBB_USDA_CACHE_DIR", str(tmp_path / "cache"))
        requested = self._patch(monkeypatch, DOWNLOAD_HTML)
        first = asyncio.run(P.resolve_full_report(PAGE_URL))
        second = asyncio.run(P.resolve_full_report(PAGE_URL))
        assert requested == [PAGE_URL]
        assert first == second == "https://www.ers.usda.gov/media/9155/gfa-36.pdf"

    def test_a_cached_absence_is_reused(self, monkeypatch, tmp_path):
        """A page with no full report is not re-parsed on every request."""
        monkeypatch.setenv("OPENBB_USDA_CACHE_DIR", str(tmp_path / "cache"))
        requested = self._patch(monkeypatch, "<html>none</html>")
        assert asyncio.run(P.resolve_full_report(PAGE_URL)) is None
        assert asyncio.run(P.resolve_full_report(PAGE_URL)) is None
        assert requested == [PAGE_URL]


class TestAfetchPublication:
    """Tests for the resolve-then-download fetch."""

    @staticmethod
    def _patch(monkeypatch, report_url, content=b"%PDF-1.7 report"):
        """Serve a fake resolution and file download."""
        requested: list = []

        async def fake_resolve(page_url, use_cache=True):
            return report_url

        async def fake_file(media_path, product=None, ttl=None):
            requested.append(media_path)
            if isinstance(content, Exception):
                raise content
            return content

        monkeypatch.setattr(P, "resolve_full_report", fake_resolve)
        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file", fake_file
        )
        return requested

    def test_returns_the_pdf_and_its_filename(self, monkeypatch):
        """The download yields the bytes and the media file name."""
        requested = self._patch(
            monkeypatch, "https://www.ers.usda.gov/media/9155/gfa-36.pdf"
        )
        content, filename = asyncio.run(P.afetch_publication(PAGE_URL))
        assert content == b"%PDF-1.7 report"
        assert filename == "gfa-36.pdf"
        assert requested == ["/media/9155/gfa-36.pdf"]

    def test_a_page_without_a_full_report_raises(self, monkeypatch):
        """A page with no full report is an error, not an empty download."""
        self._patch(monkeypatch, None)
        with pytest.raises(OpenBBError, match="No Full Report PDF is published"):
            asyncio.run(P.afetch_publication(PAGE_URL))

    def test_a_foreign_resolved_host_is_refused(self, monkeypatch):
        """A media URL off the ERS host is never downloaded."""
        requested = self._patch(monkeypatch, "https://evil.example.com/media/1/x.pdf")
        with pytest.raises(OpenBBError, match="Refusing to download"):
            asyncio.run(P.afetch_publication(PAGE_URL))
        assert requested == []

    def test_a_non_pdf_body_raises(self, monkeypatch):
        """A response that is not a PDF raises rather than returning junk."""
        self._patch(
            monkeypatch,
            "https://www.ers.usda.gov/media/9155/gfa-36.pdf",
            b"<html>error</html>",
        )
        with pytest.raises(OpenBBError, match="are not a PDF"):
            asyncio.run(P.afetch_publication(PAGE_URL))

    def test_an_invalid_page_url_raises(self, monkeypatch):
        """Validation runs inside the fetch as well."""

        async def fake_resolve(page_url, use_cache=True):
            raise OpenBBError(f"Invalid ERS publication URL -> {page_url}.")

        monkeypatch.setattr(P, "resolve_full_report", fake_resolve)
        with pytest.raises(OpenBBError, match="Invalid ERS publication URL"):
            asyncio.run(P.afetch_publication("https://evil.example.com/publications/1"))


class TestErsPublications:
    """Tests for the ErsPublications model."""

    def test_the_default_series_is_the_outlook_group(self):
        """The default selection expands to the outlook codes."""
        query = ErsPublicationsFetcher.transform_query({})
        assert sorted(query.series.split(",")) == sorted(
            P.SERIES_GROUPS["outlook-reports"]
        )

    def test_the_default_series_is_never_the_url_slug(self):
        """Forwarding the slug would return zero rows."""
        query = ErsPublicationsFetcher.transform_query({})
        assert "outlook-reports" not in query.series

    def test_an_unknown_series_is_rejected(self):
        """An unknown series would silently return the whole corpus."""
        with pytest.raises(OpenBBError, match="Invalid publication series"):
            ErsPublicationsFetcher.transform_query({"series": "ZZZZ"})

    def test_an_empty_series_falls_back_to_the_default(self):
        """An empty selection uses the default group."""
        query = ErsPublicationsFetcher.transform_query({"series": ""})
        assert sorted(query.series.split(",")) == sorted(
            P.SERIES_GROUPS["outlook-reports"]
        )

    def test_multiple_items_are_allowed_for_series(self):
        """The Workspace reads the multi-select contract off the schema."""
        extra = ErsPublicationsQueryParams.__json_schema_extra__["series"]
        assert extra["multiple_items_allowed"] is True
        assert "outlook-reports" in extra["choices"]
        assert "LDPM" in extra["choices"]

    @staticmethod
    def _fetch(params, rows, monkeypatch):
        """Run the fetcher against a fake listing."""

        async def fake_fetch(series, start_date=None, end_date=None):
            return rows

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_publications.fetch_publications",
            fake_fetch,
        )
        query = ErsPublicationsFetcher.transform_query(params)
        raw = asyncio.run(ErsPublicationsFetcher.aextract_data(query, None))
        return ErsPublicationsFetcher.transform_data(query, raw)

    def test_maps_a_row_to_the_output_record(self, monkeypatch):
        """The record carries the page URL the viewer downloads."""
        results = self._fetch(
            {"series": "LDPM"}, [P.normalize_row(_row())], monkeypatch
        )
        row = results[0]
        assert row.id == "115092"
        assert row.title == "Livestock, Dairy, and Poultry Outlook: July 2026"
        assert row.release_date == date(2026, 7, 16)
        assert row.series_code == "LDPM"
        assert row.report_number == "LDP-M-385"
        assert row.url == PAGE_URL
        assert row.authors == "Russell Knight"
        assert row.topics == "Animal Products"

    def test_the_url_is_the_publication_page_not_a_media_url(self, monkeypatch):
        """The download model does the two-hop resolve itself."""
        results = self._fetch(
            {"series": "LDPM"}, [P.normalize_row(_row())], monkeypatch
        )
        assert "/publications/" in results[0].url
        assert "/media/" not in results[0].url

    def test_sentinel_fields_are_omitted_from_the_record(self, monkeypatch):
        """An unpopulated field never renders as a dead column."""
        rows = [P.normalize_row(_row(shortDescription=0, reportNumber=0, authors=[]))]
        results = self._fetch({"series": "LDPM"}, rows, monkeypatch)
        dumped = results[0].model_dump()
        assert "short_description" not in dumped
        assert "report_number" not in dumped
        assert "authors" not in dumped
        assert dumped["id"] == "115092"

    def test_multiple_authors_are_joined(self, monkeypatch):
        """Authors render as one comma-separated cell."""
        rows = [
            P.normalize_row(
                _row(
                    authors=[
                        {"id": "1", "name": "A", "url": "/a"},
                        {"id": "2", "name": "B", "url": 0},
                    ]
                )
            )
        ]
        results = self._fetch({"series": "LDPM"}, rows, monkeypatch)
        assert results[0].authors == "A, B"

    def test_limit_caps_the_listing(self, monkeypatch):
        """The limit is applied newest first."""
        rows = [
            P.normalize_row(_row(id=str(i), url=f"/publications/{i}")) for i in range(5)
        ]
        results = self._fetch({"series": "LDPM", "limit": 2}, rows, monkeypatch)
        assert [row.id for row in results] == ["0", "1"]

    def test_no_limit_returns_every_row(self, monkeypatch):
        """A None limit returns the full listing."""
        rows = [
            P.normalize_row(_row(id=str(i), url=f"/publications/{i}")) for i in range(5)
        ]
        results = self._fetch({"series": "LDPM"}, rows, monkeypatch)
        assert len(results) == 5

    def test_dates_are_passed_to_the_client(self, monkeypatch):
        """The date window reaches the listing fetch."""
        captured: dict = {}

        async def fake_fetch(series, start_date=None, end_date=None):
            captured.update(series=series, start_date=start_date, end_date=end_date)
            return []

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_publications.fetch_publications",
            fake_fetch,
        )
        query = ErsPublicationsFetcher.transform_query(
            {"series": "LDPM", "start_date": "2026-01-01", "end_date": "2026-07-01"}
        )
        asyncio.run(ErsPublicationsFetcher.aextract_data(query, None))
        assert captured["series"] == "LDPM"
        assert captured["start_date"] == date(2026, 1, 1)
        assert captured["end_date"] == date(2026, 7, 1)


class TestErsPublicationDownload:
    """Tests for the ErsPublicationDownload model."""

    URL_A = "https://www.ers.usda.gov/publications/115092"
    URL_B = "https://www.ers.usda.gov/publications/113293"

    def test_urls_are_required(self):
        """A request without a file selection is rejected."""
        with pytest.raises(ValueError, match="urls"):
            ErsPublicationDownloadQueryParams()

    def test_multiple_items_are_allowed_for_urls(self):
        """The Workspace reads the multi-file contract off the schema."""
        assert ErsPublicationDownloadQueryParams.__json_schema_extra__["urls"] == {
            "multiple_items_allowed": True
        }

    @staticmethod
    def _patch(monkeypatch, result=(b"%PDF-1.7 report", "ldp-m-385.pdf")):
        """Serve a fake publication download and record every request."""
        requested: list = []

        async def fake_fetch(page_url):
            requested.append(page_url)
            if isinstance(result, Exception):
                raise result
            return result

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_publications.afetch_publication",
            fake_fetch,
        )
        return requested

    @staticmethod
    def _fetch(urls, monkeypatch, result=(b"%PDF-1.7 report", "ldp-m-385.pdf")):
        """Run the download fetcher."""
        requested = TestErsPublicationDownload._patch(monkeypatch, result)
        query = ErsPublicationDownloadFetcher.transform_query({"urls": urls})
        raw = asyncio.run(ErsPublicationDownloadFetcher.aextract_data(query, None))
        return requested, ErsPublicationDownloadFetcher.transform_data(query, raw)

    def test_urls_accepts_a_list(self, monkeypatch):
        """Each URL in a list is downloaded."""
        requested, results = self._fetch([self.URL_A, self.URL_B], monkeypatch)
        assert requested == [self.URL_A, self.URL_B]
        assert len(results) == 2

    def test_urls_accepts_a_comma_separated_string(self, monkeypatch):
        """A single string of URLs is split and whitespace is trimmed."""
        requested, results = self._fetch(f" {self.URL_A} , {self.URL_B} ", monkeypatch)
        assert requested == [self.URL_A, self.URL_B]
        assert len(results) == 2

    def test_urls_accepts_the_workspace_dict_form(self, monkeypatch):
        """The Workspace posts the file selection as a dict."""
        requested, results = self._fetch({"urls": [self.URL_A]}, monkeypatch)
        assert requested == [self.URL_A]
        assert len(results) == 1

    def test_encodes_the_pdf_with_its_filename(self, monkeypatch):
        """The PDF is base64 encoded and named after the resolved media file."""
        import base64

        _, results = self._fetch([self.URL_A], monkeypatch)
        row = results[0]
        assert base64.b64decode(row.content) == b"%PDF-1.7 report"
        assert row.error_type is None
        assert row.filename == "ldp-m-385.pdf"
        assert row.data_format == {
            "data_type": "pdf",
            "filename": "ldp-m-385.pdf",
        }

    def test_a_publication_page_url_is_accepted(self, monkeypatch):
        """The urls values are page URLs, resolved by the download model."""
        requested, results = self._fetch([self.URL_A], monkeypatch)
        assert requested == [self.URL_A]
        assert results[0].error_type is None

    def test_an_invalid_url_reports_without_downloading(self, monkeypatch):
        """A URL the source does not serve is reported, not fetched."""
        requested, results = self._fetch(
            ["https://evil.example.com/publications/1"], monkeypatch
        )
        assert requested == []
        assert results[0].error_type == "invalid_url"
        assert results[0].filename is None
        assert "Invalid ERS publication URL" in results[0].content

    def test_a_media_url_is_rejected(self, monkeypatch):
        """The endpoint takes page URLs, so a media URL is an invalid input."""
        requested, results = self._fetch(
            ["https://www.ers.usda.gov/media/9155/gfa-36.pdf"], monkeypatch
        )
        assert requested == []
        assert results[0].error_type == "invalid_url"

    def test_a_download_failure_reports_that_url_only(self, monkeypatch):
        """One failed report does not discard the reports that succeeded."""
        calls: list = []

        async def fake_fetch(page_url):
            calls.append(page_url)
            if page_url == self.URL_A:
                raise OpenBBError("No Full Report PDF is published")
            return b"%PDF-1.7 report", "gfa-36.pdf"

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_publications.afetch_publication",
            fake_fetch,
        )
        query = ErsPublicationDownloadFetcher.transform_query(
            {"urls": [self.URL_A, self.URL_B]}
        )
        raw = asyncio.run(ErsPublicationDownloadFetcher.aextract_data(query, None))
        results = ErsPublicationDownloadFetcher.transform_data(query, raw)
        assert calls == [self.URL_A, self.URL_B]
        assert results[0].error_type == "download_error"
        assert "No Full Report PDF is published" in results[0].content
        assert results[1].error_type is None
        assert results[1].filename == "gfa-36.pdf"
