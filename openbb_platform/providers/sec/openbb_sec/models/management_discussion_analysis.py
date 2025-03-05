"""SEC Management & Discussion Model."""

# pylint: disable=unused-argument,too-many-branches,too-many-locals,too-many-statements,too-many-nested-blocks,too-many-boolean-expressions,too-many-lines

from typing import Any, Literal, Optional

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

    strategy: Literal["inscriptis", "trafilatura"] = Field(
        default="trafilatura",
        description="The strategy to use for extracting the text. Default is 'trafilatura'.",
    )
    wrap_length: int = Field(
        default=120,
        description="The length to wrap the extracted text, excluding tables. Default is 120.",
    )
    include_tables: bool = Field(
        default=False,
        description="Return tables formatted as markdown in the text. Default is False."
        + " Tables may reveal 'missing' content,"
        + " but will likely need some level of manual cleaning, post-request, to display properly."
        + " In some cases, tables may not be recoverable due to the nature of the document.",
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
        params: dict[str, Any]
    ) -> SecManagementDiscussionAnalysisQueryParams:
        """Transform the query."""
        return SecManagementDiscussionAnalysisQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecManagementDiscussionAnalysisQueryParams,
        credentials: Optional[dict[str, Any]],
        **kwargs: Any,
    ) -> dict:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        from aiohttp_client_cache import SQLiteBackend
        from aiohttp_client_cache.session import CachedSession
        from openbb_core.app.utils import get_user_cache_directory
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_sec.models.company_filings import SecCompanyFilingsFetcher
        from openbb_sec.utils.helpers import SEC_HEADERS, sec_callback
        from pandas import offsets, to_datetime

        # Get the company filings to find the URL.

        if query.symbol == "BLK" or query.symbol.isnumeric():
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
                filings[0]
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
                    if f.report_type == "10-K"
                    and f.filing_date.year == query.calendar_year
                ]
                if not target_filing:
                    target_filing = [
                        f for f in filings if f.filing_date.year == query.calendar_year
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
                    if start_date < filing.filing_date < end_date:
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

        if response and not isinstance(response, str):
            raise OpenBBError(
                f"Unexpected response received. Expected string and got -> {response.__class__.__name__}"
                f" -> {response[:100]}"
            )

        if isinstance(response, str):
            return {
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

    @staticmethod
    def transform_data(  # noqa: PLR0912
        query: SecManagementDiscussionAnalysisQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> SecManagementDiscussionAnalysisData:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        import re  # noqa
        from inscriptis import get_text
        from inscriptis.model.config import ParserConfig
        from textwrap import wrap
        from trafilatura import extract
        from warnings import warn

        if query.raw_html is True:
            return SecManagementDiscussionAnalysisData(**data)

        is_quarterly = data.get("report_type", "").endswith("Q")
        is_inscriptis = query.strategy == "inscriptis"

        def is_table_header(line: str) -> bool:
            """Check if line is a table header"""
            return (
                (
                    all(
                        not char.isnumeric()
                        for char in line.replace("(", "")
                        .replace(")", "")
                        .replace(",", "")
                        .replace(" ", "")
                        .replace("|", "")
                    )
                    and line.replace("|", "").replace("-", "").strip() != ""
                    and "/" not in line
                )
                or all(
                    len(str(word).strip()) == 4 and str(word).strip().startswith("20")
                    for word in line.split("|")
                    if word
                )
                or line.replace("|", "").replace(" ", "").endswith(":")
                or "of dollars" in line.lower()
            )

        def insert_cell_dividers(line):
            cells = line.strip().split("|")
            new_cells: list = []
            for cell in cells:
                cell = cell.replace("$", "").replace(" % ", "").replace("%", "")  # noqa
                if (
                    "par value" in cell.lower()
                    or "shares" in cell.lower()
                    or (" %-" in cell and "notes" in cell.lower())
                    or "as of" in cell.lower()
                    or "of dollars" in cell.lower()
                    or "year" in cell.lower()
                    or "scenario" in cell.lower()
                    or " to " in cell.lower()
                    or "section" in cell.lower()
                    or "title" in cell.lower()
                    or "adverse currency fluctuation" in cell.lower()
                    or "vs" in cell.lower()
                    or cell.strip().endswith(",")
                ):
                    new_cells.append(cell)
                    continue
                if "Form 10-" in cell:
                    continue
                new_cell = cell.strip()
                if new_cell.endswith(("-", "—", "–")) and any(
                    c.isalpha() for c in new_cell
                ):
                    # Remove the dash and insert a divider before it
                    new_cell = re.sub(r"[—\-–]+$", "", new_cell).strip() + " | —"
                elif (
                    re.search("[A-Za-z]", new_cell)
                    and re.search("[0-9]", new_cell)
                    and re.search(r"[A-Za-z]\s+[0-9]", new_cell)
                    and "thru" not in new_cell.lower()
                    and "through" not in new_cell.lower()
                    and "outstanding" not in new_cell.lower()
                    and "Tier" not in new_cell
                    and "%" not in new_cell
                    and "$" not in new_cell
                    and "in" not in new_cell
                    and "year" not in new_cell
                    and "scenario" not in new_cell
                ):
                    # Handle cases with spaces between letters and numbers
                    new_cell = re.sub(
                        r"(?<=[A-Za-z])\s+(?=[0-9])(?!\([a-zA-Z])", " |", new_cell
                    )
                    new_cell = re.sub(
                        r"(?<=[A-Za-z])(?=[0-9])(?!\([a-zA-Z])", "|", new_cell
                    )
                # Insert divider between consecutive numbers, excluding number(letter)
                if (
                    re.search(
                        r"(\(\d+\.?\d*\)|\d+\.?\d*)\s+(\(\d+\.?\d*\)|\d+\.?\d*)",
                        new_cell,
                    )
                    and "versus" not in new_cell.lower()
                    and "thru" not in new_cell.lower()
                    and "through" not in new_cell.lower()
                    and not re.search(r"\d+\.?\d*\([a-zA-Z]\)", new_cell)
                ):
                    new_cell = re.sub(
                        r"(\(\d+\)|\d+(?:\.\d+)?)\s+(?=\(|\d)(?!\([a-zA-Z])",
                        r"\1|",
                        new_cell,
                    )
                new_cells.append(new_cell)
            return "|".join(new_cells)

        def process_extracted_text(  # noqa: PLR0912
            extracted_text: str, is_inscriptis: bool
        ) -> list:
            """Process extracted text"""

            new_lines: list = []
            starting_line = "Item 2."
            annual_start = "Item 7."
            ending_line = "Item 6"
            annual_end = "Item 8. "
            found_start = False
            at_end = False
            previous_line = ""
            start_line_text = ""
            line_i = 0
            extracted_lines = extracted_text.splitlines()

            for line in extracted_lines:
                line_i += 1
                if (
                    not line.strip()
                    or line.replace("|", "")
                    .strip()
                    .startswith(("Page ", "Table of Contents"))
                    or line.strip() in ("|", start_line_text)
                    or (len(line) < 3 and line.isnumeric())
                    or line.strip().replace("_", "").replace("**", "") == ""
                ):
                    continue

                if (
                    "Discussion and Analysis of Financial Condition and Results of Operations is presented in".lower()
                    in line.lower()
                ):
                    annual_end = "PART IV"
                elif (
                    "see the information under" in line.lower()
                    and "discussion and analysis" in line.lower()
                ) and (
                    (is_quarterly and "10-K" not in line)
                    or (not is_quarterly and "10-Q" not in line)
                ):
                    annual_end = "statements of consolidated"
                    ending_line = "statements of conslidated"

                if (
                    (
                        line.strip()
                        .lower()
                        .startswith(
                            (
                                starting_line.lower(),
                                annual_start.lower(),
                            )
                        )
                        and "management" in line.lower()
                    )
                    or (
                        line.replace("|", "")
                        .lstrip(" ")
                        .lower()
                        .startswith("the following is management")
                        and "discussion and analysis of" in line.lower()
                    )
                    or (
                        line.endswith(
                            " “Management’s Discussion and Analysis of Financial Condition and Results of Operations” "
                            "below."
                        )
                    )
                    or (
                        line.replace("*", "").strip().lower().startswith("item")
                        and line.replace("*", "")
                        .replace(".", "")
                        .strip()
                        .lower()
                        .endswith(
                            "discussion and analysis of financial condition and results of operations"
                        )
                    )
                    # Section may be in a nested table.
                    or (
                        line.replace("*", "")
                        .replace("|", "")
                        .strip()
                        .lower()
                        .startswith("item")
                        and line.replace("*", "")
                        .replace("|", "")
                        .replace(".", "")
                        .rstrip(" ")
                        .lower()
                        .endswith(
                            "discussion and analysis of financial condition and results of operations"
                        )
                        and line_i > 200
                    )
                    or (
                        line.replace("*", "").replace("|", "").strip().lower()
                        == "financial review"
                        and line_i > 200
                    )
                    or (
                        line.replace("*", "")
                        .replace("|", "")
                        .replace(".", "")
                        .strip()
                        .lower()
                        .endswith(
                            (
                                "discussion and analysis",
                                "discussion and analysis of",
                                "analysis of financial",
                                "of financial condition",
                            )
                        )
                        and extracted_lines[line_i + 1]
                        .replace("|", "")
                        .replace(".", "")
                        .strip()
                        .lower()
                        .endswith(("financial condition", "results of operations"))
                    )
                    or (
                        line.replace("|", "").replace(".", "").strip()
                        == "Management’s Discussion and Analysis of Financial Condition and Results of Operations"
                    )
                    or (
                        line
                        in [
                            "2. MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS",
                            "7. MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS",
                            "Items 2. and 3. Management’s Discussion and Analysis of Financial Condition and "
                            "Results of Operations; Quantitative and Qualitative Disclosures about Market Risk",
                            "MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS |",
                            "Item 2. Management’s Discussion and Analysis of Financial Condition and Results of Operations.",  # noqa
                            "Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations.",  # noqa
                            "MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS",
                            "Management's Discussion and Analysis of Financial Condition and Results of Operations",
                            "MANAGEMENT’S DISCUSSION AND ANALYSIS OF THE FINANCIAL CONDITION AND RESULTS OF",
                            "MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS",
                            "Part I. Item 2. Management’s Discussion and Analysis of Financial Condition and Results of Operations",  # noqa
                            "MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS (“MD&A”)",  # noqa
                            "ITEM 7 – MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS (MD&A)",  # noqa
                            "ITEM 2 – MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS (MD&A)",  # noqa
                            "Part II. Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations",  # noqa  # pylint: disable=line-too-long
                            "| Item 2. | |",
                            "| Item 7. | |",
                        ]
                    )
                    or line.startswith(
                        "Item 7—Management's Discussion and Analysis of Financial Conditions"
                    )
                    or (
                        line.startswith(
                            "MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS (MD&A)"
                        )
                        and line_i > 200
                    )
                    or (
                        line.replace("|", "").strip()
                        == "Management's Discussion and Analysis"
                        and line_i > 300
                    )
                    or (
                        line.replace("|", "")
                        .strip()
                        .startswith(
                            "The following discussion and analysis of the financial condition and results of operations"
                        )
                    )
                ):
                    line = line.replace("|", "").replace("*", "")  # noqa
                    if line.strip(" ")[-1].isnumeric():
                        continue

                    if (
                        extracted_lines[line_i + 1]
                        .replace("*", "")
                        .replace(".", "")
                        .strip()
                        .lower()
                        .endswith(("financial condition", "results of operations"))
                    ):
                        line = "Management’s Discussion and Analysis of Financial Condition and Results of Operations"  # noqa
                        _ = extracted_lines.pop(line_i + 1)
                    found_start = True
                    at_end = False
                    start_line_text = line
                    new_lines.append(
                        "# **MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS (MD&A)"
                        "**\n\n"
                    )
                    continue

                if (
                    found_start
                    and (
                        line.replace("|", "")
                        .strip()
                        .lower()
                        .startswith(ending_line.lower())
                        and is_quarterly
                    )
                    or (
                        annual_end.lower() in line.lower()
                        and not is_quarterly
                        and len(new_lines) > 20
                    )
                    or line.replace("|", "").strip().lower().startswith("signatures")
                    or line.strip().startswith(
                        "Item 8—Financial Statements and Supplementary Data"
                    )
                    or line.strip().startswith("MANAGEMENT AND AUDITOR’S REPORTS")
                    or line == "EXHIBIT INDEX"
                ):
                    at_end = True
                    line = line.replace("|", " ").replace("  ", " ")  # noqa

                if found_start and not at_end:
                    if (
                        line[0].isdigit()
                        or line[0] == "•"
                        or line[0] == "●"
                        and line[1] not in [".", " ", "\u0020"]
                        and line[1].isalpha()
                    ):
                        word = line.split(" ")[0]
                        if not word.replace(" ", "").isnumeric():
                            line = line[0] + " " + line[1:]  # noqa

                    if "▪" in line:
                        line = line.replace("▪", "").replace("|", "").strip()  # noqa
                        line = "- " + line  # noqa

                    if "●" in line or "•" in line or "◦" in line:
                        line = (  # noqa
                            line.replace("|", "")
                            .replace("●", "-")
                            .replace("•", "-")
                            .replace("◦", "-")
                        )

                    if (
                        line.replace("|", "").strip().startswith("-")
                        and len(line.strip()) > 1
                        and line.strip()[1] != " "
                    ):
                        line = "- " + line[1:]  # noqa

                    if "the following table" in line.lower():
                        line = (  # noqa
                            line.replace("|", "").replace("  ", " ").strip() + "\n"
                        )

                    if (
                        line.replace("|", "").replace(" ", "").strip().startswith("(")
                        and (
                            line.replace("|", "").replace(" ", "").strip().endswith(")")
                        )
                        and line.count("|") < 3
                    ):
                        line = line.replace("|", "").replace(" ", "").strip()  # noqa
                        next_line = (
                            extracted_lines[line_i + 1]
                            if line_i + 1 < len(extracted_lines)
                            else ""
                        )
                        if not next_line.replace("|", "").replace(" ", "").strip():
                            next_line = (
                                extracted_lines[line_i + 2]
                                if line_i + 2 < len(extracted_lines)
                                else ""
                            )
                            if line_i + 1 < len(extracted_lines):
                                _ = extracted_lines.pop(line_i + 1)
                        if (
                            next_line.replace("|", "")
                            .replace(" ", "")
                            .strip()
                            .endswith((",", ";", "."))
                        ):
                            line = (  # noqa
                                line.replace("|", "").replace(" ", "").strip()
                                + " "
                                + next_line.replace("|", "").strip()
                            )
                            _ = extracted_lines.pop(line_i + 1)

                    if "|" in line:
                        first_word = line.split("|")[0].strip()
                        if first_word.isupper() or "item" in first_word.lower():
                            line = (  # noqa
                                line.replace("|", " ").replace("  ", " ").strip()
                            )

                        if (
                            line.endswith("|")
                            and not line.startswith("|")
                            and len(line) > 1
                        ):
                            line = (  # noqa
                                "| " + line
                                if len(line.split("|")) > 1
                                else line.replace("|", "").strip()
                            )
                        elif (
                            line.startswith("|")
                            and not line.endswith("|")
                            and len(line) > 1
                            and len(line.split("|"))
                        ):
                            line = (  # noqa
                                line + " |"
                                if len(line.split("|")) > 1
                                else line.replace("|", "").strip()
                            )

                        if query.include_tables is False and "|" in line:
                            continue

                        if (
                            "page" in line.replace("|", "").lower()
                            or "form 10-" in line.lower()
                        ):
                            continue

                        if "$" in line:
                            line = line.replace("$ |", "").replace("| |", "|")  # noqa
                        elif "%" in line:
                            line = line.replace("% |", "").replace("| |", "|")  # noqa

                        if "|" not in previous_line and all(
                            char == "|" for char in line.replace(" ", "")
                        ):
                            line = (  # noqa
                                line
                                + "\n"
                                + line.replace("      ", "")
                                .replace("   ", "")
                                .replace("  ", "")
                                .replace(" ", ":------:")
                            )

                        else:
                            is_header = is_table_header(line)
                            is_multi_header = (
                                "months ended" in line.lower()
                                or "year ended" in line.lower()
                                or "quarter ended" in line.lower()
                                or "change" in line.lower()
                                or line.strip().endswith(",")
                            )
                            is_date = (
                                ", 20" in line
                                and "through" not in line.lower()
                                and "thru" not in line.lower()
                                and "from" not in line.lower()
                            ) or (
                                "20" in line
                                and all(
                                    len(d.strip()) == 4 for d in line.split("|") if d
                                )
                            )
                            if is_header or is_date or is_multi_header:
                                line = (  # noqa
                                    line.replace(" | | ", " | ")
                                    .replace(" | |", " | ")
                                    .replace("| % |", "")
                                    .replace("| $ |", "")
                                    .replace("|$ |", "")
                                )
                                if is_header:
                                    line = "| " + line  # noqa
                            else:
                                line = (  # noqa
                                    line.replace("| $ | ", "")
                                    .replace("| % |", "")
                                    .replace("   ", "|")
                                    .replace("|$ |", "")
                                )
                                if not line.strip().startswith("|"):
                                    line = "| " + line  # noqa
                                line = insert_cell_dividers(line)  # noqa
                                line = (  # noqa
                                    line.replace(" | | ", " | ")
                                    .replace(" | |", " |")
                                    .replace("||", "|")
                                    .replace("||", "|")
                                    .replace(" | | | ", " | ")
                                    .replace(" | | |", "|")
                                )
                                if line[-1] != "|":
                                    line = line + "|"  # noqa

                        previous_line = new_lines[-1]
                        next_line = extracted_lines[line_i + 1]

                        if "|" in previous_line and not line.strip():
                            continue

                        if (
                            "|" in previous_line
                            and "|" in next_line
                            and not line.strip("\n").replace(" ", "")
                        ):
                            continue

                        if (
                            "|" in previous_line
                            and "|" not in next_line
                            and "|" in extracted_lines[line_i + 2]
                            and not line.strip()
                        ):
                            line_i += 1
                            continue

                        if (
                            "|" in previous_line
                            and "|" in next_line
                            and not line.strip("\n").replace(" ", "")
                        ):
                            continue
                        if (
                            "|" in previous_line
                            and "|" not in next_line
                            and "|" in extracted_lines[line_i + 2]
                            and not line.strip()
                        ):
                            line_i += 1
                            continue

                        if is_inscriptis is True:
                            if (
                                "|:-" in previous_line
                                and "|" in extracted_lines[line_i + 1]
                                and line.strip()
                                and not line.strip().startswith("|")
                            ):
                                line = "|" + line  # noqa
                                if not line.strip().endswith("|"):
                                    line = line + "|"  # noqa

                            line = (  # noqa
                                line.replace("||||", "|")
                                .replace("|||", "|")
                                .replace("|          |", "")
                                .replace("| | |", "|")
                                .replace("| |", "|")
                                .replace("    ", "")
                                .replace("||", "|")
                                .replace("|%|", "")
                                .replace("|%  |", "")
                                .replace("|$|", "")
                                .replace("|$ |", "")
                                .replace("|)", ")")
                                .replace("  )", ")")
                                .replace(" )", ")")
                                .replace("| | |", "|")
                                .replace("|  |", "|")
                                .replace(" | | ", "|")
                                .replace("| |", "|")
                            )
                            if (
                                "months ended" in line.lower()
                                or "year ended" in line.lower()
                                or "quarter ended" in line.lower()
                                or "weeks ended" in line.lower()
                                and "|" not in line
                                and "|" in previous_line
                            ):
                                line = "|" + line  # noqa

                        if line not in ["||", "|  |"]:
                            new_lines.append(line)
                            previous_line = line
                    else:
                        if (
                            "|" in previous_line
                            and "|" in extracted_lines[line_i + 1]
                            and not line.strip()
                        ):
                            continue

                        if is_inscriptis is True and ".   " in line:
                            line = line.replace(".   ", ".\n\n")  # noqa
                        elif is_inscriptis is True and ".  " in line:
                            line = line.replace(".  ", ".\n\n")  # noqa

                        if " ." in line:
                            line = line.replace(" .", ".")  # noqa

                        if "|" in previous_line:
                            new_lines.extend(
                                ["\n"] + wrap(line, width=query.wrap_length) + ["\n"]
                            )
                        elif line.strip().startswith("-"):
                            new_lines.extend([line] + ["\n"])
                        else:
                            new_lines.extend(
                                wrap(line, width=query.wrap_length) + ["\n"]
                            )
                        previous_line = line

            return new_lines

        # Do a first pass, and if extraction fails we can identify where the problem originates.

        def try_inscriptis(filing_str):
            """Try using Inscriptis instead."""
            extracted_text = get_text(
                filing_str,
                config=ParserConfig(
                    table_cell_separator="|",
                ),
            )
            extracted_lines = []
            for line in extracted_text.splitlines():
                if not line.strip():
                    continue
                extracted_lines.append(
                    line.strip()
                    .replace(" , ", ", ")
                    .replace(" . ", ". ")
                    .replace(" .", ".")
                    .replace(" ’ ", "'")
                    .replace(" ' ", "'")
                    .replace("“  ", "“")
                    .replace("  ”", "”")
                    .replace("o f", "of")
                    .replace("a n", "an")
                    .replace("in crease", "increase")
                )

            return process_extracted_text("\n".join(extracted_lines), True)

        filing_str = data.get("content", "")

        if query.strategy == "trafilatura":
            extracted_text = extract(
                filing_str,
                include_tables=True,
                include_comments=True,
                include_formatting=True,
                include_images=True,
                include_links=False,
            )
            new_lines = process_extracted_text(extracted_text, False)

            if not new_lines:
                warn("Trafilatura extraction failed, trying Inscriptis.")
                new_lines = try_inscriptis(filing_str)
                is_inscriptis = True

        else:
            new_lines = try_inscriptis(filing_str)

        if not new_lines:
            raise EmptyDataError(
                "No content was found in the filing, likely a parsing error from unreachable content."
                f" -> {data['url']}"
                " -> The content can be analyzed by inspecting"
                " the output of `SecManagementDiscussionAnalysisFetcher.aextract_data`,"
                " or by setting `raw_html=True` in the query."
            )

        # Second pass - clean up document

        def is_title_case(line: str) -> bool:
            """Check if line follows financial document title case patterns"""
            if (
                line.strip().startswith("-")
                or line.strip().endswith(".")
                or line.strip().endswith(",")
                or "“" in line
                or line.endswith("-")
                or line.lower().endswith("ended")
            ):
                return False

            if line.istitle() and not line.endswith(".") and not line.startswith("-"):
                return True

            if (
                line.strip().endswith(",")
                or line.strip().startswith("-")
                or line.strip().endswith(".")
            ):
                return False

            if (
                "|" not in line
                and line.strip().isupper()
                and len(line.strip()) > 1
                and line[-1].isalpha()
                or line.strip().startswith("Item")
                or line.strip().startswith("ITEM")
            ):
                return True

            return (
                line.replace("(", "")
                .replace(")", "")
                .replace(",", "")
                .replace(" and ", " And ")
                .replace(" of ", " Of ")
                .replace(" the ", " The ")
                .replace(" vs ", " VS ")
                .replace(" in ", " In ")
                .replace(" to ", " To ")
                .replace(" for ", " For ")
                .replace(" with ", " With ")
                .replace(" on ", " On ")
                .replace(" at ", " At ")
                .replace(" from ", " From ")
                .replace(" by ", " By ")
            ).istitle()

        def count_columns_in_data_row(data_row: str) -> int:
            """Count actual columns from first data row"""
            return len(list(data_row.split("|"))) - 2

        def pad_row_columns(row: str, target_cols: int) -> str:
            """Pad a table row with empty cells to match target column count"""
            cells = row.split("|")
            current_cols = len(cells) - 2  # Exclude outer pipes

            if current_cols < target_cols:
                # Add empty cells
                if (
                    is_table_header(row)
                    and row.replace("|", "").replace(" ", "").endswith(":")
                    or (
                        row.replace("|", "").replace(" ", "").endswith(")")
                        and row.replace("|", "").replace(" ", "")[0].isalpha()
                        and len(row.split("|")) < 3
                    )
                    and not (
                        "20" in row and all(len(d) == 4 for d in row.split("|") if d)
                    )
                ):
                    cells = [c for c in cells if c.strip()] + [
                        " " for _ in range(target_cols - current_cols - 2)
                    ]
                    return "|" + "|".join(cells)
                cells = [" " for _ in range(target_cols - current_cols - 2)] + cells

            return "|".join(cells)

        def process_document(  # noqa: PLR0912
            document: list[str], is_inscriptis: bool
        ) -> list[str]:
            """Clean up document lines"""
            cleaned_lines: list = []
            i = 0
            max_cols = 0

            while i < len(document):
                current_line = document[i]
                if (
                    "|" in document[i - 1]
                    and i - 1 > 1
                    and i + 1 <= len(document)
                    and i + 1 < len(document)
                    and "|" in document[i + 1]
                ) and (
                    current_line == "" or current_line.replace("|", "").strip() == ""
                ):
                    i += 1
                    continue

                if is_inscriptis is True and "|" not in current_line:
                    current_line = current_line.replace("   ", " ")

                if is_inscriptis is True and "-::-" in current_line:
                    current_line = (
                        current_line.replace(":------::", "")
                        .replace("::------:", "")
                        .replace("::------::", "")
                        .replace(" ", "")
                    ).strip()
                if (
                    is_inscriptis is True
                    and "|:-" in current_line
                    and "|" not in document[i - 1]
                ):
                    cleaned_lines.append("|   " * current_line.count("|"))

                if is_inscriptis is True and "|" in document[i - 1]:
                    if current_line.strip() in [
                        '""',
                        "",
                        " ",
                        "\n",
                        "|",
                        "|   |   |   |   |",
                        "|   |   |",
                    ]:
                        _ = document.pop(i)
                        continue

                    current_line = current_line.replace("   ", " ")

                    if (
                        current_line.strip().startswith("(inmillions")
                        and "|" not in current_line
                    ):
                        current_line = "|" + current_line

                    if (
                        current_line.strip().startswith("|:-")
                        and current_line[-1] != "|"
                    ):
                        current_line = current_line + "|"

                    if (
                        "in the preceding table" in current_line.lower()
                        or "in the table above" in current_line.lower()
                        or "the following tables present" in current_line.lower()
                        and "|" in document[i - 1]
                    ):
                        cleaned_lines.append("\n")
                        current_line = "\n" + current_line.replace("|", "").strip()

                    if (
                        current_line.startswith("# ")
                        and "|" not in current_line
                        and "|" in document[i - 1]
                    ):
                        current_line = "|" + current_line.replace("# ", " *")
                        cleaned_lines.append(current_line)
                        i += 1
                        continue

                    if (
                        "|" in document[i - 1]
                        and len(current_line) > 1
                        and "|" not in current_line
                        and current_line.replace(")", "")[-1].isnumeric()
                    ):
                        current_line = "|" + current_line + " |"

                if (
                    current_line.strip()
                    and current_line.strip().startswith("-")
                    and current_line.strip().endswith("-")
                    and len(current_line.strip().replace("-", "").replace(" ", "")) < 4
                    and current_line.strip()
                    .replace("-", "")
                    .replace(" ", "")
                    .isnumeric()
                ):
                    i += 1
                    continue
                if "![" in current_line:
                    image_file = (
                        current_line.split("]")[1].replace("(", "").replace(")", "")
                    )
                    base_url = data["url"].rsplit("/", 1)[0]
                    image_url = f"{base_url}/{image_file}"
                    cleaned_lines.append(f"![Graphic]({image_url})")
                    i += 1
                    continue

                if current_line.strip() == "| | o |":
                    i += 1
                    current_line = "- " + document[i].replace("|", "").strip()
                    cleaned_lines.append(current_line)
                    i += 1
                    continue
                if current_line.strip() == ":------:":
                    i += 1
                    continue
                if current_line.count("|") < 3:
                    current_line = (
                        current_line.replace("|", "").replace(":------:", "").strip()
                    )
                    cleaned_lines.append(current_line)
                    i += 1
                    continue

                next_line = document[i + 1] if i + 1 < len(document) else ""

                if next_line.replace("**", "").strip() == "AND RESULTS OF OPERATIONS":
                    current_line = (
                        "**"
                        + current_line.replace("**", "").replace("\n", "").strip()
                        + " "
                        + "AND RESULTS OF OPERATIONS"
                        + "**"
                    )
                    _ = document.pop(i + 1)
                    cleaned_lines.append(current_line)
                    i += 1
                    continue

                previous_line = document[i - 1] if i > 0 else ""

                if current_line.strip() in (
                    "--",
                    "-",
                    "|:------:|",
                    "||",
                    "|  |",
                    ":------:",
                ):
                    if not next_line.strip() or next_line == current_line:
                        i += 2
                        continue
                    i += 1
                    continue

                if "| :-" in current_line:
                    current_line = current_line.replace(" :- ", ":-")

                if "|:-" in current_line and not current_line.strip().endswith("|"):
                    current_line = current_line + "|"

                if (
                    not current_line.strip()
                    and "|" in document[i - 1]
                    and "|" in document[i + 1]
                ):
                    continue

                if (
                    query.include_tables is False
                    and "|" in current_line
                    and "|" not in document[i - 1]
                ):
                    current_line = current_line.replace("|", "")

                if current_line.startswith(" -"):
                    current_line = "- " + current_line[2:]

                if (
                    current_line.startswith(("(", "["))
                    and current_line.endswith((")", "]"))
                    and len(current_line) < 4
                ):
                    current_line = current_line.replace("[", "(").replace("]", ")")
                    dead_line = True
                    new_i = i
                    while dead_line is True:
                        new_i += 1
                        next_line = document[new_i]
                        if next_line.replace("|", "").strip():
                            dead_line = False
                            break

                    next_line = next_line.replace("|", "").rstrip()

                    if document[new_i + 1].replace("|", "").rstrip() == next_line:
                        new_i += 1

                    current_line = (
                        current_line
                        + " "
                        + next_line.replace("|", "").strip().rstrip(" ")
                    ).strip()
                    i = new_i
                    previous_line = document[i - 1]

                if (
                    current_line.replace("|", "").strip().startswith("-")
                    and current_line[1] != " "
                ):
                    current_line = current_line.replace("|", "").replace("-", "- ")

                if (
                    "|" in current_line
                    and "|" in previous_line
                    and "|" in next_line
                    and "|:-" not in next_line
                    and current_line.replace(" ", "").replace("|", "") == ""
                ):
                    i += 1
                    continue

                if query.include_tables is False and "|" in current_line:
                    i += 1
                    continue

                # Fix table header rows with missing dividers.
                # We can't fix all tables, but this helps with some.

                if (
                    "|" in current_line
                    and "|" not in previous_line
                    and "|:-" not in next_line
                ) and current_line.count("|") > 2:
                    n_bars = current_line.replace(" |  | ", "|").count("|")
                    inserted_line = ("|:------:" * (n_bars - 2)) + "|"

                    document.insert(
                        i + 1,
                        inserted_line.replace(":------:", "   ").strip()[1:-2],
                    )
                    document.insert(i + 2, inserted_line)
                    current_line = current_line.replace("|", "").lstrip(" ") + "\n"

                elif (
                    "|:-" in current_line
                    and "|" not in previous_line
                    and "|" in next_line
                ):
                    inserted_line = current_line.replace("-", "").replace("::", "   ")

                    if previous_line.strip():
                        inserted_line = "\n" + inserted_line

                    document.insert(i - 1, inserted_line)
                    cleaned_lines.append(inserted_line)

                if current_line.startswith("|:-") and not current_line.strip().endswith(
                    "|"
                ):
                    current_line = current_line + "|"

                # Detect table by empty header pattern
                if (
                    i + 2 < len(document)
                    and "|" in current_line
                    and all(not cell.strip() for cell in current_line.split("|")[1:-1])
                    and ":---" in document[i + 1]
                ):
                    table_i = i + 2
                    max_cols = 0
                    # First pass - find max columns
                    while table_i < len(document):
                        if "|" not in document[table_i]:
                            break
                        row = document[table_i].strip()
                        if row and row != "|":
                            cols = count_columns_in_data_row(row)
                            max_cols = max(max_cols, cols)
                        table_i += 1

                    # Fix empty header row
                    header_line = (
                        "| " + " | ".join([" " for _ in range(max_cols)]) + " |"
                    )
                    cleaned_lines.append(header_line)

                    # Fix separator row
                    separator_line = (
                        "|" + "|".join([":------:" for _ in range(max_cols)]) + "|"
                    )
                    cleaned_lines.append(separator_line)

                    i += 2  # Skip original header and separator
                else:
                    if current_line.strip().startswith("-"):
                        current_line = current_line.replace("|", "")
                        if current_line.strip()[-1] not in (".", ";", ":") and (
                            (
                                next_line.replace("|", "").strip().islower()
                                and next_line.replace("|", "").strip().endswith(".")
                            )
                            or not next_line.strip()
                            and i + 2 < len(document)
                            and document[i + 2].replace("|", "").strip().endswith(".")
                        ):
                            if not next_line.strip() and i + 2 <= len(document):
                                next_line = document[i + 2].strip()

                            current_line = (
                                current_line + " " + next_line.replace("|", "").strip()
                            )
                            cleaned_lines.append(current_line)
                            i += 2
                            continue
                    # Check if this is a table row that needs padding
                    current_line = current_line.replace(")  (", ")|(")
                    if (
                        current_line.strip().startswith("-")
                        and "|" not in current_line
                        and "." in current_line
                        and (
                            document[i - 1].strip().endswith(", and")
                            or document[i - 1].strip().endswith(" and")
                        )
                    ):
                        clean_line = current_line.split(".")[0] + ".\n\n"
                        if len(current_line.split(".")) > 1:
                            remaining = ". ".join(current_line.split(".")[1:])
                            clean_line += remaining + "\n"
                        cleaned_lines.append(clean_line)
                        i += 1
                        continue

                    if current_line.strip().startswith("-") and (
                        "|" not in current_line
                        and not previous_line.replace("|", "")
                        .strip()
                        .endswith((";", ".", ":"))
                        and current_line.strip()
                        .replace("-", "")
                        .replace(" ", "")
                        .islower()
                    ):
                        old_line = cleaned_lines.pop(-1)
                        if not old_line.strip("\n"):
                            old_line = cleaned_lines.pop(-2)

                        cleaned_lines.append(
                            old_line.strip("\n")
                            + " "
                            + current_line.replace("-", "").strip()
                        )

                    elif "|" in current_line:
                        current_line = current_line.replace("|)|", ")|").replace(
                            "| | (Dollars in ", "| (Dollars in "
                        )
                        if (
                            current_line in ("|  |", "| |", "|")
                            or "form 10-k" in current_line.replace("|", "").lower()
                        ):
                            i += 1
                            continue
                        current_cols = count_columns_in_data_row(current_line)
                        if max_cols and max_cols > 0 and current_cols != max_cols:
                            padded_line = pad_row_columns(current_line, max_cols)
                            cleaned_lines.append(padded_line.strip())
                        else:
                            cleaned_lines.append(current_line)

                    # Not a table row, keep unchanged
                    else:
                        cleaned_lines.append(current_line)
                    i += 1

            return cleaned_lines

        document = "\n".join(new_lines)

        cleaned_lines = process_document(document.splitlines(), is_inscriptis)

        finished_lines: list = []

        i = 0
        for line in cleaned_lines:
            i += 1
            line = line.replace(  # noqa
                "(amountsinmillions,exceptpershare,share,percentagesandwarehousecountdata) ",
                "",
            )
            if (
                "|" not in line
                and "#" not in line
                and is_title_case(line)
                and "|" not in cleaned_lines[i - 1]
            ):
                if "." in line and " " not in line:
                    continue
                if len(finished_lines) > 1 and "|" not in finished_lines[-1]:
                    finished_lines.append(
                        f"## **{line.strip().replace('*', '').rstrip()}**"
                        if line.strip().startswith("Item") or line.strip().isupper()
                        else f"### **{line.strip().replace('*', '').rstrip()}**"
                    )
            else:
                finished_lines.append(line)

        data["content"] = "\n".join(finished_lines)

        return SecManagementDiscussionAnalysisData(**data)
