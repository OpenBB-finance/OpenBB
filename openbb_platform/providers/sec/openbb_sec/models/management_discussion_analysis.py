"""SEC Management & Discussion Model."""

# pylint: disable=unused-argument,too-many-branches,too-many-locals,too-many-statements,too-many-nested-blocks,too-many-boolean-expressions

from typing import Any, Optional

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
                calendar_period = query.calendar_period
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
        from textwrap import wrap
        from trafilatura import extract

        if query.raw_html is True:
            return SecManagementDiscussionAnalysisData(**data)

        is_quarterly = data.get("report_type", "").endswith("Q")

        def is_table_header(line: str) -> bool:
            """Check if line is a table header"""
            return (
                all(
                    not char.isnumeric()
                    for char in line.replace("(", "")
                    .replace(")", "")
                    .replace(",", "")
                    .replace(" ", "")
                    .replace("|", "")
                )
                and line.replace("|", "").replace("-", "").strip() != ""
            ) or line.replace("|", "").replace(" ", "").endswith(":")

        def insert_cell_dividers(line):
            cells = line.strip().split("|")
            new_cells: list = []
            for cell in cells:
                if (
                    "par value" in cell.lower()
                    or "shares" in cell.lower()
                    or (" %-" in cell and "notes" in cell.lower())
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
                ):
                    # Handle cases with spaces between letters and numbers
                    new_cell = re.sub(r"(?<=[A-Za-z])\s+(?=[0-9])", " |", new_cell)
                    new_cell = re.sub(r"(?<=[A-Za-z])(?=[0-9])", "|", new_cell)
                # Insert divider between consecutive numbers
                if (
                    re.search(
                        r"(\(\d+\.?\d*\)|\d+\.?\d*)\s+(\(\d+\.?\d*\)|\d+\.?\d*)",
                        new_cell,
                    )
                    and "versus" not in new_cell.lower()
                    and "thru" not in new_cell.lower()
                    and "through" not in new_cell.lower()
                ):
                    new_cell = re.sub(
                        r"(\(\d+\)|\d+(?:\.\d+)?)\s+(?=\(|\d)", r"\1|", new_cell
                    )
                new_cells.append(new_cell)
            return "|".join(new_cells)

        def process_extracted_text(extracted_text: str) -> list:  # noqa: PLR0912
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

            for line in extracted_text.splitlines():
                if (
                    not line.strip()
                    or line.startswith("Page ")
                    or line.startswith("Table of Contents")
                    or line.strip() == "|"
                    or (len(line) < 3 and line.isnumeric())
                    or line == start_line_text
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
                    line.replace("|", "")
                    .strip()
                    .lower()
                    .startswith(starting_line.lower())
                    or line.replace("|", "")
                    .strip()
                    .lower()
                    .startswith(annual_start.lower())
                ) and "management" in line.lower():
                    found_start = True
                    line = line.replace("|", "")  # noqa
                    start_line_text = line

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
                ) or line.replace("|", "").strip().lower().startswith("signatures"):
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

                    if "●" in line or "•" in line:
                        line = (  # noqa
                            line.replace("|", "").replace("●", "-").replace("•", "-")
                        )

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
                            line = line + "\n" + line.replace(" ", ":------:")  # noqa

                        else:
                            is_header = is_table_header(line)
                            is_multi_header = (
                                "months ended" in line.lower()
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
                                and all(len(d) == 4 for d in line.split("|") if d)
                            )
                            if is_header or is_date or is_multi_header:
                                line = (  # noqa
                                    line.replace(" | | ", " | ")
                                    .replace(" | |", " | ")
                                    .replace("| % |", "")
                                    .replace("| $ |", "")
                                )
                                if is_header:
                                    line = "| " + line  # noqa
                                # line = insert_cell_dividers(line)  # noqa
                            else:
                                line = line.replace("| $ | ", "").replace(  # noqa
                                    "| % |", ""
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

                        new_lines.append(line)
                        previous_line = line
                    else:
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

        # Do a first pass, and if extraction fails we can try a different strategy.

        filing_str = data.get("content", "")

        extracted_text = extract(
            filing_str,
            include_tables=True,
            include_comments=True,
            include_formatting=True,
            include_images=True,
            include_links=False,
        )

        if not extracted_text:
            raise EmptyDataError("No text was extracted from the filing!")

        new_lines = process_extracted_text(extracted_text)

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
            ignore_words = [
                "and",
                "the",
                "of",
                "in",
                "to",
                "for",
                "with",
                "on",
                "at",
                "by",
                "from",
                "versus",
                "&",
                ",",
                "$",
                "per",
                "share",
                "compared",
            ]

            # Basic checks
            if (
                not line
                or not line.strip()
                or len(line.strip()) < 4
                or "|" in line
                or line.strip().endswith('."')
                or line.strip()[0].islower()
                or line.strip().isnumeric()
                or line.strip()[0] == "("
                or (
                    line.strip().endswith((".", ":", ";", ",", "-", '"'))
                    and not line.strip().isupper()
                )
            ):
                return False

            words = line.strip().split()

            if (
                words[0].isnumeric()
                and words[-1].isnumeric()
                and len(words) > 2
                and words[1].isalpha()
                and "." not in words[1]
            ):
                return True

            if (
                all(
                    word.replace("(", "")
                    .replace(")", "")
                    .replace("-", "")
                    .replace(",", "")
                    .replace(".", "")
                    .isupper()
                    for word in words
                )
                or str(words)
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .replace(",", "")
                .replace(".", "")
                .istitle()
            ):
                return True

            if len(words) < 2 and (
                str(words).isnumeric() or str(words).startswith("(")
            ):
                return False

            # Check remaining words
            for i, word in enumerate(words[1:], 1):
                # Skip common lowercase words unless first/last
                if word.lower() in ignore_words and i != len(words) - 1:
                    continue

                # Allow numbers and abbreviations
                if word.isupper() or word[0].isdigit():
                    continue

                # Other words should be capitalized
                if not word[0].isupper():
                    return False

            return True

        def count_columns_in_data_row(data_row: str) -> int:
            """Count actual columns from first data row"""
            return len(list(data_row.split("|")))

        def pad_row_columns(row: str, target_cols: int) -> str:
            """Pad a table row with empty cells to match target column count"""
            cells = row.split("|")
            current_cols = len(cells) - 2  # Exclude outer pipes
            if current_cols < target_cols:
                # Add empty cells
                if is_table_header(row) and row.replace("|", "").replace(
                    " ", ""
                ).endswith(":"):
                    cells = [c for c in cells if c.strip()] + [
                        " " for _ in range(target_cols - current_cols - 2)
                    ]
                    return "|" + "|".join(cells)
                cells = [" " for _ in range(target_cols - current_cols - 2)] + cells
            return "|".join(cells)

        def process_document(document: list[str]) -> list[str]:
            """Clean up document lines"""
            cleaned_lines: list = []
            i = 0
            max_cols = 0

            while i < len(document):
                current_line = document[i]
                next_line = document[i + 1] if i + 1 < len(document) else ""
                previous_line = document[i - 1] if i > 0 else ""

                if "| :-" in current_line:
                    current_line = current_line.replace(" :- ", ":-")

                if (
                    query.include_tables is False
                    and "|" in current_line
                    and "|" not in document[i - 1]
                ):
                    current_line = current_line.replace("|", "")

                if (
                    "|" in current_line
                    and "|" not in previous_line
                    and "|:-" not in next_line
                ):
                    current_line = current_line.replace("|", "")

                if query.include_tables is False and "|" in current_line:
                    i += 1
                    continue

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

                elif current_line.strip().startswith("!["):
                    image_file = (
                        current_line.split("]")[1].replace("(", "").replace(")", "")
                    )
                    base_url = data["url"].rsplit("/", 1)[0]
                    image_url = f"{base_url}/{image_file}"
                    cleaned_lines.append(f"![Graphic]({image_url})")
                    i += 1

                elif is_title_case(current_line):
                    cleaned_lines.append(
                        f"## **{current_line.strip().replace('*', '').rstrip()}**"
                        if current_line.strip().startswith("Item")
                        or current_line.strip().isupper()
                        else f"### **{current_line.strip().replace('*', '').rstrip()}**"
                    )
                    i += 1

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
                    elif current_line.strip().startswith("-") and (
                        "|" not in current_line
                        and not previous_line.replace("|", "").strip().endswith(";")
                        and not previous_line.replace("|", "").strip().endswith(".")
                        and not previous_line.replace("|", "").strip().endswith(":")
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

        cleaned_lines = process_document(document.splitlines())

        data["content"] = "\n".join(cleaned_lines)

        return SecManagementDiscussionAnalysisData(**data)
