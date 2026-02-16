"""SEC Management & Discussion Model."""

# pylint: disable=unused-argument, too-many-locals, too-many-branches
# flake8: noqa: PLR0912, PLR0914


from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.management_discussion_analysis import (
    ManagementDiscussionAnalysisData,
    ManagementDiscussionAnalysisQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class SecManagementDiscussionAnalysisQueryParams(
    ManagementDiscussionAnalysisQueryParams
):
    """SEC Management & Discussion Query."""

    include_tables: bool = Field(
        default=True,
        description="Return tables formatted as markdown in the text. Default is True.",
    )
    use_cache: bool = Field(
        default=True,
        description="When True, the file will be cached for use later. Default is True.",
    )
    raw_html: bool = Field(
        default=False,
        description="When True, the raw HTML content of the entire filing will be returned. Default is False."
        + " Use this option to parse the document manually.",
    )


class SecManagementDiscussionAnalysisData(ManagementDiscussionAnalysisData):
    """SEC Management & Discussion Data."""

    url: str = Field(
        description="The URL of the filing from which the data was extracted."
    )


class SecManagementDiscussionAnalysisFetcher(
    Fetcher[
        SecManagementDiscussionAnalysisQueryParams, SecManagementDiscussionAnalysisData
    ]
):
    """SEC Management & Discussion Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SecManagementDiscussionAnalysisQueryParams:
        """Transform the query."""
        return SecManagementDiscussionAnalysisQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecManagementDiscussionAnalysisQueryParams,
        credentials: dict[str, Any] | None,
        **kwargs: Any,
    ) -> dict:  # type: ignore[override]
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        import re

        from aiohttp_client_cache import SQLiteBackend
        from aiohttp_client_cache.session import CachedSession
        from openbb_core.app.utils import get_user_cache_directory
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_sec.models.company_filings import SecCompanyFilingsFetcher
        from openbb_sec.utils.helpers import SEC_HEADERS, sec_callback
        from pandas import offsets, to_datetime

        # Get the company filings to find the URL.

        if (
            query.symbol == "BLK" and query.calendar_year and query.calendar_year < 2025
        ) or query.symbol.isnumeric():
            filings = await SecCompanyFilingsFetcher.fetch_data(
                {
                    "cik": "0001364742" if query.symbol == "BLK" else query.symbol,
                    "form_type": "10-K,10-Q",
                    "use_cache": query.use_cache,
                },
                {},
            )

        else:
            filings = await SecCompanyFilingsFetcher.fetch_data(
                {
                    "symbol": query.symbol,
                    "form_type": "10-K,10-Q",
                    "use_cache": query.use_cache,
                },
                {},
            )

        if not filings:
            raise OpenBBError(
                f"Could not find any 10-K or 10-Q filings for the symbol. -> {query.symbol}"
            )

        # If no calendar year or period is provided, get the most recent filing.

        target_filing: Any = None
        calendar_year: Any = None
        calendar_period: Any = None

        if query.calendar_year is None and query.calendar_period is None:
            target_filing = (
                filings[0]  # type: ignore
                if not query.calendar_year and not query.calendar_period
                else None
            )

        if not target_filing:
            if query.calendar_period and not query.calendar_year:
                calendar_year = to_datetime("today").year
                calendar_period = to_datetime("today").quarter
            elif query.calendar_year and query.calendar_period:
                calendar_year = query.calendar_year
                calendar_period = int(query.calendar_period[1])
            elif query.calendar_year:
                calendar_year = query.calendar_year
                calendar_period = 1

            if query.calendar_year and not query.calendar_period:
                target_filing = [
                    f
                    for f in filings
                    if f.report_type == "10-K"  # type: ignore
                    and f.filing_date.year == query.calendar_year  # type: ignore
                ]
                if not target_filing:
                    target_filing = [
                        f for f in filings if f.filing_date.year == query.calendar_year  # type: ignore
                    ]
                if target_filing:
                    target_filing = target_filing[0]

            elif calendar_year and calendar_period:
                start = to_datetime(f"{calendar_year}Q{calendar_period}")
                start_date = (
                    start - offsets.QuarterBegin(1) + offsets.MonthBegin(1)
                ).date()
                end_date = (
                    start_date + offsets.QuarterEnd(0) - offsets.MonthEnd(0)
                ).date()

                for filing in filings:
                    if start_date < filing.filing_date < end_date:  # type: ignore
                        target_filing = filing
                        break

        if not target_filing:
            raise OpenBBError(
                f"Could not find a filing for the symbol -> {query.symbol}"
            )

        url = target_filing.report_url
        response = ""

        if query.use_cache is True:
            cache_dir = f"{get_user_cache_directory()}/http/sec_financials"
            async with CachedSession(cache=SQLiteBackend(cache_dir)) as session:
                try:
                    await session.delete_expired_responses()
                    response = await amake_request(
                        url,
                        headers=SEC_HEADERS,
                        response_callback=sec_callback,
                        session=session,
                    )  # type: ignore
                finally:
                    await session.close()
        else:
            response = await amake_request(url, headers=SEC_HEADERS, response_callback=sec_callback)  # type: ignore

        # Some 10-K filings have a stub Item 7 that simply
        # cross-references the Annual Report to Stockholders filed as
        # Exhibit 13.  When we detect this pattern we pre-fetch the
        # exhibit so that transform_data can extract MD&A from it.
        exhibit_content: str | None = None
        exhibit_url: str | None = None

        if isinstance(response, str) and re.search(
            r"incorporated\s+herein\s+by\s+reference", response, re.IGNORECASE
        ):
            _base_dir = url.rsplit("/", 1)[0]

            # Strategy 1: look for an inline exhibit link in the HTML
            # (modern filings embed <a href="...">Annual Report to
            # Security Holders</a>).
            _ar_re = re.compile(
                r'<a\b[^>]*href="([^"]+)"[^>]*>[^<]*'
                r"Annual\s+Report\s+to\s+(?:Security|Stock|Share)\s*[Hh]olders"
                r"[^<]*</a>",
                re.IGNORECASE,
            )
            _m = _ar_re.search(response)

            # Strategy 2: fall back to the filing index page and look for
            # the EX-13 exhibit document (older filings).
            if not _m:
                _index_url = target_filing.filing_detail_url
                try:
                    if query.use_cache is True:
                        cache_dir = f"{get_user_cache_directory()}/http/sec_financials"
                        async with CachedSession(
                            cache=SQLiteBackend(cache_dir)
                        ) as session:
                            try:
                                _index_html = await amake_request(
                                    _index_url,
                                    headers=SEC_HEADERS,
                                    response_callback=sec_callback,
                                    session=session,
                                )
                            finally:
                                await session.close()
                    else:
                        _index_html = await amake_request(
                            _index_url,
                            headers=SEC_HEADERS,
                            response_callback=sec_callback,
                        )
                    if isinstance(_index_html, str):
                        # Look for a link whose row has EX-13 type or
                        # whose filename contains "ex-13" / "ex13".
                        _ex13_re = re.compile(
                            r'<a\b[^>]*href="([^"]+ex[\-_]?13[^"]*\.htm[l]?)"',
                            re.IGNORECASE,
                        )
                        _em = _ex13_re.search(_index_html)
                        if _em:
                            _href = _em.group(1)
                            # Index page links are usually absolute paths
                            if _href.startswith("http"):
                                _m_url = _href
                            elif _href.startswith("/"):
                                _m_url = "https://www.sec.gov" + _href
                            else:
                                _m_url = _base_dir + "/" + _href

                            # Wrap in a fake match-like object
                            class _FakeMatch:
                                def group(self, n):
                                    return _m_url if n == 1 else ""

                            _m = _FakeMatch()  # type: ignore
                except Exception:  # noqa  # pylint: disable=broad-except
                    pass  # Index page unavailable; proceed without exhibit

            if _m:
                _href = _m.group(1)
                _exhibit_url: str = (
                    _href if _href.startswith("http") else _base_dir + "/" + _href
                )
                exhibit_url = _exhibit_url
                if query.use_cache is True:
                    cache_dir = f"{get_user_cache_directory()}/http/sec_financials"
                    async with CachedSession(cache=SQLiteBackend(cache_dir)) as session:
                        try:
                            exhibit_content = await amake_request(
                                _exhibit_url,
                                headers=SEC_HEADERS,
                                response_callback=sec_callback,
                                session=session,
                            )  # type: ignore
                        finally:
                            await session.close()
                else:
                    exhibit_content = await amake_request(  # type: ignore
                        _exhibit_url,
                        headers=SEC_HEADERS,
                        response_callback=sec_callback,
                    )

        if isinstance(response, str):
            result: dict[str, Any] = {
                "symbol": query.symbol,
                "calendar_year": (
                    calendar_year if calendar_year else target_filing.report_date.year
                ),
                "calendar_period": (
                    calendar_period
                    if calendar_period
                    else to_datetime(target_filing.report_date).quarter
                ),
                "period_ending": target_filing.report_date,
                "report_type": target_filing.report_type,
                "url": url,
                "content": response,
            }
            if exhibit_content and exhibit_url:
                result["exhibit_content"] = exhibit_content
                result["exhibit_url"] = exhibit_url
            return result

        raise OpenBBError(
            f"Unexpected response received. Expected string and got -> {response.__class__.__name__}"
            f" -> {response[:100]}"
        )

    @staticmethod
    def transform_data(
        query: SecManagementDiscussionAnalysisQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> SecManagementDiscussionAnalysisData:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        import re

        from openbb_sec.utils.html2markdown import html_to_markdown

        if query.raw_html is True:
            return SecManagementDiscussionAnalysisData(**data)

        filing_html = data.get("content", "")
        base_url = data.get("url", "")
        is_quarterly = data.get("report_type", "").endswith("Q")

        # Convert the full HTML filing to markdown.
        markdown = html_to_markdown(
            filing_html,
            base_url=base_url,
            keep_tables=query.include_tables,
        )

        if not markdown:
            raise EmptyDataError(
                "No content was found in the filing after HTML-to-Markdown conversion."
                f" -> {data.get('url', '')}"
                " -> The content can be analyzed by setting"
                " `raw_html=True` in the query."
            )

        # Strip leftover HTML anchor tags that the converter may leave
        # (e.g. <a id="item_2_management"></a>).  These interfere with
        # line-start-anchored regex matching.
        markdown = re.sub(r"<a\s[^>]*>\s*</a>", "", markdown)
        lines = markdown.splitlines()
        # Matches an Item 7 / Item 2 header for MD&A (the formal SEC item).
        item_header_re = re.compile(
            r"^(?:#{1,4}\s*)?(?:\*{1,2})?\s*"
            r"(?:Part\s+(?:I{1,2}|1|2)[\.\s,\-\u2013\u2014]*\s*)?"
            r"(?:ITEM|Item)\s*(?:7|2)"
            r"[\.\s\-\u2013\u2014:]*"
            r"(?:Management.s|MANAGEMENT.S)\s+Discussion",
            re.IGNORECASE,
        )
        # When we see a bare Item header we check the next non-blank line for the
        # MD&A title.
        bare_item_re = re.compile(
            r"^(?:#{1,4}\s*)?(?:\*{1,2})?\s*"
            r"(?:Part\s+(?:I{1,2}|1|2)[\.\s,\-\u2013\u2014]*\s*)?"
            r"(?:ITEM|Item)\s*(?:7|2)"
            r"\s*[\.\-\u2013\u2014:]*\s*$",
            re.IGNORECASE,
        )
        mda_title_re = re.compile(
            r"^(?:#{1,4}\s*)?(?:\*{1,2})?\s*"
            r"(?:Management.s|MANAGEMENT.S)\s+Discussion",
            re.IGNORECASE,
        )

        standalone_mda_re = re.compile(
            r"^(?:#{1,4}\s*)?\*{0,2}\s*"
            r"(?:Management.s|MANAGEMENT.S)\s+Discussion\s+and\s+Analysis",
            re.IGNORECASE,
        )

        # Any Item header (to detect section boundaries).
        any_item_re = re.compile(
            r"^(?:#{1,4}\s*)?\*{0,2}\s*" + r"(?:ITEM|Item)\s*\d",
            re.IGNORECASE,
        )

        # End-of-section patterns.
        end_patterns_quarterly = [
            re.compile(
                r"^(?:#{1,4}\s*)?\*{0,2}\s*"
                r"(?:ITEM|Item)\s*(?:3|4)"
                r"[.\s\-\u2013\u2014:]",
                re.IGNORECASE,
            ),
            re.compile(
                r"^(?:#{1,4}\s*)?\*{0,2}\s*SIGNATURES",
                re.IGNORECASE,
            ),
        ]

        end_patterns_annual = [
            re.compile(
                r"^(?:#{1,4}\s*)?\*{0,2}\s*"
                r"(?:ITEM|Item)\s*(?:7A|8)"
                r"[.\s\-\u2013\u2014:]",
                re.IGNORECASE,
            ),
            re.compile(
                r"^(?:#{1,4}\s*)?\*{0,2}\s*"
                r"(?:Financial\s+Statements\s+and\s+Supplementary\s+Data"
                r"|FINANCIAL\s+STATEMENTS)",
                re.IGNORECASE,
            ),
            re.compile(
                r"^(?:#{1,4}\s*)?\*{0,2}\s*SIGNATURES",
                re.IGNORECASE,
            ),
            re.compile(
                r"^(?:#{1,4}\s*)?\*{0,2}\s*PART\s+IV",
                re.IGNORECASE,
            ),
        ]

        end_patterns = end_patterns_quarterly if is_quarterly else end_patterns_annual

        def _find_end(start: int) -> int:
            """Find the end line index for a section starting at *start*."""
            body_lines = 0
            for j in range(start + 1, len(lines)):
                stripped = lines[j].strip()
                if not stripped:
                    continue
                body_lines += 1
                if body_lines > 15:
                    for pat in end_patterns:
                        if pat.search(stripped):
                            return j
            return len(lines)

        def _is_stub(start: int) -> bool:
            """Return True if the section at *start* is a stub / cross-ref.

            A stub is a very short section (< 500 chars of body text) that
            either contains a cross-reference phrase or is immediately
            followed by another Item header with no real body content.
            """
            # Gather text until the next Item header or end of document.
            body_chars: list[str] = []
            for j in range(start + 1, min(start + 30, len(lines))):
                stripped = lines[j].strip()

                if not stripped:
                    continue
                # Hit another Item header → the section between is the body.

                if any_item_re.match(stripped):
                    break

                body_chars.append(stripped)

            body_text = " ".join(body_chars)
            # If the body is substantial, it's not a stub.
            if len(body_text) > 500:
                return False
            # Short body — check for cross-reference language.
            crossref_re = re.compile(
                r"see\s+(?:the\s+)?(?:information|discussion)|"
                r"(?:is|are)\s+(?:presented|included|incorporated)\s+(?:in|by)|"
                r"incorporated\s+herein\s+by\s+reference|"
                r"(?:refer|refers)\s+to\s+(?:Item|Part|the\s+section|pages?\s+\d)|"
                r"included\s+(?:elsewhere|herein|in\s+(?:Part|Item))|"
                r"set\s+forth\s+(?:in|under|below)|"
                r"appears?\s+on\s+page|"
                r"begins?\s+on\s+page|"
                r"found\s+(?:on|in)\s+(?:page|section)|"
                r"(?:should|must)\s+be\s+read\s+in\s+conjunction|"
                r"contained\s+(?:in|on)\s+page|"
                r"(?:is|are)\s+(?:set\s+forth|described|discussed)\s+(?:in|on|under)",
                re.IGNORECASE,
            )
            if crossref_re.search(body_text):
                return True
            # Very short body with no cross-ref — still a stub if nearly empty.
            return len(body_text) < 100

        # -- main extraction --------------------------------------------------

        # Strategy:
        #  1. Find all Item 7/2 header matches.
        #  2. For each, check body length to determine stub vs real.
        #  3. If all are stubs, fall back to standalone heading.

        best_start: int | None = None
        best_end: int | None = None

        for i, line in enumerate(lines):
            stripped = line.strip()

            if not stripped:
                continue

            if item_header_re.search(stripped):
                if _is_stub(i):
                    continue
                best_start = i
                best_end = _find_end(i)
                break
            # Handle split headers: "Item 2." on one line, MD&A title on next.
            if bare_item_re.search(stripped):
                # Look at the next non-blank line for the MD&A title.
                for k in range(i + 1, min(i + 4, len(lines))):
                    next_stripped = lines[k].strip()

                    if not next_stripped:
                        continue

                    if mda_title_re.search(next_stripped) and not _is_stub(i):
                        best_start = i
                        best_end = _find_end(i)
                    break  # Only check up to the first non-blank line

                if best_start is not None:
                    break

        # Fallback: standalone "Management's Discussion and Analysis" heading.
        if best_start is None:
            for i, line in enumerate(lines):
                stripped = line.strip()

                if not stripped:
                    continue

                if standalone_mda_re.search(stripped) and not _is_stub(i):
                    candidate_end = _find_end(i)
                    body = "\n".join(lines[i:candidate_end]).strip()

                    if len(body) > 200:
                        best_start = i
                        best_end = candidate_end
                        break

        # -- Exhibit fallback: Annual Report to Stockholders (Exhibit 13) ---
        # When the main 10-K document only has a stub Item 7 that says
        # "Refer to pages X–Y of the Annual Report …, incorporated
        # herein by reference", the real MD&A lives in the separately
        # filed Annual Report exhibit.  aextract_data pre-fetched the
        # exhibit HTML when it detected the cross-reference pattern.

        if best_start is None and data.get("exhibit_content"):
            exhibit_base_url = data.get("exhibit_url", "")
            exhibit_md = html_to_markdown(
                data["exhibit_content"],
                base_url=exhibit_base_url,
                keep_tables=query.include_tables,
            )
            exhibit_md = re.sub(r"<a\s[^>]*>\s*</a>", "", exhibit_md)
            exhibit_lines = exhibit_md.splitlines()
            _exhibit_start_re = re.compile(
                r"^(?:#{1,4}\s*)?\*{0,2}\s*" + r"MANAGEMENT\s+DISCUSSION",
                re.IGNORECASE,
            )
            _exhibit_end_re = re.compile(
                r"^(?:#{1,4}\s*)?\*{0,2}\s*(?:"
                r"Management\s+Responsibility\s+for\s+Financial|"
                r"Management.s\s+Report\s+on\s+Internal\s+Control|"
                r"Report\s+of\s+(?:Management|Independent)|"
                r"Consolidated\s+(?:Balance\s+Sheet|Statement|Financial)|"
                r"Notes?\s+to\s+(?:Consolidated\s+)?Financial"
                r")",
                re.IGNORECASE,
            )

            for i, eline in enumerate(exhibit_lines):
                estripped = eline.strip()
                if not estripped or estripped.startswith("|"):
                    continue
                if _exhibit_start_re.search(estripped):
                    end = len(exhibit_lines)
                    body_count = 0
                    for j in range(i + 1, len(exhibit_lines)):
                        sj = exhibit_lines[j].strip()
                        if not sj:
                            continue
                        body_count += 1
                        if body_count > 15 and _exhibit_end_re.search(sj):
                            end = j
                            break
                    _content = "\n".join(exhibit_lines[i:end]).strip()
                    if len(_content) > 200:
                        data["content"] = _content
                        data["url"] = exhibit_base_url
                        return SecManagementDiscussionAnalysisData(**data)

        if best_start is None:
            raise EmptyDataError(
                "Could not locate the MD&A section in the filing."
                f" -> {data.get('url', '')}"
                " -> The content can be analyzed by setting"
                " `raw_html=True` in the query."
            )

        if best_end is None:
            best_end = len(lines)

        mda_content = "\n".join(lines[best_start:best_end]).strip()

        if not mda_content:
            raise EmptyDataError(
                "The MD&A section appears to be empty after extraction."
                f" -> {data.get('url', '')}"
                " -> The content can be analyzed by setting"
                " `raw_html=True` in the query."
            )

        data["content"] = mda_content

        return SecManagementDiscussionAnalysisData(**data)
